"""Count-adaptive motion stays bounded, continuous and independent per zone."""

import subprocess
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rgb_effects import EFFECTS, RGBEffectConfig, render_effect, render_hex_frame
from modules.rgb_studio.v1_15.effect_sampling import sampling_plan, motion_scale
from modules.rgb_studio.v1_15.gpu_routing import render_zone_frame


@pytest.mark.parametrize("count", [1,2,8,30,80,240,512,4096])
def test_all_effects_preserve_exact_count_determinism_bounds_and_brightness(count):
    for effect in EFFECTS:
        config = RGBEffectConfig(effect.effect_id, "7a28ff", "00f0ff", speed=110)
        frame = render_effect(config, count, 1.31)
        assert len(frame) == count and frame == render_effect(config, count, 1.31)
        assert all(0 <= channel <= 255 for color in frame for channel in color)
        dark = RGBEffectConfig(effect.effect_id, brightness=0)
        assert render_effect(dark, count, 1.31) == [(0,0,0)] * count
    assert sampling_plan(count) * count <= max(1024, count)


@pytest.mark.parametrize("effect_id", ["spinner", "comet"])
def test_30_led_motion_has_no_hard_pixel_head_jump_at_25_hz_or_cycle_wrap(effect_id):
    config = RGBEffectConfig(effect_id, "000000", "ffffff", speed=110)
    frames = [render_effect(config, 30, n / 25) for n in range(130)]
    largest_jump = max(abs(a-b) for first, second in zip(frames,frames[1:])
                       for left,right in zip(first,second) for a,b in zip(left,right))
    assert largest_jump < 85
    assert any(0 < color[0] < 255 for frame in frames for color in frame)
    assert motion_scale(8) < motion_scale(30) == 1


def test_all_configured_zones_use_own_coordinates_even_without_a_gpu_override():
    config = RGBEffectConfig("spinner", "7a28ff", "00f0ff")
    actual = render_zone_frame(config, 118, (0,30,8,80), ("JAF","JARGB 1","JARGB 2","JARGB 3"), {}, .51)
    assert actual == (render_hex_frame(config,30,.51) + render_hex_frame(config,8,.51) + render_hex_frame(config,80,.51))
    with pytest.raises(ValueError): render_zone_frame(config,119,(0,30,8,80),("a","b","c","d"),{},.51)


def test_spatial_convergence_moves_both_sides_into_the_case_centre():
    config = RGBEffectConfig("converge", "000000", "ffffff", speed=100)
    start = render_effect(config, 31, 0.0)
    meeting = render_effect(config, 31, 3.55)
    brightness = lambda color: sum(color)
    assert brightness(start[0]) > brightness(start[15])
    assert brightness(start[-1]) > brightness(start[15])
    assert brightness(meeting[15]) > brightness(meeting[0])
    assert brightness(meeting[15]) > brightness(meeting[-1])


def test_pure_renderer_import_does_not_load_qt_or_depend_on_import_order():
    result = subprocess.run([sys.executable, "-c",
        "import sys;sys.path.insert(0,'src');import rgb_effects;assert 'PySide6' not in sys.modules;assert len(rgb_effects.render_hex_frame(rgb_effects.RGBEffectConfig('spinner'),30,1))==30"],
        cwd=ROOT, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
