#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure persisted-setting policy for the Thermalright Levita 1.4 runtime."""

from __future__ import annotations


def safe_split_mode(value: object) -> int:
    """Return a bounded preview mode; malformed and missing values mean Off."""

    try:
        parsed = int(value) if value is not None else 0
    except (TypeError, ValueError):
        return 0
    return max(0, min(3, parsed))
