#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compatibility facade for the versioned, per-language localization module."""

from modules.localization.v1_0 import (
    ABOUT_SUMMARY_TEXT as _ABOUT_SUMMARY_TEXT,
    GIF_SAFETY_TEXT as _GIF_SAFETY_TEXT,
    HELP_TOPICS,
    SETUP_TRANSLATIONS,
    SUPPORTED_LANGUAGE_CODES,
    UI_TRANSLATIONS,
    interactive_text_needs_translation,
    translated_control_text,
)

__all__ = [
    "HELP_TOPICS",
    "SETUP_TRANSLATIONS",
    "SUPPORTED_LANGUAGE_CODES",
    "UI_TRANSLATIONS",
    "_ABOUT_SUMMARY_TEXT",
    "_GIF_SAFETY_TEXT",
    "interactive_text_needs_translation",
    "translated_control_text",
]
