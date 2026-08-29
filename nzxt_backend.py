#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""NZXT device registry and capability model for Open Hardware Control.

The GUI intentionally uses liquidctl for supported Kraken commands.  This
module centralizes USB identification and per-generation capabilities so newer
Kraken models can be added without hard-coding one product throughout the UI.
Raw/experimental RGB transports remain explicitly gated until verified on real
hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

NZXT_USB_VENDOR_ID = "1e71"


class SupportLevel(str, Enum):
    SUPPORTED = "supported"
    EXPERIMENTAL = "experimental"
    DETECTION_ONLY = "detection-only"


@dataclass(frozen=True)
class KrakenCapabilities:
    liquid_temperature: bool = True
    pump_rpm: bool = True
    pump_control: bool = True
    fan_rpm: bool = True
    fan_control: bool = True
    hardware_fan_curves: bool = True
    lcd_static: bool = True
    lcd_gif: bool = True
    lcd_temperature: bool = True
    lcd_brightness: bool = True
    lcd_rotation: bool = True
    pump_rgb: bool = False
    fan_rgb: bool = False
    hue2_direct: bool = False


@dataclass(frozen=True)
class KrakenDeviceProfile:
    product_id: str
    liquidctl_name: str
    display_name: str
    lcd_resolution: str
    support: SupportLevel
    capabilities: KrakenCapabilities
    notes: str = ""

    @property
    def allows_writes(self) -> bool:
        return self.support != SupportLevel.DETECTION_ONLY


KRAKEN_2023_CAPS = KrakenCapabilities()
KRAKEN_2024_ELITE_CAPS = KrakenCapabilities(
    pump_rgb=True,
    fan_rgb=True,
    hue2_direct=True,
)
KRAKEN_PLUS_CAPS = KrakenCapabilities()

KRAKEN_DEVICES: tuple[KrakenDeviceProfile, ...] = (
    KrakenDeviceProfile(
        product_id="300e",
        liquidctl_name="NZXT Kraken 2023",
        display_name="NZXT Kraken 2023",
        lcd_resolution="240 × 240",
        support=SupportLevel.SUPPORTED,
        capabilities=KRAKEN_2023_CAPS,
    ),
    KrakenDeviceProfile(
        product_id="300c",
        liquidctl_name="NZXT Kraken 2023 Elite",
        display_name="NZXT Kraken 2023 Elite",
        lcd_resolution="640 × 640",
        support=SupportLevel.DETECTION_ONLY,
        capabilities=KrakenCapabilities(
            pump_control=False,
            fan_control=False,
            hardware_fan_curves=False,
            lcd_static=False,
            lcd_gif=False,
            lcd_brightness=False,
            lcd_rotation=False,
        ),
        notes="liquidctl marks USB 1e71:300c as broken; detection is safe, writes stay disabled.",
    ),
    KrakenDeviceProfile(
        product_id="3012",
        liquidctl_name="NZXT Kraken 2024 Elite RGB",
        display_name="NZXT Kraken Elite 2024 RGB",
        lcd_resolution="640 × 640",
        support=SupportLevel.SUPPORTED,
        capabilities=KRAKEN_2024_ELITE_CAPS,
        notes=(
            "Cooling and LCD are supported through liquidctl. Embedded ring/fan RGB is kept "
            "experimental in OHC until its channel mapping is verified on real hardware."
        ),
    ),
    KrakenDeviceProfile(
        product_id="3014",
        liquidctl_name="NZXT Kraken 2024 Plus",
        display_name="NZXT Kraken Plus",
        lcd_resolution="240 × 240",
        support=SupportLevel.SUPPORTED,
        capabilities=KRAKEN_PLUS_CAPS,
    ),
)

BY_PRODUCT_ID = {profile.product_id: profile for profile in KRAKEN_DEVICES}
NZXT_LIQUIDCTL_PRODUCT_IDS = frozenset((*BY_PRODUCT_ID, "2012"))


def detect_profile_from_liquidctl_output(output: str) -> KrakenDeviceProfile | None:
    """Return the most specific known Kraken mentioned by liquidctl output."""
    text = output.casefold()
    # Long/specific names first so the generic 2023 name cannot shadow Elite.
    for profile in sorted(KRAKEN_DEVICES, key=lambda item: len(item.liquidctl_name), reverse=True):
        if profile.liquidctl_name.casefold() in text:
            return profile
    return None


def detect_profile_from_sysfs(root: Path = Path("/sys/bus/usb/devices")) -> KrakenDeviceProfile | None:
    """Best-effort USB-ID detection without opening the device."""
    try:
        entries = sorted(root.iterdir())
    except OSError:
        return None
    for entry in entries:
        try:
            vendor_path = entry / "idVendor"
            product_path = entry / "idProduct"
            if not vendor_path.exists() or not product_path.exists():
                continue
            vendor = vendor_path.read_text(encoding="ascii").strip().lower()
            product = product_path.read_text(encoding="ascii").strip().lower()
        except OSError:
            continue
        if vendor == NZXT_USB_VENDOR_ID and product in BY_PRODUCT_ID:
            return BY_PRODUCT_ID[product]
    return None


def nzxt_liquidctl_device_present(root: Path = Path("/sys/bus/usb/devices")) -> bool:
    """Return whether a known Kraken or NZXT 2023 RGB controller is present."""

    try:
        entries = sorted(root.iterdir())
    except OSError:
        return False
    for entry in entries:
        try:
            vendor = (entry / "idVendor").read_text(encoding="ascii").strip().lower()
            product = (entry / "idProduct").read_text(encoding="ascii").strip().lower()
        except OSError:
            continue
        if vendor == NZXT_USB_VENDOR_ID and product in NZXT_LIQUIDCTL_PRODUCT_IDS:
            return True
    return False


def detected_profile(output: str = "") -> KrakenDeviceProfile | None:
    """Prefer liquidctl's identity and fall back to non-invasive sysfs probing."""
    return detect_profile_from_liquidctl_output(output) or detect_profile_from_sysfs()


def udev_product_ids() -> tuple[str, ...]:
    return tuple(profile.product_id for profile in KRAKEN_DEVICES)
