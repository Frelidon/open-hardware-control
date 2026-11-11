# SPDX-License-Identifier: GPL-3.0-or-later
"""Original smooth data trails for low-resolution LED rings and strips."""
from __future__ import annotations

import math

PERIOD_SECONDS = 12.0


def rain_pixel(position: float, phase: float, primary, secondary, seed: int):
    """Periodic green trails, with continuous heads/tails even at the wrap.

    Phase is the shared RGB engine's speed/direction-adjusted elapsed time.
    A von Mises head and wrapped Gaussian tails avoid per-frame random buckets
    and the discontinuity of a truncated exponential at the ring seam.
    """
    energy = peak = 0.0
    offset = (seed % 997) / 997.0
    for stream, cycles in enumerate((2, 3, 4)):
        head = phase / PERIOD_SECONDS * cycles + offset + stream * .371
        for tail in range(6):
            distance = position - head + tail * .038
            body = math.exp(31.0 * (math.cos(math.tau * distance) - 1.0))
            energy += body * math.exp(-tail * .62) * (.58 - stream * .10)
        tip = math.exp(180.0 * (math.cos(math.tau * (position - head)) - 1.0))
        peak = max(peak, tip * (.74 - stream * .13))
    energy = min(1.0, .015 + energy)
    shimmer = .91 + .09 * math.cos(math.tau * (phase / PERIOD_SECONDS * 5 + position * 7))
    return tuple(round(max(0.0, min(255.0,
        (base * energy * (1 - peak) + bright * peak) * shimmer)))
        for base, bright in zip(primary, secondary))
