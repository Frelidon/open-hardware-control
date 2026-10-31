#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dependency-free Qt chart for interactive dated multi-sensor temperatures."""

from __future__ import annotations

from datetime import datetime
import hashlib

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from .model import HistorySample, TemperatureHistoryBuffer


BASE_COLORS = {
    "cpu": QColor("#36c5ff"),
    "gpu": QColor("#d06cff"),
    "liquid": QColor("#52d6a8"),
}
PALETTE = ("#ffb454", "#ff6b8a", "#75e39b", "#6fa8ff", "#e5d46b", "#b98cff", "#60d5cf", "#f58f5e")


class TemperatureHistoryChart(QWidget):
    def __init__(self, history: TemperatureHistoryBuffer, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.history = history
        self.visible_series = {"cpu", "gpu", "liquid"}
        self.series_labels = {"cpu": "CPU", "gpu": "GPU", "liquid": "Kühlmittel"}
        self.series_groups = {"cpu": "cpu", "gpu": "gpu", "liquid": "cooling"}
        self.window_seconds: int | None = 900
        self.unit = "c"
        self.empty_text = "Noch keine Temperaturwerte in dieser Sitzung"
        self.hover_x: float | None = None
        self.setMinimumHeight(245)
        self.setMouseTracking(True)
        self.setAccessibleName("Interaktiver Temperaturverlauf")

    def set_visible_series(self, keys: set[str]) -> None:
        self.visible_series = set(keys)
        self.update()

    def set_window_seconds(self, seconds: int | None) -> None:
        self.window_seconds = seconds
        self.update()

    def set_temperature_unit(self, unit: str) -> None:
        self.unit = "f" if str(unit).casefold() == "f" else "c"
        self.update()

    def set_series_labels(self, labels: dict[str, str]) -> None:
        self.series_labels.update({str(key): str(value) for key, value in labels.items()})
        self.update()

    def set_series_metadata(self, metadata: dict[str, tuple[str, str]]) -> None:
        for key, (label, group) in metadata.items():
            self.series_labels[str(key)] = str(label)
            self.series_groups[str(key)] = str(group)
        self.update()

    def set_empty_text(self, text: str) -> None:
        self.empty_text = str(text)
        self.update()

    def _display_value(self, celsius: float) -> float:
        return celsius * 9.0 / 5.0 + 32.0 if self.unit == "f" else celsius

    @staticmethod
    def _plot_rect(widget_rect: QRectF) -> QRectF:
        return widget_rect.adjusted(52.0, 18.0, -18.0, -52.0)

    @staticmethod
    def timestamp_label(timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M:%S")

    def _window_samples(self) -> tuple[HistorySample, ...]:
        return self.history.window(self.window_seconds)

    @staticmethod
    def _fallback_color(key: str) -> QColor:
        digest = hashlib.sha256(key.encode("utf-8", errors="replace")).digest()[0]
        return QColor(PALETTE[digest % len(PALETTE)])

    def series_color(self, key: str) -> QColor:
        return BASE_COLORS.get(key, self._fallback_color(key))

    def _ordered_keys(self) -> list[str]:
        primary = [key for key in ("cpu", "gpu", "liquid") if key in self.visible_series]
        return primary + sorted(self.visible_series - set(primary), key=lambda key: self.series_labels.get(key, key).casefold())

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        bounds = QRectF(self.rect())
        painter.fillRect(bounds, QColor(8, 14, 24, 150))
        plot = self._plot_rect(bounds)
        samples = self._window_samples()
        values = [self._display_value(sample.values[key]) for sample in samples for key in self.visible_series if key in sample.values]
        if not values or plot.width() <= 1 or plot.height() <= 1:
            painter.setPen(QColor("#9ba8b8"))
            painter.drawText(plot, Qt.AlignmentFlag.AlignCenter, self.empty_text)
            return
        low, high = min(values), max(values)
        padding = max(2.0, (high - low) * 0.15)
        low -= padding
        high = max(high + padding, low + 10.0)
        first = samples[0].timestamp
        last = max(samples[-1].timestamp, first + 1.0)
        grid_pen = QPen(QColor(105, 126, 150, 65), 1)
        painter.setPen(grid_pen)
        for index in range(5):
            y = plot.top() + plot.height() * index / 4.0
            painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
            value = high - (high - low) * index / 4.0
            painter.setPen(QColor("#91a2b6"))
            painter.drawText(QRectF(2, y - 9, 46, 18), Qt.AlignmentFlag.AlignRight, f"{value:.0f}°")
            painter.setPen(grid_pen)
        for key in self._ordered_keys():
            path = QPainterPath()
            started = False
            for sample in samples:
                if key not in sample.values:
                    continue
                x = plot.left() + (sample.timestamp - first) / (last - first) * plot.width()
                value = self._display_value(sample.values[key])
                y = plot.bottom() - (value - low) / (high - low) * plot.height()
                path.lineTo(x, y) if started else path.moveTo(x, y)
                started = True
            if started:
                painter.setPen(QPen(self.series_color(key), 2.2))
                painter.drawPath(path)
        painter.setPen(QColor("#91a2b6"))
        painter.drawText(QRectF(plot.left(), plot.bottom() + 7, 170, 36), Qt.AlignmentFlag.AlignLeft, self.timestamp_label(first))
        painter.drawText(QRectF(plot.right() - 170, plot.bottom() + 7, 170, 36), Qt.AlignmentFlag.AlignRight, self.timestamp_label(last))
        self._paint_hover(painter, plot, samples, first, last)

    def _paint_hover(self, painter: QPainter, plot: QRectF, samples: tuple[HistorySample, ...], first: float, last: float) -> None:
        if self.hover_x is None or not plot.contains(QPointF(self.hover_x, plot.center().y())):
            return
        ratio = (self.hover_x - plot.left()) / plot.width()
        target = first + ratio * (last - first)
        sample = min(samples, key=lambda item: abs(item.timestamp - target))
        x = plot.left() + (sample.timestamp - first) / (last - first) * plot.width()
        painter.setPen(QPen(QColor("#dcecff"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom()))
        symbol = "°F" if self.unit == "f" else "°C"
        values = [
            f"{self.series_labels.get(key, key)} {self._display_value(sample.values[key]):.1f} {symbol}"
            for key in self._ordered_keys() if key in sample.values
        ]
        lines = [self.timestamp_label(sample.timestamp)]
        lines.extend("  ·  ".join(values[index:index + 3]) for index in range(0, len(values), 3))
        width = min(plot.width(), max(260.0, max((len(line) for line in lines), default=20) * 7.0))
        height = 12.0 + 19.0 * len(lines)
        left = min(max(plot.left(), x - width / 2.0), plot.right() - width)
        bubble = QRectF(left, plot.top() + 8, width, height)
        painter.setPen(QPen(QColor("#5dbdf5"), 1))
        painter.setBrush(QColor(9, 18, 31, 235))
        painter.drawRoundedRect(bubble, 8, 8)
        painter.setPen(QColor("#eff8ff"))
        for index, line in enumerate(lines):
            painter.drawText(QRectF(bubble.left() + 8, bubble.top() + 4 + index * 19, bubble.width() - 16, 18), Qt.AlignmentFlag.AlignLeft, line)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt API
        self.hover_x = event.position().x()
        self.update()

    def leaveEvent(self, _event) -> None:  # noqa: N802 - Qt API
        self.hover_x = None
        self.update()
