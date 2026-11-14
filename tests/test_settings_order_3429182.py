"""Real Qt settings order without reconstructing the hardware-owning window."""
from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OHC_DISABLE_HARDWARE_IO", "1")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QPoint, QProcess, QSettings, QTimer, Qt
from PySide6.QtGui import QFont, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QVBoxLayout, QWidget
from kraken_control import KrakenControl
from modules.setup_features.v1_0.model import feature_choices
from modules.setup_features.v1_0.ownership import FeatureOwnershipMixin
from modules.ui_themes.v1_0.controller import UiThemeMixin

APP = QApplication.instance() or QApplication([])
ORDER = ("background", "design", "language", "display", "temperature", "program",
         "performance", "navigation", "features", "authority", "backends", "access",
         "dependencies", "runtime", "levita_fps", "experimental", "notice")


def recorded(name):
    def callback(self, *arguments): self.calls.append((name, arguments))
    return callback


class SettingsHost(QWidget):
    tr_static = KrakenControl.tr_static
    capture_translation_sources = KrakenControl.capture_translation_sources
    apply_ui_language = KrakenControl.apply_ui_language
    make_percent_slider = staticmethod(KrakenControl.make_percent_slider)
    make_external_link = staticmethod(KrakenControl.make_external_link)
    refresh_authority_status = FeatureOwnershipMixin.refresh_authority_status

    def __init__(self, path):
        super().__init__()
        self.calls = []; self._i18n_widget_sources = {}
        self.settings = QSettings(str(path), QSettings.Format.IniFormat)
        for key, value in {"performance/transitions_enabled": False,
                           "performance/transition_style": "rise",
                           "performance/transition_duration_ms": 550,
                           "performance/ssd_cache_mb": 2048}.items():
            self.settings.setValue(key, value)
        self.theme_mode = "dark"; self.accent_hex = "#00aaff"; self.ui_language = "de"
        self.enabled_features = {choice.key for choice in feature_choices() if choice.default_enabled}
        self.control_authority = {domain: "monitor" for domain in ("rgb", "lcd", "cooling", "gpu", "wallpaper")}
        self.authority_status_labels = {}; self.navigation_user_hidden = {"about"}
        self.display_backend_choice = self.fan_backend_choice = "auto"
        self.temperature_unit = "f"; self.display_auto = True; self.ui_scale_percent = 90
        self.windowed_size_percent = 90; self.display_layout = "16:9"; self.window_start_mode = "windowed"
        self.background_enabled = True; self.background_theme = "Matrix Code Rain · Video"
        self.background_fps = 60; self.background_intensity = 55; self.background_pause_inactive = True
        self.show_undetected_modules = False; self.experimental_desktop_designs_enabled = False
        self.base_font = QFont(APP.font()); self.system_palette = QPalette(APP.palette())
        self.initial_settings = {key: self.settings.value(key) for key in self.settings.allKeys()}
        self.page = KrakenControl.make_settings_tab(self)
        QVBoxLayout(self).addWidget(self.page)
        self.capture_translation_sources()

    def make_module_hero(self, _icon, title, *_args):
        hero = QWidget(); hero.setObjectName("settingsTestHero")
        QVBoxLayout(hero).addWidget(QLabel(title)); return hero

    def populate_window_screen_combo(self):
        self.window_screen_combo.addItem("Test screen", "primary")

    def update_hardware_backend_status(self): pass
    def update_experimental_notice_status(self): pass


for _name in (
    "pick_theme_accent", "set_accent_preset", "apply_design_settings", "on_language_changed",
    "set_feature_enabled", "set_control_authority", "set_navigation_module_enabled", "show_all_navigation_modules",
    "apply_hardware_backend_selection", "on_temperature_unit_changed", "refresh_screen_inventory",
    "apply_display_settings", "on_background_enabled_toggled", "apply_background_settings", "disable_background",
    "set_autostart", "update_status_interval", "set_show_undetected_modules",
    "set_experimental_desktop_designs_enabled", "maybe_show_setup_wizard", "request_application_restart",
    "reset_experimental_warnings", "refresh_dependency_status", "install_missing_dependencies",
    "test_access", "repair_permissions",
):
    setattr(SettingsHost, _name, recorded(_name))


