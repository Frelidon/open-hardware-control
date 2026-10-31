"""Visual resize and connector naming must never change hardware topology."""
import os
from pathlib import Path
import sys
from dataclasses import replace
from types import SimpleNamespace
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OHC_DISABLE_HARDWARE_IO", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rgb_devices import RGBGroup, RGBLayoutSlot, normalize_layout_slots, normalize_layout_scale
from modules.pc_case_profiles.v1_5 import CASE_TEMPLATES, PCLayoutDiagram, PcCaseProfilesMixin
from modules.pc_case_profiles.v1_5.case_geometry import arrange_case_slots
from modules.pc_case_profiles.v1_5.channel_labels import channel_caption, channel_details
from modules.pc_case_profiles.v1_5.view_state import cooling_slots, resize_cooling_slot, move_cooling_slot, set_synchronized
from test_case_workspace_342983 import Settings

APP = QApplication.instance() or QApplication([])
SLOT = RGBLayoutSlot("front", "Front", 2, "fans", "", (), "fans-front", .79, .54, "intake", 120)


@pytest.mark.parametrize("value,expected", [(None, 1), ("oops", 1), (True, 1), (float("nan"), 1),
                                           (float("inf"), 1), (-1, .25), (10, 2), (.5, .5)])
def test_scale_validation(value, expected):
    assert normalize_layout_scale(value) == expected


def test_old_and_new_profiles_keep_visual_scale_separate_from_hardware():
    host = SimpleNamespace(rgb_layout_slots=[replace(SLOT, scale=.5)])
    payload = PcCaseProfilesMixin.rgb_layout_slots_payload(host)
    groups = [RGBGroup("fans", "Fans")]
    assert normalize_layout_slots(payload, groups) == host.rgb_layout_slots
    payload[0].pop("scale")
    assert normalize_layout_slots(payload, groups)[0] == SLOT


@pytest.mark.parametrize("size", [(760, 570), (1200, 900)])
def test_all_case_templates_fit_proportionally_and_preserve_metadata(size):
    diagram = PCLayoutDiagram()
    diagram.resize(*size)
    for template in CASE_TEMPLATES:
        diagram.set_case_template(template)
        slots = [replace(SLOT, position=position, count=count) for position, count in template.fan_layout]
        arranged = arrange_case_slots(slots, template.case_id)
        for original, slot in zip(slots, arranged):
            assert replace(slot, x=original.x, y=original.y) == original
            for scale in (.25, 1, 2):
                assert diagram.canvas_area().contains(diagram.slot_rect(replace(slot, scale=scale)))
    diagram.close()


def test_corner_resize_commits_once_and_escape_cancels():
    diagram = PCLayoutDiagram()
    diagram.resize(900, 650)
    diagram.set_slots([SLOT])
    diagram.set_selected_slot(SLOT.slot_id)
    diagram.show()
    APP.processEvents()
    changes = []
    diagram.slot_resized.connect(lambda *args: changes.append(args))
    center = diagram.slot_center(SLOT)
    corner = diagram.resize_handle(SLOT).center()
    target = center + (corner - center) * .5
    QTest.mousePress(diagram, Qt.MouseButton.LeftButton, pos=corner.toPoint())
    QTest.mouseMove(diagram, target.toPoint())
    APP.processEvents()
    assert changes == []
    assert diagram.slot_rect(SLOT).width() < 58
    QTest.mouseRelease(diagram, Qt.MouseButton.LeftButton, pos=target.toPoint())
    assert len(changes) == 1 and .45 < changes[0][1] < .55
    assert diagram.slots == [SLOT]
    QTest.mousePress(diagram, Qt.MouseButton.LeftButton, pos=corner.toPoint())
    QTest.keyClick(diagram, Qt.Key.Key_Escape)
    QTest.mouseRelease(diagram, Qt.MouseButton.LeftButton, pos=target.toPoint())
    assert len(changes) == 1
    diagram.close()


def test_shared_and_separate_cooling_scales_preserve_pwm_led_identity():
    calls = []
    host = SimpleNamespace(settings=Settings(), rgb_layout_slots=[SLOT],
                           mainboard_layout_assignments={"nct6687:pwm6": SLOT.slot_id},
                           refresh_rgb_layout_editor=lambda: None,
                           resize_rgb_layout_slot=lambda *args: calls.append(args))
    resize_cooling_slot(host, SLOT.slot_id, .5)
    assert calls == [(SLOT.slot_id, .5)]
    set_synchronized(host, False)
    resize_cooling_slot(host, SLOT.slot_id, .5)
    move_cooling_slot(host, SLOT.slot_id, .3, .4, "rear")
    visual = cooling_slots(host)[0]
    assert visual.scale == .5 and visual.position == "rear"
    assert host.rgb_layout_slots == [SLOT]
    assert visual.size_mm == SLOT.size_mm and visual.device_ids == SLOT.device_ids
    assert host.mainboard_layout_assignments == {"nct6687:pwm6": SLOT.slot_id}
    set_synchronized(host, True)
    assert cooling_slots(host) == [SLOT]
    set_synchronized(host, False)
    assert cooling_slots(host)[0].scale == .5


