"""LACT integration contracts without touching a live GPU or service."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QWidget

from modules.gpu_control.v1_0.client import LactClient, LactError, clock_controls, proposed_config
from modules.gpu_control.v1_0.ownership import coolercontrol_gpu_claim
from modules.gpu_control.v1_0.page import GpuControlPage
from modules.gpu_control.v1_0.snapshot import read_snapshot


def test_lact_local_json_contract(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "lactd.sock"
    seen = []

    class Socket:
        def __enter__(self): return self
        def __exit__(self, *_args): pass
        def settimeout(self, _timeout): pass
        def connect(self, address): seen.append(address)
        def sendall(self, payload): seen.append(json.loads(payload))
        def recv(self, _size):
            return b'{"status":"ok","data":[{"id":"gpu-1","name":"Test GPU"}]}\n'

    monkeypatch.setattr("modules.gpu_control.v1_0.client.socket.socket", lambda *_args: Socket())
    assert LactClient(path).devices() == [{"id": "gpu-1", "name": "Test GPU"}]
    assert seen == [str(path), {"command": "list_devices"}]


def test_unsaved_lact_profile_is_empty_but_malformed_profile_is_rejected(monkeypatch) -> None:
    client = LactClient()
    monkeypatch.setattr(client, "request", lambda *_args: None)
    assert client.config("gpu-1") == {}
    monkeypatch.setattr(client, "request", lambda *_args: [])
    try:
        client.config("gpu-1")
    except LactError as exc:
        assert "invalid GPU configuration" in str(exc)
    else:
        raise AssertionError("Malformed LACT profile accepted")


def test_lact_overdrive_status_is_explicit(monkeypatch) -> None:
    client = LactClient()
    monkeypatch.setattr(client, "request", lambda *_args: {"amdgpu_overdrive_enabled": False})
    assert client.overdrive_enabled() is False
    monkeypatch.setattr(client, "request", lambda *_args: {})
    assert client.overdrive_enabled() is None


def test_overdrive_setup_uses_only_lact_command_after_disabled_status(monkeypatch) -> None:
    client = LactClient()
    seen = []
    monkeypatch.setattr(client, "require_supported_version", lambda: None)
    monkeypatch.setattr(client, "request", lambda command, args=None: seen.append((command, args)) or
                        ({"amdgpu_overdrive_enabled": False} if command == "system_info" else None))
    client.prepare_overdrive()
    assert seen == [("system_info", None), ("enable_overdrive", None)]
    seen.clear()
    monkeypatch.setattr(client, "request", lambda command, args=None: seen.append((command, args)) or
                        {"amdgpu_overdrive_enabled": True})
    try:
        client.prepare_overdrive()
    except LactError:
        pass
    else:
        raise AssertionError("Overdrive setup was accepted when already active")
    assert seen == [("system_info", None)]


def test_proposed_config_bounds() -> None:
    baseline = {"power_cap": 200.0, "max_core_clock": 2000, "fan_control_enabled": False}
    assert proposed_config(baseline, {"power_cap": 210.0},
                           {"power": {"cap_min": 100, "cap_max": 250}})["power_cap"] == 210.0
    try:
        proposed_config(baseline, {"max_core_clock": 2300}, {})
    except LactError as exc:
        assert "trial bound" in str(exc)
    else:
        raise AssertionError("Unsafe clock jump accepted")


RDNA4_CLOCKS = {"table": {"type": "amd", "value": {"kind": "rdna", "data": {
    "current_sclk_range": {"min": None, "max": None},
    "sclk_offset": 0,
    "current_mclk_range": {"min": 97, "max": 1259},
    "od_range": {"sclk": None, "sclk_offset": {"min": -500, "max": 1000},
                 "mclk": {"min": 97, "max": 1500}},
}}}}


def test_rdna4_live_clock_limits_enable_unsaved_offset_and_memory() -> None:
    baseline = {"power_cap": 330.0, "performance_level": "auto"}
    controls = clock_controls(baseline, RDNA4_CLOCKS)
    assert "max_core_clock" not in controls
    assert controls["max_memory_clock"] == (1259, 97, 1500)
    assert controls["gpu_clock_offset_0"] == (0, -500, 1000)
    result = proposed_config(baseline, {"gpu_clock_offset_0": 50,
                                        "max_memory_clock": 1300}, {}, RDNA4_CLOCKS)
    assert result["gpu_clock_offsets"] == {"0": 50}
    assert result["max_memory_clock"] == 1300
    assert baseline == {"power_cap": 330.0, "performance_level": "auto"}
    for change in ({"gpu_clock_offset_0": 101}, {"max_memory_clock": 1350},
                   {"max_memory_clock": 1501}):
        try:
            proposed_config(baseline, change, {}, RDNA4_CLOCKS)
        except LactError:
            pass
        else:
            raise AssertionError(f"Unsafe unsaved RDNA4 change accepted: {change}")


def test_coolercontrol_gpu_assignment_blocks_lact(tmp_path: Path, monkeypatch) -> None:
    from modules.gpu_control.v1_0 import ownership

    class Active:
        coolercontrol_active = True

    monkeypatch.setattr(ownership, "detect_cooling_owner", lambda: Active())
    config = tmp_path / "config.toml"
    modes = tmp_path / "modes.json"
    config.write_text('[devices]\nGPU123 = "amdgpu"\n[device-settings]\nGPU123 = {}\n')
    modes.write_text('{"modes":[]}', encoding="utf-8")
    assert coolercontrol_gpu_claim(config, modes)[0] is False
    config.write_text('[devices]\nGPU123 = "amdgpu"\n[device-settings]\nGPU123 = { fan = "profile" }\n')
    assert coolercontrol_gpu_claim(config, modes)[0] is True
    config.write_text('broken toml = [')
    assert coolercontrol_gpu_claim(config, modes)[0] is True


class Host(QWidget):
    def __init__(self, settings: QSettings):
        super().__init__()
        self.settings = settings
        self.messages = []

    def make_module_hero(self, *_args):
        return QLabel("GPU")

    def tr_static(self, source):
        return source

    def log_message(self, message):
        self.messages.append(message)


class FakeLact:
    def __init__(self, initial):
        self.current = dict(initial)

    def config(self, _gpu_id):
        return dict(self.current)

    def devices(self):
        return [{"id": "gpu-1", "name": "Test GPU"}]

    def overdrive_enabled(self):
        return True

    def stats(self, _gpu_id):
        return {"power": {"cap_min": 100, "cap_default": 220, "cap_max": 250, "cap_current": 200},
                "temps": {"edge": 40}}

    def clocks(self, _gpu_id):
        return RDNA4_CLOCKS

    def request(self, _command, _args):
        return {"gpu": "Test GPU"}

    def set_config(self, _gpu_id, candidate):
        self.current = dict(candidate)
        return 5.0

    def pending(self, _action):
        pass


def test_gpu_dashboard_exposes_live_fan_rpm(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "dashboard.ini"), QSettings.Format.IniFormat))

    class DashboardGpu(FakeLact):
        def stats(self, _gpu_id):
            return {
                "power": {"cap_min": 100, "cap_default": 220, "cap_max": 250,
                          "cap_current": 200, "average": 86},
                "temps": {"edge": {"current": 52}, "junction": {"current": 66}},
                "fan": {"speed_current": 1240, "temperature_range": [25, 100]},
            }

    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim",
                        lambda: (False, "free"))
    page = GpuControlPage(host)
    page.client = DashboardGpu({"power_cap": 200.0})
    page.refresh()
    assert page.gpu_temperature_value.text() == "52 °C"
    assert page.gpu_hotspot_value.text() == "66 °C"
    assert page.gpu_fan_rpm_value.text() == "1.240 RPM"
    assert page.gpu_power_value.text() == "86 W"
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_unsaved_profile_keeps_gpu_metrics_visible_and_tuning_locked(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))

    class NewGpu(FakeLact):
        def __init__(self): super().__init__({})
        def overdrive_enabled(self): return False
        def devices(self):
            return [{"id": "apu", "name": "Integrated", "device_type": "Integrated"},
                    {"id": "gpu-1", "name": "Dedicated", "device_type": "Dedicated"}]

    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim",
                        lambda: (False, "CoolerControl service is inactive"))
    page = GpuControlPage(host)
    page.client = NewGpu()
    page.refresh()
    assert page.devices.currentData() == "gpu-1"
    assert page.metrics.rowCount() > 0
    assert page.hardware.rowCount() > 0
    assert "AMD-Overdrive ist aus" in page.status.text()
    assert "kein GPU-Lüfterkonflikt" in page.owner_status.text()
    assert not page.power.isEnabled()
    assert not page.core.isEnabled()
    assert "Nutze den GPU-Taktversatz" in page.tuning_note.text()
    assert not page.test_button.isEnabled()
    assert page.overdrive_button.isEnabled()
    assert page.free_fan_button.isEnabled()  # live release remains available after external LACT changes
    page.release_gpu_fan()
    assert "bereits freigegeben" in page.status.text()
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_rdna4_page_uses_live_clock_limits_even_without_saved_fields(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim", lambda: (False, "free"))
    page = GpuControlPage(host)
    page.client = FakeLact({"power_cap": 200.0})
    page.refresh()
    assert page.memory.isEnabled() and page.memory.value() == 1259
    assert page.offset.isEnabled() and page.offset.value() == 0
    assert not page.core.isEnabled()
    assert not page.test_button.isEnabled()
    page.offset.setValue(50)
    assert page.test_button.isEnabled()
    assert page._changes() == {"gpu_clock_offset_0": 50}
    assert page.client.current == {"power_cap": 200.0}
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_external_lact_fan_can_be_released_and_profile_reset_is_confirmed(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    initial = {"fan_control_enabled": False, "power_cap": 200.0}

    class TrackingLact(FakeLact):
        def __init__(self):
            super().__init__(initial)
            self.writes = []
        def set_config(self, gpu_id, candidate):
            self.writes.append(dict(candidate))
            return super().set_config(gpu_id, candidate)

    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim", lambda: (False, "free"))
    lact = TrackingLact()
    page = GpuControlPage(host)
    page.client = lact
    page.refresh()
    assert page.free_fan_button.isEnabled()
    assert page.factory_button.isEnabled()

    lact.current = {"fan_control_enabled": True, "fan_control_settings":
                    {"mode": "static", "static_speed": 1.0}, "power_cap": 200.0}
    page.free_fan_button.click()
    assert lact.current["fan_control_enabled"] is False
    assert lact.writes[-1]["fan_control_settings"]["static_speed"] == 1.0
    assert "Firmware" in page.status.text()

    page.refresh()
    lact.current["power_cap"] = 210.0  # stale UI must not clear an external edit
    page.reset_lact_profile()
    assert lact.current["power_cap"] == 210.0
    assert lact.writes[-1] != {}
    page.refresh()
    def edit_during_confirmation(*_args):
        lact.current["power_cap"] = 220.0
        return QMessageBox.StandardButton.Yes
    monkeypatch.setattr("modules.gpu_control.v1_0.reset_ui.QMessageBox.question", edit_during_confirmation)
    page.factory_button.click()
    assert lact.current["power_cap"] == 220.0
    assert lact.writes[-1] != {}
    page.refresh()
    monkeypatch.setattr("modules.gpu_control.v1_0.reset_ui.QMessageBox.question",
                        lambda *_args: QMessageBox.StandardButton.Yes)
    page.factory_button.click()
    assert lact.writes[-1] == {}
    assert lact.current == {}
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_disabled_feature_and_external_owner_block_direct_gpu_reset_and_release(tmp_path: Path, monkeypatch) -> None:
    from PySide6.QtCore import QCoreApplication, QEvent
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "blocked.ini"), QSettings.Format.IniFormat))
    page = GpuControlPage(host)
    page.gpu_id = "gpu-1"
    page.baseline = {"power_cap": 200.0, "fan_control_enabled": True}
    page.overdrive_enabled = True
    calls = []
    class ForbiddenClient:
        def config(self, *_args): calls.append("read"); raise AssertionError("Blocked GPU API read")
        def set_config(self, *_args): calls.append("write"); raise AssertionError("Blocked GPU write")
    page.client = ForbiddenClient()
    monkeypatch.setattr(page, "refresh_ownership", lambda: (_ for _ in ()).throw(AssertionError("Blocked ownership probe")))
    monkeypatch.setattr("modules.gpu_control.v1_0.reset_ui.QMessageBox.question",
                        lambda *_args: (_ for _ in ()).throw(AssertionError("Blocked reset dialog")))
    try:
        for enabled, owner in ((False, "ohc_lact"), (True, "external")):
            host.feature_enabled = lambda _key, value=enabled: value
            host.control_authority = {"gpu": owner}
            page._sync_buttons()
            assert not page.factory_button.isEnabled() and not page.free_fan_button.isEnabled()
            page.reset_lact_profile()
            page.release_gpu_fan()
            assert calls == []
    finally:
        page.shutdown()
        host.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_lact_diagnostics_export_is_explicit_and_private(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    page = GpuControlPage(host)
    target = tmp_path / "lact-log.txt"
    page.gpu_events.setPlainText("GPU-LACT: Lüftermessung · Ist=3852 RPM")
    page.lact_journal.setPlainText("lactd: saving updated config")
    page.copy_gpu_diagnostics("ohc")
    assert QApplication.clipboard().text() == "GPU-LACT: Lüftermessung · Ist=3852 RPM"
    page.copy_gpu_diagnostics("lact")
    assert QApplication.clipboard().text() == "lactd: saving updated config"
    page.copy_gpu_diagnostics("all")
    assert "3852 RPM" in QApplication.clipboard().text()
    assert "saving updated config" in QApplication.clipboard().text()
    assert not target.exists()
    monkeypatch.setattr("modules.gpu_control.v1_0.diagnostics_ui.QFileDialog.getSaveFileName",
                        lambda *_args: (str(target), "Text (*.txt)"))
    page.export_gpu_diagnostics()
    assert "3852 RPM" in target.read_text(encoding="utf-8")
    assert "saving updated config" in target.read_text(encoding="utf-8")
    assert target.stat().st_mode & 0o777 == 0o600
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_saved_gpu_baseline_survives_page_restart(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    host = Host(settings)
    original = {"power_cap": 200.0, "fan_control_enabled": False}
    candidate = {"power_cap": 210.0, "fan_control_enabled": False}
    lact = FakeLact(original)
    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim",
                        lambda: (False, "free"))
    page = GpuControlPage(host)
    page.client = lact
    page.gpu_id = "gpu-1"
    page.baseline = original
    page.stats = lact.stats("gpu-1")
    page.overdrive_enabled = True
    page.candidate = candidate
    page.tested = True
    page.save_tested()
    assert lact.current == candidate
    assert read_snapshot(settings, "gpu-1")["original"] == original
    page.deleteLater()
    second = GpuControlPage(host)
    second.client = lact
    second.gpu_id = "gpu-1"
    second.baseline = candidate
    second.restore_baseline()
    assert lact.current == original
    assert read_snapshot(settings, "gpu-1") is None
    second.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_power_limit_above_lact_default_requires_explicit_unlock(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim", lambda: (False, "free"))
    page = GpuControlPage(host)
    page.client = FakeLact({"power_cap": 200.0})
    page.refresh()
    assert page.power.maximum() == 220
    assert page.power_unlock.isChecked() is False
    assert page._power_candidate_allowed({"power_cap": 240.0}) is False
    page.power_unlock.setChecked(True)
    assert page.power.maximum() == 220
    assert not page.power_unlock.isChecked()
    assert not page.power_unlock_panel.isHidden()
    page.power_unlock_confirm.click()
    assert page.power_unlock.isChecked()
    assert page.power.maximum() == 250
    assert page._power_candidate_allowed({"power_cap": 240.0}) is True
    page.power_unlock.setChecked(False)
    assert page.power.maximum() == 220
    page.client.current["power_cap"] = 240.0
    page.refresh()
    assert page.power.value() == 220
    assert "240" in page.power_default_note.text()
    assert page._changes()["power_cap"] == 220
    assert page.client.current["power_cap"] == 240.0
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_msi_and_asus_openrgb_gpu_inventory_needs_no_argb_route(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    host.openrgb_devices = [
        SimpleNamespace(index=1, name="MSI GeForce RTX", device_type="GPU", supports_direct=True),
        SimpleNamespace(index=2, name="ASUS Aura GPU", device_type="GPU", supports_direct=False),
        SimpleNamespace(index=3, name="MSI Mainboard", device_type="Motherboard", supports_direct=True),
    ]
    page = GpuControlPage(host)
    page.refresh_rgb_lighting_inventory()
    assert page.rgb_devices.count() == 2
    assert [page.rgb_devices.itemData(i) for i in range(2)] == [1, 2]
    assert "Direct" in page.rgb_devices.itemText(0)
    assert "native GPU" in page.rgb_devices.itemText(1)
    page.deleteLater()
    host.deleteLater()
    app.processEvents()


def test_failed_save_health_check_reverts_pending_gpu_change(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    host = Host(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    original = {"power_cap": 200.0, "fan_control_enabled": False}
    candidate = {"power_cap": 210.0, "fan_control_enabled": False}

    class UnhealthyLact(FakeLact):
        def pending(self, action):
            assert action == "revert"
            self.current = dict(original)

        def stats(self, _gpu_id):
            return {"power": {"cap_min": 100, "cap_default": 220, "cap_max": 250},
                    "temps": {}, "busy_percent": 30}

    lact = UnhealthyLact(original)
    monkeypatch.setattr("modules.gpu_control.v1_0.page.coolercontrol_gpu_claim",
                        lambda: (False, "free"))
    page = GpuControlPage(host)
    page.client = lact
    page.gpu_id = "gpu-1"
    page.baseline = original
    page.stats = lact.stats("gpu-1")
    page.overdrive_enabled = True
    page.candidate = candidate
    page.tested = True
    page.save_tested()
    assert lact.current == original
    assert read_snapshot(host.settings, "gpu-1") is None
    assert any("fehlgeschlagen" in message for message in host.messages)
    page.deleteLater()
    host.deleteLater()
    app.processEvents()
