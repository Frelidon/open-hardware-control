#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Keep the two newest complete OHC release sets outside the worktree."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import shutil
import tempfile


BACKUP_DIRECTORY_NAME = "Open Hardware Control Backup"
BACKUP_FOLDER_PATTERN = re.compile(
    r"^Version (?P<version>\d+\.\d+\.\d+(?:\.\d+)?) (?P<channel>INTERN|STABLE)$"
)
MINIMUM_RETAINED_VERSIONS = 2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def version_key(version: str) -> tuple[int, ...]:
    parts = version.split(".")
    if len(parts) not in {3, 4} or not all(part.isdigit() for part in parts):
        raise ValueError(f"Ungültige Backup-Version: {version!r}")
    return tuple(int(part) for part in parts)


def _release_artifacts(dist: Path, version: str) -> list[Path]:
    dotted = version
    underscored = version.replace(".", "_")
    artifacts = [
        path for path in sorted(dist.iterdir())
        if path.is_file()
        and not path.is_symlink()
        and path.name != "SHA256SUMS"
        and (dotted in path.name or underscored in path.name)
    ]
    names = [path.name.casefold() for path in artifacts]
    required = {
        "Laufzeit-ZIP": any(name.startswith("open_hardware_control_v") and name.endswith(".zip") for name in names),
        "Entwicklerpaket": any(name.startswith("entwicklerpaket ") and name.endswith(".zip") for name in names),
        "Quellarchiv": any(name.endswith("-source.tar.gz") for name in names),
        "Local-AI-Gitbundle": any(name.endswith(".gitbundle") for name in names),
    }
    missing = [label for label, present in required.items() if not present]
    if missing:
        raise ValueError("Unvollständiger Release-Satz: " + ", ".join(missing))
    return artifacts


def _backup_entries(backup_root: Path) -> list[tuple[tuple[int, ...], Path]]:
    entries: list[tuple[tuple[int, ...], Path]] = []
    for path in backup_root.iterdir():
        if not path.is_dir() or path.is_symlink():
            continue
        match = BACKUP_FOLDER_PATTERN.fullmatch(path.name)
        if match:
            entries.append((version_key(match.group("version")), path))
    return sorted(entries, key=lambda item: item[0], reverse=True)


def backup_release(
    project_root: Path,
    dist: Path,
    version: str,
    channel: str,
    *,
    backup_root: Path | None = None,
    keep: int = MINIMUM_RETAINED_VERSIONS,
) -> Path:
    """Atomically archive one complete release and retain the newest two."""

    project = project_root.resolve()
    source = dist.resolve()
    destination_root = (
        backup_root.resolve()
        if backup_root is not None
        else project.parent / BACKUP_DIRECTORY_NAME
    )
    if destination_root == project or project in destination_root.parents:
        raise ValueError("Der Release-Backupordner muss außerhalb des Arbeitsbaums liegen")
    normalized_channel = channel.strip().upper()
    if normalized_channel not in {"INTERN", "STABLE"}:
        raise ValueError(f"Ungültiger Release-Kanal: {channel!r}")
    version_key(version)
    if not source.is_dir():
        raise ValueError(f"Release-Ordner fehlt: {source}")
    artifacts = _release_artifacts(source, version)

    destination_root.mkdir(parents=True, exist_ok=True)
    target = destination_root / f"Version {version} {normalized_channel}"
    with tempfile.TemporaryDirectory(
        prefix=f".ohc-backup-{version}-", dir=destination_root,
    ) as staging_name:
        staging = Path(staging_name)
        for artifact in artifacts:
            shutil.copy2(artifact, staging / artifact.name)
        notes = project / "docs" / f"RELEASE_NOTES_v{version}.md"
        if notes.is_file() and not notes.is_symlink():
            shutil.copy2(notes, staging / notes.name)
        info = (
            f"Open Hardware Control {version} {normalized_channel}\n"
            f"Erstellt (UTC): {datetime.now(timezone.utc).isoformat()}\n"
            "Inhalt: vollständiges Entwicklerpaket, Laufzeitpaket, Quellarchiv, "
            "Local-AI-Gitbundle sowie alle für diese Version erzeugten RPM-/DEB-Pakete.\n"
        )
        (staging / "BACKUP_INFO.txt").write_text(info, encoding="utf-8")
        checksum_files = sorted(
            path for path in staging.iterdir()
            if path.is_file() and path.name != "SHA256SUMS"
        )
        (staging / "SHA256SUMS").write_text(
            "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_files),
            encoding="utf-8",
        )
        if target.exists():
            if target.is_symlink() or not target.is_dir():
                raise ValueError(f"Unsicheres vorhandenes Backupziel: {target}")
            shutil.rmtree(target)
        staging.rename(target)

    retained = max(MINIMUM_RETAINED_VERSIONS, int(keep))
    for _key, obsolete in _backup_entries(destination_root)[retained:]:
        shutil.rmtree(obsolete)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("channel")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--backup-root", type=Path)
    args = parser.parse_args()
    target = backup_release(
        args.project_root,
        args.dist,
        args.version,
        args.channel,
        backup_root=args.backup_root,
    )
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
