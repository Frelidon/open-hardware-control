#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only status inspection for the MSI VRR Hardware Fix profile."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess

from .profile import (
    CORRECTED_EDID_SHA256, FIRMWARE_PATH, KERNEL_PARAMETER,
    STATE_ROOT, os_family, sha256_file, validate_profile_assets,
)


@dataclass(frozen=True)
class HardwareFixStatus:
    os_family: str
    resources_valid: bool
    monitor_connectors: tuple[str, ...]
    monitor_original: bool
    corrected_edid_loaded: bool
    firmware_present: bool
    firmware_valid: bool
    boot_parameter_running: bool
    boot_configuration_present: bool
    automation_installed: bool
    automation_active: bool
    selected_provider: str
    actual_provider: str
    reboot_required: bool
    detail: str


def _read(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError:
        return b""


def _is_profile_monitor(data: bytes) -> bool:
    """Match model identity while intentionally ignoring the EDID serial descriptor."""

    return (
        len(data) == 384
        and data[:8] == b"\x00\xff\xff\xff\xff\xff\xff\x00"
        and data[8:12] == bytes.fromhex("3669f05c")
        and b"MAG 274 X30MV" in data[:128]
        and all(sum(data[index:index + 128]) % 256 == 0 for index in range(0, 384, 128))
    )


def _contains_parameter(path: Path) -> bool:
    try:
        return KERNEL_PARAMETER in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def _provider_metadata() -> tuple[str, str]:
    selected = "local"
    actual = "local"
    path = STATE_ROOT / "provider.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        candidate = str(raw.get("selected") or "")
        if candidate in {"local", "open_hardware_control"}:
            selected = candidate
        candidate = str(raw.get("actual") or "")
        if candidate in {"local", "open_hardware_control"}:
            actual = candidate
    except (OSError, ValueError, TypeError):
        pass
    return selected, actual


def inspect_status() -> HardwareFixStatus:
    valid, asset_detail = validate_profile_assets()
    connectors: list[str] = []
    original = False
    corrected = False
    for edid_path in sorted(Path("/sys/class/drm").glob("card*-*/edid")):
        data = _read(edid_path)
        if not _is_profile_monitor(data):
            continue
        connectors.append(edid_path.parent.name)
        original = original or data[0x64] == 0
        corrected = corrected or data[0x64] == 1
    firmware_present = FIRMWARE_PATH.is_file()
    try:
        firmware_valid = firmware_present and sha256_file(FIRMWARE_PATH) == CORRECTED_EDID_SHA256
    except OSError:
        firmware_valid = False
    running = _contains_parameter(Path("/proc/cmdline"))
    configured = any(_contains_parameter(path) for path in (
        Path("/etc/default/grub"), Path("/etc/kernel/cmdline"),
        Path("/etc/default/grub.d/99-msi-vrr.cfg"),
    ))
    unit = Path.home() / ".config/systemd/user/msi-vrr-games.service"
    try:
        automation_installed = unit.is_file() and "MSI VRR Ubuntu automation" in unit.read_text(
            encoding="utf-8", errors="replace"
        )
    except OSError:
        automation_installed = False
    automation_active = False
    if automation_installed:
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "msi-vrr-games.service"],
                capture_output=True, text=True, timeout=3, check=False,
            )
            automation_active = result.returncode == 0 and result.stdout.strip() == "active"
        except (OSError, subprocess.TimeoutExpired):
            pass
    selected, actual = _provider_metadata()
    if automation_installed and not (STATE_ROOT / "provider.json").exists():
        actual = "local"
    reboot_required = configured != running or (firmware_valid and running and not corrected)
    detail = asset_detail
    if not connectors:
        detail += " Passende EDID ist derzeit an keinem DRM-Anschluss lesbar."
    return HardwareFixStatus(
        os_family(), valid, tuple(connectors), original, corrected,
        firmware_present, firmware_valid, running, configured,
        automation_installed, automation_active, selected, actual,
        reboot_required, detail,
    )


def status_json() -> str:
    return json.dumps(asdict(inspect_status()), ensure_ascii=False, sort_keys=True)
