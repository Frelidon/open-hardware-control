# SPDX-License-Identifier: GPL-3.0-or-later
"""Continuous open-strip light heads for explicitly routed GPU headers; no I/O."""
import math
from dataclasses import replace
from rgb_effects import hex_to_rgb, rgb_to_hex, render_effect
from .effect_sampling import motion_scale
from .led_topology import DIRECTIONS, path_points, render_physical_frame, projected_coordinate

TARGET_HZ = 25
TEMPORAL_SAMPLES = 3
SPATIAL_SAMPLES = 4
CLOCK_PADDING = .5  # Supports every bounded per-strip edge without wrap leakage.


def strip_plan(config, count, tuning=None, role="gpu"):
    if type(count) is not int or not 1 <= count <= 4096: raise ValueError("GPU_STRIP_COUNT")
    cfg = config.normalized()
    scale = min(motion_scale(count) * .5, 12. / count)
    rate = (.18 if cfg.effect_id == "comet" else .24) * cfg.speed / 100. * scale
    # The 30-LED Sapphire strip is a long line, unlike the surrounding fan
    # rings. Keep its white highlight compact so the blue body stays visible.
    # A wider, low-intensity approach illuminates the next physical pixels
    # before the bright core reaches them. Keep the same progress for a paired
    # support strip, even when its physical LED count differs.
    leading = min(.32, max(.18, 9.6 / count))
    tail = min(.40, max(.38 if cfg.effect_id == "comet" else .36, 6.5 / count))
    if tuning is not None:
        from .gpu_motion import normalize
        values = normalize(tuning)
        if role not in {"gpu", "support"}: raise ValueError("GPU_STRIP_ROLE")
        leading = values[f"{role}_lead"] / 100.
        tail = values[f"{role}_tail"] / 100.
        rate *= values["tempo"] / 100.
    else:
        from .gpu_motion import DEFAULT
        values = DEFAULT
    return dict(rate=rate, leading=leading, tail=tail, cycle=1. + tail + leading,
                peak=values["gpu_peak"] / 100. if role == "gpu" else 1.,
                motion_scale=scale, leds_per_second=rate * count)


def strip_clock(config, count, tuning=None):
    """One traversal for both strips, independent of their different light envelopes."""
    rate = strip_plan(config, count, tuning, "gpu")["rate"]
    return dict(rate=rate, padding=CLOCK_PADDING, cycle=1. + 2. * CLOCK_PADDING)


def _strength(distance, leading, tail):
    # Signed distance, never modular LED distance: strip ends are not adjacent.
    width = leading if distance < 0 else tail
    fraction = max(0., 1. - abs(distance) / width)
    # Cubic smoothstep keeps zero slope at both ends while showing more of the
    # dim approach and afterglow than the old quintic curve. This reduces the
    # visible brightness jump as the head crosses each physical LED.
    return fraction * fraction * (3. - 2. * fraction)


def render_gpu_strip_frame(config, count, elapsed, path=None, direction="local",
                           rect=(0., 0., 1., 1.), horizontal=True, sync_count=None,
                           tuning=None, role="gpu"):
    """Keep ring/non-moving effects unchanged; sample an open strip analytically."""
    if path is not None:
        direction = path.get("direction", direction)
    if (config.effect_id not in {"spinner", "comet"} and sync_count is None
            or path and path.get("kind") == "ring"):
        return render_physical_frame(config, count, elapsed, path, direction, rect, horizontal)
    strip_plan(config, count)  # Validate real per-header count independently.
    reference_count = sync_count if sync_count is not None else count
    plan = strip_plan(config, reference_count, tuning, role)
    # Edge widths may differ, but the moving head must never acquire a second
    # phase or cycle when the support uses its own softer/shorter light shape.
    clock = strip_clock(config, reference_count, tuning)
    cfg = config.normalized()
    elapsed = float(elapsed)
    if not math.isfinite(elapsed): raise ValueError("GPU_STRIP_TIME")
    if path is None or direction == "local":
        positions = [i / max(1, count - 1) for i in range(count)]
    else:
        if direction not in DIRECTIONS: raise ValueError("LED_DIRECTION")
        x, y, w, h = rect
        positions = [projected_coordinate((x + px * w, y + py * h), direction)
                     for px, py in path_points(path, count, horizontal)]
    if path and path.get("reverse_effect", False):
        positions = [1. - position for position in positions]
    if sync_count is not None and positions:
        # Paired strips share progress, not their different case-space offsets.
        low, high = min(positions), max(positions)
        positions = [(p - low) / (high - low) for p in positions] if high > low else [
            i / max(1, count - 1) for i in range(count)]
    if cfg.effect_id not in {"spinner", "comet"}:
        if direction != "local" and cfg.effect_id == "rainbow":
            cfg = replace(cfg, direction=-cfg.direction)
        frame = render_effect(cfg, sync_count, elapsed)
        colors = []
        for p in positions:
            index = max(0., min(sync_count - 1., p * (sync_count - 1)))
            low = math.floor(index); high = min(sync_count - 1, low + 1)
            colors.append(rgb_to_hex(tuple(round(a + (b - a) * (index - low))
                                           for a, b in zip(frame[low], frame[high]))))
        return colors
    if cfg.direction < 0: positions = [1. - p for p in positions]
    footprint = 1. / (sync_count if sync_count is not None else count)
    primary, secondary = hex_to_rgb(cfg.primary), hex_to_rgb(cfg.secondary)
    comet = cfg.effect_id == "comet"
    base = .15 if comet else .22
    floor = .02 if comet else .04
    times = [max(0., elapsed - (1. - (i + .5) / TEMPORAL_SAMPLES) / TARGET_HZ)
             for i in range(TEMPORAL_SAMPLES)]
    heads = [-clock["padding"] + (t * clock["rate"]) % clock["cycle"] for t in times]
    colors = []
    for position in positions:
        # Edge coverage is clipped: a light exiting LED N must not illuminate 1.
        strengths = [_strength(head - max(0., min(1., position + ((s + .5) / SPATIAL_SAMPLES - .5) * footprint)),
                               plan["leading"], plan["tail"])
                     for head in heads for s in range(SPATIAL_SAMPLES)]
        amount = max(floor, sum(strengths) / len(strengths))
        if role == "gpu":
            # The GPU diffuser/white LEDs saturate earlier than the support.
            # Raise the dim edge above its barely visible 8-bit values, while
            # limiting the white peak so the physical fade stays discernible.
            amount = floor + (1. - floor) * max(0., (amount - floor) / (1. - floor)) ** .65
        colors.append(rgb_to_hex(tuple(round((a * base + (b * plan["peak"] - a * base) * amount) * cfg.brightness / 100.)
                                       for a, b in zip(primary, secondary))))
    return colors
