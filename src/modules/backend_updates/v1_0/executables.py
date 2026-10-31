# SPDX-License-Identifier: GPL-3.0-or-later
"""Ubuntu-only preference for explicitly installed, root-owned OHC backends.

No environment override, user-writable search path, hardware probe or installer
is used here. Other distributions keep their existing system executable.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import sys


_APPROVED_EXECUTABLES = {
    "openrgb": Path("/usr/local/lib/open-hardware-control-backends/openrgb-1.0/openrgb"),
    "liquidctl": Path("/usr/local/lib/open-hardware-control-backends/liquidctl-1.16.0/bin/liquidctl"),
}
_APPROVED_ROOTS = {
    "openrgb": Path("/usr/local/lib/open-hardware-control-backends/openrgb-1.0"),
    "liquidctl": Path("/usr/local/lib/open-hardware-control-backends/liquidctl-1.16.0"),
}


def is_ubuntu_runtime() -> bool:
    try:
        release = Path("/etc/os-release").read_text(encoding="utf-8")
    except OSError:
        return False
    values = {}
    for line in release.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key] = value.strip().strip('"').strip("'").casefold()
    return values.get("ID") == "ubuntu" or "ubuntu" in values.get("ID_LIKE", "").split()


def _trusted_file(path: Path, *, executable: bool = False) -> bool:
    try:
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0
                or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)):
            return False
        for parent in path.parents:
            info = parent.lstat()
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid != 0
                    or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)):
                return False
        return not executable or os.access(path, os.X_OK)
    except OSError:
        return False


def _resolve(component: str, default: str, ubuntu_runtime: bool | None) -> str:
    ubuntu = is_ubuntu_runtime() if ubuntu_runtime is None else bool(ubuntu_runtime)
    preferred = _APPROVED_EXECUTABLES[component]
    return str(preferred) if ubuntu and _trusted_file(preferred, executable=True) else default


def resolve_openrgb_executable(default: str = "openrgb", *, ubuntu_runtime: bool | None = None) -> str:
    return _resolve("openrgb", default, ubuntu_runtime)


def resolve_liquidctl_executable(default: str = "liquidctl", *, ubuntu_runtime: bool | None = None) -> str:
    return _resolve("liquidctl", default, ubuntu_runtime)


def resolve_liquidctl_python(default: str, *, ubuntu_runtime: bool | None = None) -> str:
    """Use the approved venv for the CAM helper, never for frozen Qt helpers."""
    if getattr(sys, "frozen", False):
        return default
    executable = _resolve("liquidctl", "", ubuntu_runtime)
    if not executable:
        return default
    python = Path(executable).parent / "python"
    try:
        info = python.lstat()
        if info.st_uid != 0:
            return default
        if stat.S_ISLNK(info.st_mode):
            # The venv has a root-owned symlink to the root-protected system
            # interpreter. Validate the resolved executable instead of rejecting
            # a standard venv, without allowing a user-controlled interpreter.
            target = python.resolve(strict=True)
            if not _trusted_file(target, executable=True):
                return default
        elif not _trusted_file(python, executable=True):
            return default
        return str(python)
    except (OSError, RuntimeError):
        return default


def preferred_backend_version(component: str, *, ubuntu_runtime: bool | None = None) -> str:
    """Read installation metadata only when executable and manifest are trusted."""
    if component not in _APPROVED_EXECUTABLES:
        return ""
    if _resolve(component, "", ubuntu_runtime) == "":
        return ""
    manifest = _APPROVED_ROOTS[component] / "backend-version.json"
    if not _trusted_file(manifest):
        return ""
    try:
        if manifest.stat().st_size > 4096:
            return ""
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("component") != component:
            return ""
        version = payload.get("version")
        if not isinstance(version, str) or len(version) > 32:
            return ""
        return version
    except (OSError, ValueError, TypeError):
        return ""
