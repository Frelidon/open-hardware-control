#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Original vector chassis materials and components; no product art or polling."""

import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainterPath, QPen
from .depth_renderer import draw_case_depth, draw_component_depth
from modules.gpu_profiles.v1_0.visual_catalog import resolve_gpu_visual

# Art parameters, not mechanical dimensions or fan/LED compatibility claims.
# Reference-reviewed fronts: Retro 360 TG, North; glass families use catalog sources.
APPEARANCES = {
    "thermaltake-retro-360-tg": ("retro", "#c7bfaa", .14, 6),
    "fractal-north": ("wood", "#9a774f", .12, 10),
    "fractal-north-xl": ("wood", "#af8554", .15, 12),
    "fractal-meshify-3": ("facets", "#586772", .13, 10),
    "fractal-torrent": ("ribs", "#7f8a8f", .14, 8),
    "nzxt-h5-flow-2024": ("mesh", "#60758b", .11, 10),
    "nzxt-h6-flow": ("bevel", "#b3c5cc", .17, 9),
    "nzxt-h7-flow-2024": ("mesh", "#8294a7", .12, 7),
    "nzxt-h9-flow": ("glass", "#b7c7d5", .17, 6),
    "corsair-3200d": ("frame", "#858b9b", .13, 8),
    "corsair-4000d-airflow": ("triangles", "#788d99", .12, 8),
    "corsair-5000d-airflow": ("triangles", "#9aafb4", .15, 10),
    "corsair-6500d-airflow": ("dual-mesh", "#81979e", .20, 9),
    "corsair-air-5400": ("dual-mesh", "#9bb7c4", .22, 12),
    "lian-li-o11-evo": ("glass", "#98acb9", .19, 7),
    "lian-li-o11-vision": ("glass-top", "#c3d8de", .18, 6),
    "lian-li-lancool-207": ("mesh", "#768b98", .14, 6),
    "lian-li-lancool-iii": ("frame", "#778b93", .15, 7),
    "hyte-y60": ("bevel", "#90a9bf", .20, 10),
    "hyte-y70": ("bevel-display", "#aab9d5", .22, 12),
    "montech-air-903-max": ("mesh", "#8f959b", .16, 9),
    "montech-king-95-pro": ("curved-glass", "#b4c6d2", .21, 14),
    "bequiet-pure-base-500dx": ("split-mesh", "#8d938d", .12, 10),
    "bequiet-shadow-base-800": ("split-mesh", "#acb5ab", .16, 12),
    "phanteks-g500a": ("mesh", "#899ea9", .15, 14),
    "phanteks-nv5": ("glass", "#b4d0d5", .16, 12),
    "coolermaster-td500-v2": ("facets", "#8ca0bb", .14, 12),
    "coolermaster-nr200p-v2": ("compact", "#99b7bb", .13, 8),
    "asus-proart-pa602": ("ribs", "#a09b81", .17, 12),
    "antec-flux-pro": ("wood-mesh", "#8a6850", .16, 10),
}


def case_aspect_ratio(case_id):
    """Original side-view art proportions, not a hardware clearance table."""
    return {
        "thermaltake-retro-360-tg": .95, "fractal-north": .96, "fractal-north-xl": 1.03,
        "fractal-meshify-3": .98, "fractal-torrent": 1.08, "nzxt-h5-flow-2024": .93,
        "nzxt-h6-flow": 1.05, "nzxt-h7-flow-2024": .95, "nzxt-h9-flow": 1.10,
        "corsair-3200d": .98, "corsair-4000d-airflow": .94, "corsair-5000d-airflow": 1.02,
        "corsair-6500d-airflow": 1.13, "corsair-air-5400": 1.16, "lian-li-o11-evo": 1.09,
        "lian-li-o11-vision": 1.10, "lian-li-lancool-207": .92, "lian-li-lancool-iii": 1.02,
        "hyte-y60": 1.08, "hyte-y70": 1.06, "montech-air-903-max": .98,
        "montech-king-95-pro": 1.15, "bequiet-pure-base-500dx": 1.02,
        "bequiet-shadow-base-800": 1.06, "phanteks-g500a": 1.03, "phanteks-nv5": 1.09,
        "coolermaster-td500-v2": 1.00, "coolermaster-nr200p-v2": 1.35,
        "asus-proart-pa602": 1.10, "antec-flux-pro": 1.08,
    }.get(case_id, .95)


