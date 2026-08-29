#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Safe motherboard-PWM cooling support for Thermalright Levita Vision.

The Levita display and cooling wiring are deliberately separate: USB carries
display data, while pump and radiator fans use motherboard 4-pin PWM headers.
This module performs read-only identification and channel-role suggestions.
It never authorizes a PWM write; the user must physically confirm both mapped
headers in the existing OHC calibration flow first.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol


THERMALRIGHT_USB_VENDOR_ID = "87ad"
THERMALRIGHT_USB_PRODUCT_ID = "70db"
LEVITA_COOLER_KEY = "thermalright-levita-vision-360-argb-black"
LEVITA_DISPLAY_NAME = "Thermalright Levita Vision 360 ARGB Black"


class FanChannelLike(Protocol):
    stable_id: str
    display_name: str
    rpm: int | None


@dataclass(frozen=True, slots=True)
class AioChannelSuggestion:
    pump_channel_id: str = ""
    radiator_channel_id: str = ""

    @property
    def complete(self) -> bool:
        return bool(self.pump_channel_id and self.radiator_channel_id)


def thermalright_display_present(root: Path = Path("/sys/bus/usb/devices")) -> bool:
    """Detect the shared Levita display USB id without opening or writing it."""
    try:
        entries = sorted(root.iterdir())
    except OSError:
        return False
    for entry in entries:
        try:
            vendor = (entry / "idVendor").read_text(encoding="ascii").strip().casefold()
            product = (entry / "idProduct").read_text(encoding="ascii").strip().casefold()
        except OSError:
            continue
        if (vendor, product) == (THERMALRIGHT_USB_VENDOR_ID, THERMALRIGHT_USB_PRODUCT_ID):
            return True
    return False


def aio_channel_role(label: str) -> str | None:
    """Classify driver-provided header labels, never a board-model guess."""
    normalized = " ".join(str(label).replace("_", " ").replace("-", " ").casefold().split())
    if "pump" in normalized or "pumpe" in normalized or "aio" in normalized:
        return "pump"
    if "cpu fan" in normalized or "cpu lüfter" in normalized:
        return "radiator"
    return None


def suggest_aio_channels(channels: Iterable[FanChannelLike]) -> AioChannelSuggestion:
    """Suggest label-matched headers; physical confirmation remains mandatory."""
    pump = ""
    radiator = ""
    for channel in channels:
        role = aio_channel_role(channel.display_name)
        if role == "pump" and not pump:
            pump = channel.stable_id
        elif role == "radiator" and not radiator:
            radiator = channel.stable_id
    return AioChannelSuggestion(pump, radiator)


def profile_duties(name: str) -> tuple[int, int]:
    """Return conservative pump/radiator PWM percentages for the Levita."""
    values = {
        "leise": (55, 35),
        "ausbalanciert": (70, 50),
        "leistung": (90, 75),
        "sicherheit": (100, 100),
        "sicheres standardprofil": (75, 65),
    }
    return values.get(str(name).strip().casefold(), (70, 50))
