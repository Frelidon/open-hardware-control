"""Reported fan RGB preview keeps shared phase and visibility, without I/O."""
import copy
import os
from dataclasses import replace
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OHC_DISABLE_HARDWARE_IO", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from openrgb_integration import OpenRGBDevice
from rgb_devices import RGBLayoutSlot
from rgb_effects import RGBEffectConfig, render_hex_frame
from modules.pc_case_profiles.v1_5.case_animation import build_specs, frame
from modules.pc_case_profiles.v1_5.diagram import PCLayoutDiagram
from modules.pc_case_profiles.v1_5.fan_preview import brighter_preview_color, ring_segments
from modules.rgb_studio.v1_15.led_topology import render_physical_frame
from modules.rgb_studio.v1_15.led_topology_store import case_rectangles
from modules.rgb_studio.v1_15.render_plan import build, render
from modules.rgb_studio.v1_15.slot_routes import KEY

APP = QApplication.instance() or QApplication([])
SOURCE = "openrgb:1111111111111111"
FAN = RGBLayoutSlot("front", "Front fans", 2, "case", "Channel A1", (SOURCE,),
                    "front-fans", .82, .45)
RING = dict(kind="ring", start="top", end="bottom", units=2, clockwise=True,
            reverse_units=True, reverse_effect=True, direction="local")
LINE = dict(RING, kind="line", start="left", end="right")


class Settings:
    def __init__(self):
        self.data = {}

    def value(self, key, default=None, **_kwargs):
        return self.data.get(key, default)

    def setValue(self, *_args):
        raise AssertionError("A preview must not persist settings")

    def sync(self):
        raise AssertionError("A preview must not persist settings")


@pytest.fixture(params=["ubuntu", "fedora"])
def host(request):
    """Same shared UI contract; this is not a live distribution/hardware test."""
    config = RGBEffectConfig("rainbow", speed=160)
    return SimpleNamespace(
        distribution_fixture=request.param, settings=Settings(),
        openrgb_devices=[OpenRGBDevice(1, "Airgoo", modes=("Direct",),
                                      zones=("Channel A1",), leds=tuple(str(n) for n in range(16)))],
        openrgb_stable_ids={1: SOURCE}, rgb_gpu_routes={},
        rgb_selected_devices={SOURCE}, rgb_group_assignments={},
        rgb_layout_slots=[FAN], rgb_zone_configurations={
            SOURCE: {"Channel A1": {"units": 2, "leds_per_unit": 8}}},
        openrgb_effect_assignments={SOURCE: config}, openrgb_effect_active=True,
        rgb_last_sent_elapsed=0., openrgb_device_conflict=lambda _device: False,
    )


def test_absent_physical_path_keeps_reported_schematic_fan_frame(host):
    before = copy.deepcopy(host.rgb_zone_configurations), copy.deepcopy(host.settings.data), FAN
    specs = build_specs(host, [FAN], {})
    assert specs["front-fans"]["path"] is None
    assert specs["front-fans"]["targets"] == ((SOURCE, "Channel A1", 16),)
    first = frame(host, specs["front-fans"])
    assert first == tuple(render_hex_frame(host.openrgb_effect_assignments[SOURCE], 16, 0.))
    host.rgb_last_sent_elapsed = .4
    second = frame(host, specs["front-fans"])
    assert len(first) == len(second) == 16 and first != second
    assert (host.rgb_zone_configurations, host.settings.data, FAN) == before
    # Without an active/assigned writer, the schematic does not invent output.
    host.openrgb_effect_assignments = {}
    assert frame(host, specs["front-fans"]) == ()
    host.openrgb_effect_active = False
    assert frame(host, specs["front-fans"]) == ()


@pytest.mark.parametrize("path", [LINE, RING])
def test_declared_row_ring_order_and_count_are_not_rewritten(host, path):
    saved = copy.deepcopy(path)
    specs = build_specs(host, [FAN], {"front-fans": (path, 16)})
    host.rgb_last_sent_elapsed = .3
    expected = render_physical_frame(host.openrgb_effect_assignments[SOURCE], 16, .3,
                                     path, "local", horizontal=False)
    assert frame(host, specs["front-fans"]) == tuple(expected)
    assert path == saved and specs["front-fans"]["path"] == (saved, 16)
    assert host.settings.data == {}


