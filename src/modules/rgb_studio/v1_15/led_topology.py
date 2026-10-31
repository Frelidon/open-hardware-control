# SPDX-License-Identifier: GPL-3.0-or-later
"""Declared physical LED paths and bounded case-space sampling, without I/O."""
import math
from dataclasses import replace
from rgb_effects import render_effect, rgb_to_hex

POINTS = {"left": (0., .5), "right": (1., .5), "top": (.5, 0.), "bottom": (.5, 1.),
          "top-left": (0., 0.), "top-right": (1., 0.), "bottom-left": (0., 1.), "bottom-right": (1., 1.)}
DIRECTIONS = {"left-right": (1, 0), "right-left": (-1, 0), "top-bottom": (0, 1), "bottom-top": (0, -1),
              "top-left-bottom-right": (1, 1), "bottom-right-top-left": (-1, -1),
              "top-right-bottom-left": (-1, 1), "bottom-left-top-right": (1, -1)}


def normalize_path(raw):
    if not isinstance(raw, dict) or not all(isinstance(raw.get(k), str) for k in ("kind", "start", "end")):
        return None
    if raw.get("kind") not in {"line", "ring"}:
        return None
    if raw.get("start") not in POINTS or raw.get("end") not in POINTS:
        return None
    if raw["kind"] == "line" and raw["start"] == raw["end"]: return None
    if type(raw.get("units")) is not int or not 1 <= raw["units"] <= 64: return None
    if type(raw.get("clockwise")) is not bool: return None
    if type(raw.get("reverse_units", False)) is not bool: return None
    if type(raw.get("reverse_effect", False)) is not bool: return None
    if "direction" in raw and raw.get("direction") not in {"local", *DIRECTIONS}: return None
    result = {k: raw[k] for k in ("kind", "start", "end", "units", "clockwise")}
    if raw.get("reverse_units", False): result["reverse_units"] = True
    if raw.get("reverse_effect", False): result["reverse_effect"] = True
    if "direction" in raw: result["direction"] = raw["direction"]
    return result


def path_points(path, count, horizontal=True):
    """One point for each physical 1-based LED, not a colour-frame permutation."""
    path = normalize_path(path)
    if path is None or type(count) is not int or not 1 <= count <= 4096:
        raise ValueError("LED_PATH")
    start, end = POINTS[path["start"]], POINTS[path["end"]]
    if path["kind"] == "line":
        return [(start[0] + (end[0] - start[0]) * i / max(1, count - 1),
                 start[1] + (end[1] - start[1]) * i / max(1, count - 1)) for i in range(count)]
    units = path["units"]
    if count % units or units > count: raise ValueError("LED_RING_COUNT")
    per_unit = count // units
    angle = math.atan2(start[1] - .5, start[0] - .5)
    direction = 1 if path["clockwise"] else -1
    result = []
    for unit in range(units):
        physical_unit = units - 1 - unit if path.get("reverse_units", False) else unit
        for i in range(per_unit):
            theta = angle + direction * math.tau * i / per_unit
            x, y = .5 + .46 * math.cos(theta), .5 + .46 * math.sin(theta)
            result.append(((physical_unit + x) / units, y) if horizontal else (x, (physical_unit + y) / units))
    return result


def projected_coordinate(point, direction):
    dx, dy = DIRECTIONS[direction]
    x, y = point
    # Normalized full-case projection. Negative axes reverse the spatial origin.
    return ((x if dx > 0 else 1 - x) * abs(dx) + (y if dy > 0 else 1 - y) * abs(dy)) / (abs(dx) + abs(dy))


def render_physical_frame(config, count, elapsed, path, direction="local", rect=(0., 0., 1., 1.), horizontal=True):
    from rgb_effects import render_hex_frame
    if path is not None:
        direction = path.get("direction", direction)
    if path is None or direction == "local":
        colors = render_hex_frame(config, count, elapsed)
        return colors[::-1] if path and path.get("reverse_effect", False) else colors
    if direction not in DIRECTIONS: raise ValueError("LED_DIRECTION")
    points = path_points(path, count, horizontal)
    if config.effect_id == "rainbow":
        # Rainbow's positive phase travels backwards; wave already travels
        # forwards. Spatial directions describe visible travel, not phase.
        config = replace(config, direction=-config.direction)
    frame = render_effect(config, count, elapsed)
    x, y, w, h = rect
    colors = []
    for px, py in points:
        fraction = projected_coordinate((x + px * w, y + py * h), direction)
        if path.get("reverse_effect", False):
            fraction = 1. - fraction
        sample = max(0., min(count - 1., fraction * (count - 1)))
        low = math.floor(sample); high = min(count - 1, low + 1)
        amount = sample - low
        colors.append(rgb_to_hex(tuple(round(a + (b - a) * amount) for a, b in zip(frame[low], frame[high]))))
    return colors
