#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Cooling ownership helpers for Open Hardware Control.

The functions in this module never write fan PWM values.  They only detect a
competing CoolerControl daemon and, after an explicit user action, ask systemd
to stop/start that daemon through pkexec.  This keeps ownership transitions
separate from the NCT6687 fan helper and makes them easy to test.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

COOLERCONTROL_SERVICE = "coolercontrold.service"
COOLERCONTROL_PROCESS = "coolercontrold"


@dataclass(frozen=True)
class CoolingOwnerStatus:
    coolercontrol_service_active: bool = False
    coolercontrol_process_active: bool = False

    @property
    def coolercontrol_active(self) -> bool:
        return self.coolercontrol_service_active or self.coolercontrol_process_active

    @property
    def owner(self) -> str:
        return "coolercontrol" if self.coolercontrol_active else "available"


def _run(command: list[str], *, timeout: float = 5.0) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.SubprocessError):
        return None


def detect_cooling_owner() -> CoolingOwnerStatus:
    systemctl = shutil.which("systemctl")
    service_active = False
    if systemctl:
        result = _run([systemctl, "is-active", "--quiet", COOLERCONTROL_SERVICE])
        service_active = bool(result is not None and result.returncode == 0)

    pgrep = shutil.which("pgrep")
    process_active = False
    if pgrep:
        result = _run([pgrep, "-x", COOLERCONTROL_PROCESS])
        process_active = bool(result is not None and result.returncode == 0)

    return CoolingOwnerStatus(service_active, process_active)


def _switch_coolercontrol(action: str, *, timeout: float = 20.0) -> tuple[bool, str]:
    if action not in {"start", "stop"}:
        return False, "Ungültige CoolerControl-Aktion"
    pkexec = shutil.which("pkexec") or "/usr/bin/pkexec"
    systemctl = shutil.which("systemctl") or "/usr/bin/systemctl"
    if not shutil.which("pkexec"):
        return False, "pkexec/Polkit ist nicht verfügbar"
    result = _run([pkexec, systemctl, action, COOLERCONTROL_SERVICE], timeout=timeout)
    if result is None:
        return False, "CoolerControl-Umschaltung konnte nicht gestartet werden"
    if result.returncode != 0:
        text = (result.stderr or result.stdout or "").strip()
        if result.returncode in {126, 127}:
            return False, "Authentifizierung wurde abgebrochen oder verweigert"
        return False, text or f"systemctl {action} fehlgeschlagen ({result.returncode})"
    return True, ""


def stop_coolercontrol() -> tuple[bool, str]:
    return _switch_coolercontrol("stop")


def start_coolercontrol() -> tuple[bool, str]:
    return _switch_coolercontrol("start")
