"""LACT read failures cannot advertise confirmed data or disappear from logs."""
import os
from pathlib import Path
import sys
from types import SimpleNamespace
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from PySide6.QtCore import QCoreApplication, QEvent, QSettings
from PySide6.QtWidgets import QApplication, QWidget
from modules.gpu_control.v1_0.page import GpuControlPage
from modules.gpu_control.v1_0.read_status import log_failure, refresh, set_state
from modules.localization.v1_0.help_dashboard_messages import HELP_DASHBOARD_MESSAGES

APP = QApplication.instance() or QApplication([])


class Host(QWidget):
    def __init__(self, path):
        super().__init__(); self.settings = QSettings(str(path), QSettings.Format.IniFormat)
        self.ui_language = 'de'; self.messages = []; self.control_authority = {'gpu': 'external'}
    def tr_static(self, source):
        return {HELP_DASHBOARD_MESSAGES['de'][key]: value
                for key, value in HELP_DASHBOARD_MESSAGES[self.ui_language].items()}.get(source, source)
    def log_message(self, message): self.messages.append(message)


def test_timeout_badge_failure_log_dedup_and_four_language_recovery(tmp_path, monkeypatch):
    monkeypatch.setattr('modules.gpu_control.v1_0.read_ui.detect_distribution', lambda: SimpleNamespace(family='fedora'))
    host = Host(tmp_path / 'gpu.ini'); page = GpuControlPage(host)
    try:
        assert page.gpu_read_state == 'unknown'
        assert page.gpu_service_badge.objectName() != 'gpuServiceBadge'
        page._gpu_read_failed('device', 'LACT connection failed: TimeoutError')
        assert page.gpu_service_badge.objectName() == 'healthCritical'
        assert 'TimeoutError' in page.status.text()
        assert len(host.messages) == 1 and 'GPU-LACT-FEHLER:' in host.messages[0]
        page._gpu_read_failed('device', 'LACT connection failed: TimeoutError')
        assert len(host.messages) == 1
        for language in ('de', 'en', 'es', 'fr'):
            host.ui_language = language; refresh(page)
            assert host.tr_static('LACT · Daten nicht verfügbar') in page.gpu_service_badge.text()
            assert host.tr_static('Letzte Abfrage fehlgeschlagen. Frühere Werte sind nicht aktuell.') == page.gpu_temperature_value.toolTip()
        assert not page._write_allowed()
        page._apply_gpu_read(dict(stats={'temps': {'edge': 41}}, clocks={}, baseline={},
                                  overdrive=True, info={'name': 'Test GPU'}, ownership=[False, 'inactive']))
        assert page.gpu_read_state == 'connected'
        assert page.gpu_service_badge.objectName() == 'gpuServiceBadge'
        assert page.gpu_temperature_value.text() == '41 °C'
        assert not page.gpu_temperature_value.toolTip()
        assert not page._write_allowed() and not page.test_button.isEnabled()
        page._populate_gpu_devices([])
        assert page.gpu_read_state == 'empty'
        assert page.gpu_service_badge.objectName() != 'gpuServiceBadge'
    finally:
        page.shutdown(); host.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_failure_reporting_redacts_private_values_and_bounds_flood_cache():
    messages = []; page = SimpleNamespace(host=SimpleNamespace(log_message=messages.append), _gpu_log=messages.append)
    # Synthetic private address for the redaction test, not a published host
    # literal. Documentation-range addresses are intentionally left readable.
    address = '.'.join(('10', '20', '30', '40'))
    reason = f'/home/exampleuser/file {address}'
    assert log_failure(page, 'device', reason, now=0)
    assert '/home/exampleuser' not in messages[0] and address not in messages[0]
    assert not log_failure(page, 'device', reason, now=1)
    assert log_failure(page, 'device', reason, now=11)
    for index in range(40): log_failure(page, 'device', f'failure {index}', now=12+index)
    assert len(page.gpu_read_failure_log) <= 16
