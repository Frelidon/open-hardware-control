"""Stable public API for hardware backend selection 1.0."""

from .policy import (
    BackendResolution,
    DISPLAY_BACKENDS,
    FAN_BACKENDS,
    normalize_backend_choice,
    resolve_backend,
)

MODULE_VERSION = "1.0"

__all__ = [
    "BackendResolution",
    "DISPLAY_BACKENDS",
    "FAN_BACKENDS",
    "MODULE_VERSION",
    "normalize_backend_choice",
    "resolve_backend",
]
