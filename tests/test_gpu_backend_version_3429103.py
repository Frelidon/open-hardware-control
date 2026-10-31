"""The LACT package version is checked without invoking its unsupported --version flag."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.gpu_control.v1_0.client import LactError  # noqa: E402
from modules.gpu_control.v1_0 import version  # noqa: E402


@pytest.mark.parametrize("installed,accepted", [
    ("0.10.1", True), ("0.11.0", True), ("0.10.0", False), ("garbage", False),
])
def test_gpu_write_checks_installed_package_version(monkeypatch, installed, accepted) -> None:
    monkeypatch.setattr(version.shutil, "which", lambda command: f"/usr/bin/{command}" if command in {"lact", "rpm"} else None)
    commands = []

    def query(command, **_kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout=installed)

    monkeypatch.setattr(version.subprocess, "run", query)
    if accepted:
        version.require_supported_version()
    else:
        with pytest.raises(LactError):
            version.require_supported_version()
    assert commands == [("rpm", "-q", "--qf", "%{VERSION}", "lact")]


def test_install_script_accepts_copr_package_without_cli_version(tmp_path: Path) -> None:
    script = (ROOT / "packaging/install-lact.sh").read_text(encoding="utf-8")
    os_release = tmp_path / "os-release"
    os_release.write_text("ID=fedora\n", encoding="utf-8")
    script = script.replace("/etc/os-release", str(os_release))
    installed_script = tmp_path / "install-lact.sh"
    installed_script.write_text(script, encoding="utf-8")
    binary_dir = tmp_path / "bin"
    binary_dir.mkdir()
    for name, body in (
        ("lact", "exit 0"),
        ("rpm", 'printf "%s\\n" "$TEST_LACT_PACKAGE_VERSION"'),
        ("systemctl", "exit 0"),
    ):
        program = binary_dir / name
        program.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        program.chmod(0o755)
    for installed, expected in (("0.10.1", 0), ("0.10.0", 10)):
        env = dict(os.environ, PATH=f"{binary_dir}:{os.environ['PATH']}",
                   TEST_LACT_PACKAGE_VERSION=installed)
        check = subprocess.run(["bash", str(installed_script), "--check"],
                               env=env, capture_output=True, text=True, check=False)
        assert check.returncode == expected
        assert check.stdout.strip() == "fedora"


def test_lact_installer_has_checksum_verified_ubuntu_2604_path() -> None:
    script = (ROOT / "packaging/install-lact.sh").read_text(encoding="utf-8")
    assert "ubuntu) family=ubuntu" in script
    assert "lact-0.10.1-0.amd64.ubuntu-2604.deb" in script
    assert "b8006a0d7e414de08f193760a82d346c7308675747ae928501941ac714b59fd3" in script
    assert "sha256sum -c -" in script
