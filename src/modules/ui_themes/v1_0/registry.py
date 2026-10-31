#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Allowlisted registry for current and future OHC application themes."""

from dataclasses import replace
from typing import Callable

from PySide6.QtGui import QColor, QPalette

from .dark import build_dark_theme
from .light import build_light_theme
from .model import ThemeDefinition
from .studio import build_studio_light_theme, build_studio_dark_theme

ThemeFactory = Callable[[QColor], ThemeDefinition]
THEME_FACTORIES: dict[str, ThemeFactory] = {
    "light": build_light_theme,
    "dark": build_dark_theme,
    "studio-light": build_studio_light_theme,
    "studio-dark": build_studio_dark_theme,
}
THEME_IDS = ("system", *THEME_FACTORIES)


def resolve_theme(mode: object, system_palette: QPalette, accent: QColor) -> ThemeDefinition:
    """Resolve a saved ID; system keeps native palette roles but borrows matching semantic tokens."""

    clean = str(mode)
    if clean in THEME_FACTORIES:
        return THEME_FACTORIES[clean](accent)
    dark = system_palette.color(QPalette.ColorRole.Window).lightness() < 150
    resolved = build_dark_theme(accent) if dark else build_light_theme(accent)
    return replace(resolved, theme_id="system", title="Systemmodus", palette_colors={})
