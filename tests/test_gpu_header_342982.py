"""GPU JARGB1 routing, independent frames, profile retention and pixel tests."""
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from openrgb_integration import OpenRGBDevice
from rgb_devices import RGBLayoutSlot
from rgb_effects import RGBEffectConfig, render_hex_frame
from modules.rgb_studio.v1_15.gpu_lighting import GpuLightingMixin
from modules.rgb_studio.v1_15.gpu_led_editor import header_configuration, show_gpu_header_editor
from modules.rgb_studio.v1_15.gpu_routing import gpu_mode_for_effect, normalize_gpu_routes, render_zone_frame

GPU = OpenRGBDevice(2, "Sapphire Radeon RX 9070 XT Nitro+", device_type="GPU",
                    modes=("Static", "Rainbow Wave", "External Control"), leds=("GPU",))
MSI = OpenRGBDevice(3, "MSI MYSTIC LIGHT", device_type="Motherboard", modes=("Direct",),
                    zones=("JAF", "JARGB 1", "JARGB 2", "JARGB 3"))
IDS = {2: "openrgb:gpu", 3: "openrgb:msi"}
ROUTE = {"controller": "openrgb:msi", "zone": "JARGB 1"}
ZONES = [{"name": n, "current": 90, "minimum": 0, "maximum": 240, "resizable": True} for n in MSI.zones]


class Settings:
    def __init__(self): self.data = {"rgb_studio/layout_profile": "flori"}
    def value(self, key, default=None, **kwargs): return self.data.get(key, default)
    def setValue(self, key, value): self.data[key] = value


class Host(GpuLightingMixin):
    def __init__(self):
        self.settings = Settings()
        self.openrgb_devices = [GPU, MSI]
        self.openrgb_stable_ids = IDS
        self.rgb_gpu_routes = {"openrgb:gpu": dict(ROUTE)}
        self.rgb_zone_configurations = {"openrgb:msi": {n: {"units": 3, "leds_per_unit": 80} for n in MSI.zones}}
        self.rgb_selected_devices = {"openrgb:gpu"}
        self.rgb_layout_slots = []
        self.saved = 0
    def save_rgb_workspace(self): self.saved += 1
    def openrgb_device_conflict(self, device): return False


def test_schema_migrates_legacy_routes_without_guessing_zone_and_validates_names():
    assert normalize_gpu_routes({"openrgb:gpu": "openrgb:msi"}) == {"openrgb:gpu": {"controller": "openrgb:msi", "zone": ""}}
    assert normalize_gpu_routes({"openrgb:gpu": ROUTE}) == {"openrgb:gpu": ROUTE}
    for zone in ([], "x" * 97, "JARGB\n1"):
        assert normalize_gpu_routes({"openrgb:gpu": {"controller": "openrgb:msi", "zone": zone}}) == {}
    assert gpu_mode_for_effect(GPU, "wave", IDS, {"openrgb:gpu": ROUTE}, [MSI]) == "External Control"
    assert gpu_mode_for_effect(GPU, "wave", IDS, {"openrgb:gpu": {**ROUTE, "zone": "missing"}}, [MSI]) == "Rainbow Wave"


def test_gpu_frame_uses_80_leds_not_960_and_keeps_other_zone_effects():
    config = RGBEffectConfig(effect_id="spinner", primary="ff0000", secondary="0000ff")
    gpu_config = RGBEffectConfig(effect_id="comet", primary="00ff00", secondary="0000ff")
    sizes = (240, 80, 240, 240)
    colors = render_zone_frame(config, sum(sizes), sizes, MSI.zones, {"JARGB 1": gpu_config}, 1.7)
    assert colors[240:320] == render_hex_frame(gpu_config, 80, 1.7)
    assert colors[:240] == render_hex_frame(config, 240, 1.7)
    assert colors[320:560] == render_hex_frame(config, 240, 1.7)
    assert render_zone_frame(config, 90, None, MSI.zones, {}, 1.7) == render_hex_frame(config, 90, 1.7)
    with pytest.raises(ValueError):
        render_zone_frame(config, 960, sizes, MSI.zones, {"JARGB 1": config}, 0)


@pytest.mark.parametrize("startup", [False, True])
def test_old_and_new_profiles_do_not_reset_current_gpu_cabling_or_manual_count(startup):
    host = Host()
    host.rgb_zone_configurations["openrgb:msi"]["JARGB 1"] = {"units": 1, "leds_per_unit": 80}
    host.restore_gpu_profile_hardware({"studio_gpu_routes": {}, "studio_zone_configurations": {
        "openrgb:msi": {n: {"units": 3, "leds_per_unit": 30} for n in MSI.zones}}}, startup)
    assert host.rgb_gpu_routes["openrgb:gpu"] == ROUTE
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 1"] == {"units": 1, "leds_per_unit": 80}
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 2"] == {"units": 3, "leds_per_unit": 30}
    host.select_gpu_route_sources()
    assert "openrgb:msi" in host.rgb_selected_devices
    slot = RGBLayoutSlot("gpu", "my GPU", 1, "gpu", connection="old", device_ids=("openrgb:gpu",), x=0.47, y=0.59)
    host.rgb_layout_slots = [slot]
    host.select_gpu_route_sources()
    assert host.rgb_layout_slots[0].connection == "JARGB 1"
    assert (host.rgb_layout_slots[0].x, host.rgb_layout_slots[0].y, host.rgb_layout_slots[0].count) == (0.47, 0.59, 1)
    code = (Path(__file__).resolve().parents[1] / "src/modules/pc_case_profiles/v1_5/controller.py").read_text()
    section = code.split("    def load_selected_rgb_case_profile", 1)[1].split("    def delete_selected_rgb_case_profile", 1)[0]
    assert 'getattr(self, "select_gpu_route_sources", None)' in section
    host.rgb_gpu_routes = {"openrgb:gpu": {"controller": "", "zone": ""}}
    host.restore_gpu_profile_hardware({"studio_gpu_routes": {"openrgb:gpu": ROUTE}}, startup)
    assert host.rgb_gpu_routes["openrgb:gpu"]["controller"] == ""


