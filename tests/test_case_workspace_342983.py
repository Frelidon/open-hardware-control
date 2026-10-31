"""Shared chassis mapping, independent positions and all-header pixel tests."""

import os
from pathlib import Path
import sys
from types import SimpleNamespace
from dataclasses import replace
import json
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OHC_DISABLE_HARDWARE_IO", "1")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QMessageBox, QPushButton, QSpinBox, QWidget, QFormLayout
from openrgb_integration import OpenRGBDevice
from rgb_devices import RGBLayoutSlot, flori_rgb_layout_profile
from modules.pc_case_profiles.v1_5.view_state import cooling_slots, move_cooling_slot, set_synchronized
from modules.pc_case_profiles.v1_5.case_page import assign_pwm, slot_build_caption, slot_declares_lighting, slot_supports_pwm
from modules.pc_case_profiles.v1_5.controller import PcCaseProfilesMixin
from modules.pc_case_profiles.v1_5.case_renderer import APPEARANCES, slot_label_placements
from modules.pc_case_profiles.v1_5 import CASE_TEMPLATES, PCLayoutDiagram
from modules.rgb_studio.v1_15.gpu_led_editor import show_gpu_header_editor
from modules.rgb_studio.v1_15.argb_controls import slot_header_targets
from modules.rgb_studio.v1_15.argb_store import remember_headers
from modules.rgb_studio.v1_15.gpu_lighting import GpuLightingMixin
from modules.rgb_studio.v1_15.studio_panels import build_transfer_status

APP = QApplication.instance() or QApplication([])
MSI = OpenRGBDevice(3, "MSI MYSTIC LIGHT", device_type="Motherboard", modes=("Direct",),
                    zones=("JAF", "JARGB 1", "JARGB 2", "JARGB 3"))
GPU = OpenRGBDevice(2, "Sapphire RX 9070 XT NITRO+", device_type="GPU",
                    modes=("External Control", "Rainbow Wave"), leds=("GPU",))
SLOT = RGBLayoutSlot("front", "Front fans", 2, "front", "JARGB_V2_2", ("openrgb:msi",), "front-slot", .87, .4)
ZONES = [{"name": n, "current": 90, "minimum": 0, "maximum": 240, "resizable": True} for n in MSI.zones]


class Settings:
    def __init__(self): self.data = {}
    def value(self, key, default=None, **kwargs): return self.data.get(key, default)
    def contains(self, key): return key in self.data
    def setValue(self, key, value): self.data[key] = value
    def sync(self): pass


@pytest.mark.parametrize("height", [30, 46])
def test_personal_case_callouts_do_not_cover_components_or_each_other(height):
    from PySide6.QtCore import QRectF
    diagram = PCLayoutDiagram()
    diagram.resize(900, 570)
    _, slots = flori_rgb_layout_profile("thermalright")
    diagram.set_slots(slots)
    rectangles = [diagram.slot_rect(slot) for slot in slots]
    badges = slot_label_placements(QRectF(diagram.rect()), diagram.canvas_area(), rectangles, height=height, side_first=True)
    assert all(badge is not None for badge in badges)
    for index, badge in enumerate(badges):
        assert QRectF(diagram.rect()).contains(badge)
        assert not any(badge.intersects(rect) for rect in rectangles)
        assert not any(badge.intersects(other) for other in badges[index + 1:])
    diagram.close()


def test_sync_opt_out_retains_independent_positions_and_shared_hardware():
    host = SimpleNamespace(settings=Settings(), rgb_layout_slots=[SLOT],
                           rgb_gpu_routes={}, mainboard_layout_assignments={"hw:pwm4": "front-slot"})
    moved = []
    host.move_rgb_layout_slot = lambda *args: moved.append(args)
    host.refresh_rgb_layout_editor = lambda: None
    assert cooling_slots(host)[0] == SLOT
    set_synchronized(host, False)
    move_cooling_slot(host, "front-slot", .2, .5, "rear")
    assert host.rgb_layout_slots[0] == SLOT
    assert cooling_slots(host)[0].x == .2
    assert cooling_slots(host)[0].device_ids == SLOT.device_ids
    assert host.mainboard_layout_assignments == {"hw:pwm4": "front-slot"}
    set_synchronized(host, True)
    assert cooling_slots(host)[0] == SLOT
    move_cooling_slot(host, "front-slot", .3, .6, "side")
    assert moved == [("front-slot", .3, .6, "side")]
    set_synchronized(host, False)
    assert cooling_slots(host)[0].x == .2
    move_cooling_slot(host, "missing", .1, .1, "rear")
    move_cooling_slot(host, "front-slot", float("nan"), .1, "rear")
    assert cooling_slots(host)[0].x == .2


