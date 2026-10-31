#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small read-only process-name probe used outside the GUI thread."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    names: set[str] = set()
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            name = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()
        except (OSError, ValueError):
            continue
        if name:
            names.add(name.casefold())
        try:
            with (entry / "cmdline").open("rb") as handle:
                executable = handle.read(4096).split(b"\0", 1)[0]
            basename = executable.decode("utf-8", "replace").replace("\\", "/").rsplit("/", 1)[-1]
        except (OSError, ValueError):
            basename = ""
        if basename:
            names.add(basename.casefold())
    print(json.dumps({"processes": sorted(names)[:4096]}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
