"""One real GPU page: draft retention, curve geometry and existing safe routes."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_one_page_gpu_workspace_retains_drafts_and_control_guards():
    environment = os.environ.copy()
    environment.update(QT_QPA_PLATFORM='offscreen', PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker'],
        cwd=ROOT, env=environment, capture_output=True, text=True, timeout=100)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'GPU workspace: three sizes, four languages, two themes, drafts and guards passed' in result.stdout


def _worker(render_dir=None):
    import copy
    import tempfile
    from PySide6.QtCore import QCoreApplication, QEvent, QPoint, QProcess, QSettings, QTimer
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QTabWidget
    from shiboken6 import isValid

    class FixtureLact:
        writes = 0
        def devices(self): return [{'id': '1002:fixture', 'name': 'GPU UI fixture · Beispieldaten', 'device_type': 'Dedicated'}]
        def config(self, _ident): return {'power_cap': 200.0, 'fan_control_enabled': False}
        def stats(self, _ident):
            return {'power': {'cap_min': 100, 'cap_default': 220, 'cap_max': 250, 'cap_current': 200, 'average': 86},
                    'temps': {'edge': {'current': 52}, 'junction': {'current': 66}},
                    'fan': {'speed_current': 1240, 'temperature_range': [25, 100], 'pwm_max': 254},
                    'busy_percent': 47, 'clockspeed': {'gpu_clockspeed': 2300}}
        def clocks(self, _ident): return {}
        def request(self, command, _arguments):
            assert command == 'device_info'
            return {'name': 'GPU UI fixture'}
        def overdrive_enabled(self): return True
        def set_config(self, *_args):
            self.writes += 1; raise AssertionError('layout must not write GPU state')
        def pending(self, *_args):
            self.writes += 1; raise AssertionError('layout must not commit GPU state')

    with tempfile.TemporaryDirectory(prefix='ohc-gpu-workspace-') as temporary:
        isolated = Path(temporary)
        os.environ.update(OHC_DISABLE_HARDWARE_IO='1', XDG_CONFIG_HOME=str(isolated/'config'),
            XDG_STATE_HOME=str(isolated/'state'), OHC_DESKTOP_DESIGN_CONFIG_DIR=str(isolated/'desktop-config'),
            OHC_DESKTOP_DESIGN_STATE_DIR=str(isolated/'desktop-state'), OHC_WALLPAPER_STEAM_LIBRARY=str(isolated/'Steam'))
        sys.path.insert(0, str(ROOT/'src'))
        import kraken_control as application
        import modules.gpu_control.v1_0.page as gpu_module
        from modules.localization.v1_0.gpu_workspace_messages import GPU_WORKSPACE_MESSAGES
        from modules.application_shutdown.v1_1.qt_processes import stop_remaining
        application.KrakenControl.check_dependencies = lambda _self: ['isolated-gpu-workspace']
        original_refresh = gpu_module.GpuControlPage.refresh
        gpu_module.GpuControlPage.refresh = lambda _self: None
        gpu_module.coolercontrol_gpu_claim = lambda: (False, 'isolated owner fixture')
        app = QApplication.instance() or QApplication([])
        settings = QSettings(application.ORG_NAME, application.APP_NAME)
        for key, value in {'setup/completed': True, 'dependencies/desktop_design_offer_330': True,
            'cooling/hardware_kind': application.LEVITA_COOLER_KEY,
            'performance/transitions_enabled': False, 'background/enabled': False}.items():
            settings.setValue(key, value)
        settings.sync()
        window = application.KrakenControl()
        try:
            assert window.hardware_io_disabled
            page = window.gpu_control_page; page.client = client = FixtureLact()
            original_refresh(page)
            assert not isinstance(page.sections, QTabWidget)
            assert page.sections.count() == 7
            assert len(page.gpu_workspace_sections) == 5
            assert page.sections.isAncestorOf(page.tuning_page)
            assert page.sections.isAncestorOf(page.fan_page)
            page.power.setValue(210)
            page.lact_fan.setChecked(True)
            page._set_fan_curve_point(2, 61, 65)
            page.gpu_profile_name.setText('Unsaved GPU draft')
            baseline = copy.deepcopy(page.baseline)
            diagnostics = []
            page.capture_gpu_diagnostics = lambda: diagnostics.append('sample')
            page.load_lact_journal = lambda: diagnostics.append('journal')

            def draft():
                return (page.power.value(), page.core.value(), page.memory.value(), page.offset.value(),
                        page.lact_fan.isChecked(), page.fan_mode.currentData(), page.fan_static_speed.value(),
                        tuple((temperature.value(), speed.value()) for temperature, speed in page.fan_points),
                        page.fan_persist_after_test.isChecked(), page.gpu_profile_name.text())

            expected = draft()
            window.tabs.setCurrentWidget(page); window.show()

            def settle():
                app.processEvents(); QTest.qWait(85); app.processEvents()

            def check_geometry(size):
                window.resize(*size); settle()
                assert page.widget().width() <= page.viewport().width(), (size, page.widget().width(), page.viewport().width())
                for section in page.gpu_workspace_sections.values(): section.button.setChecked(True)
                settle()
                assert page.tuning_page.isVisible() and page.fan_page.isVisible()
                assert page.fan_visual.height() >= 310
                assert page.fan_visual._graph_rect().height() >= page.fan_visual.height() * .52
                assert page.tuning_gpu_art.height() >= 170
                assert not page.tuning_gpu_art.pixmap().isNull()
                graph = page.fan_visual._graph_rect()
                for index, (temperature, speed) in enumerate(page.fan_points):
                    point = page.fan_visual._plot_point(graph, temperature.value(), speed.value())
                    assert graph.contains(point)
                for widget in (page.power, page.test_button, page.fan_visual, page.fan_test_apply_button,
                               page.stress_button, page.gpu_profile_name, page.metrics, page.hardware, page.gpu_events):
                    page.ensureWidgetVisible(widget, 8, 8); settle()
                    bounds = widget.rect().translated(widget.mapTo(page.widget(), QPoint()))
                    assert page.widget().rect().contains(bounds), (size, type(widget).__name__, bounds)
                    assert widget.width() > 0 and widget.height() > 0
                for section in page.gpu_workspace_sections.values(): section.button.setChecked(False)
                page.verticalScrollBar().setValue(0); settle()
                assert draft() == expected
                assert page.baseline == baseline and not page.tested
                assert client.writes == 0

            for size in ((2551, 1337), (1440, 1000), (1000, 900)): check_geometry(size)
            for language in ('de', 'en', 'es', 'fr'):
                window.apply_ui_language(language, persist=False, log_change=False)
                for message, source in ((3703, 'Lasttest und Darstellung'), (3704, 'GPU-Unterprofile'),
                                        (3705, 'Messwerte und Beleuchtung'), (3706, 'Hardwaredetails'),
                                        (3707, 'Diagnose und Protokolle')):
                    assert page.gpu_workspace_sections[source].button.text() == GPU_WORKSPACE_MESSAGES[language][message]
                assert page.stress_button.text() == window.tr_static('GPU-Lasttest starten')
                assert page.stress_size.itemText(0) == window.tr_static('4K · hohe Last')
                assert page.stress_presentation.itemText(0) == window.tr_static('Max. Fenster · Taskleiste sichtbar')
                assert page.fan_visual.toolTip() == GPU_WORKSPACE_MESSAGES[language][3708]
                assert page.fan_edit_hint.text() == GPU_WORKSPACE_MESSAGES[language][3708]
                assert page.gpu_temperature_value.text() == '52 °C'
                assert page.stress_live_temperature.text() == window.tr_static('Temperatur') + '\n52 °C'
                assert page.stress_live_power.text() == GPU_WORKSPACE_MESSAGES[language][3714] + '\n86 W'
                assert page.stress_live_load.text() == window.tr_static('GPU-Auslastung') + '\n47 %'
                assert page.stress_live_clock.text() == GPU_WORKSPACE_MESSAGES[language][3713] + '\n2300 MHz'
                for theme in ('dark', 'light'):
                    window.theme_mode = theme; window.apply_theme()
                    check_geometry((1440, 1000))
                    assert draft() == expected
            window.apply_ui_language('de', persist=False, log_change=False)
            page.sections.setCurrentIndex(4)
            diagnostics.clear(); page.sections.setCurrentIndex(page.diagnostics_index); settle()
            assert diagnostics == ['sample', 'journal']
            diagnostic_section = page.gpu_workspace_sections['Diagnose und Protokolle']
            assert diagnostic_section.button.isChecked()
            diagnostic_section.button.setChecked(False); settle()
            assert diagnostics == ['sample', 'journal']
            diagnostic_section.button.setChecked(True); settle()
            assert diagnostics == ['sample', 'journal', 'sample', 'journal']
            window.control_authority['gpu'] = 'external'; page._sync_buttons()
            assert not page.test_button.isEnabled() and not page.fan_test_apply_button.isEnabled()
            assert not page.save_button.isEnabled()
            assert client.writes == 0
            if render_dir is not None:
                render_dir.mkdir(parents=True, exist_ok=True)
                for theme in ('dark', 'light'):
                    window.theme_mode = theme; window.apply_theme(); window.resize(2551,1337)
                    for section in page.gpu_workspace_sections.values(): section.button.setChecked(False)
                    page.verticalScrollBar().setValue(0); settle()
                    assert window.grab().save(str(render_dir/f'gpu-workspace-{theme}-overview.png'))
                    page.ensureWidgetVisible(page.fan_visual, 12, 18); settle()
                    assert window.grab().save(str(render_dir/f'gpu-workspace-{theme}-curve.png'))
            print('GPU workspace: three sizes, four languages, two themes, drafts and guards passed')
        finally:
            if isValid(window):
                window.background_widget.media_background.shutdown(); window.design_hub_page.shutdown()
                studio = window.thermalright_display_studio
                studio.shutdown_started=True; studio.startup_apply_active=False; studio.thumbnail_shutting_down=True
                studio.media_preview.shutdown(); studio.lcd_runtime.shutdown(); studio.game_activity.shutdown(); studio.gallery_preparation.shutdown()
                for timer in window.findChildren(QTimer): timer.stop()
                window.snapshot_manager_page.stop_processes(); window.process_runtime.shutdown()
                window.ui_performance.shutdown(); window.backend.shutdown(); stop_remaining(window)
                assert all(process.state()==QProcess.ProcessState.NotRunning for process in window.findChildren(QProcess))
                window.deleteLater(); QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--worker', action='store_true')
    parser.add_argument('--render-dir', type=Path)
    args = parser.parse_args(); _worker(args.render_dir)
