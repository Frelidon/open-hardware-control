"""Live Qt content transitions preserve page geometry and quiet navigation."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QSettings
from PySide6.QtWidgets import QApplication, QHBoxLayout, QTabWidget, QTreeWidget, QWidget

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from modules.ui_performance.v1_1.controller import UiPerformanceController
from modules.ui_performance.v1_1.page_transition import transition_duration
from modules.rgb_studio.v1_15.design_gallery import RGBDesignGallery


APP = QApplication.instance() or QApplication([])


@pytest.fixture
def host(tmp_path):
    window = QWidget()
    window.settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    layout = QHBoxLayout(window)
    window.navigation = QTreeWidget(window)
    window.tabs = QTabWidget(window)
    for title in ("first", "second"):
        window.tabs.addTab(QWidget(), title)
    layout.addWidget(window.navigation)
    layout.addWidget(window.tabs)
    window.resize(1000, 650)
    window.show()
    APP.processEvents()
    window.controller = UiPerformanceController(window)
    yield window
    window.controller.shutdown()
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


@pytest.mark.parametrize("style", ["fade", "slide", "rise", "glow"])
def test_transition_targets_real_content_and_restores_position(host, style):
    host.settings.setValue("performance/transition_style", style)
    page = host.tabs.currentWidget()
    original = page.pos()
    navigation_rect = host.navigation.geometry()
    host.controller.play(page)
    overlay = host.controller.overlays[page]
    assert overlay.parentWidget() is page and overlay.isVisible()
    assert host.navigation.viewport() not in host.controller.overlays
    animation = host.controller.animations[page]
    assert animation.duration() == 380
    if style in {"slide", "rise"}:
        assert page.pos() != original
    animation.setCurrentTime(animation.duration())
    assert page.pos() == original and not overlay.isVisible()
    assert host.navigation.geometry() == navigation_rect


def test_rapid_switch_resize_hide_and_disable_cancel_the_previous_transition(host):
    host.settings.setValue("performance/transition_style", "slide")
    first = host.tabs.currentWidget()
    origin = first.pos()
    for _ in range(25):
        host.controller.play(first)
    assert len(host.controller.animations) == 1
    host.tabs.setCurrentIndex(1)
    APP.processEvents()
    assert first.pos() == origin
    second = host.tabs.currentWidget()
    assert set(host.controller.animations) == {second}
    host.controller.play(first)  # queued stale page change
    assert first not in host.controller.animations
    second.resize(second.width() + 1, second.height())
    assert not host.controller.animations
    host.controller.play(second)
    host.hide()
    assert not host.controller.animations
    host.show()
    APP.processEvents()
    host.settings.setValue("performance/transitions_enabled", False)
    host.controller.play(second)
    assert not host.controller.animations


def test_duration_is_bounded_and_suggestions_fill_twelve_cards(host):
    for value, expected in ((220, 220), (550, 550), ("broken", 380), (-1, 380), (99999, 380)):
        host.settings.setValue("performance/transition_duration_ms", value)
        assert transition_duration(host.settings) == expected
    gallery = RGBDesignGallery()
    assert len(set(gallery.visible_indices())) == 12
    for width, columns in ((1200, 6), (800, 4), (400, 2)):
        gallery.resize(width, 800)
        gallery.update_geometry_height()
        assert gallery.column_count() == columns
        assert gallery.minimumHeight() >= (12 // columns) * gallery.card_height
    gallery.deleteLater()
