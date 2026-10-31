"""GPU fan ownership and benchmark checks without running a GPU workload."""
from __future__ import annotations

import os
from pathlib import Path
import sys
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from PySide6.QtCore import QProcess, QSettings
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from modules.gpu_control.v1_0.client import LactError, config_equivalent, proposed_config
from modules.gpu_control.v1_0.fan_profile import displayed_curve, fan_preview_verified
from modules.gpu_control.v1_0.page import GpuControlPage, fan_only_change_requested, fan_preview_change_requested
from modules.gpu_control.v1_0.power_policy import (power_cap_allowed, reported_power_bounds,
                                                     sustained_power_excess)
from modules.gpu_control.v1_0.stress import (benchmark_command, benchmark_gpu_environment,
                                              load_sample, vkmark_reported_gpu)


FAN_STATS = {"fan": {"temperature_range": [25, 100], "pwm_max": 254},
             "temps": {"edge": {"current": 39, "crit": 110}}, "busy_percent": 20}
POINTS = ((40, 35), (50, 45), (60, 60), (70, 80), (80, 100))


def test_fan_preview_accepts_change_mapping_without_set_dict_type_error() -> None:
    assert fan_preview_change_requested({"fan_control_settings": POINTS})
    assert fan_preview_change_requested({"fan_control_enabled": True})
    assert not fan_preview_change_requested({"power_cap": 330})
    assert fan_only_change_requested({"fan_control_enabled": True})
    assert fan_only_change_requested({"fan_control_settings": POINTS, "fan_control_enabled": True})
    assert not fan_only_change_requested({"fan_control_settings": POINTS, "power_cap": 330})
    assert not fan_only_change_requested({})


def test_five_point_curve_is_created_from_lact_capabilities() -> None:
    original = {"fan_control_enabled": False, "pmfw_options": {"zero_rpm": True}}
    result = proposed_config(original, {"fan_control_enabled": True,
                                        "fan_control_settings": POINTS}, FAN_STATS)
    assert result["fan_control_enabled"] is True
    assert result["fan_control_settings"]["mode"] == "curve"
    assert result["fan_control_settings"]["curve"] == {
        "40": .35, "50": .45, "60": .6, "70": .8, "80": 1.0}
    assert displayed_curve(result, FAN_STATS) == POINTS
    assert original == {"fan_control_enabled": False, "pmfw_options": {"zero_rpm": True}}
    with pytest.raises(LactError):
        proposed_config(original, {"fan_control_enabled": True,
                                   "fan_control_settings": ((40, 35), (50, 45))}, FAN_STATS)
    with pytest.raises(LactError):
        proposed_config(original, {"fan_control_enabled": True,
                                   "fan_control_settings": ((40, 35), (50, 45), (60, 60),
                                                            (70, 80), (80, 80))}, FAN_STATS)


def test_static_fan_setting_uses_lact_schema_and_rejects_out_of_range_speed() -> None:
    original = {"fan_control_enabled": False, "power_cap": 330.0}
    result = proposed_config(original, {"fan_control_enabled": True,
                                        "fan_control_settings": {"mode": "static", "speed": 100}}, FAN_STATS)
    assert result["fan_control_enabled"] is True
    assert result["fan_control_settings"]["mode"] == "static"
    assert result["fan_control_settings"]["static_speed"] == 1.0
    assert result["fan_control_settings"].get("spindown_delay_ms", 0) == 0
    observed = {"fan_control_enabled": True, "power_cap": 330.0,
                "fan_control_settings": {key: value for key, value in result["fan_control_settings"].items()
                                         if key not in {"spindown_delay_ms", "change_threshold"}}}
    assert config_equivalent(result, observed)
    observed["fan_control_settings"]["static_speed"] = .5
    assert not config_equivalent(result, observed)
    assert original["fan_control_enabled"] is False
    for speed in (-1, 0, 101, True):
        with pytest.raises(LactError):
            proposed_config(original, {"fan_control_enabled": True,
                                       "fan_control_settings": {"mode": "static", "speed": speed}}, FAN_STATS)