def test_system_fan_caption_does_not_guess_or_renumber_driver_channels():
    channel = SimpleNamespace(display_name="System Fan #4", index=6, name="nct6687", stable_id="nct6687:pwm6")
    assert channel_caption(None, channel) == "SYS_FAN4"
    assert "pwm6" in channel_details(channel) and "PWM 6" in channel_details(channel)
    channel.display_name = "Unlabelled"
    assert channel_caption(None, channel) == "Unlabelled"


def test_unassigned_block_double_click_opens_editor_without_rgb_error():
    calls = []
    host = SimpleNamespace(rgb_layout_slots=[SLOT], focus_rgb_layout_slot=lambda key: calls.append(key),
                           rgb_logical_devices=lambda: [], edit_selected_rgb_layout_slot=lambda: calls.append("edit"),
                           show_error=lambda msg: pytest.fail(msg))
    PcCaseProfilesMixin.open_rgb_layout_slot_device_editor(host, SLOT.slot_id)
    assert calls == [SLOT.slot_id, "edit"]


def test_unassigned_led_action_does_not_recursively_open_block_editors(monkeypatch):
    from modules.rgb_studio.v1_15.argb_controls import edit_slot_header
    calls = []
    host = SimpleNamespace(rgb_layout_slots=[SLOT], openrgb_devices=[], openrgb_stable_ids={},
                           rgb_gpu_routes={}, tr_static=lambda text: text,
                           rgb_layout_status_label=SimpleNamespace(setText=lambda text: calls.append(text)),
                           open_rgb_layout_slot_device_editor=lambda key: pytest.fail("nested block editor"))
    monkeypatch.setattr("modules.rgb_studio.v1_15.argb_controls.choose_slot_header",
                        lambda _host, slot, targets, **kwargs: calls.append((slot.slot_id, targets, kwargs)))
    edit_slot_header(host, SLOT.slot_id)
    assert calls == [(SLOT.slot_id, [], {"suggested_units": SLOT.count})]


def test_callouts_show_configured_gpu_and_holder_leds_and_physical_sysfan():
    from modules.pc_case_profiles.v1_5.topology_labels import slot_topology_label
    from openrgb_integration import OpenRGBDevice
    source = OpenRGBDevice(3, "MSI MYSTIC LIGHT", device_type="Motherboard",
                           modes=("Direct",), zones=("JARGB 1", "JARGB 2"))
    gpu = OpenRGBDevice(2, "Sapphire", device_type="GPU", modes=("Rainbow",), leds=("GPU",))
    host = SimpleNamespace(
        openrgb_devices=[source, gpu], openrgb_stable_ids={3: "openrgb:msi", 2: "openrgb:gpu"},
        rgb_gpu_routes={"openrgb:gpu": {"controller": "openrgb:msi", "zone": "JARGB 1"}},
        rgb_zone_configurations={"openrgb:msi": {"JARGB 1": {"units": 1, "leds_per_unit": 30},
                                        "JARGB 2": {"units": 2, "leds_per_unit": 24}}},
        chassis_mainboard_channels=lambda: [SimpleNamespace(stable_id="nct6687:pwm6", display_name="System Fan #4")],
        mainboard_layout_assignments={"nct6687:pwm6": "fans-front"},
    )
    assert slot_topology_label(host, replace(SLOT, device_ids=("openrgb:msi",), connection="JARGB_V2_2"))[:2] == (
        "LEDs: 48", "PWM: SYS_FAN4")
    assert slot_topology_label(host, replace(SLOT, position="gpu", slot_id="gpu", device_ids=("openrgb:gpu",)))[:2] == (
        "LEDs: 30", "PWM: —")
    assert slot_topology_label(host, replace(SLOT, device_ids=()))[:2] == ("LEDs: —", "PWM: SYS_FAN4")
    holder = OpenRGBDevice(4, "Airgoo", modes=("Direct",), zones=("Channel B6", "Channel B7"))
    host.openrgb_devices.append(holder)
    host.openrgb_stable_ids[4] = "airgoo"
    host.rgb_zone_configurations["airgoo"] = {"Channel B6": {"units": 1, "leds_per_unit": 24}}
    label = slot_topology_label(host, replace(SLOT, device_ids=("airgoo",), connection="RGB-Hub B6 · 1×24 LEDs"))
    assert label[:2] == ("LEDs: 24", "PWM: SYS_FAN4")
