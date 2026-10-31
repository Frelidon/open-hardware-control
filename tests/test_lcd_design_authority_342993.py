"""Regression: one saved default and immutable recovery despite browsing."""
import ast
from pathlib import Path
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from modules.lcd_runtime.v1_1.design_state import DesignState
from modules.lcd_runtime.v1_1.memory_guard import MemoryGuard, MIB, HARD_LIMIT, available_memory
from modules.levita_daemon_health.v1_1 import DaemonMemorySample
from PySide6.QtCore import QProcess


class Settings:
    def __init__(self, **values): self.values = values
    def value(self, key, default=None, **kwargs): return self.values.get(key, default)
    def setValue(self, key, value): self.values[key] = value


def method(name, **extra):
    tree = ast.parse((ROOT / 'src/thermalright_display_ui.py').read_text())
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    env = dict(Path=Path, QProcess=QProcess, LayoutBlock=object, time=time, LEVITA_APPLY_COOLDOWN_SECONDS=10,
               QTimer=SimpleNamespace(singleShot=lambda delay, fn: None))
    env.update(extra)
    exec(compile(ast.Module([node], type_ignores=[]), 'real_lcd_method', 'exec'), env)
    return env[name]


def test_automatic_profile_cannot_replace_saved_disabled_or_missing_standard():
    settings = Settings(**{'thermalright/start_media': '/missing/cyber.mp4',
                           'thermalright/autostart_enabled': False})
    state = DesignState(settings)
    host = SimpleNamespace(design_state=state, _log=lambda text: None)
    assert not method('restore_profile_startup_payload')(host, {'media': '/landscape.mp4'}, startup=True)
    assert settings.values == {'thermalright/start_media': '/missing/cyber.mp4',
                               'thermalright/autostart_enabled': False}


def test_preview_changes_do_not_mutate_standard():
    settings = Settings(**{'thermalright/start_media': 'cyber.mp4',
                           'thermalright/start_hardware_design': 'orbital'})
    host = SimpleNamespace(settings=settings, _refresh_startup_status=lambda: None)
    method('_sync_autostart_selection_if_enabled')(host)
    assert settings.values == {'thermalright/start_media': 'cyber.mp4',
                               'thermalright/start_hardware_design': 'orbital'}


def test_browsing_cancels_a_start_retry_without_authorizing_preview_hardware():
    state = DesignState(Settings(**{'thermalright/start_media': 'cyber.mp4'}))
    host = SimpleNamespace(design_state=state, startup_apply_active=True,
                           restoring_startup_selection=False, _refresh_startup_status=lambda: None)
    method('_sync_autostart_selection_if_enabled')(host)
    assert state.generation == 1 and not host.startup_apply_active
    assert state.settings.value('thermalright/start_media') == 'cyber.mp4'
    host.startup_apply_active = host.restoring_startup_selection = True
    method('_sync_autostart_selection_if_enabled')(host)
    assert state.generation == 1 and host.startup_apply_active


def test_recovery_replays_last_accepted_sequence_and_never_reads_preview():
    state = DesignState(Settings())
    sequence = [(['display', 'load-theme', '/cache/cyber'], False)]
    state.capture(sequence, True)
    sequence[0][0][-1] = '/cache/landscape'
    starts = []
    host = SimpleNamespace(design_state=state, shutdown_started=False,
        daemon_restart_in_progress=True, next_hardware_apply_at=10,
        test_mode=SimpleNamespace(isChecked=lambda: False),
        apply_start_timer=SimpleNamespace(start=lambda: starts.append(True)),
        _status=lambda text: None, apply_design=lambda: (_ for _ in ()).throw(AssertionError('preview read')))
    method('_resume_after_daemon_restart')(host)
    assert starts == [True] and not host.daemon_restart_in_progress
    assert host.pending_apply_sequence == [(('display', 'load-theme', '/cache/cyber'), False)]
    assert host.pending_apply_animated and host.apply_retry_remaining == 1
    host.pending_apply_sequence.clear()
    assert state.recover(host) and len(host.pending_apply_sequence) == 1


