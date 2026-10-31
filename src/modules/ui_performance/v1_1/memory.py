#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Return idle Python/Qt decoder allocations to the operating system."""

from __future__ import annotations

import ctypes
import gc
from typing import NamedTuple


class ReclaimResult(NamedTuple):
    collected: int
    heap_trimmed: bool


def release_idle_memory() -> ReclaimResult:
    """Collect cycles and ask glibc to release completely free heap pages.

    ``malloc_trim`` is optional.  Non-glibc systems simply keep their normal
    allocator behaviour, while decoder shutdown and Python collection still
    happen everywhere.
    """

    collected = gc.collect()
    trimmed = False
    try:
        process = ctypes.CDLL(None)
        malloc_trim = process.malloc_trim
        malloc_trim.argtypes = [ctypes.c_size_t]
        malloc_trim.restype = ctypes.c_int
        trimmed = bool(malloc_trim(0))
    except (AttributeError, OSError):
        pass
    return ReclaimResult(collected, trimmed)
