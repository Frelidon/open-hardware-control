#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded session storage and absolute ranges for sampled temperatures."""

from __future__ import annotations

from dataclasses import dataclass
import math
import time
from typing import Mapping


@dataclass(frozen=True, slots=True)
class HistorySample:
    timestamp: float
    values: dict[str, float]


class TemperatureHistoryBuffer:
    """Keep validated temperatures in memory, never on disk."""

    def __init__(self, *, max_age_seconds: int = 86_400, max_samples: int = 28_800) -> None:
        self.max_age_seconds = max(60, int(max_age_seconds))
        self.max_samples = max(20, int(max_samples))
        self._samples: list[HistorySample] = []

    @property
    def samples(self) -> tuple[HistorySample, ...]:
        return tuple(self._samples)

    def append(self, values: Mapping[str, float | int | None], timestamp: float | None = None) -> bool:
        clean: dict[str, float] = {}
        for key, raw in values.items():
            if raw is None:
                continue
            try:
                value = float(raw)
            except (TypeError, ValueError):
                continue
            if math.isfinite(value) and -40.0 <= value <= 150.0:
                clean[str(key)] = value
        if not clean:
            return False
        now = float(time.time() if timestamp is None else timestamp)
        if not math.isfinite(now):
            return False
        self._samples.append(HistorySample(now, clean))
        cutoff = now - self.max_age_seconds
        self._samples = [sample for sample in self._samples[-self.max_samples :] if sample.timestamp >= cutoff]
        return True

    def window(self, seconds: int | None, now: float | None = None) -> tuple[HistorySample, ...]:
        if not self._samples or seconds is None:
            return self.samples
        end = self._samples[-1].timestamp if now is None else float(now)
        cutoff = end - max(1, int(seconds))
        return tuple(sample for sample in self._samples if sample.timestamp >= cutoff)

    def between(self, start: float, end: float) -> tuple[HistorySample, ...]:
        """Return an inclusive absolute local-report range without mutating history."""

        low, high = sorted((float(start), float(end)))
        return tuple(sample for sample in self._samples if low <= sample.timestamp <= high)

    def latest(self, key: str, seconds: int | None = None) -> HistorySample | None:
        return next(
            (sample for sample in reversed(self.window(seconds)) if key in sample.values),
            None,
        )

    def statistics(self, key: str, seconds: int | None = None) -> tuple[float, float, float] | None:
        values = [sample.values[key] for sample in self.window(seconds) if key in sample.values]
        if not values:
            return None
        return values[-1], min(values), max(values)
