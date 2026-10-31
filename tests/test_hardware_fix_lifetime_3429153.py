"""A deferred Hardware Fix read must not survive its Qt page."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication, QWidget
from shiboken6 import delete
from modules.hardware_fix.v1_0.page import HardwareFixPanel


def test_initial_status_callback_is_cancelled_when_page_is_deleted(monkeypatch):
    app = QApplication.instance() or QApplication([])
    calls = []
    monkeypatch.setattr(HardwareFixPanel, "refresh_status", lambda self: calls.append(self))
    host = QWidget()
    page = HardwareFixPanel(host, lambda text: text)
    delete(page)
    app.processEvents()
    assert calls == []
    delete(host)
