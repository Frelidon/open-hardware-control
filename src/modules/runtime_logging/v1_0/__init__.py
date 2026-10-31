#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Public API for runtime logging module 1.0."""

from .model import (
    LOG_MAX_CHARACTERS,
    LOG_MAX_ENTRIES,
    LOG_RETENTION_SECONDS,
    RollingLogBuffer,
    is_error_log_message,
)

__all__ = [
    "LOG_MAX_CHARACTERS",
    "LOG_MAX_ENTRIES",
    "LOG_RETENTION_SECONDS",
    "RollingLogBuffer",
    "is_error_log_message",
]
