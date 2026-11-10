# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded GPU/support motion preferences and transport-paced display clock."""
import json
import math

KEY = "rgb_studio/gpu_motion_v1"
DEFAULT = {"gpu_lead": 40, "gpu_tail": 38, "gpu_peak": 65,
           "support_lead": 32, "support_tail": 36, "tempo": 100}
RANGES = {"gpu_lead": (18, 50), "gpu_tail": (20, 50),
          "gpu_peak": (35, 100),
          "support_lead": (18, 50), "support_tail": (20, 50),
          "tempo": (40, 140)}


def normalize(value):
    if not isinstance(value, dict):
        return dict(DEFAULT)
    result = {}
    for key, (minimum, maximum) in RANGES.items():
        entry = value.get(key, DEFAULT[key])
        if type(entry) is not int or not minimum <= entry <= maximum:
            return dict(DEFAULT)
        result[key] = entry
    return result


def load(host):
    settings = getattr(host, "settings", None)
    if settings is None:
        return dict(DEFAULT)
    try:
        return normalize(json.loads(str(settings.value(KEY, "{}"))))
    except (TypeError, ValueError):
        return dict(DEFAULT)


def save(host, value):
    result = normalize(value)
    if result != value:
        raise ValueError("GPU_MOTION_SETTINGS")
    host.settings.setValue(KEY, json.dumps(result, sort_keys=True))
    host.settings.sync()
    return result


def paced_elapsed(previous, wall_delta):
    """Advance by real monotonic time without dilating slow hardware batches."""
    if not all(type(v) in (int, float) and math.isfinite(v) for v in (previous, wall_delta)):
        raise ValueError("GPU_MOTION_CLOCK")
    if previous < 0 or wall_delta < 0:
        raise ValueError("GPU_MOTION_CLOCK")
    return previous + wall_delta


def configured_count(host, controller, zone):
    raw = getattr(host, "rgb_zone_configurations", {}).get(controller, {}).get(zone, {})
    units, leds = raw.get("units"), raw.get("leds_per_unit")
    if (type(units) is not int or type(leds) is not int or units < 1 or leds < 1
            or not 1 <= units * leds <= 512):
        return 0
    return units * leds


def support_count(host):
    from .slot_routes import slot_routes
    route = slot_routes(host).get("gpu-support", {})
    return configured_count(host, route.get("controller", ""), route.get("zone", ""))
