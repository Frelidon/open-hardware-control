#!/usr/bin/env python3
"""Build every main page with real PySide6 while suppressing hardware I/O."""

from __future__ import annotations

import os
import atexit
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
temporary = tempfile.TemporaryDirectory(prefix="ohc-full-ui-build-")
temporary_root = Path(temporary.name)
os.environ["XDG_CONFIG_HOME"] = str(temporary_root / "config")
os.environ["XDG_STATE_HOME"] = str(temporary_root / "state")
os.environ["OHC_DESKTOP_DESIGN_CONFIG_DIR"] = str(temporary_root / "desktop-config")
os.environ["OHC_DESKTOP_DESIGN_STATE_DIR"] = str(temporary_root / "desktop-state")
os.environ["OHC_DISABLE_HARDWARE_IO"] = "1"
os.environ["OHC_WALLPAPER_STEAM_LIBRARY"] = str(temporary_root / "Steam")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QCoreApplication, QEvent, QProcess, QSettings, QSize, Qt, QTimer  # noqa: E402
from PySide6.QtGui import QAction, QColor, QImage, QPalette, QPixmap  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QAbstractButton, QApplication, QComboBox, QGraphicsView, QGroupBox,
    QLabel, QLineEdit, QMenu, QSizePolicy, QTableWidget,
)
import kraken_control as application  # noqa: E402
from cooling_ownership import CoolingOwnerStatus  # noqa: E402
from modules.localization.v1_0 import de, en, es, fr  # noqa: E402
from modules.localization.v1_0.policy import (  # noqa: E402
    interactive_text_needs_translation, translated_control_text,
)
from modules.wallpaper_engine.v1_3.library import WallpaperEntry  # noqa: E402
from modules.application_shutdown.v1_1.qt_processes import stop_remaining  # noqa: E402
from shiboken6 import isValid  # noqa: E402

# A synthetic missing dependency prevents initialize_devices() and all deferred
# hardware discovery. The test covers the complete synchronous UI construction
# that caused the 3.4.29 startup failure.
application.KrakenControl.check_dependencies = lambda self: ["ui-build-no-hardware"]

qt_app = QApplication.instance() or QApplication([])


def dispose_window(host: application.KrakenControl) -> None:
    """Reap this test window before the shared Qt application runs other tests."""
    host.settings.setValue("setup/completed", True)
    host.settings.setValue("dependencies/desktop_design_offer_330", True)
    studio = host.thermalright_display_studio
    # The test has exercised startup intent but must not let its delayed retry
    # outlive the window.  Quiesce UI-only owners without firmware restoration.
    host.background_widget.media_background.shutdown()
    studio.shutdown_started = True
    studio.startup_apply_active = False
    studio.thumbnail_shutting_down = True
    studio.media_preview.shutdown()
    studio.lcd_runtime.shutdown()
    studio.game_activity.shutdown()
    studio.gallery_preparation.shutdown()
    # Resolve queued startup callbacks while their widgets are still alive.
    qt_app.processEvents()
    for timer in host.findChildren(QTimer):
        timer.stop()
    host.snapshot_manager_page.stop_processes()
    host.process_runtime.shutdown()
    host.ui_performance.shutdown()
    host.backend.shutdown()
    stop_remaining(host)
    assert all(
        process.state() == QProcess.ProcessState.NotRunning
        for process in host.findChildren(QProcess)
    )
    host.deleteLater()
    # processEvents() alone does not guarantee that Qt handles DeferredDelete
    # without a running outer event loop.  Otherwise periodic probe timers
    # survive this module and can start helpers during unrelated pytest tests.
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert not isValid(host)


# Reproduce startup with a persisted TRCC media directory and editable data
# blocks, before log_view exists.
# renders its first preview while the LCD page is built, before log_view exists.
saved_designs = temporary_root / "saved-thermalright-designs"
saved_designs.mkdir()
preview = QImage(32, 32, QImage.Format.Format_RGB32)
preview.fill(QColor("#163452"))
assert preview.save(str(saved_designs / "saved-preview.png"))
second_preview = QImage(32, 32, QImage.Format.Format_RGB32)
second_preview.fill(QColor("#b24a21"))
assert second_preview.save(str(saved_designs / "second-preview.png"))
duplicate_dir = saved_designs / "alt" / "copied-designs"
duplicate_dir.mkdir(parents=True)
assert preview.save(str(duplicate_dir / "saved-preview.png"))
live_theme = saved_designs / "theme1600720l" / "LiveTheme"
live_theme.mkdir(parents=True)
(live_theme / "config1.dc").write_bytes(b"live values")
(live_theme / "trcc.json").write_text(
    json.dumps(
        {
            "name": "LiveTheme",
            "width": 1600,
            "height": 720,
            "elements": [
                {
                    "type": "metric",
                    "metric": "cpu_usage",
                    "text": "CPU",
                    "format": "CPU {value:.0f}%",
                    "x": 120,
                    "y": 160,
                    "size": 48,
                    "color": "#ffffff",
                }
            ],
        }
    )
    + "\n",
    encoding="utf-8",
)
theme_preview = QImage(1600, 720, QImage.Format.Format_RGB32)
theme_preview.fill(QColor("#102a44"))
assert theme_preview.save(str(live_theme / "Theme.png"))
theme_overlay = QImage(1600, 720, QImage.Format.Format_RGBA8888)
theme_overlay.fill(QColor(0, 0, 0, 0))
theme_overlay.setPixelColor(100, 100, QColor("#55ccff"))
assert theme_overlay.save(str(live_theme / "01.png"))
settings = QSettings(application.ORG_NAME, application.APP_NAME)
settings.setValue("thermalright/media_directory", str(saved_designs))
settings.setValue("thermalright/brightness", 0)
# The UI contract below is specifically the Levita cooling lane. Keep it
# deterministic on hardware-free CI instead of inheriting the host's USB set.
settings.setValue("cooling/hardware_kind", application.LEVITA_COOLER_KEY)
settings.setValue("navigation/hidden", json.dumps(["settings", "about"]))
settings.sync()

