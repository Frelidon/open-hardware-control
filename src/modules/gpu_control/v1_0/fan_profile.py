# SPDX-License-Identifier: GPL-3.0-or-later
"""Validated five-point LACT GPU fan curves; no direct GPU writes."""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any


DEFAULT_TEMPERATURES = (40, 50, 60, 70, 80)
DEFAULT_SPEEDS = (35, 45, 60, 80, 100)


def fan_preview_verified(*, newly_enabled: bool, baseline_rpm: int,
                         peak_rpm: int, pwm_seen: bool) -> bool:
    """A newly claimed fan needs an observed spin-up, not only a LACT ACK."""
    if not pwm_seen:
        return False
    return not newly_enabled or peak_rpm >= max(100, baseline_rpm + 100)


def _range(stats: dict[str, Any]) -> tuple[int, int] | None:
    fan = stats.get("fan")
    reported = fan.get("temperature_range") if isinstance(fan, dict) else None
    if not isinstance(reported, list) or len(reported) != 2:
        return None
    lower, upper = reported
    if (not isinstance(lower, (int, float)) or isinstance(lower, bool)
            or not isinstance(upper, (int, float)) or isinstance(upper, bool)
            or not math.isfinite(lower) or not math.isfinite(upper)
            or not 0 <= lower < upper <= 125):
        return None
    return int(lower), int(upper)


def fan_curve_supported(stats: dict[str, Any]) -> bool:
    limits = _range(stats)
    fan = stats.get("fan")
    return bool(limits and limits[0] <= DEFAULT_TEMPERATURES[0]
                and limits[1] >= DEFAULT_TEMPERATURES[-1]
                and isinstance(fan, dict) and isinstance(fan.get("pwm_max"), (int, float))
                and fan["pwm_max"] > 0 and isinstance(stats.get("temps"), dict)
                and "edge" in stats["temps"])


def displayed_curve(config: dict[str, Any], stats: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    """Keep a previously saved five-point curve's temperature positions."""
    settings = config.get("fan_control_settings")
    curve = settings.get("curve") if isinstance(settings, dict) else None
    if isinstance(curve, dict) and len(curve) == 5:
        try:
            points = tuple(sorted((int(temp), round(float(speed) * 100))
                                  for temp, speed in curve.items()))
            validated_curve(points, stats)
            return points
        except (TypeError, ValueError):
            pass
    return tuple(zip(DEFAULT_TEMPERATURES, DEFAULT_SPEEDS))


def validated_curve(points: tuple[tuple[int, int], ...], stats: dict[str, Any]) -> dict[str, float]:
    """Conservative monotone curve within LACT-reported temperatures."""
    limits = _range(stats)
    if not fan_curve_supported(stats) or limits is None or len(points) != 5:
        raise ValueError("LACT did not report a compatible GPU fan curve")
    result: dict[str, float] = {}
    last_temp, last_speed = -1, -1
    for temp, speed in points:
        if (not isinstance(temp, int) or isinstance(temp, bool)
                or not isinstance(speed, int) or isinstance(speed, bool)
                or not limits[0] <= temp <= limits[1]
                or temp <= last_temp or not 35 <= speed <= 100 or speed < last_speed):
            raise ValueError("GPU fan curve must rise within the reported device range")
        result[str(temp)] = speed / 100.0
        last_temp, last_speed = temp, speed
    if last_speed < 90 or last_temp > 90:
        raise ValueError("GPU fan curve must reach at least 90% by 90°C")
    return result


def proposed_fan_settings(config: dict[str, Any], points: tuple[tuple[int, int], ...],
                          stats: dict[str, Any]) -> dict[str, Any]:
    curve = validated_curve(points, stats)
    previous = config.get("fan_control_settings")
    result = deepcopy(previous) if isinstance(previous, dict) else {}
    result.update({"mode": "curve", "curve": curve, "temperature_key": "edge",
                   "interval_ms": 500})
    result.setdefault("static_speed", 1.0)
    return result


def proposed_static_fan_settings(config: dict[str, Any], speed: int,
                                 stats: dict[str, Any]) -> dict[str, Any]:
    """Build a LACT static profile from a reported controllable fan."""
    if not fan_curve_supported(stats) or not isinstance(speed, int) or isinstance(speed, bool) or not 35 <= speed <= 100:
        raise ValueError("LACT did not report a compatible static GPU fan setting")
    previous = config.get("fan_control_settings")
    result = deepcopy(previous) if isinstance(previous, dict) else {}
    result.update({"mode": "static", "static_speed": speed / 100.0,
                   "temperature_key": "edge", "interval_ms": 500})
    result.setdefault("curve", validated_curve(tuple(zip(DEFAULT_TEMPERATURES, DEFAULT_SPEEDS)), stats))
    return result
