#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Stable data contract for an OHC application theme."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from PySide6.QtGui import QPalette


@dataclass(frozen=True)
class ThemeDefinition:
    """Palette roles and semantic QSS tokens supplied by one visual theme."""

    theme_id: str
    title: str
    dark: bool
    palette_colors: Mapping[QPalette.ColorRole, str]
    styles: Mapping[str, str]
    animated_background_allowed: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "palette_colors", MappingProxyType(dict(self.palette_colors)))
        object.__setattr__(self, "styles", MappingProxyType(dict(self.styles)))