window = application.KrakenControl()
atexit.register(lambda: dispose_window(window) if isValid(window) else None)
# Old preferences and both editing entrances must retain the Settings anchor.
assert window.navigation_user_hidden == {"about"}
assert "settings" not in window.navigation_module_checkboxes
window.set_navigation_module_enabled("settings", False)
assert not window.nav_settings.isHidden()
assert "settings" not in json.loads(window.settings.value("navigation/hidden"))
window.toggle_navigation_customization()
assert not window.nav_settings.flags() & Qt.ItemFlag.ItemIsUserCheckable
assert window.nav_settings.data(1, Qt.ItemDataRole.CheckStateRole) is None
window.toggle_navigation_customization()
window.navigation_user_hidden.add("settings")
window.update_navigation_visibility()
assert "settings" not in window.navigation_user_hidden and not window.nav_settings.isHidden()
window.show_all_navigation_modules()
from modules.profile_bundle.v1_0.controller import snapshot as bundle_snapshot
from modules.profile_bundle.v1_0.archive import json_bytes as bundle_json_bytes
complete_snapshot = bundle_snapshot(window)
assert bundle_json_bytes(complete_snapshot)
assert complete_snapshot["settings"] and complete_snapshot["profiles"]
assert "rgb_studio/layout_slots" in complete_snapshot["settings"]
labels = [label.text() for label in window.findChildren(QLabel)]

# Every interactive caption built by the real UI must be present atomically in
# English, Spanish and French. Technical identifiers and proper product/design
# names are deliberately excluded by the narrow production policy.
interactive_sources: set[str] = set()
interactive_types = (QAbstractButton, QComboBox, QGroupBox, QLineEdit, QMenu, QTableWidget, QAction)
for obj, source_record in window._i18n_widget_sources.items():
    if not isinstance(obj, interactive_types) and obj is not window.tabs:
        continue
    for field in ("text", "title", "placeholder"):
        raw = source_record.get(field)
        if isinstance(raw, str) and interactive_text_needs_translation(raw):
            interactive_sources.add(raw.strip())
    for field in ("items", "tabs", "headers"):
        if field == "items" and not source_record.get("translate_items"):
            continue
        interactive_sources.update(
            str(raw).strip() for raw in source_record.get(field, ())
            if interactive_text_needs_translation(str(raw))
        )
for language in ("en", "es", "fr"):
    missing = sorted(interactive_sources - application.UI_TRANSLATIONS[language].keys())
    assert not missing, f"{language} misses interactive UI translations: {missing}"
navigation_sources = {raw for _item, raw in window._navigation_item_sources}
for caption in ("Übersicht", "Kühlung", "Einstellungen", "Über"):
    assert any(raw.endswith(caption) for raw in navigation_sources)
language_modules = (de, en, es, fr)
assert tuple(module.LANGUAGE_CODE for module in language_modules) == ("de", "en", "es", "fr")
assert all(set(module.UI_MESSAGES) == set(de.UI_MESSAGES) for module in language_modules)
assert len(set(de.UI_MESSAGES.values())) == len(de.UI_MESSAGES)
assert all(application.UI_TRANSLATIONS["de"][source] == source for source in de.UI_MESSAGES.values())
assert translated_control_text("personal.png\nBild", application.UI_TRANSLATIONS["en"]) == "personal.png\nImage"
assert translated_control_text("Alle Hintergründe · 27", application.UI_TRANSLATIONS["fr"]) == "Tous les arrière-plans · 27"

# Prove that live switching applies the catalog, not merely that keys exist.
balanced_button = next(
    obj for obj, source in window._i18n_widget_sources.items()
    if isinstance(obj, QAbstractButton) and source.get("text") == "Ausbalanciert"
)
language_combo = next(
    obj for obj, source in window._i18n_widget_sources.items()
    if isinstance(obj, QComboBox) and "Deutsch" in source.get("items", ())
)
german_index = list(window._i18n_widget_sources[language_combo]["items"]).index("Deutsch")
for language, profile_text, german_text in (
    ("en", "Balanced", "German"),
    ("es", "Equilibrado", "Alemán"),
    ("fr", "Équilibré", "Allemand"),
):
    window.apply_ui_language(language, persist=False, log_change=False)
    window.refresh_dynamic_translations()
    assert balanced_button.text() == profile_text
    for button, caption in zip(window.profile_bundle_controller.buttons,
                               ("Komplettpaket exportieren", "Komplettpaket importieren"), strict=True):
        assert button.text() == application.UI_TRANSLATIONS[language][caption]
    assert window.openrgb_gpu_setup_button.text() == application.UI_TRANSLATIONS[language][
        "Grafikkarte: Steuerweg und LEDs"
    ]
    assert language_combo.itemText(german_index) == german_text
    assert language not in {"en", "es", "fr"} or "Übersicht" not in window.nav_overview.text(0)
    assert language not in {"en", "es", "fr"} or "Kühlung" not in window.nav_nzxt.text(0)
    window.tabs.setCurrentIndex(1)
    assert window.page_title_label.text() == application.UI_TRANSLATIONS[language]["Kühlungszentrale"]

included_label = next(
    obj for obj, source in window._i18n_widget_sources.items()
    if isinstance(obj, QLabel) and str(source.get("text", "")).startswith("<b>Enthalten:</b>")
)
window.apply_ui_language("en", persist=False, log_change=False)
assert included_label.text().startswith("<b>Included:</b>")
window._cooling_owner_probe_ready(CoolingOwnerStatus(False, False, False))
assert window.cooling_ownership_label.text().startswith("✓ No competing CoolerControl")
assert window.cooling_autostart_button.text() == "Enable CoolerControl permanently"
window._cooling_owner_probe_ready(CoolingOwnerStatus(True, True, True))
assert window.cooling_ownership_label.text().startswith("⚠ The CoolerControl background service")
assert window.cooling_autostart_button.text() == "Permanently disable CoolerControl"

