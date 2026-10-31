"""Hardware-free regressions for recovery, personal fans and LED preview return."""
import ast
import os
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6.QtCore import QProcess, QTimer
from PySide6.QtWidgets import QComboBox, QPushButton, QSpinBox
from test_slot_argb_routes_342985 import APP, Host, SLOT, MSI, HUB, choose
from modules.rgb_studio.v1_15.engine_recovery import manual_engine_recovery
from modules.rgb_studio.v1_15.fan_profiles import (
    KEY, declared_total, normalize_profiles, profile_for_slot, remember_profile,
)
from modules.rgb_studio.v1_15.fan_profile_editor import FanProfileEditor
from modules.rgb_studio.v1_15.header_preview import HeaderPreview
from modules.rgb_studio.v1_15.slot_route_editor import build_slot_route_dialog
from modules.rgb_studio.v1_15.slot_routes import reported_sources, remember_slot_route

ROOT = Path(__file__).resolve().parents[1]


def actual_conflict_method():
    tree = ast.parse((ROOT / "src/kraken_control.py").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "KrakenControl")
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)
               and n.name in {"openrgb_device_conflict", "openrgb_wiring_conflict"}]
    namespace = {"OpenRGBDevice": object}
    exec(compile(ast.Module(methods, type_ignores=[]), "actual_conflicts", "exec"), namespace)
    return namespace


def test_offline_controller_choices_remain_but_writes_are_disabled(monkeypatch):
    host = Host()
    ns = actual_conflict_method()
    host.openrgb_device_conflict = ns["openrgb_device_conflict"].__get__(host)
    host.openrgb_wiring_conflict = ns["openrgb_wiring_conflict"].__get__(host)
    host.openrgb_server_reachable = False
    host.openrgb_external_server_detected = False
    host.openrgb_quarantined_devices = {}
    host.nzxt_rgb_ready = host.openlinkhub_detected = False
    host.ckb_next_process_ids = ()
    assert reported_sources(host) == [MSI, HUB]
    assert host.openrgb_device_conflict(MSI)
    assert host.openrgb_wiring_conflict(MSI) == ""
    dialog = build_slot_route_dialog(host, SLOT, [])
    choose(dialog, "openrgb:hub", "Channel A1")
    assert dialog.findChild(QComboBox, "slotArgbController").currentData() == "openrgb:hub"
    assert not dialog.findChild(QPushButton, "slotArgbTestLed").isEnabled()
    assert not dialog.findChild(QPushButton, "slotArgbEditLeds").isEnabled()
    assert remember_slot_route(host, "front-slot", "openrgb:hub", "Channel A1")
    # Device quarantine and real ownership conflicts still block wiring choices.
    host.openrgb_quarantined_devices["openrgb:hub"] = "quarantine"
    assert reported_sources(host) == [MSI]
    host.openrgb_server_reachable = True
    APP.processEvents()
    next(t for t in dialog.findChildren(QTimer)).timeout.emit()
    assert dialog.findChild(QComboBox, "slotArgbController").currentData() == ""
    dialog.close()
    host.close()


def test_route_dialog_tracks_inventory_appearing_after_manual_recovery():
    host = Host()
    host.openrgb_devices = []
    host.openrgb_server_reachable = False
    host.restart_rgb_engine_and_refresh = lambda: host.calls.append("manual-recovery")
    dialog = build_slot_route_dialog(host, SLOT, [])
    dialog.findChild(QPushButton, "slotArgbRecoverEngine").click()
    assert host.calls == ["manual-recovery"]
    host.openrgb_devices = [MSI, HUB]
    host.openrgb_server_reachable = True
    dialog.findChildren(QTimer)[0].timeout.emit()
    choose(dialog, "openrgb:msi", "JARGB 3")
    assert dialog.findChild(QPushButton, "slotArgbTestLed").isEnabled()
    dialog.close()
    host.close()


