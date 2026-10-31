#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit CSV/JSON export for selected in-memory temperature samples."""

from __future__ import annotations

import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Mapping

from .model import TemperatureHistoryBuffer


def temperature_report_rows(
    history: TemperatureHistoryBuffer,
    start: float,
    end: float,
    keys: set[str],
    catalog: Mapping[str, tuple[str, str, str]],
) -> list[dict[str, object]]:
    selected = {str(key) for key in keys if key in catalog}
    rows: list[dict[str, object]] = []
    for sample in history.between(start, end):
        local_time = datetime.fromtimestamp(sample.timestamp).astimezone()
        for key in sorted(selected):
            if key not in sample.values:
                continue
            label, group, source = catalog[key]
            rows.append({
                "date": local_time.strftime("%Y-%m-%d"),
                "time": local_time.strftime("%H:%M:%S"),
                "timestamp_local": local_time.isoformat(timespec="seconds"),
                "sensor_key": key,
                "sensor": label,
                "group": group,
                "source": source,
                "value_c": round(sample.values[key], 3),
            })
    return rows


def write_temperature_report(path: Path, rows: list[dict[str, object]], file_format: str) -> Path:
    target = path.expanduser().resolve()
    mode = str(file_format).casefold()
    if mode not in {"csv", "json"}:
        raise ValueError("Unsupported report format")
    expected = f".{mode}"
    if target.suffix.casefold() != expected:
        target = target.with_suffix(expected)
    if mode == "json":
        target.write_text(
            json.dumps({"schema": 1, "readings": rows}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        fields = ("date", "time", "timestamp_local", "sensor_key", "sensor", "group", "source", "value_c")
        with target.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    return target
