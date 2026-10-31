"""Direct block header selection, stable persistence and existing LED tests."""
import json
import os
from dataclasses import replace
from pathlib import Path
import sys

import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OHC_DISABLE_HARDWARE_IO", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QPushButton, QWidget
from localization_catalog import UI_TRANSLATIONS
from openrgb_integration import OpenRGBDevice
from rgb_devices import RGBLayoutSlot
from modules.rgb_studio.v1_15.argb_controls import edit_slot_header, slot_header_targets
from modules.rgb_studio.v1_15.slot_route_editor import build_slot_route_dialog
from modules.rgb_studio.v1_15.slot_routes import KEY, normalize_slot_routes, remember_slot_route, slot_routes
from modules.pc_case_profiles.v1_5.topology_labels import slot_topology_label, slot_led_path

APP = QApplication.instance() or QApplication([])
MSI = OpenRGBDevice(3, "MSI MYSTIC LIGHT", device_type="Motherboard", modes=("Direct",),
                    zones=("JARGB 1", "JARGB 2", "JARGB 3"))
HUB = OpenRGBDevice(4, "Airgoo", modes=("Direct",), zones=("Channel A1", "Channel B6"))
SLOT = RGBLayoutSlot("front", "Front fans", 2, "front", "SYS_FAN4", (), "front-slot", .8, .4)


class Settings:
    def __init__(self): self.data = {}
    def value(self, key, default=None): return self.data.get(key, default)
    def setValue(self, key, value): self.data[key] = value
    def sync(self): pass


class Host(QWidget):
    def __init__(self, settings=None, language="de"):
        super().__init__()
        self.settings = settings or Settings()
        self.tr_static = lambda text: UI_TRANSLATIONS[language][text]
        self.openrgb_devices = [MSI, HUB]
        self.openrgb_stable_ids = {3: "openrgb:msi", 4: "openrgb:hub"}
        self.rgb_layout_slots = [SLOT]
        self.rgb_gpu_routes = {}
        self.rgb_zone_configurations = {"openrgb:msi": {
            "JARGB 1": {"units": 1, "leds_per_unit": 30},
            "JARGB 2": {"units": 3, "leds_per_unit": 30}}}
        self.mainboard_layout_assignments = {"nct6687:pwm6": "front-slot"}
        self.calls = []
        self.blocked = set()
    def openrgb_device_conflict(self, d): return d.index in self.blocked
    def save_rgb_workspace(self): self.calls.append("save")
    def rebuild_rgb_workspace(self): self.calls.append("refresh")
    def append_log(self, value): self.calls.append(value)
    def select_gpu_route_sources(self): self.calls.append("gpu-selection")
    def chassis_mainboard_channels(self):
        from types import SimpleNamespace
        return [SimpleNamespace(stable_id="nct6687:pwm6", display_name="System Fan #4")]


def choose(dialog, controller="openrgb:msi", zone="JARGB 1"):
    source_combo = dialog.findChild(QComboBox, "slotArgbController")
    source_combo.setCurrentIndex(source_combo.findData(controller))
    zone_combo = dialog.findChild(QComboBox, "slotArgbZone")
    zone_combo.setCurrentIndex(zone_combo.findData(zone))


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
def test_unassigned_block_has_localized_controller_header_count_and_test_choices(language):
    host = Host(language=language)
    dialog = build_slot_route_dialog(host, SLOT, [])
    controller = dialog.findChild(QComboBox, "slotArgbController")
    zone = dialog.findChild(QComboBox, "slotArgbZone")
    assert controller.currentData() == ""  # SYS_FAN4 must not imply an ARGB port.
    assert not zone.isEnabled()
    for name, caption in [("slotArgbEditLeds", "LED-Anzahl am ARGB-Anschluss ändern"),
                          ("slotArgbTestLed", "Eine LED testen")]:
        button = dialog.findChild(QPushButton, name)
        assert button.text() == UI_TRANSLATIONS[language][caption]
        assert not button.isEnabled()
    choose(dialog)
    assert zone.currentData() == "JARGB 1"
    assert dialog.findChild(QPushButton, "slotArgbTestLed").isEnabled()
    assert host.calls == [] and slot_routes(host) == {}
    render_dir = os.environ.get("OHC_UI_RENDER_DIR")
    if render_dir:
        dialog.show()
        APP.processEvents()
        dialog.grab().save(str(Path(render_dir) / f"argb-routing-{language}.png"))
    dialog.reject()
    assert host.calls == [] and slot_routes(host) == {}
    host.close()


@pytest.mark.parametrize("source,zone", [("openrgb:msi", "JARGB 1"), ("openrgb:msi", "JARGB 2"),
                                       ("openrgb:msi", "JARGB 3"), ("openrgb:hub", "Channel A1"),
                                       ("openrgb:hub", "Channel B6")])
