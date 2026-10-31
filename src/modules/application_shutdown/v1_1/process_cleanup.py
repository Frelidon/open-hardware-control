# SPDX-License-Identifier: GPL-3.0-or-later
"""Close an owned helper's input first; never assume permission to signal root."""
import subprocess
from privacy_logging import append_startup_event


def stop_pipe_bound_process(process):
    """Bounded EOF -> wait -> permitted terminate/kill, no privileged kill tool.

    The fixed fan helper exits its existing stdin session on EOF. pkexec may
    make it root-owned; its desktop parent cannot send it Unix signals. A
    denied fallback is logged, not propagated into unrelated exit cleanup.
    """
    if process is None:
        return True
    try:
        if process.stdin is not None:
            process.stdin.close()
    except (OSError, ValueError):
        pass
    for action in (None, process.terminate, process.kill):
        try:
            if process.poll() is not None:
                return True
            if action is not None:
                action()
            process.wait(timeout=1.0)
            return True
        except subprocess.TimeoutExpired:
            continue
        except (OSError, ValueError) as exc:
            # Includes PermissionError/ProcessLookupError and their races.
            if process.poll() is not None:
                return True
            append_startup_event(
                f"SYSTEMENDE: phase=fan-helper state=pending type={type(exc).__name__} "
                "stdin=closed signals=unavailable")
            return False
    append_startup_event("SYSTEMENDE: phase=fan-helper state=pending type=TimeoutExpired stdin=closed")
    return False
