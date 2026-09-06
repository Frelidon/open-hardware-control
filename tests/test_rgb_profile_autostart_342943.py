#!/usr/bin/env python3
"""Regression test for an OpenRGB profile waiting on cold-start inventory."""

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from kraken_control import KrakenControl


class _CheckBox:
    def isChecked(self) -> bool:
        return True


class _Label:
    def __init__(self) -> None:
        self.text = ""

    def setText(self, text: str) -> None:
        self.text = text


class _Lock:
    def __init__(self) -> None:
        self.released = False

    def acquire(self) -> bool:
        return True

    def release(self) -> None:
        self.released = True


class _Timer:
    def __init__(self) -> None:
        self.delay = 0

    def start(self, delay: int) -> None:
        self.delay = delay


class _ProfileStartState:
    rgb_profile_autostart_checkbox = _CheckBox()
    rgb_session_lock = _Lock()
    rgb_profile_start_retry_timer = _Timer()
    openrgb_effect_status = _Label()
    openrgb_client = SimpleNamespace(installed=True)
    openrgb_server_reachable = True
    openrgb_devices: list[object] = []
    openrgb_expected_device_count = 6
    openrgb_write_enabled = False
    rgb_profile_autostart_pending = False
    rgb_profile_autostart_name = ""
    rgb_profile_start_retry_count = 99
    rgb_profile_inventory_stable_since = 99.0

    def __init__(self) -> None:
        self.logs: list[str] = []
        self.inventory_retries: list[tuple[int, str]] = []
        self.checkbox_state = False
        self.controls_updated = False

    def conflicting_openrgb_process_ids(self) -> tuple[int, ...]:
        return ()

    def set_openrgb_write_checkbox_state(self, checked: bool) -> None:
        self.checkbox_state = checked

    def rgb_logical_devices(self) -> list[object]:
        return []

    def log_message(self, message: str) -> None:
        self.logs.append(message)

    def schedule_rgb_inventory_retry(self, delay: int, reason: str) -> None:
        self.inventory_retries.append((delay, reason))

    def update_openrgb_control_state(self) -> None:
        self.controls_updated = True


def test_saved_rgb_profile_waits_for_incomplete_initial_inventory() -> None:
    state = _ProfileStartState()

    KrakenControl.start_rgb_profile_automatically(state, "Startprofil")

    assert state.checkbox_state
    assert state.openrgb_write_enabled
    assert state.rgb_profile_autostart_pending
    assert state.rgb_profile_autostart_name == "Startprofil"
    assert state.rgb_profile_start_retry_count == 0
    assert state.rgb_profile_inventory_stable_since == 0.0
    assert not state.rgb_session_lock.released
    assert state.rgb_profile_start_retry_timer.delay == 700
    assert state.inventory_retries == [
        (1_500, "gespeichertes RGB-Startprofil wartet auf Geräte")
    ]
    assert "vollständigen OpenRGB-Gerätebestand" in state.openrgb_effect_status.text
    assert any("bleibt vorgemerkt" in message for message in state.logs)
    assert state.controls_updated
