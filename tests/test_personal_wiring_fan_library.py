"""Owner wiring and reusable fan models, without hardware/settings side effects."""
import copy
import json
import os
from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtWidgets import QSpinBox
from test_slot_argb_routes_342985 import APP, Host
from localization_catalog import UI_TRANSLATIONS
from openrgb_integration import OpenRGBDevice
from rgb_devices import flori_rgb_layout_profile
from modules.rgb_studio.v1_15 import fan_library
from modules.rgb_studio.v1_15.argb_controls import slot_header_targets
from modules.rgb_studio.v1_15.argb_store import retain_manual_headers
from modules.rgb_studio.v1_15.fan_profile_editor import FanProfileEditor
from modules.rgb_studio.v1_15.fan_profiles import profile_for_slot
from modules.rgb_studio.v1_15.personal_wiring import COUNTS_KEY, KEY, WIRING, migrate_personal_wiring
from modules.rgb_studio.v1_15.slot_routes import slot_routes


def wiring_host():
    host = Host()
    host.settings.setValue("rgb_studio/layout_profile", "flori")
    host.is_thermalright_cooling = lambda: True
    hub = OpenRGBDevice(4, "Airgoo AG-DRGB16", modes=("Direct",),
                        zones=tuple(f"Channel {bank}{n}" for bank in "AB" for n in range(1, 9)))
    host.openrgb_devices = [hub]
    host.openrgb_sdk_ready_devices = {"openrgb:hub"}
    host.rgb_layout_slots = flori_rgb_layout_profile("thermalright")[1]
    host.rgb_zone_configurations["openrgb:hub"] = {
        zone: dict(units=3, leds_per_unit=30) for zone in hub.zones}
    host.log_message = host.calls.append
    return host, hub


def test_owner_wiring_counts_and_models_migrate_once_preserving_geometry_pwm_and_other_zones():
    host, hub = wiring_host()
    original = copy.deepcopy(host.rgb_layout_slots)
    pwm = copy.deepcopy(host.mainboard_layout_assignments)
    msi = copy.deepcopy(host.rgb_zone_configurations["openrgb:msi"])
    assert migrate_personal_wiring(host)
    assert host.settings.value(KEY) and host.settings.value(COUNTS_KEY)
    for slot in host.rgb_layout_slots:
        previous = next(s for s in original if s.slot_id == slot.slot_id)
        assert (slot.x, slot.y, slot.scale, slot.airflow, slot.device_ids, slot.group_id) == (
            previous.x, previous.y, previous.scale, previous.airflow, previous.device_ids, previous.group_id)
        if slot.slot_id in WIRING:
            port, count, leds, _pwm = WIRING[slot.slot_id]
            assert slot_header_targets(host, slot) == [(hub, f"Channel {port}", None)]
            assert host.rgb_zone_configurations["openrgb:hub"][f"Channel {port}"] == dict(units=count, leds_per_unit=leds)
    assert host.mainboard_layout_assignments == pwm
    assert host.rgb_zone_configurations["openrgb:msi"] == msi
    assert host.rgb_zone_configurations["openrgb:hub"]["Channel A2"] == dict(units=3, leds_per_unit=30)
    radiator = next(s for s in host.rgb_layout_slots if s.slot_id == "radiator-top")
    assert profile_for_slot(host, radiator)["brand"] == "Thermalright"
    assert profile_for_slot(host, radiator)["leds_per_fan"] == 10
    holder = next(s for s in host.rgb_layout_slots if s.slot_id == "gpu-support")
    assert "12 LEDs" in holder.name
    # A later user choice is not continually forced back to a reference size.
    host.rgb_zone_configurations["openrgb:hub"]["Channel B6"] = dict(units=1, leds_per_unit=11)
    host.settings.setValue("rgb_studio/slot_argb_routes_v1", json.dumps({
        **slot_routes(host), "fan-rear": dict(controller="openrgb:hub", zone="Channel A3")}))
    saved = copy.deepcopy(host.settings.data)
    assert not migrate_personal_wiring(host)
    assert host.settings.data == saved
    restored = {"openrgb:hub": {z: dict(units=3, leds_per_unit=30) for z in hub.zones}}
    retain_manual_headers(host, restored)
    assert restored["openrgb:hub"]["Channel B6"]["leds_per_unit"] == 11
    assert restored["openrgb:hub"]["Channel B8"] == dict(units=1, leds_per_unit=8)
    host.close()


