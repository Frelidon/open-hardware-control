# SPDX-License-Identifier: GPL-3.0-or-later
"""Proportional schematic geometry, not CAD or hardware detection."""

from dataclasses import replace
from PySide6.QtCore import QPointF, QRectF
from rgb_devices import normalize_layout_scale
from .catalog import case_template

# Artistic side-view mounting centers. Retro's front is below the drive fascia;
# front/top/MB-side/rear/PSU-cover mounts reviewed against the official manual:
# https://file.thermaltake.com/file/qig/Retro360TG_Manual.pdf
BASE_POINTS = {"top": (.45, .13), "bottom": (.46, .83), "rear": (.13, .31),
               "front": (.79, .54), "side": (.66, .43), "gpu": (.40, .59),
               "gpu-support": (.40, .70), "ram": (.51, .32), "pump": (.33, .36)}


def mount_point(case_id, position, ordinal=0):
    template = case_template(case_id)
    x, y = BASE_POINTS.get(position, (.5, .5))
    if template.visual_style == "panorama":
        x, y = {"side": (.69, .43), "front": (.79, .44), "bottom": (.47, .85)}.get(position, (x, y))
    elif template.visual_style == "compact":
        x, y = {"top": (.43, .16), "bottom": (.43, .79), "front": (.78, .46)}.get(position, (x, y))
    elif template.visual_style == "dual":
        x, y = {"side": (.63, .43), "front": (.76, .44)}.get(position, (x, y))
    if case_id != "thermaltake-retro-360-tg" and position == "front":
        y = .45
    if ordinal:
        x = max(.10, x - .10 * (ordinal % 3))
        y = min(.88, y + .08 * ((ordinal + 2) // 3))
    return x, y


def arrange_case_slots(slots, case_id):
    """Explicit arrangement only: preserve hardware identity, counts and scale."""
    ordinals, result = {}, []
    for slot in slots:
        ordinal = ordinals.get(slot.position, 0)
        ordinals[slot.position] = ordinal + 1
        x, y = mount_point(case_id, slot.position, ordinal)
        result.append(replace(slot, x=x, y=y))
    return result


def fitted_slot_rect(slot, area, *, point=None, scale=None):
    """Keep render/hit-test geometry inside the chassis at any viewport size."""
    factor = area.height() / 540
    count = max(1, min(12, slot.count))
    if slot.position in {"top", "bottom"}:
        width, height = min(220, count * 58), 58
    elif slot.position in {"front", "side", "rear"}:
        width, height = 58, min(260, count * 58)
    else:
        width, height = {"gpu": (208, 62), "gpu-support": (165, 35),
                         "ram": (56, 110)}.get(slot.position, (78, 78))
    multiplier = normalize_layout_scale(slot.scale if scale is None else scale)
    safe = QRectF(area.left() + area.width() * .055, area.top() + area.height() * .075,
                  area.width() * .79, area.height() * .85)
    width, height = min(safe.width(), width * factor * multiplier), min(safe.height(), height * factor * multiplier)
    center = point or QPointF(area.left() + area.width() * slot.x, area.top() + area.height() * slot.y)
    x = max(safe.left() + width / 2, min(safe.right() - width / 2, center.x()))
    y = max(safe.top() + height / 2, min(safe.bottom() - height / 2, center.y()))
    return QRectF(x - width / 2, y - height / 2, width, height)


def fan_radius(rect, count, horizontal):
    cell = rect.width() / max(1, count) if horizontal else rect.height() / max(1, count)
    cross = rect.height() if horizontal else rect.width()
    return max(1, min(cell, cross) * .40)
