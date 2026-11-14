#!/usr/bin/env python3
"""Render the real main window with isolated settings and synthetic fix status."""
import os
from pathlib import Path
import sys
import tempfile
import json

ROOT = Path(__file__).resolve().parents[1]
runtime = tempfile.TemporaryDirectory(prefix='ohc-hardware-fix-ui-')
os.environ.update(QT_QPA_PLATFORM='offscreen', XDG_CONFIG_HOME=runtime.name + '/config',
                  XDG_STATE_HOME=runtime.name + '/state', OHC_DISABLE_HARDWARE_IO='1')
sys.path.insert(0, str(ROOT / 'src'))
from PySide6.QtCore import QCoreApplication, QEvent, QSettings, QTimer, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import kraken_control as application
from modules.hardware_fix.v1_0 import page
from modules.hardware_fix.v1_0.status import HardwareFixStatus
from modules.application_shutdown.v1_1.qt_processes import stop_remaining


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs/images/rendering-evidence'
    output.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    settings = QSettings(application.ORG_NAME, application.APP_NAME)
    for key, value in {'setup/completed': True, 'design/theme': 'light',
                       'dependencies/desktop_design_offer_330': True,
                       'ui/background_enabled': False}.items():
        settings.setValue(key, value)
    settings.sync()
    application.KrakenControl.check_dependencies = lambda self: ['render-without-hardware']
    page.inspect_status = lambda: HardwareFixStatus(
        'ubuntu', True, ('card1-DP-2',), False, True, True, True,
        True, True, True, True, 'local', 'local', False, '',
    )
    window = application.KrakenControl()
    panel = window.hardware_checker_page.hardware_fix_panel
    window.navigation.setCurrentItem(window.navigation_items['hardware_fix'])
    window.show()
    evidence = []
    for theme in ('light', 'dark'):
        window.theme_mode = theme
        window.apply_theme()
        for language, size, expanded in (('de', (2551, 1337), False), ('de', (1440, 1000), False), ('de', (1000, 900), True),
                                         ('fr', (1000, 900), False), ('en', (1440, 1000), True)):
            window.apply_ui_language(language, persist=False, log_change=False)
            window.resize(*size)
            panel.technical.button.setChecked(expanded)
            panel.verticalScrollBar().setValue(0)
            for _ in range(6):
                app.processEvents()
            assert panel.horizontalScrollBar().maximum() == 0
            assert window.hardware_checker_page.horizontalScrollBar().maximum() == 0
            QTest.qWait(650)
            for button in (panel.activate_button, panel.uninstall_button, panel.options_button):
                assert button.isVisible()
                assert button.width() >= button.sizeHint().width()
                assert button.geometry().right() <= button.parentWidget().width()
                right = button.mapTo(panel.viewport(), QPoint(button.width(), 0)).x()
                assert right <= panel.viewport().width()
            name = f'hardware-fix-183-{theme}-{language}-{size[0]}-{"details" if expanded else "main"}.png'
            assert window.grab().save(str(output / name))
            evidence.append({'file': name, 'theme': theme, 'language': language,
                             'size': [window.width(), window.height()], 'details': expanded,
                             'status': 'synthetic; no hardware writes'})
    (output / 'hardware-fix-183.json').write_text(json.dumps(evidence, indent=2) + '\n')
    window.background_widget.media_background.shutdown()
    studio = window.thermalright_display_studio
    studio.shutdown_started = True
    studio.startup_apply_active = False
    studio.thumbnail_shutting_down = True
    for owner in (studio.media_preview, studio.lcd_runtime, studio.game_activity, studio.gallery_preparation):
        owner.shutdown()
    app.processEvents()
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.snapshot_manager_page.stop_processes()
    window.process_runtime.shutdown()
    window.ui_performance.shutdown()
    window.backend.shutdown()
    stop_remaining(window)
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    print('Verified', len(evidence), 'main-window renders:', output)


if __name__ == '__main__':
    main()