# Fan cards are created only after hwmon discovery and must use the active
# language even though they were absent from the startup translation snapshot.
fan_root = temporary_root / "fan-card"
fan_root.mkdir()
pwm_path = fan_root / "pwm3"
pwm_path.write_text("128\n", encoding="ascii")
rpm_path = fan_root / "fan3_input"
rpm_path.write_text("912\n", encoding="ascii")
label_path = fan_root / "fan3_label"
label_path.write_text("System Fan 3\n", encoding="ascii")
channel = application.MainboardFanChannel(
    index=3,
    hwmon_path=fan_root,
    name="nct6687",
    pwm_path=pwm_path,
    enable_path=None,
    rpm_path=rpm_path,
    label_path=label_path,
    writable=True,
    pwm_value=128,
    rpm=912,
)
window.mainboard_channels = {channel.stable_id: channel}
profile = window.mainboard_default_profile(channel)
profile.update({"calibrated": True, "enabled": False, "preset": "balanced"})
window.mainboard_fan_profiles[channel.stable_id] = profile
window.apply_ui_language("en", persist=False, log_change=False)
window.refresh_dynamic_translations()
fan_buttons = {button.text() for button in window.mainboard_fan_cards.findChildren(QAbstractButton)}
fan_labels = {label.text() for label in window.mainboard_fan_cards.findChildren(QLabel)}
assert {"Test", "Test 0% / 2 min", "Edit curve & details", "Assign", "Enable automatic control", "Quiet", "Balanced", "Performance"} <= fan_buttons
assert "Curve profile:" in fan_labels
assert any(text.startswith("Profile: Balanced") for text in fan_labels)
assert "System Fan 3" in fan_labels
assert "SYS_FAN3" in fan_labels
assert not any("PWM 3" in text for text in fan_labels)
assert any("nct6687:pwm3" in label.toolTip() for label in window.mainboard_fan_cards.findChildren(QLabel))
assert not any("System Fan 3 · pwm3" in text for text in fan_labels)
assert "1 system-fan channels  ·  1 assigned  ·  0 profile active" == window.cooling_case_summary_label.text()
window.toggle_mainboard_channel_enabled_from_card(channel.stable_id)
fan_buttons = {button.text() for button in window.mainboard_fan_cards.findChildren(QAbstractButton)}
assert "Disable automatic control" in fan_buttons
assert window.mainboard_fan_profiles[channel.stable_id]["enabled"] is True
window.toggle_mainboard_channel_enabled_from_card(channel.stable_id)
assert window.mainboard_fan_profiles[channel.stable_id]["enabled"] is False
window.mainboard_channels = {}
window.mainboard_fan_profiles.pop(channel.stable_id, None)
window.apply_ui_language("de", persist=False, log_change=False)
assert balanced_button.text() == "Ausbalanciert"
assert tuple(application.UI_TRANSLATIONS[language]["0 % / 2 min testen"] for language in ("en", "es", "fr")) == (
    "Test 0% / 2 min", "Probar 0 % / 2 min", "Tester 0 % / 2 min",
)