def test_newly_enabled_fan_requires_measured_spinup_before_save() -> None:
    assert not fan_preview_verified(newly_enabled=True, baseline_rpm=0, peak_rpm=50, pwm_seen=True)
    assert fan_preview_verified(newly_enabled=True, baseline_rpm=0, peak_rpm=482, pwm_seen=True)
    assert not fan_preview_verified(newly_enabled=True, baseline_rpm=0, peak_rpm=482, pwm_seen=False)
    assert fan_preview_verified(newly_enabled=False, baseline_rpm=600, peak_rpm=600, pwm_seen=True)


def test_ui_can_prepare_curve_without_opening_lact(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])

    class Host(QWidget):
        def __init__(self):
            super().__init__()
            self.settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
        def make_module_hero(self, *_args): return QLabel("GPU")
        def tr_static(self, source): return source
        def log_message(self, _message): pass

    class Lact:
        def devices(self): return [{"id": "gpu-1", "name": "Radeon", "device_type": "Dedicated"}]
        def stats(self, _gpu_id): return FAN_STATS
        def clocks(self, _gpu_id): return {}
        def request(self, *_args): return {}
        def config(self, _gpu_id): return {"fan_control_enabled": False}
        def overdrive_enabled(self): return True

    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim", lambda: (False, "free"))
    host = Host()
    page = GpuControlPage(host)
    page.client = Lact()
    page.refresh()
    assert page.lact_fan.isEnabled()
    assert page.fan_test_button.text() == "Test"
    assert "GPU-Lüfter mit LACT testen" in page.fan_test_button.toolTip()
    assert page.fan_apply_button.text() == "Speichern"
    assert "Getestete Änderung dauerhaft speichern" in page.fan_apply_button.toolTip()
    assert not page.fan_apply_button.isEnabled()
    assert not page.fan_persist_after_test.isChecked()
    assert "Nur ein bestätigter reiner Lüftertest" in page.fan_persist_after_test.toolTip()
    requests = []
    monkeypatch.setattr(page, "start_preview", lambda: requests.append(page._changes()))
    page.prepare_lact_fan()
    assert page.lact_fan.isChecked()
    assert "fan_control_settings" in page._changes()
    assert page.test_button.isEnabled()
    assert len(requests) == 1
    page.fan_mode.setCurrentIndex(page.fan_mode.findData("static"))
    page.fan_static_speed.setValue(100)
    assert page._changes()["fan_control_settings"] == {"mode": "static", "speed": 100}
    page.fan_test_button.click()
    assert len(requests) == 2 and requests[-1]["fan_control_settings"]["speed"] == 100
    page.candidate = proposed_config(page.baseline, page._changes(), page.stats, page.clocks)
    page.tested = True
    page._sync_buttons()
    assert page.fan_apply_button.isEnabled()
    page._apply_fan_preset("quiet")
    assert page.fan_mode.currentData() == "curve"
    assert tuple((temperature.value(), speed.value()) for temperature, speed in page.fan_points) == (
        (40, 35), (50, 35), (60, 45), (72, 65), (85, 95),
    )
    page._set_fan_curve_point(2, 61, 50)
    assert (page.fan_points[2][0].value(), page.fan_points[2][1].value()) == (61, 50)
    page.preview_active = False
    page.prepare_lact_fan = lambda: setattr(page, "preview_active", True)
    page.fan_test_apply_button.click()
    assert page.preview_active
    assert page.fan_persist_after_test.isChecked()
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_fan_cards_reflow_without_height_caps_or_caption_changes(tmp_path: Path) -> None:
    from PySide6.QtCore import QCoreApplication, QEvent, QPoint
    from modules.gpu_control.v1_0.visuals import WrappedCheckBox
    from localization_catalog import UI_TRANSLATIONS
    app = QApplication.instance() or QApplication([])
    class Host(QWidget):
        def __init__(self):
            super().__init__()
            self.settings = QSettings(str(tmp_path / "layout.ini"), QSettings.Format.IniFormat)
        def make_module_hero(self, *_args): return QLabel("GPU")
        def tr_static(self, source): return source
    host = Host()
    page = GpuControlPage(host)
    checkbox = page.fan_persist_after_test
    assert isinstance(checkbox, WrappedCheckBox)
    caption = "Nach bestandenem Test dauerhaft in LACT speichern"
    try:
        for width, position in ((420, (1, 0)), (680, (0, 1))):
            page.fan_page.resize(width, 900)
            page._layout_fan_controls()
            assert page.fan_top_grid.getItemPosition(1)[:2] == position
        assert page.fan_workflow_group.maximumHeight() > 245
        assert page.fan_control_group.maximumHeight() > 245
        assert page.fan_mode.currentText() == "Lüfterkurve"
        for language in ("de", "en", "es", "fr"):
            text = UI_TRANSLATIONS[language][caption]
            checkbox.setText(text)
            wrapped_height = checkbox.heightForWidth(180)
            assert wrapped_height > checkbox.fontMetrics().height()
            checkbox.resize(180, wrapped_height)
            assert checkbox.text() == text
            assert checkbox.hitButton(QPoint(80, wrapped_height - 3))
            assert not checkbox.grab().isNull()
        checkbox.setEnabled(True)
        checkbox.click()
        assert checkbox.isChecked()
    finally:
        page.shutdown()
        host.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_vkmark_is_preferred_and_thermal_fault_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    executable, args = benchmark_command({"vkmark": "/usr/bin/vkmark", "glmark2": "/usr/bin/glmark2"})
    assert executable == "/usr/bin/vkmark"
    assert "--run-forever" in args and "1600x900" in args and "wayland" in args
    assert "shading:shading=phong:duration=10.0" in args
    assert "7680x4320" in benchmark_command({"vkmark": "/usr/bin/vkmark"}, size="7680x4320")[1]
    assert "shading:shading=phong:duration=135.0" in benchmark_command(
        {"vkmark": "/usr/bin/vkmark"}, size="7680x4320", duration_seconds=135)[1]
    assert benchmark_command({"vkcube": "/usr/bin/vkcube"}) == ("", [])
    assert load_sample(FAN_STATS) == (True, "", 20.0)
    hot = {**FAN_STATS, "temps": {"edge": {"current": 96, "crit": 110}}}
    assert load_sample(hot)[0] is False
    assert load_sample({**FAN_STATS, "throttle_info": {"thermal": True}})[0] is False


