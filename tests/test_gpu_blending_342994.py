"""Softer GPU colour gradients and paired 30/24 or 30/12 output, no hardware."""
import copy
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from rgb_effects import RGBEffectConfig, hex_to_rgb, render_hex_frame
from test_gpu_strip_smoothing_342989 import sync_host, MSI, HUB
from modules.rgb_studio.v1_15.gpu_strip_sampling import render_gpu_strip_frame, strip_plan, strip_clock
from modules.rgb_studio.v1_15.gpu_lighting import GpuLightingMixin
from modules.rgb_studio.v1_15.gpu_support_sync import pair
from modules.rgb_studio.v1_15.render_plan import build, render
from modules.rgb_studio.v1_15.gpu_motion import DEFAULT, load as load_motion


def test_gpu_peak_limits_saturated_white_and_support_keeps_original_brightness():
    config = RGBEffectConfig('spinner', '0000ff', 'ffffff', speed=100)
    clock = strip_clock(config, 30)
    elapsed = (clock['padding'] + .5) / clock['rate']
    reduced = dict(DEFAULT, gpu_peak=45)
    full = dict(DEFAULT, gpu_peak=100)
    gpu_reduced = [hex_to_rgb(color) for color in render_gpu_strip_frame(
        config, 30, elapsed, sync_count=30, tuning=reduced)]
    gpu_full = [hex_to_rgb(color) for color in render_gpu_strip_frame(
        config, 30, elapsed, sync_count=30, tuning=full)]
    assert max(color[0] for color in gpu_reduced) < max(color[0] for color in gpu_full)
    support_reduced = render_gpu_strip_frame(config, 12, elapsed, sync_count=30,
                                             tuning=reduced, role='support')
    support_full = render_gpu_strip_frame(config, 12, elapsed, sync_count=30,
                                          tuning=full, role='support')
    assert support_reduced == support_full


@pytest.mark.parametrize('effect', ['spinner', 'comet'])
@pytest.mark.parametrize('speed', [83, 110, 200])
def test_gpu_head_has_a_wide_soft_gradient_and_small_frame_steps(effect, speed):
    config = RGBEffectConfig(effect, '000000', 'ffffff', speed=speed)
    clock = strip_clock(config, 30)
    center = (clock['padding'] + .6) / clock['rate']
    frame = [hex_to_rgb(c)[0] for c in render_gpu_strip_frame(config, 30, center)]
    assert max(abs(a - b) for a, b in zip(frame, frame[1:])) <= 72
    assert sum(c > 102 for c in frame) >= 9, 'The colour fade collapses into isolated bright LEDs'
    frames = [[hex_to_rgb(c)[0] for c in render_gpu_strip_frame(config, 30, center + n / 25)]
              for n in range(-25, 26)]
    step = max(abs(a - b) for first, second in zip(frames, frames[1:])
               for a, b in zip(first, second))
    gallery_frames = [[hex_to_rgb(c)[0] for c in render_hex_frame(config, 30, center + n / 25)]
                      for n in range(-25, 26)]
    gallery_step = max(abs(a - b) for first, second in zip(gallery_frames, gallery_frames[1:])
                       for a, b in zip(first, second))
    assert step <= 36
    assert step < gallery_step


def centroid(colors):
    weights = [max(0, sum(hex_to_rgb(c)) - 30) for c in colors]
    return sum(i / (len(weights) - 1) * value for i, value in enumerate(weights)) / sum(weights)


@pytest.mark.parametrize('support_count', [12, 24])
@pytest.mark.parametrize('effect', ['spinner', 'comet'])
def test_paired_strips_share_colour_field_clock_and_worker_result(support_count, effect):
    host = sync_host()
    config = RGBEffectConfig(effect, '000000', 'ffffff', speed=110)
    host.rgb_group_effect_configs['gpu'] = config
    host.rgb_zone_configurations['openrgb:hub']['Channel B6']['leds_per_unit'] = support_count
    before = copy.deepcopy((host.settings.data, host.rgb_zone_configurations,
                            host.rgb_selected_devices, host.mainboard_layout_assignments))
    linked = pair(host, config)
    assert linked['count'] == 30
    clock = strip_clock(config, 30, load_motion(host))
    for position in (.3, .5, .7):
        elapsed = (clock['padding'] + position) / clock['rate']
        gpu = GpuLightingMixin.render_gpu_controller_frame(host, 'openrgb:msi', MSI, config, 46, [30, 8, 8], elapsed)
        support = GpuLightingMixin.render_gpu_controller_frame(host, 'openrgb:hub', HUB, config,
                                                               16 + support_count, [16, support_count], elapsed)
        assert len(gpu) == 46 and len(support) == 16 + support_count
        assert abs(centroid(gpu[:30]) - centroid(support[16:])) <= .025
        gpu_head = max(range(30), key=lambda index: sum(hex_to_rgb(gpu[index]))) / 29
        support_head = max(range(support_count), key=lambda index: sum(hex_to_rgb(support[16 + index]))) / (support_count - 1)
        assert abs(gpu_head - support_head) <= .1
        assert gpu[30:] == render_hex_frame(config, 8, elapsed) * 2
        assert support[:16] == render_hex_frame(config, 16, elapsed)
        for stable, source, count, sizes, expected in (
            ('openrgb:msi', MSI, 46, [30, 8, 8], gpu),
            ('openrgb:hub', HUB, 16 + support_count, [16, support_count], support)):
            payload = build(host, stable, source, config, elapsed)
            assert render(payload, count, sizes) == expected
    assert (host.settings.data, host.rgb_zone_configurations, host.rgb_selected_devices,
            host.mainboard_layout_assignments) == before
    host.close()
