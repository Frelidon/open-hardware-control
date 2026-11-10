#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware-independent RGB Studio gallery with suggestions and favorites."""

from __future__ import annotations

import math

from PySide6.QtCore import QPoint, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QGridLayout, QPushButton, QWidget

from rgb_effects import (
    BUILTIN_DESIGN_CATEGORIES,
    BUILTIN_DESIGNS,
    RGBEffectConfig,
    normalize_hex,
    render_effect,
)


def build_category_selector(translator, callback):
    """Build the compact four-column category row outside the root orchestrator."""
    host = QWidget()
    layout = QGridLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    buttons = {}
    categories = ("Alle", "Ruhig", "Spektrum", "Bewegung", "Energie", "Impuls", "Räumlich", "OHC Originale", "OpenRGB Originale")
    for index, category in enumerate(categories):
        button = QPushButton(translator(category))
        button.setCheckable(True)
        button.setChecked(category == "Alle")
        button.clicked.connect(lambda _checked=False, value=category: callback(value))
        buttons[category] = button
        layout.addWidget(button, index // 4, index % 4)
    host.setVisible(False)
    return host, buttons


class RGBDesignGallery(QWidget):
    """Render and select the built-in RGB designs without hardware access."""

    design_selected = Signal(int)
    design_context_requested = Signal(int, QPoint)
    favorite_toggled = Signal(int, bool)

    def __init__(self, parent: QWidget | None = None, *, translator=None):
        super().__init__(parent)
        self.tr = translator if callable(translator) else str
        self.category = "Alle"
        self.view_mode = "suggestions"
        self.favorite_indices: set[int] = set()
        self.suggestion_indices = tuple(range(max(0, len(BUILTIN_DESIGNS) - 4), len(BUILTIN_DESIGNS)))
        self.selected_index = -1
        self.active_index = -1
        self.elapsed = 0.0
        self._elapsed_bucket = -1
        self.static_color = "00aaff"
        self.design_overrides: dict[int, RGBEffectConfig] = {}
        self.card_height = 132
        self.gap = 9
        self.setMinimumWidth(360)
        self.setMouseTracking(True)
        self.setAccessibleName(self.tr("Animierte RGB-Designgalerie"))
        self.update_geometry_height()

    def visible_indices(self) -> list[int]:
        if self.view_mode == "suggestions":
            return list(self.suggestion_indices)
        if self.view_mode == "favorites":
            return sorted(self.favorite_indices)[:4]
        if self.category == "Alle":
            return list(range(len(BUILTIN_DESIGNS)))
        return [
            index
            for index, category in enumerate(BUILTIN_DESIGN_CATEGORIES)
            if category == self.category
        ]

    def column_count(self) -> int:
        return max(2, min(6, max(1, self.width()) // 190))

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

    def set_view_mode(self, mode: str) -> None:
        self.view_mode = mode if mode in {"suggestions", "favorites", "all"} else "suggestions"
        self.update_geometry_height()

    def set_favorite_indices(self, indices: set[int]) -> None:
        self.favorite_indices = {
            int(index) for index in indices if 0 <= int(index) < len(BUILTIN_DESIGNS)
        }
        self.update_geometry_height()

    def favorite_rect(self, visible_position: int) -> QRectF:
        area = self.card_rect(visible_position).adjusted(3, 3, -3, -3)
        return QRectF(area.right() - 36, area.bottom() - 38, 28, 28)

    def set_selected_index(self, index: int) -> None:
        self.selected_index = index if 0 <= index < len(BUILTIN_DESIGNS) else -1
        self.update()

    def set_active_index(self, index: int) -> None:
        self.active_index = index if 0 <= index < len(BUILTIN_DESIGNS) else -1
        self.update()

    def set_elapsed(self, elapsed: float) -> None:
        value = max(0.0, float(elapsed))
        bucket = int(value * 10.0)
        if bucket == self._elapsed_bucket:
            return
        self._elapsed_bucket = bucket
        self.elapsed = value
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
                    if event.button() == Qt.MouseButton.LeftButton and self.favorite_rect(position).contains(event.position()):
                        favorite = design_index not in self.favorite_indices
                        if favorite:
                            self.favorite_indices.add(design_index)
                        else:
                            self.favorite_indices.discard(design_index)
                        self.favorite_toggled.emit(design_index, favorite)
                        self.update_geometry_height()
                        event.accept()
                        return
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

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        base_font = QFont(painter.font())
        exposed = QRectF(event.rect())
        for position, design_index in enumerate(self.visible_indices()):
            title, config = BUILTIN_DESIGNS[design_index]
            config = self.design_overrides.get(design_index, config)
            if title == "Feste Farbe":
                config = RGBEffectConfig(
                    "static", self.static_color, self.static_color,
                    config.brightness, config.speed,
                )
            area = self.card_rect(position).adjusted(3, 3, -3, -3)
            if not area.intersects(exposed):
                continue
            selected = design_index == self.selected_index
            active = design_index == self.active_index
            border_color = QColor("#53c7ff") if selected else QColor("#36d58c") if active else QColor("#34465f")
            painter.setPen(QPen(border_color, 4 if selected else 3 if active else 1))
            background = QLinearGradient(area.topLeft(), area.bottomRight())
            background.setColorAt(0.0, QColor("#17344d") if selected else QColor("#0d1c2b"))
            background.setColorAt(1.0, QColor("#0b1724") if selected else QColor("#07111c"))
            painter.setBrush(background)
            painter.drawRoundedRect(area, 14, 14)
            if selected and active:
                painter.setPen(QPen(QColor("#36d58c"), 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(area.adjusted(5, 5, -5, -5), 10, 10)

            preview = QRectF(area.left() + 10, area.top() + 27, area.width() - 20, 60)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(3, 7, 13, 235))
            painter.drawRoundedRect(preview, 9, 9)
            colors = render_effect(config, 28, self.elapsed)
            columns = 14
            led_width = max(3.0, (preview.width() - 18) / columns - 2.0)
            for led_index, (red, green, blue) in enumerate(colors):
                row, column = divmod(led_index, columns)
                x = preview.left() + 10 + column * ((preview.width() - 18) / columns)
                y = preview.top() + 14 + row * 21
                color = QColor(red, green, blue)
                painter.setBrush(color)
                painter.setPen(QPen(color.lighter(150), 1))
                painter.drawRoundedRect(QRectF(x, y, led_width, 8), 3, 3)

            painter.setPen(QColor("#edf6ff"))
            title_font = QFont(base_font)
            title_font.setBold(True)
            title_font.setPixelSize(13)
            painter.setFont(title_font)
            text_width = max(20, int(area.width() - 66))
            title_text = QFontMetrics(title_font).elidedText(
                self.tr(title), Qt.TextElideMode.ElideRight, text_width,
            )
            painter.drawText(
                QRectF(area.left() + 12, area.bottom() - 39, text_width, 20),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                title_text,
            )
            painter.setPen(QColor("#8ca4bc"))
            meta_font = QFont(base_font)
            meta_font.setBold(False)
            meta_font.setPixelSize(11)
            painter.setFont(meta_font)
            painter.drawText(
                QRectF(area.left() + 12, area.bottom() - 19, text_width, 14),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                self.tr(BUILTIN_DESIGN_CATEGORIES[design_index]),
            )
            category_font = QFont(base_font)
            category_font.setBold(True)
            category_font.setPixelSize(10)
            painter.setFont(category_font)
            painter.setPen(QColor("#80d8ff"))
            painter.drawText(
                QRectF(area.left() + 12, area.top() + 7, text_width, 18),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                self.tr(BUILTIN_DESIGN_CATEGORIES[design_index]).upper(),
            )
            star_area = self.favorite_rect(position)
            painter.setPen(QColor("#ffd166") if design_index in self.favorite_indices else QColor("#6f8193"))
            star_font = QFont(base_font)
            star_font.setBold(True)
            star_font.setPixelSize(18)
            painter.setFont(star_font)
            painter.drawText(star_area, Qt.AlignmentFlag.AlignCenter, "★" if design_index in self.favorite_indices else "☆")
            if selected or active:
                badge = "AKTIV · AUSGEWÄHLT" if selected and active else "AUSGEWÄHLT" if selected else "AKTIV"
                badge_color = QColor("#53c7ff") if selected else QColor("#36d58c")
                badge_area = QRectF(area.right() - 116, area.top() + 8, 108, 20)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(2, 12, 21, 225))
                painter.drawRoundedRect(badge_area, 8, 8)
                badge_font = QFont(base_font)
                badge_font.setBold(True)
                badge_font.setPixelSize(10)
                painter.setFont(badge_font)
                painter.setPen(badge_color)
                painter.drawText(badge_area, Qt.AlignmentFlag.AlignCenter, badge)
