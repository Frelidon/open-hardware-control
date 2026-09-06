#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware-independent Qt gallery for built-in RGB Studio designs."""

from __future__ import annotations

import math

from PySide6.QtCore import QPoint, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from rgb_effects import (
    BUILTIN_DESIGN_CATEGORIES,
    BUILTIN_DESIGNS,
    RGBEffectConfig,
    normalize_hex,
    render_effect,
)


class RGBDesignGallery(QWidget):
    """Render and select the built-in RGB designs without hardware access."""

    design_selected = Signal(int)
    design_context_requested = Signal(int, QPoint)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.category = "Alle"
        self.selected_index = -1
        self.active_index = -1
        self.elapsed = 0.0
        self.static_color = "00aaff"
        self.design_overrides: dict[int, RGBEffectConfig] = {}
        self.card_height = 126
        self.gap = 10
        self.setMinimumWidth(560)
        self.setMouseTracking(True)
        self.setAccessibleName("Animierte RGB-Designgalerie")
        self.update_geometry_height()

    def visible_indices(self) -> list[int]:
        if self.category == "Alle":
            return list(range(len(BUILTIN_DESIGNS)))
        return [
            index
            for index, category in enumerate(BUILTIN_DESIGN_CATEGORIES)
            if category == self.category
        ]

    def column_count(self) -> int:
        return max(2, min(4, max(1, self.width()) // 225))

    def update_geometry_height(self) -> None:
        count = len(self.visible_indices())
        columns = self.column_count()
        rows = max(1, math.ceil(count / columns))
        self.setMinimumHeight(rows * self.card_height + max(0, rows - 1) * self.gap)
        self.updateGeometry()
        self.update()

    def set_category(self, category: str) -> None:
        self.category = category if category in {"Alle", *BUILTIN_DESIGN_CATEGORIES} else "Alle"
        self.update_geometry_height()

    def set_selected_index(self, index: int) -> None:
        self.selected_index = index if 0 <= index < len(BUILTIN_DESIGNS) else -1
        self.update()

    def set_active_index(self, index: int) -> None:
        self.active_index = index if 0 <= index < len(BUILTIN_DESIGNS) else -1
        self.update()

    def set_elapsed(self, elapsed: float) -> None:
        self.elapsed = max(0.0, float(elapsed))
        self.update()

    def set_static_color(self, color: str) -> None:
        try:
            self.static_color = normalize_hex(color)
        except (TypeError, ValueError):
            self.static_color = "00aaff"
        self.update()

    def set_design_overrides(self, overrides: dict[int, RGBEffectConfig]) -> None:
        self.design_overrides = dict(overrides)
        self.update()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API
        super().resizeEvent(event)
        self.update_geometry_height()

    def card_rect(self, visible_position: int) -> QRectF:
        columns = self.column_count()
        width = (self.width() - self.gap * (columns - 1)) / columns
        row, column = divmod(visible_position, columns)
        return QRectF(
            column * (width + self.gap),
            row * (self.card_height + self.gap),
            width,
            self.card_height,
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt API
        if event.button() in {Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton}:
            for position, design_index in enumerate(self.visible_indices()):
                if self.card_rect(position).contains(event.position()):
                    self.set_selected_index(design_index)
                    if event.button() == Qt.MouseButton.LeftButton:
                        self.design_selected.emit(design_index)
                    else:
                        self.design_context_requested.emit(
                            design_index, event.globalPosition().toPoint()
                        )
                    event.accept()
                    return
        super().mousePressEvent(event)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        for position, design_index in enumerate(self.visible_indices()):
            title, config = BUILTIN_DESIGNS[design_index]
            config = self.design_overrides.get(design_index, config)
            if title == "Feste Farbe":
                config = RGBEffectConfig(
                    "static", self.static_color, self.static_color,
                    config.brightness, config.speed,
                )
            area = self.card_rect(position).adjusted(3, 3, -3, -3)
            selected = design_index == self.selected_index
            active = design_index == self.active_index
            border_color = QColor("#53c7ff") if selected else QColor("#36d58c") if active else QColor("#34465f")
            painter.setPen(QPen(border_color, 4 if selected else 3 if active else 1))
            painter.setBrush(QColor("#12263a") if selected else QColor("#09131f"))
            painter.drawRoundedRect(area, 14, 14)
            if selected and active:
                painter.setPen(QPen(QColor("#36d58c"), 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(area.adjusted(5, 5, -5, -5), 10, 10)

            preview = QRectF(area.left() + 12, area.top() + 12, area.width() - 24, 72)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(3, 7, 13, 235))
            painter.drawRoundedRect(preview, 9, 9)
            colors = render_effect(config, 28, self.elapsed)
            columns = 14
            led_width = max(3.0, (preview.width() - 18) / columns - 2.0)
            for led_index, (red, green, blue) in enumerate(colors):
                row, column = divmod(led_index, columns)
                x = preview.left() + 10 + column * ((preview.width() - 18) / columns)
                y = preview.top() + 20 + row * 24
                color = QColor(red, green, blue)
                painter.setBrush(color)
                painter.setPen(QPen(color.lighter(150), 1))
                painter.drawRoundedRect(QRectF(x, y, led_width, 10), 3, 3)

            painter.setPen(QColor("#edf6ff"))
            title_font = painter.font()
            title_font.setBold(True)
            title_font.setPointSize(max(9, title_font.pointSize()))
            painter.setFont(title_font)
            painter.drawText(
                QRectF(area.left() + 12, area.bottom() - 36, area.width() - 24, 22),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                title,
            )
            painter.setPen(QColor("#8ca4bc"))
            meta_font = painter.font()
            meta_font.setBold(False)
            meta_font.setPointSize(max(7, meta_font.pointSize() - 2))
            painter.setFont(meta_font)
            painter.drawText(
                QRectF(area.left() + 12, area.bottom() - 18, area.width() - 24, 15),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                BUILTIN_DESIGN_CATEGORIES[design_index],
            )
            if selected or active:
                badge = "AKTIV · AUSGEWÄHLT" if selected and active else "AUSGEWÄHLT" if selected else "AKTIV"
                badge_color = QColor("#53c7ff") if selected else QColor("#36d58c")
                badge_area = QRectF(area.right() - 116, area.top() + 8, 108, 20)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(2, 12, 21, 225))
                painter.drawRoundedRect(badge_area, 8, 8)
                badge_font = painter.font()
                badge_font.setBold(True)
                badge_font.setPointSize(max(7, badge_font.pointSize() - 2))
                painter.setFont(badge_font)
                painter.setPen(badge_color)
                painter.drawText(badge_area, Qt.AlignmentFlag.AlignCenter, badge)
