\
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "AGENT_BACKUP_CONFIG.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {"drive_folder": "OpenHardware-Control/Backups", "local_staging_dir": ".ohc-backups"}


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(ROOT), *args], text=True, capture_output=True, check=check)


def require_git_repo() -> None:
    proc = run_git("rev-parse", "--is-inside-work-tree", check=False)
    if proc.returncode != 0 or proc.stdout.strip() != "true":
        raise RuntimeError("This backup gate requires the project to be opened from its Git repository.")


def git_head() -> str:
    return run_git("rev-parse", "HEAD").stdout.strip()


def git_branch() -> str:
    proc = run_git("symbolic-ref", "--short", "HEAD", check=False)
    return proc.stdout.strip() or "DETACHED"


def require_clean() -> None:
    status = run_git("status", "--porcelain=v1", "--untracked-files=all").stdout.strip()
    if status:
        raise RuntimeError("Working tree is not clean. Commit the intended changes before creating the GitHub backup.\n" + status)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def state_paths() -> tuple[Path, Path]:
    cfg = load_config()
    state_dir = ROOT / cfg.get("local_staging_dir", ".ohc-backups")
    pending = state_dir / "pending"
    pending.mkdir(parents=True, exist_ok=True)
    return state_dir, pending


def state_file() -> Path:
    return state_paths()[0] / "state.json"


def save_state(data: dict) -> None:
    path = state_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_state() -> dict:
    path = state_file()
    if not path.exists():
        raise RuntimeError("No backup state exists. Run ./scripts/prepare_drive_backup.sh first.")
    return json.loads(path.read_text(encoding="utf-8"))


def prepare() -> int:
    require_git_repo()
    require_clean()
    cfg = load_config()
    head = git_head()
    branch = git_branch()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    _, pending = state_paths()
    archive_name = f"OpenHardware-Control-v{version}-git-{head[:12]}-{timestamp}.zip"
    archive_path = pending / archive_name

    with tempfile.TemporaryDirectory(prefix="ohc-git-backup-") as temp_name:
        temp = Path(temp_name)
        bundle = temp / "repository.bundle"
        source_zip = temp / "head-source.zip"
        metadata = temp / "BACKUP_METADATA.json"

        bundle_proc = run_git("bundle", "create", str(bundle), "--all", check=False)
        if bundle_proc.returncode != 0:
            raise RuntimeError("git bundle failed: " + (bundle_proc.stderr or bundle_proc.stdout).strip())
        archive_proc = run_git("archive", "--format=zip", f"--output={source_zip}", "HEAD", check=False)
        if archive_proc.returncode != 0:
            raise RuntimeError("git archive failed: " + (archive_proc.stderr or archive_proc.stdout).strip())

        meta = {
            "schema_version": 1,
            "project": "Open Hardware Control",
            "version": version,
            "git_head": head,
            "git_branch": branch,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "drive_folder": cfg.get("drive_folder", "OpenHardware-Control/Backups"),
            "repository_bundle_sha256": sha256(bundle),
            "head_source_zip_sha256": sha256(source_zip),
        }
        metadata.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write(bundle, arcname="repository.bundle")
            zf.write(source_zip, arcname="head-source.zip")
            zf.write(metadata, arcname="BACKUP_METADATA.json")

    digest = sha256(archive_path)
    state = {
        "schema_version": 1,
        "project": "Open Hardware Control",
        "version": version,
        "git_head": head,
        "git_branch": branch,
        "archive_path": str(archive_path.relative_to(ROOT)),
        "archive_name": archive_name,
        "archive_sha256": digest,
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "drive_folder": cfg.get("drive_folder", "OpenHardware-Control/Backups"),
        "drive_upload_confirmed": False,
        "confirmed_at_utc": None,
        "remote_name": None,
        "drive_file_id": None,
    }
    save_state(state)
    print(f"Prepared backup: {archive_path}")
    print(f"SHA256: {digest}")
    print(f"Google Drive target: {state['drive_folder']}")
    print("Upload this exact ZIP through Cursor's official Google Drive plugin, then run confirm_drive_backup.sh.")
    return 0