assert window.tabs.count() == 21
assert window.tabs.tabText(window.design_automation_page_index) == "Automationszentrale"
assert window.navigation_items["automations"].data(0, Qt.ItemDataRole.UserRole) == window.design_automation_page_index
assert window.tabs.tabText(window.programs_page_index) == "Programme"
assert window.navigation_items["programs"].data(0, Qt.ItemDataRole.UserRole) == window.programs_page_index
hub_parent = window.navigation_items["design_hub"]
assert [window.navigation_item_key(hub_parent.child(i)) for i in range(hub_parent.childCount())] == ["paired_designs", "games", "automations"]
assert window.navigation_items["automations"].parent() is hub_parent
assert window.tabs.tabText(13) == "Gehäuse"
assert window.tabs.tabText(window.gpu_control_page_index) == "Grafikkarte"
assert window.navigation_items["case"].data(0, Qt.ItemDataRole.UserRole) == 13
assert window.tabs.tabText(14) == "Hardware-Prüfung"
assert window.navigation_items["hardware_checker"].data(0, Qt.ItemDataRole.UserRole) == 14
assert window.tabs.tabText(window.snapshot_manager_page_index) == "Snapshot-Manager"
assert window.navigation_items["snapshot_manager"].data(0, Qt.ItemDataRole.UserRole) == window.snapshot_manager_page_index
assert window.tabs.tabText(9) == "Wallpaper Engine"
assert window.navigation_items["wallpaper_engine"].data(0, Qt.ItemDataRole.UserRole) == 9
assert window.tabs.tabText(11) == "Display-Effekte"
assert window.navigation_items["display_effects"].data(0, Qt.ItemDataRole.UserRole) == 11
assert window.help_page_index == 12
navigation_root = window.navigation.invisibleRootItem()
assert [window.navigation_item_key(navigation_root.child(index)) for index in range(navigation_root.childCount())] == [
    "overview", *(key for key in application.NAVIGATION_DEFAULT_ORDER if key not in {"display_effects", "automations"})
]
assert window.nav_display_effects.parent() is window.nav_lcd
assert window.nav_lcd_studio.parent() is window.nav_lcd
assert len(window.lcd_section_tabs.bars) == 2
assert all(bar.count() == 2 for bar in window.lcd_section_tabs.bars)
window.lcd_section_tabs.bars[0].setCurrentIndex(1)
assert window.tabs.currentIndex() == 11
assert all(bar.currentIndex() == 1 for bar in window.lcd_section_tabs.bars)
window.lcd_section_tabs.bars[1].setCurrentIndex(0)
assert window.tabs.currentIndex() == 3
assert all(bar.currentIndex() == 0 for bar in window.lcd_section_tabs.bars)
assert window.nav_cooling_controls.parent() is window.nav_nzxt
assert window.nav_temperature_recording.parent() is window.nav_nzxt
window.navigation.setCurrentItem(window.nav_temperature_recording)
assert window.tabs.currentIndex() == 1
assert window.cooling_subtabs.currentIndex() == 1
assert window.nav_nzxt.isExpanded()
window.navigation.setCurrentItem(window.nav_cooling_controls)
assert window.cooling_subtabs.currentIndex() == 0
window.tabs.setCurrentIndex(11)
assert window.nav_lcd.isExpanded()
window.tabs.setCurrentIndex(2)
assert not window.nav_lcd.isExpanded()
settings.setValue("navigation/order", json.dumps(application.NAVIGATION_LEGACY_DEFAULTS[-1]))
assert window.load_navigation_order() == list(application.NAVIGATION_DEFAULT_ORDER)
assert window.wallpaper_engine_page.sections.count() == 3
assert window.window_screen_preference == application.PRIMARY_SCREEN_PREFERENCE
assert window.window_screen_combo.currentData() == application.PRIMARY_SCREEN_PREFERENCE
assert window.window_screen_combo.count() >= 1
assert window.windowed_size_spin.value() == application.DEFAULT_WINDOWED_SIZE_PERCENT
assert window.page_transitions_checkbox.isChecked()
assert window.page_transition_style_combo.currentData() == "fade"
assert window.page_transition_duration_combo.currentData() == 380
assert len(window.rgb_design_gallery.visible_indices()) == 12
assert window.ssd_cache_combo.currentData() == 2048
assert window.ui_performance is not None
assert window.window_chrome.close_button.size() == QSize(48, 42)
assert window.cooling_auto_case_button.isCheckable()
assert window.cooling_auto_case_button.isChecked() == window.mainboard_control_active
assert window.rgb_devices_effects_panel.isHidden()
button_texts = {button.text() for button in window.findChildren(QAbstractButton)}
assert "Mein Retro 360 bei Amazon" not in button_texts
assert "Luftstrom umkehren" in button_texts
assert "Block in Einzellüfter teilen" in button_texts
assert [window.rgb_case_cooling_combo.itemData(index) for index in range(3)] == ["auto", "aio", "air"]
window.move(100000, 100000)
assert window.position_window_on_preferred_screen("Offscreen-Regression")
preferred_screen, preferred_matched = window.preferred_window_screen()
assert preferred_screen is QApplication.primaryScreen()
assert preferred_matched
assert preferred_screen.availableGeometry().contains(window.frameGeometry().center())
available = preferred_screen.availableGeometry()
window._last_windowed_rect = application.WindowRect(
    available.x(), available.y(), available.width(), available.height()
)
assert window.restore_safe_windowed_geometry("Maximierte-Normalgröße-Regression")
assert window.width() < available.width()
assert available.contains(window.geometry().topLeft())
assert available.contains(window.geometry().bottomRight())
window.apply_display_settings()
assert settings.value("window/screen_preference") == application.PRIMARY_SCREEN_PREFERENCE
window.wallpaper_engine_page.refresh_library()
assert "Workshop-Wallpaper" in window.wallpaper_engine_page.status_label.text()
wallpaper_page = window.wallpaper_engine_page
assert "Workshop-Wallpaper" in wallpaper_page.onboarding.checklist.text()
assert wallpaper_page.display_mode_combo.count() == 3
assert [wallpaper_page.display_mode_combo.itemData(index) for index in range(3)] == [0, 1, 2]
assert wallpaper_page.workshop_list.iconSize() == QSize(192, 108)
assert wallpaper_page.workshop_list.gridSize() == QSize(224, 154)
wallpaper_page._stabilize_gallery_layout()
assert wallpaper_page.workshop_list.gridSize() == QSize(224, 154)
gallery_entries = [
    WallpaperEntry(
        ident=str(9000 + index),
        title=f"Galerie {index}",
        kind="video",
        source_path=saved_designs / "saved-preview.png",
        preview_path=saved_designs / "saved-preview.png",
    )
    for index in range(8)
]
for _refresh in range(2):
    wallpaper_page._thumb_queue.clear()
    wallpaper_page.workshop_entries = gallery_entries
    wallpaper_page._populate_gallery(wallpaper_page.workshop_list, gallery_entries, workshop=True)
    hidden_queue_size = len(wallpaper_page._thumb_queue)
    wallpaper_page._load_thumbnail_batch()
    assert len(wallpaper_page._thumb_queue) == hidden_queue_size
    assert not wallpaper_page.thumbnail_timer.isActive()
    assert wallpaper_page.workshop_list.count() == 8
    assert all(
        wallpaper_page.workshop_list.item(row).sizeHint() == QSize(224, 154)
        for row in range(wallpaper_page.workshop_list.count())
    )
