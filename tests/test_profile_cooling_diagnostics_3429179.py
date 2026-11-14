"""Fresh sensor waiting/cancellation and bounded, durable error capture."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import os
import sys
import threading
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import pytest
from PySide6.QtCore import qWarning, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from modules.profile_cooling.v1_0.restore import ProfileCoolingWait, cancel, wait_for_cpu
from modules.runtime_logging.v1_0.error_capture import ErrorCapture
from modules.runtime_logging.v1_0.error_bridge import ErrorLogBridge


class Host(QWidget):
    def __init__(self):
        super().__init__()
        self.calls=[];self.logs=[];self.errors=[];self.value=None;self.ready=True
        self.controls={'pump':55,'fan':45,'pump_mode':'curve'}
        self.footer_status=QLabel(self)
        self.process_runtime=SimpleNamespace(received=0.,pending=False,failures=0,failure_reason='',poll=lambda:self.calls.append('poll'))
    def tr_static(self,value):return value
    def log_message(self,message,**kwargs):self.logs.append((message,kwargs))
    def capture_profile_payload(self,_category):return deepcopy(self.controls)
    def read_amd_cpu_temperature(self):return self.value,'synthetic CPU'
    def cooling_device_ready(self):return self.ready
    def transmit_profile_cooling(self,payload,name):self.calls.append(('existing-apply',payload,name))
    def report_profile_apply_error(self,*args,**kwargs):self.errors.append((args,kwargs))


@pytest.fixture
def host():
    app=QApplication.instance() or QApplication([])
    widget=Host()
    yield widget
    for timer in widget.findChildren(QTimer):timer.stop()
    widget.deleteLater();app.processEvents()


def test_missing_then_fresh_sample_uses_existing_apply_once(host):
    payload={'fan_mode':'curve','fan_curve':[[30,30],[80,100]]};original=deepcopy(payload)
    wait_for_cpu(host,payload,'saved')
    controller=host.profile_cooling_wait
    assert controller.pending and host.calls==['poll'] and not host.errors
    payload['fan_curve'][0][1]=99
    controller.check();assert not any(isinstance(call,tuple) for call in host.calls)
    host.value=51.2;controller.check();controller.check()
    assert [call for call in host.calls if isinstance(call,tuple)]==[('existing-apply',original,'saved')]
    assert not controller.timer.isActive() and controller.pending is None


@pytest.mark.parametrize('value',[None,float('nan'),float('inf'),True,0.,151.,50.])
def test_deadline_reports_nonmodal_error_and_never_applies_late(host,value,monkeypatch):
    wait_for_cpu(host,{},'saved');controller=host.profile_cooling_wait
    host.value=value;monkeypatch.setattr('modules.profile_cooling.v1_0.restore.time.monotonic',lambda:controller.deadline+.1)
    controller.check()
    assert len(host.errors)==1 and controller.pending is None and not controller.timer.isActive()
    assert 'snapshot_age=' in host.errors[0][0][1]
    host.value=50.;controller.check()
    assert not any(isinstance(call,tuple) for call in host.calls)


@pytest.mark.parametrize('change',['controls','shutdown','lost-device','superseded'])
def test_pending_profile_cannot_override_new_user_intent(host,change):
    wait_for_cpu(host,{'fan':40},'old');controller=host.profile_cooling_wait
    if change=='controls':host.controls['fan']=90
    if change=='shutdown':host.explicit_quit_requested=True
    if change=='lost-device':host.ready=False
    if change=='superseded':cancel(host)
    host.value=50.;controller.check()
    assert controller.pending is None and not any(isinstance(call,tuple) for call in host.calls)


def test_latest_waiting_request_replaces_old_payload(host):
    wait_for_cpu(host,{'fan':40},'old');wait_for_cpu(host,{'fan':70},'new')
    host.value=50.;host.profile_cooling_wait.check()
    assert [call for call in host.calls if isinstance(call,tuple)]==[('existing-apply',{'fan':70},'new')]


def test_error_capture_redacts_deduplicates_bounds_and_bridges_without_double_persistence(host,monkeypatch):
    persisted=[];monkeypatch.setattr('modules.runtime_logging.v1_0.error_capture.append_error_event',lambda text,**kwargs:persisted.append(text))
    capture=ErrorCapture();capture.record('test',str(Path.home())+'/private 192.0.2.17')
    capture.record('test',str(Path.home())+'/private 192.0.2.17')
    assert len(persisted)==1 and str(Path.home()) not in persisted[0] and '192.0.2.17' in persisted[0]
    bridge=ErrorLogBridge(host,capture);bridge.timer.stop()
    assert host.logs[-1][1]=={'persist_error':False} and not capture.drain()
    for i in range(100):capture.record('test',str(i))
    assert len(capture.drain())==64 and len(capture.recent)<=64


def test_python_thread_unraisable_and_qt_warning_hooks_retain_original_behavior(host,monkeypatch):
    persisted=[];delegated=[]
    monkeypatch.setattr('modules.runtime_logging.v1_0.error_capture.append_error_event',lambda text,**kwargs:persisted.append(text))
    monkeypatch.setattr(sys,'excepthook',lambda *args:delegated.append('python'))
    monkeypatch.setattr(threading,'excepthook',lambda args:delegated.append('thread'))
    monkeypatch.setattr(sys,'unraisablehook',lambda args:delegated.append('unraisable'))
    capture=ErrorCapture();capture.install()
    try:
        try:raise ValueError('synthetic worker failure')
        except ValueError as error:
            sys.excepthook(type(error),error,error.__traceback__)
            args=SimpleNamespace(exc_type=type(error),exc_value=error,exc_traceback=error.__traceback__)
            threading.excepthook(args);sys.unraisablehook(args)
        qWarning('synthetic Qt warning')
        messages=capture.drain()
        assert delegated==['python','thread','unraisable']
        assert len(messages)==4 and len(persisted)==3
        assert any(message.startswith('LAUFZEIT-WARNUNG:') and 'synthetic Qt warning' in message for message in messages)
    finally:capture.restore()


def test_existing_module_failures_are_forwarded_to_general_log_without_loop(host,monkeypatch,tmp_path):
    import privacy_logging
    monkeypatch.setenv('XDG_STATE_HOME',str(tmp_path))
    capture=ErrorCapture();capture.install()
    try:
        path=privacy_logging.append_error_event('MODULE: sensors failure · synthetic timeout')
        assert path.is_file()
        bridge=ErrorLogBridge(host,capture);bridge.timer.stop()
        assert len(host.logs)==1 and 'synthetic timeout' in host.logs[0][0]
        assert host.logs[0][1]=={'persist_error':False}
        assert not capture.drain()
        assert path.read_text().count('synthetic timeout')==1
    finally:capture.restore()


def test_module_journal_keeps_build_version_while_redacting_private_details(monkeypatch,tmp_path):
    import json
    from app_constants import APP_VERSION
    from modules.process_runtime.v1_1.diagnostics import record
    monkeypatch.setenv('XDG_STATE_HOME',str(tmp_path))
    path=record('sensors','failure',reason=f'{Path.home()}/private · 192.0.2.17')
    row=json.loads(path.read_text().splitlines()[-1])
    assert row['version']==APP_VERSION
    assert str(Path.home()) not in row['reason'] and '192.0.2.17' in row['reason']


def test_error_file_serializes_concurrent_writers(monkeypatch,tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from privacy_logging import append_error_event
    monkeypatch.setenv('XDG_STATE_HOME',str(tmp_path))
    with ThreadPoolExecutor(max_workers=4) as pool:
        paths=list(pool.map(lambda i:append_error_event(f'synthetic concurrent failure {i}'),range(40)))
    assert all(path==paths[0] for path in paths)
    lines=paths[0].read_text().splitlines()
    assert len(lines)==40
    assert all(sum(line.endswith(f'synthetic concurrent failure {i}') for line in lines)==1 for i in range(40))
