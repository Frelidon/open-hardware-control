# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, presentation-only fan light rings from existing colour frames."""
from __future__ import annotations

import math
from functools import lru_cache

from modules.rgb_studio.v1_15.led_topology import POINTS, normalize_path


@lru_cache(maxsize=512)
def brighter_preview_color(color: str, factor: float = 1.18) -> str:
    """Lift preview-only RGB intensity while preserving black and colour steps."""
    value = str(color).strip().lower().removeprefix("#")
    if len(value) != 6:
        return value
    try:
        channels = tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))
    except ValueError:
        return value
    bounded = max(1.0, min(1.35, float(factor)))
    return "".join(f"{min(255, round(channel * bounded)):02x}" for channel in channels)


def ring_segments(colors, index, fan_count, path=None):
    """Project colours schematically unless an exact fan-ring path is declared.

    This neither creates LED counts nor represents an RPM measurement. A saved
    line remains a line for effect calculation; its colours are merely shown
    on the existing fan illustration, without inventing a physical LED order.
    """
    if (type(index) is not int or type(fan_count) is not int
            or not 1 <= fan_count <= 64 or not 0 <= index < fan_count
            or not colors or len(colors) > 512):
        return ()
    start, clockwise = 0.0, True
    declared = normalize_path(path)
    if (declared is not None and declared["kind"] == "ring"
            and declared["units"] == fan_count and len(colors) % fan_count == 0):
        if declared.get("reverse_units", False):
            index = fan_count - 1 - index
        x, y = POINTS[declared["start"]]
        start = -math.degrees(math.atan2(y - .5, x - .5))
        clockwise = declared["clockwise"]
    first, last = index * len(colors) // fan_count, (index + 1) * len(colors) // fan_count
    # When fewer logical LEDs than fan illustrations are reported, do not
    # manufacture colours for empty fan segments.
    if first == last:
        return ()
    amount = min(24, last - first)
    step = (-360.0 if clockwise else 360.0) / amount
    return tuple((start + n * step, step, colors[first + n * (last - first) // amount])
                 for n in range(amount))


def draw_light_ring(painter, center, radius, colors, index, fan_count, path=None):
    """Keep the fan frame, stationary blades, channel label and hit area intact."""
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QColor, QPen

    segments = ring_segments(colors, index, fan_count, path)
    if not segments:
        return
    painter.save()
    painter.setBrush(Qt.BrushStyle.NoBrush)
    ring_radius = radius * 19 / 24
    ring = QRectF(center.x() - ring_radius, center.y() - ring_radius,
                  ring_radius * 2, ring_radius * 2)
    for start, span, color in segments:
        painter.setPen(QPen(QColor("#" + brighter_preview_color(color)),
                            max(2.2, radius * .12),
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        painter.drawArc(ring, round(start * 16), round(span * 16))
    painter.restore()
