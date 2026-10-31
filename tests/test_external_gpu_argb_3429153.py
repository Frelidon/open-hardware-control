"""External GPU block routes need no native GPU scan, resize or fake device."""
import copy
import json
import os
from dataclasses import replace
from pathlib import Path
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OHC_DISABLE_HARDWARE_IO", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QDialogButtonBox, QPushButton, QWidget
from localization_catalog import UI_TRANSLATIONS
from openrgb_integration import OpenRGBDevice
from rgb_devices import RGBGroup, RGBLayoutSlot
from rgb_effects import RGBEffectConfig
from modules.pc_case_profiles.v1_5.controller import PcCaseProfilesMixin
from modules.pc_case_profiles.v1_5.profiles import decode_profiles, encode_profiles
from modules.rgb_studio.v1_15.argb_controls import (
    build_case_gpu_setup_button, open_case_gpu_setup, slot_header_targets,
)
from modules.rgb_studio.v1_15.gpu_lighting import GpuLightingMixin
from modules.rgb_studio.v1_15.gpu_routing import gpu_zone_overrides
from modules.rgb_studio.v1_15.gpu_support_sync import pair
from modules.rgb_studio.v1_15.render_plan import build, render
from modules.rgb_studio.v1_15.slot_route_editor import build_slot_route_dialog
from modules.rgb_studio.v1_15.slot_routes import KEY, remember_slot_route, slot_routes

APP = QApplication.instance() or QApplication([])
# Synthetic identity: private controller hashes must not enter release fixtures.
MSI_ID = "openrgb:1111111111111111"
MSI = OpenRGBDevice(3, "MSI MYSTIC LIGHT", device_type="Motherboard", modes=("Direct",),
                    zones=("JAF", "JARGB 1", "JARGB 2", "JARGB 3"))
HUB = OpenRGBDevice(4, "Airgoo", modes=("Direct",), zones=("Channel A1", "Channel B6"))
GPU_SLOT = RGBLayoutSlot("gpu", "Sapphire RX 9070 XT", 1, "group_grafikkarte", "", (), "gpu", .47, .59)
ROUTE = {"controller": MSI_ID, "zone": "JARGB 1"}


class Settings:
    def __init__(self): self.data = {}
    def value(self, key, default=None, **_kwargs): return self.data.get(key, default)
    def setValue(self, key, value): self.data[key] = value
    def sync(self): pass


class Host(GpuLightingMixin, QWidget):
    def __init__(self, language="de"):
        super().__init__()
        self.settings = Settings()
        self.tr_static = lambda source: UI_TRANSLATIONS[language].get(source, source)
        self.openrgb_devices = [MSI, HUB]
        self.openrgb_stable_ids = {3: MSI_ID, 4: "openrgb:hub"}
        self.rgb_layout_slots = [GPU_SLOT]
        self.rgb_layout_selected_slot_id = "gpu"
        self.rgb_gpu_routes = {}
        self.rgb_selected_devices = set()
        self.rgb_groups = [RGBGroup("group_grafikkarte", "GPU")]
        self.rgb_group_assignments = {}
        self.rgb_device_aliases = {}
        self.rgb_group_effect_configs = {"group_grafikkarte": RGBEffectConfig("spinner", "0000ff", "ffffff")}
        self.rgb_zone_configurations = {MSI_ID: {
            "JAF": {"units": 1, "leds_per_unit": 0},
            "JARGB 1": {"units": 1, "leds_per_unit": 30},
            "JARGB 2": {"units": 1, "leds_per_unit": 0},
            "JARGB 3": {"units": 1, "leds_per_unit": 0},
        }}
        self.mainboard_layout_assignments = {}
        self.calls = []
        self.blocked = set()

    def show_error(self, message): self.calls.append(("error", message))
    def selected_openrgb_device(self): return MSI
    def openrgb_device_conflict(self, device): return device.index in self.blocked
    def save_rgb_workspace(self): self.calls.append("save")
    def rebuild_rgb_workspace(self): self.calls.append("refresh")
    def append_log(self, value): self.calls.append(value)


