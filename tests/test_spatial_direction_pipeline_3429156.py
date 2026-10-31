"""Saved motion intent reaches pure frames without changing wiring or transport."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rgb_effects import EFFECTS, RGBEffectConfig, hex_to_rgb, render_hex_frame
from modules.rgb_studio.v1_15 import render_plan
from modules.rgb_studio.v1_15.gpu_strip_sampling import render_gpu_strip_frame
from modules.rgb_studio.v1_15.led_topology import path_points, render_physical_frame
from modules.rgb_studio.v1_15.led_topology_store import DIRECTION_KEY, KEY
from openrgb_sdk import process_worker_frame

PATH = dict(kind="line", start="left", end="right", units=1, clockwise=True)
AXES = {
    "left-right": ("left", "right"), "right-left": ("right", "left"),
    "top-bottom": ("top", "bottom"), "bottom-top": ("bottom", "top"),
    "top-left-bottom-right": ("top-left", "bottom-right"),
    "bottom-right-top-left": ("bottom-right", "top-left"),
    "top-right-bottom-left": ("top-right", "bottom-left"),
    "bottom-left-top-right": ("bottom-left", "top-right"),
}


class Settings:
    def __init__(self, values):
        self.values = values

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, *_args):
        raise AssertionError("Rendering must not change settings")

    def sync(self):
        raise AssertionError("Rendering must not change settings")


def host_with_paths(declared, movement="local", ubuntu=False):
    settings = Settings({KEY: json.dumps({"openrgb:hub": declared}), DIRECTION_KEY: movement})
    return SimpleNamespace(settings=settings, openrgb_devices=[], rgb_selected_devices=set(),
                           rgb_layout_slots=[], _ubuntu_runtime=ubuntu)


@pytest.mark.parametrize("movement", AXES)
@pytest.mark.parametrize("effect_direction", [1, -1])
@pytest.mark.parametrize("paired", [False, True])
@pytest.mark.parametrize("effect", ["wave", "rainbow"])
def test_wave_and_rainbow_move_temporally_in_declared_axis_and_compose_effect_direction(
        movement, effect_direction, paired, effect):
    start, end = AXES[movement]
    path = {**PATH, "start": start, "end": end, "direction": movement}
    config = RGBEffectConfig(effect, "000000", "ffffff", direction=effect_direction)
    render = render_gpu_strip_frame if paired else render_physical_frame
    extra = {"sync_count": 101} if paired else {}
    peaks = []
    for elapsed in (.1, .5):
        frame = render(config, 101, elapsed, path, **extra)
        if effect == "wave":
            peaks.append(max(range(1, 48), key=lambda index: sum(hex_to_rgb(frame[index]))))
        else:
            def red_peak(index):
                red, green, blue = hex_to_rgb(frame[index])
                return red - green - blue
            peaks.append(max(range(101), key=red_peak))
    assert (peaks[1] - peaks[0]) * effect_direction > 0


@pytest.mark.parametrize("effect", [item.effect_id for item in EFFECTS])
def test_unmapped_and_unchanged_local_paths_preserve_exact_legacy_frames(effect):
    config = RGBEffectConfig(effect, "002244", "ffffff", direction=-1)
    expected = render_hex_frame(config, 24, .83)
    for movement in ("local", *AXES):
        assert render_physical_frame(config, 24, .83, None, movement) == expected
    assert render_physical_frame(config, 24, .83, PATH) == expected
    path = {**PATH, "direction": "local", "reverse_effect": True}
    points = path_points(PATH, 24)
    assert path_points(path, 24) == points
    assert render_physical_frame(config, 24, .83, path, "left-right") == expected[::-1]


@pytest.mark.parametrize("effect", ["spinner", "comet", "wave", "rainbow"])
@pytest.mark.parametrize("effect_direction", [1, -1])
@pytest.mark.parametrize("paired", [False, True])
def test_local_gpu_motion_reverse_is_independent_of_effect_sign_pairing_and_led_order(
        effect, effect_direction, paired):
    config = RGBEffectConfig(effect, "002244", "ffffff", direction=effect_direction)
    path = {**PATH, "direction": "local"}
    reverse = {**path, "reverse_effect": True}
    extra = {"sync_count": 30} if paired else {}
    forward_frame = render_gpu_strip_frame(config, 30, 4.2, path, **extra)
    reverse_frame = render_gpu_strip_frame(config, 30, 4.2, reverse, **extra)
    assert reverse_frame == forward_frame[::-1]
    assert path_points(reverse, 30) == path_points(path, 30)


@pytest.mark.parametrize("ubuntu", [False, True], ids=["fedora", "ubuntu"])
def test_individual_spatial_header_uses_case_rectangle_in_worker_without_global_override(
        monkeypatch, ubuntu):
    declared = {"Strip": {**PATH, "direction": "left-right"},
                "Local": {**PATH, "direction": "local", "reverse_effect": True}}
    host = host_with_paths(declared, ubuntu=ubuntu)
    saved = deepcopy(host.settings.values)
    calls = []
    bounds = {"Strip": ((.1, .2, .3, .4), True),
              "Local": ((.7, .2, .2, .4), True)}
    monkeypatch.setattr(render_plan, "case_rectangles",
                        lambda owner, source: calls.append((owner, source)) or bounds)
    device = SimpleNamespace(zones=("Strip", "Local"), supports_direct=True)
    config = RGBEffectConfig("wave", "000000", "ffffff", direction=-1)
    raw = render_plan.build(host, "openrgb:hub", device, config, .53)
    assert raw["direction"] == "local" and raw["rectangles"] == bounds
    assert raw["paths"] == declared and calls == [(host, "openrgb:hub")]
    received = []

    def write_frame(index, count, colors, **kwargs):
        received.append((index, count, colors, kwargs))
        return {"ok": True}

    request = dict(id=7, devices=[dict(key="openrgb:hub", device=3, led_count=38,
                                     zone_sizes=[30, 8], render_plan=raw, prepare=False)])
    response = process_worker_frame(SimpleNamespace(write_frame=write_frame), request)
    expected = (render_physical_frame(config, 30, .53, declared["Strip"],
                                     rect=bounds["Strip"][0])
                + render_hex_frame(config, 8, .53)[::-1])
    assert response["ok"] and received[0][:3] == (3, 38, expected)
    assert host.settings.values == saved


@pytest.mark.parametrize("ubuntu", [False, True], ids=["fedora", "ubuntu"])
@pytest.mark.parametrize("declared", [{}, {"Strip": {**PATH, "direction": "local"}}])
def test_global_direction_never_creates_geometry_or_overrides_explicit_local_header(
        monkeypatch, ubuntu, declared):
    host = host_with_paths(declared, "left-right", ubuntu=ubuntu)
    monkeypatch.setattr(render_plan, "case_rectangles",
                        lambda *_args: pytest.fail("No spatial path may create inferred geometry"))
    config = RGBEffectConfig("wave", "002244", "ffffff", direction=-1)
    raw = render_plan.build(host, "openrgb:hub", SimpleNamespace(zones=("Strip",),
                                                               supports_direct=True), config, .83)
    assert raw["rectangles"] == {}
    assert render_plan.render(raw, 24, [24]) == render_hex_frame(config, 24, .83)


def test_header_specific_group_effect_keeps_its_sign_before_spatial_projection():
    base = RGBEffectConfig("static", "000000")
    group = RGBEffectConfig("wave", "000000", "ffffff", direction=-1)
    raw = dict(schema=1, config=asdict(base), elapsed=.5, zones=["Strip", "Other"],
               overrides={"Strip": asdict(group)}, paths={"Strip": {**PATH, "direction": "left-right"}},
               rectangles={}, gpu_zones=[], sync_counts={}, direction="right-left")
    assert render_plan.render(raw, 38, [30, 8]) == (
        render_physical_frame(group, 30, .5, raw["paths"]["Strip"])
        + render_hex_frame(base, 8, .5))


@pytest.mark.parametrize("ubuntu", [False, True], ids=["fedora", "ubuntu"])
def test_actual_legacy_mixin_frame_matches_worker_for_individual_spatial_header(monkeypatch, ubuntu):
    from modules.rgb_studio.v1_15.gpu_lighting import GpuLightingMixin
    from modules.rgb_studio.v1_15 import led_topology_store
    declared = {"Strip": {**PATH, "direction": "left-right"}}
    host = host_with_paths(declared, ubuntu=ubuntu)
    saved = deepcopy(host.settings.values)
    bounds = {"Strip": ((.1, .2, .3, .4), True)}
    monkeypatch.setattr(led_topology_store, "case_rectangles", lambda *_args: bounds)
    monkeypatch.setattr(render_plan, "case_rectangles", lambda *_args: bounds)
    device = SimpleNamespace(zones=("Strip",), supports_direct=True)
    config = RGBEffectConfig("wave", "000000", "ffffff")
    actual = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:hub", device,
                                                         config, 30, [30], .53)
    raw = render_plan.build(host, "openrgb:hub", device, config, .53)
    assert actual == render_plan.render(raw, 30, [30]) == render_physical_frame(
        config, 30, .53, declared["Strip"], rect=bounds["Strip"][0])
    assert host.settings.values == saved