@pytest.mark.parametrize("action", ["slotArgbEditLeds", "slotArgbTestLed"])
def test_every_reported_header_can_delegate_to_existing_bounded_led_editor(monkeypatch, source, zone, action):
    host = Host()
    calls = []
    monkeypatch.setattr("modules.rgb_studio.v1_15.slot_route_editor.configure_argb_header",
                        lambda h, d, n, **kwargs: calls.append((h, d, n, kwargs)))
    dialog = build_slot_route_dialog(host, SLOT, [])
    inventory_timer = dialog.findChild(QTimer, "slotArgbInventoryTimer")
    assert inventory_timer is not None and inventory_timer.isActive()
    choose(dialog, source, zone)
    dialog.findChild(QPushButton, action).click()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert not inventory_timer.isActive()
    for _ in range(10):
        APP.processEvents()
    device = MSI if source == "openrgb:msi" else HUB
    assert calls == [(host, device, zone, {"gpu": None, "component_name": SLOT.name})]
    assert slot_header_targets(host, SLOT) == [(device, zone, None)]
    assert slot_routes(host)["front-slot"] == {"controller": source, "zone": zone}
    assert host.rgb_layout_slots == [SLOT]  # No geometry/group/PWM mutation.
    assert host.mainboard_layout_assignments == {"nct6687:pwm6": "front-slot"}
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 2"]["units"] == 3
    host.close()


def test_current_binding_survives_restart_stale_parent_save_and_design_profile_slots():
    host = Host()
    assert remember_slot_route(host, "front-slot", "openrgb:msi", "JARGB 1")
    new_host = Host(settings=host.settings)
    # A parent's captured slot and an old design snapshot contain no RGB device.
    new_host.rgb_layout_slots = [replace(SLOT, device_ids=(), connection="old note", x=.3)]
    assert slot_header_targets(new_host, new_host.rgb_layout_slots[0]) == [(MSI, "JARGB 1", None)]
    assert slot_topology_label(new_host, new_host.rgb_layout_slots[0])[:2] == ("LEDs: 30", "PWM: SYS_FAN4")
    dialog = build_slot_route_dialog(new_host, new_host.rgb_layout_slots[0], [])
    assert dialog.findChild(QComboBox, "slotArgbController").currentData() == "openrgb:msi"
    assert dialog.findChild(QComboBox, "slotArgbZone").currentData() == "JARGB 1"
    dialog.reject()
    host.close()
    new_host.close()


