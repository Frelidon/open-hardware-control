# SPDX-License-Identifier: GPL-3.0-or-later
"""Conservative CoolerControl GPU-fan ownership check; no config writes."""
from __future__ import annotations

import json
from pathlib import Path
import tomllib

from cooling_ownership import detect_cooling_owner


def coolercontrol_gpu_claim(
    config_path: Path = Path("/etc/coolercontrol/config.toml"),
    modes_path: Path = Path("/etc/coolercontrol/modes.json"),
) -> tuple[bool, str]:
    """True means LACT writes must wait for a visible Unmanaged handoff."""
    if not detect_cooling_owner().coolercontrol_active:
        return False, "CoolerControl service is inactive"
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        modes = json.loads(modes_path.read_text(encoding="utf-8")) if modes_path.exists() else {}
    except (OSError, ValueError, TypeError):
        return True, "CoolerControl GPU ownership could not be verified"
    devices = config.get("devices")
    assignments = config.get("device-settings")
    if not isinstance(devices, dict) or not isinstance(assignments, dict):
        return True, "CoolerControl configuration format is unknown"
    gpu_ids = {
        uid for uid, name in devices.items()
        if isinstance(name, str) and (
            "amdgpu" in name.casefold() or "radeon" in name.casefold()
            or "geforce" in name.casefold() or "nvidia" in name.casefold()
            or name.casefold().startswith("gpu ")
        )
    }
    if any(bool(assignments.get(uid)) for uid in gpu_ids):
        return True, "CoolerControl has GPU channel settings"
    mode_rows = modes.get("modes", []) if isinstance(modes, dict) else []
    if not isinstance(mode_rows, list):
        return True, "CoolerControl mode format is unknown"
    for mode in mode_rows:
        saved = mode.get("all_device_settings", {}) if isinstance(mode, dict) else None
        if not isinstance(saved, dict):
            return True, "CoolerControl mode settings are unknown"
        if any(bool(saved.get(uid)) for uid in gpu_ids):
            return True, "A CoolerControl mode still has GPU fan settings"
    return False, "CoolerControl has no configured GPU fan channel"
