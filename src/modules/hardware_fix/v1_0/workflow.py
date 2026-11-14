"""Local setup uses the existing fixed installers and one user service."""

from __future__ import annotations

from collections.abc import Callable


def is_gnome(desktop: str) -> bool:
    return "gnome" in desktop.casefold().split(":")


def install_local(family: str, desktop: str, inspect: Callable, execute: Callable) -> tuple[int, bool]:
    """Return (exit code, reboot pending); stop immediately on a failed step.

    A freshly installed EDID only becomes available after reboot. Repeating
    Install completes GNOME setup without rebuilding healthy boot resources.
    Fedora keeps its existing boot-only path, without Ubuntu automation.
    """
    status = inspect()
    if not (status.firmware_valid and status.boot_configuration_present):
        result = execute("install")
        if result:
            return result, False
        status = inspect()
    if status.reboot_required or not status.corrected_edid_loaded:
        return 0, True
    if family == "ubuntu" and is_gnome(desktop):
        for action in ("desktop", "automation-install"):
            result = execute(action)
            if result:
                return result, False
    return 0, False
