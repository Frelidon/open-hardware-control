#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit OpenRGB ownership policy for RGB Studio.

The UI may render previews and store physical LED counts, but one controller
must never receive two competing control paths.  A Direct controller belongs
to OHC's one persistent software stream so the physical output uses the exact
same colours and phase as the preview.  Native hardware modes remain the
fallback for controllers that cannot accept complete software frames.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from openrgb_integration import OpenRGBDevice, best_native_mode_for_effect


@dataclass(frozen=True)
class OpenRGBControlChoice:
    device_index: int
    path: str
    mode: str = ""

    @property
    def uses_openrgb_mode(self) -> bool:
        return self.path == "native"

    @property
    def uses_ohc_stream(self) -> bool:
        return self.path == "stream"


def choose_control_path(
    device: OpenRGBDevice,
    effect_id: str,
    *,
    preferred_mode: str = "",
) -> OpenRGBControlChoice:
    """Choose exactly one owner for a controller."""

    if device.supports_direct:
        return OpenRGBControlChoice(device.index, "stream")
    mode = best_native_mode_for_effect(device, effect_id, preferred_mode)
    if mode:
        return OpenRGBControlChoice(device.index, "native", mode)
    return OpenRGBControlChoice(device.index, "unavailable")


def split_control_paths(
    devices: Iterable[OpenRGBDevice],
    effect_id: str,
) -> tuple[tuple[OpenRGBDevice, OpenRGBControlChoice], ...]:
    """Return deterministic per-device ownership decisions for one effect."""

    return tuple(
        (device, choose_control_path(device, effect_id))
        for device in sorted(devices, key=lambda item: item.index)
    )

