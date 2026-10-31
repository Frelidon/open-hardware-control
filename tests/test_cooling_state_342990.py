"""Stored intent, fresh ownership, actual-state badges and curve roundtrips."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import pytest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from modules.cooling_state.v1_0.controller import (
    checked_master, closing, requested, restore_requested, sync_master, toggle_dashboard,
)

class Host:
    def __init__(self):
        self.mainboard_control_active = False
        self.mainboard_startup_pending = True
        self.cooling_owner_status_known = False
        self.cooling_owner_status = SimpleNamespace(coolercontrol_active=True)
        self.mainboard_channels = {"pwm6": object()}
        self.callbacks, self.calls, self.badges = [], [], []
        self.ready = self.calibrated = True
        self.mainboard_master_enable = SimpleNamespace(
            blockSignals=lambda value: False, setChecked=lambda value: self.badges.append(value))
    def refresh_cooling_dashboard_summary(self): self.badges.append(self.mainboard_control_active)
    def refresh_cooling_ownership_status(self, callback): self.callbacks.append(callback)
    def fan_backend_write_ready(self): return self.ready
    def toggle_mainboard_master_control(self, enabled, **kwargs):
        self.calls.append((enabled, kwargs))
        assert kwargs.get("owner_checked")
        self.mainboard_control_active = enabled and self.ready and self.calibrated and not self.cooling_owner_status.coolercontrol_active
    def show_error(self, text): self.calls.append(text)
    def tr_static(self, text): return text
    def owner_result(self, conflict=False):
        self.cooling_owner_status_known = True
        self.cooling_owner_status.coolercontrol_active = conflict
        callbacks, self.callbacks = self.callbacks, []
        for callback in callbacks: callback()


def test_pending_start_is_saved_without_claiming_actual_control():
    host = Host()
    restore_requested(host)
    assert requested(host) and not host.mainboard_control_active and not host.calls
    sync_master(host)
    assert not any(host.badges)
    host.owner_result()
    assert host.mainboard_control_active and not host.mainboard_startup_pending
    assert requested(host) and all(host.badges[-2:])


@pytest.mark.parametrize("blocked", ["foreign", "missing", "backend", "uncalibrated"])
def test_restore_keeps_intent_but_never_bypasses_gates(blocked):
    host = Host(); host.owner_result(conflict=blocked == "foreign")
    if blocked == "missing": host.mainboard_channels = {}
    if blocked == "backend": host.ready = False
    if blocked == "uncalibrated": host.calibrated = False
    restore_requested(host)
    assert requested(host) and not host.mainboard_control_active
    assert not any(host.badges)


@pytest.mark.parametrize("action", [toggle_dashboard, checked_master])
def test_explicit_enable_uses_new_result_not_cached_free_status(action):
    host = Host(); host.owner_result()
    action(host)
    assert not host.mainboard_control_active and not host.calls
    host.owner_result(conflict=True)
    assert not host.mainboard_control_active


@pytest.mark.parametrize("flag", ["explicit_quit_requested", "session_shutdown_requested", "exit_cleanup_in_progress", "exit_hardware_cleanup_done"])
def test_late_owner_result_does_not_enable_during_exit(flag):
    host = Host(); toggle_dashboard(host)
    setattr(host, flag, True)
    assert closing(host)
    host.owner_result()
    assert not host.calls and not host.mainboard_control_active


def test_newer_action_invalidates_old_owner_callback():
    host = Host(); toggle_dashboard(host)
    host.cooling_dashboard_request += 1
    host.owner_result()
    assert not host.calls


def test_actual_settings_methods_preserve_pending_master_and_quiet_profiles(tmp_path):
    from PySide6.QtCore import QSettings
    tree = ast.parse((ROOT / "src/kraken_control.py").read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "KrakenControl")
    functions = [node for node in cls.body if isinstance(node, ast.FunctionDef)
                 and node.name in {"save_mainboard_fan_settings", "restore_mainboard_fan_settings"}]
    queued = []
    namespace = {"json": json, "QTimer": SimpleNamespace(singleShot=lambda _delay, callback: queued.append(callback))}
    exec(compile(ast.Module(functions, type_ignores=[]), "actual-settings", "exec"), namespace)
    host = Host()
    host.settings = QSettings(str(tmp_path / "roundtrip.ini"), QSettings.Format.IniFormat)
    profiles = {"pwm6": {"preset": "quiet", "enabled": True, "calibrated": True,
                         "curve": [[30, 25], [60, 38]], "source": "cpu"}}
    host.mainboard_fan_profiles = profiles
    host.mainboard_layout_assignments = {"pwm6": "front"}
    host.save_mainboard_fan_settings = namespace["save_mainboard_fan_settings"].__get__(host)
    host.discover_mainboard_fans = lambda **_kwargs: host.save_mainboard_fan_settings()
    host.log_message = lambda _message: None
    host.save_mainboard_fan_settings()
    namespace["restore_mainboard_fan_settings"](host)
    assert host.settings.value("mainboard_fans/master_enabled", False, type=bool)
    assert host.mainboard_fan_profiles == profiles
    assert host.mainboard_layout_assignments == {"pwm6": "front"}
    assert len(queued) == 1
    queued[0]()
    assert not host.mainboard_control_active and host.callbacks
    host.owner_result()
    host.save_mainboard_fan_settings()
    assert json.loads(host.settings.value("mainboard_fans/profiles")) == profiles
