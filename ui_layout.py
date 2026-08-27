#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Stable, dependency-free UI layout preferences for Open Hardware Control."""

from __future__ import annotations

from collections.abc import Iterable


SECTION_DEFAULTS: dict[str, tuple[str, ...]] = {
    "rgb": ("engine", "devices_effects", "pc_layout", "groups"),
    "cooling": ("mode", "manual", "curves", "cpu_profile", "mainboard", "safety"),
    "lcd": (
        "preview",
        "display",
        "image",
        "hardware",
        "hardware_animation",
        "layers",
        "gif",
        "clock",
        "startup",
    ),
}


DASHBOARD_CARD_DEFAULTS: tuple[str, ...] = (
    "water_temperature",
    "cpu_temperature",
    "gpu_temperature",
    "pump",
    "radiator_fans",
    "firmware",
    "cpu_model",
    "cpu_topology",
    "gpu_model",
    "gpu_memory",
)


def sanitize_section_order(scope: str, stored: object) -> list[str]:
    """Return a complete, duplicate-free order for one supported page."""

    default = SECTION_DEFAULTS.get(str(scope), ())
    if isinstance(stored, str):
        candidates: Iterable[object] = stored.split(",")
    elif isinstance(stored, (list, tuple)):
        candidates = stored
    else:
        candidates = ()
    result: list[str] = []
    for value in candidates:
        key = str(value).strip()
        if key in default and key not in result:
            result.append(key)
    result.extend(key for key in default if key not in result)
    return result


def sanitize_dashboard_cards(stored: object) -> list[str]:
    """Return the known dashboard cards selected by the user."""

    if stored is None:
        return list(DASHBOARD_CARD_DEFAULTS)
    if isinstance(stored, str):
        candidates: Iterable[object] = stored.split(",") if stored else ()
    elif isinstance(stored, (list, tuple)):
        candidates = stored
    else:
        return list(DASHBOARD_CARD_DEFAULTS)
    result: list[str] = []
    for value in candidates:
        key = str(value).strip()
        if key in DASHBOARD_CARD_DEFAULTS and key not in result:
            result.append(key)
    return result
