#!/usr/bin/env python3
"""Render the real Snapshot Manager page with deterministic demo data."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/images/rendering-evidence/snapshot-manager-3.4.29.128.png"
temporary = tempfile.TemporaryDirectory(prefix="ohc-snapshot-render-")
runtime = Path(temporary.name)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["XDG_CONFIG_HOME"] = str(runtime / "config")
os.environ["XDG_STATE_HOME"] = str(runtime / "state")
os.environ["OHC_DISABLE_HARDWARE_IO"] = "1"
os.environ["OHC_SNAPSHOT_MANAGER_DEMO"] = "1"
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
import kraken_control as application  # noqa: E402


def main() -> int:
    app = QApplication.instance() or QApplication([])
    settings = QSettings(application.ORG_NAME, application.APP_NAME)
    settings.setValue("design/theme", "dark")
    settings.setValue("design/accent", "#20b8ff")
    settings.setValue("display/ui_scale", 100)
    settings.setValue("setup/completed", True)
    settings.sync()
    application.KrakenControl.check_dependencies = lambda self: ["render-no-hardware"]
    window = application.KrakenControl()
    window.resize(1600, 1350)
    window.connection_label.setText("● System bereit")
    window.connection_label.setObjectName("connectionOk")
    window.footer_status.setText("Snapshot-Manager · sichere Demo-Daten")
    window.navigation.setCurrentItem(window.navigation_items["snapshot_manager"])
    window.tabs.setCurrentIndex(window.snapshot_manager_page_index)
    window.show()
    for _ in range(6):
        app.processEvents()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image = window.grab()
    if image.isNull() or not image.save(str(OUTPUT), "PNG"):
        raise SystemExit("Snapshot Manager rendering could not be saved")
    window.snapshot_manager_page.stop_processes()
    window.hide()
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
