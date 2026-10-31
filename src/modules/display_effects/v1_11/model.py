#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validated serializable settings for procedural display effects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json


DIRECTIONS = ("right", "left", "up", "down")


def _bounded(value: object, minimum: int, maximum: int, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = fallback
    return max(minimum, min(maximum, parsed))


def _color(value: object, fallback: str) -> str:
    candidate = str(value or "").strip().upper()
    if len(candidate) == 7 and candidate.startswith("#"):
        try:
            int(candidate[1:], 16)
        except ValueError:
            pass
        else:
            return candidate
    return fallback


@dataclass(frozen=True)
class SmokeSettings:
    """One bounded smoke configuration shared by UI, preview and exporter."""

    primary_color: str = "#FF6A00"
    secondary_color: str = "#F5F7FA"
    sharpness: int = 93
    density: int = 65
    speed: int = 40
    turbulence: int = 58
    glow: int = 55
    direction: str = "right"

    @classmethod
    def from_mapping(cls, values: dict[str, object] | None) -> "SmokeSettings":
        raw = values or {}
        direction = str(raw.get("direction", "right"))
        return cls(
            primary_color=_color(raw.get("primary_color"), "#FF6A00"),
            secondary_color=_color(raw.get("secondary_color"), "#F5F7FA"),
            sharpness=_bounded(raw.get("sharpness"), 50, 100, 93),
            density=_bounded(raw.get("density"), 20, 100, 65),
            speed=_bounded(raw.get("speed"), 10, 100, 40),
            turbulence=_bounded(raw.get("turbulence"), 0, 100, 58),
            glow=_bounded(raw.get("glow"), 0, 100, 55),
            direction=direction if direction in DIRECTIONS else "right",
        )

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def cache_key(self) -> str:
        payload = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


PRESETS: dict[str, SmokeSettings] = {
    "ember": SmokeSettings(),
    "ice": SmokeSettings("#23A8FF", "#EAF8FF", 95, 58, 34, 48, 62, "left"),
    "plasma": SmokeSettings("#B349FF", "#38E8FF", 91, 72, 52, 74, 68, "up"),
}
