#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only MOK state and fixed, interactive terminal command policy."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

try:
    from .distribution import detect_board, detect_distribution
except ImportError:  # direct status-helper execution from the installed tree
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from modules.mainboard_driver_setup.v1_1.distribution import detect_board, detect_distribution


MOK_CERTIFICATE = Path("/var/lib/dkms/mok.pub")
MAX_CERTIFICATE_BYTES = 1024 * 1024


@dataclass(frozen=True, slots=True)
class MokStatus:
    secure_boot: str
    certificate_exists: bool
    enrolled: bool | None
    module_loaded: bool
    module_available: bool
    module_signer: str
    mokutil_available: bool
    dkms_available: bool
    sudo_available: bool
    modprobe_available: bool
    terminal_available: bool
    distribution_id: str = ""
    distribution_name: str = "Linux"
    distribution_family: str = "unsupported"
    board_name: str = "Unbekannt"
    msi_x870_family: bool = False


def _run(arguments: list[str], timeout: int = 4) -> subprocess.CompletedProcess[str] | None:
    try:
        environment = dict(os.environ)
        environment["LC_ALL"] = "C"
        return subprocess.run(
            arguments, capture_output=True, text=True, timeout=timeout,
            check=False, env=environment,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def mok_enrollment_from_result(result: subprocess.CompletedProcess[str] | None) -> bool | None:
    """Interpret mokutil without mistaking a keyring warning for non-enrollment."""
    if result is None:
        return None
    output = f"{result.stdout or ''}\n{result.stderr or ''}".casefold()
    if "already enrolled" in output or "is enrolled" in output:
        return True
    if "not enrolled" in output or "isn't enrolled" in output:
        return False
    if result.returncode == 0:
        return True
    return None


def valid_mok_certificate(path: Path = MOK_CERTIFICATE) -> bool:
    try:
        return (
            path == MOK_CERTIFICATE
            and path.is_file()
            and not path.is_symlink()
            and 1 <= path.stat().st_size <= MAX_CERTIFICATE_BYTES
        )
    except OSError:
        return False


def inspect_mok_status() -> MokStatus:
    """Inspect only documented system state and never change Secure Boot."""
    mokutil = shutil.which("mokutil")
    certificate_exists = valid_mok_certificate()
    secure_boot = "unknown"
    enrolled: bool | None = None
    if mokutil:
        result = _run([mokutil, "--sb-state"])
        output = ((result.stdout or result.stderr) if result else "").casefold()
        if "enabled" in output:
            secure_boot = "enabled"
        elif "disabled" in output:
            secure_boot = "disabled"
        if certificate_exists:
            result = _run([mokutil, "--test-key", str(MOK_CERTIFICATE)])
            enrolled = mok_enrollment_from_result(result)
    module_loaded = False
    try:
        module_loaded = re.search(r"^nct6687\s", Path("/proc/modules").read_text(errors="replace"), re.MULTILINE) is not None
    except OSError:
        pass
    module_available = module_loaded
    signer = ""
    modinfo = shutil.which("modinfo")
    if modinfo:
        result = _run([modinfo, "-F", "filename", "nct6687"])
        module_available = bool(result and result.returncode == 0 and result.stdout.strip())
        result = _run([modinfo, "-F", "signer", "nct6687"])
        if result and result.returncode == 0:
            signer = result.stdout.strip()[:240]
    terminal_available = any(
        shutil.which(name) for name in ("ptyxis", "konsole", "gnome-terminal", "xterm")
    )
    distribution = detect_distribution()
    board_name, msi_x870 = detect_board()
    return MokStatus(
        secure_boot, certificate_exists, enrolled, module_loaded, module_available, signer,
        bool(mokutil), bool(shutil.which("dkms")), bool(shutil.which("sudo")),
        bool(shutil.which("modprobe")), terminal_available,
        distribution.distro_id, distribution.pretty_name, distribution.family,
        board_name, msi_x870,
    )


def setup_step_completion(status: MokStatus) -> tuple[bool, bool, bool, bool]:
    """Return completion for driver, certificate, MOK and module-load steps."""
    driver_ready = status.module_available or status.module_loaded
    certificate_ready = status.secure_boot == "disabled" or status.certificate_exists
    mok_ready = (
        status.secure_boot == "disabled"
        or status.enrolled is True
        or status.module_loaded
    )
    return driver_ready, certificate_ready, mok_ready, status.module_loaded


def _fixed_privileged_command(action: str) -> list[str] | None:
    sudo = shutil.which("sudo")
    if not sudo:
        return None
    if action == "generate" and not valid_mok_certificate():
        dkms = shutil.which("dkms")
        return [sudo, dkms, "generate_mok"] if dkms else None
    if action == "import" and valid_mok_certificate():
        mokutil = shutil.which("mokutil")
        return [sudo, mokutil, "--import", str(MOK_CERTIFICATE)] if mokutil else None
    if action == "load":
        modprobe = shutil.which("modprobe")
        return [sudo, modprobe, "nct6687"] if modprobe else None
    return None


def privileged_terminal_spec(action: str) -> tuple[str, list[str]] | None:
    """Wrap one fixed command in an interactive terminal; never accept a password."""
    command = _fixed_privileged_command(action)
    if not command:
        return None
    terminal = next((shutil.which(name) for name in ("ptyxis", "konsole", "gnome-terminal", "xterm") if shutil.which(name)), None)
    if not terminal:
        return None
    if Path(terminal).name == "konsole":
        return terminal, ["--hold", "-e", *command]
    if Path(terminal).name == "xterm":
        return terminal, ["-hold", "-e", *command]
    shell = shutil.which("bash") or "/bin/bash"
    fixed = shlex.join(command)
    prompt = "result=$?; printf '\\n[Enter]\\n'; read -r; exit $result"
    prefix = ["--standalone", "--"] if Path(terminal).name == "ptyxis" else ["--wait", "--"]
    return terminal, [*prefix, shell, "-lc", f"{fixed}; {prompt}"]


def _main(arguments: list[str]) -> int:
    if arguments != ["--status-json"]:
        return 2
    print(json.dumps(asdict(inspect_mok_status()), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
