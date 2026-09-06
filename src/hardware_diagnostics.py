#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure read-only plausibility checks for hardware telemetry."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ClockReading:
    source: str
    raw: int | None
    mhz: float | None
    issue: str = ""


@dataclass(frozen=True, slots=True)
class MetricIssue:
    metric: str
    value: object
    reason: str


def normalize_linux_clock(raw: object, *, maximum_mhz: float) -> tuple[float | None, str]:
    """Normalize a Linux clock that may be reported in Hz or MHz."""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None, "Wert ist keine Zahl"
    if not math.isfinite(value):
        return None, "Wert ist nicht endlich"
    if value <= 0:
        return None, "Wert ist nicht positiv"
    mhz = value / 1_000_000.0 if value >= 100_000.0 else value
    if not 0.1 <= mhz <= maximum_mhz:
        return None, f"normalisiert außerhalb 0,1–{maximum_mhz:g} MHz"
    return mhz, ""


def read_primary_amd_gpu_clock(
    drm_root: Path = Path("/sys/class/drm"),
) -> ClockReading:
    """Read the largest-VRAM AMD GPU clock without writing to sysfs."""
    cards: list[tuple[int, Path]] = []
    for card in sorted(drm_root.glob("card[0-9]*")):
        device = card / "device"
        try:
            if (device / "vendor").read_text(encoding="ascii").strip().casefold() != "0x1002":
                continue
            vram_path = device / "mem_info_vram_total"
            vram = int(vram_path.read_text(encoding="ascii").strip()) if vram_path.exists() else 0
            cards.append((vram, device))
        except (OSError, ValueError):
            continue
    for _vram, device in sorted(cards, key=lambda item: item[0], reverse=True):
        for hwmon in sorted((device / "hwmon").glob("hwmon*")):
            source = hwmon / "freq1_input"
            try:
                raw = int(source.read_text(encoding="ascii").strip())
            except (OSError, ValueError):
                continue
            mhz, issue = normalize_linux_clock(raw, maximum_mhz=5_000.0)
            # TRCC Linux 9.9.11 uses > 1_000_000 for its Hz decision.  At the
            # exact idle boundary it therefore renders 1,000,000 MHz.
            if 100_000 <= raw <= 1_000_000 and not issue:
                issue = (
                    f"TRCC-9.9.11-Grenzfall: {raw} Hz wird dort als MHz behandelt; "
                    f"OHC normalisiert den Wert zu {mhz:g} MHz"
                )
            return ClockReading(str(source), raw, mhz, issue)
    return ClockReading("amdgpu/freq1_input", None, None, "keine lesbare AMD-GPU-Taktquelle")


def validate_metric_snapshot(values: Mapping[str, object]) -> tuple[MetricIssue, ...]:
    """Return only malformed or physically implausible common metrics."""
    bounds = {
        "cpuClock": (50.0, 10_000.0, "MHz"),
        "gpuClock": (0.1, 5_000.0, "MHz"),
        "cpuLoad": (0.0, 100.0, "%"),
        "gpuLoad": (0.0, 100.0, "%"),
        "ramLoad": (0.0, 100.0, "%"),
        "cpuTemp": (0.0, 125.0, "°C"),
        "gpuTemp": (0.0, 130.0, "°C"),
    }
    issues: list[MetricIssue] = []
    for metric, (minimum, maximum, unit) in bounds.items():
        value = values.get(metric)
        if value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            issues.append(MetricIssue(metric, value, "keine numerische Angabe"))
            continue
        if not math.isfinite(number):
            issues.append(MetricIssue(metric, value, "NaN oder unendlich"))
        elif not minimum <= number <= maximum:
            issues.append(MetricIssue(
                metric, value,
                f"außerhalb des plausiblen Bereichs {minimum:g}–{maximum:g} {unit}",
            ))
    return tuple(issues)