def gradient(rect, first, last):
    fill = QLinearGradient(rect.topLeft(), rect.bottomRight())
    fill.setColorAt(0, QColor(first))
    fill.setColorAt(1, QColor(last))
    return fill


def draw_chassis(painter, area, case_id):
    pattern, tone, front_fraction, detail = APPEARANCES.get(case_id, APPEARANCES["thermaltake-retro-360-tg"])
    metal = QColor(tone)
    draw_case_depth(painter, area, metal)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(0, 0, 0, 90))
    painter.drawRoundedRect(area.adjusted(4, 6, 4, 6), 14, 14)
    painter.setPen(QPen(metal, 2))
    painter.setBrush(gradient(area, metal.lighter(135), metal.darker(210)))
    painter.drawRoundedRect(area, 5 if pattern == "retro" else 14, 5 if pattern == "retro" else 14)
    inner = area.adjusted(12, 36, -12, -24)
    painter.setPen(QPen(metal.darker(160), 1))
    painter.setBrush(gradient(inner, "#101b24", "#080e16"))
    painter.drawRoundedRect(inner, 6, 6)
    front = QRectF(area.right() - area.width() * front_fraction, area.top() + 32,
                   area.width() * front_fraction - 8, area.height() - 52)
    glass = QRectF(inner.left() + 4, inner.top() + 3, front.left() - inner.left() - 10, inner.height() - 8)
    painter.setBrush(gradient(glass, "#243540", "#101822"))
    painter.setPen(QPen(metal.darker(180), 2))
    painter.drawRoundedRect(glass, 4, 4)
    # PSU compartment and actual-looking motherboard tray behind movable slots.
    shroud = QRectF(glass.left() + 4, area.top() + area.height() * .78, glass.width() - 8, area.height() * .15)
    painter.setBrush(gradient(shroud, "#2a3640", "#111b22"))
    painter.drawRoundedRect(shroud, 3, 3)
    board = QRectF(area.left() + area.width() * .20, area.top() + area.height() * .23,
                  area.width() * .39, area.height() * .47)
    painter.setPen(QPen(QColor("#395464"), 1))
    painter.setBrush(QColor("#12272a"))
    painter.drawRoundedRect(board, 4, 4)
    for i in range(6):
        chip = QRectF(board.left() + 12 + i * 12, board.top() + 13, 8, 28)
        painter.setBrush(QColor("#344754"))
        painter.drawRoundedRect(chip, 2, 2)
        painter.drawLine(board.left() + 12, board.bottom() - 12 - i * 7, board.right() - 10, board.bottom() - 12 - i * 7)
    for y in (.26, .43, .62):
        hole = QRectF(area.left() + area.width() * .61, area.top() + area.height() * y, 16, 32)
        painter.setBrush(QColor("#070c12"))
        painter.drawRoundedRect(hole, 6, 6)
    # Top filter and rear PCI vent are decorative; never extra controllable blocks.
    painter.setPen(QPen(metal.darker(190), 1))
    for i in range(12):
        x = area.left() + 22 + i * (area.width() * .68 / 12)
        painter.drawLine(QPointF(x, area.top() + 11), QPointF(x + 10, area.top() + 11))
    for i in range(7):
        painter.drawRoundedRect(QRectF(area.left() + 18, area.top() + area.height() * .55 + i * 9, 35, 5), 1, 1)
    painter.setBrush(gradient(front, metal.darker(130), metal.darker(230)))
    painter.setPen(QPen(metal, 1))
    painter.drawRoundedRect(front, 5, 5)
    if pattern == "retro":
        painter.setBrush(gradient(front, metal.lighter(115), metal.darker(110)))
        painter.drawRoundedRect(front, 2, 2)
        for row in range(3):
            bay = QRectF(front.left() + 7, front.top() + 10 + row * 30, front.width() - 14, 23)
            painter.setBrush(metal.darker(112))
            painter.drawRoundedRect(bay, 2, 2)
            painter.drawLine(bay.left() + 5, bay.center().y(), bay.right() - 5, bay.center().y())
        painter.setPen(QPen(metal.darker(200), 2))
        for y in range(int(front.top() + 118), int(front.bottom() - 16), 7):
            painter.drawLine(front.left() + 9, y, front.right() - 9, y)
    elif "wood" in pattern:
        for i in range(detail):
            x = front.left() + 6 + i * (front.width() - 12) / detail
            painter.setPen(QPen(metal.lighter(130), max(2, front.width() / detail * .48)))
            painter.drawLine(QPointF(x, front.top() + 10), QPointF(x, front.bottom() - 10))
            painter.setPen(QPen(metal.darker(170), 1))
            painter.drawLine(QPointF(x + 2, front.top() + 10), QPointF(x + 2, front.bottom() - 10))
    elif "glass" in pattern or "bevel" in pattern:
        painter.setBrush(gradient(front, "#234859", "#111e2c"))
        painter.drawRoundedRect(front.adjusted(3, 3, -3, -3), 18 if pattern == "curved-glass" else 3, 3)
        painter.setPen(QPen(QColor("#6b91a8"), 1))
        painter.drawLine(front.topLeft() + QPointF(6, 5), front.bottomRight() - QPointF(6, 5))
        if "bevel" in pattern:
            painter.drawLine(front.left() + 8, front.top() + 2, front.left() + 8, front.bottom() - 2)
        if pattern == "bevel-display":
            display = front.adjusted(12, 70, -12, -70)
            painter.setBrush(gradient(display, "#34577c", "#131c35"))
            painter.drawRoundedRect(display, 5, 5)
        if pattern == "glass-top":
            painter.setPen(QPen(QColor("#b2ced9"), 2))
            painter.drawLine(area.left() + 12, area.top() + 5, front.right(), area.top() + 5)
    else:
        painter.setPen(QPen(metal.lighter(130), 1))
        step = max(6, int(front.width() / detail))
        if pattern == "ribs":
            for x in range(int(front.left() + 7), int(front.right() - 4), step):
                painter.drawLine(x, front.top() + 8, x, front.bottom() - 8)
        else:
            for y in range(int(front.top() + 8), int(front.bottom() - 7), 8):
                for x in range(int(front.left() + 7), int(front.right() - 5), 8):
                    painter.drawPoint(x + (4 if y % 16 else 0), y)
        if pattern in {"facets", "triangles", "frame"}:
            for i in range(4):
                y = front.top() + i * front.height() / 4
                painter.drawLine(front.left() + 4, y + 4, front.right() - 4, y + front.height() / 4)
        if pattern == "split-mesh":
            painter.setPen(QPen(QColor("#8fbcd7"), 2))
            painter.drawLine(front.center().x(), front.top() + 10, front.center().x(), front.bottom() - 10)
    # Glass-edge reflection, fastening screws, feet and power/I/O details.
    painter.setPen(QPen(QColor(154, 201, 225, 55), 2))
    painter.drawLine(glass.topLeft() + QPointF(10, 5), glass.topRight() - QPointF(10, -5))
    for point in (inner.topLeft(), inner.topRight(), inner.bottomLeft(), inner.bottomRight()):
        painter.setPen(QPen(metal.lighter(125), 1))
        painter.setBrush(metal.darker(220))
        painter.drawEllipse(point, 2.5, 2.5)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#253440"))
    for x in (area.left() + 25, area.right() - 65):
        painter.drawRoundedRect(QRectF(x, area.bottom() - 1, 40, 10), 3, 3)
    painter.setBrush(QColor("#91d6e3"))
    painter.drawEllipse(QPointF(area.right() - 21, area.top() + 16), 3, 3)
    painter.setBrush(QColor("#17222c"))
    for i in range(2):
        painter.drawRoundedRect(QRectF(area.right() - 58 + i * 14, area.top() + 13, 9, 5), 1, 1)
    painter.restore()
    return glass