def test_known_case_header_opens_led_editor_directly_and_route_button_still_opens_assignment(monkeypatch):
    from modules.rgb_studio.v1_15.argb_controls import build_slot_route_button
    host = Host()
    assert remember_slot_route(host, "front-slot", "openrgb:msi", "JARGB 1")
    calls = []
    monkeypatch.setattr("modules.rgb_studio.v1_15.argb_controls.configure_argb_header",
                        lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr("modules.rgb_studio.v1_15.argb_controls.choose_slot_header",
                        lambda *args, **kwargs: calls.append(("route", kwargs)))
    edit_slot_header(host, "front-slot")
    assert calls == [((host, MSI, "JARGB 1"), {
        "gpu": None, "component_name": SLOT.name, "suggested_units": SLOT.count,
    })]
    route_button = build_slot_route_button(host, "front-slot")
    route_button.click()
    assert calls[-1][0] == "route"
    host.close()


def test_case_led_path_uses_only_a_saved_unambiguous_physical_route():
    from modules.rgb_studio.v1_15.led_topology_store import remember_path
    from modules.pc_case_profiles.v1_5.diagram import PCLayoutDiagram
    host = Host()
    assert slot_led_path(host, SLOT) is None
    assert remember_slot_route(host, "front-slot", "openrgb:msi", "JARGB 1")
    path = dict(kind="line", start="left", end="right", units=1, clockwise=True)
    assert remember_path(host, "openrgb:msi", "JARGB 1", path, "local", 30)
    assert slot_led_path(host, SLOT) == ({**path, "direction": "local"}, 30)
    diagram = PCLayoutDiagram()
    diagram.set_slots([SLOT])
    diagram.set_led_paths({"front-slot": slot_led_path(host, SLOT)})
    assert diagram.led_paths["front-slot"][1] == 30
    diagram.resize(900, 650)
    diagram.show(); APP.processEvents()
    assert not diagram.grab().isNull()
    diagram.close(); host.close()


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
def test_case_gpu_button_opens_selected_gpu_setup_in_every_language(language):
    from modules.rgb_studio.v1_15.argb_controls import build_case_gpu_setup_button
    gpu = OpenRGBDevice(2, "Test GPU", device_type="GPU", modes=("External Control",))
    host = Host(language=language)
    host.openrgb_devices.append(gpu)
    host.openrgb_stable_ids[2] = "openrgb:gpu"
    host.rgb_layout_slots = [replace(SLOT, position="gpu", device_ids=("openrgb:gpu",))]
    host.rgb_layout_selected_slot_id = "front-slot"
    opened = []
    host.configure_gpu_lighting = opened.append
    button = build_case_gpu_setup_button(host)
    assert button.text() == UI_TRANSLATIONS[language]["Grafikkarte: Steuerweg und LEDs"]
    button.click()
    assert opened == [gpu]
    host.close()


def test_unassign_suppresses_legacy_fallback_without_erasing_global_led_counts():
    host = Host()
    host.rgb_layout_slots = [replace(SLOT, device_ids=("openrgb:msi",))]
    before = json.dumps(host.rgb_zone_configurations, sort_keys=True)
    assert remember_slot_route(host, "front-slot", "", "")
    assert slot_header_targets(host, host.rgb_layout_slots[0]) == []
    assert json.dumps(host.rgb_zone_configurations, sort_keys=True) == before
    host.close()


def test_missing_controller_or_zone_never_falls_back_to_a_different_header():
    host = Host()
    assert remember_slot_route(host, "front-slot", "openrgb:msi", "JARGB 2")
    host.openrgb_devices = [replace(MSI, zones=("JARGB 1",)), HUB]
    assert slot_header_targets(host, replace(SLOT, device_ids=("openrgb:hub",))) == []
    host.openrgb_devices = [HUB]
    assert slot_header_targets(host, SLOT) == []
    assert slot_routes(host)["front-slot"]["zone"] == "JARGB 2"
    host.close()


def test_multi_device_ram_block_is_not_narrowed_by_legacy_single_dimm_route():
    first = OpenRGBDevice(6, "ENE DRAM 1", modes=("Direct",), zones=("Unknown",))
    second = OpenRGBDevice(7, "ENE DRAM 2", modes=("Direct",), zones=("Unknown",))
    host = Host()
    host.openrgb_devices = [first, second]
    host.openrgb_stable_ids = {6: "openrgb:ram-1", 7: "openrgb:ram-2"}
    ram = replace(
        SLOT, position="ram", slot_id="ram", connection="DDR5",
        device_ids=("openrgb:ram-1", "openrgb:ram-2"),
    )
    host.rgb_layout_slots = [ram]
    host.settings.setValue(KEY, json.dumps({
        "ram": {"controller": "openrgb:ram-1", "zone": "Unknown"},
    }))
    assert slot_header_targets(host, ram) == [
        (first, "Unknown", None), (second, "Unknown", None),
    ]
    host.close()


def test_locked_native_only_devices_and_stale_ui_choices_are_not_accepted():
    host = Host()
    host.blocked = {3}
    host.openrgb_devices.append(OpenRGBDevice(5, "Native", modes=("Rainbow",), zones=("GPU",)))
    host.openrgb_stable_ids[5] = "openrgb:native"
    dialog = build_slot_route_dialog(host, SLOT, [])
    controller = dialog.findChild(QComboBox, "slotArgbController")
    assert controller.findData("openrgb:msi") == controller.findData("openrgb:native") == -1
    assert not remember_slot_route(host, "front-slot", "openrgb:msi", "JARGB 1")
    choose(dialog, "openrgb:hub", "Channel B6")
    host.openrgb_devices = []
    dialog.findChild(QPushButton, "slotArgbEditLeds").click()
    assert host.calls == [] and slot_routes(host) == {}
    dialog.reject()
    host.close()


@pytest.mark.parametrize("raw", [None, [], {"x": True}, {"x": {"controller": "usb:1", "zone": "JARGB 1"}},
                               {"x": {"controller": "openrgb:msi", "zone": "\nport"}},
                               {"x": {"controller": "", "zone": "JARGB 1"}},
                               {"x" * 97: {"controller": "", "zone": ""}}])
def test_malformed_persisted_routes_fail_closed(raw):
    assert normalize_slot_routes(raw) == {}


def test_slot_route_limits_and_deleted_block_are_bounded():
    host = Host()
    host.settings.setValue(KEY, json.dumps({f"slot-{i}": {"controller": "", "zone": ""} for i in range(300)}))
    assert len(slot_routes(host)) == 128
    assert not remember_slot_route(host, "front-slot", "openrgb:msi", "JARGB 1")
    assert not remember_slot_route(host, "deleted", "openrgb:msi", "JARGB 1")
    host.settings.setValue(KEY, "invalid json")
    assert slot_routes(host) == {}
    host.close()


def test_gpu_block_uses_existing_gpu_route_authority_not_a_second_binding(monkeypatch):
    host = Host()
    gpu = OpenRGBDevice(2, "Sapphire", device_type="GPU", modes=("External Control", "Rainbow"))
    host.openrgb_devices.append(gpu)
    host.openrgb_stable_ids[2] = "openrgb:gpu"
    host.rgb_layout_slots = [replace(SLOT, position="gpu", device_ids=("openrgb:gpu",))]
    assert remember_slot_route(host, "front-slot", "openrgb:msi", "JARGB 1")
    assert host.rgb_gpu_routes["openrgb:gpu"] == {"controller": "openrgb:msi", "zone": "JARGB 1"}
    assert slot_routes(host) == {}
    assert slot_header_targets(host, host.rgb_layout_slots[0]) == [(MSI, "JARGB 1", gpu)]
    host.rgb_gpu_routes["openrgb:gpu"] = {"controller": "openrgb:hub", "zone": "Channel B6"}
    assert slot_header_targets(host, host.rgb_layout_slots[0]) == [(HUB, "Channel B6", gpu)]
    assert remember_slot_route(host, "front-slot", "", "")
    assert slot_header_targets(host, host.rgb_layout_slots[0]) == []
    host.close()
