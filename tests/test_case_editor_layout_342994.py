"""Actual inline form geometry, responsive drafts and four-language tab titles."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def exercise():
    with tempfile.TemporaryDirectory(prefix='ohc-case-editor94-') as temp:
        for key in ('XDG_CONFIG_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME',
                    'OHC_DESKTOP_DESIGN_CONFIG_DIR', 'OHC_DESKTOP_DESIGN_STATE_DIR'):
            os.environ[key] = str(Path(temp) / key)
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        os.environ['OHC_DISABLE_HARDWARE_IO'] = '1'
        sys.path.insert(0, str(ROOT / 'src'))
        from PySide6.QtCore import QPoint
        from PySide6.QtWidgets import QApplication, QDialogButtonBox, QScrollArea, QSpinBox, QTabWidget
        from rgb_devices import RGBGroup, flori_rgb_layout_profile
        from openrgb_integration import OpenRGBDevice
        from modules.pc_case_profiles.v1_5.editor_sections import EditorSections
        from modules.pc_case_profiles.v1_5.inline_editor import present_editor
        from modules.pc_case_profiles.v1_5.case_page import build_slot_pwm_button
        from modules.rgb_studio.v1_15.gpu_led_editor import show_gpu_header_editor
        from modules.rgb_studio.v1_15.led_topology_editor import LedTopologyEditor
        import kraken_control as application
        application.KrakenControl.check_dependencies = lambda self: ['hardware-free-layout']
        app = QApplication([]); app.setQuitOnLastWindowClosed(False)
        window = application.KrakenControl()
        errors = []; window.show_error = errors.append
        window.settings.setValue('setup/completed', True)
        window.settings.setValue('dependencies/desktop_design_offer_330', True)
        window.rgb_groups = [RGBGroup('test', 'Test Fans')]
        _, window.rgb_layout_slots = flori_rgb_layout_profile('thermalright')
        window.refresh_rgb_layout_editor()
        window.tabs.setCurrentIndex(window.case_page_index)
        window.resize(1600, 1000); window.show()

        def settle():
            for _ in range(5): app.processEvents()

        def fits(widget, container):
            origin = widget.mapTo(container, QPoint(0, 0))
            assert widget.isVisible(), widget.objectName()
            assert origin.x() >= 0 and origin.y() >= 0, (widget.objectName(), origin)
            assert origin.x() + widget.width() <= container.width() + 1
            assert origin.y() + widget.height() <= container.height() + 1

        def check_form():
            settle()
            inspector = window.case_inspector
            dialog = inspector.active_dialog
            assert dialog is not None and not dialog.isWindow()
            assert not inspector.findChildren(QScrollArea), 'An internal scroll area hides fields'
            assert inspector.body_layout.count() == 1
            buttons = dialog.findChild(QDialogButtonBox)
            fits(buttons, inspector)
            fits(buttons, window)
            for control in dialog.findChildren(QSpinBox):
                if control.isVisible(): fits(control, inspector)
            return dialog

        slot = next(s for s in window.rgb_layout_slots if s.position == 'front')
        window.focus_rgb_layout_slot(slot.slot_id or slot.position)
        for language in ('de', 'en', 'es', 'fr'):
            window.apply_ui_language(language, log_change=False)
            window.resize(1600, 1000)
            window.edit_selected_rgb_layout_slot()
            dialog = check_form()
            sections = dialog.findChild(EditorSections)
            assert sections.wide and window.case_inspector.width() > 470
            scale = dialog.findChild(QSpinBox, 'caseSlotScale'); scale.setValue(35)
            leds = dialog.findChild(QSpinBox, 'slotFanLedsPerFan'); leds.setValue(8)
            window.resize(1200, 800)
            dialog = check_form()
            assert not sections.wide and sections.tabs.count() == 2
            assert sections.tabs.tabText(0) == window.tr_static('Eigenschaften')
            sections.tabs.setCurrentIndex(1); settle(); fits(leds, window.case_inspector)
            window.apply_ui_language('en', log_change=False); settle()
            assert sections.tabs.tabText(0) == 'Properties'
            assert sections.tabs.tabText(1) == window.tr_static('Lüfter')
            window.resize(1600, 1000); check_form()
            window.resize(1200, 800); check_form()
            assert sections.tabs.currentIndex() == 1
            assert scale.value() == 35 and leds.value() == 8
            render = os.environ.get('OHC_UI_RENDER_DIR')
            if render and language in {'de', 'fr'}:
                window.apply_ui_language(language, log_change=False)
                window.resize(1600, 1000); check_form()
                output = Path(render); output.mkdir(parents=True, exist_ok=True)
                window.grab().save(str(output / f'case-component-wide-{language}.png'))
                window.resize(1200, 800); check_form()
                window.grab().save(str(output / f'case-component-tabs-{language}.png'))
            dialog.reject(); settle()
            assert next(s for s in window.rgb_layout_slots if s.slot_id == slot.slot_id).scale == slot.scale

        window.resize(2000, 1000)
        source = OpenRGBDevice(3, 'Synthetic motherboard', device_type='Motherboard',
                               modes=('Direct',), zones=('JARGB 1',))
        window.openrgb_devices = [source]; window.openrgb_stable_ids = {3: 'synthetic:board'}
        window.rgb_zone_configurations = {'synthetic:board': {'JARGB 1': dict(units=1, leds_per_unit=30)}}
        zones = [dict(name='JARGB 1', current=30, minimum=1, maximum=512, resizable=True)]
        for language in ('de', 'en', 'es', 'fr'):
            window.apply_ui_language(language, log_change=False)
            show_gpu_header_editor(window, None, source, 'JARGB 1', zones)
            dialog = check_form()
            topology = dialog.findChild(LedTopologyEditor)
            sections = topology.findChild(EditorSections)
            tabs = next(tab for tab in dialog.findChildren(QTabWidget) if tab.indexOf(topology) >= 0)
            tabs.setCurrentWidget(topology); settle(); check_form()
            assert sections.wide
            window.resize(1200, 800); check_form()
            assert not sections.wide
            for index in range(sections.tabs.count()):
                sections.tabs.setCurrentIndex(index); check_form()
            assert topology.count.value() == 30
            if os.environ.get('OHC_UI_RENDER_DIR') and language in {'de', 'fr'}:
                window.resize(2000, 1000); check_form()
                window.grab().save(str(Path(os.environ['OHC_UI_RENDER_DIR']) / f'case-led-path-{language}.png'))
            dialog.reject(); settle()
            assert window.rgb_zone_configurations['synthetic:board']['JARGB 1']['leds_per_unit'] == 30
            window.resize(2000, 1000)

        gpu = OpenRGBDevice(7, 'Synthetic GPU', device_type='GPU', modes=('External Control',))
        for language in ('de', 'en', 'es', 'fr'):
            window.apply_ui_language(language, log_change=False)
            dialog, *_ = window.build_gpu_lighting_dialog(gpu, 'synthetic:gpu', [source])
            assert present_editor(window, dialog)
            for width, height in ((1600, 1000), (1200, 800)):
                window.resize(width, height); check_form()
            dialog.reject(); settle()
            build_slot_pwm_button(window, slot.slot_id or slot.position).click()
            check_form(); window.case_inspector.dismiss(); settle()
        assert not errors, errors
        window.mainboard_channels = {}
        window.perform_orderly_hardware_exit('responsive form test')
        window.backend.shutdown()
        window.close(); settle()
        print('responsive forms/drafts/footer/four-language tabs: passed', flush=True)


def test_responsive_real_case_forms():
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child'], cwd=ROOT,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                            capture_output=True, text=True, timeout=25)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'four-language tabs: passed' in result.stdout


if __name__ == '__main__' and '--child' in sys.argv: exercise()
