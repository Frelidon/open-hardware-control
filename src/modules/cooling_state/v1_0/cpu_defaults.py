# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure policy for CPU-detected default curves versus user overrides."""

from __future__ import annotations


AUTO_ORIGIN = "auto"
USER_ORIGIN = "user"


def normalized_points(points: object) -> tuple[tuple[int, int], ...]:
    try:
        return tuple((int(point[0]), int(point[1])) for point in points)  # type: ignore[index, union-attr]
    except (TypeError, ValueError, IndexError):
        return ()


def infer_origin(saved_origin: object, current_pump: object, current_fan: object,
                 profile_pump: object, profile_fan: object) -> str:
    """Migrate older settings without overwriting an existing custom curve."""

    origin = str(saved_origin or "").strip().casefold()
    if origin in {AUTO_ORIGIN, USER_ORIGIN}:
        return origin
    if (normalized_points(current_pump) == normalized_points(profile_pump)
            and normalized_points(current_fan) == normalized_points(profile_fan)):
        return AUTO_ORIGIN
    return USER_ORIGIN


def should_load_detected_defaults(enabled: bool, origin: object) -> bool:
    return bool(enabled and str(origin or "").strip().casefold() == AUTO_ORIGIN)
