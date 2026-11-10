#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Original bounded pixel-area sampling and count-aware motion envelopes."""

import math


def sampling_plan(count):
    count = max(1, min(4096, int(count)))
    return 4 if count <= 128 else 2 if count <= 512 else 1


def averaged_pixel(index, count, sample):
    samples = sampling_plan(count)
    colors = [sample((index + (n + .5) / samples - .5) / count)
              for n in range(samples)]
    return tuple(round(sum(color[channel] for color in colors) / samples)
                 for channel in range(3))


def smooth_fraction(value):
    return value * value * (3.0 - 2.0 * value)


def motion_scale(count):
    """Small strips move more slowly; the fixed 60-Hz request target is unchanged."""
    return min(1.0, max(.25, count / 24.0))


def moving_head_strength(position, head, count, *, comet=False):
    """Soft leading edge and tail span multiple LEDs, including at strip wrap."""
    distance = (head - position) % 1.0
    tail = max(1 / (5.5 if comet else 7), min(.45, 3 / count))
    leading = max(1 / count, tail * .15)
    if distance > .5:
        boundary = math.exp(-.5 * (.5 / leading) ** 2)
        return max(0.0, (math.exp(-.5 * ((1 - distance) / leading) ** 2) - boundary) / (1 - boundary))
    strength = max(0.0, 1 - distance / tail)
    return strength ** 2 if comet else smooth_fraction(strength)