def draw_fan(painter, center, color, label="", highlighted=False, radius=24):
    painter.save()
    painter.translate(center)
    painter.scale(radius / 24, radius / 24)
    center = QPointF()
    frame = QRectF(center.x() - 24, center.y() - 24, 48, 48)
    draw_component_depth(painter, frame)
    painter.setPen(QPen(QColor("#4b5c6b"), 1))
    painter.setBrush(gradient(frame, "#334453", "#0d1822"))
    painter.drawRoundedRect(frame, 5, 5)
    painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 48), 6))
    painter.setBrush(QColor("#09121a"))
    painter.drawEllipse(center, 20, 20)
    painter.setPen(QPen(color.lighter(130), 2.5))
    painter.drawEllipse(center, 19, 19)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color.red(), color.green(), color.blue(), 190 if highlighted else 120))
    for n in range(7):
        angle = n * math.tau / 7
        blade = QPainterPath(center)
        def point(a, r): return center + QPointF(math.cos(a) * r, math.sin(a) * r)
        blade.cubicTo(point(angle + .1, 12), point(angle + .8, 22), point(angle + 1, 14))
        blade.quadTo(point(angle + 1.2, 6), center)
        painter.drawPath(blade)
    painter.setBrush(gradient(frame, "#52687a", "#16232e"))
    painter.drawEllipse(center, 7, 7)
    for dx, dy in ((-20, -20), (20, -20), (-20, 20), (20, 20)):
        painter.setBrush(QColor("#0b1219"))
        painter.drawEllipse(center + QPointF(dx, dy), 1.6, 1.6)
    if label:
        painter.setPen(QColor("#f4fbff"))
        painter.setBrush(QColor("#112431"))
        painter.drawEllipse(center, 10, 10)
        font = QFont(painter.font())
        font.setBold(True)
        font.setPixelSize(12)
        painter.setFont(font)
        painter.drawText(QRectF(center.x() - 10, center.y() - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, label)
    painter.restore()


def draw_component(painter, rect, position, accent):
    painter.save()
    native_width, native_height = {"gpu": (230, 68), "gpu-support": (190, 42), "ram": (82, 126)}.get(position, (96, 96))
    painter.translate(rect.center())
    painter.scale(rect.width() / native_width, rect.height() / native_height)
    rect = QRectF(-native_width / 2, -native_height / 2, native_width, native_height)
    draw_component_depth(painter, rect)
    painter.setPen(QPen(QColor("#536c80"), 1))
    painter.setBrush(gradient(rect, "#34485a", "#101923"))
    if position == "gpu":
        body = rect.adjusted(5, 7, -5, -7)
        painter.drawRoundedRect(body, 5, 5)
        for i in range(3):
            center = QPointF(body.left() + body.width() * (i + .5) / 3, body.center().y())
            painter.setPen(QPen(QColor("#88a4b8"), 1))
            painter.drawEllipse(center, 18, 18)
            for n in range(7):
                a = n * math.tau / 7
                painter.drawLine(center + QPointF(math.cos(a) * 6, math.sin(a) * 6),
                                 center + QPointF(math.cos(a + .5) * 15, math.sin(a + .5) * 15))
        painter.setPen(QPen(accent.lighter(135), 3))
        painter.drawLine(body.left() + 7, body.top() + 3, body.right() - 7, body.top() + 3)
    elif position == "ram":
        for offset in (-16, 16):
            module = QRectF(rect.center().x() + offset - 10, rect.top() + 8, 20, rect.height() - 16)
            painter.setPen(QPen(QColor("#7c92a4"), 1))
            painter.setBrush(gradient(module, "#405a6e", "#142432"))
            painter.drawRoundedRect(module, 3, 3)
            painter.setPen(QPen(accent, 3))
            painter.drawLine(module.topLeft() + QPointF(3, 3), module.topRight() - QPointF(3, -3))
            painter.setPen(QPen(QColor("#c7a660"), 2))
            for y in range(int(module.bottom() - 12), int(module.bottom() - 3), 3):
                painter.drawLine(module.left() + 4, y, module.right() - 4, y)
    elif position == "gpu-support":
        painter.drawRoundedRect(rect.adjusted(6, 10, -6, -10), 4, 4)
        painter.setPen(QPen(accent, 3))
        painter.drawLine(rect.left() + 12, rect.center().y(), rect.right() - 12, rect.center().y())
    else:
        screen = QRectF(rect.center().x() - 43, rect.center().y() - 22, 86, 44)
        painter.drawRoundedRect(screen.adjusted(-4, -4, 4, 4), 8, 8)
        painter.setBrush(gradient(screen, "#244d69", "#111f39"))
        painter.setPen(QPen(accent, 1))
        painter.drawRoundedRect(screen, 5, 5)
        painter.setPen(QColor("#d8edff"))
        painter.drawText(screen, Qt.AlignmentFlag.AlignCenter, "OHC")
    painter.restore()


def _sample_color(colors, index, count, fallback):
    if not colors:
        return fallback
    sample = min(len(colors) - 1, int((index + .5) * len(colors) / max(1, count)))
    return QColor("#" + colors[sample])


def draw_gpu_component(painter, rect, name, profile_id, colors, accent):
    """Draw an original schematic matching only the selected light topology."""

    profile = resolve_gpu_visual(profile_id, name)
    painter.save()
    native_width, native_height = 230, 68
    painter.translate(rect.center())
    painter.scale(rect.width() / native_width, rect.height() / native_height)
    body = QRectF(-110, -27, 220, 54)
    draw_component_depth(painter, body)
    painter.setPen(QPen(QColor("#536c80"), 1))
    painter.setBrush(gradient(body, "#34485a", "#101923"))
    painter.drawRoundedRect(body, 6, 6)
    fan_count = max(1, min(4, profile.fan_count))
    fan_radius_value = min(19.0, body.width() / fan_count * .34)
    for index in range(fan_count):
        center = QPointF(body.left() + body.width() * (index + .5) / fan_count, body.center().y() + 2)
        color = _sample_color(colors, index, fan_count, accent)
        ring_color = color if profile.lighting in {"fan-rings", "mixed"} else QColor("#71899a")
        painter.setPen(QPen(ring_color, 3 if profile.lighting in {"fan-rings", "mixed"} else 1))
        painter.setBrush(QColor("#08121a"))
        painter.drawEllipse(center, fan_radius_value, fan_radius_value)
        painter.setPen(QPen(QColor("#7890a1"), 1))
        for blade in range(7):
            angle = blade * math.tau / 7
            painter.drawLine(
                center + QPointF(math.cos(angle) * 5, math.sin(angle) * 5),
                center + QPointF(math.cos(angle + .48) * (fan_radius_value - 3),
                                 math.sin(angle + .48) * (fan_radius_value - 3)),
            )
        hub = color if profile.lighting == "fan-hubs" else QColor("#526879")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(hub)
        painter.drawEllipse(center, 5.5, 5.5)
    if profile.lighting in {"edge-strip", "mixed", "indirect"}:
        line_y = body.top() + (3 if profile.lighting != "indirect" else 7)
        segments = min(36, max(8, len(colors)))
        for index in range(segments):
            color = _sample_color(colors, index, segments, accent)
            left = body.left() + 8 + (body.width() - 16) * index / segments
            right = body.left() + 8 + (body.width() - 16) * (index + 1) / segments
            painter.setPen(QPen(color, 4 if profile.lighting == "edge-strip" else 2.5))
            painter.drawLine(QPointF(left, line_y), QPointF(right, line_y))
    elif profile.lighting == "logo":
        painter.setPen(QPen(_sample_color(colors, 0, 1, accent), 2))
        painter.drawText(body.adjusted(8, 5, -8, -5), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "OHC")
    painter.restore()


def slot_label_placements(bounds, area, rectangles, *, height=30, side_first=False):
    """Place bounded callouts without covering components or other labels."""
    safe = bounds.adjusted(8, 8, -8, -8)
    occupied = [r.adjusted(-3, -3, 3, 3) for r in rectangles]
    result = [None] * len(rectangles)
    for index in sorted(range(len(rectangles)), key=lambda i: rectangles[i].center().y()):
        rect = rectangles[index]
        width = min(190, max(90, rect.width() + 20))
        candidates = [QRectF(rect.center().x() - width / 2, rect.bottom() + 5, width, height),
                      QRectF(rect.center().x() - width / 2, rect.top() - height - 5, width, height)]
        sides = [(safe.left(), area.left() - safe.left() - 12),
                 (area.right() + 12, safe.right() - area.right() - 12)]
        if rect.center().x() > area.center().x():
            sides.reverse()
        for left, available in sides:
            if available < 70:
                continue
            badge_width = min(190, available)
            desired = max(safe.top(), min(safe.bottom() - height, rect.center().y() - height / 2))
            for delta in [0, *[sign * step for step in range(height + 4, int(safe.height()), height + 4) for sign in (1, -1)]]:
                candidates.append(QRectF(left, desired + delta, badge_width, height))
        if side_first: candidates = [*candidates[2:], *candidates[:2]]
        for badge in candidates:
            if safe.contains(badge) and not any(badge.intersects(other) for other in occupied):
                result[index] = badge
                occupied.append(badge.adjusted(-3, -3, 3, 3))
                break
    return result


def draw_slot_label(painter, rect, name, connection, selected, *, badge=None, metadata=None):
    if badge is None:
        return  # Dense/custom layouts retain complete mouse tooltips and table rows.
    painter.save()
    painter.setPen(QPen(QColor("#7694a8"), 1))
    anchor = QPointF(max(rect.left(), min(rect.right(), badge.center().x())),
                     max(rect.top(), min(rect.bottom(), badge.center().y())))
    painter.drawLine(anchor, badge.center())
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(9, 18, 28, 240))
    painter.drawRoundedRect(badge, 5, 5)
    font = QFont(painter.font())
    font.setPixelSize(11)
    font.setBold(selected)
    painter.setFont(font)
    metrics = QFontMetrics(font)
    if metadata:
        tones = ("#e4f0f8", "#8ca9be", "#a8d8ec", "#b7c9d7", "#b7c9d7")
        for index, (text, tone) in enumerate(zip((name, *metadata), tones)):
            painter.setPen(QColor(tone))
            line = QRectF(badge.left() + 5, badge.top() + index * 15, badge.width() - 10, 15)
            painter.drawText(line, Qt.AlignmentFlag.AlignCenter,
                             metrics.elidedText(text, Qt.TextElideMode.ElideRight, int(line.width())))
        painter.restore()
        return
    painter.setPen(QColor("#e4f0f8"))
    painter.drawText(badge.adjusted(5, 0, -5, -13), Qt.AlignmentFlag.AlignCenter,
                     metrics.elidedText(name, Qt.TextElideMode.ElideRight, int(badge.width() - 10)))
    painter.setPen(QColor("#8ca9be"))
    painter.drawText(badge.adjusted(5, 13, -5, 0), Qt.AlignmentFlag.AlignCenter,
                     metrics.elidedText(connection, Qt.TextElideMode.ElideRight, int(badge.width() - 10)))
    painter.restore()
