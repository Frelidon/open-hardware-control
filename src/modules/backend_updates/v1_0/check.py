#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Out-of-process entry point for the network-bound backend audit."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from modules.backend_updates.v1_0.policy import collect_backend_updates  # noqa: E402


def main() -> int:
    try:
        print(json.dumps(collect_backend_updates(), ensure_ascii=False))
        return 0
    except Exception as exc:  # the GUI needs a bounded diagnostic instead of a traceback
        print(json.dumps({"ok": False, "error": str(exc)[:500]}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
