#!/usr/bin/env python3
"""Regression guards for primary and fixed monitor selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.window_placement.v1_5 import (  # noqa: E402
    DEFAULT_WINDOWED_SIZE_PERCENT,
    PRIMARY_SCREEN_PREFERENCE,
    WindowRect,
    apply_initial_window_presentation,
    confirm_window_screen_after_mapping,
    finish_initial_window_mapping,
    decode_window_rect,
    encode_window_rect,
    normalize_screen_preference,
    normalize_window_start_mode,
    normalize_windowed_size_percent,
    preferred_window_rect,
    preference_for_screen,
    resembles_maximized_rect,
    safe_window_rect,
    screen_option_label,
    select_preferred_screen,
    resolve_start_maximized,
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

ultrawide_work_area = WindowRect(1920, 0, 3440, 1394)
corrupt_restored_maximum = WindowRect(1920, 0, 3440, 1394)
assert resembles_maximized_rect(corrupt_restored_maximum, ultrawide_work_area)
recovered = safe_window_rect(corrupt_restored_maximum, ultrawide_work_area)
assert recovered == preferred_window_rect(ultrawide_work_area, DEFAULT_WINDOWED_SIZE_PERCENT)
assert recovered.width == 1600 and recovered.height == 1000
assert recovered.x >= ultrawide_work_area.x
assert recovered.x + recovered.width <= ultrawide_work_area.x + ultrawide_work_area.width
assert recovered.y + recovered.height <= ultrawide_work_area.y + ultrawide_work_area.height

partly_offscreen = WindowRect(5000, -200, 1280, 880)
clamped = safe_window_rect(partly_offscreen, ultrawide_work_area)
assert clamped == WindowRect(4080, 0, 1280, 880)
assert normalize_windowed_size_percent("bad") == DEFAULT_WINDOWED_SIZE_PERCENT
assert normalize_windowed_size_percent(10) == 60
assert normalize_windowed_size_percent(120) == 95
assert decode_window_rect(encode_window_rect(clamped)) == clamped
assert decode_window_rect("1920,0,999999,880") is None
assert normalize_window_start_mode(None) == "last"
assert normalize_window_start_mode("maximized") == "maximized"
assert normalize_window_start_mode("windowed") == "windowed"
assert resolve_start_maximized("last", True)
assert not resolve_start_maximized("last", False)
assert resolve_start_maximized("maximized", False)
assert not resolve_start_maximized("windowed", True)

orchestrator = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
position_body = orchestrator.split("def position_window_on_preferred_screen", 1)[1].split(
    "def refresh_display_info", 1,
)[0]
assert "self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMaximized)" in position_body
assert "self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)" in position_body
assert position_body.index("self.setGeometry") < position_body.index(
    "self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)"
)
assert "if was_visible:\n                self.hide()" in position_body
startup_body = orchestrator.split("def apply_initial_window_state", 1)[1].split(
    "# ---------- app settings ----------", 1,
)[0]
assert "apply_initial_window_presentation" in startup_body
assert "self.show()" not in startup_body
confirmation_code = (ROOT / "src/modules/window_placement/v1_5/confirmation.py").read_text(encoding="utf-8")
presentation_body = confirmation_code.split("def apply_initial_window_presentation", 1)[1].split(
    "def activate_window_from_tray", 1,
)[0]
assert "resolve_start_maximized" in presentation_body
assert "WA_DontShowOnScreen, True" in presentation_body
assert presentation_body.index("position_window_on_preferred_screen") < presentation_body.index("finish_initial_window_mapping")
assert "confirm_window_screen_after_mapping" in presentation_body
assert callable(apply_initial_window_presentation)
assert callable(confirm_window_screen_after_mapping)
assert callable(finish_initial_window_mapping)
assert "QTimer.singleShot(0, self.apply_initial_window_state)" not in orchestrator

print("3.4.29.80 monitor placement and state restore regression guards passed.")
