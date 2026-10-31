"""Persistent exit phases and side-label activation without moving components."""
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('OHC_DISABLE_HARDWARE_IO', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from modules.application_shutdown.v1_1 import (
    classify_records,
    has_confirmed_tray_choice,
    journal,
    latest_shutdown_report,
    watcher,
)
from modules.application_shutdown.v1_1.sequence import ShutdownSequence
from modules.pc_case_profiles.v1_5.diagram import PCLayoutDiagram
from rgb_devices import flori_rgb_layout_profile

APP = QApplication.instance() or QApplication([])


def test_phases_survive_ui_log_failure_and_redact_private_path(monkeypatch, tmp_path):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    def broken(_text): raise RuntimeError('deleted widget')
    sequence = ShutdownSequence(broken)
    sequence.run('test', lambda: 1)
    sequence.run('failure', lambda: (_ for _ in ()).throw(OSError('private')))
    journal.record('test-home', detail=str(Path.home()))
    path = tmp_path / 'open-hardware-control/shutdown.jsonl'
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert [r['event'] for r in records[:4]] == ['phase-start', 'phase-done', 'phase-start', 'phase-failed']
    assert str(Path.home()) not in path.read_text()
    assert path.stat().st_mode & 0o777 == 0o600


def test_watcher_exits_on_exact_parent_pid_reuse(monkeypatch, tmp_path):
    identities = iter([('123', 'S'), ('456', 'S')])
    monkeypatch.setattr(watcher, 'identity', lambda _pid: next(identities))
    path = tmp_path / 'shutdown.jsonl'
    path.touch()
    watcher.watch(123456789, tmp_path, duration=.1, interval=.01)
    assert json.loads(path.read_text())['event'] == 'parent-gone'


def test_journal_does_not_follow_existing_symlink(monkeypatch, tmp_path):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    directory = tmp_path / 'open-hardware-control'; directory.mkdir()
    target = tmp_path / 'unrelated'; target.write_text('unchanged')
    (directory / 'shutdown.jsonl').symlink_to(target)
    journal.record('test')
    assert target.read_text() == 'unchanged'


def test_arm_records_native_timeout_and_independent_bounded_observer(monkeypatch, tmp_path):
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    monkeypatch.setenv('OHC_DISABLE_HARDWARE_IO', '0')
    monkeypatch.setattr(journal, '_armed', False)
    monkeypatch.setattr(journal, '_trace', None)
    registered, dumped, started = [], [], []
    monkeypatch.setattr(journal.atexit, 'register', registered.append)
    monkeypatch.setattr(journal.faulthandler, 'dump_traceback_later', lambda *a, **k: dumped.append((a, k)))
    monkeypatch.setattr(journal.subprocess, 'Popen', lambda *a, **k: started.append((a, k)))
    journal.begin('test exit'); journal.begin('second request')
    assert len(started) == 1 and len(dumped) == 1
    assert dumped[0][0] == (15,) and dumped[0][1]['repeat'] is False
    assert started[0][1]['close_fds'] is True
    assert started[0][0][0][2] == str(os.getpid())
    assert journal._trace.name is not None
    journal._trace.close()


def test_shutdown_diagnostics_distinguish_tray_from_a_clean_exit():
    tray = classify_records([
        {'event': 'window-close', 'pid': 17, 'close_to_tray': True, 'explicit': False},
        {'event': 'window-close-choice', 'pid': 17, 'decision': 'tray'},
    ])
    assert tray.status == 'continued-in-tray' and tray.pid == 17

    clean = classify_records([
        {'event': 'exit-request', 'pid': 18},
        {'event': 'phase-start', 'pid': 18, 'phase': 'hardware'},
        {'event': 'phase-done', 'pid': 18, 'phase': 'hardware'},
        {'event': 'qt-loop-returned', 'pid': 18},
        {'event': 'parent-gone', 'parent_pid': 18},
    ])
    assert clean.status == 'clean' and not clean.phase


def test_shutdown_diagnostics_name_last_unfinished_phase_and_ignore_bad_lines(tmp_path):
    path = tmp_path / 'shutdown.jsonl'
    path.write_text(
        'not-json\n'
        + json.dumps({'event': 'exit-request', 'pid': 19}) + '\n'
        + json.dumps({'event': 'phase-start', 'pid': 19, 'phase': 'remaining-processes'}) + '\n'
        + json.dumps({'event': 'parent-still-alive', 'parent_pid': 19}) + '\n',
        encoding='utf-8',
    )
    report = latest_shutdown_report(path)
    assert report.status == 'stuck'
    assert report.phase == 'remaining-processes'


def test_shutdown_diagnostics_report_cancelled_close():
    report = classify_records([
        {'event': 'window-close', 'pid': 20, 'close_to_tray': True, 'explicit': False},
        {'event': 'window-close-choice', 'pid': 20, 'decision': 'cancel'},
    ])
    assert report.status == 'cancelled'


def test_previous_session_crash_and_failed_restore_are_not_reported_clean():
    crash = classify_records([
        {'event': 'app-start', 'pid': 31, 'starttime': '1'},
        {'event': 'parent-gone', 'parent_pid': 31},
    ])
    assert crash.status == 'unexpected-exit'
    failed = classify_records([
        {'event': 'exit-request', 'pid': 32},
        {'event': 'phase-failed', 'pid': 32, 'phase': 'coolercontrol-return', 'error': 'RuntimeError'},
        {'event': 'qt-loop-returned', 'pid': 32},
    ])
    assert failed.status == 'cleanup-failed'
    assert 'coolercontrol-return' in failed.reason


def test_crash_recovery_uses_only_owned_process_identities(monkeypatch, tmp_path):
    path = tmp_path / 'shutdown.jsonl'; path.touch()
    stopped = []
    monkeypatch.setattr(watcher, '_stop_owned', lambda pid, start: stopped.append((pid, start)) or 'stopped')
    monkeypatch.setattr(watcher.time, 'sleep', lambda _: None)
    rows = [
        {'event': 'app-start', 'pid': 41},
        {'event': 'owned-process-start', 'pid': 41, 'child_pid': 42, 'starttime': 'old'},
        {'event': 'owned-process-finished', 'pid': 41, 'child_pid': 42},
        {'event': 'owned-process-start', 'pid': 41, 'child_pid': 43, 'starttime': 'new'},
        {'event': 'owned-trcc-start', 'pid': 41, 'child_pid': 44, 'starttime': 'trcc'},
        {'event': 'owned-trcc-replaced', 'pid': 41, 'child_pid': 46,
         'previous_child_pid': 44, 'starttime': 'trcc-new'},
        {'event': 'owned-process-start', 'pid': 99, 'child_pid': 45, 'starttime': 'foreign'},
    ]
    watcher.recover_owned(41, path, rows)
    assert stopped == [(43, 'new'), (46, 'trcc-new')]
    events = [json.loads(line)['event'] for line in path.read_text().splitlines()]
    assert events == ['unexpected-exit-recovery', 'owned-process-recovery', 'owned-trcc-recovery']


def test_exact_identity_check_refuses_replaced_child(monkeypatch):
    monkeypatch.setattr(watcher, 'identity', lambda pid: ('replacement', 'S'))
    monkeypatch.setattr(watcher.os, 'kill', lambda *_: pytest.fail('must not signal a replaced PID'))
    assert watcher._stop_owned(12, 'original') == 'already-gone-or-replaced'


def test_explicit_tray_choice_can_be_migrated_to_the_persistent_setting(tmp_path):
    path = tmp_path / 'shutdown.jsonl'
    path.write_text(
        json.dumps({'event': 'window-close', 'pid': 21, 'close_to_tray': True}) + '\n'
        + json.dumps({'event': 'window-close-choice', 'pid': 21, 'decision': 'tray'}) + '\n',
        encoding='utf-8',
    )
    assert has_confirmed_tray_choice(path)

    path.write_text(
        json.dumps({'event': 'window-close', 'pid': 22, 'close_to_tray': True}) + '\n',
        encoding='utf-8',
    )
    assert not has_confirmed_tray_choice(path)

    path.write_text(
        json.dumps({'event': 'window-close', 'pid': 23, 'close_to_tray': True}) + '\n'
        + json.dumps({'event': 'window-close-choice', 'pid': 23, 'decision': 'automatic-tray'}) + '\n',
        encoding='utf-8',
    )
    assert not has_confirmed_tray_choice(path)
    assert classify_records(json.loads(line) for line in path.read_text().splitlines()).status == 'continued-in-tray'


@pytest.mark.parametrize('size', [(1600, 1000), (920, 620), (760, 570)])
def test_side_label_single_click_focuses_and_opens_without_move(size):
    diagram = PCLayoutDiagram()
    diagram.set_slots(flori_rgb_layout_profile('thermalright')[1])
    diagram.resize(*size); diagram.show(); APP.processEvents()
    focused, opened, moved = [], [], []
    diagram.slot_focused.connect(focused.append)
    diagram.slot_selected.connect(opened.append)
    diagram.slot_moved.connect(lambda *args: moved.append(args))
    snapshot = [(s.slot_id, s.x, s.y) for s in diagram.slots]
    label = next((s, r) for s, r in zip(diagram.slots, diagram.label_rectangles()) if r is not None)
    key = label[0].slot_id or label[0].position
    QTest.mouseClick(diagram, Qt.MouseButton.LeftButton, pos=label[1].center().toPoint())
    assert focused == [key] and opened == [key] and not moved
    assert not diagram.drag_slot_id
    assert snapshot == [(s.slot_id, s.x, s.y) for s in diagram.slots]
    diagram.close(); diagram.deleteLater()
