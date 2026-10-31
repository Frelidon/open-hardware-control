# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure, device-reported GPU power boundaries for the LACT UI."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PowerBounds:
    minimum: float
    factory: float
    maximum: float


def reported_power_bounds(stats: dict) -> PowerBounds | None:
    power = stats.get("power")
    if not isinstance(power, dict):
        return None
    values = (power.get("cap_min"), power.get("cap_default"), power.get("cap_max"))
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) for value in values):
        return None
    minimum, factory, maximum = map(float, values)
    if not 0 < minimum <= factory <= maximum:
        return None
    return PowerBounds(minimum, factory, maximum)


def power_cap_allowed(value: float, bounds: PowerBounds | None, *, unlocked: bool) -> bool:
    if bounds is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return (math.isfinite(value) and bounds.minimum <= value <= bounds.maximum
            and (unlocked or value <= bounds.factory))


def sustained_power_excess(average_watts: float | None, bounds: PowerBounds | None) -> bool:
    """Ignore short sensor spikes; caller requires ten consecutive samples."""
    return bool(bounds and isinstance(average_watts, (int, float))
                and not isinstance(average_watts, bool) and math.isfinite(average_watts)
                and average_watts > bounds.factory * 1.05)
