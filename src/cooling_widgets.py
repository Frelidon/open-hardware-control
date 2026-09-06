#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Frelidon contributors
"""Reusable, hardware-independent cooling curve presentation widgets."""

from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import QWidget

from temperature_utils import celsius_to_display, normalize_temperature_unit, temperature_symbol


class CurveEditor(QWidget):
    """Interactive, safety-aware CPU-temperature curve editor.

    Points can be dragged with the mouse or adjusted with the arrow keys. The
    editor keeps temperatures strictly increasing and duties non-decreasing.
    The final point remains fixed at 100 percent and cannot move beyond 100 °C.
    """

    pointsChanged = Signal(object)

    def __init__(self, points: list[tuple[int, int]], minimum_duty: int, channel_label: str):
        super().__init__()
        self._points = [(int(temp), int(duty)) for temp, duty in points]
        self._minimum_duty = int(minimum_duty)
        self._channel_label = channel_label
        self._temperature_min = 20
        self._temperature_max = 100
        self._accent = QColor("#00aaff")
        self._current_temperature: float | None = None
        self._temperature_unit = "c"
        self._drag_index: int | None = None
        self._selected_index = 0
        self.setMinimumSize(360, 250)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setObjectName("curveEditor")
        self.setAccessibleName(f"Grafischer Kurveneditor für {channel_label}")
        self.setToolTip(
            "Punkte mit der Maus ziehen oder mit den Pfeiltasten verschieben. "
            "Der letzte Punkt bleibt aus Sicherheitsgründen bei 100 %."
        )

    def points(self) -> list[tuple[int, int]]:
        return list(self._points)

    def set_points(self, points: list[tuple[int, int]], emit: bool = False) -> None:
        normalized = [(int(temp), int(duty)) for temp, duty in points]
        if len(normalized) < 2:
            return
        self._points = normalized
        self._selected_index = min(self._selected_index, len(self._points) - 1)
        self.update()
        if emit:
            self.pointsChanged.emit(self.points())

    def set_minimum_duty(self, minimum_duty: int) -> None:
        self._minimum_duty = max(0, min(100, int(minimum_duty)))
        self.update()

    def set_accent_color(self, color: QColor) -> None:
        if color.isValid():
            self._accent = QColor(color)
            self.update()

    def set_current_temperature(self, temperature: float | None) -> None:
        self._current_temperature = temperature
        self.update()

    def set_temperature_unit(self, unit: str) -> None:
        self._temperature_unit = normalize_temperature_unit(unit)
        self.update()

    def _temperature_text(self, value: float, decimals: int = 0) -> str:
        displayed = celsius_to_display(value, self._temperature_unit)
        return f"{displayed:.{decimals}f}{temperature_symbol(self._temperature_unit)}"

    def _plot_rect(self) -> QRectF:
        return QRectF(54.0, 18.0, max(120.0, self.width() - 78.0), max(100.0, self.height() - 70.0))

    def _to_canvas(self, temp: float, duty: float) -> QPointF:
        rect = self._plot_rect()
        span = float(self._temperature_max - self._temperature_min)
        x = rect.left() + ((temp - self._temperature_min) / span) * rect.width()
        y = rect.bottom() - (duty / 100.0) * rect.height()
        return QPointF(x, y)

    def _from_canvas(self, point: QPointF) -> tuple[int, int]:
        rect = self._plot_rect()
        span = float(self._temperature_max - self._temperature_min)
        temp = self._temperature_min + ((point.x() - rect.left()) / max(1.0, rect.width())) * span
        duty = ((rect.bottom() - point.y()) / max(1.0, rect.height())) * 100.0
        return int(round(temp)), int(round(duty))

    def _move_selected(self, delta_temp: int, delta_duty: int) -> None:
        if not self._points:
            return
        index = self._selected_index
        temp, duty = self._points[index]
        self._set_point(index, temp + delta_temp, duty + delta_duty)

    def _set_point(self, index: int, temp: int, duty: int) -> None:
        previous_temp = self._points[index - 1][0] + 1 if index > 0 else self._temperature_min
        next_temp = self._points[index + 1][0] - 1 if index < len(self._points) - 1 else self._temperature_max
        previous_duty = self._points[index - 1][1] if index > 0 else self._minimum_duty
        next_duty = self._points[index + 1][1] if index < len(self._points) - 1 else 100

        temp = max(previous_temp, min(next_temp, int(temp)))
        if index == len(self._points) - 1:
            duty = 100
        else:
            duty = max(previous_duty, min(next_duty, int(duty)))

        updated = list(self._points)
        updated[index] = (temp, duty)
        if updated == self._points:
            return
        self._points = updated
        self.update()
        self.pointsChanged.emit(self.points())

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self._plot_rect()
        palette = self.palette()
        text_color = palette.color(QPalette.ColorRole.Text)
        muted = palette.color(QPalette.ColorRole.Mid)
        grid = palette.color(QPalette.ColorRole.Midlight)
        background = palette.color(QPalette.ColorRole.Base)

        painter.setPen(QPen(grid, 1))
        painter.setBrush(background)
        painter.drawRoundedRect(rect, 9, 9)

        # Grid and axis labels.
        font = painter.font()
        font.setPointSize(max(8, font.pointSize() - 1))
        painter.setFont(font)
        for duty in range(0, 101, 20):
            p1 = self._to_canvas(self._temperature_min, duty)
            p2 = self._to_canvas(self._temperature_max, duty)
            painter.setPen(QPen(grid, 1, Qt.PenStyle.DotLine))
            painter.drawLine(p1, p2)
            painter.setPen(muted)
            painter.drawText(QRectF(2, p1.y() - 10, 46, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{duty}%")
        for temp in range(self._temperature_min, self._temperature_max + 1, 10):
            p1 = self._to_canvas(temp, 0)
            p2 = self._to_canvas(temp, 100)
            painter.setPen(QPen(grid, 1, Qt.PenStyle.DotLine))
            painter.drawLine(p1, p2)
            painter.setPen(muted)
            painter.drawText(QRectF(p1.x() - 24, rect.bottom() + 7, 48, 20), Qt.AlignmentFlag.AlignHCenter, self._temperature_text(temp))

        # Current CPU temperature marker.
        if self._current_temperature is not None:
            current = max(float(self._temperature_min), min(float(self._temperature_max), float(self._current_temperature)))
            x = self._to_canvas(current, 0).x()
            warning = QColor("#d49b21")
            painter.setPen(QPen(warning, 2, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            painter.setPen(warning)
            painter.drawText(QRectF(x - 55, rect.top() + 3, 110, 20), Qt.AlignmentFlag.AlignHCenter, f"Aktuell {self._temperature_text(self._current_temperature, 1)}")

        # Curve path.
        canvas_points = [self._to_canvas(temp, duty) for temp, duty in self._points]
        if canvas_points:
            path = QPainterPath(canvas_points[0])
            for point in canvas_points[1:]:
                path.lineTo(point)
            painter.setPen(QPen(self._accent, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        # Draggable points and labels.
        for index, ((temp, duty), point) in enumerate(zip(self._points, canvas_points)):
            selected = index == self._selected_index
            radius = 8 if selected else 6
            painter.setPen(QPen(self._accent, 2))
            painter.setBrush(palette.color(QPalette.ColorRole.Window) if selected else self._accent)
            painter.drawEllipse(point, radius, radius)
            painter.setPen(text_color)
            label_rect = QRectF(point.x() - 37, point.y() - 30, 74, 20)
            painter.drawText(label_rect.adjusted(-10, 0, 10, 0), Qt.AlignmentFlag.AlignHCenter, f"{self._temperature_text(temp)} / {duty}%")

        painter.setPen(muted)
        painter.drawText(
            QRectF(rect.left(), self.height() - 25, rect.width(), 20),
            Qt.AlignmentFlag.AlignHCenter,
            "Pfeile: ändern · Strg+Links/Rechts: Punkt wählen · Tab: weiter",
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        position = event.position()
        distances = [((position.x() - p.x()) ** 2 + (position.y() - p.y()) ** 2, i) for i, p in enumerate(
            self._to_canvas(temp, duty) for temp, duty in self._points
        )]
        distance, index = min(distances, default=(999999.0, 0))
        if distance <= 18 ** 2:
            self._selected_index = index
            self._drag_index = index
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self.update()
        else:
            self._drag_index = None

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_index is None:
            return super().mouseMoveEvent(event)
        temp, duty = self._from_canvas(event.position())
        self._set_point(self._drag_index, temp, duty)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_index = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_Left:
            self._selected_index = (self._selected_index - 1) % len(self._points)
            self.update()
        elif modifiers & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_Right:
            self._selected_index = (self._selected_index + 1) % len(self._points)
            self.update()
        elif key == Qt.Key.Key_Home:
            self._selected_index = 0
            self.update()
        elif key == Qt.Key.Key_End:
            self._selected_index = len(self._points) - 1
            self.update()
        elif key == Qt.Key.Key_Left:
            self._move_selected(-1, 0)
        elif key == Qt.Key.Key_Right:
            self._move_selected(1, 0)
        elif key == Qt.Key.Key_Up:
            self._move_selected(0, 1)
        elif key == Qt.Key.Key_Down:
            self._move_selected(0, -1)
        else:
            # Tab and Shift+Tab deliberately pass through for normal focus traversal.
            return super().keyPressEvent(event)
        event.accept()


class FanCurveMiniPreview(QWidget):
    """Compact, read-only fan-curve preview used on chassis fan cards."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.points: list[tuple[int, int]] = [(30, 30), (45, 40), (60, 55), (75, 75), (85, 100)]
        self.setMinimumHeight(74)
        self.setMaximumHeight(88)
        self.setAccessibleName("Grafische Vorschau der Lüfterkurve")

    def set_points(self, points: Iterable[tuple[int, int]]) -> None:
        clean: list[tuple[int, int]] = []
        for temp, duty in points:
            clean.append((int(temp), max(0, min(100, int(duty)))))
        if clean:
            self.points = clean
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        area = QRectF(8, 8, max(40, self.width() - 16), max(34, self.height() - 18))
        painter.setPen(QPen(QColor("#385167"), 1))
        painter.setBrush(QColor(16, 29, 40, 90))
        painter.drawRoundedRect(area, 8, 8)
        if len(self.points) < 2:
            return
        temps = [point[0] for point in self.points]
        lo, hi = min(temps), max(temps)
        span = max(1, hi - lo)
        path = QPainterPath()
        for index, (temp, duty) in enumerate(self.points):
            x = area.left() + ((temp - lo) / span) * area.width()
            y = area.bottom() - (duty / 100.0) * area.height()
            if index == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        accent = QColor("#42d8ff")
        painter.setPen(QPen(accent, 2.4))
        painter.drawPath(path)
        painter.setBrush(accent)
        for temp, duty in self.points:
            x = area.left() + ((temp - lo) / span) * area.width()
            y = area.bottom() - (duty / 100.0) * area.height()
            painter.drawEllipse(QPointF(x, y), 3.2, 3.2)
