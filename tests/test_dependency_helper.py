#!/usr/bin/env python3
"""Checks for optional KDE desktop dependency detection."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "packaging/install-dependencies.sh"


def write_command(directory: Path, name: str) -> None:
    target = directory / name
    target.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    target.chmod(0o755)


with tempfile.TemporaryDirectory(prefix="ohc-dependency-test-") as temporary:
    fake_bin = Path(temporary)
    write_command(fake_bin, "kwriteconfig6")
    write_command(fake_bin, "qdbus-qt6")
    env = {**os.environ, "PATH": f"{fake_bin}:/usr/bin:/bin"}
    result = subprocess.run(
        [str(HELPER), "--check-desktop"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert result.returncode in {0, 10}, result.stderr or result.stdout
    if result.returncode == 10:
        assert "python3-pyside6.qtnetwork" in result.stdout
        assert "python3-pyside6.qtdbus" in result.stdout

    write_command(fake_bin, "openrgb")
    result = subprocess.run(
        [str(HELPER), "--check-openrgb"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr or result.stdout

    (fake_bin / "qdbus-qt6").unlink()
    write_command(fake_bin, "qdbus6")
    result = subprocess.run(
        [str(HELPER), "--check-desktop"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert result.returncode in {0, 10}, result.stderr or result.stdout
    if result.returncode == 10:
        assert "python3-pyside6.qtnetwork" in result.stdout
        assert "python3-pyside6.qtdbus" in result.stdout

with tempfile.TemporaryDirectory(prefix="ohc-fedora-openrgb-test-") as temporary:
    fake_bin = Path(temporary)
    write_command(fake_bin, "dnf")
    write_command(fake_bin, "openrgb")
    rpm = fake_bin / "rpm"
    rpm.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    rpm.chmod(0o755)
    env = {**os.environ, "PATH": f"{fake_bin}:/usr/bin:/bin"}
    result = subprocess.run(
        [str(HELPER), "--check-openrgb"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 10, result.stderr or result.stdout
    assert "openrgb-udev-rules" in result.stdout

source = HELPER.read_text(encoding="utf-8")
assert "qdbus-qt6" in source
assert "/usr/lib64/qt6/bin/qdbus" in source
assert "--check-desktop" in source
assert "--install-desktop" in source
assert "--check-openrgb" in source
assert "--install-openrgb" in source
assert "openrgb-udev-rules" in source
assert shutil.which("bash") is not None

print("Desktop dependency helper checks passed.")