def test_case_device_capabilities_hide_impossible_display_led_and_pwm_fields():
    _, slots = flori_rgb_layout_profile("thermalright")
    pump = next(slot for slot in slots if slot.position == "pump")
    front = next(slot for slot in slots if slot.position == "front")
    support = next(slot for slot in slots if slot.position == "gpu-support")
    assert slot_build_caption(pump) == "Display / Pumpenkopf"
    # The Levita pump head now exposes its separately wired PUMP_FAN channel.
    assert slot_supports_pwm(pump)
    assert not slot_declares_lighting(pump, [])
    assert slot_supports_pwm(front)
    assert slot_build_caption(front) == "2 × 120 mm"
    assert slot_declares_lighting(front, [])
    assert not slot_supports_pwm(support)
    assert slot_declares_lighting(support, [])


def test_pwm_assignment_reuses_existing_chassis_mapping_without_enabling_control():
    channel = SimpleNamespace(stable_id="hw:pwm4", index=4)
    calls = []
    host = SimpleNamespace(
        mainboard_calibration_channel_id="", rgb_layout_selected_slot_id="front-slot",
        mainboard_layout_assignments={}, _fan_layout_slot=lambda key: SLOT if key == "front-slot" else None,
        chassis_mainboard_channels=lambda: [channel], refresh_rgb_layout_editor=lambda: calls.append("refresh"),
        assign_selected_channel_to_cooling_slot=lambda: calls.append("assign"),
        tr_static=lambda s: s, show_error=lambda s: calls.append("error"),
        mainboard_control_active=False, mainboard_fan_profiles={"hw:pwm4": {"enabled": False, "calibrated": False}},
    )
    assign_pwm(host, channel_id="hw:pwm4", slot_id="front-slot")
    assert calls == ["assign", "refresh"]
    assert host.mainboard_selected_channel_id == "hw:pwm4"
    assert host.cooling_layout_selected_slot_id == "front-slot"
    assert not host.mainboard_control_active
    assert host.mainboard_fan_profiles["hw:pwm4"] == {"enabled": False, "calibrated": False}
    host.mainboard_calibration_channel_id = "hw:pwm4"
    assign_pwm(host, channel_id="", slot_id="front-slot")
    assert calls[-1] == "error"


