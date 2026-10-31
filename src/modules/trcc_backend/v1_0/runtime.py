# SPDX-License-Identifier: GPL-3.0-or-later
"""Ubuntu-only TRCC process adapter; no stock backend or global PATH changes."""
from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any
import xml.etree.ElementTree as ET

from modules.backend_updates.v1_0.executables import _trusted_file, is_ubuntu_runtime


DMI_HELPER = Path("/usr/libexec/open-hardware-control-dmi-memory-helper")
DMI_POLICY = Path("/usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.dmi.policy")
SYSTEM_PYTHON = Path("/usr/bin/python3")
SYSTEM_TRCC = frozenset({"/usr/local/bin/trcc", "/usr/bin/trcc"})


def command_prefix(executable: str, *, ubuntu: bool | None = None) -> tuple[str, ...]:
    """Keep Fedora/user installs untouched; adapt the audited Ubuntu package."""
    ubuntu = is_ubuntu_runtime() if ubuntu is None else ubuntu
    if (not ubuntu or getattr(sys, "frozen", False) or executable not in SYSTEM_TRCC
            or not _trusted_file(Path(executable), executable=True)):
        return (executable,)
    return (str(SYSTEM_PYTHON), str(Path(__file__).with_name("launcher.py")), executable)


def memory_helper_available() -> bool:
    if not (_trusted_file(DMI_HELPER, executable=True) and _trusted_file(DMI_POLICY)):
        return False
    try:
        with DMI_POLICY.open("rb") as stream:
            data = stream.read(16_385)
        if len(data) > 16_384:
            return False
        policy = ET.fromstring(data)
        action = policy.find("action[@id='io.github.Frelidon.OpenHardwareControl.memory-info']")
        return (action is not None
                and action.findtext("defaults/allow_any") == "no"
                and action.findtext("defaults/allow_inactive") == "no"
                and action.findtext("defaults/allow_active") == "yes"
                and action.findtext("annotate[@key='org.freedesktop.policykit.exec.path']") == str(DMI_HELPER))
    except (OSError, ET.ParseError):
        return False


def configure_backend(linux: Any, daemon: Any, prefix: tuple[str, ...]) -> None:
    """Adapt only this child process; optional metadata never asks for a secret.

    Upstream 9.10.4 uses these two small factories. Only its exact read-only
    memory query may use the OHC helper. Unknown/general DMI, SMART and IMC
    requests receive no additional authorization and degrade to unavailable.
    """
    def metadata_command(binary: str, args: list[str]) -> list[str]:
        if binary == "dmidecode" and args == ["-t", "memory"] and memory_helper_available():
            return ["/usr/bin/pkexec", str(DMI_HELPER)]
        return [binary, *args]

    if not callable(getattr(linux, "_privileged_cmd", None)):
        raise RuntimeError("TRCC memory-command adapter is unavailable")
    if not callable(getattr(daemon, "_daemon_spawn_cmd", None)):
        raise RuntimeError("TRCC daemon-command adapter is unavailable")
    linux._privileged_cmd = metadata_command
    daemon._daemon_spawn_cmd = lambda: [*prefix, "daemon"]
    # IMC uses a separate upstream pkexec path and is optional metadata, not
    # display control. This documented flag is inherited by the OHC daemon.
    os.environ["TRCC_DISABLE_LIVE_IMC"] = "1"
