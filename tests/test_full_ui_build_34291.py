#!/usr/bin/env python3
"""Build every main page with real PySide6 while suppressing hardware I/O."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
temporary = tempfile.TemporaryDirectory(prefix="ohc-full-ui-build-")
temporary_root = Path(temporary.name)
os.environ["XDG_CONFIG_HOME"] = str(temporary_root / "config")
os.environ["XDG_STATE_HOME"] = str(temporary_root / "state")
os.environ["OHC_DESKTOP_DESIGN_CONFIG_DIR"] = str(temporary_root / "desktop-config")
os.environ["OHC_DESKTOP_DESIGN_STATE_DIR"] = str(temporary_root / "desktop-state")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtGui import QColor, QImage  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel  # noqa: E402
import kraken_control as application  # noqa: E402

# A synthetic missing dependency prevents initialize_devices() and all deferred
# hardware discovery. The test covers the complete synchronous UI construction
# that caused the 3.4.29 startup failure.
application.KrakenControl.check_dependencies = lambda self: ["ui-build-no-hardware"]

qt_app = QApplication.instance() or QApplication([])

# Reproduce the real 3.4.29.5 startup: a persisted TRCC media directory
# renders its first preview while the LCD page is built, before log_view exists.
saved_designs = temporary_root / "saved-thermalright-designs"
saved_designs.mkdir()
preview = QImage(32, 32, QImage.Format.Format_RGB32)
preview.fill(QColor("#163452"))
assert preview.save(str(saved_designs / "saved-preview.png"))
settings = QSettings(application.ORG_NAME, application.APP_NAME)
settings.setValue("thermalright/media_directory", str(saved_designs))
settings.sync()

window = application.KrakenControl()
labels = [label.text() for label in window.findChildren(QLabel)]

assert window.tabs.count() == 11
assert application._GIF_SAFETY_TEXT in labels
assert application._ABOUT_SUMMARY_TEXT in labels
assert window.windowTitle().startswith("Open Hardware Control by Frelidon 3.4.29.5 INTERN")
assert window.thermalright_display_studio.current_media_path() == (saved_designs / "saved-preview.png")

window.backend.shutdown()
window.deleteLater()
qt_app.processEvents()
temporary.cleanup()

print("3.4.29.5 full offscreen UI construction restored a saved TRCC directory before the Log page.")
