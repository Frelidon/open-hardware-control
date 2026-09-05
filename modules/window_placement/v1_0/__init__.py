"""Public interface for monitor-aware main-window placement."""

from .placement import (
    PRIMARY_SCREEN_PREFERENCE,
    normalize_screen_preference,
    preference_for_screen,
    screen_option_label,
    select_preferred_screen,
)

__all__ = [
    "PRIMARY_SCREEN_PREFERENCE",
    "normalize_screen_preference",
    "preference_for_screen",
    "screen_option_label",
    "select_preferred_screen",
]