@pytest.mark.parametrize("owned,running", [(False, False), (False, True), (True, False), (True, True)])
def test_manual_recovery_invalidates_busy_inventory_and_never_signals_foreign_engine(owned, running):
    host = Host()
    host.hardware_io_disabled = False
    host.openrgb_discovery_generation = 7
    host.openrgb_status_busy = True
    host.rgb_engine_disabled_by_reset = host.openrgb_engine_crash_quarantined = True
    host.openrgb_sdk_ready_devices = {"old"}
    host.openrgb_engine_owned = owned
    host.openrgb_engine_stop_requested = True
    host.openrgb_server_process = SimpleNamespace(
        state=lambda: QProcess.ProcessState.Running if running else QProcess.ProcessState.NotRunning,
        kill=lambda: host.calls.append("owned-kill"))
    host.stop_openrgb_effect = lambda text: host.calls.append("stop-effect")
    host.stop_managed_rgb_engine = lambda: host.calls.append("stop-owned")
    host.refresh_rgb_studio = lambda: host.calls.append("refresh")
    host.log_message = lambda text: host.calls.append(text)
    manual_engine_recovery(host)
    assert host.openrgb_discovery_generation == 8 and not host.openrgb_status_busy
    assert not host.openrgb_engine_crash_quarantined and not host.openrgb_sdk_ready_devices
    if owned and running:
        assert host.rgb_engine_restart_pending and "stop-owned" in host.calls
        host.findChildren(QTimer)[0].timeout.emit()
        assert "owned-kill" in host.calls
    else:
        assert "refresh" in host.calls
        assert "stop-owned" not in host.calls and "owned-kill" not in host.calls
    host.close()


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
def test_personal_eight_led_fans_black_white_and_dynamic_total(language):
    host = Host(language=language)
    host.settings.setValue("rgb_studio/layout_profile", "flori")
    slot = replace(SLOT, slot_id="fans-front")
    count = QSpinBox(host)
    count.setRange(1, 12)
    count.setValue(2)
    panel = FanProfileEditor(host, slot, count)
    render_dir = os.environ.get("OHC_UI_RENDER_DIR")
    if render_dir:
        panel.resize(540, 320)
        panel.show()
        APP.processEvents()
        assert panel.grab().save(str(Path(render_dir) / f"fan-profile-{language}.png"))
    assert panel.leds.value() == 8 and panel.total() == 16
    assert panel.color.currentData() == "black"
    count.setValue(3)
    assert panel.total() == 24
    panel.color.setCurrentIndex(panel.color.findData("white"))
    assert panel.total() == 24  # Color is metadata, never an electrical count.
    assert remember_profile(host, "fans-front", panel.values())
    assert profile_for_slot(host, slot)["color"] == "white"
    host.settings.setValue("rgb_studio/layout_profile", "other")
    assert profile_for_slot(host, slot)["leds_per_fan"] == 8
    assert profile_for_slot(host, replace(slot, slot_id="other"))["leds_per_fan"] == 0
    host.close()


def test_fan_metadata_validation_persistence_and_no_header_overwrite():
    host = Host()
    before = repr(host.rgb_zone_configurations)
    valid = dict(brand="TZMRIT", model="Interstellar-V2", color="black", leds_per_fan=8)
    assert remember_profile(host, "front-slot", valid)
    assert profile_for_slot(host, SLOT) == valid
    assert repr(host.rgb_zone_configurations) == before and host.calls == []
    for invalid in [True, -1, 513, "8"]:
        assert normalize_profiles({"slot": {**valid, "leds_per_fan": invalid}}) == {}
    assert normalize_profiles({"slot": {**valid, "brand": "x\n"}}) == {}
    assert declared_total(valid, 13) is None
    host.settings.setValue(KEY, "broken")
    assert profile_for_slot(host, SLOT)["leds_per_fan"] == 0
    host.close()


def preview_host():
    host = Host()
    host.current_rgb_design_snapshot = lambda: (1, "design", "wave")
    host.current_rgb_studio_config = lambda: SimpleNamespace(effect_id="wave")
    host.rgb_selected_devices = {"openrgb:msi", "openrgb:hub"}
    host.openrgb_write_enabled = host.openrgb_server_reachable = True
    host.openrgb_external_server_detected = False
    host.backend = SimpleNamespace(_shutting_down=False)
    host.log_message = lambda text: host.calls.append(text)
    host.start_openrgb_effect = lambda: host.calls.append("restore-effect")
    host.apply_openrgb_static = lambda: host.calls.append("restore-static")
    return host


def test_preview_waits_for_test_completion_and_restores_once_without_qt_timer(monkeypatch):
    host = preview_host()
    queued = []
    monkeypatch.setattr(QTimer, "singleShot", lambda delay, context, callback: queued.append(callback))
    preview = HeaderPreview(host)
    preview.start()
    preview.close()
    assert not queued
    assert host.rgb_header_preview_depth == 0
    preview.complete(True)
    preview.close(True)
    assert not queued
    assert host.calls[-1] == "restore-effect"
    host.close()


@pytest.mark.parametrize("blocked", ["explicit_quit_requested", "session_shutdown_requested",
    "exit_hardware_cleanup_done", "openrgb_external_server_detected", "openrgb_engine_crash_quarantined",
    "offline", "disabled", "shutdown", "new-selection", "new-design"])
def test_preview_never_reenables_output_or_overwrites_new_intent(blocked):
    host = preview_host()
    preview = HeaderPreview(host)
    host.rgb_header_preview_depth = 0  # Dialog closed before this delayed callback.
    if blocked == "offline": host.openrgb_server_reachable = False
    elif blocked == "disabled": host.openrgb_write_enabled = False
    elif blocked == "shutdown": host.backend._shutting_down = True
    elif blocked == "new-selection": host.rgb_selected_devices = {"openrgb:msi"}
    elif blocked == "new-design": host.current_rgb_design_snapshot = lambda: (2, "other", "wave")
    else: setattr(host, blocked, True)
    preview.restore()
    assert not host.calls
    host.close()


