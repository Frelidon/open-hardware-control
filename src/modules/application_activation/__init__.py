"""Versioned single-instance activation package."""

from .v1_0 import ApplicationActivationServer, request_existing_instance, suppress_autostart_startup_feedback

__all__ = ["ApplicationActivationServer", "request_existing_instance", "suppress_autostart_startup_feedback"]
