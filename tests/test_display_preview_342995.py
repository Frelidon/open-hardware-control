"""Real selected-video playback, exposed viewports and confirmed-design fallback."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
# The offscreen QPA intentionally does not promise window exposure on every
# runner. The minimal headless QPA keeps deterministic widget/viewport geometry
# so this test can exercise the real exposure contract without a display server.
os.environ.setdefault('QT_QPA_PLATFORM', 'minimal')


def test_light_bands_use_real_supersampling_and_no_cold_edge_stripes():
    from PySide6.QtWidgets import QApplication
    from modules.display_effects.v1_11.light_bands_renderer import render_light_bands_frame
    app = QApplication.instance() or QApplication([])
    source = render_light_bands_frame('right', 0, width=4800, height=2160)
    assert (source.width(), source.height()) == (4800, 2160)
    image = render_light_bands_frame('right', 0)
    # A dim band formerly retained a blue-grey pen, brighter than its body.
    for x in range(1500, 1505):
        color = image.pixelColor(x, 360)
        assert color.blue() <= 22, (x, color.name())
    app.processEvents()


def test_null_motion_does_not_rebuild_or_move_live_blocks():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QPixmap
    from modules.lcd_levita.v1_7.layout_canvas import ThermalrightCanvas
    app = QApplication.instance() or QApplication([])
    canvas = ThermalrightCanvas(lambda *_: None, lambda: None, lambda *_: None)
    before = tuple(canvas.scene().items())
    for _ in range(20): canvas.set_motion_layer(QPixmap())
    assert tuple(canvas.scene().items()) == before
    canvas.close(); app.processEvents()


def test_late_ui_tab_callbacks_are_cancelled_with_deleted_host(monkeypatch):
    from PySide6.QtCore import QCoreApplication, QEvent, QSettings
    from PySide6.QtWidgets import QApplication, QTabWidget, QWidget
    from modules.ui_performance.v1_1.controller import UiPerformanceController
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory(prefix='ohc-tabs95-') as temp:
        host = QWidget()
        host.settings = QSettings(str(Path(temp) / 'settings.ini'), QSettings.Format.IniFormat)
        controller = UiPerformanceController(host)
        errors = []
        monkeypatch.setattr(sys, 'excepthook', lambda *args: errors.append(args))
        QTabWidget(host)  # Queues a deferred child/tab scan.
        host.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
        controller._attach_new_tabs()  # An already dispatched stale callback is also harmless.
        assert not errors


def exercise():
    with tempfile.TemporaryDirectory(prefix='ohc-preview95-') as temp:
        for key in ('XDG_CONFIG_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME',
                    'OHC_DESKTOP_DESIGN_CONFIG_DIR', 'OHC_DESKTOP_DESIGN_STATE_DIR'):
            os.environ[key] = str(Path(temp) / key)
        os.environ['OHC_DISABLE_HARDWARE_IO'] = '1'
        from PySide6.QtCore import QSettings, Qt
        from PySide6.QtGui import QPixmap
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication, QScrollArea, QWidget
        from modules.lcd_media_manager.v1_1.preview_visibility import exposed
        import modules.display_effects.v1_11.page as display_effects_page_module
        import modules.lcd_levita.v1_7.media_preview as levita_media_preview_module
        import kraken_control as application
        def wait_until(predicate, timeout=2.0):
            deadline = time.monotonic() + timeout
            while not predicate() and time.monotonic() < deadline:
                QTest.qWait(20)
            return bool(predicate())
        application.KrakenControl.check_dependencies = lambda self: ['hardware-free-preview']
        settings = QSettings(application.ORG_NAME, application.APP_NAME)
        settings.setValue('cooling/hardware_kind', application.LEVITA_COOLER_KEY)
        settings.sync()
        app = QApplication([]); app.setQuitOnLastWindowClosed(False)

        # Verify the real geometry contract in a small, deterministic hierarchy.
        # The complete application is intentionally not used for this assertion:
        # headless QPA plugins expose different virtual screen sizes and window
        # frame policies although the scroll viewport semantics are identical.
        visibility_host = QWidget(); visibility_host.resize(320, 240)
        visibility_area = QScrollArea(visibility_host); visibility_area.setGeometry(0, 0, 300, 220)
        visibility_content = QWidget(); visibility_content.setFixedSize(280, 800)
        visibility_probe = QWidget(visibility_content); visibility_probe.setGeometry(20, 650, 100, 80)
        visibility_area.setWidget(visibility_content)
        visibility_host.show(); app.processEvents()
        assert not exposed(visibility_probe)
        visibility_area.ensureWidgetVisible(visibility_probe, 0, 0); app.processEvents()
        assert wait_until(lambda: exposed(visibility_probe))
        visibility_area.verticalScrollBar().setValue(0); app.processEvents()
        assert not exposed(visibility_probe)
        visibility_host.close()

        # Keep the full application integration independent of a headless
        # runner's virtual desktop geometry. The real exposure predicate above
        # is covered separately; here a controlled signal verifies that both
        # preview drivers actually pause and resume their production pipelines.
        visible_previews = set()
        preview_exposed = lambda widget: widget in visible_previews
        levita_media_preview_module.exposed = preview_exposed
        display_effects_page_module.exposed = preview_exposed
        window = application.KrakenControl()
        window.settings.setValue('setup/completed', True)
        window.settings.setValue('dependencies/desktop_design_offer_330', True)
        # Stay within Qt's smallest CI offscreen screen. A window larger than
        # that virtual screen can never satisfy the real parent-intersection
        # visibility contract even after the scroll area exposes the canvas.
        window.resize(760, 700); window.show()
        studio = window.thermalright_display_studio
        page = window.display_effects_page
        first = ROOT / 'src/assets/levita-designs/ohc-3d-quantum-core-10s.mp4'
        second = ROOT / 'src/assets/levita-designs/ohc-3d-neon-apex-10s.mp4'
        studio.hardware_design_combo.setCurrentIndex(0)
        studio._select_effect_media(first, 'Quantum')
        page._open_lcd_studio()
        assert window.lcd_workspace.device.currentData() == 'thermalright'
        assert studio.workspace_tabs.currentIndex() == 1
        visible_previews.add(studio.canvas)
        studio.media_preview.refresh()
        assert wait_until(
            lambda: studio.media_preview.video is not None and studio.media_preview.video._active
        )
        positions = []
        for _ in range(7):
            QTest.qWait(100)
            positions.append(studio.canvas.mapToGlobal(studio.canvas.rect().topLeft()).y())
        assert max(positions) - min(positions) <= 2, 'First layout opening changes preview geometry'
        assert not studio.media_preview.video.latest_image.isNull()
        background = studio.canvas._background.cacheKey()
        QTest.qWait(250)
        assert studio.canvas._background.cacheKey() != background, 'Selected video needs no hover'
        studio.media_preview.capture(); studio.media_preview.confirm()
        frozen = studio.media_preview.applied
        studio._select_effect_media(second, 'Neon')
        studio.media_preview.capture()  # An unconfirmed/failed apply cannot replace the live snapshot.
        assert frozen.media == first and studio.media_preview.applied is frozen
        visible_previews.discard(studio.canvas); studio.media_preview.refresh(); QTest.qWait(100)
        assert not studio.media_preview.video._active
        assert not studio.layer2_motion_timer.isActive()

        visible_previews.add(page.preview_canvas)
        window.tabs.setCurrentIndex(window.display_effects_page_index)
        area = next(a for a in page.findChildren(QScrollArea) if a.widget() and a.widget().isAncestorOf(page.preview_canvas))
        area.ensureWidgetVisible(page.preview_canvas)
        page._refresh_preview_driver()
        QTest.qWait(180)
        assert page.video_preview.source_path == first.resolve()
        assert not page._preview_override and not any(b.isChecked() for b in page.stock_library._design_cards.values())
        assert not page.apply_button.isEnabled() and not page.remember_button.isEnabled()
        assert page.video_preview._active
        startup = tuple(studio.settings.value(key, '') for key in
                        ('thermalright/start_media', 'thermalright/profile_pending_media'))
        page.stock_library._select_design_card('ohc-light-bands')
        QTest.qWait(150)
        selected = page.stock_library.current_video()
        assert page._preview_override and page.video_preview.source_path == selected
        assert studio.media_preview.applied is frozen and studio.current_media_path() == second
        QTest.mouseClick(page.preview_canvas.viewport(), Qt.MouseButton.LeftButton)
        QTest.qWait(100)
        assert not page._preview_override and page.video_preview.source_path == first.resolve()
        page.stock_library._select_design_card('ohc-light-bands'); QTest.qWait(100)
        page.clear_button.click(); QTest.qWait(100)
        assert not page._preview_override and page.video_preview.source_path == first.resolve()
        page.stock_library._select_design_card('ohc-light-bands'); QTest.qWait(100)
        visible_previews.discard(page.preview_canvas); page._refresh_preview_driver()
        window.tabs.setCurrentIndex(window.case_page_index); QTest.qWait(100)
        assert not page._preview_override and not page.video_preview._active
        visible_previews.add(page.preview_canvas)
        window.tabs.setCurrentIndex(window.display_effects_page_index); QTest.qWait(150)
        page._refresh_preview_driver()
        assert page.video_preview.source_path == first.resolve()
        visible_previews.discard(page.preview_canvas); page._refresh_preview_driver(); QTest.qWait(100)
        assert not page.video_preview._active
        visible_previews.add(page.preview_canvas); page._refresh_preview_driver(); QTest.qWait(100)
        assert page.video_preview._active
        assert startup == tuple(studio.settings.value(key, '') for key in
                                ('thermalright/start_media', 'thermalright/profile_pending_media'))

        # A confirmed active catalog effect remains correctly mirrored on return.
        studio._select_effect_media(selected, 'Light Bands')
        studio.media_preview.capture(); studio.media_preview.confirm()
        QTest.qWait(100)
        assert not page._preview_override and page.video_preview.source_path == selected
        assert page.stock_library._design_cards['ohc-light-bands'].isChecked()
        render = os.environ.get('OHC_UI_RENDER_DIR')
        for language in ('de', 'en', 'es', 'fr'):
            window.apply_ui_language(language, log_change=False); QTest.qWait(80)
            assert page.clear_button.text() == window.tr_static('Auswahl aufheben')
            assert page.video_preview.source_path == selected and not page._preview_override
            assert page.stock_library.description_label.text() == window.tr_static(page.stock_library.current_design().description)
            assert page.stock_library.variant_combo.currentText() == window.tr_static(page.stock_library.current_variant().label)
            if render and language in {'de', 'fr'}:
                output = Path(render); output.mkdir(parents=True, exist_ok=True)
                window.grab().save(str(output / f'effects-live-{language}.png'))
        window.mainboard_channels = {}
        window.snapshot_manager_page.stop_processes()
        window.perform_orderly_hardware_exit('preview regression')
        window.backend.shutdown(); window.close(); app.processEvents()
        print('viewport/selected video/pause-resume/confirmed fallback/four languages: passed', flush=True)


def test_real_preview_visibility_and_selection_fallback():
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child'], cwd=ROOT,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                                 'QT_QPA_PLATFORM': 'minimal'},
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'four languages: passed' in result.stdout


if __name__ == '__main__' and '--child' in sys.argv: exercise()