def choose(dialog, controller=MSI_ID, zone="JARGB 1"):
    combo = dialog.findChild(QComboBox, "slotArgbController")
    combo.setCurrentIndex(combo.findData(controller))
    port = dialog.findChild(QComboBox, "slotArgbZone")
    port.setCurrentIndex(port.findData(zone))


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
@pytest.mark.parametrize("entry", ["case", "studio"])
def test_external_gpu_button_opens_existing_localized_header_editor_without_native_gpu(monkeypatch, language, entry):
    host = Host(language)
    before = copy.deepcopy(host.rgb_zone_configurations)
    dialogs = []

    def inspect(dialog):
        dialogs.append(dialog)
        assert dialog.objectName() == "slotArgbRouteDialog"
        assert GPU_SLOT.name in dialog.windowTitle()
        controller = dialog.findChild(QComboBox, "slotArgbController")
        assert controller.findData(MSI_ID) >= 0
        # A cooler drawing or component name must not silently select JARGB 1.
        assert controller.currentData() == ""
        choose(dialog)
        assert dialog.findChild(QComboBox, "slotArgbZone").currentData() == "JARGB 1"
        assert dialog.findChild(QPushButton, "slotArgbEditLeds").text() == UI_TRANSLATIONS[language][
            "LED-Anzahl am ARGB-Anschluss ändern"]
        assert dialog.findChild(QPushButton, "slotArgbEditLeds").isEnabled()
        dialog.reject()
        return QDialog.DialogCode.Rejected

    monkeypatch.setattr(QDialog, "exec", inspect)
    if entry == "case":
        button = build_case_gpu_setup_button(host, "gpu")
        assert button.text() == UI_TRANSLATIONS[language]["Grafikkarte: Steuerweg und LEDs"]
        button.click()
    else:
        host.configure_gpu_lighting()
    assert len(dialogs) == 1
    assert host.calls == [] and slot_routes(host) == {}
    assert host.rgb_selected_devices == set()
    assert host.rgb_zone_configurations == before
    assert host.openrgb_devices == [MSI, HUB]  # No invented Sapphire controller.
    host.close()


def test_external_gpu_route_commit_keeps_counts_and_survives_pc_profile_roundtrip():
    host = Host()
    before = copy.deepcopy(host.rgb_zone_configurations)
    dialog = build_slot_route_dialog(host, GPU_SLOT, [])
    choose(dialog)
    buttons = dialog.findChild(QDialogButtonBox)
    save = next(button for button in buttons.buttons()
                if buttons.buttonRole(button) == QDialogButtonBox.ButtonRole.AcceptRole)
    save.click()
    assert slot_routes(host) == {"gpu": ROUTE}
    assert host.rgb_gpu_routes == {}
    assert host.rgb_selected_devices == {MSI_ID}
    assert host.rgb_layout_slots == [GPU_SLOT] and GPU_SLOT.device_ids == ()
    assert host.rgb_zone_configurations == before
    assert slot_header_targets(host, GPU_SLOT) == [(MSI, "JARGB 1", None)]

    hardware = PcCaseProfilesMixin._profile_hardware_snapshot(host)
    profile = dict(id="user-pc", name="PC", case_id="custom", slots=[], groups=[], hardware=hardware)
    loaded = decode_profiles(encode_profiles([profile]))[0]["hardware"]
    assert loaded["slot_routes"] == {"gpu": ROUTE}
    assert loaded["zone_configurations"][MSI_ID]["JARGB 1"] == {"units": 1, "leds_per_unit": 30}
    assert loaded["zone_configurations"][MSI_ID]["JARGB 2"] == {"units": 1, "leds_per_unit": 0}
    assert loaded["selected_devices"] == [MSI_ID]
    resumed = Host()
    resumed.settings.setValue(KEY, json.dumps(loaded["slot_routes"]))
    resumed.rgb_zone_configurations = loaded["zone_configurations"]
    resumed.rgb_selected_devices = set(loaded["selected_devices"])
    assert slot_header_targets(resumed, GPU_SLOT) == [(MSI, "JARGB 1", None)]
    assert gpu_zone_overrides(resumed, MSI_ID, MSI, RGBEffectConfig()) == {
        "JARGB 1": resumed.rgb_group_effect_configs["group_grafikkarte"]}
    resumed.close(); host.close()


def test_led_editor_delegates_only_to_real_reported_header_no_gpu_command(monkeypatch):
    host = Host()
    delegated = []
    before = copy.deepcopy(host.rgb_zone_configurations)
    monkeypatch.setattr("modules.rgb_studio.v1_15.slot_route_editor.configure_argb_header",
                        lambda *args, **kwargs: delegated.append((args, kwargs)))
    dialog = build_slot_route_dialog(host, GPU_SLOT, [])
    choose(dialog)
    dialog.findChild(QPushButton, "slotArgbEditLeds").click()
    assert delegated == [((host, MSI, "JARGB 1"), {"gpu": None, "component_name": GPU_SLOT.name})]
    assert host.rgb_zone_configurations == before
    host.close()


def test_cached_native_id_can_resolve_exact_saved_gpu_route_without_rediscovery():
    host = Host()
    cached = replace(GPU_SLOT, device_ids=("openrgb:former-gpu",))
    host.rgb_layout_slots = [cached]
    host.rgb_gpu_routes = {"openrgb:former-gpu": ROUTE}
    host.rgb_selected_devices = {MSI_ID}
    assert slot_header_targets(host, cached) == [(MSI, "JARGB 1", None)]
    assert gpu_zone_overrides(host, MSI_ID, MSI, RGBEffectConfig()) == {
        "JARGB 1": host.rgb_group_effect_configs["group_grafikkarte"]}
    # An explicit unassignment takes precedence over the cached native route.
    host.settings.setValue(KEY, json.dumps({"gpu": {"controller": "", "zone": ""}}))
    assert slot_header_targets(host, cached) == []
    assert gpu_zone_overrides(host, MSI_ID, MSI, RGBEffectConfig()) == {}
    host.close()


