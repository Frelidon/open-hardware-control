#!/usr/bin/env python3
"""Regression guards for responsive startup and Display Effects selection."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
STUDIO = (ROOT / "src/thermalright_display_ui.py").read_text(encoding="utf-8")
PAGE = (ROOT / "src/modules/display_effects/v1_11/base_page.py").read_text(encoding="utf-8")
PROBE = (ROOT / "src/modules/responsive_startup/v1_0/probe.py").read_text(encoding="utf-8")
CONTROLLER = (ROOT / "src/modules/responsive_startup/v1_0/controller.py").read_text(encoding="utf-8")
WORKER = (ROOT / "src/modules/display_effects/v1_11/worker.py").read_text(encoding="utf-8")


def test_startup_does_not_wait_for_shell_status_or_device_initialization() -> None:
    dependency_body = MAIN.split("def missing_dependency_packages()", 1)[1].split(
        "def refresh_dependency_status", 1,
    )[0]
    assert "subprocess.run" not in dependency_body
    assert "QTimer.singleShot(0, self.initialize_devices)" in MAIN
    assert "detect_cooling_owner()" not in MAIN
    assert "CoolingOwnerStatus(True, True, False)" in CONTROLLER
    assert "self.cooling_owner_probe.request()" in CONTROLLER
    assert "QProcess(self)" in PROBE
    assert "self._pending = True" in PROBE
    assert "isValid(self.process)" in PROBE
    assert "self._shutting_down" in PROBE


def test_deleted_probe_process_ignores_late_request() -> None:
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication
    from modules.responsive_startup.v1_0.probe import CoolingOwnershipProbe

    QApplication.instance() or QApplication([])
    probe = CoolingOwnershipProbe()
    probe.process.deleteLater()
    QCoreApplication.sendPostedEvents(probe.process, QEvent.Type.DeferredDelete)
    assert not probe.busy
    probe.request()
    probe.shutdown()


def test_levita_library_is_deferred_until_after_first_paint() -> None:
    assert 'QTimer.singleShot(80, self, self.load_initial_library)' in STUDIO
    assert 'os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1"' in STUDIO
    assert "library_ready = Signal()" in STUDIO
    assert "self.library_ready.emit()" in STUDIO


def test_display_effects_reuses_graphical_layer2_cards_and_fast_cache_path() -> None:
    assert "def layer2_preview_choices" in STUDIO
    assert "self.layer2_cards_grid" in PAGE
    assert "QToolButton" in PAGE
    assert 'QGroupBox("Effekt")' in PAGE
    assert "self.studio.library_ready.connect(self._refresh_layer2_choices)" in PAGE
    assert "signature == self._layer2_signature" in PAGE
    assert '"-preset", "veryfast"' in WORKER
    assert "known = any(entry.path == candidate" in STUDIO