def test_benchmark_selects_lact_gpu_by_id_instead_of_unstable_ordinal() -> None:
    gpu = "1002:7550-1DA2:E489-0000:03:00.0"
    assert benchmark_gpu_environment(gpu, "/usr/bin/vkmark") == {
        "MESA_VK_DEVICE_SELECT": "1002:7550!"}
    assert benchmark_gpu_environment(gpu, "/usr/bin/gamescope") == {
        "MESA_VK_DEVICE_SELECT": "1002:7550!"}
    assert benchmark_gpu_environment(gpu, "/usr/bin/glmark2") == {"DRI_PRIME": "1002:7550"}
    assert vkmark_reported_gpu("Vendor ID: 0x1002\nDevice ID: 0x7550\n") == "1002:7550"
    assert vkmark_reported_gpu("WARNING: radv is not a conformant Vulkan implementation") is None
    with pytest.raises(ValueError):
        benchmark_gpu_environment("gpu-1", "/usr/bin/vkmark")


def test_power_ceiling_uses_lact_factory_default_until_explicit_unlock() -> None:
    stats = {"power": {"cap_min": 231, "cap_default": 330, "cap_max": 374}}
    bounds = reported_power_bounds(stats)
    assert bounds is not None and bounds.factory == 330
    assert power_cap_allowed(330, bounds, unlocked=False)
    assert not power_cap_allowed(370, bounds, unlocked=False)
    assert power_cap_allowed(370, bounds, unlocked=True)
    assert not power_cap_allowed(400, bounds, unlocked=True)
    assert reported_power_bounds({"power": {"cap_min": 231, "cap_max": 374}}) is None
    assert not sustained_power_excess(342, bounds)
    assert sustained_power_excess(350, bounds)


