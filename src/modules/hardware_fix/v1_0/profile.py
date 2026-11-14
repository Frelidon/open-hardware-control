#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Declarative, allow-listed Hardware Fix profile definitions."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import shlex
import shutil
import sys


PROFILE_ID = "msi-mag274qpf-x30mv-vrr"
ORIGINAL_EDID_SHA256 = "e6c8562c659b080a013ac1429c198dc905a7260df54e06e53a070a195615588f"
CORRECTED_EDID_SHA256 = "7d975778662fb0f3b16aba96dbd0282a072c6b6b7fb992967f79846f82d13fdc"
KERNEL_PARAMETER = "drm.edid_firmware=DP:edid/msi-mag274qpf-x30mv-vrr.bin"
FIRMWARE_PATH = Path("/usr/lib/firmware/edid/msi-mag274qpf-x30mv-vrr.bin")
ASSET_ROOT = Path(__file__).resolve().parent / "assets" / PROFILE_ID
STATE_ROOT = Path.home() / ".local/state/open-hardware-control/hardware-fix" / PROFILE_ID


@dataclass(frozen=True)
class HardwareFixProfile:
    profile_id: str
    title: str
    vendor: str
    product: str
    original_edid_sha256: str
    corrected_edid_sha256: str
    kernel_parameter: str
    firmware_path: Path
    asset_root: Path


MSI_VRR_PROFILE = HardwareFixProfile(
    PROFILE_ID,
    "MSI MAG 274QPF X30MV – VRR",
    "MSI",
    "MAG 274 X30MV",
    ORIGINAL_EDID_SHA256,
    CORRECTED_EDID_SHA256,
    KERNEL_PARAMETER,
    FIRMWARE_PATH,
    ASSET_ROOT,
)


RESOURCE_HASHES = {
    "01-Installieren-Fedora.sh": "4e52935d95508589a5607593cef36b8fe51b71b81bf0595ecf605e416d61096d",
    "01-Installieren-Ubuntu.sh": "c6be41ee75d3cb28f6437548f3c185e19d97c902bc3733bb2503182c750838e0",
    "02-VRR-im-Desktop-aktivieren.sh": "72b4461bee1a9a70793af3247c0d0a7b8da8446b724db6122a71986bd55468b6",
    "03-VRR-Status-pruefen.sh": "37a788395b4aadf51bae22171f1690b529e1f65d87d22d6c3ddc7d81da712448",
    "04-Ruecknahme.sh": "f23c0d3dddbf850ecbbcc132e836f03e6651362e38bcb77f903f503d771e9573",
    "05-Ubuntu-VRR-Automatik.sh": "1769ac3f8750d49f0ce3329b1ad32b949490d2e3ceae0d1e85ef5df1b57b4d41",
    "EDID/original.bin": ORIGINAL_EDID_SHA256,
    "EDID/vrr-korrigiert.bin": CORRECTED_EDID_SHA256,
    "lib/auto_setup.py": "0699bcd88febdf9b0eb43eb81224a5d9d044ddc5e24f864d6bad1ed0020f3dc3",
    "lib/auto_vrr.py": "cd66fcb28c1eb1b09c3c4f4e21a6341f44480cf456479bd7123de81c6979d12a",
    "lib/desktop.py": "6f67113cce0052afc476e5e04f1c5866893ad7d1ee7ee5c74e469fc625b5d14d",
    "lib/install.py": "d6ecacc1316c43bbc7f1c8fa2b50dd915a9d154661ea3cd57d87a30c49e6a2d0",
    "lib/status.py": "4f6bf4e64fc89d335b01a169e8887ff6763df910f5f004e63b7dfd822a3bceaa",
    "lib/vrr_hardware.py": "0065b2af31fbac3b043a33c4fc36b02f42b284f5360a5d67eb7dd6882aa83974",
    "lib/x11_games.py": "ee0c26a62635e7a9d868929a544657d86b1f15d1d976f9137bbb19cbe6236664",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(131_072), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_profile_assets(profile: HardwareFixProfile = MSI_VRR_PROFILE) -> tuple[bool, str]:
    """Verify immutable EDID identity before any profile command is offered."""

    if profile.asset_root.is_symlink() or not profile.asset_root.is_dir():
        return False, "Profilressourcen fehlen oder sind eine symbolische Verknüpfung."
    for relative, expected in RESOURCE_HASHES.items():
        path = profile.asset_root / relative
        if path.is_symlink() or not path.is_file() or sha256_file(path) != expected:
            return False, f"Profilressource ist nicht unverändert: {relative}"
    return True, "Profilressourcen geprüft."


def parse_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return result
    for line in lines:
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw = line.split("=", 1)
        try:
            values = shlex.split(raw)
        except ValueError:
            values = []
        result[key] = values[0] if values else raw.strip().strip('"')
    return result


def os_family(path: Path = Path("/etc/os-release")) -> str:
    release = parse_os_release(path)
    families = {release.get("ID", ""), *release.get("ID_LIKE", "").split()}
    if "ubuntu" in families or "debian" in families:
        return "ubuntu"
    if "fedora" in families or "rhel" in families:
        return "fedora"
    return "unsupported"


def runner_argv(action: str, job_id: str | None = None) -> list[str] | None:
    allowed = {
        "preflight", "status", "install", "install-local", "desktop", "automation-install",
        "automation-status", "automation-remove", "game-test", "uninstall",
    }
    if action not in allowed:
        return None
    if job_id is not None and not re.fullmatch(r"[0-9a-f]{32}", job_id):
        return None
    runner = Path(__file__).with_name("runner.py")
    return [os.fspath(Path(sys.executable).resolve()), os.fspath(runner), action, *([job_id] if job_id else [])]


def terminal_spec(action: str, job_id: str | None = None) -> tuple[str, list[str]] | None:
    """Wrap one fixed runner action in an interactive terminal."""

    command = runner_argv(action, job_id)
    if not command:
        return None
    terminal = next(
        (shutil.which(name) for name in ("ptyxis", "konsole", "gnome-terminal", "xterm") if shutil.which(name)),
        None,
    )
    if not terminal:
        return None
    name = Path(terminal).name
    if name == "konsole":
        return terminal, ["--hold", "-e", *command]
    if name == "xterm":
        return terminal, ["-hold", "-e", *command]
    if name == "ptyxis":
        return terminal, ["--standalone", "--", *command]
    return terminal, ["--wait", "--", *command]
