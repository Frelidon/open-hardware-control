#!/usr/bin/env python3
"""Build every main page with real PySide6 while suppressing hardware I/O."""

from __future__ import annotations

import os
import json
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
os.environ["OHC_DISABLE_HARDWARE_IO"] = "1"
os.environ["OHC_WALLPAPER_STEAM_LIBRARY"] = str(temporary_root / "Steam")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QSettings, QSize, Qt  # noqa: E402
from PySide6.QtGui import QColor, QImage, QPalette, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel, QGraphicsView, QSizePolicy  # noqa: E402
import kraken_control as application  # noqa: E402
from modules.wallpaper_engine.v1_2.library import WallpaperEntry  # noqa: E402

# A synthetic missing dependency prevents initialize_devices() and all deferred
# hardware discovery. The test covers the complete synchronous UI construction
# that caused the 3.4.29 startup failure.
application.KrakenControl.check_dependencies = lambda self: ["ui-build-no-hardware"]

qt_app = QApplication.instance() or QApplication([])

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
settings.sync()

window = application.KrakenControl()
labels = [label.text() for label in window.findChildren(QLabel)]

assert window.tabs.count() == 12
assert window.tabs.tabText(9) == "Wallpaper Engine"
assert window.navigation_items["wallpaper_engine"].data(0, Qt.ItemDataRole.UserRole) == 9
navigation_root = window.navigation.invisibleRootItem()
assert [window.navigation_item_key(navigation_root.child(index)) for index in range(navigation_root.childCount())] == [
    "overview", *application.NAVIGATION_DEFAULT_ORDER
]
settings.setValue("navigation/order", json.dumps(application.NAVIGATION_LEGACY_DEFAULTS[-1]))
assert window.load_navigation_order() == list(application.NAVIGATION_DEFAULT_ORDER)
assert window.wallpaper_engine_page.sections.count() == 3
assert window.window_screen_preference == application.PRIMARY_SCREEN_PREFERENCE
assert window.window_screen_combo.currentData() == application.PRIMARY_SCREEN_PREFERENCE
assert window.window_screen_combo.count() >= 1
window.move(100000, 100000)
assert window.position_window_on_preferred_screen("Offscreen-Regression")
preferred_screen, preferred_matched = window.preferred_window_screen()
assert preferred_screen is QApplication.primaryScreen()
assert preferred_matched
assert preferred_screen.availableGeometry().contains(window.frameGeometry().center())
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
    while wallpaper_page._thumb_queue:
        wallpaper_page._load_thumbnail_batch()
    wallpaper_page._stabilize_gallery_layout()
    assert wallpaper_page.workshop_list.count() == 8
    assert all(
        wallpaper_page.workshop_list.item(row).sizeHint() == QSize(224, 154)
        for row in range(wallpaper_page.workshop_list.count())
    )
assert application._GIF_SAFETY_TEXT in labels
assert application._ABOUT_SUMMARY_TEXT in labels
assert window.windowTitle().startswith("Open Hardware Control by Frelidon 3.4.29.44 STABLE")
assert window.temp_card.isHidden()
assert not window.cpu_temp_card.isHidden()
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
assert studio.canvas.maximumWidth() == 960
assert studio.canvas.maximumHeight() == 432
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
studio.startup_apply_requested = False
studio.apply_startup_design_if_enabled()
assert studio.startup_apply_requested
assert studio.command_process.state() == application.QProcess.ProcessState.NotRunning
assert window.hardware_io_disabled
assert window.openrgb_server_process.state() == application.QProcess.ProcessState.NotRunning
window.theme_mode = "light"
window.apply_theme()
assert "rgba(255, 255, 255, 252)" in window.styleSheet()
assert "QLabel#brandLabel" in window.styleSheet()
assert "QScrollBar:vertical" in window.styleSheet()
assert "width: 8px" in window.styleSheet()
assert window.navigation.palette().color(QPalette.ColorRole.HighlightedText).name() == "#18202a"
assert window.navigation.palette().color(QPalette.ColorRole.Text).name() == "#18202a"
window.theme_mode = "dark"
window.apply_theme()
assert "rgba(7, 19, 31, 248)" in window.styleSheet()

window.backend.shutdown()
window.deleteLater()
qt_app.processEvents()

# A KDE/Wayland tray autostart must suppress the native window surface before
# the large UI constructor can expose an unpainted black frame.  Opening from
# the tray explicitly releases that suppression.
original_argv = list(sys.argv)
sys.argv.append("--autostart")
settings.setValue("setup/completed", True)
settings.setValue("app/autostart_minimized", True)
settings.sync()
autostart_window = application.KrakenControl()
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
autostart_window.backend.shutdown()
autostart_window.deleteLater()
sys.argv[:] = original_argv
qt_app.processEvents()
temporary.cleanup()

print("Full offscreen UI construction restored an editable TRCC directory without hardware I/O.")
