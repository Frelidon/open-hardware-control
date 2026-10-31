"""Public platform support API."""

from .v1_0 import (
    IS_LINUX, IS_WINDOWS, current_platform, helper_command,
    platform_display_name, run_frozen_helper,
)

__all__ = [
    "IS_LINUX", "IS_WINDOWS", "current_platform", "helper_command",
    "platform_display_name", "run_frozen_helper",
]
