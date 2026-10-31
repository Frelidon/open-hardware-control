"""Portion bounds, app-input idle gate, reuse, cancellation and small caches."""
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from PySide6.QtCore import QEvent, QPoint, QSettings, Qt
from PySide6.QtGui import QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QGridLayout, QToolButton, QWidget
from modules.ui_performance.v1_1.gallery_preparation import GalleryPreparation
from modules.ui_performance.v1_1.thumbnails import card_source
from modules.ui_performance.v1_1.cache import preview_cache_path

APP = QApplication.instance() or QApplication([])


class Studio(QWidget):
    def __init__(self):
        super().__init__()
        self.shutdown_started = False
        self.media_cards_grid = QGridLayout(self)
        self.media_card_buttons = {}
        self._media_gallery_columns = 4
        self._media_cards_materialized = False
        self.created = 0
    def current_media_path(self): return None
    def _design_card(self, _entry, **_kwargs):
        self.created += 1
        return QToolButton(self)


def drain(preparation, studio):
    deadline = time.monotonic() + 3
    while preparation.jobs and time.monotonic() < deadline: APP.processEvents()
    assert not preparation.jobs and studio._media_cards_materialized


def test_idle_portions_and_resize_reuse_are_bounded():
    studio = Studio(); preparation = GalleryPreparation(studio)
    entries = [SimpleNamespace(path=f"synthetic:{index}") for index in range(120)]
    preparation.request(entries)
    preparation.advance()
    assert studio.created == 0
    preparation.last_input -= 4
    preparation.advance()
    assert 1 <= studio.created <= 4
    studio.show(); drain(preparation, studio)
    originals = dict(studio.media_card_buttons)
    assert studio.created == 120 and len(originals) == 120
    studio._media_gallery_columns = 6
    preparation.request(entries, reuse=True); drain(preparation, studio)
    assert studio.created == 120 and studio.media_card_buttons == originals
    preparation.shutdown(); studio.close()


def test_new_request_retains_pending_reusable_cards_and_shutdown_cancels():
    studio = Studio(); preparation = GalleryPreparation(studio)
    entries = [SimpleNamespace(path=f"synthetic:{index}") for index in range(20)]
    studio.show(); preparation.request(entries); drain(preparation, studio)
    original = dict(studio.media_card_buttons)
    preparation.request(entries, reuse=True); preparation.advance()
    assert preparation.jobs and studio.created == 20
    preparation.request(entries, reuse=True); drain(preparation, studio)
    assert studio.media_card_buttons == original and studio.created == 20
    preparation.request(entries); preparation.shutdown()
    assert not preparation.timer.isActive() and not preparation.jobs
    studio.close()


def test_input_on_another_page_defers_hidden_preparation():
    window = QWidget(); layout = QGridLayout(window)
    studio = Studio(); other = QWidget(); layout.addWidget(other)
    studio.setParent(window); studio.hide(); window.show()
    preparation = GalleryPreparation(studio)
    preparation.request([SimpleNamespace(path="synthetic:0")])
    preparation.last_input -= 4
    QTest.mouseClick(other, Qt.MouseButton.LeftButton, pos=QPoint(1, 1))
    preparation.advance()
    assert studio.created == 0 and time.monotonic() - preparation.last_input < 1
    preparation.shutdown(); window.close()


def test_host_window_attribute_does_not_break_global_input_filter():
    window = QWidget(); studio = Studio(); studio.setParent(window)
    studio.window = window  # Real LCD studio shadows QWidget.window().
    preparation = GalleryPreparation(studio)
    studio.show(); window.show()
    preparation.last_input -= 4
    QTest.mouseClick(studio, Qt.MouseButton.LeftButton, pos=QPoint(1, 1))
    assert time.monotonic() - preparation.last_input < 1
    preparation.shutdown(); window.close()


def test_small_png_cache_preserves_alpha_and_invalidates_changed_source(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    source = tmp_path / "large.png"
    image = QImage(1600, 720, QImage.Format.Format_ARGB32); image.fill(0x60123456)
    assert image.save(str(source))
    first = card_source(source, settings)
    assert first.width() == 176 and first.height() == 79 and first.hasAlphaChannel()
    target = preview_cache_path("levita-still", source, 2048, ".png")
    assert target.is_file() and not card_source(source, settings).isNull()
    image.fill(0x60998877); assert image.save(str(source))
    os.utime(source, ns=(time.time_ns(), time.time_ns()))
    changed = preview_cache_path("levita-still", source, 2048, ".png")
    assert changed != target
    assert card_source(source, settings).toImage().pixel(0, 0) != first.toImage().pixel(0, 0)
    settings.setValue("performance/ssd_cache_mb", 0)
    assert not card_source(source, settings).isNull()
    assert card_source(tmp_path / "missing.png", settings).isNull()
