"""GPU subprofile, presentation and user-artwork regression coverage."""
from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QImage

from modules.gpu_control.v1_0.stress import benchmark_command
from modules.gpu_control.v1_0.stress_window_bridge import kwin_script, valid_request
from modules.gpu_profiles.v1_0 import (
    GPU_MODELS, append_or_replace_profile, config_digest, detect_model,
    load_profiles, normalize_profile, remove_profile, zero_rpm_state,
)
from modules.gpu_profiles.v1_0.artwork import (
    import_transparent_artwork, remove_managed_artwork,
)


def profile(profile_id: str, *, autostart: bool = False, gpu_id: str = "1002:7550") -> dict:
    config = {
        "power_cap": 330,
        "fan_control_enabled": True,
        "fan_control_settings": {"mode": "curve", "zero_rpm": True},
    }
    return {
        "id": profile_id, "name": profile_id, "gpu_id": gpu_id,
        "model_id": "amd-radeon-rx-9070-xt", "orientation": "vertical",
        "artwork": "", "config": config, "config_digest": config_digest(config),
        "verified": True, "activate_at_start": autostart,
        "stress_duration": 60, "stress_size": "7680x4320",
        "stress_presentation": "minimized",
    }


def test_current_amd_and_nvidia_families_are_presentational_only() -> None:
    names = {row["name"] for row in GPU_MODELS}
    assert {"Radeon RX 9070 XT", "Radeon RX 7900 XTX", "GeForce RTX 5090",
            "GeForce RTX 4090"} <= names
    assert detect_model("Sapphire Radeon RX 9070 XT Nitro+")["name"] == "Radeon RX 9070 XT"
    assert all(set(row) == {"id", "vendor", "generation", "name"} for row in GPU_MODELS)


def test_profile_is_exact_gpu_bound_and_preserves_zero_rpm(tmp_path: Path) -> None:
    settings = QSettings(str(tmp_path / "profiles.ini"), QSettings.Format.IniFormat)
    first = profile("quiet", autostart=True)
    clean = normalize_profile(first)
    assert clean is not None
    assert clean["gpu_id"] == "1002:7550"
    assert clean["zero_rpm"] is True
    assert zero_rpm_state(clean["config"]) is True
    assert clean["stress_presentation"] == "minimized"

    second = profile("gaming", autostart=True)
    saved = append_or_replace_profile(settings, first)
    saved = append_or_replace_profile(settings, second)
    assert [row["id"] for row in saved if row["activate_at_start"]] == ["gaming"]
    assert load_profiles(settings) == saved
    assert remove_profile(settings, "gaming")[0]["id"] == "quiet"

    tampered = profile("bad")
    tampered["config"]["power_cap"] = 999
    assert normalize_profile(tampered) is None


@pytest.mark.parametrize("trigger", ("saved_autostart", "main_profile_restore"))
def test_profile_refresh_does_not_outlive_deleted_gpu_page(tmp_path: Path, monkeypatch, trigger) -> None:
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication, QLabel, QWidget
    from shiboken6 import isValid
    from modules.gpu_control.v1_0.page import GpuControlPage
    app = QApplication.instance() or QApplication([])
    class Host(QWidget):
        def __init__(self):
            super().__init__()
            self.settings = QSettings(str(tmp_path / "autostart.ini"), QSettings.Format.IniFormat)
        def make_module_hero(self, *_args): return QLabel("GPU")
        def tr_static(self, source): return source
    host = Host()
    if trigger == "saved_autostart":
        append_or_replace_profile(host.settings, profile("startup", autostart=True))
    calls = []
    # This spy records invalid wrappers without invoking their Qt methods and
    # replaces all discovery. The old unscoped functor records False here.
    monkeypatch.setattr(GpuControlPage, "refresh", lambda page: calls.append(isValid(page)))
    deleted = GpuControlPage(host)
    if trigger == "main_profile_restore":
        assert deleted.baseline is None and not deleted.gpu_profiles
        deleted.restore_main_profile_payload(profile("startup", autostart=True), startup=True)
        assert deleted._pending_main_gpu_profile is not None
    assert any(item["activate_at_start"] for item in deleted.gpu_profiles)
    deleted.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert not isValid(deleted)
    app.processEvents()
    assert calls == []
    # The same persisted profile still triggers exactly one initial refresh
    # when its page remains alive: lifetime safety must not disable autostart.
    if trigger == "main_profile_restore":
        host.settings.clear()
    living = GpuControlPage(host)
    if trigger == "main_profile_restore":
        living.restore_main_profile_payload(profile("startup", autostart=True), startup=True)
    app.processEvents()
    assert calls == [True]
    living.shutdown()
    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_user_artwork_is_normalized_privately_and_original_is_untouched(tmp_path: Path) -> None:
    source = tmp_path / "my-card.webp"
    image = QImage(96, 48, QImage.Format.Format_RGBA8888)
    image.fill(QColor(0, 0, 0, 0))
    image.setPixelColor(20, 20, QColor(25, 170, 240, 220))
    assert image.save(str(source), "WEBP")
    original = source.read_bytes()

    managed = tmp_path / "private" / "gpu-art"
    imported = import_transparent_artwork(source, managed)
    assert imported.parent == managed and imported.suffix == ".png"
    assert source.read_bytes() == original
    assert imported.stat().st_mode & 0o777 == 0o600
    assert not remove_managed_artwork(source, managed)
    assert source.exists()
    assert remove_managed_artwork(imported, managed)
    assert not imported.exists() and source.exists()

    opaque = tmp_path / "opaque.png"
    opaque_image = QImage(32, 32, QImage.Format.Format_RGB32)
    opaque_image.fill(QColor("red"))
    assert opaque_image.save(str(opaque), "PNG")
    with pytest.raises(ValueError, match="alpha"):
        import_transparent_artwork(opaque, managed)


def test_stress_presentation_is_validated_and_pid_bound(monkeypatch) -> None:
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    executable, windowed = benchmark_command(
        {"vkmark": "/usr/bin/vkmark"}, size="7680x4320", presentation="maximized",
    )
    assert executable == "/usr/bin/vkmark"
    assert windowed[:2] == ["--size", "7680x4320"]
    _executable, fullscreen = benchmark_command(
        {"vkmark": "/usr/bin/vkmark"}, size="7680x4320", presentation="fullscreen",
    )
    assert "--fullscreen" in fullscreen and "--size" not in fullscreen
    assert benchmark_command({"vkmark": "/usr/bin/vkmark"}, presentation="invalid") == ("", [])
    scaled_executable, scaled = benchmark_command(
        {"vkmark": "/usr/bin/vkmark", "gamescope": "/usr/bin/gamescope"},
        size="7680x4320", output_size="2560x1400", presentation="maximized",
    )
    assert scaled_executable == "/usr/bin/gamescope"
    assert scaled[:8] == ["-w", "7680", "-h", "4320", "-W", "2560", "-H", "1400"]
    assert scaled[scaled.index("--") + 1:scaled.index("--") + 3] == ["/usr/bin/vkmark", "--fullscreen"]

    assert valid_request(4242, "maximized")
    script = kwin_script(4242, "maximized", "io.github.Frelidon.OHC.GpuStressWindow.test")
    assert "w.pid === pid" in script and "target.setMaximize(true, true)" in script
    assert "workspace.activeWindow" not in script
    with pytest.raises(ValueError):
        kwin_script(1, "maximized", "io.github.Frelidon.OHC.GpuStressWindow.test")