@pytest.fixture
def settings_host(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    palette = QPalette(APP.palette()); font = QFont(APP.font())
    host = SettingsHost(tmp_path / "settings.ini")
    yield host
    host.hide()
    for timer in host.findChildren(QTimer): timer.stop()
    assert all(p.state() == QProcess.ProcessState.NotRunning for p in host.findChildren(QProcess))
    host.deleteLater(); QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    APP.setPalette(palette); APP.setFont(font)


def top_level_widgets(host):
    layout = host.settings_page_scroll.widget().layout()
    return [layout.itemAt(index).widget() for index in range(layout.count()) if layout.itemAt(index).widget()]


def assert_saved_controls(host):
    assert host.accent_hex_input.text() == "#aa77cc"
    assert host.background_enabled_checkbox.isChecked()
    assert host.background_theme_combo.currentData() == "Matrix Code Rain · Video"
    assert host.background_fps_combo.currentData() == 60
    assert host.background_intensity_slider.value() == 55
    assert host.temperature_unit_combo.currentData() == "f"
    assert host.ui_scale_spin.value() == 90
    assert host.page_transition_style_combo.currentData() == "rise"
    assert host.page_transition_duration_combo.currentData() == 550
    assert host.ssd_cache_combo.currentData() == 2048
    assert not host.page_transitions_checkbox.isChecked()
    assert all(combo.currentData() == "monitor" for combo in host.authority_combos.values())
    assert "settings" not in host.navigation_module_checkboxes
    assert {key: host.settings.value(key) for key in host.settings.allKeys()} == host.initial_settings


def test_everyday_settings_first_all_groups_reachable_and_state_retained(settings_host):
    host = settings_host; content = host.settings_page_scroll.widget()
    widgets = top_level_widgets(host); hero, sections = widgets[0], widgets[1:]
    assert hero.objectName() == "settingsTestHero"
    assert len(sections) == len(ORDER) == 17
    assert tuple(section.property("settingsSection") for section in sections) == ORDER
    assert all(isinstance(section, QGroupBox) and section.parentWidget() is content for section in sections)
    original_widgets = tuple(sections)
    host.accent_hex_input.setText("#aa77cc")
    assert not host.calls, "construction/reordering must not emit user actions"
    host.show()
    for theme in ("dark", "light"):
        host.theme_mode = theme; UiThemeMixin.apply_theme(host)
        for language in ("de", "en", "es", "fr"):
            host.apply_ui_language(language, persist=False, log_change=False)
            for width, height in ((2551, 1337), (1440, 1000), (1000, 900)):
                host.resize(width, height); APP.processEvents(); QTest.qWait(5)
                assert tuple(top_level_widgets(host)[1:]) == original_widgets
                assert tuple(section.property("settingsSection") for section in sections) == ORDER
                assert sections[0].title() == host.tr_static("Animierter Hintergrund")
                for previous, following in zip(sections, sections[1:]):
                    assert previous.geometry().bottom() < following.geometry().top()
                host.settings_page_scroll.verticalScrollBar().setValue(0); APP.processEvents()
                viewport = host.settings_page_scroll.viewport()
                assert 0 <= sections[0].mapTo(viewport, QPoint()).y() < viewport.height()
                host.settings_page_scroll.ensureWidgetVisible(sections[-1], 0, 0); APP.processEvents()
                bottom = sections[-1].mapTo(viewport, QPoint(0, sections[-1].height())).y()
                assert 0 < bottom <= viewport.height()
                assert_saved_controls(host)
    assert not host.calls, "language/theme/geometry changes must not apply user settings"
    assert not host.page.grab().isNull()


def test_existing_settings_signals_and_keys_remain_connected(settings_host):
    host = settings_host
    host.background_enabled_checkbox.setChecked(False)
    assert host.calls[-1] == ("on_background_enabled_toggled", (False,))
    host.autostart_checkbox.setChecked(True)
    assert host.calls[-1] == ("set_autostart", (True,))
    host.page_transition_style_combo.setCurrentIndex(host.page_transition_style_combo.findData("fade"))
    assert host.settings.value("performance/transition_style") == "fade"
    host.autostart_minimized_checkbox.setChecked(False)
    assert host.settings.value("app/autostart_minimized", True, type=bool) is False
    assert host.control_authority["gpu"] == "monitor"
    assert "settings" not in host.navigation_module_checkboxes