assert application._GIF_SAFETY_TEXT in labels
assert application._ABOUT_SUMMARY_TEXT in labels
assert window.windowTitle().startswith("Open Hardware Control by Frelidon 3.4.29.180 INTERN")
assert window.temp_card.isHidden()
assert not window.cpu_temp_card.isHidden()
assert window.mainboard_sensor_source.findData("liquid") == -1
assert window.mainboard_sensor_source.findData("max") >= 0
assert window.mainboard_curve_overlay_source.findData("liquid") == -1
window.devices_ready = True
window.current_liquid_temp = 31.5
window.apply_dashboard_card_visibility(save=False)
assert not window.temp_card.isHidden()
window.current_liquid_temp = None
window.apply_dashboard_card_visibility(save=False)
assert window.temp_card.isHidden()
assert any(size.width() == 22 and size.height() == 22 for size in window.tray.icon().availableSizes())
assert window.thermalright_display_studio.current_media_path() == (saved_designs / "saved-preview.png")
studio = window.thermalright_display_studio
custom_before = sum(item.kind == "text" for item in studio.overlay_specs)
studio.add_custom_text_overlay()
custom_item = next(item for item in studio.overlay_specs if item.kind == "text")
assert sum(item.kind == "text" for item in studio.overlay_specs) == custom_before + 1
custom_controls = studio.overlay_controls[custom_item.ident]
custom_controls["label"].setText("Mein Rechner")
custom_controls["label"].editingFinished.emit()
custom_controls["font"].setCurrentIndex(min(1, custom_controls["font"].count() - 1))
stored_custom = next(item for item in studio.overlay_specs if item.ident == custom_item.ident)
assert stored_custom.text == "Mein Rechner"
assert stored_custom.font == str(custom_controls["font"].currentData() or "")
studio.remove_custom_text_overlay(custom_item.ident)
assert sum(item.kind == "text" for item in studio.overlay_specs) == custom_before
assert custom_item.ident not in studio.overlay_controls
assert studio.custom_media_directory == saved_designs.resolve()
assert studio.media_duplicate_count == 1
assert sum(entry.path.name == "saved-preview.png" for entry in studio.media_entries) == 1
assert studio.levita_brightness.value() == 0
assert studio.custom_media_enabled.isChecked()
assert studio.layer1_intensity_slider.value() == 100
assert studio.layer2_intensity_slider.minimum() == 25
assert studio.layer2_intensity_slider.maximum() == 150
assert studio.canvas.dragMode() == QGraphicsView.DragMode.NoDrag
black = QImage(1600, 720, QImage.Format.Format_RGB32)
black.fill(QColor("#000000"))
studio.canvas.set_background(QPixmap.fromImage(black))
studio._select_media_card(str((saved_designs / "saved-preview.png").resolve()))
assert studio.canvas._background.toImage().pixelColor(800, 360) == QColor("#163452")
studio._select_media_card(str((saved_designs / "second-preview.png").resolve()))
assert studio.canvas._background.toImage().pixelColor(800, 360) == QColor("#b24a21")
studio._select_media_card(str((saved_designs / "saved-preview.png").resolve()))
assert studio.hardware_design_combo.findData(str(live_theme.resolve())) >= 0
assert studio.media_combo.findData(str(live_theme.resolve())) < 0
studio.load_default_trcc_designs()
assert Path(str(settings.value("thermalright/custom_media_directory"))) == saved_designs.resolve()
assert any(entry.path == (saved_designs / "saved-preview.png") for entry in studio.media_entries)
with patch("thermalright_display_ui.default_trcc_design_directory", return_value=None):
    studio.custom_media_enabled.setChecked(False)
    assert not any(entry.path.is_relative_to(saved_designs) for entry in studio.media_entries)
