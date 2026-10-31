#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Original OHC glow/particle decorations for editable Levita Layer 2."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen


SUPPORTED_MOTION_THEMES = frozenset({
    "ohc-spectrum-ring", "ohc-neon-double-arc", "ohc-prism-segments", "ohc-aurora-radar",
})


def _hue(phase: float, offset: float, alpha: int = 255) -> QColor:
    color = QColor.fromHsvF((phase + offset) % 1.0, 0.72, 1.0, alpha / 255.0)
    return color


def _arc(
    painter: QPainter, rect: QRectF, start: float, length: float, color: QColor, width: float,
) -> None:
    pen = QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawArc(rect, round(start * 16), round(length * 16))


def _glowing_arc(
    painter: QPainter, rect: QRectF, start: float, length: float, color: QColor, core: float = 6.0,
) -> None:
    for width, alpha in ((34.0, 20), (22.0, 35), (13.0, 72)):
        glow = QColor(color)
        glow.setAlpha(alpha)
        _arc(painter, rect, start, length, glow, width)
    core_color = QColor(color)
    core_color.setAlpha(235)
    _arc(painter, rect, start, length, core_color, core)
    highlight = QColor("#ffffff")
    highlight.setAlpha(175)
    _arc(painter, rect, start + length * 0.72, length * 0.12, highlight, max(2.0, core / 3))


def _particles(
    painter: QPainter, cx: float, cy: float, rx: float, ry: float, phase: float,
    *, count: int, hue_offset: float = 0.0,
) -> None:
    painter.setPen(Qt.PenStyle.NoPen)
    for index in range(count):
        progress = (phase + index / count + 0.025 * math.sin(index * 4.7)) % 1.0
        angle = progress * math.tau
        wobble = 1.0 + 0.035 * math.sin(angle * 5.0 + phase * math.tau)
        x = cx + math.cos(angle) * rx * wobble
        y = cy + math.sin(angle) * ry * wobble
        radius = 2.0 + 4.5 * (0.5 + 0.5 * math.sin(index * 2.1 + phase * math.tau * 3))
        color = _hue(phase, hue_offset + index / max(1, count), 210)
        glow = QColor(color)
        glow.setAlpha(45)
        painter.setBrush(glow)
        painter.drawEllipse(QPointF(x, y), radius * 3.0, radius * 3.0)
        painter.setBrush(color)
        painter.drawEllipse(QPointF(x, y), radius, radius)


def _ring(painter: QPainter, cx: float, cy: float, rx: float, ry: float, phase: float) -> None:
    rect = QRectF(cx - rx, cy - ry, rx * 2, ry * 2)
    rotation = phase * 360.0
    for index in range(8):
        start = -rotation + index * 45.0
        color = _hue(phase, index / 8.0)
        _glowing_arc(painter, rect, start, 28.0, color, 7.0)
    _particles(painter, cx, cy, rx, ry, phase, count=24)


def _aurora(painter: QPainter, phase: float) -> None:
    for band in range(4):
        path = QPainterPath(QPointF(170, 355 + band * 18))
        for x in range(170, 1450, 24):
            y = 340 + band * 18 + 55 * math.sin(x / 155 + phase * math.tau + band * 0.8)
            path.lineTo(x, y)
        color = _hue(phase, 0.34 + band * 0.08, 80 - band * 10)
        painter.setPen(QPen(color, 26 - band * 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)
    rect = QRectF(570, 155, 380, 380)
    _glowing_arc(painter, rect, -phase * 360, 82, _hue(phase, 0.36), 5)
    _glowing_arc(painter, rect.adjusted(32, 32, -32, -32), phase * 360 + 150, 48, _hue(phase, 0.73), 4)
    _particles(painter, 760, 345, 190, 190, phase, count=20, hue_offset=0.3)


def render_layer2_motion_frame(
    theme: str, phase: float, *, width: int = 1600, height: int = 720,
) -> QImage:
    """Render one transparent, deterministic and seamlessly looping frame."""
    key = str(theme)
    image = QImage(1600, 720, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p = float(phase) % 1.0
    if key == "ohc-spectrum-ring":
        _ring(painter, 760, 350, 235, 235, p)
    elif key == "ohc-neon-double-arc":
        _ring(painter, 400, 355, 175, 175, p)
        _ring(painter, 1110, 355, 175, 175, 1.0 - p)
    elif key == "ohc-prism-segments":
        _ring(painter, 760, 360, 250, 250, p)
        _ring(painter, 760, 360, 205, 205, 1.0 - p)
        _particles(painter, 760, 360, 330, 255, p, count=28, hue_offset=0.12)
    elif key == "ohc-aurora-radar":
        _aurora(painter, p)
    painter.end()
    if (width, height) != (1600, 720):
        return image.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio,
                            Qt.TransformationMode.SmoothTransformation)
    return image
