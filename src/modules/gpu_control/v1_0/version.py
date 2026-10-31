# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify the installed LACT package version; its CLI has no --version flag."""
from __future__ import annotations

import re
import shutil
import subprocess

from .client import LactError


def require_supported_version() -> None:
    if shutil.which("lact") is None:
        raise LactError("LACT 0.10.1 or newer is required for GPU writes")
    queries = (
        ("rpm", ("rpm", "-q", "--qf", "%{VERSION}", "lact")),
        ("pacman", ("pacman", "-Q", "lact")),
        ("dpkg-query", ("dpkg-query", "-W", "-f=${Version}", "lact")),
    )
    for manager, command in queries:
        if shutil.which(manager) is None:
            continue
        try:
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=2, check=False)
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode:
            continue
        # An Arch query includes the package name; Debian may include an epoch.
        value = result.stdout.strip().split()[-1].split(":")[-1] if result.stdout.strip() else ""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:[-+._].*)?$", value)
        if match and tuple(int(number) for number in match.groups()) >= (0, 10, 1):
            return
    raise LactError("LACT 0.10.1 or newer is required for GPU writes")
