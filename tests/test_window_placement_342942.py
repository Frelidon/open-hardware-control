#!/usr/bin/env python3
"""Regression guards for primary and fixed monitor selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.window_placement.v1_0 import (  # noqa: E402
    PRIMARY_SCREEN_PREFERENCE,
    normalize_screen_preference,
    preference_for_screen,
    screen_option_label,
    select_preferred_screen,
)


@dataclass(frozen=True)
class Geometry:
    width_value: int
    height_value: int

    def width(self) -> int:
        return self.width_value

    def height(self) -> int:
        return self.height_value


@dataclass(frozen=True)
class Screen:
    connector: str
    width: int
    height: int

    def name(self) -> str:
        return self.connector

    def geometry(self) -> Geometry:
        return Geometry(self.width, self.height)


primary = Screen("DP-1", 3440, 1440)
secondary = Screen("HDMI-A-1", 1920, 1080)
screens = [secondary, primary]

assert normalize_screen_preference(None) == PRIMARY_SCREEN_PREFERENCE
assert normalize_screen_preference("invalid") == PRIMARY_SCREEN_PREFERENCE
assert normalize_screen_preference("screen:\nunsafe") == PRIMARY_SCREEN_PREFERENCE
assert normalize_screen_preference("screen:HDMI-A-1") == "screen:HDMI-A-1"
assert preference_for_screen(secondary) == "screen:HDMI-A-1"

selected, matched = select_preferred_screen(screens, primary, "primary")
assert selected is primary and matched

selected, matched = select_preferred_screen(screens, primary, "screen:HDMI-A-1")
assert selected is secondary and matched

selected, matched = select_preferred_screen(screens, primary, "screen:disconnected")
assert selected is primary and not matched

selected, matched = select_preferred_screen([], None, "screen:DP-1")
assert selected is None and not matched

assert screen_option_label(primary, 1) == "Monitor 2 · DP-1 · 3440×1440"

print("3.4.29.47 monitor placement regression guards passed.")
