# SPDX-License-Identifier: GPL-3.0-or-later
"""Observe exact parent identity and release only registered owned helpers."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def identity(pid):
    try:
        fields = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()
        return fields[19], fields[0]  # starttime, state; comm may contain spaces.
    except (OSError, IndexError):
        return None


def watch(pid, directory, duration=90, interval=1):
    original = identity(pid)
    if original is None: return
    path = Path(directory) / 'shutdown.jsonl'
    next_report = 10
    started = time.monotonic()
    while time.monotonic() - started < duration:
        current = identity(pid)
        elapsed = time.monotonic() - started
        ended = current is None or current[0] != original[0] or current[1] == 'Z'
        if ended or elapsed >= next_report:
            payload = dict(event='parent-gone' if ended else 'parent-still-alive',
                           parent_pid=pid, elapsed=round(elapsed, 2), time=time.time())
            if not ended:
                try:
                    status = (Path('/proc') / str(pid) / 'status').read_text().splitlines()
                    payload['status'] = [s for s in status if s.startswith(('State:', 'VmRSS:', 'Threads:'))]
                except OSError: pass
            try:
                descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW)
                with os.fdopen(descriptor, 'w') as stream:
                    stream.write(json.dumps(payload) + '\n')
            except OSError: return
            if ended: return
            next_report += 20
        time.sleep(interval)


def _rows(path):
    if path.is_symlink():
        return []
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, 'rb') as stream:
            size = os.fstat(stream.fileno()).st_size
            if size > 256 * 1024:
                stream.seek(-256 * 1024, os.SEEK_END)
                stream.readline()
            data = stream.read(256 * 1024)
    except OSError:
        return []
    rows = []
    for line in data.splitlines():
        try:
            value = json.loads(line)
        except (ValueError, TypeError):
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _append(path, event, **fields):
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(event=event, time=time.time(), **fields)) + '\n')
    except OSError:
        pass


def _stop_owned(pid, starttime):
    """Signals are limited to the exact process incarnation registered by OHC."""
    original = identity(pid)
    if original is None or original[0] != starttime or original[1] == 'Z':
        return 'already-gone-or-replaced'
    try:
        os.kill(pid, signal.SIGTERM)
        for _ in range(20):
            time.sleep(0.1)
            current = identity(pid)
            if current is None or current[0] != starttime or current[1] == 'Z':
                return 'stopped'
        current = identity(pid)
        if current is not None and current[0] == starttime and current[1] != 'Z':
            os.kill(pid, signal.SIGKILL)
        for _ in range(10):
            time.sleep(0.1)
            current = identity(pid)
            if current is None or current[0] != starttime or current[1] == 'Z':
                return 'stopped'
    except (OSError, ValueError) as exc:
        return type(exc).__name__
    return 'still-running'


def recover_owned(parent_pid, path, rows):
    """Best effort after parent death; never stop a preexisting system daemon."""
    starts = [index for index, row in enumerate(rows)
              if row.get('event') == 'app-start' and row.get('pid') == parent_pid]
    session = [row for row in rows[starts[-1] if starts else 0:]
               if row.get('pid') == parent_pid]
    if not session:
        return
    events = [str(row.get('event') or '') for row in session]
    clean = 'qt-loop-returned' in events and 'phase-failed' not in events and any(
        row.get('event') == 'cleanup-result' and row.get('success') is True
        for row in session
    )
    if clean:
        return
    _append(path, 'unexpected-exit-recovery', parent_pid=parent_pid,
            reason='No verified clean cleanup and Qt return')
    owned = {}
    trcc = {}
    coolercontrol_lease = False
    for row in session:
        event = row.get('event')
        child_pid = row.get('child_pid')
        if event == 'owned-process-start' and isinstance(child_pid, int):
            owned[child_pid] = str(row.get('starttime') or '')
        elif event in {'owned-process-finished', 'owned-process-result'} and isinstance(child_pid, int):
            if event == 'owned-process-finished' or row.get('stopped') is True:
                owned.pop(child_pid, None)
        elif event in {'owned-trcc-start', 'owned-trcc-replaced'} and isinstance(child_pid, int):
            previous_child_pid = row.get('previous_child_pid')
            if event == 'owned-trcc-replaced' and isinstance(previous_child_pid, int):
                trcc.pop(previous_child_pid, None)
            trcc[child_pid] = str(row.get('starttime') or '')
        elif event == 'owned-trcc-stopped' and isinstance(child_pid, int):
            trcc.pop(child_pid, None)
        elif event == 'coolercontrol-stopped-for-ohc':
            coolercontrol_lease = True
        elif event in {'coolercontrol-returned', 'coolercontrol-explicit-setting'}:
            coolercontrol_lease = False
    for child_pid, starttime in owned.items():
        outcome = _stop_owned(child_pid, starttime)
        _append(path, 'owned-process-recovery', parent_pid=parent_pid,
                child_pid=child_pid, outcome=outcome)
    if trcc:
        # The separate firmware guard gets its chance to disconnect first.
        time.sleep(3)
        for child_pid, starttime in trcc.items():
            outcome = _stop_owned(child_pid, starttime)
            _append(path, 'owned-trcc-recovery', parent_pid=parent_pid,
                    child_pid=child_pid, outcome=outcome)
    if coolercontrol_lease:
        try:
            result = subprocess.run(
                ['/usr/bin/pkexec', '/usr/bin/systemctl', 'start', 'coolercontrold.service'],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=20, check=False,
            )
            outcome = 'restored' if result.returncode == 0 else f'exit-{result.returncode}'
        except (OSError, subprocess.SubprocessError) as exc:
            outcome = type(exc).__name__
        _append(path, 'coolercontrol-recovery', parent_pid=parent_pid, outcome=outcome)


def watch_lifetime(pid, directory, interval=1):
    original = identity(pid)
    if original is None:
        return
    path = Path(directory) / 'shutdown.jsonl'
    while True:
        current = identity(pid)
        if current is None or current[0] != original[0] or current[1] == 'Z':
            break
        time.sleep(interval)
    _append(path, 'parent-gone', parent_pid=pid)
    recover_owned(pid, path, _rows(path))


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--lifetime':
        watch_lifetime(int(sys.argv[2]), Path(sys.argv[3]))
    else:
        watch(int(sys.argv[1]), Path(sys.argv[2]))
