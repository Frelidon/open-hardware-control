# SPDX-License-Identifier: GPL-3.0-or-later
"""One-shot LACT Overdrive setup outside the OHC GUI process."""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from modules.gpu_control.v1_0.client import LactClient, LactError  # noqa: E402


def main() -> int:
    try:
        LactClient(timeout=240.0).prepare_overdrive()
    except LactError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)[:300]}, ensure_ascii=False), flush=True)
        return 1
    print(json.dumps({"ok": True}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