assert saved_designs.is_dir()
assert Path(str(settings.value("thermalright/custom_media_directory"))) == saved_designs.resolve()
studio.custom_media_enabled.setChecked(True)
assert any(entry.path == (saved_designs / "saved-preview.png") for entry in studio.media_entries)
studio._select_hardware_card(str(live_theme.resolve()))
assert studio.current_media_path() == (saved_designs / "saved-preview.png")
assert not studio.canvas._hardware_layer.isNull()
assert studio.canvas._background.toImage().pixelColor(800, 360) == QColor("#163452")
assert studio.canvas._hardware_layer.toImage().pixelColor(800, 360).alpha() == 0
assert studio.canvas._hardware_layer.toImage().pixelColor(100, 100).alpha() == 255
assert studio.canvas._layout is not None
assert len(studio.canvas._layout.blocks) == 1
layout_block = studio.canvas._layout.blocks[0]
layout_item = next(
    item for item in studio.canvas.scene().items()
    if getattr(getattr(item, "block", None), "ident", None) == layout_block.ident
)
layout_item_center = layout_item.mapToScene(layout_item.boundingRect().center())
assert round(layout_item_center.x()) == layout_block.x + studio.canvas._layout.offset_x
assert round(layout_item_center.y()) == layout_block.y + studio.canvas._layout.offset_y
next_frame = QPixmap(1600, 720)
next_frame.fill(QColor("#224466"))
studio.canvas.set_background(next_frame)
same_layout_item = next(
    item for item in studio.canvas.scene().items()
    if getattr(getattr(item, "block", None), "ident", None) == layout_block.ident
)
assert same_layout_item is layout_item
studio._open_layer2_inline_editor(layout_block)
assert not studio.layer2_inline_editor.isHidden()
studio.layer2_inline_color.setText("#ff5500")
studio.layer2_inline_size.setValue(55)
studio.layer2_inline_text.setText("Prozessor {value:.0f}%")
studio._apply_layer2_inline_editor()
assert studio.layer2_inline_editor.isHidden()
edited_block = studio.canvas._layout.blocks[0]
assert edited_block.color == "#ff5500"
assert edited_block.size == 55
assert edited_block.preview_text == "Prozessor 42%"
assert studio.layer2_offset_x.isEnabled()
studio.layer2_offset_x.setValue(25)
assert studio.canvas._layout.offset_x == 25
studio.geometry_toggle.setChecked(True)
assert not studio.geometry_scroll.isHidden()
assert studio.geometry_scroll.widget() is studio.geometry_box
assert studio.background_x.minimumHeight() >= 36
assert studio.background_x.minimumWidth() >= 148
assert studio.media_scale_mode.minimumHeight() >= 36
assert studio.media_scale_mode.minimumWidth() >= 320
assert studio.split_mode.minimumWidth() >= 320
assert studio.geometry_box.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Minimum
saved_overrides = json.loads(str(settings.value("thermalright/layer2_overrides_v1")))
assert saved_overrides["schema"] == 1
assert studio.canvas.minimumWidth() == 880
assert studio.canvas.maximumWidth() == 880
assert studio.canvas.minimumHeight() == 396
assert studio.canvas.maximumHeight() == 396
assert studio.canvas.heightForWidth(800) == 360
studio.move_selected_theme_to_background_layer()
assert studio.media_combo.findData(str(live_theme.resolve())) >= 0
studio.move_selected_theme_to_data_layer()
assert studio.hardware_design_combo.findData(str(live_theme.resolve())) >= 0
studio.hardware_design_combo.setCurrentIndex(0)
studio._select_media_card(str((saved_designs / "saved-preview.png").resolve()))
studio.remember_startup_design()
assert settings.value("thermalright/autostart_enabled", False, type=bool)
assert Path(str(settings.value("thermalright/start_media"))) == (saved_designs / "saved-preview.png")
assert studio.stage_profile_startup_design()
profile_payload = window.capture_profile_payload("LCD")
assert profile_payload["levita_display"] == {
    "media": str((saved_designs / "saved-preview.png").resolve()),
    "hardware_design": "",
    "enabled": True,
    "layer2_motion": False,
    "desktop_fps": 15,
    "game_fps": 15,
}
settings.setValue("thermalright/start_media", str(saved_designs / "second-preview.png"))
assert not studio.restore_profile_startup_payload(profile_payload["levita_display"], startup=True)
assert Path(str(settings.value("thermalright/start_media"))) == saved_designs / "second-preview.png"
assert studio.restore_profile_startup_payload(profile_payload["levita_display"])
assert Path(str(settings.value("thermalright/start_media"))) == (saved_designs / "saved-preview.png")
bundled_effect = next((ROOT / "src/assets/display-effects").glob("*.mp4")).resolve()
assert not any(entry.path == bundled_effect for entry in studio.media_entries)
assert studio.restore_profile_startup_payload({
    "media": str(bundled_effect),
    "hardware_design": "",
    "enabled": True,
})
assert studio._restore_startup_selection()
assert studio.current_media_path() == bundled_effect
effects_page = window.display_effects_page
pending_before_preview = settings.value("thermalright/profile_pending_media")
effects_page.effect_combo.setCurrentIndex(effects_page.effect_combo.findData("library"))
assert settings.value("thermalright/profile_pending_media") == pending_before_preview
effects_page.remember_for_profile_start()
assert Path(str(settings.value("thermalright/profile_pending_media"))) == effects_page.stock_library.current_video()
assert Path(str(settings.value("thermalright/start_media"))) == effects_page.stock_library.current_video()
assert settings.value("thermalright/autostart_enabled", False, type=bool)
studio.startup_apply_requested = False
studio.apply_startup_design_if_enabled()
assert studio.startup_apply_requested
assert studio.command_process.state() == application.QProcess.ProcessState.NotRunning
assert window.hardware_io_disabled
assert window.openrgb_server_process.state() == application.QProcess.ProcessState.NotRunning
window.theme_mode = "light"
previous_home_icon = window.openlinkhub_mouse_home_button.icon().cacheKey()
window.apply_theme()
assert window.openlinkhub_mouse_home_button.icon().cacheKey() != previous_home_icon
assert "rgba(255, 255, 255, 252)" in window.styleSheet()
assert "QLabel#brandLabel" in window.styleSheet()
assert "QScrollBar:vertical" in window.styleSheet()
assert "width: 8px" in window.styleSheet()
assert window.navigation.palette().color(QPalette.ColorRole.HighlightedText).name() == "#102a43"
assert window.navigation.palette().color(QPalette.ColorRole.Text).name() == "#17212b"
window.theme_mode = "dark"
window.apply_theme()
assert "rgba(7, 19, 31, 248)" in window.styleSheet()

render_dir = os.environ.get("OHC_UI_RENDER_DIR")
if render_dir:
    settings.setValue("setup/completed", True)
    settings.setValue("dependencies/desktop_design_offer_330", True)
    from rgb_devices import flori_rgb_layout_profile
    _, window.rgb_layout_slots = flori_rgb_layout_profile("thermalright")
    window.refresh_rgb_layout_editor()
    window.rgb_layout_diagram.set_cooling_visual("aio")
    output = Path(render_dir)
    output.mkdir(parents=True, exist_ok=True)
    window.resize(1800, 1100)
    window.tabs.setCurrentIndex(window.case_page_index)
    window.show()
    qt_app.processEvents()
    assert window.grab().save(str(output / "case-page.png"))
    window.tabs.setCurrentIndex(2)
    window.set_rgb_devices_effects_expanded(True)
    qt_app.processEvents()
    window.rgb_page_scroll.verticalScrollBar().setValue(0)
    qt_app.processEvents()
    assert window.grab().save(str(output / "rgb-gallery.png"))
    window.rgb_page_scroll.ensureWidgetVisible(window.openrgb_performance_label, 20, 20)
    qt_app.processEvents()
    assert window.grab().save(str(output / "rgb-transfer.png"))
    window.tabs.setCurrentIndex(window.hardware_checker_page_index)
    qt_app.processEvents()
    assert window.grab().save(str(output / "hardware-checker-cards.png"))
    window.tabs.setCurrentIndex(window.gpu_control_page_index)
    window.gpu_control_page.sections.setCurrentIndex(0)
    window.gpu_control_page.verticalScrollBar().setValue(0)
    qt_app.processEvents()
    assert window.grab().save(str(output / "gpu-cockpit.png"))
    window.gpu_control_page.ensureWidgetVisible(window.gpu_control_page.fan_visual, 20, 20)
    qt_app.processEvents()
    assert window.grab().save(str(output / "gpu-fan-curve.png"))
    window.tabs.setCurrentIndex(4)
    modules_box = next(iter(window.navigation_module_checkboxes.values())).parentWidget().parentWidget()
    assert isinstance(modules_box, QGroupBox)
    window.settings_page_scroll.ensureWidgetVisible(modules_box, 24, 24)
    qt_app.processEvents()
    assert window.grab().save(str(output / "settings-modules.png"))
    assert modules_box.grab().save(str(output / "settings-modules-panel.png"))
    window.tabs.setCurrentIndex(5)
    qt_app.processEvents()
    window.profile_workspace.transfers.button.setChecked(True)
    qt_app.processEvents()
    assert window.profile_bundle_controller.buttons[0].isVisible()
    assert window.grab().save(str(output / "profiles-complete-package.png"))
