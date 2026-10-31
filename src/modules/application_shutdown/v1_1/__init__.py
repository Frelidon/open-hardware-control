# SPDX-License-Identifier: GPL-3.0-or-later
"""Error-isolated orderly shutdown; never a new hardware writer."""
from .diagnostics import (
    ShutdownReport,
    classify_records,
    has_confirmed_tray_choice,
    latest_shutdown_report,
)
from .process_cleanup import stop_pipe_bound_process

__all__ = [
    "ShutdownReport",
    "classify_records",
    "has_confirmed_tray_choice",
    "latest_shutdown_report",
    "stop_pipe_bound_process",
]
