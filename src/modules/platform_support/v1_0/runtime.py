#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small cross-platform runtime and frozen-helper contract."""

from __future__ import annotations

import os
from pathlib import Path
import runpy
import sys
from typing import Sequence


IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")
_SOURCE_ROOT = Path(__file__).resolve().parents[3]
_HELPER_PREFIX = "--ohc-helper"


def current_platform(value: str | None = None) -> str:
    target = str(value or sys.platform).casefold()
    if target.startswith("win"):
        return "windows"
    if target.startswith("linux"):
        return "linux"
    return "other"


def platform_display_name(value: str | None = None) -> str:
    return {"windows": "Windows", "linux": "Linux"}.get(current_platform(value), "Desktop")


def _application_root() -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    return Path(str(frozen_root)).resolve() if frozen_root else _SOURCE_ROOT


def _safe_relative_helper(path: Path) -> str:
    candidate = path.resolve()
    roots = (_SOURCE_ROOT, _application_root())
    for root in roots:
        try:
            relative = candidate.relative_to(root.resolve())
        except ValueError:
            continue
        if relative.suffix == ".py" and ".." not in relative.parts:
            return relative.as_posix()
    raise ValueError("helper must be a Python file inside the OHC application tree")


def helper_command(path: Path, arguments: Sequence[object] = ()) -> tuple[str, list[str]]:
    """Return a QProcess-friendly command for source and PyInstaller builds."""

    clean = [str(value) for value in arguments]
    if getattr(sys, "frozen", False):
        return sys.executable, [_HELPER_PREFIX, _safe_relative_helper(path), *clean]
    return sys.executable, [os.fspath(path), *clean]


def run_frozen_helper(arguments: Sequence[str]) -> int | None:
    """Dispatch an allowlisted bundled Python helper in a child OHC process."""

    values = list(arguments)
    if len(values) < 3 or values[1] != _HELPER_PREFIX:
        return None
    relative = Path(values[2])
    if relative.is_absolute() or relative.suffix != ".py" or ".." in relative.parts:
        return 2
    target = (_application_root() / relative).resolve()
    try:
        target.relative_to(_application_root())
    except ValueError:
        return 2
    if not target.is_file():
        return 2
    sys.argv = [os.fspath(target), *values[3:]]
    try:
        runpy.run_path(os.fspath(target), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0) if isinstance(exc.code, (int, type(None))) else 1
    return 0
