"""Fault injection for concrete owned workers, without USB/PWM writes."""
import ast
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('OHC_DISABLE_HARDWARE_IO', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QWidget
from modules.process_runtime.v1_1.controller import ProcessRuntime
from modules.process_runtime.v1_1.diagnostics import record, MAX_BYTES
from modules.process_runtime.v1_1.restart_policy import RestartBudget
from modules.process_runtime.v1_1.sdk_supervisor import SDKSupervisor
from modules.lcd_runtime.v1_1.controller import LCDRuntime
from modules.lcd_runtime.v1_1.progress import DisplayProgress, daemon_owns_playback
from modules.lcd_runtime.v1_1 import game_probe

APP = QApplication.instance() or QApplication([])


def drain(predicate, timeout=4):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        APP.processEvents()
        time.sleep(.005)
    assert predicate()


def actual_method(filename, name):
    tree = ast.parse((ROOT / 'src' / filename).read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and any(isinstance(c, ast.FunctionDef) and c.name == name for c in n.body))
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(QProcess=QProcess, QTimer=__import__('PySide6.QtCore', fromlist=['QTimer']).QTimer,
              time=time, Path=Path, json=json, sys=sys, Iterable=object, Callable=object,
              LEVITA_APPLY_COOLDOWN_SECONDS=10)
    exec(compile(ast.Module([method], type_ignores=[]), 'actual_runtime', 'exec'), ns)
    return ns[name]


def test_progress_accepts_only_complete_success_lines_and_video_wraps():
    progress = DisplayProgress(); progress.reset(100)
    assert not progress.feed('Playing on device\nwarning: sent 100 bytes\n  sent 0 bytes (theme=\'test\')\n', 101)
    assert not progress.feed('  sent 400 bytes (theme=\'test\', video frame 29/30)', 102)
    assert progress.feed('\n  sent 400 bytes (theme=\'test\', video frame 0/30)\n', 103)
    assert progress.frames == 2 and progress.last_sent == 103
    assert not progress.timeout(117.9) and progress.timeout(118)
    progress.reset(200)
    assert not progress.timeout(244.9) and progress.timeout(245)
    progress.feed('x' * 10000, 201)
    assert len(progress.buffer) <= 4096 and progress.frames == 0


def test_trcc_9104_daemon_playback_handoff_is_exact() -> None:
    assert daemon_owns_playback(
        "The daemon is playing 87ad:70db — it keeps the panel updated."
    )
    assert not daemon_owns_playback("The daemon failed 87ad:70db")
    assert not daemon_owns_playback("it keeps the panel updated")


def test_retry_budget_requires_stable_confirmed_progress():
    budget = RestartBudget()
    assert [budget.failure() for _ in range(4)] == [1000, 2000, 4000, None]
    budget.progress(100, 129.9)
    assert budget.failure() is None
    budget.progress(100, 130)
    assert budget.failure() == 1000


def test_journal_preserves_exit_request_traceback_and_redacts(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    path = record('sensors', 'failure', pid=123, exit_code=7, request_id=9, retry_ms=2000,
                  stderr='Traceback:\nFile /home/exampleuser/private.py\nserial=ABC123\nRuntimeError: failed')
    data = json.loads(path.read_text())
    assert data['pid'] == 123 and data['exit_code'] == 7 and data['request_id'] == 9
    assert 'RuntimeError: failed' in data['stderr'] and 'Traceback:' in data['stderr']
    assert 'exampleuser' not in path.read_text() and 'ABC123' not in path.read_text()
    assert path.stat().st_mode & 0o777 == 0o600
    assert 'sensors' in (path.parent / 'errors.log').read_text()


def test_journal_rotation_keeps_valid_json_and_rejects_symlink(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    path = record('lcd', 'started')
    path.write_text((json.dumps({'event': 'old'}) + '\n') * (MAX_BYTES // 10))
    record('lcd', 'failure', reason='timeout')
    assert path.stat().st_size < MAX_BYTES
    assert all(isinstance(json.loads(line), dict) for line in path.read_text().splitlines())
    path.unlink(); target = tmp_path / 'untouched'; target.write_text('untouched')
    path.symlink_to(target)
    assert record('lcd', 'failure') is None and target.read_text() == 'untouched'


def test_sensor_real_crash_preserves_stderr_and_only_restarts_child(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    host = QWidget(); runtime = ProcessRuntime(host)
    runtime.started = time.monotonic()
    runtime.process.start(sys.executable, ['-c', 'import sys; print("RuntimeError: injected sensor crash",file=sys.stderr); sys.exit(7)'])
    drain(lambda: runtime.restart.isActive())
    data = [json.loads(line) for line in (tmp_path / 'open-hardware-control/module-events.jsonl').read_text().splitlines()]
    failure = next(row for row in data if row['event'] == 'failure')
    assert failure['exit_code'] == 7 and failure['pid'] > 0
    assert 'injected sensor crash' in failure['stderr'] and failure['retry_ms'] == 1000
    assert not runtime.closed and runtime.current() == {} and host.isEnabled()
    runtime.shutdown(); host.deleteLater()


def test_sensor_timeout_and_trailing_valid_reply_cannot_restore_bad_generation(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    host = QWidget(); runtime = ProcessRuntime(host)
    runtime.started = time.monotonic()
    runtime.process.start(sys.executable, ['-c', 'import time; time.sleep(60)'])
    drain(lambda: runtime.process.state() == QProcess.ProcessState.Running)
    runtime.pending = True; runtime.requested = time.monotonic() - 4
    runtime.snapshot = {'cpu': 50}; runtime.poll()
    drain(lambda: runtime.restart.isActive())
    assert runtime.current() == {} and 'sample-timeout' in runtime.failure_reason
    runtime.shutdown()
    host.deleteLater()
    host = QWidget(); runtime = ProcessRuntime(host)
    now = time.monotonic(); raw = dict(schema=1,cpu=50,gpu=None,sampled_at=now,metrics={},sensors=[])
    runtime.pending = True; runtime.requested = now
    killed = []
    runtime.process = SimpleNamespace(readAllStandardOutput=lambda: ('{}\n'+json.dumps(raw)+'\n').encode(), kill=lambda:killed.append(1))
    runtime.receive()
    assert runtime.current() == {} and killed == [1]
    runtime.closed = True; host.deleteLater()


def sdk_host():
    host = QWidget(); host.openrgb_effect_process = QProcess(host)
    host.openrgb_effect_active = True; host.rgb_manual_write_active = False
    host.openrgb_worker_ready = False; host.openrgb_worker_frame_inflight = False
    host.openrgb_worker_frame_started = 0; host.openrgb_worker_frame_sequence = 42
    host.openrgb_worker_stderr_buffer = ''; host.stops = []
    supervisor = SDKSupervisor(host)
    def finished(code,status):
        host.openrgb_worker_stderr_buffer += bytes(host.openrgb_effect_process.readAllStandardError()).decode()
        supervisor.finished(code,status)
    host.on_openrgb_worker_finished = finished
    host.stop_openrgb_effect = lambda reason: (host.stops.append(reason),setattr(host,'openrgb_effect_active',False))
    host.openrgb_effect_process.finished.connect(finished)
    return host,supervisor


def test_sdk_hung_readiness_or_frame_kills_exact_child_with_backoff(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    for ready in (False,True):
        host, supervisor = sdk_host()
        supervisor.launching()
        host.openrgb_effect_process.start(sys.executable,['-c','import time; time.sleep(60)'])
        drain(lambda: host.openrgb_effect_process.state() == QProcess.ProcessState.Running)
        host.openrgb_worker_ready = ready; host.openrgb_worker_frame_inflight = ready
        host.openrgb_worker_frame_started = supervisor.started = time.monotonic() - 6
        supervisor.poll()
        drain(lambda: not supervisor.active_generation)
        assert supervisor.budget.attempts == 1 and not supervisor.allowed()
        assert host.openrgb_effect_active and not host.stops
        assert ('frame-timeout' if ready else 'ready-timeout') in supervisor.reason
        supervisor.stop(); host.deleteLater()


def test_sdk_failed_start_is_bounded_and_explicit_effect_reset_rearms(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    host, supervisor = sdk_host()
    for attempt in range(4):
        supervisor.launching()
        host.openrgb_effect_process.start(str(tmp_path/'missing'))
        drain(lambda: not supervisor.active_generation)
        assert supervisor.budget.attempts == min(attempt+1,3)
    assert host.stops and not supervisor.allowed()
    supervisor.reset(); assert supervisor.allowed()
    supervisor.stop(); host.deleteLater()


def lcd_host():
    host = QWidget()
    host.command_process = QProcess(host); host.stream_process = QProcess(host)
    host.shutdown_started = False; host.stream_should_run = True; host.stream_stop_requested = False
    host.daemon_restart_in_progress = False; host.pending_apply_sequence = []
    host.stream_output_tail = ''; host.test_mode = SimpleNamespace(isChecked=lambda:False)
    host.failures = []
    host._on_command_finished = lambda code,status:host.failures.append((code,status))
    return host,LCDRuntime(host)


def test_lcd_actual_ticker_hang_and_command_deadline_are_independent(tmp_path,monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME',str(tmp_path))
    host,runtime = lcd_host(); runtime.stream_launch()
    host.stream_process.start(sys.executable,['-c','import time; print("  sent 400 bytes (theme=\\\'test\\\')",flush=True); time.sleep(60)'])
    drain(lambda: host.stream_process.bytesAvailable()>0)
    assert runtime.progress.feed(bytes(host.stream_process.readAllStandardOutput()).decode(),time.monotonic())
    runtime.progress.last_sent -= 16
    runtime.poll()
    drain(lambda: host.stream_process.state() == QProcess.ProcessState.NotRunning)
    assert 'send-timeout' in runtime.stream_reason and host.isEnabled()
    runtime.command_launch(('trcc','display','load-theme'))
    host.command_process.start(sys.executable,['-c','import time; time.sleep(60)'])
    drain(lambda: host.command_process.state() == QProcess.ProcessState.Running)
    runtime.command_started -= 46; runtime.poll()
    drain(lambda: host.command_process.state() == QProcess.ProcessState.NotRunning)
    assert runtime.command_done(-1,QProcess.ExitStatus.CrashExit,'')
    assert 'command-timeout' in runtime.command_reason
    runtime.shutdown(); host.deleteLater()


def test_lcd_watchdog_respects_tests_shutdown_and_inflight_apply(tmp_path,monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME',str(tmp_path))
    host,runtime = lcd_host(); runtime.stream_launch()
    host.stream_process.start(sys.executable,['-c','import time; time.sleep(60)'])
    drain(lambda: host.stream_process.state() == QProcess.ProcessState.Running)
    runtime.progress.started -= 60
    for gate in ('test','shutdown','apply'):
        host.test_mode = SimpleNamespace(isChecked=lambda:gate=='test')
        host.shutdown_started = gate=='shutdown'
        host.pending_apply_sequence = [('pending',)] if gate=='apply' else []
        runtime.poll()
        assert host.stream_process.state() == QProcess.ProcessState.Running
    host.shutdown_started = True; runtime.shutdown()
    host.stream_process.kill(); host.stream_process.waitForFinished(300); host.deleteLater()


def test_static_display_also_starts_existing_ipc_ticker_but_test_mode_never_does():
    method = actual_method('thermalright_display_ui.py','_daemon_stream_started')
    for test in (False,True):
        starts = []
        host = SimpleNamespace(pending_apply_animated=False,current_hardware_design_path=lambda:None,
            current_media_path=lambda:None,firmware_guard=SimpleNamespace(arm=lambda _:True),
            cli=SimpleNamespace(executable='trcc'),_log=lambda _:None,_status=lambda *a,**k:None,
            _start_stream_client=lambda:starts.append(1),test_mode=SimpleNamespace(isChecked=lambda:test),
            shutdown_started=False,pending_apply_warning='',startup_apply_active=False)
        method(host)
        assert starts == ([] if test else [1])


def test_game_probe_uses_names_not_load_and_imports_no_qt(tmp_path,monkeypatch):
    for pid,name in [('1','gamescope'),('2','mygame')]:
        folder=tmp_path/pid;folder.mkdir();(folder/'comm').write_text(name)
    assert set(game_probe.running_names(tmp_path)) == {'gamescope','mygame'}
    monkeypatch.setattr(game_probe,'running_names',lambda:iter(['mygame']))
    monkeypatch.setattr(game_probe.shutil,'which',lambda _:None)
    assert game_probe.probe(('mygame',)) == dict(schema=1,process_active=True,
        process_reason='Programmliste · mygame',gamemode=False,
        fullscreen=False,borderless=False,window_title='')
    import subprocess
    result=subprocess.run([sys.executable,'-c','from modules.lcd_runtime.v1_1 import game_probe; import sys; assert not any(n.startswith("PySide6") for n in sys.modules)'],env={**os.environ,'PYTHONPATH':str(ROOT/'src')},capture_output=True,timeout=5)
    assert result.returncode == 0,result.stderr


def test_long_static_and_looping_video_progress_stays_bounded_without_wallclock_sleep():
    progress = DisplayProgress(); progress.reset(1)
    for tick in range(120000):
        now = 1 + tick * 10
        assert progress.feed(f"  sent 400 bytes (theme='test', video frame {tick % 30}/30)\n", now)
        assert not progress.timeout(now + 10)
    assert progress.frames == 120000 and len(progress.buffer) == 0


def test_game_reply_is_ignored_after_disable_or_new_allowlist(tmp_path,monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    from modules.lcd_runtime.v1_1.game_activity import GameActivity
    host = QWidget(); host.gamemode_process = QProcess(host)
    host.shutdown_started = False; host.game_auto_detection = True
    host.game_process_names = ('oldgame',); host.game_manual = False
    updates = []; host._update_game_activity = lambda *args: updates.append(args)
    controller = GameActivity(host); controller.intent = ('oldgame',)
    output = json.dumps(dict(schema=1, process_active=True, process_reason='oldgame',gamemode=True)).encode()
    host.gamemode_process = SimpleNamespace(readAll=lambda:output)
    host.game_auto_detection = False
    controller.finished(0, QProcess.ExitStatus.NormalExit)
    assert not updates
    host.game_auto_detection = True; host.game_process_names = ('newgame',)
    # Keep the queued fresh probe bounded to this test; no process is launched.
    controller.poll = lambda:updates.append(('fresh-probe',))
    controller.finished(0, QProcess.ExitStatus.NormalExit)
    assert not updates
    APP.processEvents()
    assert updates == [('fresh-probe',)]
    controller.shutdown(); host.deleteLater()


def test_lcd_long_silent_start_does_not_renew_restart_budget(tmp_path,monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME',str(tmp_path))
    from modules.lcd_levita.v1_7.stream_recovery import StreamRestartPolicy
    from modules.levita_performance.v1_1 import fallback_lcd_fps
    method = actual_method('thermalright_display_ui.py','_on_stream_finished')
    method.__globals__.update(fallback_lcd_fps=fallback_lcd_fps,is_probable_daemon_failure=lambda _:False)
    starts=[]; statuses=[]; now=time.monotonic()
    host=SimpleNamespace(_capture_stream_output=lambda:None,stream_stop_requested=False,
        stream_should_run=True,stream_started_at=now-100,active_lcd_fps=15,stream_output_tail='',
        stream_restart_timer=SimpleNamespace(isActive=lambda:False,start=starts.append),
        stream_restart_policy=StreamRestartPolicy(attempts=3),
        lcd_runtime=SimpleNamespace(stream_done=lambda *args:None,stream_reason='',
            progress=SimpleNamespace(frames=0,last_sent=0,started=now-100)),
        _status=lambda text,**kwargs:statuses.append(text))
    method(host,7,QProcess.ExitStatus.NormalExit)
    assert not host.stream_should_run and not starts
    assert host.stream_restart_policy.attempts == 3 and 'ausgeschöpft' in statuses[-1]


def test_trcc_9104_daemon_handoff_does_not_consume_restart_budget(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    from modules.lcd_levita.v1_7.stream_recovery import StreamRestartPolicy
    method = actual_method('thermalright_display_ui.py', '_on_stream_finished')
    method.__globals__.update(
        fallback_lcd_fps=lambda value: value,
        is_probable_daemon_failure=lambda _text: False,
        daemon_owns_playback=daemon_owns_playback,
    )
    events = []
    policy = StreamRestartPolicy(attempts=2)
    host = SimpleNamespace(
        _capture_stream_output=lambda: None,
        stream_stop_requested=False,
        stream_should_run=True,
        stream_delegated=False,
        stream_output_tail="The daemon is playing 87ad:70db — it keeps the panel updated.",
        stream_restart_timer=SimpleNamespace(isActive=lambda: False, stop=lambda: events.append('stop')),
        stream_restart_policy=policy,
        _fps_restart_pending=False,
        lcd_runtime=SimpleNamespace(stream_done=lambda *args: events.append(args), stream_reason=''),
        _status=lambda text, **_kwargs: events.append(text),
        game_reason='Desktop', preview_fps=30,
        game_status_label=SimpleNamespace(setText=lambda text: events.append(text)),
    )
    method(host, 0, QProcess.ExitStatus.NormalExit)
    assert host.stream_delegated and host.stream_should_run
    assert policy.attempts == 0
    assert not any('Wiederanlauf' in str(event) for event in events)


def test_fps_change_stop_deadline_cannot_leave_ticker_stuck(tmp_path,monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME',str(tmp_path))
    host,runtime=lcd_host()
    host.stream_stop_requested=True;host._fps_restart_pending=True
    host.stream_process.start(sys.executable,['-c','import time; time.sleep(60)'])
    drain(lambda:host.stream_process.state()==QProcess.ProcessState.Running)
    runtime.stop_started=time.monotonic()-4
    runtime.poll()
    drain(lambda:host.stream_process.state()==QProcess.ProcessState.NotRunning)
    runtime.shutdown();host.deleteLater()


def test_sdk_invalid_ack_cannot_release_frame_or_renew_health():
    host,supervisor=sdk_host()
    host.openrgb_worker_frame_inflight=True
    supervisor.active_generation=True
    # Stub only the exact owned stop operation; invalid data never enters SDK.
    kills=[]
    host.openrgb_effect_process=SimpleNamespace(kill=lambda:kills.append(1))
    valid=dict(id=42,duration_ms=1,devices=[dict(key='gpu',ok=True,duration_ms=1)])
    assert supervisor.accept_frame(valid)
    for change in [dict(id=41),dict(duration_ms=float('nan')),dict(devices=[]),
                   dict(devices=[dict(key='gpu',ok='true')]),
                   dict(devices=[dict(key='gpu',ok=True),dict(key='gpu',ok=True)])]:
        supervisor.reason=''
        assert not supervisor.accept_frame({**valid,**change})
        assert host.openrgb_worker_frame_inflight and supervisor.progress_at==0
    assert len(kills)==5
    supervisor.stop();host.deleteLater()
