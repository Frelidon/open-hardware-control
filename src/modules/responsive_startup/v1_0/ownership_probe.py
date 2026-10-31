#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small subprocess entry point for the blocking ownership inspection."""

from __future__ import annotations

import json
from pathlib import Path
import sys

SOURCE_ROOT = Path(__file__).resolve().parents[3]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from cooling_ownership import detect_cooling_owner


def main() -> int:
    status = detect_cooling_owner()
    print(json.dumps({
        "service_active": status.coolercontrol_service_active,
        "process_active": status.coolercontrol_process_active,
        "service_enabled": status.coolercontrol_service_enabled,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
