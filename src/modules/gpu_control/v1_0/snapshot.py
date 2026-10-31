# SPDX-License-Identifier: GPL-3.0-or-later
"""Remember the pre-tuning LACT configuration for explicit later release."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any


def snapshot_key(gpu_id: str) -> str:
    return "gpu_control/snapshot/" + sha256(gpu_id.encode("utf-8")).hexdigest()


def read_snapshot(settings: Any, gpu_id: str) -> dict[str, Any] | None:
    try:
        record = json.loads(str(settings.value(snapshot_key(gpu_id), "")))
    except (TypeError, ValueError):
        return None
    if (isinstance(record, dict) and record.get("gpu_id") == gpu_id
            and isinstance(record.get("original"), dict)
            and isinstance(record.get("saved"), dict)):
        return record
    return None


def write_snapshot(settings: Any, gpu_id: str, original: dict[str, Any],
                   saved: dict[str, Any]) -> None:
    record = {"gpu_id": gpu_id, "original": original, "saved": saved}
    settings.setValue(snapshot_key(gpu_id), json.dumps(record, sort_keys=True))
    settings.sync()


def forget_snapshot(settings: Any, gpu_id: str) -> None:
    settings.remove(snapshot_key(gpu_id))
    settings.sync()