def test_discovery_and_auto_apply_are_paused_during_pixel_preview():
    tree = ast.parse((ROOT / "src/kraken_control.py").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "KrakenControl")
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)
               and n.name in {"refresh_rgb_studio", "apply_pending_rgb_design"}]
    namespace = {}
    exec(compile(ast.Module(methods, type_ignores=[]), "actual_preview_pause", "exec"), namespace)
    host = SimpleNamespace(rgb_header_preview_depth=1)
    # Both actual methods return before touching inventory or starting writes.
    namespace["refresh_rgb_studio"](host, background=True)
    namespace["apply_pending_rgb_design"](host)


def test_failed_preview_restores_synchronously_but_unused_preview_does_not(monkeypatch):
    queued = []
    monkeypatch.setattr(QTimer, "singleShot", lambda *args: queued.append(args))
    for failed in (False, True):
        host = preview_host()
        preview = HeaderPreview(host)
        if failed:
            preview.start()
            preview.complete(False)
        preview.close()
        assert not queued and host.rgb_header_preview_depth == 0
        if failed:
            assert host.calls[-1] == "restore-effect"
        queued.clear()
        host.close()


def test_fan_total_is_delegated_only_to_the_selected_header(monkeypatch):
    calls = []
    host = Host()
    monkeypatch.setattr("modules.rgb_studio.v1_15.slot_route_editor.configure_argb_header",
                        lambda h, source, zone, **kw: calls.append((source, zone, kw)))
    dialog = build_slot_route_dialog(host, SLOT, [], suggested_count=16)
    choose(dialog, "openrgb:hub", "Channel A1")
    dialog.findChild(QPushButton, "slotArgbEditLeds").click()
    assert calls == [(HUB, "Channel A1", {"gpu": None, "component_name": SLOT.name, "suggested_count": 16})]
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 1"]["leds_per_unit"] == 30
    host.close()


def test_saved_case_fan_count_and_led_model_are_forwarded_automatically(monkeypatch):
    from modules.rgb_studio.v1_15.argb_controls import edit_slot_header
    from modules.rgb_studio.v1_15.fan_profiles import remember_profile
    from modules.rgb_studio.v1_15.slot_routes import remember_slot_route
    calls = []
    host = Host()
    assert remember_profile(host, "front-slot", {
        "brand": "Own", "model": "Eight LED", "color": "black", "leds_per_fan": 8,
    })
    assert remember_slot_route(host, "front-slot", "openrgb:hub", "Channel A1")
    monkeypatch.setattr("modules.rgb_studio.v1_15.argb_controls.configure_argb_header",
                        lambda h, source, zone, **kw: calls.append((source, zone, kw)))
    edit_slot_header(host, "front-slot")
    assert calls == [(HUB, "Channel A1", {
        "gpu": None, "component_name": SLOT.name,
        "suggested_count": 16, "suggested_units": 2,
    })]
    host.close()


def test_unsaved_component_editor_fan_count_is_forwarded_to_led_button(monkeypatch):
    from modules.rgb_studio.v1_15.argb_controls import build_slot_led_button
    calls = []
    host = Host()
    monkeypatch.setattr("modules.rgb_studio.v1_15.argb_controls.edit_slot_header",
                        lambda *args, **kwargs: calls.append((args, kwargs)))
    button = build_slot_led_button(host, "front-slot", led_count=lambda: 32, unit_count=lambda: 4)
    button.click()
    assert calls == [((host, "front-slot"), {"suggested_count": 32, "suggested_units": 4})]
    host.close()


def test_model_total_rejects_sdk_bounds_instead_of_clamping():
    from modules.rgb_studio.v1_15.gpu_led_editor import header_configuration
    zones = [dict(name="Channel A1", current=60, minimum=0, maximum=256, resizable=True)]
    assert header_configuration(zones, {}, "Channel A1", 16)["Channel A1"] == dict(units=1, leds_per_unit=16)
    with pytest.raises(ValueError):
        header_configuration(zones, {}, "Channel A1", 300)
    with pytest.raises(ValueError):
        header_configuration([{**zones[0], "resizable": False}], {}, "Channel A1", 16)


def test_unchanged_fan_bank_keeps_units_instead_of_becoming_one_strip():
    from modules.rgb_studio.v1_15.gpu_led_editor import header_configuration
    zones = [dict(name="Channel A2", current=90, minimum=0, maximum=256, resizable=True)]
    stored = {"Channel A2": dict(units=3, leds_per_unit=30)}
    assert header_configuration(zones, stored, "Channel A2", 90)["Channel A2"] == stored["Channel A2"]
    assert header_configuration(zones, stored, "Channel A2", 60)["Channel A2"] == {
        "units": 3, "leds_per_unit": 20,
    }


def test_existing_topology_repairs_a_previously_flattened_fan_bank():
    from modules.rgb_studio.v1_15.gpu_led_editor import header_configuration
    zones = [dict(name="Channel A2", current=90, minimum=0, maximum=256, resizable=True)]
    stored = {"Channel A2": dict(units=1, leds_per_unit=90)}
    assert header_configuration(zones, stored, "Channel A2", 90, topology_units=3)["Channel A2"] == {
        "units": 3, "leds_per_unit": 30,
    }