@pytest.mark.parametrize("case", ["other-profile", "nzxt", "missing-port", "duplicate-controller", "duplicate-port", "bad-id", "control-id", "control-zone", "long-zone"])
def test_personal_migration_never_guesses_unsupported_or_ambiguous_wiring(case):
    host, hub = wiring_host()
    if case == "other-profile": host.settings.setValue("rgb_studio/layout_profile", "other")
    elif case == "nzxt": host.is_thermalright_cooling = lambda: False
    elif case == "missing-port": host.openrgb_devices = [replace(hub, zones=hub.zones[:-1])]
    elif case == "duplicate-controller": host.openrgb_devices.append(replace(hub, index=5))
    elif case == "duplicate-port": host.openrgb_devices = [replace(hub, zones=(*hub.zones, "Channel B8"))]
    elif case == "control-id": host.openrgb_stable_ids[4] = "openrgb:hub\n"
    elif case == "control-zone": host.openrgb_devices = [replace(hub, zones=(*hub.zones[:-1], "Channel B8\n"))]
    elif case == "long-zone": host.openrgb_devices = [replace(hub, zones=(*hub.zones[:-1], "Channel B8" + " " * 96))]
    else: host.openrgb_stable_ids[4] = "not-openrgb"
    before = copy.deepcopy((host.settings.data, host.rgb_layout_slots, host.rgb_zone_configurations))
    assert not migrate_personal_wiring(host)
    assert (host.settings.data, host.rgb_layout_slots, host.rgb_zone_configurations) == before
    assert host.calls == []
    host.close()


def test_partial_configuration_never_zeros_other_reported_ports_and_completes_later():
    host, hub = wiring_host()
    host.rgb_zone_configurations["openrgb:hub"] = {"Channel B6": dict(units=1, leds_per_unit=12)}
    assert migrate_personal_wiring(host)
    assert not host.settings.value(COUNTS_KEY, False)
    assert host.rgb_zone_configurations["openrgb:hub"] == {"Channel B6": dict(units=1, leds_per_unit=12)}
    host.rgb_zone_configurations["openrgb:hub"] = {z: dict(units=1, leds_per_unit=30) for z in hub.zones}
    assert migrate_personal_wiring(host)
    assert host.settings.value(COUNTS_KEY)
    host.close()


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
def test_custom_fan_library_reusable_across_restart_and_both_editors(language):
    host, _hub = wiring_host()
    host.tr_static = lambda text: UI_TRANSLATIONS[language][text]
    # Use only this synthetic settings store; never touch installed settings.
    count = QSpinBox(host)
    count.setRange(1, 12)
    count.setValue(3)
    slot = next(s for s in host.rgb_layout_slots if s.slot_id == "radiator-top")
    panel = FanProfileEditor(host, slot, count)
    assert panel.save_model.text() == UI_TRANSLATIONS[language]["Modell speichern"]
    assert panel.total() == 30 and panel.brand.currentText() == "Thermalright"
    panel.brand.setEditText("My Fan Brand")
    panel.model.setEditText("Custom Reverse 120")
    panel.leds.setValue(8)
    before = copy.deepcopy(host.rgb_zone_configurations)
    panel.save_model.click()
    assert panel.model.findText("Custom Reverse 120") >= 0
    assert "My Fan Brand" in fan_library.available_brands(host)
    value = panel.values()
    assert value in fan_library.stored_library(host)
    assert host.rgb_zone_configurations == before and host.calls == []
    second = Host(settings=host.settings, language=language)
    fresh = FanProfileEditor(second, slot, count)
    fresh.brand.setEditText("My Fan Brand")
    index = fresh.model.findText("Custom Reverse 120")
    assert index >= 0
    fresh.model.setCurrentIndex(index)
    fresh.model.activated.emit(index)
    assert fresh.leds.value() == 8 and fresh.total() == 24
    models = fan_library.zone_models(second)
    custom = [m for m in models if m.model_id.startswith("custom-fan-")]
    assert len(custom) == 1 and custom[0].leds_per_fan == 8
    assert custom[0].model_id == fan_library.zone_models(host)[-1].model_id
    render_dir = os.environ.get("OHC_UI_RENDER_DIR")
    if render_dir:
        panel.resize(570, 370)
        panel.show()
        APP.processEvents()
        assert panel.grab().save(str(Path(render_dir) / f"custom-fan-{language}.png"))
    second.close()
    host.close()


def test_library_validation_bounds_duplicate_updates_and_corrupt_settings():
    host = Host()
    value = dict(brand="Custom", model="Fan", color="black", leds_per_fan=8)
    for invalid in (True, -1, 513, "8", 0):
        assert not fan_library.remember_model(host, {**value, "leds_per_fan": invalid})
    for field in ("brand", "model"):
        assert not fan_library.remember_model(host, {**value, field: ""})
        assert not fan_library.remember_model(host, {**value, field: "bad\n"})
    assert fan_library.remember_model(host, value)
    assert fan_library.remember_model(host, {**value, "leds_per_fan": 10})
    assert len(fan_library.stored_library(host)) == 1
    assert fan_library.stored_library(host)[0]["leds_per_fan"] == 10
    for n in range(127): assert fan_library.remember_model(host, {**value, "model": f"Fan {n}"})
    assert not fan_library.remember_model(host, {**value, "model": "overflow"})
    assert fan_library.remember_model(host, value)  # Update at capacity remains allowed.
    host.settings.setValue(fan_library.KEY, "broken")
    assert fan_library.stored_library(host) == []
    assert "Thermalright" in fan_library.available_brands(host)
    host.close()
