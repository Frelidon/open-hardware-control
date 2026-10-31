"""Owned sensor supervision and pure RGB plans; no hardware writes."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('OHC_DISABLE_HARDWARE_IO', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QWidget
from modules.process_runtime.v1_1.controller import ProcessRuntime
from modules.process_runtime.v1_1 import sensor_worker
from modules.rgb_studio.v1_15.render_plan import render
from modules.rgb_studio.v1_15.gpu_routing import render_zone_frame
from rgb_effects import EFFECTS, RGBEffectConfig
from dataclasses import asdict

APP = QApplication.instance() or QApplication([])


def drain(predicate, timeout=4):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        APP.processEvents(); time.sleep(.01)
    assert predicate()


def test_actual_owned_sensor_child_and_eof_shutdown(monkeypatch, tmp_path):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    host = QWidget()
    runtime = ProcessRuntime(host)
    runtime.start()
    drain(lambda: runtime.process.state() == QProcess.ProcessState.Running)
    runtime.poll()
    drain(lambda: bool(runtime.current()))
    assert isinstance(runtime.metrics(), dict)
    assert isinstance(runtime.sensors(), tuple)
    assert not runtime.pending
    runtime.received = time.monotonic() - 3
    assert runtime.current() == {} and runtime.temperature('cpu')[0] is None
    runtime.shutdown()
    assert runtime.process.state() == QProcess.ProcessState.NotRunning
    assert not runtime.timer.isActive() and not runtime.restart.isActive()
    runtime.start()
    assert runtime.process.state() == QProcess.ProcessState.NotRunning
    host.deleteLater()


def test_bounded_restart_and_shutdown_cancels_future_start(monkeypatch, tmp_path):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    runtime = ProcessRuntime(QWidget())
    for delay in (1000, 2000, 4000):
        runtime.finished()
        assert runtime.restart.interval() == delay and runtime.restart.isActive()
        runtime.restart.stop()
    runtime.finished()
    assert not runtime.restart.isActive() and runtime.current() == {}
    runtime.shutdown(); runtime.finished()
    assert not runtime.restart.isActive()


def test_worker_protocol_is_bounded_and_imports_no_qt():
    assert sensor_worker.run(io.StringIO('{"op":"stop"}\n'), io.StringIO()) == 0
    assert sensor_worker.run(io.StringIO('x' * 4097), io.StringIO()) == 2
    result = subprocess.run([sys.executable, '-c',
        'import sys; from modules.process_runtime.v1_1 import sensor_worker; '
        'assert not any(n.startswith("PySide6") for n in sys.modules)'],
        env={**os.environ, 'PYTHONPATH': str(ROOT / 'src')}, capture_output=True, timeout=5)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize('effect', [effect.effect_id for effect in EFFECTS])
def test_worker_render_matches_existing_effect_math(effect):
    config = RGBEffectConfig(effect_id=effect, speed=110)
    raw = dict(schema=1, config=asdict(config), elapsed=12.345,
               zones=['Strip'], overrides={}, paths={}, rectangles={}, gpu_zones=[], sync_counts={})
    assert render(raw, 30, [30]) == render_zone_frame(config, 30, [30], ['Strip'], {}, 12.345)


@pytest.mark.parametrize('change', [{'schema': 7}, {'elapsed': float('nan')}, {'elapsed': -1},
                                    {'config': None}, {'paths': []}, {'sync_counts': {'Strip': 0}},
                                    {'gpu_zones': 'Strip'}, {'rectangles': []}])
def test_invalid_render_plan_rejected_without_sdk_transaction(change):
    raw = dict(schema=1, config=asdict(RGBEffectConfig()), elapsed=1,
               zones=['Strip'], overrides={}, paths={}, rectangles={}, gpu_zones=[], sync_counts={})
    raw.update(change)
    with pytest.raises(ValueError): render(raw, 30, [30])


def test_sdk_worker_renders_plan_before_existing_transaction():
    from openrgb_sdk import process_worker_frame
    received = []
    def write(device, count, colors, **kwargs):
        received.append((device, count, colors, kwargs))
        return {'ok': True}
    config = RGBEffectConfig(effect_id='spinner', speed=110)
    raw = dict(schema=1, config=asdict(config), elapsed=12.345, zones=['Strip'],
               overrides={}, paths={}, rectangles={}, gpu_zones=['Strip'], sync_counts={'Strip': 30})
    request = dict(id=42, devices=[dict(key='test:gpu', device=3, led_count=30,
                   render_plan=raw, zone_sizes=[30], prepare=True)])
    result = process_worker_frame(SimpleNamespace(write_frame=write), request)
    assert result['id'] == 42 and result['ok']
    assert received[0][2] == render(raw, 30, [30])
    assert result['devices'][0]['render_ms'] >= 0


@pytest.mark.parametrize('change', [{'cpu': True}, {'gpu': 200}, {'sampled_at': float('nan')},
                                    {'metrics': {'cpuLoad': 'invalid'}}, {'sensors': {}}])
def test_bad_sensor_reply_clears_snapshot_and_stops_only_owned_worker(change):
    host = QWidget(); runtime = ProcessRuntime(host)
    runtime.requested = time.monotonic(); runtime.pending = True
    raw = dict(schema=1, cpu=45, gpu=50, sampled_at=runtime.requested, metrics={}, sensors=[])
    raw.update(change)
    stopped = []
    runtime.process = SimpleNamespace(readAllStandardOutput=lambda: (json.dumps(raw) + '\n').encode(),
                                      kill=lambda: stopped.append(True))
    runtime.receive()
    assert runtime.current() == {} and stopped == [True]
    runtime.closed = True; host.deleteLater()