@pytest.mark.parametrize("failure", ["not-selected", "conflict", "missing-zone", "non-direct", "ambiguous"])
def test_external_gpu_render_fails_closed_without_selected_reported_unambiguous_source(failure):
    host = Host()
    host.settings.setValue(KEY, json.dumps({"gpu": ROUTE}))
    host.rgb_selected_devices = {MSI_ID}
    source = MSI
    if failure == "not-selected": host.rgb_selected_devices.clear()
    elif failure == "conflict": host.blocked.add(MSI.index)
    elif failure == "missing-zone": source = replace(MSI, zones=("JARGB 2",))
    elif failure == "non-direct": source = replace(MSI, modes=("Static",))
    else:
        host.rgb_layout_slots.append(replace(GPU_SLOT, slot_id="another-gpu"))
        host.settings.setValue(KEY, json.dumps({"gpu": ROUTE, "another-gpu": ROUTE}))
    assert gpu_zone_overrides(host, MSI_ID, source, RGBEffectConfig()) == {}
    host.close()


def test_external_gpu_uses_saved_group_and_30_leds_in_existing_full_device_render_plan():
    from modules.pc_case_profiles.v1_5.case_animation import build_specs, frame
    host = Host()
    assert remember_slot_route(host, "gpu", MSI_ID, "JARGB 1")
    baseline = copy.deepcopy((host.settings.data, host.rgb_zone_configurations, host.openrgb_devices))
    default = RGBEffectConfig("static", "ff0000")
    plan = build(host, MSI_ID, MSI, default, 1.5)
    assert plan["gpu_zones"] == ["JARGB 1"]
    assert plan["gpu_roles"] == {"JARGB 1": "gpu"}
    assert plan["overrides"]["JARGB 1"]["effect_id"] == "spinner"
    colors = render(plan, 30, [0, 30, 0, 0])
    assert len(colors) == 30
    host.openrgb_effect_active = True
    host.openrgb_effect_assignments = {MSI_ID: default}
    host.rgb_last_sent_elapsed = host.rgb_gpu_visual_elapsed = 1.5
    specs = build_specs(host, host.rgb_layout_slots, {})
    assert specs["gpu"]["gpu_id"] == "" and specs["gpu"]["targets"] == ((MSI_ID, "JARGB 1", 30),)
    assert frame(host, specs["gpu"]) == tuple(colors)
    assert (host.settings.data, host.rgb_zone_configurations, host.openrgb_devices) == baseline
    host.close()


def test_external_only_gpu_can_pair_with_explicit_support_without_sharing_counts():
    host = Host()
    support = replace(GPU_SLOT, position="gpu-support", slot_id="gpu-support", name="Support")
    host.rgb_layout_slots.append(support)
    host.settings.setValue(KEY, json.dumps({"gpu": ROUTE, "gpu-support": {
        "controller": "openrgb:hub", "zone": "Channel B6"}}))
    host.rgb_selected_devices = {MSI_ID, "openrgb:hub"}
    host.rgb_zone_configurations["openrgb:hub"] = {"Channel B6": {"units": 1, "leds_per_unit": 12}}
    before = copy.deepcopy(host.rgb_zone_configurations)
    linked = pair(host, RGBEffectConfig())
    assert linked["gpu"] == (MSI_ID, "JARGB 1")
    assert linked["support"] == ("openrgb:hub", "Channel B6")
    assert linked["count"] == 30 and linked["config"] == host.rgb_group_effect_configs["group_grafikkarte"]
    assert host.rgb_zone_configurations == before
    host.close()


def test_component_button_keeps_its_explicit_gpu_slot_not_an_unrelated_selected_gpu(monkeypatch):
    host = Host()
    native = OpenRGBDevice(7, "Other GPU", device_type="GPU", modes=("External Control",))
    host.openrgb_devices.append(native)
    host.openrgb_stable_ids[7] = "openrgb:other-gpu"
    other = replace(GPU_SLOT, slot_id="other", device_ids=("openrgb:other-gpu",))
    host.rgb_layout_slots.append(other)
    host.rgb_layout_selected_slot_id = "other"
    routed = []
    monkeypatch.setattr("modules.rgb_studio.v1_15.argb_controls.edit_slot_header",
                        lambda *args, **kwargs: routed.append((args, kwargs)))
    open_case_gpu_setup(host, "gpu")
    assert routed == [((host, "gpu"), {"route_only": True})]
    assert host.calls == []
    host.close()
