#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded independent cooling positions; hardware mappings remain shared."""

from dataclasses import replace
import json
import math
from rgb_devices import normalize_layout_scale

SYNC_KEY = "case_workspace/synchronize"
POSITIONS_KEY = "case_workspace/cooling_positions"
POSITIONS = {"top", "front", "side", "bottom", "rear", "gpu", "gpu-support", "ram", "pump"}


def layout_synchronized(host):
    return host.settings.value(SYNC_KEY, True, type=bool)


def read_positions(host):
    try:
        raw = json.loads(str(host.settings.value(POSITIONS_KEY, "{}")))
        if not isinstance(raw, dict):
            return {}
        result = {}
        for key, value in list(raw.items())[:64]:
            if not isinstance(key, str) or len(key) > 96 or not isinstance(value, dict):
                continue
            x, y = float(value.get("x")), float(value.get("y"))
            position = str(value.get("position"))
            if math.isfinite(x) and math.isfinite(y) and .04 <= x <= .96 and .04 <= y <= .96 and position in POSITIONS:
                result[key] = {"x": x, "y": y, "position": position}
                if "scale" in value:
                    result[key]["scale"] = normalize_layout_scale(value["scale"])
        return result
    except (TypeError, ValueError):
        return {}


def cooling_slots(host):
    if layout_synchronized(host):
        return list(host.rgb_layout_slots)
    positions = read_positions(host)
    return [replace(slot, **positions[slot.slot_id or slot.position])
            if (slot.slot_id or slot.position) in positions else slot for slot in host.rgb_layout_slots]


def set_synchronized(host, enabled):
    # First opt-out is a snapshot. Re-enabling never erases independent edits.
    if not enabled and not read_positions(host):
        positions = {slot.slot_id or slot.position: {"x": slot.x, "y": slot.y, "position": slot.position, "scale": slot.scale}
                     for slot in host.rgb_layout_slots[:64]}
        host.settings.setValue(POSITIONS_KEY, json.dumps(positions))
    host.settings.setValue(SYNC_KEY, bool(enabled))


def move_cooling_slot(host, slot_id, x, y, position):
    if not math.isfinite(x) or not math.isfinite(y) or position not in POSITIONS:
        return
    if not any((slot.slot_id or slot.position) == slot_id for slot in host.rgb_layout_slots):
        return
    if layout_synchronized(host):
        host.move_rgb_layout_slot(slot_id, x, y, position)
        return
    positions = read_positions(host)
    positions[slot_id] = {**positions.get(slot_id, {}), "x": max(.04, min(.96, x)), "y": max(.04, min(.96, y)), "position": position}
    host.settings.setValue(POSITIONS_KEY, json.dumps(positions))
    host.settings.sync()
    host.refresh_rgb_layout_editor()


def resize_cooling_slot(host, slot_id, scale):
    slot = next((s for s in cooling_slots(host) if (s.slot_id or s.position) == slot_id), None)
    if slot is None:
        return
    if layout_synchronized(host):
        host.resize_rgb_layout_slot(slot_id, scale)
        return
    positions = read_positions(host)
    positions[slot_id] = {"x": slot.x, "y": slot.y, "position": slot.position, "scale": normalize_layout_scale(scale)}
    host.settings.setValue(POSITIONS_KEY, json.dumps(positions))
    host.settings.sync()
    host.refresh_rgb_layout_editor()
