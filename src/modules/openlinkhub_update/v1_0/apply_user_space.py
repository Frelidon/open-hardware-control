#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Apply one prepared OpenLinkHub user-service update with rollback."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time


SERVICE_NAME = "OpenLinkHub.service"


def _run_systemctl(action: str) -> None:
    result = subprocess.run(
        ["systemctl", "--user", action, SERVICE_NAME],
        capture_output=True, text=True, timeout=20, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"systemctl --user {action} failed")


def _installation_directory() -> Path:
    service = Path.home() / ".config/systemd/user/OpenLinkHub.service"
    if service.is_symlink() or not service.is_file():
        raise RuntimeError("safe OpenLinkHub user service was not found")
    text = service.read_text(encoding="utf-8")
    working_match = re.search(r"(?m)^WorkingDirectory=([^\n\r]+)$", text)
    executable_match = re.search(r"(?m)^ExecStart=([^\s\n\r]+)$", text)
    if not working_match or not executable_match:
        raise RuntimeError("OpenLinkHub user service has no unambiguous paths")
    home = Path.home().resolve()
    working = Path(working_match.group(1)).expanduser().resolve()
    executable = Path(executable_match.group(1)).expanduser().resolve()
    try:
        working.relative_to(home)
    except ValueError as exc:
        raise RuntimeError("OpenLinkHub user installation is outside the home directory") from exc
    if executable != working / "OpenLinkHub" or working.is_symlink() or not executable.is_file() or executable.is_symlink():
        raise RuntimeError("OpenLinkHub user installation paths are unsafe")
    return working


def _preserve_user_data(backup: Path, installed: Path) -> None:
    for filename in ("config.json", "dashboard.json", "display.json"):
        source = backup / filename
        if source.is_file() and not source.is_symlink():
            shutil.copy2(source, installed / filename)
    database = backup / "database"
    if database.is_dir() and not database.is_symlink():
        shutil.copytree(database, installed / "database", dirs_exist_ok=True, symlinks=False)


def apply_update(stage: Path, cache_root: Path) -> dict[str, object]:
    root = cache_root.expanduser().resolve()
    candidate = stage.expanduser().resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("prepared OpenLinkHub update is outside the private cache") from exc
    if candidate.is_symlink() or not (candidate / "OpenLinkHub").is_file() or not (candidate / "web").is_dir():
        raise RuntimeError("prepared OpenLinkHub update is incomplete")
    installed = _installation_directory()
    if installed.parent.stat().st_dev != candidate.stat().st_dev:
        raise RuntimeError("OpenLinkHub update staging and installation must be on the same filesystem")
    suffix = f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
    backup = installed.with_name(f".{installed.name}-ohc-backup-{suffix}")
    failed = installed.with_name(f".{installed.name}-ohc-failed-{suffix}")
    _run_systemctl("stop")
    installed.rename(backup)
    try:
        candidate.rename(installed)
        (installed / "OpenLinkHub").chmod(0o755)
        _preserve_user_data(backup, installed)
        _run_systemctl("daemon-reload")
        _run_systemctl("start")
    except Exception:
        try:
            if installed.exists():
                installed.rename(failed)
            if backup.exists():
                backup.rename(installed)
            _run_systemctl("daemon-reload")
            _run_systemctl("start")
        except Exception as rollback_error:
            raise RuntimeError(f"update failed and rollback also failed: {rollback_error}")
        raise
    return {"ok": True, "backup": str(backup), "installed": str(installed)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload: dict[str, object] = apply_update(args.stage, args.cache_root)
        payload["ok"] = True
    except Exception as exc:
        payload = {"ok": False, "error": str(exc)[:500]}
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
