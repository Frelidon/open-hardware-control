#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Original OHC renderer for seamless directional light-band waves."""

from __future__ import annotations

import math

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter, QPen, QRadialGradient


DIRECTION_ANGLES: dict[str, float] = {
    "right": 0.0,
    "left": 180.0,
    "down": 90.0,
    "up": -90.0,
    "down-right": 45.0,
    "up-left": 225.0,
    "down-left": 135.0,
    "up-right": -45.0,
}


def _mix(first: QColor, second: QColor, amount: float) -> QColor:
    amount = max(0.0, min(1.0, amount))
    return QColor(
        round(first.red() * (1.0 - amount) + second.red() * amount),
        round(first.green() * (1.0 - amount) + second.green() * amount),
        round(first.blue() * (1.0 - amount) + second.blue() * amount),
    )


def render_light_bands_frame(
    direction: str,
    phase: float,
    *,
    width: int = 1600,
    height: int = 720,
) -> QImage:
    """Render one deterministic frame of an eight-direction seamless light wave."""

    width = max(320, min(4800, int(width)))
    height = max(144, min(2160, int(height)))
    phase = float(phase) % 1.0
    angle = DIRECTION_ANGLES.get(direction, 0.0)
    image = QImage(width, height, QImage.Format.Format_RGB888)
    image.fill(QColor("#020307"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    backdrop = QRadialGradient(width * 0.5, height * 0.5, width * 0.68)
    backdrop.setColorAt(0.0, QColor("#15121A"))
    backdrop.setColorAt(0.52, QColor("#080A11"))
    backdrop.setColorAt(1.0, QColor("#010205"))
    painter.fillRect(image.rect(), backdrop)

    painter.save()
    painter.translate(width / 2, height / 2)
    painter.rotate(angle)
    extent = math.hypot(width, height) * 0.62
    bar_width = max(12.0, height * 0.034)
    spacing = bar_width * 1.62
    count = math.ceil(extent * 2 / spacing) + 4
    warm = QColor("#FF5A20")
    gold = QColor("#FFB229")
    core = QColor("#FFF4C7")
    for index in range(-count // 2, count // 2 + 1):
        x = index * spacing
        position = (x / (extent * 2) + 0.5) % 1.0
        distance = abs(((position - phase + 0.5) % 1.0) - 0.5)
        pulse = math.exp(-((distance / 0.105) ** 2))
        echo_distance = abs(((position - phase - 0.32 + 0.5) % 1.0) - 0.5)
        pulse = min(1.0, pulse + math.exp(-((echo_distance / 0.18) ** 2)) * 0.23)
        body = _mix(QColor("#160B07"), warm, pulse)
        highlight = _mix(body, gold, pulse)
        center = _mix(highlight, core, pulse * 0.72)
        rect = QRectF(x - bar_width / 2, -extent, bar_width, extent * 2)
        if pulse > 0.001:
            glow = QColor(warm)
            glow.setAlpha(round(pulse * 98))
            painter.setPen(QPen(glow, bar_width * (1.7 + pulse), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(rect.center().x(), rect.top(), rect.center().x(), rect.bottom())
        gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
        gradient.setColorAt(0.0, _mix(body, QColor("#090A10"), pulse))
        gradient.setColorAt(0.18, body)
        gradient.setColorAt(0.5, center)
        gradient.setColorAt(0.82, body)
        gradient.setColorAt(1.0, _mix(body, QColor("#08090E"), pulse))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, bar_width * 0.42, bar_width * 0.42)
    painter.restore()

    shade = QLinearGradient(0, 0, 0, height)
    shade.setColorAt(0.0, QColor(0, 0, 0, 170))
    shade.setColorAt(0.18, QColor(0, 0, 0, 12))
    shade.setColorAt(0.78, QColor(0, 0, 0, 8))
    shade.setColorAt(1.0, QColor(0, 0, 0, 190))
    painter.fillRect(image.rect(), shade)
    painter.setPen(QPen(QColor(255, 155, 64, 75), max(1.0, height * 0.004)))
    painter.drawLine(0, round(height * 0.08), width, round(height * 0.08))
    painter.drawLine(0, round(height * 0.92), width, round(height * 0.92))
    painter.end()
    return image
