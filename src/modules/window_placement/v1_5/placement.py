#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure selection helpers for the OHC main-window monitor preference.

The module deliberately has no Qt import.  Production passes QScreen objects,
while regression tests use tiny screen doubles with the same read-only API.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


PRIMARY_SCREEN_PREFERENCE = "primary"
_NAMED_SCREEN_PREFIX = "screen:"
DEFAULT_WINDOWED_SIZE_PERCENT = 82
WINDOW_START_LAST = "last"
WINDOW_START_MAXIMIZED = "maximized"
WINDOW_START_WINDOWED = "windowed"
WINDOW_START_MODES = (WINDOW_START_LAST, WINDOW_START_MAXIMIZED, WINDOW_START_WINDOWED)


def normalize_window_start_mode(value: object) -> str:
    """Return a stable window-start policy, defaulting to the last real state."""
    candidate = str(value or "").strip().casefold()
    return candidate if candidate in WINDOW_START_MODES else WINDOW_START_LAST


def resolve_start_maximized(mode: object, last_maximized: object) -> bool:
    """Resolve the visible start state without conflating it with geometry."""
    normalized = normalize_window_start_mode(mode)
    if normalized == WINDOW_START_MAXIMIZED:
        return True
    if normalized == WINDOW_START_WINDOWED:
        return False
    return bool(last_maximized)


@dataclass(frozen=True)
class WindowRect:
    """Qt-independent window/screen rectangle in logical desktop pixels."""

    x: int
    y: int
    width: int
    height: int


def normalize_windowed_size_percent(value: object) -> int:
    """Keep the user-facing floating-window size preference useful and safe."""
    try:
        percent = int(value)
    except (TypeError, ValueError):
        percent = DEFAULT_WINDOWED_SIZE_PERCENT
    return max(60, min(95, percent))


def encode_window_rect(rect: WindowRect) -> str:
    """Return a small, portable QSettings representation."""
    return f"{rect.x},{rect.y},{rect.width},{rect.height}"


def decode_window_rect(value: object) -> WindowRect | None:
    """Decode a bounded saved normal geometry without trusting settings data."""
    parts = str(value or "").split(",")
    if len(parts) != 4:
        return None
    try:
        x, y, width, height = (int(part.strip()) for part in parts)
    except ValueError:
        return None
    if not (-1_000_000 <= x <= 1_000_000 and -1_000_000 <= y <= 1_000_000):
        return None
    if not (320 <= width <= 32_768 and 240 <= height <= 32_768):
        return None
    return WindowRect(x, y, width, height)


def preferred_window_rect(
    available: WindowRect,
    percent: object = DEFAULT_WINDOWED_SIZE_PERCENT,
    *,
    minimum_width: int = 920,
    minimum_height: int = 620,
) -> WindowRect:
    """Return a centered, comfortably sized floating window for one screen."""
    size_percent = normalize_windowed_size_percent(percent)
    usable_width = max(1, available.width - 24)
    usable_height = max(1, available.height - 24)
    width = min(1600, round(usable_width * size_percent / 100))
    height = min(1000, round(usable_height * size_percent / 100))
    width = min(usable_width, max(minimum_width, width))
    height = min(usable_height, max(minimum_height, height))
    return WindowRect(
        available.x + max(0, (available.width - width) // 2),
        available.y + max(0, (available.height - height) // 2),
        width,
        height,
    )


def resembles_maximized_rect(rect: WindowRect, available: WindowRect) -> bool:
    """Detect compositor work-area dimensions accidentally reused as normal size."""
    return (
        rect.width >= available.width - 24
        and rect.height >= available.height - 80
    )


def safe_window_rect(
    candidate: WindowRect | None,
    available: WindowRect,
    percent: object = DEFAULT_WINDOWED_SIZE_PERCENT,
    *,
    minimum_width: int = 920,
    minimum_height: int = 620,
) -> WindowRect:
    """Fit a normal window wholly on-screen or replace maximized/corrupt geometry."""
    if candidate is None or resembles_maximized_rect(candidate, available):
        return preferred_window_rect(
            available,
            percent,
            minimum_width=minimum_width,
            minimum_height=minimum_height,
        )
    width = min(available.width, max(minimum_width, candidate.width))
    height = min(available.height, max(minimum_height, candidate.height))
    max_x = available.x + max(0, available.width - width)
    max_y = available.y + max(0, available.height - height)
    return WindowRect(
        max(available.x, min(candidate.x, max_x)),
        max(available.y, min(candidate.y, max_y)),
        width,
        height,
    )


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
