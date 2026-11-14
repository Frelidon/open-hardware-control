"""Real Qt layout regressions for the installed profile workspace contract.

The worker owns isolated settings and disables every hardware transport. It can
also inspect an installed runtime explicitly, without loading personal profiles:
``python tests/test_profiles_workspace_geometry_3429180.py --worker
--runtime /path/to/installed/application --render-dir /tmp/profile-evidence``.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_lcd_summary_prefers_enabled_levita_and_preserves_legacy_fallback() -> None:
    from copy import deepcopy
    sys.path.insert(0, str(ROOT / "src"))
    from modules.profiles_workspace.v1_1.model import lcd_summary_data, summaries
    legacy = {"file": "", "mode": "unchanged", "brightness": 80}
    enabled = {"media": "/saved/matrix.mp4", "enabled": True}
    payload = {"lcd": legacy, "levita_display": enabled}
    before = deepcopy(payload)
    assert lcd_summary_data(payload) is enabled
    assert summaries(payload, str)[0][-1] == ["matrix.mp4", "2 Einstellungen"]
    assert payload == before
    for invalid in (
        {"media": "/saved/matrix.mp4", "enabled": False},
        {"media": " ", "enabled": True},
        {"media": 123, "enabled": True},
        None,
    ):
        fallback = {"lcd": legacy, "levita_display": invalid}
        assert lcd_summary_data(fallback) is legacy
        assert summaries(fallback, str)[0][-1] == ["Helligkeit · 80 %", "3 Einstellungen"]


def test_expanded_profile_workspace_retains_readable_content_and_drafts() -> None:
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker"],
        cwd=ROOT, env=environment, capture_output=True, text=True, timeout=90,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "profile geometry: 3 sizes, 4 languages, 2 themes passed" in completed.stdout


def _worker(runtime: Path, render_dir: Path | None = None, presentation: bool = False) -> None:
    import copy
    import tempfile
    from unittest.mock import patch

    with tempfile.TemporaryDirectory(prefix="ohc-profile-geometry-") as temporary:
        isolated = Path(temporary)
        os.environ.update(
            OHC_DISABLE_HARDWARE_IO="1",
            XDG_CONFIG_HOME=str(isolated / "config"),
            XDG_STATE_HOME=str(isolated / "state"),
            OHC_DESKTOP_DESIGN_CONFIG_DIR=str(isolated / "desktop-config"),
            OHC_DESKTOP_DESIGN_STATE_DIR=str(isolated / "desktop-state"),
            OHC_WALLPAPER_STEAM_LIBRARY=str(isolated / "Steam"),
        )
        sys.path.insert(0, str(runtime))
        from PySide6.QtCore import QCoreApplication, QEvent, QPoint, QProcess, QSettings, QTimer
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QAbstractButton, QApplication, QLabel, QScrollArea
        from shiboken6 import isValid
        import kraken_control as application
        from modules.application_shutdown.v1_1.qt_processes import stop_remaining
        from modules.display_effects.v1_11.catalog import DESIGNS

        # Suppress deferred device discovery as well as the transport itself.
        application.KrakenControl.check_dependencies = lambda _self: ["isolated-profile-layout"]
        app = QApplication.instance() or QApplication([])
        settings = QSettings(application.ORG_NAME, application.APP_NAME)
        for key, value in {
            "setup/completed": True,
            "dependencies/desktop_design_offer_330": True,
            "cooling/hardware_kind": application.LEVITA_COOLER_KEY,
            "performance/transitions_enabled": False,
            "display/ui_scale": 90,
            "background/enabled": presentation,
            "background/theme": "Matrix Code Rain · Video",
            "background/pause_inactive": False,
        }.items():
            settings.setValue(key, value)
        settings.sync()
        window = application.KrakenControl()
        try:
            assert window.hardware_io_disabled
            workspace = window.profile_workspace
            assert isinstance(workspace.scroll, QScrollArea)
            assert workspace.scroll.widget() is workspace.content
            assert window.profiles_table.isHidden()
            matrix_media = next(design for design in DESIGNS if design.ident == "ohc-code-rain").variants[0].video_path
            assert matrix_media.is_file()
            payload = {
                "cooling": {"pump": 70, "fan": 50, "fan_curve": [[30, 25], [50, 35], [65, 55], [80, 80], [90, 100]]},
                "gpu": {"name": "Saved GPU", "config": {"power": 120}},
                "rgb": {"studio_effect": "code_rain", "studio_brightness": 75,
                        "studio_primary": "00ff88", "studio_secondary": "d7ffe7"},
                "lcd": {"brightness": 80, "mode": "unchanged", "file": ""},
                "levita_display": {"media": str(matrix_media), "enabled": True},
                "design": {"theme": "dark", "background_theme": "Matrix Code Rain · Video", "accent": "24c9ff"},
                "future": {"unrecognized": "preserved"},
            }
            profile = {
                "id": "geometry-fixture", "name": "Geometry fixture",
                "description": "Saved settings for isolated layout checks.",
                "category": "Gesamt", "builtin": False, "payload": payload,
            }
            window.user_profiles = [copy.deepcopy(profile)]
            workspace.refresh()
            workspace.select(profile["id"])
            window.tabs.setCurrentWidget(workspace)
            window.show()

            def settle() -> None:
                app.processEvents()
                QTest.qWait(60)
                app.processEvents()

            def rect_in(widget, parent):
                return widget.rect().translated(widget.mapTo(parent, QPoint()))

            def geometry_chain(widget):
                result = []
                while widget is not None and len(result) < 8:
                    result.append({
                        "type": type(widget).__name__, "name": widget.objectName(),
                        "geometry": widget.geometry().getRect(),
                        "minimum": (widget.minimumWidth(), widget.minimumHeight()),
                        "minimum_hint": (widget.minimumSizeHint().width(), widget.minimumSizeHint().height()),
                        "size_hint": (widget.sizeHint().width(), widget.sizeHint().height()),
                        "height_for_width": widget.heightForWidth(widget.width()),
                    })
                    widget = widget.parentWidget()
                return result

            def check_geometry(size) -> None:
                window.resize(*size)
                for section in (workspace.editor, workspace.details, workspace.transfers):
                    section.button.setChecked(True)
                settle()
                assert (window.width(), window.height()) == size
                tiles = workspace.summary_tiles
                assert len(tiles) == 5, size
                for tile in tiles:
                    assert tile.isVisible(), size
                    assert tile.minimumHeight() >= 148
                    tile_required = tile.heightForWidth(tile.width())
                    if tile_required < 0:
                        tile_required = tile.minimumSizeHint().height()
                    assert tile.height() >= max(148, tile.minimumHeight(), tile_required), (
                        size, tile.key, geometry_chain(tile),
                        "value", geometry_chain(tile.value_label)[:1],
                    )
                    # Merely being visible is insufficient: the old layout left
                    # these labels technically visible at zero pixels high.
                    labels = tile.findChildren(QLabel)
                    assert labels
                    for label in labels:
                        if label.isHidden():
                            continue
                        bounds = rect_in(label, tile)
                        assert bounds.width() > 0 and bounds.height() > 0, (size, label.text(), bounds)
                        assert tile.rect().contains(bounds), (size, label.text(), bounds, tile.rect())
                        required = label.heightForWidth(label.width())
                        if required < 0:
                            required = label.minimumSizeHint().height()
                        assert label.height() >= required > 0, (size, label.text(), label.height(), required)
                    value = tile.value_label
                    required = value.heightForWidth(value.width())
                    if required < 0:
                        required = value.minimumSizeHint().height()
                    assert value.height() >= required > 0, (size, value.text(), value.height(), required)
                    assert tile.icon_label.height() >= 24
                    if tile.key == "lcd":
                        assert "Matrix" in value.text()
                        assert "80" not in value.text()
                        posters = [label for label in labels if not label.pixmap().isNull() and label is not tile.icon_label]
                        assert len(posters) == 1 and posters[0].height() == 58
                tile_rects = [rect_in(tile, workspace.summary_container) for tile in tiles]
                for index, bounds in enumerate(tile_rects):
                    assert all(not bounds.intersects(other) for other in tile_rects[index + 1:]), size
                sections = (workspace.editor, workspace.details, workspace.transfers)
                section_rects = [rect_in(section, workspace.content) for section in sections]
                summary_bounds = rect_in(workspace.summary_container, workspace.content)
                for index, bounds in enumerate(section_rects):
                    assert all(not bounds.intersects(other) for other in section_rects[index + 1:]), size
                    assert not summary_bounds.intersects(bounds), size
                    assert sections[index].body.isVisible()
                    body = sections[index].body
                    required = body.heightForWidth(body.width())
                    if required < 0:
                        required = body.minimumSizeHint().height()
                    assert body.height() >= required > 0, (
                        size, sections[index].button.text(), geometry_chain(sections[index].body),
                        "header", geometry_chain(sections[index].button)[:1],
                        "labels", [
                            (label.text(), label.geometry().getRect(), label.minimumSizeHint().height(),
                             label.heightForWidth(label.width()))
                            for label in sections[index].body.findChildren(QLabel) if not label.isHidden()
                        ],
                    )
                    for label in body.findChildren(QLabel):
                        if label.isHidden():
                            continue
                        required = label.heightForWidth(label.width())
                        if required < 0:
                            required = label.minimumSizeHint().height()
                        assert label.height() >= required > 0, (size, label.text(), label.height(), required)
                        assert body.rect().contains(rect_in(label, body)), (size, label.text(), geometry_chain(label))
                    for control in body.findChildren(QAbstractButton):
                        if control.isHidden():
                            continue
                        hint = control.minimumSizeHint()
                        assert control.height() >= max(control.minimumHeight(), hint.height()), (
                            size, control.text(), geometry_chain(control)
                        )
                        assert control.width() >= hint.width(), (size, control.text(), control.width(), hint.width())
                        assert body.rect().contains(rect_in(control, body)), (size, control.text(), geometry_chain(control))
                assert window.profile_bundle_controller.buttons
                viewport = workspace.scroll.viewport()
                for control in window.profile_bundle_controller.buttons:
                    workspace.scroll.ensureWidgetVisible(control, 8, 8)
                    settle()
                    assert viewport.rect().contains(rect_in(control, viewport)), (size, control.text())
                if size == (1000, 900):
                    assert workspace.scroll.verticalScrollBar().maximum() > 0
                workspace.scroll.verticalScrollBar().setValue(0)
                settle()

            with patch.object(window, "apply_profile_payload", side_effect=AssertionError("browsing applied hardware")), \
                 patch.object(window, "save_profiles", side_effect=AssertionError("browsing rewrote profiles")):
                for size in ((2551, 1337), (1440, 1000), (1000, 900)):
                    check_geometry(size)
                    if render_dir:
                        render_dir.mkdir(parents=True, exist_ok=True)
                        assert window.grab().save(str(render_dir / f"profiles-expanded-{size[0]}x{size[1]}.png"))

                if render_dir:
                    # Capture both normal entry and the expanded transfer
                    # controls from the same real Qt page and saved fixture.
                    for theme in ("dark", "light"):
                        window.theme_mode = theme
                        window.apply_theme()
                        check_geometry((2551, 1337))
                        assert window.grab().save(str(render_dir / f"profiles-{theme}-expanded-top-2551x1337.png"))
                        workspace.scroll.ensureWidgetVisible(workspace.transfers, 12, 18)
                        settle()
                        assert window.grab().save(str(render_dir / f"profiles-{theme}-transfers-2551x1337.png"))
                        for section in (workspace.editor, workspace.details, workspace.transfers):
                            section.button.setChecked(False)
                        workspace.scroll.verticalScrollBar().setValue(0)
                        settle()
                        assert window.grab().save(str(render_dir / f"profiles-{theme}-overview-2551x1337.png"))

                workspace.select("builtin-quiet")
                for action in (workspace.edit, workspace.rename, workspace.delete, workspace.update):
                    assert not action.isEnabled()
                for action in (workspace.apply, workspace.duplicate, workspace.export):
                    assert action.isEnabled()
                workspace.select(profile["id"])
                workspace.editor.button.setChecked(True)
                window.profile_name_input.setText("Unsaved profile name")
                window.profile_description_input.setText("Unsaved profile description")
                for key, check in window.profile_section_checks.items():
                    check.setChecked(key in {"cooling", "rgb", "design"})
                draft = (
                    window.profile_name_input.text(), window.profile_description_input.text(),
                    window.profile_category_combo.currentData(),
                    {key: check.isChecked() for key, check in window.profile_section_checks.items()},
                )
                for language in ("de", "en", "es", "fr"):
                    window.apply_ui_language(language, persist=False, log_change=False)
                    for theme in ("dark", "light"):
                        window.theme_mode = theme
                        window.apply_theme()
                        check_geometry((1440, 1000) if theme == "dark" else (1000, 900))
                        assert window.selected_profile()["id"] == profile["id"]
                        assert workspace.editor.button.isChecked()
                        assert (
                            window.profile_name_input.text(), window.profile_description_input.text(),
                            window.profile_category_combo.currentData(),
                            {key: check.isChecked() for key, check in window.profile_section_checks.items()},
                        ) == draft
                        assert window.user_profiles == [profile]
                        assert all(action.isEnabled() for action in (
                            workspace.edit, workspace.rename, workspace.delete, workspace.update,
                        ))
                # A new, unsaved profile has no selected ID. In particular,
                # language refresh must not silently select an active profile
                # and turn the Update action into an overwrite operation.
                window.current_profile_id = profile["id"]
                workspace.new_profile()
                window.profile_name_input.setText("Entirely new unsaved profile")
                window.profile_description_input.setText("New draft must stay independent")
                for key, check in window.profile_section_checks.items():
                    check.setChecked(key == "rgb")
                new_draft = (
                    window.profile_name_input.text(), window.profile_description_input.text(),
                    window.profile_category_combo.currentData(),
                    {key: check.isChecked() for key, check in window.profile_section_checks.items()},
                )
                for language in ("de", "en", "es", "fr"):
                    window.apply_ui_language(language, persist=False, log_change=False)
                    for theme in ("dark", "light"):
                        window.theme_mode = theme
                        window.apply_theme()
                        window.resize(*((1440, 1000) if theme == "dark" else (1000, 900)))
                        settle()
                        assert window.selected_profile() is None
                        assert not workspace.update.isEnabled()
                        assert not workspace.apply.isEnabled()
                        assert workspace.editor.button.isChecked()
                        assert (
                            window.profile_name_input.text(), window.profile_description_input.text(),
                            window.profile_category_combo.currentData(),
                            {key: check.isChecked() for key, check in window.profile_section_checks.items()},
                        ) == new_draft
                        assert window.user_profiles == [profile]
            captured = {"rgb": {"studio_effect": "code_rain", "studio_brightness": 55}}
            with patch.object(window, "capture_profile_payload_from_editor", return_value=captured) as capture, \
                 patch.object(window, "save_profiles") as save, \
                 patch.object(window, "apply_profile_payload", side_effect=AssertionError("saving applied hardware")):
                window.create_profile_from_current()
                selected = window.selected_profile()
                assert selected is not None and selected["id"] == window.current_profile_id
                assert selected["id"] != profile["id"]
                assert selected["name"] == new_draft[0]
                assert selected["description"] == new_draft[1]
                assert selected["payload"] == captured
                assert workspace.new_draft is False
                assert workspace.update.isEnabled()
                capture.assert_called_once_with()
                save.assert_called_once_with()
                assert window.user_profiles[0] == profile
                assert len(window.user_profiles) == 2
                window.apply_ui_language("en", persist=False, log_change=False)
                settle()
                assert window.selected_profile()["id"] == selected["id"]
                assert workspace.update.isEnabled()
            print("profile geometry: 3 sizes, 4 languages, 2 themes passed")
        finally:
            if isValid(window):
                window.background_widget.media_background.shutdown()
                window.design_hub_page.shutdown()
                studio = window.thermalright_display_studio
                studio.shutdown_started = True
                studio.startup_apply_active = False
                studio.thumbnail_shutting_down = True
                studio.media_preview.shutdown()
                studio.lcd_runtime.shutdown()
                studio.game_activity.shutdown()
                studio.gallery_preparation.shutdown()
                for timer in window.findChildren(QTimer):
                    timer.stop()
                window.snapshot_manager_page.stop_processes()
                window.process_runtime.shutdown()
                window.ui_performance.shutdown()
                window.backend.shutdown()
                stop_remaining(window)
                assert all(p.state() == QProcess.ProcessState.NotRunning for p in window.findChildren(QProcess))
                window.deleteLater()
                QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true", required=True)
    parser.add_argument("--runtime", type=Path, default=ROOT / "src")
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--presentation", action="store_true", help="Enable the bundled Matrix backdrop for optional visual evidence.")
    arguments = parser.parse_args()
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    _worker(arguments.runtime.resolve(), arguments.render_dir, arguments.presentation)