@pytest.mark.parametrize(
    "channel_id,target,accepted,expected_mapping,expected_pump,expected_radiator",
    [
        ("cpu", "pump", True, {"cpu": "pump"}, "cpu", ""),
        ("pump-channel", "radiator-top", True, {"pump-channel": "radiator-top"}, "", "pump-channel"),
        ("cpu", "front-slot", True, {"cpu": "front-slot", "pump-channel": "pump"}, "pump-channel", ""),
        ("case", "pump", True, {"cpu": "radiator-top", "case": "pump"}, "case", "cpu"),
        ("cpu", "pump", False, {"cpu": "radiator-top", "pump-channel": "pump"}, "pump-channel", "cpu"),
    ],
)
def test_pwm_moves_and_replacements_keep_persisted_aio_roles_consistent(
    monkeypatch, channel_id, target, accepted, expected_mapping, expected_pump, expected_radiator,
):
    channels = {
        key: SimpleNamespace(stable_id=key, display_name=key)
        for key in ("cpu", "pump-channel", "case")
    }
    slots = [
        SLOT,
        RGBLayoutSlot("top", "Radiator", 3, "cooling", slot_id="radiator-top", size_mm=120),
        RGBLayoutSlot("pump", "Pump", 1, "cooling", slot_id="pump", size_mm=0),
    ]
    settings = Settings()
    settings.setValue("thermalright_cooling/pump_channel", "pump-channel")
    settings.setValue("thermalright_cooling/radiator_channel", "cpu")
    saved = []
    host = SimpleNamespace(
        rgb_layout_slots=slots, mainboard_layout_assignments={"cpu": "radiator-top", "pump-channel": "pump"},
        cooling_layout_selected_slot_id=target, settings=settings,
        thermalright_pump_channel_id="pump-channel", thermalright_radiator_channel_id="cpu",
        selected_mainboard_channel=lambda: channels[channel_id],
        tr_static=lambda text: text, show_error=lambda text: pytest.fail(text),
        mainboard_profile_for=lambda _channel: {"name": "custom", "enabled": False, "calibrated": False},
        save_mainboard_fan_settings=lambda: saved.append("settings"),
        sync_selected_rgb_case_profile_pwm_assignments=lambda: saved.append("profile"),
        refresh_chassis_assistant_summary=lambda: None, refresh_mainboard_fan_table=lambda: None,
        refresh_rgb_layout_editor=lambda: None, log_message=lambda _message: None,
        footer_status=SimpleNamespace(setText=lambda _message: None),
    )
    host._fan_layout_slot = lambda key: PcCaseProfilesMixin._fan_layout_slot(host, key)
    monkeypatch.setattr(
        QMessageBox, "question",
        lambda *_args: QMessageBox.StandardButton.Yes if accepted else QMessageBox.StandardButton.No,
    )
    PcCaseProfilesMixin.assign_selected_channel_to_cooling_slot(host)
    assert host.mainboard_layout_assignments == expected_mapping
    assert host.thermalright_pump_channel_id == expected_pump
    assert host.thermalright_radiator_channel_id == expected_radiator
    assert settings.value("thermalright_cooling/pump_channel") == expected_pump
    assert settings.value("thermalright_cooling/radiator_channel") == expected_radiator
    assert saved == (["settings", "profile"] if accepted else [])


@pytest.mark.parametrize(
    "persisted,expected_pump,expected_radiator",
    [
        ({}, "pump-channel", "cpu"),
        ({"pump_channel": "", "radiator_channel": ""}, "", ""),
        ({"pump_channel": "pump-channel", "radiator_channel": ""}, "pump-channel", ""),
        ({"pump_channel": "missing", "radiator_channel": "cpu"}, "", "cpu"),
    ],
)
def test_aio_suggestions_only_fill_missing_settings_not_explicit_unassignments(
    persisted, expected_pump, expected_radiator,
):
    from kraken_control import KrakenControl
    settings = Settings()
    for role, channel_id in persisted.items():
        settings.setValue(f"thermalright_cooling/{role}", channel_id)
    host = SimpleNamespace(
        settings=settings,
        mainboard_channels={
            "pump-channel": SimpleNamespace(stable_id="pump-channel", display_name="Pump Fan"),
            "cpu": SimpleNamespace(stable_id="cpu", display_name="CPU Fan"),
        },
        thermalright_pump_channel_id=persisted.get("pump_channel", ""),
        thermalright_radiator_channel_id=persisted.get("radiator_channel", ""),
        thermalright_pump_channel_combo=QComboBox(), thermalright_radiator_channel_combo=QComboBox(),
        _mainboard_channel_rpm=lambda _channel: None,
    )
    host.save_thermalright_channel_mapping = lambda: KrakenControl.save_thermalright_channel_mapping(host)
    if not persisted:
        detected_channels, host.mainboard_channels = host.mainboard_channels, {}
        KrakenControl.populate_thermalright_channel_combos(host)
        assert not settings.contains("thermalright_cooling/pump_channel")
        assert not settings.contains("thermalright_cooling/radiator_channel")
        host.mainboard_channels = detected_channels
    # A later refresh must preserve a deliberately empty or disappeared role.
    for _refresh in range(2):
        KrakenControl.populate_thermalright_channel_combos(host)
        assert host.thermalright_pump_channel_id == expected_pump
        assert host.thermalright_radiator_channel_id == expected_radiator
        assert settings.value("thermalright_cooling/pump_channel") == expected_pump
        assert settings.value("thermalright_cooling/radiator_channel") == expected_radiator


