"""Check every preset's wrap in gallery, physical, worker and GPU renderers."""

from dataclasses import asdict, replace
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rgb_effects import BUILTIN_DESIGNS, render_effect
from modules.rgb_studio.v1_15.effect_sampling import motion_scale
from modules.rgb_studio.v1_15.gpu_strip_sampling import render_gpu_strip_frame
from modules.rgb_studio.v1_15.led_topology import render_physical_frame
from modules.rgb_studio.v1_15.render_plan import render as render_worker


PATH = dict(kind="line", start="left", end="right", units=1, clockwise=True)


def _frame(renderer, config, count, elapsed):
    if renderer == "gallery":
        return render_effect(config, count, elapsed)
    if renderer == "physical":
        colors = render_physical_frame(config, count, elapsed, PATH, "left-right")
    elif renderer == "worker":
        colors = render_worker(dict(schema=1, config=asdict(config), elapsed=elapsed,
                                    zones=["strip"], paths={"strip": PATH},
                                    direction="left-right"), count, [count])
    else:
        colors = render_gpu_strip_frame(config, count, elapsed, PATH)
    return [tuple(int(color[offset:offset + 2], 16) for offset in (0, 2, 4)) for color in colors]


def _boundaries(effect, count, renderer):
    # These are the phase wraps promised by the algorithms, not a forced global
    # reset. Multiple spatial waves have independent wraps; sparkle changes
    # seeded buckets rather than repeating an entire animation.
    if effect == "static":
        return [1., 100.]
    if effect in {"spinner", "comet"}:
        rate = .24 if effect == "spinner" else .18
        scale = 1. if renderer == "gpu" else motion_scale(count)
        return [cycle / (rate * scale) for cycle in (1, 2, 5)]
    rates = {"code_rain": (1/12.,), "breathing": (1.,), "rainbow": (.16,), "wave": (.30,),
             "pulse": (.44,), "alternating": (1.,), "sparkle": (8.,),
             "converge": (.22,), "crossflow": (.16, .13), "depthwave": (.12, .20)}
    return [cycle / rate for rate in rates[effect] for cycle in (1, 2, 5)]


@pytest.mark.parametrize("renderer", ["gallery", "physical", "worker", "gpu"])
@pytest.mark.parametrize("title,config", BUILTIN_DESIGNS, ids=[name for name, _ in BUILTIN_DESIGNS])
def test_all_presets_have_continuous_cycle_boundaries(renderer, title, config):
    for count in (1, 8, 30, 114):
        for direction in (-1, 1):
            cfg = replace(config, direction=direction)
            if cfg.effect_id == "lightning":
                # Deliberate random lightning flashes have no repeated cycle.
                # Retain the flash character; it must still be deterministic.
                assert _frame(renderer, cfg, count, 1.234) == _frame(renderer, cfg, count, 1.234)
                continue
            for phase in _boundaries(cfg.effect_id, count, renderer):
                boundary = phase * 100. / cfg.speed
                before = _frame(renderer, cfg, count, boundary - 1e-6)
                after = _frame(renderer, cfg, count, boundary + 1e-6)
                delta = max(abs(a - b) for left, right in zip(before, after) for a, b in zip(left, right))
                assert delta <= 2, (title, renderer, count, direction, boundary, delta)


@pytest.mark.parametrize("renderer", ["gallery", "physical", "worker", "gpu"])
def test_corrected_pulses_and_convergence_do_not_hide_a_jump_just_before_wrap(renderer):
    for title, config in BUILTIN_DESIGNS:
        if config.effect_id not in {"pulse", "converge"}:
            continue
        for speed in (10, 100, 200):
            cfg = replace(config, speed=speed, primary="ff0000", secondary="00ffff")
            period = 100. / (speed * (.44 if cfg.effect_id == "pulse" else .22))
            # Sample the whole final overlap and the next cycle, rather than
            # merely making the last and first frames equal.
            times = [period * (.74 + step / 1000.) for step in range(521)]
            previous = _frame(renderer, cfg, 30, times[0])
            for elapsed in times[1:]:
                frame = _frame(renderer, cfg, 30, elapsed)
                delta = max(abs(a - b) for left, right in zip(previous, frame) for a, b in zip(left, right))
                assert delta <= 5, (title, renderer, speed, elapsed, delta)
                previous = frame
