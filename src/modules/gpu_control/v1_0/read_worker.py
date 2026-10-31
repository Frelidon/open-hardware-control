#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only LACT discovery outside the GUI; no tuning or ownership writes."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from modules.gpu_control.v1_0.client import LactClient, LactError
from modules.gpu_control.v1_0.ownership import coolercontrol_gpu_claim


def read_device(client, gpu_id: str, *, ownership_reader=coolercontrol_gpu_claim) -> dict:
    result = {"gpu_id": gpu_id, "stats": client.stats(gpu_id), "warnings": []}
    try:
        result["clocks"] = client.clocks(gpu_id)
    except LactError as exc:
        result["clocks"] = {}
        result["warnings"].append(f"GPU-LACT: Taktgrenzen nicht lesbar · {exc}")
    result["info"] = client.request("device_info", {"id": gpu_id})
    result["baseline"] = client.config(gpu_id)
    if gpu_id.split(":", 1)[0].casefold() == "10de":
        result["overdrive"] = True
    else:
        try:
            result["overdrive"] = client.overdrive_enabled()
        except LactError as exc:
            result["overdrive"] = None
            result["warnings"].append(f"GPU-LACT: Overdrive-Status nicht lesbar · {exc}")
    result["ownership"] = list(ownership_reader())
    return result


def main() -> int:
    try:
        request = json.loads(sys.stdin.readline(4096))
        if os.environ.get("OHC_DISABLE_HARDWARE_IO", "").casefold() in {"1", "true", "yes"}:
            raise LactError("Hardware I/O disabled")
        client = LactClient(Path(request["socket"]), timeout=1.5)
        kind = request["kind"]
        if kind == "ownership":
            data = {"ownership": list(coolercontrol_gpu_claim())}
        elif kind == "inventory":
            data = {"rows": client.devices()}
        elif kind == "device":
            data = read_device(client, str(request["gpu_id"]))
        elif kind == "metrics":
            data = {"gpu_id": str(request["gpu_id"]), "stats": client.stats(str(request["gpu_id"]))}
        else:
            raise ValueError("Unsupported read request")
        payload = {"ok": True, "data": data}
    except (LactError, OSError, ValueError, KeyError, TypeError) as exc:
        payload = {"ok": False, "error": str(exc)[:300]}
    print(json.dumps(payload, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