@pytest.mark.parametrize(
    "hardware,expected_pump,expected_radiator",
    [
        ({"aio_channels": {"pump": "case", "radiator": "cpu"}}, "case", "cpu"),
        ({"aio_channels": {"pump": "", "radiator": ""}}, "", ""),
        ({"aio_channels": {"pump": "missing", "radiator": "cpu"}}, "", "cpu"),
        ({"pwm_assignments": {"pump-channel": "pump", "cpu": "radiator-top"}}, "pump-channel", "cpu"),
        ({"pwm_assignments": {"pump-channel": "pump", "case": "pump"}}, "", ""),
        ({"pwm_assignments": {"missing": "pump", "cpu": "not-in-this-profile"}}, "", ""),
        ({"pwm_assignments": {}}, "", ""),
        ({}, "", ""),
    ],
)
def test_loading_case_profiles_restores_only_their_own_known_aio_roles(
    hardware, expected_pump, expected_radiator,
):
    settings = Settings()
    host = SimpleNamespace(
        settings=settings, mainboard_channels={key: object() for key in ("cpu", "pump-channel", "case")},
        rgb_layout_slots=[
            RGBLayoutSlot("pump", "Pump", 1, "cooling", slot_id="pump", size_mm=0),
            RGBLayoutSlot("top", "Radiator", 3, "cooling", slot_id="radiator-top", size_mm=120),
        ],
        rgb_groups=[], rgb_device_aliases={}, mainboard_layout_assignments={"foreign-old": "pump"},
        thermalright_pump_channel_id="foreign-old", thermalright_radiator_channel_id="foreign-radiator",
        mainboard_control_active=False, save_mainboard_fan_settings=lambda: None,
        set_mainboard_channel_percent=lambda *_args: pytest.fail("profile load wrote PWM"),
    )
    host._restore_profile_aio_channels = lambda data: PcCaseProfilesMixin._restore_profile_aio_channels(host, data)
    PcCaseProfilesMixin._restore_profile_hardware(host, {"hardware": hardware})
    assert host.thermalright_pump_channel_id == expected_pump
    assert host.thermalright_radiator_channel_id == expected_radiator
    assert settings.value("thermalright_cooling/pump_channel") == expected_pump
    assert settings.value("thermalright_cooling/radiator_channel") == expected_radiator
    assert not host.mainboard_control_active


def test_all_header_targets_use_assigned_controllers_and_explicit_gpu_route():
    host = SimpleNamespace(openrgb_devices=[GPU, MSI], openrgb_stable_ids={2:"openrgb:gpu",3:"openrgb:msi"},
                           rgb_gpu_routes={"openrgb:gpu":{"controller":"openrgb:msi","zone":"JARGB 1"}})
    assert slot_header_targets(host, SLOT) == [(MSI, "JARGB 2", None)]
    gpu_slot = replace(SLOT, position="gpu", device_ids=("openrgb:gpu",), connection="")
    assert slot_header_targets(host, gpu_slot) == [(MSI, "JARGB 1", GPU)]
    host.rgb_gpu_routes = {}
    assert slot_header_targets(host, gpu_slot) == []
    assert slot_header_targets(host, replace(SLOT, device_ids=())) == []


def test_manual_other_header_counts_survive_design_profiles_but_unedited_zones_can_restore():
    host = SimpleNamespace(settings=Settings(), rgb_gpu_routes={}, rgb_zone_configurations={
        "openrgb:msi": {"JARGB 1":{"units":1,"leds_per_unit":30}, "JARGB 2":{"units":2,"leds_per_unit":24}}})
    remember_headers(host, "openrgb:msi", ["JARGB 2"])
    GpuLightingMixin.restore_gpu_profile_hardware(host, {"studio_zone_configurations":{
        "openrgb:msi":{"JARGB 1":{"units":1,"leds_per_unit":90}, "JARGB 2":{"units":1,"leds_per_unit":1}}}})
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 2"] == {"units":2,"leds_per_unit":24}
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 1"] == {"units":1,"leds_per_unit":90}