def test_missing_short_test_benchmark_offers_install_without_gpu_write(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    calls = []

    class Backend:
        def run_async(self, argv, *, callback, timeout):
            calls.append((argv, callback, timeout))

    class Host(QWidget):
        def __init__(self):
            super().__init__()
            self.settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
            self.backend = Backend()
        def make_module_hero(self, *_args): return QLabel("GPU")
        def tr_static(self, source): return source
        def log_message(self, _message): pass

    host = Host()
    page = GpuControlPage(host)
    page.gpu_id = "gpu-1"
    page.baseline = {"power_cap": 200}
    page.overdrive_enabled = True
    monkeypatch.setattr(page, "refresh_ownership", lambda: True)
    monkeypatch.setattr(page, "_load_helper", lambda: ("", []))
    monkeypatch.setattr("modules.gpu_control.v1_0.stress_ui.shutil.which", lambda _name: None)
    page.start_preview()
    page.start_preview()
    assert "vkmark" in page.status.text()
    assert len(calls) == 1
    assert calls[0][0][-1] == "--check-gpu-benchmark-and-install"
    assert not page.preview_active
    assert page.candidate is None
    assert not page.preview_install.isEnabled()
    monkeypatch.setattr("modules.gpu_control.v1_0.stress_ui.shutil.which", lambda _name: "/usr/bin/vkmark")
    calls[0][1](SimpleNamespace(ok=True, combined=""))
    assert page.preview_install.isEnabled()
    assert "bereit" in page.status.text()
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_long_load_can_check_current_gpu_without_saved_tuning(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    writes = []

    class Host(QWidget):
        def __init__(self):
            super().__init__()
            self.settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
        def make_module_hero(self, *_args): return QLabel("GPU")
        def tr_static(self, source): return source
        def log_message(self, _message): pass

    class Lact:
        def devices(self): return [{"id": "1002:7550-0000:03:00.0", "name": "Radeon", "device_type": "Dedicated"}]
        def stats(self, _gpu_id): return FAN_STATS
        def clocks(self, _gpu_id): return {}
        def request(self, *_args): return {}
        def config(self, _gpu_id): return {}
        def overdrive_enabled(self): return True
        def set_config(self, *_args): writes.append("set")
        def pending(self, *_args): writes.append("pending")

    class FakeProcess:
        ProcessState = QProcess.ProcessState
        def __init__(self, _parent): self.running = False
        @staticmethod
        def nullDevice(): return "/dev/null"
        def setStandardOutputFile(self, _path): pass
        def setStandardErrorFile(self, _path): pass
        def setProcessEnvironment(self, environment): self.environment = environment
        def start(self, _program, _args): self.running = True
        def waitForStarted(self, _timeout): return True
        def state(self):
            return self.ProcessState.Running if self.running else self.ProcessState.NotRunning
        def terminate(self): self.running = False
        def waitForFinished(self, _timeout): return True
        def kill(self): self.running = False
        def deleteLater(self): pass
        def readAllStandardOutput(self): return b"Vendor ID: 0x1002\nDevice ID: 0x7550\n"
        def readAllStandardError(self): return b""
        def exitCode(self): return 0

    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim", lambda: (False, "free"))
    monkeypatch.setattr("modules.gpu_control.v1_0.stress_ui.QProcess", FakeProcess)
    host = Host()
    page = GpuControlPage(host)
    page.client = Lact()
    page.refresh()
    assert page.stress_button.isEnabled()
    monkeypatch.setattr(page, "_stress_command", lambda: ("/usr/bin/vkmark", []))
    page.start_stress()
    assert page.stress_process is not None
    assert page.stress_process.environment.value("MESA_VK_DEVICE_SELECT") == "1002:7550!"
    assert not page.stress_process.environment.contains("DRI_PRIME")
    assert page.stress_reference == {}
    assert not page.stress_has_snapshot
    page.stop_stress("Vom Nutzer abgebrochen")
    assert not writes
    page.start_stress()
    page.stress_busy_samples = [12.0, 12.0, 12.0]
    page.stress_peak_load = 12.0
    page.stop_stress()
    assert "Test nicht aussagekräftig" in page.stress_status.text()
    page.start_stress()
    page.stress_busy_samples = [96.0, 98.0, 99.0]
    page.stress_peak_load = 99.0
    page.stop_stress()
    assert "Lasttest bestanden" in page.stress_status.text()
    page.start_stress()
    page.stress_process.running = False
    page._stress_tick()
    assert "Exit 0" in page.stress_status.text()
    assert "Keine OHC-Vorwerte" not in page.stress_status.text()
    assert not writes
    page.deleteLater()
    host.deleteLater()
    app.processEvents()
