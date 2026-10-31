#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic Qt renderer for the seamless high-contrast smoke loop."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter, QPainterPath, QPen

from .model import SmokeSettings


def _mix(first: QColor, second: QColor, amount: float) -> QColor:
    amount = max(0.0, min(1.0, amount))
    return QColor(
        round(first.red() * (1.0 - amount) + second.red() * amount),
        round(first.green() * (1.0 - amount) + second.green() * amount),
        round(first.blue() * (1.0 - amount) + second.blue() * amount),
    )


def _oriented(point: QPointF, direction: str, width: int, height: int) -> QPointF:
    if direction == "left":
        return QPointF(width - point.x(), point.y())
    if direction == "up":
        return QPointF(point.y() * width / height, height - point.x() * height / width)
    if direction == "down":
        return QPointF(point.y() * width / height, point.x() * height / width)
    return point


def render_smoke_frame(
    settings: SmokeSettings,
    phase: float,
    *,
    width: int = 1600,
    height: int = 720,
) -> QImage:
    """Render one loop-periodic frame; identical phases produce identical pixels."""

    width = max(320, min(1920, int(width)))
    height = max(144, min(1080, int(height)))
    phase = float(phase) % 1.0
    image = QImage(width, height, QImage.Format.Format_RGB888)
    image.fill(QColor("#030406"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    background = QLinearGradient(0, 0, width, height)
    background.setColorAt(0.0, QColor("#050609"))
    background.setColorAt(0.48, QColor("#090A0E"))
    background.setColorAt(1.0, QColor("#010203"))
    painter.fillRect(image.rect(), background)

    primary = QColor(settings.primary_color)
    secondary = QColor(settings.secondary_color)
    strand_count = 8 + round(settings.density * 0.12)
    turbulence = 18.0 + settings.turbulence * 0.72
    speed_phase = phase * (0.45 + settings.speed / 100.0)
    sharp = settings.sharpness / 100.0
    glow = settings.glow / 100.0

    for index in range(strand_count):
        seed = index * 1.61803398875
        color = _mix(primary, secondary, (index % 7) / 6.0)
        base_y = height * (0.08 + 0.84 * ((index * 0.381966) % 1.0))
        travel = (speed_phase + index * 0.071) % 1.0
        offset = (travel - 0.5) * width * 0.24
        path = QPainterPath()
        points: list[QPointF] = []
        segments = 10
        for segment in range(segments + 1):
            x = -width * 0.12 + segment * width * 1.24 / segments + offset
            wave = math.sin((segment * 0.61 + seed + phase * math.tau) * 1.42)
            curl = math.sin(segment * 1.07 - phase * math.tau * 1.2 + seed * 2.1)
            y = base_y + (wave * turbulence + curl * turbulence * 0.42)
            points.append(_oriented(QPointF(x, y), settings.direction, width, height))
        path.moveTo(points[0])
        for segment in range(segments):
            first = points[segment]
            second = points[segment + 1]
            control_one = QPointF(
                first.x() + (second.x() - first.x()) * 0.46,
                first.y(),
            )
            control_two = QPointF(
                first.x() + (second.x() - first.x()) * 0.54,
                second.y(),
            )
            path.cubicTo(control_one, control_two, second)

        stroke_scale = max(0.32, height / 720.0)
        width_seed = (10.0 + (index % 5) * 4.0 + settings.density * 0.09) * stroke_scale
        if glow > 0.0:
            glow_color = QColor(color)
            glow_color.setAlpha(round(10 + glow * 28))
            painter.setPen(QPen(glow_color, width_seed * (2.2 + glow * 1.8), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPath(path)
        body = QColor(color)
        body.setAlpha(round(38 + sharp * 72))
        painter.setPen(QPen(body, width_seed * (1.25 - sharp * 0.35), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)
        core = QColor(_mix(color, QColor("#FFFFFF"), 0.24 + sharp * 0.36))
        core.setAlpha(round(78 + sharp * 105))
        painter.setPen(QPen(core, max(1.0, width_seed * (0.17 - sharp * 0.06)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)

    painter.end()
    return image
