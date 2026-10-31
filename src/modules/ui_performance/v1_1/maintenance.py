#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-priority cache budget enforcement worker."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

LAST_SCAN_FILES = 0


def trim_cache(root: Path, budget_bytes: int) -> tuple[int, int]:
    """Remove oldest regular cache files until the requested budget is met."""
    try:
        resolved = root.expanduser().resolve(strict=True)
    except OSError:
        return 0, 0
    global LAST_SCAN_FILES
    files: list[tuple[int, int, Path]] = []
    total = 0
    for current, directories, names in os.walk(resolved, followlinks=False):
        directories[:] = [name for name in directories if not (Path(current) / name).is_symlink()]
        for name in names:
            path = Path(current) / name
            try:
                stat = path.stat(follow_symlinks=False)
                path.resolve().relative_to(resolved)
            except (OSError, ValueError):
                continue
            if path.is_symlink() or not path.is_file():
                continue
            total += stat.st_size
            files.append((stat.st_mtime_ns, stat.st_size, path))
            if len(files) % 128 == 0:
                time.sleep(0.003)
    LAST_SCAN_FILES = len(files)
    removed = 0
    target = max(0, int(budget_bytes * 0.9))
    for _mtime, size, path in sorted(files):
        if total <= target:
            break
        try:
            path.unlink()
        except OSError:
            continue
        total -= size
        removed += 1
        if removed % 32 == 0:
            time.sleep(0.003)
    return total, removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("budget", type=int)
    args = parser.parse_args()
    try:
        os.nice(15)
    except OSError:
        pass
    started = time.monotonic()
    total, removed = trim_cache(args.root, max(0, args.budget))
    print(json.dumps({
        "elapsed_ms": round((time.monotonic() - started) * 1000, 3),
        "files": LAST_SCAN_FILES,
        "removed": removed,
        "total": total,
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