def verify_state(*, require_confirmed: bool = True) -> dict:
    require_git_repo()
    require_clean()
    state = read_state()
    head = git_head()
    if state.get("git_head") != head:
        raise RuntimeError(f"Backup is stale: prepared for {state.get('git_head')}, current HEAD is {head}.")
    rel = state.get("archive_path")
    if not rel:
        raise RuntimeError("Backup state has no archive path.")
    archive = (ROOT / rel).resolve()
    try:
        archive.relative_to(ROOT.resolve())
    except ValueError:
        raise RuntimeError("Backup archive path escapes the repository root.")
    if not archive.is_file():
        raise RuntimeError(f"Backup archive is missing: {archive}")
    actual = sha256(archive)
    if actual != state.get("archive_sha256"):
        raise RuntimeError("Backup archive SHA-256 no longer matches the prepared state.")
    if require_confirmed and not state.get("drive_upload_confirmed"):
        raise RuntimeError("Backup exists locally but Google Drive upload has not been confirmed.")
    if require_confirmed and not state.get("remote_name"):
        raise RuntimeError("Drive confirmation is missing the uploaded file name.")
    return state


def confirm(args: argparse.Namespace) -> int:
    state = verify_state(require_confirmed=False)
    if not args.remote_name.strip():
        raise RuntimeError("--remote-name must identify the exact file reported as uploaded by Google Drive.")
    if args.remote_name.strip() != state.get("archive_name"):
        raise RuntimeError(
            f"Remote name must match the prepared archive exactly: {state.get('archive_name')}"
        )
    state["drive_upload_confirmed"] = True
    state["confirmed_at_utc"] = datetime.now(timezone.utc).isoformat()
    state["remote_name"] = args.remote_name.strip()
    state["drive_file_id"] = args.drive_file_id.strip() if args.drive_file_id else None
    save_state(state)
    print("Google Drive upload confirmation recorded for the current Git HEAD.")
    print(f"HEAD: {state['git_head']}")
    print(f"File: {state['remote_name']}")
    print("Run ./scripts/check_drive_backup.sh before pushing.")
    return 0


def verify(args: argparse.Namespace) -> int:
    state = verify_state(require_confirmed=True)
    if not args.quiet:
        print("Drive backup gate: OK")
        print(f"HEAD: {state['git_head']}")
        print(f"Archive: {state['archive_name']}")
        print(f"SHA256: {state['archive_sha256']}")
        print(f"Drive folder: {state['drive_folder']}")
        print(f"Confirmed: {state['confirmed_at_utc']}")
    return 0


def status() -> int:
    try:
        state = read_state()
    except RuntimeError as exc:
        print(f"Drive backup gate: NOT READY — {exc}")
        return 1
    print(json.dumps(state, indent=2, ensure_ascii=False))
    try:
        verify_state(require_confirmed=True)
    except Exception as exc:
        print(f"\nDrive backup gate: NOT READY — {exc}")
        return 1
    print("\nDrive backup gate: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Open Hardware Control Git/Google-Drive backup gate")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    c = sub.add_parser("confirm")
    c.add_argument("--remote-name", required=True)
    c.add_argument("--drive-file-id", default="")
    v = sub.add_parser("verify")
    v.add_argument("--quiet", action="store_true")
    sub.add_parser("status")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            return prepare()
        if args.command == "confirm":
            return confirm(args)
        if args.command == "verify":
            return verify(args)
        return status()
    except (RuntimeError, subprocess.CalledProcessError, OSError, json.JSONDecodeError) as exc:
        if getattr(args, "quiet", False):
            print(str(exc), file=sys.stderr)
        else:
            print(f"Drive backup gate: ERROR — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