def test_recovery_cannot_write_in_test_mode_or_after_shutdown():
    state = DesignState(Settings()); state.capture([(('load', 'cyber'), False)], True)
    host = SimpleNamespace(shutdown_started=True)
    assert not state.recover(host)
    host.shutdown_started = False
    host.test_mode = SimpleNamespace(isChecked=lambda: True)
    assert not state.recover(host)


def test_stale_startup_retry_is_cancelled_by_manual_intent():
    callbacks = []
    timer = SimpleNamespace(singleShot=lambda delay, context, fn: callbacks.append(fn))
    state = DesignState(Settings()); applied = []
    host = SimpleNamespace(design_state=state, startup_apply_active=True, startup_retry_count=0,
        shutdown_started=False, _status=lambda *args, **kwargs: None,
        apply_design=lambda **kwargs: applied.append(kwargs))
    retry = method('_schedule_startup_retry', QTimer=timer)
    retry(host, 'busy')
    state.invalidate_startup()
    callbacks.pop()()
    assert not applied
    host.startup_retry_count = 0
    retry(host, 'busy'); callbacks.pop()()
    assert applied == [{'startup': True}]


def test_manual_apply_cancels_pending_startup_before_cooldown():
    state = DesignState(Settings()); starts = []
    host = SimpleNamespace(shutdown_started=False, design_state=state,
        startup_apply_active=True, startup_apply_requested=False,
        next_hardware_apply_at=time.monotonic() + 5,
        apply_cooldown_timer=SimpleNamespace(start=starts.append),
        _status=lambda text: None)
    method('apply_design')(host)
    assert state.generation == 1 and not host.startup_apply_active
    assert host.startup_apply_requested and starts


def test_stable_1138_mib_video_does_not_restart_every_five_minutes():
    guard = MemoryGuard()
    for _ in range(60 * 24):
        assert not guard.reason(DaemonMemorySample(123, 1138 * MIB), 8 * 1024 * MIB)


def test_memory_growth_and_pressure_still_trigger_guard():
    guard = MemoryGuard()
    for rss in (1100, 1200, 1300):
        assert not guard.reason(DaemonMemorySample(1, rss * MIB))
    assert guard.reason(DaemonMemorySample(1, 1400 * MIB)) == 'sustained-rss-growth'
    assert not guard.reason(DaemonMemorySample(2, 1400 * MIB))
    assert guard.reason(DaemonMemorySample(2, HARD_LIMIT)) == 'hard-rss-limit'
    assert guard.reason(DaemonMemorySample(3, 1138 * MIB), 100 * MIB) == 'system-memory-pressure'
    assert not guard.reason(None)
    assert guard.pid == 0


def test_memory_probe_is_read_only_and_handles_unavailable_evidence(tmp_path):
    assert available_memory(tmp_path) is None
    (tmp_path / 'meminfo').write_text('MemTotal: 999 kB\nMemAvailable: 512000 kB\n')
    assert available_memory(tmp_path) == 512000 * 1024
    (tmp_path / 'meminfo').write_text('MemAvailable: invalid kB\n')
    assert available_memory(tmp_path) is None


def test_live_gpu_clock_metadata_is_frozen_with_the_hardware_request():
    block = SimpleNamespace(metric='gpu:primary:clock', ident='gpu1', format='{value:.0f}')
    state = DesignState(Settings())
    state.capture([(('load', 'cyber'), False)], True, hardware=True,
                  layout=SimpleNamespace(blocks=[block]))
    block.format = 'preview change'
    host = SimpleNamespace(design_state=state, hardware_design_active=True)
    assert method('_active_gpu_clock_block')(host).format == '{value:.0f}'
    assert state.desired.hardware
