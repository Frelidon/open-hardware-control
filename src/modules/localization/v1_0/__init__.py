"""Public localization API for module version 1.0."""

from .catalog import (
    ABOUT_SUMMARY_TEXT,
    GIF_SAFETY_TEXT,
    HELP_TOPICS,
    SETUP_TRANSLATIONS,
    SUPPORTED_LANGUAGE_CODES,
    UI_TRANSLATIONS,
)
from .policy import interactive_text_needs_translation, translated_control_text

__all__ = [
    "ABOUT_SUMMARY_TEXT",
    "GIF_SAFETY_TEXT",
    "HELP_TOPICS",
    "SETUP_TRANSLATIONS",
    "SUPPORTED_LANGUAGE_CODES",
    "UI_TRANSLATIONS",
    "interactive_text_needs_translation",
    "translated_control_text",
]
