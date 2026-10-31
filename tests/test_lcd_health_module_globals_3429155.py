"""Real bound LCD health callbacks must resolve the canonical device import."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["OHC_DISABLE_HARDWARE_IO"] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QCoreApplication, QEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QGroupBox, QLabel  # noqa: E402
from modules.levita_daemon_health.v1_1 import PlaybackRecoveryPolicy  # noqa: E402


@pytest.fixture
def health_page(monkeypatch):
    app = QApplication.instance() or QApplication([])
    import thermalright_display_ui as display_ui

    # Initialize a genuine Qt instance without its gallery/process constructor.
    # The bound class method retains the actual module globals: in particular,
    # neither a copied AST namespace nor a test-injected device key can hide
    # the startup NameError seen in the recurring healthy-status callback.
    page = display_ui.ThermalrightDisplayStudio.__new__(display_ui.ThermalrightDisplayStudio)
    QGroupBox.__init__(page, "LCD health regression")
    page.playback_health_status = QLabel(page)
    page.playback_health_probe_active = True
    page.playback_last_confirmed_at = 0.0
    page.playback_recovery_policy = PlaybackRecoveryPolicy(consecutive_failures=1, recovery_attempts=2)

    def forbidden(*_args, **_kwargs):
        pytest.fail("A healthy read-only response must not probe processes or recover hardware")

    monkeypatch.setattr(display_ui, "find_trcc_daemon_memory", forbidden)
    page._request_playback_reapply = forbidden
    try:
        yield page, display_ui
    finally:
        page.deleteLater()
        QCoreApplication.sendPostedEvents(page, QEvent.Type.DeferredDelete)
        app.processEvents()


@pytest.mark.parametrize("ubuntu", [True, False])
@pytest.mark.parametrize("animated", [True, False])
def test_real_healthy_callback_resolves_device_key_for_video_and_static(health_page, ubuntu, animated):
    page, display_ui = health_page
    import thermalright_display as canonical

    page.ubuntu_runtime = ubuntu
    page.stream_animated = animated
    callback = page._playback_health_finished
    assert callback.__func__ is display_ui.ThermalrightDisplayStudio._playback_health_finished
    assert callback.__func__.__globals__ is vars(display_ui)
    assert callback.__func__.__globals__["THERMALRIGHT_DEVICE_KEY"] is canonical.THERMALRIGHT_DEVICE_KEY
    output = (
        f"{canonical.THERMALRIGHT_DEVICE_KEY}: playing frame 2/20"
        if animated else json.dumps({"lcd_devices": [{
            "key": canonical.THERMALRIGHT_DEVICE_KEY, "current_theme": "synthetic-layout",
        }]})
    )
    # Exercise successive periodic successes without waiting or starting TRCC.
    for _ in range(8):
        page.playback_health_probe_active = True
        callback(True, output)
        assert not page.playback_health_probe_active
        assert page.playback_last_confirmed_at > 0
        assert page.playback_recovery_policy.consecutive_failures == 0
        assert "Wiedergabe aktiv" in page.playback_health_status.text()
    assert page.playback_recovery_policy.recovery_attempts == 0
    assert page.playback_health_status.text().endswith("0/3")
