"""Real selected-video playback, exposed viewports and confirmed-design fallback."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


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
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication, QScrollArea
        from modules.lcd_media_manager.v1_0.preview_visibility import exposed
        import kraken_control as application
        def wait_until(predicate, timeout=2.0):
            deadline = time.monotonic() + timeout
            while not predicate() and time.monotonic() < deadline:
                QTest.qWait(20)
            return bool(predicate())
        application.KrakenControl.check_dependencies = lambda self: ['hardware-free-preview']
        app = QApplication([]); app.setQuitOnLastWindowClosed(False)
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
        window.tabs.setCurrentIndex(window.tabs.indexOf(window.lcd_scroll_page))
        studio.media_preview.refresh()
        def expose_studio_canvas():
            window.lcd_scroll_page.ensureWidgetVisible(studio.canvas)
            app.processEvents()
            return exposed(studio.canvas)
        assert wait_until(expose_studio_canvas, timeout=5.0)
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
        window.lcd_scroll_page.verticalScrollBar().setValue(0)
        QTest.qWait(100)
        assert not exposed(studio.canvas) and not studio.media_preview.video._active
        assert not studio.layer2_motion_timer.isActive()

        window.tabs.setCurrentIndex(window.display_effects_page_index)
        area = next(a for a in page.findChildren(QScrollArea) if a.widget() and a.widget().isAncestorOf(page.preview_canvas))
        area.ensureWidgetVisible(page.preview_canvas)
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
        window.tabs.setCurrentIndex(window.case_page_index); QTest.qWait(100)
        assert not page._preview_override and not page.video_preview._active
        window.tabs.setCurrentIndex(window.display_effects_page_index); QTest.qWait(150)
        assert page.video_preview.source_path == first.resolve()
        # A long content page allows moving the entire preview out of view.
        area.widget().setMinimumHeight(1800); QTest.qWait(80)
        area.verticalScrollBar().setValue(area.verticalScrollBar().maximum()); QTest.qWait(100)
        assert not exposed(page.preview_canvas) and not page.video_preview._active
        area.ensureWidgetVisible(page.preview_canvas); QTest.qWait(100)
        assert page.video_preview._active
        area.widget().setMinimumHeight(0)
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
        print('selected video/viewport/confirmed fallback/four languages: passed', flush=True)


def test_real_preview_visibility_and_selection_fallback():
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child'], cwd=ROOT,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'four languages: passed' in result.stdout


if __name__ == '__main__' and '--child' in sys.argv: exercise()