def test_no_guessed_port_no_count_no_absent_controller_preview(host):
    device = replace(host.openrgb_devices[0], zones=("Channel A1", "Channel A2"))
    host.openrgb_devices = [device]
    host.rgb_zone_configurations[SOURCE]["Channel A2"] = {"units": 1, "leds_per_unit": 8}
    ambiguous = replace(FAN, connection="")
    assert build_specs(host, [ambiguous], {}) == {}
    assert "front-fans" in build_specs(host, [FAN], {})
    host.rgb_zone_configurations[SOURCE]["Channel A1"]["leds_per_unit"] = 0
    # There is no fallback to another live header when the hinted target is empty.
    assert build_specs(host, [FAN], {}) == {}
    host.settings.data[KEY] = '{"front-fans":{"controller":"openrgb:missing","zone":"Channel A1"}}'
    assert build_specs(host, [FAN], {}) == {}


@pytest.mark.parametrize("movement", ["local", "left-right", "top-bottom"])
def test_fan_frame_reuses_full_device_plan_bounds_and_clock(host, movement, monkeypatch):
    import json
    from modules.rgb_studio.v1_15.led_topology_store import KEY as PATH_KEY

    path = dict(RING, direction=movement)
    host.settings.data[PATH_KEY] = json.dumps({SOURCE: {"Channel A1": path}})
    config = host.openrgb_effect_assignments[SOURCE]
    spec = build_specs(host, [FAN], {"front-fans": (path, 16)})["front-fans"]
    before = copy.deepcopy(host.settings.data), copy.deepcopy(host.rgb_zone_configurations)
    assert "Channel A1" in case_rectangles(host, SOURCE)
    for elapsed in (0., .2, .4):
        host.rgb_last_sent_elapsed = elapsed
        plan = build(host, SOURCE, host.openrgb_devices[0], config, elapsed)
        assert frame(host, spec) == tuple(render(plan, 16, [16]))
    def forbidden(*_args):
        raise AssertionError("A frame must not rescan routes or component bounds")
    monkeypatch.setattr("modules.pc_case_profiles.v1_5.case_animation.case_rectangles", forbidden)
    for elapsed in (.6, .8, 1.):
        host.rgb_last_sent_elapsed = elapsed
        assert len(frame(host, spec)) == 16
    assert (host.settings.data, host.rgb_zone_configurations) == before


def test_case_bounds_are_built_once_per_controller_and_refreshed_with_layout(host, monkeypatch):
    import json
    from modules.pc_case_profiles.v1_5 import case_animation
    from modules.rgb_studio.v1_15.led_topology_store import KEY as PATH_KEY

    second = replace(FAN, position="rear", connection="Channel A2", slot_id="rear-fan", x=.3)
    host.openrgb_devices = [replace(host.openrgb_devices[0], zones=("Channel A1", "Channel A2"))]
    host.rgb_zone_configurations[SOURCE]["Channel A2"] = {"units": 1, "leds_per_unit": 8}
    host.rgb_layout_slots = [FAN, second]
    path = dict(LINE, direction="left-right")
    host.settings.data[PATH_KEY] = json.dumps({SOURCE: {"Channel A1": path, "Channel A2": path}})
    paths = {"front-fans": (path, 16), "rear-fan": (path, 8)}
    calls = []
    def measured_bounds(target, controller):
        calls.append(controller)
        return case_rectangles(target, controller)
    monkeypatch.setattr(case_animation, "case_rectangles", measured_bounds)
    specs = build_specs(host, host.rgb_layout_slots, paths)
    assert calls == [SOURCE] and len(specs) == 2
    before = specs["rear-fan"]["rectangle"]
    host.rgb_layout_slots = [FAN, replace(second, x=.5)]
    updated = build_specs(host, host.rgb_layout_slots, paths)
    assert calls == [SOURCE, SOURCE]
    assert updated["rear-fan"]["rectangle"] != before


def test_ring_projection_keeps_declared_start_rotation_and_fan_order():
    colors = tuple(f"{n:06x}" for n in range(16))
    first = ring_segments(colors, 0, 2, RING)
    second = ring_segments(colors, 1, 2, RING)
    assert [segment[2] for segment in first] == list(colors[8:])
    assert [segment[2] for segment in second] == list(colors[:8])
    assert first[0][:2] == (90., -45.)
    counterclockwise = ring_segments(colors, 0, 2, dict(RING, clockwise=False))
    assert counterclockwise[0][:2] == (90., 45.)
    assert len(ring_segments(colors, 0, 1, dict(RING, units=2))) == 16
    assert ring_segments(colors, -1, 2) == ring_segments(colors, 0, 0) == ()
    assert ring_segments(colors * 33, 0, 2) == ()
    assert ring_segments(("ffffff",), 0, 2) == ()
    assert len(ring_segments(("ffffff",) * 512, 0, 1)) == 24


