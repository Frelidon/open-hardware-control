#!/usr/bin/env python3
"""Dependency-free checks for the reversible KDE desktop-design module."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import desktop_designs as designs


for style in designs.SUPPORTED_STYLES:
    for mode in designs.SUPPORTED_MODES:
        plan = designs.design_plan(style, mode)
        assert plan["ok"] is True
        assert plan["reversible"] is True
        assert len(plan["changes"]) >= 8
        assert any("keine Pakete" in item for item in plan["changes"])

assert "new Panel" in designs._panel_script("windows11", Path("/tmp/wall.svg"))
assert 'location = "top"' in designs._panel_script("macos", Path("/tmp/wall.svg"))
assert 'location = "bottom"' in designs._panel_script("macos", Path("/tmp/wall.svg"))

# Backup/restore logic is tested in an isolated directory. Do not let a locally
# installed OHC desktop-shell instance participate in this unit test.
with tempfile.TemporaryDirectory(prefix="ohc-desktop-design-test-") as temporary, patch(
    "desktop_designs._stop_shell_integration"
):
    root = Path(temporary)
    config = root / "config"
    state = root / "state"
    config.mkdir()
    (config / "kdeglobals").write_text("original\n", encoding="utf-8")
    env = {
        **os.environ,
        "OHC_DESKTOP_DESIGN_CONFIG_DIR": str(config),
        "OHC_DESKTOP_DESIGN_STATE_DIR": str(state),
    }
    with patch.dict(os.environ, env, clear=True):
        backup = designs.create_backup()
        assert designs.latest_backup_path() == backup.resolve()
        manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["schema"] == designs.SCHEMA_VERSION
        assert manifest["config_files"]["kdeglobals"] is True
        assert manifest["config_files"]["kwinrc"] is False

        (config / "kdeglobals").write_text("changed\n", encoding="utf-8")
        (config / "kwinrc").write_text("created later\n", encoding="utf-8")
        designs._restore_from_backup(backup)
        assert (config / "kdeglobals").read_text(encoding="utf-8") == "original\n"
        assert not (config / "kwinrc").exists()

        exported = root / "design.zip"
        result = designs.export_backup(backup.name, exported)
        assert result["ok"] is True and exported.is_file()
        imported = designs.import_backup(exported)
        assert imported["ok"] is True
        assert any(item["id"] == imported["id"] for item in designs.list_backups())

        assert designs.set_backup_retention(2)["backup_retention"] == 2
        assert designs.backup_retention() == 2
        try:
            designs.set_backup_retention(0)
        except designs.DesktopDesignError:
            pass
        else:
            raise AssertionError("unsafe retention value accepted")

        malicious = root / "malicious.zip"
        with zipfile.ZipFile(malicious, "w") as archive:
            archive.writestr("ohc-design-backup/../../outside", "bad")
        try:
            designs.import_backup(malicious)
        except designs.DesktopDesignError:
            pass
        else:
            raise AssertionError("path traversal archive accepted")

        outside = root / "outside"
        outside.mkdir()
        (outside / "manifest.json").write_text("{}", encoding="utf-8")
        (state / "latest-backup").write_text(str(outside), encoding="utf-8")
        assert designs.latest_backup_path() is None

with patch("desktop_designs.shutil.which", side_effect=lambda name: f"/usr/bin/{name}"), patch.dict(
    os.environ,
    {"XDG_CURRENT_DESKTOP": "KDE", "KDE_FULL_SESSION": "true"},
    clear=False,
):
    status = designs.desktop_status()
    assert status["compatible"] is True
    assert status["requires_root"] is False
    assert status["uses_external_downloads"] is False

# Fedora 44 ships the Qt 6 D-Bus tool as qdbus-qt6 instead of qdbus6.
def fedora_which(name: str) -> str | None:
    return {
        "kwriteconfig6": "/usr/bin/kwriteconfig6",
        "qdbus-qt6": "/usr/bin/qdbus-qt6",
    }.get(name)


with patch("desktop_designs.shutil.which", side_effect=fedora_which), patch.dict(
    os.environ,
    {"XDG_CURRENT_DESKTOP": "KDE", "KDE_FULL_SESSION": "true"},
    clear=False,
):
    assert designs.resolve_qdbus6() == "/usr/bin/qdbus-qt6"
    status = designs.desktop_status()
    assert status["compatible"] is True
    assert status["missing_commands"] == []
    assert status["resolved_commands"]["qdbus (Qt 6)"] == "/usr/bin/qdbus-qt6"

source = Path(designs.__file__).read_text(encoding="utf-8")
assert "shell=True" not in source
assert "curl " not in source
assert "git clone" not in source
assert "windows8" in designs.SUPPORTED_STYLES and "windows81" in designs.SUPPORTED_STYLES
print("Desktop-design safety and backup checks passed.")
