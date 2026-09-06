#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Frelidon contributors
"""Stable application identity and shared backend command constants."""

from __future__ import annotations

import shutil
from pathlib import Path

from nzxt_backend import SupportLevel


APP_NAME = "Open Hardware Control"
DISPLAY_NAME = "Open Hardware Control by Frelidon"
APP_VERSION = "3.4.29.48"
BUILD_CHANNEL = "STABLE"
APP_DISPLAY_VERSION = f"{APP_VERSION} {BUILD_CHANNEL}"
ORG_NAME = "FloriLinuxTools"
LEGACY_SETTINGS_APP_NAME = "Kraken Control"
LIQUIDCTL = shutil.which("liquidctl") or "liquidctl"
KRAKEN_MATCH = "NZXT Kraken 2023"
KRAKEN_PRODUCT_ID = "300e"
KRAKEN_DISPLAY_NAME = "NZXT Kraken 2023"
KRAKEN_LCD_RESOLUTION = "240 × 240"
KRAKEN_SUPPORT_LEVEL = SupportLevel.SUPPORTED
RGB_MATCH = "NZXT 2023 RGB Controller"
DEFAULT_LCD_INTERVAL = 7
LOW_PUMP_WARNING = 30
LOW_FAN_WARNING = 20
SAFE_PROFILE_PUMP = 65
SAFE_PROFILE_FAN = 65
DEPENDENCY_PACKAGES = ("liquidctl", "python3-pyside6", "python3-pillow", "qt6-qtsvg")
PROFILE_SCHEMA_VERSION = 1
DEFAULT_UI_SCALE = 90
DEFAULT_BACKGROUND_THEME = "Sternenfeld"
LCD_FAILURE_LIMIT = 3
GIF_STREAM_START_WAIT_SECONDS = 15.0
GIF_STREAM_WATCHDOG_SECONDS = 12.0
GIF_HELPER_NAME = "kraken_cam_streamer.py"
AUTOSTART_LCD_DELAY_MS = 5000
SUPPORTED_UI_LANGUAGES = {"de": "Deutsch", "en": "English", "es": "Español", "fr": "Français"}


def helper_script_path(app_file: Path, name: str) -> Path:
    """Installed layout keeps helper scripts flat; the source tree has them in ../packaging/."""
    flat = app_file.with_name(name)
    return flat if flat.is_file() else app_file.resolve().parent.parent / "packaging" / name
