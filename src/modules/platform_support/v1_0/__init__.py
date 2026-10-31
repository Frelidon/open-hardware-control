"""Platform Support 1.0."""

from .runtime import (
    IS_LINUX, IS_WINDOWS, current_platform, helper_command,
    platform_display_name, run_frozen_helper,
)

MODULE_VERSION = "1.0"

__all__ = [
    "IS_LINUX", "IS_WINDOWS", "MODULE_VERSION", "current_platform",
    "helper_command", "platform_display_name", "run_frozen_helper",
]