def test_personal_confirmed_jargb1_migration_is_once_and_preserves_other_headers():
    host = Host()
    host.rgb_gpu_routes = {"openrgb:gpu": "openrgb:msi"}
    host.migrate_flori_gpu_header()
    assert host.rgb_gpu_routes["openrgb:gpu"] == ROUTE
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 1"] == {"units": 1, "leds_per_unit": 80}
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 2"] == {"units": 3, "leds_per_unit": 80}
    host.rgb_gpu_routes = {"openrgb:gpu": {**ROUTE, "zone": "JARGB 2"}}
    host.migrate_flori_gpu_header()
    assert host.rgb_gpu_routes["openrgb:gpu"]["zone"] == "JARGB 2"
    assert host.saved == 1
    unrelated = Host()
    unrelated.settings.data["rgb_studio/layout_profile"] = "other"
    unrelated.migrate_flori_gpu_header()
    assert unrelated.saved == 0


def test_single_header_configuration_preserves_other_counts_and_real_bounds():
    stored = {n: {"units": 3, "leds_per_unit": 80} for n in MSI.zones}
    actual = header_configuration(ZONES, stored, "JARGB 1", 80)
    assert actual["JARGB 1"] == {"units": 1, "leds_per_unit": 80}
    assert actual["JAF"] == stored["JAF"]
    assert stored["JARGB 1"]["units"] == 3
    for count in (0, -1, 241, 4096):
        with pytest.raises(ValueError): header_configuration(ZONES, stored, "JARGB 1", count)
    with pytest.raises(ValueError): header_configuration(ZONES, stored, "missing", 80)
    with pytest.raises(ValueError): header_configuration([{**z, "resizable": False} for z in ZONES], {}, "JARGB 1", 80)


def test_single_pixel_editor_saves_one_device_and_pixel_offset_without_hardware(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QWidget, QDialog, QSpinBox, QPushButton
    from PySide6.QtCore import QSettings
    app = QApplication.instance() or QApplication([])

    class UiHost(QWidget):
        def __init__(self):
            super().__init__()
            self.openrgb_stable_ids = IDS
            self.settings = QSettings(str(tmp_path / "editor.ini"), QSettings.Format.IniFormat)
            self.rgb_zone_configurations = {}
            self.openrgb_sdk_ready_devices = {"openrgb:msi"}
            self.openrgb_write_enabled = True
            self.openrgb_external_server_detected = False
            self.rgb_test_color = "ff0000"
            self.commands = []
            self.saved = 0
            self.openrgb_client = SimpleNamespace(
                native_mode_command=lambda *args: ["native", *args],
                sdk_color_command=lambda *args, **kwargs: ["sdk", args, kwargs])
        def build_rgb_device_test_commands(self, target_id="", *, exclude_ids=(), only_selected=False):
            assert target_id == "" and only_selected and "openrgb:msi" in exclude_ids and "openrgb:gpu" in exclude_ids
            return [["other-devices-black"]], []
        def tr_static(self, text): return text
        def openrgb_device_conflict(self, device): return False
        def stop_openrgb_effect(self, status): pass
        def show_error(self, text): pytest.fail(text)
        def run_rgb_command_sequence(self, commands, description, **kwargs):
            self.commands = commands
            if kwargs.get("finished"): kwargs["finished"](True)
        def save_rgb_workspace(self): self.saved += 1
        def rebuild_rgb_workspace(self): pass

    host = UiHost()
    def edit(dialog):
        count = dialog.findChild(QSpinBox, "argbLedCount")
        index = dialog.findChild(QSpinBox, "argbTestIndex")
        assert dialog.findChild(QSpinBox, "ledPathUnits") is not None
        count.setValue(80)
        index.setValue(80)
        next(b for b in dialog.findChildren(QPushButton) if b.text() == "Eine LED testen").click()
        next(b for b in dialog.findChildren(QPushButton) if b.text() == "Speichern").click()
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(QDialog, "exec", edit)
    show_gpu_header_editor(host, GPU, MSI, "JARGB 1", ZONES)
    assert host.saved == 1
    assert host.commands[0] == ["other-devices-black"]
    assert host.commands[1][2] == "External Control"
    colors = host.commands[2][1][1]
    assert len(colors) == 350
    assert colors[169] == "ffffff"
    assert colors.count("ffffff") == 1
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 1"] == {"units": 1, "leds_per_unit": 80}
    assert host.rgb_zone_configurations["openrgb:msi"]["JARGB 2"] == {"units": 1, "leds_per_unit": 90}
    assert "openrgb:msi" not in host.openrgb_sdk_ready_devices
    host.close()
    app.processEvents()
