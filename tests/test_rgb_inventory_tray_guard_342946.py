#!/usr/bin/env python3
"""Regression test: no minutely OpenRGB CLI start while OHC sits in the tray."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kraken_control import KrakenControl


class _InventoryState:
    rgb_reset_in_progress = False
    rgb_reinitialize_refreshing = False
    rgb_manual_write_active = False
    openrgb_status_busy = False
    openrgb_engine_starting = False
    openrgb_write_enable_pending = False
    rgb_profile_autostart_pending = False
    openrgb_inventory_retry_reason = ""

    def __init__(self, *, visible: bool) -> None:
        self.visible = visible
        self.refreshes: list[bool] = []
        self.logs: list[str] = []
        self.inventory_retries: list[tuple[int, str]] = []

    def isVisible(self) -> bool:
        return self.visible

    def refresh_rgb_studio(self, *, background: bool = False) -> None:
        self.refreshes.append(background)

    def log_message(self, message: str) -> None:
        self.logs.append(message)

    def schedule_rgb_inventory_retry(self, delay: int, reason: str) -> None:
        self.inventory_retries.append((delay, reason))


def test_hidden_window_skips_background_inventory_scan() -> None:
    state = _InventoryState(visible=False)

    KrakenControl.background_scan_rgb_inventory(state)

    assert state.refreshes == []
    assert state.logs == []


def test_visible_window_runs_background_inventory_scan() -> None:
    state = _InventoryState(visible=True)

    KrakenControl.background_scan_rgb_inventory(state)

    assert state.refreshes == [True]


def test_hidden_window_still_serves_pending_startup_profile() -> None:
    state = _InventoryState(visible=False)
    state.rgb_profile_autostart_pending = True

    KrakenControl.background_scan_rgb_inventory(state)

    assert state.refreshes == [True]


def test_hidden_window_still_serves_scheduled_retry() -> None:
    state = _InventoryState(visible=False)
    state.openrgb_inventory_retry_reason = "Test-Wiederholung"

    KrakenControl.background_scan_rgb_inventory(state)

    assert state.refreshes == [True]
    assert state.openrgb_inventory_retry_reason == ""
    assert any("Test-Wiederholung" in message for message in state.logs)
