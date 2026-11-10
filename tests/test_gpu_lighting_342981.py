"""Sapphire native-mode and explicit ARGB fallback regressions, no hardware writes."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from openrgb_integration import OpenRGBDevice, best_native_mode_for_effect
from modules.rgb_studio.v1_15.gpu_routing import gpu_mode_for_effect, normalize_gpu_routes

GPU = OpenRGBDevice(2, "Sapphire RX 9070 XT", device_type="GPU", modes=(
    "Static", "Rainbow Wave", "Runway", "Spectrum Cycle", "Serial", "External Control", "Off",
), leds=("GPU LED",))
SOURCE = OpenRGBDevice(3, "ARGB controller", modes=("Direct",), zones=("JAF", "JARGB 1", "JARGB 2", "JARGB 3"))
IDS = {2: "openrgb:gpu", 3: "openrgb:source"}


def test_sapphire_designs_use_reported_animated_modes_not_external_or_single_static_led():
    for effect in ("rainbow", "wave", "spinner", "comet", "lightning", "pulse",
                   "breathing", "alternating", "sparkle", "custom_design"):
        mode = best_native_mode_for_effect(GPU, effect)
        assert mode in GPU.modes
        assert mode not in ("External Control", "Off", "Static")
    assert best_native_mode_for_effect(GPU, "static") == "Static"
    assert GPU.led_count == 1


def test_selected_direct_source_keeps_external_capable_gpu_in_external_control():
    assert gpu_mode_for_effect(GPU, "wave", IDS, {}, [SOURCE]) == "External Control"
    assert normalize_gpu_routes(None) == {}


def test_external_sync_requires_explicit_route_and_selected_direct_source():
    routes = {"openrgb:gpu": "openrgb:source"}
    assert gpu_mode_for_effect(GPU, "wave", IDS, routes, [SOURCE]) == "External Control"
    assert gpu_mode_for_effect(GPU, "wave", IDS, routes, []) == "Rainbow Wave"
    non_direct = OpenRGBDevice(3, "not Direct", modes=("Static",))
    assert gpu_mode_for_effect(GPU, "wave", IDS, routes, [non_direct]) == "Rainbow Wave"
    assert gpu_mode_for_effect(GPU, "wave", {2: "openrgb:gpu", 3: "openrgb:changed"}, routes, [SOURCE]) == "Rainbow Wave"


def test_untrusted_profile_route_bounds_and_self_mapping():
    assert normalize_gpu_routes({"openrgb:gpu": "openrgb:gpu", "bad": "openrgb:source",
                                 "openrgb:x": [], "openrgb:long": "openrgb:" + "x" * 97}) == {}
    assert len(normalize_gpu_routes({f"openrgb:{i}": "openrgb:source" for i in range(600)})) == 512


def test_host_profile_and_pc_view_use_the_same_setup_without_fake_gpu_resize():
    root = Path(__file__).resolve().parents[1]
    host = (root / "src/kraken_control.py").read_text()
    controller = (root / "src/modules/pc_case_profiles/v1_5/controller.py").read_text()
    assert '"studio_gpu_routes": dict(self.rgb_gpu_routes)' in host
    assert 'self.restore_gpu_profile_hardware(rgb, startup)' in host
    assert '"rgb_studio/gpu_routes"' in host
    assert 'self.configure_gpu_lighting(openrgb_device)' in controller
    start = host.split('    def _start_openrgb_effect_now(', 1)[1].split('    def send_openrgb_effect_frame', 1)[0]
    assert 'mode = gpu_mode_for_effect(' in start
    assert 'mode = external_control or' not in start


def test_gpu_dialog_routes_led_editor_to_real_controller_and_cancel_is_read_only(monkeypatch):
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QWidget, QDialog, QComboBox, QPushButton
    from modules.rgb_studio.v1_15.gpu_lighting import GpuLightingMixin
    app = QApplication.instance() or QApplication([])

    class Host(GpuLightingMixin, QWidget):
        def __init__(self):
            super().__init__()
            self.openrgb_devices = [GPU, SOURCE]
            self.openrgb_stable_ids = IDS
            self.rgb_gpu_routes = {}
            self.rgb_selected_devices = {"openrgb:gpu"}
            self.rgb_layout_slots = []
            self.saved = 0
            self.edited = None
        def tr_static(self, text): return text
        def selected_openrgb_device(self): return GPU
        def rgb_device_display_name(self, device): return device.name
        def openrgb_device_conflict(self, device): return False
        def save_rgb_workspace(self): self.saved += 1
        def rebuild_rgb_workspace(self): pass
        def configure_openrgb_zones(self, device): self.edited = device

    host = Host()
    def edit(dialog):
        combo = dialog.findChild(QComboBox, "gpuController")
        button = next(b for b in dialog.findChildren(QPushButton)
                      if b.text() == "LED-Anzahl am ARGB-Anschluss ändern")
        assert not button.isEnabled()
        combo.setCurrentIndex(combo.findData("openrgb:source"))
        assert not button.isEnabled()
        zone = dialog.findChild(QComboBox, "gpuZone")
        zone.setCurrentIndex(zone.findData("JARGB 1"))
        assert button.isEnabled()
        button.click()
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(QDialog, "exec", edit)
    monkeypatch.setattr("modules.rgb_studio.v1_15.gpu_lighting.configure_gpu_header", lambda h, g, s, z: setattr(h, "edited", s))
    host.configure_gpu_lighting(GPU)
    assert host.edited is SOURCE
    assert host.saved == 1
    assert host.rgb_gpu_routes == {"openrgb:gpu": {"controller": "openrgb:source", "zone": "JARGB 1"}}
    assert host.rgb_selected_devices == {"openrgb:gpu", "openrgb:source"}

    monkeypatch.setattr(QDialog, "exec", lambda dialog: dialog.reject())
    host.configure_gpu_lighting(GPU)
    assert host.saved == 1
    host.close()
    app.processEvents()
