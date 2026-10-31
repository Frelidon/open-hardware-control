# SPDX-License-Identifier: GPL-3.0-or-later
"""Original 2.5-D projected edges and soft material highlights."""
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPen, QPolygonF


def draw_case_depth(painter, area, metal):
    painter.save()
    offset = QPointF(min(18, area.width() * .035), -min(14, area.height() * .025))
    painter.setPen(QPen(metal.darker(160), 1))
    for points in ((area.topLeft(), area.topLeft() + offset, area.topRight() + offset, area.topRight()),
                   (area.topRight(), area.topRight() + offset, area.bottomRight() + offset, area.bottomRight())):
        gradient = QLinearGradient(points[0], points[2])
        gradient.setColorAt(0, metal.lighter(135))
        gradient.setColorAt(1, metal.darker(200))
        painter.setBrush(gradient)
        painter.drawPolygon(QPolygonF(points))
    painter.restore()


def draw_component_depth(painter, rect):
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    for depth in (6, 4, 2):
        painter.setBrush(QColor(0, 0, 0, 35))
        painter.drawRoundedRect(rect.translated(depth, depth), 5, 5)
    painter.setPen(QPen(QColor(184, 224, 255, 110), 1))
    painter.drawLine(rect.topLeft(), rect.topRight())
    painter.restore()
