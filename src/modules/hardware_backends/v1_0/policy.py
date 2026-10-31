#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure, fail-closed policy for user-selectable hardware backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


DISPLAY_BACKENDS = ("trcc_linux",)
FAN_BACKENDS = ("ohc_hwmon",)


@dataclass(frozen=True, slots=True)
class BackendResolution:
    requested: str
    active: str | None
    available: bool
    automatic: bool


def normalize_backend_choice(value: object, supported: Sequence[str]) -> str:
    """Return a persisted choice or the safe automatic default."""

    choice = str(value or "auto").strip().casefold()
    return choice if choice == "auto" or choice in supported else "auto"


def resolve_backend(
    requested: object,
    supported: Sequence[str],
    availability: Mapping[str, bool],
) -> BackendResolution:
    """Resolve one backend without silently replacing an explicit choice."""

    choice = normalize_backend_choice(requested, supported)
    if choice != "auto":
        ready = bool(availability.get(choice, False))
        return BackendResolution(choice, choice if ready else None, ready, False)
    for backend in supported:
        if availability.get(backend, False):
            return BackendResolution("auto", backend, True, True)
    return BackendResolution("auto", None, False, True)
