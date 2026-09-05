from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from backup_release import backup_release


def _fake_release(project: Path, version: str) -> Path:
    dist = project / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    for path in dist.iterdir():
        path.unlink()
    names = (
        f"open_hardware_control_v{version.replace('.', '_')}_INTERN.zip",
        f"Entwicklerpaket {version} INTERN.zip",
        f"open-hardware-control-{version}-INTERN-source.tar.gz",
        f"Open_Hardware_Control_{version}_INTERN_LOCAL_AI.gitbundle",
        f"open-hardware-control-{version}-0.intern2.noarch.rpm",
    )
    for name in names:
        (dist / name).write_bytes(f"artifact {version} {name}".encode())
    notes = project / "docs" / f"RELEASE_NOTES_v{version}.md"
    notes.parent.mkdir(parents=True, exist_ok=True)
    notes.write_text(f"# {version}\n", encoding="utf-8")
    return dist


def test_release_backup_retains_two_complete_version_sets(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    backup_root = tmp_path / "Open Hardware Control Backup"
    backup_root.mkdir()
    marker = backup_root / "README.txt"
    marker.write_text("unrelated and preserved", encoding="utf-8")

    for version in ("3.4.29.34", "3.4.29.35", "3.4.29.36"):
        dist = _fake_release(project, version)
        target = backup_release(
            project, dist, version, "INTERN", backup_root=backup_root,
        )
        assert target.is_dir()

    versions = sorted(path.name for path in backup_root.glob("Version *"))
    assert versions == ["Version 3.4.29.35 INTERN", "Version 3.4.29.36 INTERN"]
    assert marker.read_text(encoding="utf-8") == "unrelated and preserved"
    newest = backup_root / "Version 3.4.29.36 INTERN"
    assert (newest / "Entwicklerpaket 3.4.29.36 INTERN.zip").is_file()
    assert (newest / "open-hardware-control-3.4.29.36-0.intern2.noarch.rpm").is_file()
    checks = (newest / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    for line in checks:
        expected, filename = line.split("  ", 1)
        assert hashlib.sha256((newest / filename).read_bytes()).hexdigest() == expected


def test_release_backup_must_stay_outside_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    dist = _fake_release(project, "3.4.29.36")
    with pytest.raises(ValueError, match="außerhalb"):
        backup_release(project, dist, "3.4.29.36", "INTERN", backup_root=project / "backup")


def test_release_backup_rejects_incomplete_release(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    dist = _fake_release(project, "3.4.29.36")
    (dist / "Entwicklerpaket 3.4.29.36 INTERN.zip").unlink()
    with pytest.raises(ValueError, match="Entwicklerpaket"):
        backup_release(
            project, dist, "3.4.29.36", "INTERN",
            backup_root=tmp_path / "Open Hardware Control Backup",
        )
