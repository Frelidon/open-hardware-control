"""Protect the restored bounded host-widget scan against callback storms."""

from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["OHC_DISABLE_HARDWARE_IO"] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QEvent, QObject, QSettings, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget  # noqa: E402
from modules.ui_performance.v1_1.controller import UiPerformanceController  # noqa: E402


def test_host_widget_scans_are_coalesced_and_ignore_foreign_or_nonwidget_children(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    host = QWidget()
    host.settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    controller = UiPerformanceController(host)
    app.processEvents()
    scans: list[bool] = []
    original_scan = controller._attach_new_tabs

    def scan() -> None:
        scans.append(True)
        original_scan()

    controller._attach_new_tabs = scan
    foreign = QWidget()
    try:
        timer = QTimer(host)
        plain_object = QObject(host)
        foreign_tabs = QTabWidget(foreign)
        app.processEvents()
        assert not controller._tab_scan_pending
        assert not scans
        assert foreign_tabs not in controller.attached_tabs

        late_tabs = [QTabWidget(host) for _ in range(20)]
        assert controller._tab_scan_pending
        app.processEvents()
        assert len(scans) == 1
        assert not controller._tab_scan_pending
        assert all(tabs in controller.attached_tabs for tabs in late_tabs)
        # Keep references until teardown: Qt owns these objects and the test
        # needs their ChildAdded events, not wrapper garbage collection.
        assert timer.parent() is host and plain_object.parent() is host
    finally:
        controller.shutdown()
        host.deleteLater()
        foreign.deleteLater()
        app.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_queued_widget_scan_is_cancelled_with_its_qobject_context(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    host = QWidget()
    host.settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    controller = UiPerformanceController(host)
    app.processEvents()
    scans: list[bool] = []
    controller._attach_new_tabs = lambda: scans.append(True)
    child = QTabWidget(host)
    assert controller._tab_scan_pending
    controller.shutdown()
    host.deleteLater()
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    assert not scans