# .172 hardware subnavigation and language refresh retain all existing views.
window.settings.setValue("setup/completed", True)
window.settings.setValue("dependencies/desktop_design_offer_330", True)
for language in ("de", "en", "es", "fr"):
    window.apply_ui_language(language, persist=False, log_change=False)
    parent = window.navigation_items["hardware_checker"]
    assert parent.childCount() == 2
    for key, section, caption in (("hardware_checker", 0, "Hardware-Prüfung"),
                                   ("hardware_fix", 1, "Hardware Fix"),
                                   ("supported_devices", 2, "Von OHC unterstützte Geräte")):
        window.navigation.setCurrentItem(window.navigation_items[key])
        qt_app.processEvents()
        assert window.tabs.currentIndex() == window.hardware_checker_page_index
        assert window.hardware_checker_page.section_tabs.currentIndex() == section
        assert window.page_title_label.text() == window.tr_static(caption)
        assert window.sidebar_artwork.category == key
    assert len(window.hardware_checker_page.supported_devices_page.cards) == 41
# Complete real press/move/release gestures from every expandable section.
# Regresses rows moving under a held pointer and opening a second page.
from PySide6.QtTest import QTest
from PySide6.QtCore import QPoint
window.resize(1600, 1000)
window.show_all_navigation_modules()
window.show()
for language in ("de", "en", "es", "fr"):
    window.apply_ui_language(language, persist=False, log_change=False)
    for origin in ("lcd_studio", "display_effects", "temperature_recording", "hardware_fix", "supported_devices", "paired_designs", "games", "automations"):
        for destination in ("rgb_studio", "settings", "profiles", "about", "lcd_studio", "display_effects",
                            "cooling_controls", "temperature_recording", "hardware_checker", "hardware_fix", "supported_devices", "paired_designs", "games", "automations"):
            window.navigation.setCurrentItem(window.navigation_items[origin])
            item = window.navigation_items[destination]
            qt_app.processEvents()
            window.navigation.doItemsLayout()
            window.navigation.scrollToItem(item, application.QAbstractItemView.ScrollHint.PositionAtCenter)
            qt_app.processEvents()
            window.navigation.doItemsLayout()
            window.navigation.scrollToItem(item, application.QAbstractItemView.ScrollHint.PositionAtCenter)
            position = window.navigation.visualItemRect(item).center()
            assert window.navigation.viewport().rect().contains(position), (origin, destination, position, window.navigation.viewport().rect(), item.isHidden())
            QTest.mousePress(window.navigation.viewport(), Qt.MouseButton.LeftButton, pos=position)
            QTest.mouseMove(window.navigation.viewport(), position + QPoint(0, 1))
            QTest.mouseRelease(window.navigation.viewport(), Qt.MouseButton.LeftButton, pos=position + QPoint(0, 1))
            qt_app.processEvents()
            assert window.tabs.currentIndex() == item.data(0, Qt.ItemDataRole.UserRole), (language, origin, destination)
            if destination in ("hardware_fix", "supported_devices"):
                assert window.navigation.currentItem() is item
            elif destination != "cooling_controls":
                assert window.navigation.currentItem() is item, (language, origin, destination)

window.reset_navigation_customization()
assert window.navigation_items["automations"].parent() is window.navigation_items["design_hub"]
assert window.navigation_items["design_hub"].childCount() == 3
assert all(window.navigation_items[key].parent() is window.navigation_items["hardware_checker"]
           for key in ("hardware_fix", "supported_devices"))
window.tabs.setCurrentIndex(0)
assert window.sidebar_artwork.category == "overview"

# .176 wizard is built with a synthetic connector in all four languages;
# automatic white dispatch is invoked, while hardware remains isolated.
from modules.fan_mapping.v1_0.wizard import build as build_fan_wizard
window.mainboard_channels = {channel.stable_id: channel}
window.mainboard_fan_profiles[channel.stable_id] = window.mainboard_default_profile(channel)
for language in ("de", "en", "es", "fr"):
    window.apply_ui_language(language, persist=False, log_change=False)
    with patch("modules.fan_mapping.v1_0.wizard.begin") as automatic_white:
        build_fan_wizard(window, [channel])
        qt_app.processEvents()
        automatic_white.assert_called_once_with(window)
    wizard = window.chassis_fan_wizard
    assert wizard.windowTitle() == window.tr_static("Lüfter-Zuordnung & Test-Assistent")
    assert wizard.button(application.QWizard.WizardButton.NextButton).text() == window.tr_static("Weiter")
    captions = {button.text() for button in wizard.findChildren(QAbstractButton)}
    assert window.tr_static("Nicht angeschlossen · überspringen") in captions
    assert window.tr_static("0 % / 2 min Stopp-Test · andere Gehäuselüfter 45 %") in captions
    wizard.setCurrentId(1)
    next(button for button in wizard.findChildren(QAbstractButton)
         if button.text() == window.tr_static("Nicht angeschlossen · überspringen")).click()
    assert window.mainboard_fan_profiles[channel.stable_id]["connection"] == "disconnected"
    assert window.mainboard_fan_profiles[channel.stable_id]["enabled"] is False
    assert wizard.currentId() == 3
    wizard.reject()
window.mainboard_channels = {}
window.mainboard_fan_profiles.pop(channel.stable_id, None)

