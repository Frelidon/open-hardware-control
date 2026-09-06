#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure selection helpers for the OHC main-window monitor preference.

The module deliberately has no Qt import.  Production passes QScreen objects,
while regression tests use tiny screen doubles with the same read-only API.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


PRIMARY_SCREEN_PREFERENCE = "primary"
_NAMED_SCREEN_PREFIX = "screen:"


def _screen_name(screen: Any) -> str:
    try:
        return str(screen.name()).strip()
    except (AttributeError, RuntimeError, TypeError):
        return ""


def normalize_screen_preference(value: object) -> str:
    """Return a bounded preference or the safe primary-screen default."""
    raw_preference = str(value or "")
    if any(char in raw_preference for char in "\r\n\0"):
        return PRIMARY_SCREEN_PREFERENCE
    preference = raw_preference.strip()
    if preference == PRIMARY_SCREEN_PREFERENCE:
        return preference
    if preference.startswith(_NAMED_SCREEN_PREFIX):
        name = preference[len(_NAMED_SCREEN_PREFIX):].strip()
        if name and len(name) <= 160 and not any(char in name for char in "\r\n\0"):
            return f"{_NAMED_SCREEN_PREFIX}{name}"
    return PRIMARY_SCREEN_PREFERENCE


def preference_for_screen(screen: Any) -> str:
    """Persist a connector/name identifier instead of an unstable list index."""
    name = _screen_name(screen)
    return f"{_NAMED_SCREEN_PREFIX}{name}" if name else PRIMARY_SCREEN_PREFERENCE


def select_preferred_screen(
    screens: Iterable[Any],
    primary_screen: Any | None,
    preference: object,
) -> tuple[Any | None, bool]:
    """Select the requested screen and report whether a fixed choice matched."""
    available = list(screens)
    normalized = normalize_screen_preference(preference)
    fallback = primary_screen if primary_screen is not None else (available[0] if available else None)
    if normalized == PRIMARY_SCREEN_PREFERENCE:
        return fallback, True

    requested_name = normalized[len(_NAMED_SCREEN_PREFIX):]
    for screen in available:
        if _screen_name(screen) == requested_name:
            return screen, True
    return fallback, False


def screen_option_label(screen: Any, index: int) -> str:
    """Build a readable list label without storing the translated label."""
    name = _screen_name(screen) or "Unbenannt"
    try:
        geometry = screen.geometry()
        size = f"{int(geometry.width())}×{int(geometry.height())}"
    except (AttributeError, RuntimeError, TypeError, ValueError):
        size = "Größe unbekannt"
    return f"Monitor {max(0, int(index)) + 1} · {name} · {size}"
