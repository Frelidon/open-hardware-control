"""Full-window Qt render catches native layout ownership failures after reparenting.

All state is isolated before importing the app, hardware IO is disabled, and no
apply action is clicked. Run --worker --render-dir /tmp/evidence for previews.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_case_toolbar_combo_ownership_survives_full_window_render_cycle():
    environment = os.environ.copy()
    environment.update(QT_QPA_PLATFORM='offscreen', PYTHONDONTWRITEBYTECODE='1')
    completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker'],
        cwd=ROOT, env=environment, capture_output=True, text=True, timeout=100)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert 'case ownership: full-window renders, three sizes, both themes passed' in completed.stdout


def _worker(render_dir=None):
    import copy
    import tempfile
    from PySide6.QtCore import QCoreApplication, QEvent, QPoint, QProcess, QSettings, QTimer
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from shiboken6 import isValid

    with tempfile.TemporaryDirectory(prefix='ohc-case-ownership-') as temporary:
        isolated = Path(temporary)
        os.environ.update(OHC_DISABLE_HARDWARE_IO='1', XDG_CONFIG_HOME=str(isolated/'config'),
            XDG_STATE_HOME=str(isolated/'state'), OHC_DESKTOP_DESIGN_CONFIG_DIR=str(isolated/'desktop-config'),
            OHC_DESKTOP_DESIGN_STATE_DIR=str(isolated/'desktop-state'), OHC_WALLPAPER_STEAM_LIBRARY=str(isolated/'Steam'))
        sys.path.insert(0, str(ROOT/'src'))
        import kraken_control as application
        from modules.application_shutdown.v1_1.qt_processes import stop_remaining
        application.KrakenControl.check_dependencies = lambda _self: ['isolated-case-layout']
        app = QApplication.instance() or QApplication([])
        settings = QSettings(application.ORG_NAME, application.APP_NAME)
        for key, value in {'setup/completed':True, 'dependencies/desktop_design_offer_330':True,
            'cooling/hardware_kind':application.LEVITA_COOLER_KEY,
            'performance/transitions_enabled':False, 'ui/background_enabled':False}.items():
            settings.setValue(key, value)
        settings.sync()
        window = application.KrakenControl()
        try:
            assert window.hardware_io_disabled
            toolbar = window.case_profile_toolbar
            combos = (window.rgb_case_template_combo, window.rgb_layout_profile_combo)
            assert all(isValid(combo) and toolbar.isAncestorOf(combo) for combo in combos)
            identities = tuple(combo.currentData() for combo in combos)
            topology = copy.deepcopy(window.rgb_layout_slots_payload())
            applied_case = window.rgb_case_template_id
            for theme in ('dark', 'light'):
                window.theme_mode = theme; window.apply_theme()
                for size in ((2551,1337), (1440,1000), (1000,900)):
                    window.resize(*size); window.show()
                    window.tabs.setCurrentIndex(window.case_page_index)
                    for section in (window.case_profile_section, window.case_fan_section, window.case_reference_section):
                        section.button.setChecked(False)
                    window.rgb_case_template_combo.setCurrentIndex(1)
                    window.rgb_case_template_combo.setCurrentIndex(window.rgb_case_template_combo.findData(identities[0]))
                    window.rgb_layout_profile_combo.setCurrentIndex(-1)
                    window.rgb_layout_profile_combo.setCurrentIndex(window.rgb_layout_profile_combo.findData(identities[1]))
                    app.processEvents(); QTest.qWait(45); app.processEvents()
                    window.tabs.widget(window.case_page_index).verticalScrollBar().setValue(0)
                    app.processEvents()
                    image = window.grab()
                    assert not image.isNull()
                    case_page = window.tabs.widget(window.case_page_index)
                    assert case_page.widget().width() <= case_page.viewport().width(), (size, case_page.widget().width(), case_page.viewport().width())
                    assert all(isValid(combo) and combo.width()>0 and combo.height()>0 for combo in combos)
                    if render_dir is not None:
                        image.save(str(render_dir/f'case-{theme}-{size[0]}-initial.png'))
                    for section in (window.case_profile_section, window.case_fan_section, window.case_reference_section):
                        section.button.setChecked(True)
                    app.processEvents(); QTest.qWait(45); app.processEvents()
                    image = window.grab()
                    assert not image.isNull()
                    case_page = window.tabs.widget(window.case_page_index)
                    assert case_page.widget().width() <= case_page.viewport().width(), (size, case_page.widget().width(), case_page.viewport().width())
                    if render_dir is not None:
                        image.save(str(render_dir/f'case-{theme}-{size[0]}-expanded.png'))
                        for name, section in (('profiles',window.case_profile_section), ('fans',window.case_fan_section), ('reference',window.case_reference_section)):
                            top=section.mapTo(case_page.widget(),QPoint()).y()
                            case_page.verticalScrollBar().setValue(max(0,top-16))
                            app.processEvents(); QTest.qWait(20); app.processEvents()
                            assert window.grab().save(str(render_dir/f'case-{theme}-{size[0]}-{name}.png'))
                    # Hidden tab geometry participates in full-window grabs too;
                    # this was where the dangling native layout cache crashed.
                    window.tabs.setCurrentWidget(window.design_hub_page)
                    app.processEvents(); QTest.qWait(30); app.processEvents()
                    assert not window.grab().isNull()
                    assert tuple(combo.currentData() for combo in combos) == identities
                    assert window.rgb_case_template_id == applied_case
                    assert window.rgb_layout_slots_payload() == topology
                    if render_dir is not None and size[0] in (2551,1440):
                        window.open_help_center('getting_started')
                        app.processEvents(); QTest.qWait(30); app.processEvents()
                        assert window.grab().save(str(render_dir/f'help-{theme}-{size[0]}.png'))
            print('case ownership: full-window renders, three sizes, both themes passed')
        finally:
            if isValid(window):
                window.background_widget.media_background.shutdown()
                window.design_hub_page.shutdown()
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
    args = parser.parse_args()
    if args.render_dir is not None: args.render_dir.mkdir(parents=True, exist_ok=True)
    _worker(args.render_dir)
