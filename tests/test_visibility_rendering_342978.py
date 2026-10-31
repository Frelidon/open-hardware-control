#!/usr/bin/env python3
"""Regression guards for visibility-bound presentation work."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
RGB_GALLERY = (ROOT / "src/modules/rgb_studio/v1_15/design_gallery.py").read_text(encoding="utf-8")
EFFECTS = (ROOT / "src/modules/display_effects/v1_11/page.py").read_text(encoding="utf-8")
LEVITA = (ROOT / "src/thermalright_display_ui.py").read_text(encoding="utf-8")
WALLPAPER = (ROOT / "src/modules/wallpaper_engine/v1_3/page.py").read_text(encoding="utf-8")
SHELL = (ROOT / "src/desktop_shell.py").read_text(encoding="utf-8")
CHROME = (ROOT / "src/modules/window_chrome/v1_2/chrome.py").read_text(encoding="utf-8")


def test_every_continuous_ui_preview_is_bound_to_visibility() -> None:
    assert "active_page_visible(self, self.tabs" in MAIN
    assert "movie.setPaused(False)" in MAIN and "movie.setPaused(True)" in MAIN
    assert "self.background_widget.set_window_active(window_active)" in MAIN
    assert "if not area.intersects(exposed)" in RGB_GALLERY
    assert "def showEvent" in EFFECTS and "def hideEvent" in EFFECTS
    assert "video.set_active(False)" in EFFECTS
    levita_hide = LEVITA[LEVITA.index("    def hideEvent"):LEVITA.index("    def _relayout_design_galleries")]
    assert "self.layer2_motion_timer.stop()" in levita_hide
    assert "self.hover_preview_timer.stop()" in levita_hide
    assert "self._pause_thumbnail_workers()" in levita_hide
    assert "def _thumbnail_job_visible" in LEVITA
    assert "QRect(position, button.size()).intersects" in LEVITA
    assert "if not self.isVisible() or not self.workshop_list.isVisible()" in WALLPAPER
    assert "visualItemRect(item).intersects" in WALLPAPER
    assert "self.thumbnail_timer.stop()" in WALLPAPER
    assert "self.clock_timer.stop()" in SHELL


def test_hardware_output_timers_are_not_stopped_by_page_navigation() -> None:
    sync = MAIN[MAIN.index("    def sync_active_page_performance"):MAIN.index("    def current_rgb_design_snapshot")]
    assert "openrgb_effect_timer" not in sync
    assert "hardware_lcd_timer" not in sync
    assert "mainboard_fan_timer" not in sync
    assert "cpu_curve_timer" not in sync


def test_window_close_keeps_running_and_tray_quit_owns_orderly_exit() -> None:
    minimize = MAIN[MAIN.index("    def minimize_to_tray"):MAIN.index("    def closeEvent")]
    close_event = MAIN[MAIN.index("    def closeEvent"):MAIN.index("    def show_from_tray")]
    assert "self.hide()" in minimize and "self.showMinimized()" in minimize
    assert "perform_orderly_hardware_exit" not in minimize
    assert "event.ignore()" in close_event
    assert "self.minimize_to_tray(force_tray=True)" in close_event
    assert "perform_orderly_hardware_exit" not in close_event
    assert "self.backend.shutdown()" not in close_event


def test_close_hit_target_reaches_the_top_right_corner() -> None:
    assert 'layout.setContentsMargins(14, 0, 0, 0)' in CHROME
    assert 'self.close_button.setFixedSize(48, 42)' in CHROME
    assert 'button.setProperty("windowControlHitTarget", True)' in CHROME
    control_guard = CHROME[CHROME.index('window_control ='):CHROME.index('local_position =')]
    assert "return False" in control_guard
