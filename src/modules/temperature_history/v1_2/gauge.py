#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared compact temperature scale for overview, cooling and recording."""

from __future__ import annotations

import math

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


COLORS = {"cpu": "#36c5ff", "gpu": "#d06cff", "liquid": "#52d6a8"}


class TemperatureGauge(QWidget):
    """Twelve compact segments; 0–100 °C is a display scale, not a safety limit."""

    def __init__(self, source: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.source = source
        self.value_c: float | None = None
        self.setFixedHeight(13)
        self.setMinimumWidth(84)
        self.setMaximumWidth(196)
        self.setAccessibleName(source)

    def set_value(self, value_c: float | None) -> None:
        try:
            value = float(value_c) if value_c is not None else None
        except (TypeError, ValueError):
            value = None
        self.value_c = value if value is not None and math.isfinite(value) else None
        self.setAccessibleDescription("—" if self.value_c is None else f"{self.value_c:.1f} °C")
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        count = 12
        gap = 3.0
        width = max(2.0, (self.width() - gap * (count - 1)) / count)
        active = 0 if self.value_c is None else min(count, max(0, math.ceil(self.value_c / 100.0 * count)))
        color = QColor(COLORS.get(self.source, "#75e39b"))
        for index in range(count):
            tone = QColor(color) if index < active else QColor("#6f8095")
            tone.setAlpha(235 if index < active else 65)
            painter.setBrush(tone)
            painter.drawRoundedRect(QRectF(index * (width + gap), 2, width, 9), 3, 3)
