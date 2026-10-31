#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small out-of-process entry point for the network-bound release check."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import argparse

SOURCE_ROOT = Path(__file__).resolve().parents[3]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from modules.openlinkhub_update.v1_0.policy import collect_update_status, prepare_user_space_update  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-user-space", type=Path)
    args = parser.parse_args()
    try:
        result = (
            {"ok": True, **prepare_user_space_update(args.prepare_user_space)}
            if args.prepare_user_space is not None else collect_update_status()
        )
    except Exception as exc:
        result = {"ok": False, "error": str(exc)[:500]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