# .179 temporarily missing sensors wait without a modal dialog or direct write.
with patch.object(window, 'defer_cooling_action_for_gif', return_value=False), patch.object(window, 'read_amd_cpu_temperature', return_value=(None, 'synthetic unavailable')), patch.object(window, 'show_error', side_effect=AssertionError('sensor wait must be nonmodal')):
    window.kraken_write_busy = False
    window.transmit_profile_cooling({'fan_mode':'curve'}, 'synthetic profile')
    assert window.profile_cooling_wait.pending is not None
with patch.object(window, 'read_amd_cpu_temperature', return_value=(52., 'synthetic CPU')), patch.object(window, 'cooling_device_ready', return_value=True), patch.object(window, 'transmit_profile_cooling') as retry_existing:
    window.profile_cooling_wait.check()
    assert retry_existing.call_count == 1
    assert window.profile_cooling_wait.pending is None

# .178 profile cards keep legacy IDs/CRUD and never apply on selection/filter.
workspace = window.profile_workspace
original_users = list(window.user_profiles)
original_current = window.current_profile_id
sample = {'id':'ui-profile-check','name':'Private test name','description':'draft data','category':'RGB','payload':{'rgb':{'studio_effect':'code_rain','studio_brightness':75}},'builtin':False}
window.user_profiles.append(sample)
workspace.refresh()
with patch.object(window, 'apply_profile_payload', side_effect=AssertionError('selection must not apply')), patch.object(window, 'save_profiles', side_effect=AssertionError('browsing must not save')):
    workspace.select(sample['id'])
    assert window.selected_profile()['id'] == sample['id']
    assert workspace.edit.isEnabled() and workspace.delete.isEnabled()
    workspace.search.setText('Private')
    assert not workspace.cards[sample['id']].isHidden()
    workspace.search.setText('no matching name')
    assert not workspace.empty.isHidden()
    assert window.selected_profile()['id'] == sample['id']
    workspace.search.clear()
    window.profile_name_input.setText('Unsaved name')
    window.profile_description_input.setText('Unsaved description')
    for language in ('de','en','es','fr'):
        window.apply_ui_language(language,persist=False,log_change=False)
        assert window.selected_profile()['id'] == sample['id']
        assert window.profile_name_input.text() == 'Unsaved name'
        assert window.profile_description_input.text() == 'Unsaved description'
        assert workspace.filter.itemData(0) == 'all'
        assert workspace.filter.itemText(0) == window.tr_static('Alle Profile')
        assert window.background_theme_combo.findData('Sternenfeld') >= 0
        assert window.background_theme_combo.itemText(window.background_theme_combo.findData('Sternenfeld')) == window.tr_static('Sternenfeld')
    workspace.select('builtin-quiet')
    assert not workspace.edit.isEnabled() and not workspace.delete.isEnabled()
    assert workspace.duplicate.isEnabled() and workspace.apply.isEnabled()
    workspace.new_profile()
    assert window.selected_profile() is None
    assert window.profile_name_input.text() == ''
    assert workspace.editor.button.isChecked()
    assert not workspace.update.isEnabled()
workspace.select(sample['id'])
with patch.object(window, 'save_profiles'):
    window.duplicate_selected_profile()
assert window.selected_profile()['id'] != sample['id']
assert window.selected_profile()['payload'] == sample['payload']
assert window.selected_profile()['builtin'] is False
window.user_profiles = original_users
window.current_profile_id = original_current
workspace.search.clear();workspace.filter.setCurrentIndex(0);workspace.refresh()
workspace.editor.button.setChecked(False)
window.apply_ui_language('de',persist=False,log_change=False)
assert window.profiles_table.parentWidget() is workspace and window.profiles_table.isHidden()
# Applied-profile background has independent state; visiting other pages restores
# the global choice and never changes persisted background preferences.
from modules.app_backgrounds.v1_0.profile import mark_applied, sync as sync_profile_background
configured_theme = window.background_theme
persisted_background = window.settings.value('ui/background_theme')
window.tabs.setCurrentIndex(5)
mark_applied(window, {'rgb':{'studio_effect':'code_rain','studio_primary':'00ff66'}})
assert window.background_widget.media_background.rgb.effect_id == 'code_rain'
workspace.select('builtin-quiet')
assert window.background_widget.media_background.rgb.effect_id == 'code_rain'
window.tabs.setCurrentIndex(4);sync_profile_background(window)
assert window.background_widget.media_background.rgb is None
assert window.background_theme == configured_theme
assert window.settings.value('ui/background_theme') == persisted_background

dispose_window(window)

# A KDE/Wayland tray autostart must suppress the native window surface before
# the large UI constructor can expose an unpainted black frame.  Opening from
# the tray explicitly releases that suppression.
original_argv = list(sys.argv)
sys.argv.append("--autostart")
settings.setValue("setup/completed", True)
settings.setValue("app/autostart_minimized", True)
settings.sync()
autostart_window = application.KrakenControl()
atexit.register(lambda: dispose_window(autostart_window) if isValid(autostart_window) else None)
assert autostart_window.testAttribute(application.Qt.WidgetAttribute.WA_DontShowOnScreen)
assert autostart_window.autostart_window_surface_suppressed
original_tray_available = application.QSystemTrayIcon.isSystemTrayAvailable
application.QSystemTrayIcon.isSystemTrayAvailable = staticmethod(lambda: True)
try:
    autostart_window.apply_initial_window_state()
    assert not autostart_window.isVisible()
    assert autostart_window.testAttribute(application.Qt.WidgetAttribute.WA_DontShowOnScreen)
finally:
    application.QSystemTrayIcon.isSystemTrayAvailable = original_tray_available
autostart_window.release_autostart_window_surface()
assert not autostart_window.testAttribute(application.Qt.WidgetAttribute.WA_DontShowOnScreen)
dispose_window(autostart_window)
sys.argv[:] = original_argv
temporary.cleanup()

print("Full offscreen UI construction restored an editable TRCC directory without hardware I/O.")
