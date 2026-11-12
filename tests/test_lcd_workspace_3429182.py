"""LCD UI navigation preserves drafts and hardware ownership in real Qt.

The subprocess also catches native layout-cache failures during full-window
painting; every setting and process is isolated before importing the app.
"""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_lcd_workspaces_preserve_drafts_and_render_narrow_without_hardware_io():
    environment = os.environ.copy()
    environment.update(QT_QPA_PLATFORM='offscreen', PYTHONDONTWRITEBYTECODE='1')
    completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker'],
        cwd=ROOT, env=environment, capture_output=True, text=True, timeout=150)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert 'lcd workspaces: contracts, drafts, visibility and full-window Qt passed' in completed.stdout


def _worker():
    import tempfile
    from PySide6.QtCore import QCoreApplication, QEvent, QProcess, QSettings, QTimer, Signal
    from PySide6.QtTest import QTest
    from PySide6.QtGui import QMovie
    from PySide6.QtWidgets import QApplication, QPushButton, QWidget
    from shiboken6 import isValid

    with tempfile.TemporaryDirectory(prefix='ohc-lcd-workspace-') as temporary:
        isolated = Path(temporary)
        os.environ.update(OHC_DISABLE_HARDWARE_IO='1', XDG_CONFIG_HOME=str(isolated/'config'),
            XDG_STATE_HOME=str(isolated/'state'), OHC_DESKTOP_DESIGN_CONFIG_DIR=str(isolated/'desktop-config'),
            OHC_DESKTOP_DESIGN_STATE_DIR=str(isolated/'desktop-state'), OHC_WALLPAPER_STEAM_LIBRARY=str(isolated/'Steam'))
        sys.path.insert(0, str(ROOT/'src'))
        import kraken_control as application
        from modules.application_shutdown.v1_1.qt_processes import stop_remaining
        from modules.lcd_workspace.v1_0 import LcdDeviceShell, LegacyTileGroups
        application.KrakenControl.check_dependencies = lambda _self: ['isolated-lcd-workspace']
        app = QApplication.instance() or QApplication([])

        class FakeArea(QWidget):
            orderChanged = Signal(object)
            def __init__(self, _scope, sections, order):
                super().__init__(); self.keys = [key for key, _widget, _span in sections]
                self.sequence = [key for key in order if key in self.keys]; self.visible = {}
            def set_key_visible(self, key, visible): self.visible[key] = visible
            def prioritize(self, keys): self.sequence = [key for key in keys if key in self.keys]

        keys = ['content', 'profiles', 'preview', 'hardware', 'clock', 'display', 'startup']
        saved = ['clock', 'thermalright', 'content', 'preview', 'startup', 'profiles', 'hardware', 'display']
        legacy = LegacyTileGroups(FakeArea, [(key, QWidget(), 1) for key in keys], saved)
        changes = []; legacy.orderChanged.connect(changes.append)
        assert legacy.order() == saved
        legacy.prioritize(['thermalright', 'startup'])
        assert legacy.order() == ['thermalright', 'startup', *[key for key in saved if key not in {'thermalright','startup'}]]
        assert not changes
        legacy.set_key_visible('preview', False)
        assert all(area.visible['preview'] is False for area in legacy.areas)
        shell = LcdDeviceShell(QWidget(), legacy, True)
        legacy.set_key_visible('thermalright', False); assert shell.device.currentData() == 'kraken'
        legacy.set_key_visible('thermalright', True); assert shell.device.currentData() == 'thermalright'
        shell.device.setCurrentIndex(1); shell.device.activated.emit(1)
        legacy.set_key_visible('thermalright', False); legacy.set_key_visible('thermalright', True)
        assert shell.device.currentData() == 'kraken'
        legacy.reset_order(); assert legacy.order() == ['thermalright', *keys] and len(changes) == 1
        shell.deleteLater(); QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

        settings = QSettings(application.ORG_NAME, application.APP_NAME)
        for key, value in {'setup/completed':True, 'dependencies/desktop_design_offer_330':True,
            'cooling/hardware_kind':application.LEVITA_COOLER_KEY,
            'performance/transitions_enabled':False, 'ui/background_enabled':False}.items():
            settings.setValue(key, value)
        settings.sync(); window = application.KrakenControl()
        try:
            assert window.hardware_io_disabled
            studio = window.thermalright_display_studio
            identities = tuple(id(widget) for widget in (studio.canvas, studio.media_combo,
                studio.hardware_design_combo, studio.library_manager_panel, studio.layer2_inline_editor))
            studio.layer2_inline_text.setText('Unsaved LCD draft')
            selection = (studio.current_media_path(), studio.current_hardware_design_path(),
                         studio.layer2_offset_x.value(), studio.layer2_offset_y.value())
            settings_before = {key:settings.value(key) for key in settings.allKeys() if key.startswith('thermalright/')}
            calls = []
            studio.apply_design = lambda *_args: calls.append('apply')
            window.lcd_workspace.device.setCurrentIndex(0)
            ohc = studio.media_category.findData('ohc')
            assert ohc >= 0
            studio.media_category.setCurrentIndex(ohc)
            for language in ('de', 'en', 'es', 'fr'):
                window.apply_ui_language(language, persist=False, log_change=False)
                for size in ((2551,1337), (1000,900)):
                    window.resize(*size); window.show(); window.tabs.setCurrentIndex(3)
                    for index in range(3):
                        studio.workspace_tabs.setCurrentIndex(index)
                        for section in (studio.source_section, studio.geometry_section, studio.overlays_section,
                                        studio.performance_section, studio.maintenance_section):
                            section.button.setChecked(True)
                        app.processEvents(); QTest.qWait(35); app.processEvents()
                        assert not window.grab().isNull()
                        page = window.tabs.widget(3)
                        assert page.widget().width() <= page.viewport().width(), (language, size, index,
                            page.widget().width(), page.viewport().width())
                        assert studio.top_apply_button.isVisible()
                        assert bool(studio.workspace_output_status.text())
                        assert 'USB' in studio.top_apply_button.toolTip()
                        assert studio.canvas.width() == 880 and studio.canvas.height() == 396
                        assert studio.layer2_editor_bar.height() <= 140
                        if index != 1:
                            assert not studio.layer2_motion_timer.isActive()
                            if studio.media_preview.video is not None:
                                assert not studio.media_preview.video._source_loaded
                        assert studio.layer2_inline_text.text() == 'Unsaved LCD draft'
                    window.lcd_workspace.device.setCurrentIndex(1)
                    for index in range(3):
                        window.lcd_tile_area.tabs.setCurrentIndex(index)
                        app.processEvents(); assert not window.grab().isNull()
                    window.lcd_workspace.device.setCurrentIndex(0)
                    studio.workspace_tabs.setCurrentIndex(1)
                    window.tabs.setCurrentIndex(4); app.processEvents()
                    assert not window.grab().isNull()
                    window.tabs.setCurrentIndex(3); app.processEvents(); QTest.qWait(65); app.processEvents()
                    assert studio.workspace_tabs.currentIndex() == 1
                    assert not studio.gallery_preparation.timer.isActive()
                    assert not studio.hover_preview_timer.isActive()
                    studio._relayout_design_galleries()
                    assert not studio.gallery_preparation.timer.isActive()
                    studio._rebuild_media_cards(studio._visible_media_entries, reuse=True)
                    assert 'media' in studio.gallery_preparation.jobs
                    assert not studio.gallery_preparation.timer.isActive()
                    studio.workspace_tabs.setCurrentIndex(0)
                    for _turn in range(80):
                        app.processEvents(); QTest.qWait(15)
                        if not studio.gallery_preparation.jobs: break
                    assert not studio.gallery_preparation.jobs
                    assert studio.media_card_buttons and studio.hardware_card_buttons
            assert tuple(id(widget) for widget in (studio.canvas, studio.media_combo,
                studio.hardware_design_combo, studio.library_manager_panel, studio.layer2_inline_editor)) == identities
            # Existing entry points now expose the correct inner workspace,
            # while retaining the user's chosen device on the library shortcut.
            window.apply_ui_language('de', persist=False, log_change=False)
            shortcut = next(button for button in window.findChildren(QPushButton, 'dashboardAction')
                            if 'LCD ändern' in button.text())
            for family in ('thermalright', 'kraken'):
                window.lcd_workspace.select_device(family)
                studio.workspace_tabs.setCurrentIndex(2); window.lcd_tile_area.tabs.setCurrentIndex(2)
                window.tabs.setCurrentIndex(0)
                before_link = {key:settings.value(key) for key in settings.allKeys()}
                shortcut.click()
                assert window.tabs.currentIndex() == 3
                assert window.lcd_workspace.device.currentData() == family
                worktabs = studio.workspace_tabs if family == 'thermalright' else window.lcd_tile_area.tabs
                assert worktabs.currentIndex() == 0
                assert {key:settings.value(key) for key in settings.allKeys()} == before_link
            before_link = {key:settings.value(key) for key in settings.allKeys()}
            window.display_effects_page._open_lcd_studio()
            assert window.tabs.currentIndex() == 3
            assert window.lcd_workspace.device.currentData() == 'thermalright'
            assert studio.workspace_tabs.currentIndex() == 1
            window.lcd_tile_area.set_key_visible('thermalright', False)
            assert window.lcd_workspace.device.currentData() == 'thermalright'
            assert {key:settings.value(key) for key in settings.allKeys()} == before_link

            # QMovie is local UI playback, independent of the physical LCD.
            # All three existing preview starters must stay stopped in Library.
            from PIL import Image
            clip = isolated/'preview.gif'
            Image.new('RGB', (24,24), 'blue').save(clip, save_all=True,
                append_images=[Image.new('RGB', (24,24), 'red')], duration=80, loop=0)
            window.lcd_tile_area.set_key_visible('preview', True)
            window.lcd_round_preview_available = True
            window.lcd_workspace.select_device('kraken'); window.lcd_tile_area.tabs.setCurrentIndex(0)
            for starter in (window.show_animated_round_preview, window.show_hardware_animation_preview,
                            window.show_lcd_layer_preview):
                starter(clip)
                movies = [movie for movie in (window.lcd_preview_movie, window.hardware_animation_movie) if movie is not None]
                assert all(movie.isValid() and movie.state() == QMovie.MovieState.NotRunning for movie in movies)
            window.lcd_tile_area.tabs.setCurrentIndex(1); app.processEvents(); QTest.qWait(20)
            assert window.lcd_preview_box.isVisible()
            assert all(movie.state() == QMovie.MovieState.Running for movie in movies)
            window.lcd_scroll_page.verticalScrollBar().setValue(window.lcd_scroll_page.verticalScrollBar().maximum())
            window.update_lcd_sticky_preview_visibility()
            assert window.lcd_sticky_preview.isVisible()
            for target in ('operation', 'levita'):
                if target == 'operation': window.lcd_tile_area.tabs.setCurrentIndex(2)
                else: window.lcd_workspace.select_device('thermalright')
                app.processEvents()
                assert all(movie.state() == QMovie.MovieState.Paused for movie in movies)
                assert not window.lcd_sticky_preview.isVisible()
                if target == 'operation':
                    window.lcd_tile_area.tabs.setCurrentIndex(1); app.processEvents()
                    assert all(movie.state() == QMovie.MovieState.Running for movie in movies)
            assert (studio.current_media_path(), studio.current_hardware_design_path(),
                    studio.layer2_offset_x.value(), studio.layer2_offset_y.value()) == selection
            assert {key:settings.value(key) for key in settings.allKeys() if key.startswith('thermalright/')} == settings_before
            assert not calls
            print('lcd workspaces: contracts, drafts, visibility and full-window Qt passed', flush=True)
        finally:
            if isValid(window):
                for movie in (window.lcd_preview_movie, window.hardware_animation_movie):
                    if movie is not None: movie.stop()
                window.background_widget.media_background.shutdown(); window.design_hub_page.shutdown()
                studio.shutdown_started=True; studio.startup_apply_active=False; studio.thumbnail_shutting_down=True
                studio.media_preview.shutdown(); studio.lcd_runtime.shutdown(); studio.game_activity.shutdown(); studio.gallery_preparation.shutdown()
                for timer in window.findChildren(QTimer): timer.stop()
                window.snapshot_manager_page.stop_processes(); window.process_runtime.shutdown()
                window.ui_performance.shutdown(); window.backend.shutdown(); stop_remaining(window)
                assert all(process.state()==QProcess.ProcessState.NotRunning for process in window.findChildren(QProcess))
                window.deleteLater(); QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)


if __name__ == '__main__': _worker()