@pytest.mark.parametrize("zone_name,count,pixel,offset", [("JARGB 2",30,1,120), ("JARGB 3",30,30,210)])
def test_other_header_pixel_test_does_not_switch_gpu_or_overwrite_its_confirmed_30(monkeypatch, zone_name, count, pixel, offset):
    class Host(QWidget):
        def __init__(self):
            super().__init__()
            self.settings = Settings()
            self.openrgb_stable_ids = {3:"openrgb:msi"}
            self.rgb_zone_configurations = {"openrgb:msi":{
                "JAF":{"units":0,"leds_per_unit":0}, "JARGB 1":{"units":1,"leds_per_unit":30},
                "JARGB 2":{"units":1,"leds_per_unit":90}, "JARGB 3":{"units":1,"leds_per_unit":90}}}
            self.openrgb_sdk_ready_devices = {"openrgb:msi"}
            self.openrgb_write_enabled = True
            self.openrgb_external_server_detected = False
            self.rgb_test_color = "ff0000"
            self.commands, self.logs, self.saved = [], [], 0
            self.openrgb_client = SimpleNamespace(
                native_mode_command=lambda *a: pytest.fail("Unrelated GPU write"),
                sdk_color_command=lambda *a, **kw: ["sdk", a, kw])
        def tr_static(self, s): return s
        def openrgb_device_conflict(self, d): return False
        def stop_openrgb_effect(self, s): self.logs.append("stopped")
        def show_error(self, s): pytest.fail(s)
        def log_message(self, s): self.logs.append(s)
        def run_rgb_command_sequence(self, commands, description, **kwargs):
            self.commands = commands
            kwargs["finished"](True)
        def save_rgb_workspace(self): self.saved += 1
        def rebuild_rgb_workspace(self): pass
    host = Host()
    callback_counts = []
    def edit(dialog):
        count_spin = dialog.findChild(QSpinBox, "argbLedCount")
        index = dialog.findChild(QSpinBox, "argbTestIndex")
        count_spin.setValue(count)
        index.setValue(pixel)
        next(b for b in dialog.findChildren(QPushButton) if b.text() == "Eine LED testen").click()
        next(b for b in dialog.findChildren(QPushButton) if b.text() == "Speichern").click()
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(QDialog, "exec", edit)
    show_gpu_header_editor(host, None, MSI, zone_name, ZONES, on_saved=callback_counts.append)
    colors = host.commands[0][1][1]
    assert len(host.commands) == 1 and colors.count("ffffff") == 1
    # JAF is disabled, GPU 30 is preserved, preceding header remains 90.
    expected = 30 + (90 if zone_name == "JARGB 3" else 0) + pixel - 1
    assert colors[expected] == "ffffff"
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 1"] == {"units":1,"leds_per_unit":30}
    assert host.rgb_zone_configurations["openrgb:msi"][zone_name] == {"units":1,"leds_per_unit":count}
    assert callback_counts == [count] and host.saved == 1
    assert any("pixel-test-sdk-ok" in line for line in host.logs)
    assert any(f"frame_0based={expected}" in line for line in host.logs)
    host.close()


def test_transfer_status_has_full_width_and_height_and_every_case_renders_distinctly():
    host = QWidget()
    form = QFormLayout(host)
    build_transfer_status(host, form)
    assert host.openrgb_performance_label.minimumHeight() >= 84
    assert form.itemAt(0, QFormLayout.ItemRole.SpanningRole) is not None
    assert set(APPEARANCES) == {t.case_id for t in CASE_TEMPLATES}
    images = []
    for template in CASE_TEMPLATES:
        diagram = PCLayoutDiagram()
        diagram.resize(960,720)
        diagram.set_case_template(template)
        diagram.set_slots([SLOT])
        pixmap = diagram.grab()
        assert not pixmap.isNull()
        image = pixmap.toImage()
        images.append(bytes(image.bits()))
        diagram.close()
    assert len(set(images)) == 30
    host.close()
