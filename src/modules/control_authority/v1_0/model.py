# SPDX-License-Identifier: GPL-3.0-or-later
"""Fail-closed provider choices for hardware control ownership."""

from __future__ import annotations

from dataclasses import dataclass
import sys


@dataclass(frozen=True, slots=True)
class AuthorityChoice:
    key: str
    label: str
    ohc_writes: bool
    available: bool = True


def authority_choices(domain: str, platform: str | None = None) -> tuple[AuthorityChoice, ...]:
    windows = (platform or sys.platform).casefold().startswith("win")
    # Windows commonly starts vendor RGB/GPU suites at login. Until their
    # ownership is positively ruled out, automatic mode is deliberately
    # read-only. Users can explicitly select the OHC provider below.
    common = [AuthorityChoice(
        "auto",
        "Automatisch (Konfliktschutz)" if windows else "Automatisch (empfohlen)",
        not windows,
    )]
    if domain == "rgb":
        common.extend((
            AuthorityChoice("ohc_openrgb", "OHC über OpenRGB", True),
            AuthorityChoice("signalrgb", "SignalRGB", False, windows),
            AuthorityChoice("icue", "Corsair iCUE", False, windows),
            AuthorityChoice("dynamic_lighting", "Windows Dynamic Lighting", False, windows),
            AuthorityChoice("manufacturer", "Herstellerprogramm", False),
        ))
    elif domain == "lcd":
        common.extend((
            AuthorityChoice("ohc_trcc", "OHC über TRCC", True),
            AuthorityChoice("manufacturer", "Thermalright-Herstellerprogramm", False, windows),
        ))
    elif domain == "cooling":
        common.extend((
            AuthorityChoice("ohc", "Open Hardware Control", True, not windows),
            AuthorityChoice("coolercontrol", "CoolerControl", False, not windows),
            AuthorityChoice("manufacturer", "Herstellerprogramm", False),
        ))
    elif domain == "gpu":
        common.extend((
            AuthorityChoice("ohc_lact", "OHC über LACT", True, not windows),
            AuthorityChoice("amd_adrenalin", "AMD Software: Adrenalin", False, windows),
            AuthorityChoice("nvidia", "NVIDIA-Software", False, windows),
            AuthorityChoice("manufacturer", "Herstellerprogramm", False),
        ))
    elif domain == "wallpaper":
        common.extend((
            AuthorityChoice("ohc_wallpaper", "OHC über Wallpaper Engine", True),
            AuthorityChoice("wallpaper_engine", "Wallpaper Engine direkt", False),
        ))
    common.append(AuthorityChoice("monitor", "Nur überwachen", False))
    return tuple(common)


def normalize_authority(domain: str, value: object, platform: str | None = None) -> str:
    requested = str(value or "auto").strip().casefold()
    choices = authority_choices(domain, platform)
    valid = {choice.key for choice in choices if choice.available}
    return requested if requested in valid else "monitor"


def ohc_may_write(domain: str, value: object, platform: str | None = None) -> bool:
    selected = normalize_authority(domain, value, platform)
    return next(choice.ohc_writes for choice in authority_choices(domain, platform) if choice.key == selected)
