#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared RGB animation timing targets.

The requested animation cadence is deliberately independent from the selected
effect speed and from the measured USB/controller commit cadence.  A Qt timer
uses integer milliseconds, so 16 ms is the nearest practical event interval;
the semantic target remains 60 Hz and elapsed-time based renderers preserve
the exact effect speed between ticks.
"""

RGB_TARGET_FPS = 60
RGB_TARGET_INTERVAL_MS = 16