def test_preview_brightness_is_bounded_cached_and_never_lights_black():
    assert brighter_preview_color("000000") == "000000"
    assert brighter_preview_color("204080") == "264c97"
    assert brighter_preview_color("f0f8ff") == "ffffff"
    assert brighter_preview_color("not-a-colour") == "not-a-colour"
    before = brighter_preview_color.cache_info()
    brighter_preview_color("204080")
    after = brighter_preview_color.cache_info()
    assert after.hits == before.hits + 1


class PaintedDiagram(PCLayoutDiagram):
    def __init__(self, parent=None):
        self.paint_count = 0
        super().__init__(parent)

    def paintEvent(self, event):
        self.paint_count += 1
        super().paintEvent(event)


@pytest.mark.parametrize("visual_kind", ["fans", "ring"])
def test_real_qt_timer_shows_shared_phase_and_stops_when_ancestor_hidden(host, visual_kind):
    parent = QWidget()
    layout = QVBoxLayout(parent)
    diagram = PaintedDiagram(parent)
    layout.addWidget(diagram)
    slot = replace(FAN, visual_kind=visual_kind)
    diagram.set_slots([slot])
    diagram.set_cooling_visual("aio")
    specs = build_specs(host, [slot], {})
    diagram.set_led_animations(specs, host)
    assert not diagram.animation_timer.isActive()
    parent.show()
    APP.processEvents()
    assert diagram.isVisible() and diagram.animation_timer.isActive()
    assert diagram.animation_timer.interval() == 40
    first_frame = diagram.slot_animation_colors(slot)
    first_image = diagram.grab().toImage()
    paint_count = diagram.paint_count
    started = time.monotonic()
    sent_clock = QTimer(parent)
    sent_clock.setInterval(10)
    sent_clock.timeout.connect(lambda: setattr(host, "rgb_last_sent_elapsed", time.monotonic() - started))
    sent_clock.start()
    QTest.qWait(160)
    second_frame = diagram.slot_animation_colors(slot)
    assert host.rgb_last_sent_elapsed >= .08
    assert diagram.paint_count > paint_count
    assert first_frame != second_frame
    assert first_image != diagram.grab().toImage()
    parent.hide()
    APP.processEvents()
    assert not diagram.isVisible() and not diagram.animation_timer.isActive()
    paint_count = diagram.paint_count
    elapsed = host.rgb_last_sent_elapsed
    QTest.qWait(100)
    assert diagram.paint_count == paint_count
    assert host.rgb_last_sent_elapsed > elapsed  # UI hide never pauses the worker clock.
    diagram.tick_led_animation()  # A queued stale timeout cannot restart hidden work.
    assert not diagram.animation_timer.isActive()
    parent.show()
    APP.processEvents()
    assert diagram.animation_timer.isActive() and diagram.animation_timer.interval() == 40
    assert diagram.slot_animation_colors(slot) != second_frame
    host.openrgb_effect_active = False
    diagram.tick_led_animation()
    assert diagram.animation_timer.interval() == 500
    assert diagram.slot_animation_colors(slot) == ()
    sent_clock.stop()
    parent.close()


def test_visible_preview_starts_fast_when_effect_becomes_active(host):
    diagram = PaintedDiagram()
    diagram.set_slots([FAN])
    diagram.show()
    APP.processEvents()
    host.openrgb_effect_active = False
    specs = build_specs(host, [FAN], {})
    diagram.set_led_animations(specs, host)
    assert diagram.animation_timer.interval() == 500
    host.openrgb_effect_active = True
    diagram.set_led_animations(specs, host)
    assert diagram.animation_timer.interval() == 40
    diagram.close()


@pytest.mark.parametrize("visual_kind", ["fans", "ring"])
def test_real_qt_ring_retains_motion_between_leds_when_fan_midpoint_stays_black(visual_kind):
    from PySide6.QtGui import QColor

    diagram = PaintedDiagram()
    slot = replace(FAN, count=1, visual_kind=visual_kind)
    diagram.set_slots([slot])
    diagram.set_cooling_visual("aio")
    colors = ["000000"] * 16
    colors[0] = "ff0000"
    diagram.slot_animation_colors = lambda _slot: tuple(colors)
    diagram.show()
    APP.processEvents()
    first = diagram.grab().toImage()
    representative = diagram._animation_color(colors, 0, 1, QColor("#ffffff"))
    colors[0], colors[1] = "000000", "ff0000"
    assert diagram._animation_color(colors, 0, 1, QColor("#ffffff")) == representative
    diagram.update()
    APP.processEvents()
    assert first != diagram.grab().toImage()
    assert not diagram.animation_timer.isActive()  # No private RGB clock or hardware session.
    diagram.close()
