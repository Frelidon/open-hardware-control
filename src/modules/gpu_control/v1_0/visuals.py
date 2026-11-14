# SPDX-License-Identifier: GPL-3.0-or-later
"""Lightweight animated GPU fan/curve preview; never touches hardware."""

from __future__ import annotations

import math
from typing import Callable

from PySide6.QtCore import QPointF, QRect, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import QCheckBox, QSizePolicy, QStyle, QStyleOptionButton, QStylePainter, QWidget


class WrappedCheckBox(QCheckBox):
    """Keep one accessible, clickable checkbox while wrapping its caption."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def heightForWidth(self, width):  # noqa: N802
        option = QStyleOptionButton()
        self.initStyleOption(option)
        indicator = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, option, self)
        available = max(30, width - indicator.width() - 12)
        text = self.fontMetrics().boundingRect(QRect(0, 0, available, 10_000),
                                              Qt.TextFlag.TextWordWrap, self.text())
        return max(indicator.height(), text.height()) + 6

    def sizeHint(self):  # noqa: N802
        width = min(360, super().sizeHint().width())
        return QSize(width, self.heightForWidth(width))

    def minimumSizeHint(self):  # noqa: N802
        return QSize(120, super().sizeHint().height())

    def hitButton(self, position):  # noqa: N802
        return self.rect().contains(position)

    def paintEvent(self, _event):  # noqa: N802
        option = QStyleOptionButton()
        self.initStyleOption(option)
        painter = QStylePainter(self)
        caption = option.text
        option.text = ""
        painter.drawControl(QStyle.ControlElement.CE_CheckBox, option)
        contents = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxContents, option, self)
        painter.drawItemText(contents, Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,
                             option.palette, self.isEnabled(), caption, QPalette.ColorRole.ButtonText)


class GpuFanCurvePreview(QWidget):
    def __init__(self, points: Callable[[], tuple[tuple[int, int], ...]],
                 speed: Callable[[], int], parent=None, *,
                 set_point: Callable[[int, int, int], None] | None = None,
                 editable: Callable[[], bool] | None = None,
                 temperature: Callable[[], float | None] | None = None,
                 rpm: Callable[[], float | None] | None = None,
                 locked_text: Callable[[], str] | None = None,
                 translator: Callable[[str], str] | None = None):
        super().__init__(parent)
        self._points = points
        self._speed = speed
        self._set_point = set_point
        self._editable = editable or (lambda: False)
        self._temperature = temperature or (lambda: None)
        self._rpm = rpm or (lambda: None)
        self._locked_text = locked_text or (lambda: "")
        self._tr = translator or (lambda text: text)
        self._drag_index: int | None = None
        self._phase = 0.0
        self.setMinimumSize(220, 240)
        self.setMouseTracking(True)
        self.setAccessibleName("Interaktive GPU-Lüfterkurve")
        self.refresh_language()
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self._animate)

    def refresh_language(self):
        self.setToolTip(self._tr("Kurvenpunkt ziehen oder die Werte darunter ändern."))
        self.update()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self.timer.start()

    def hideEvent(self, event):  # noqa: N802
        self.timer.stop()
        super().hideEvent(event)

    def _animate(self) -> None:
        self._phase = (self._phase + max(0.012, self._speed() / 2500.0)) % (math.pi * 2)
        self.update()

    def _graph_rect(self, bounds: QRectF | None = None) -> QRectF:
        area = bounds or QRectF(self.rect()).adjusted(8, 8, -8, -8)
        return QRectF(area.left() + 40, area.top() + 82,
                      area.width() - 70, area.height() - 118)

    @staticmethod
    def _plot_point(graph: QRectF, temperature: int, speed: int) -> QPointF:
        x = graph.left() + max(0, min(1, (temperature - 25) / 75)) * graph.width()
        y = graph.bottom() - max(0, min(1, speed / 100)) * graph.height()
        return QPointF(x, y)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton or not self._editable() or self._set_point is None:
            return super().mousePressEvent(event)
        graph = self._graph_rect()
        position = event.position()
        nearest: tuple[float, int] | None = None
        for index, (temperature, speed) in enumerate(self._points()):
            point = self._plot_point(graph, temperature, speed)
            distance = (point.x() - position.x()) ** 2 + (point.y() - position.y()) ** 2
            if nearest is None or distance < nearest[0]:
                nearest = distance, index
        if nearest is not None and nearest[0] <= 20 ** 2:
            self._drag_index = nearest[1]
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._drag_index is None or self._set_point is None or not self._editable():
            self.setCursor(Qt.CursorShape.OpenHandCursor if self._editable()
                           else Qt.CursorShape.ArrowCursor)
            return super().mouseMoveEvent(event)
        points = self._points()
        if not 0 <= self._drag_index < len(points):
            return
        graph = self._graph_rect()
        x_ratio = max(0.0, min(1.0, (event.position().x() - graph.left()) / max(1.0, graph.width())))
        y_ratio = max(0.0, min(1.0, (graph.bottom() - event.position().y()) / max(1.0, graph.height())))
        temperature = round(25 + x_ratio * 75)
        speed = round(y_ratio * 100)
        index = self._drag_index
        lower_temp = points[index - 1][0] + 1 if index else 25
        upper_temp = points[index + 1][0] - 1 if index + 1 < len(points) else 90
        lower_speed = points[index - 1][1] if index else 35
        upper_speed = points[index + 1][1] if index + 1 < len(points) else 100
        if index == len(points) - 1:
            lower_speed = max(lower_speed, 90)
        temperature = max(lower_temp, min(upper_temp, temperature))
        speed = max(lower_speed, min(upper_speed, speed))
        self._set_point(index, temperature, speed)
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event):  # noqa: N802
        if self._drag_index is not None:
            self._drag_index = None
            self.setCursor(Qt.CursorShape.OpenHandCursor if self._editable()
                           else Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event):  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = QRectF(self.rect()).adjusted(8, 8, -8, -8)
        palette = self.palette()
        accent = palette.color(QPalette.ColorRole.Highlight)
        base = palette.color(QPalette.ColorRole.Base)
        foreground = palette.color(QPalette.ColorRole.Text)
        dark = base.lightness() < 128
        background = QLinearGradient(bounds.topLeft(), bounds.bottomRight())
        background.setColorAt(0.0, base)
        background.setColorAt(1.0, base.darker(120) if dark else base.darker(103))
        painter.setPen(QPen(palette.color(QPalette.ColorRole.Mid), 1))
        painter.setBrush(background)
        painter.drawRoundedRect(bounds, 18, 18)

        fan_y = bounds.top() + 46
        radius = min(25.0, bounds.width() / 13)
        for index, center_x in enumerate((bounds.left() + bounds.width() * .22,
                                          bounds.center().x(),
                                          bounds.left() + bounds.width() * .78)):
            center = QPointF(center_x, fan_y)
            painter.setPen(QPen(accent, 2))
            fan_fill = QColor(accent); fan_fill.setAlpha(35)
            painter.setBrush(fan_fill)
            painter.drawEllipse(center, radius, radius)
            painter.setBrush(base)
            for blade in range(7):
                angle = self._phase * (1 if index != 1 else -1) + blade * math.tau / 7
                path = QPainterPath(center)
                path.cubicTo(
                    QPointF(center.x() + math.cos(angle + .2) * radius * .28,
                            center.y() + math.sin(angle + .2) * radius * .28),
                    QPointF(center.x() + math.cos(angle + .7) * radius * .88,
                            center.y() + math.sin(angle + .7) * radius * .88),
                    QPointF(center.x() + math.cos(angle + 1.25) * radius * .52,
                            center.y() + math.sin(angle + 1.25) * radius * .52),
                )
                painter.drawPath(path)
            painter.setBrush(accent)
            painter.drawEllipse(center, 5, 5)

        graph = self._graph_rect(bounds)
        grid_color = QColor(palette.color(QPalette.ColorRole.Mid)); grid_color.setAlpha(80)
        painter.setPen(QPen(grid_color, 1))
        for step in range(6):
            y = graph.bottom() - graph.height() * step / 5
            painter.drawLine(QPointF(graph.left(), y), QPointF(graph.right(), y))
            x = graph.left() + graph.width() * step / 5
            painter.drawLine(QPointF(x, graph.top()), QPointF(x, graph.bottom()))
        points = self._points()
        if points:
            path = QPainterPath()
            plotted = []
            for temp, speed in points:
                plotted.append(self._plot_point(graph, temp, speed))
            path.moveTo(plotted[0])
            for point in plotted[1:]:
                path.lineTo(point)
            painter.setPen(QPen(accent, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
            painter.setPen(QPen(accent.lighter(125) if dark else accent.darker(115), 2))
            painter.setBrush(accent)
            for index, point in enumerate(plotted):
                radius = 8 if index == self._drag_index else 6
                if index == self._drag_index:
                    painter.setBrush(foreground)
                    painter.setPen(QPen(accent, 3))
                else:
                    painter.setBrush(accent)
                    painter.setPen(QPen(accent.lighter(125) if dark else accent.darker(115), 2))
                painter.drawEllipse(point, radius, radius)
        painter.setPen(foreground)
        painter.drawText(graph.adjusted(0, 8, 0, 24), Qt.AlignmentFlag.AlignBottom, "25–100 °C")
        temperature = self._temperature()
        rpm = self._rpm()
        temperature_text = "— °C" if temperature is None else f"{temperature:.0f} °C"
        rpm_text = "— RPM" if rpm is None else f"{rpm:,.0f} RPM".replace(",", ".")
        painter.drawText(bounds.adjusted(0, 10, -16, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                         f"LIVE · {temperature_text} · {rpm_text}")
        if self._editable():
            painter.drawText(bounds.adjusted(16, 10, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                             self._tr("Punkte ziehen"))
        else:
            painter.setPen(QColor("#fbbf24"))
            painter.drawText(bounds.adjusted(16, 10, -16, 0),
                             Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                             self._locked_text())
