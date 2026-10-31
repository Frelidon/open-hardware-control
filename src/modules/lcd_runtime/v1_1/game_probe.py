# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only process/GameMode probe isolated from the Qt event loop."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from modules.levita_performance.v1_1 import normalize_process_names, parse_gamemode_status, process_game_signal
from modules.platform_support.v1_0 import helper_command


def running_names(proc_root=Path('/proc')):
    try:
        entries = proc_root.iterdir()
        for entry in entries:
            if entry.name.isdigit():
                try:
                    yield (entry / 'comm').read_text(errors='replace').strip()
                except OSError:
                    continue
    except OSError:
        return


def window_state():
    bridge = Path(__file__).resolve().parents[2] / 'snapshot_manager' / 'v1_0' / 'fullscreen_probe.py'
    if not bridge.is_file() or 'kde' not in os.environ.get('XDG_CURRENT_DESKTOP', '').casefold():
        return False, False, ''
    try:
        program, arguments = helper_command(bridge)
        result = subprocess.run(
            [program, *arguments], capture_output=True, text=True,
            timeout=3, check=False,
        )
        payload = json.loads(result.stdout[-4096:])
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, TypeError):
        return False, False, ''
    return (
        bool(payload.get('fullscreen')),
        bool(payload.get('borderless')),
        str(payload.get('title', ''))[:128],
    )


def probe(configured, *, detect_fullscreen=True, detect_borderless=True):
    active, reason = process_game_signal(running_names(), configured)
    fullscreen, borderless, window_title = window_state() if (
        detect_fullscreen or detect_borderless
    ) else (False, False, '')
    gamemode = False
    executable = shutil.which('gamemoded')
    if executable:
        try:
            result = subprocess.run([executable, '-s'], capture_output=True, text=True, timeout=2, check=False)
            gamemode = parse_gamemode_status(result.stdout[-4096:], result.returncode)
        except (OSError, subprocess.TimeoutExpired):
            pass
    return dict(
        schema=1,
        process_active=active,
        process_reason=reason,
        gamemode=gamemode,
        fullscreen=bool(fullscreen and detect_fullscreen),
        borderless=bool(borderless and detect_borderless),
        window_title=window_title,
    )


if __name__ == '__main__':
    configured = normalize_process_names(sys.argv[1] if len(sys.argv) > 1 else '')
    fullscreen = len(sys.argv) < 3 or sys.argv[2] == '1'
    borderless = len(sys.argv) < 4 or sys.argv[3] == '1'
    print(json.dumps(probe(configured, detect_fullscreen=fullscreen, detect_borderless=borderless)))
