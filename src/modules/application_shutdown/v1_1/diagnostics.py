# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, read-only interpretation of the private shutdown journal."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Iterable, Mapping

from privacy_logging import application_state_directory


@dataclass(frozen=True)
class ShutdownReport:
    """Machine-readable result; user-facing text stays in the localization layer."""

    status: str = "unknown"
    pid: int | None = None
    phase: str = ""
    reason: str = ""


def _record_pid(record: Mapping[str, object]) -> int | None:
    value = record.get("parent_pid") if record.get("event") in {
        "parent-gone", "parent-still-alive"
    } else record.get("pid")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def classify_records(records: Iterable[Mapping[str, object]]) -> ShutdownReport:
    """Classify the latest close/exit attempt without inferring hardware success."""
    rows = [record for record in records if isinstance(record, Mapping)]
    attempts = [
        (index, record)
        for index, record in enumerate(rows)
        if record.get("event") in {"app-start", "window-close", "exit-request"}
    ]
    if not attempts:
        return ShutdownReport()

    start_index, attempt = attempts[-1]
    pid = _record_pid(attempt)
    related = [
        record for record in rows[start_index:]
        if pid is not None and _record_pid(record) == pid
    ]
    event = str(attempt.get("event") or "")
    events = [str(record.get("event") or "") for record in related]
    failures = [
        record for record in related
        if record.get("event") == "phase-failed"
    ]
    failed_reason = ""
    if failures:
        latest = failures[-1]
        failed_reason = f"{str(latest.get('phase') or 'unknown')}: {str(latest.get('error') or 'failed')}"

    if event == "app-start" and "exit-request" not in events:
        if "parent-gone" in events:
            return ShutdownReport("unexpected-exit", pid, reason="No orderly exit request")
        if pid is not None and pid != os.getpid():
            from .watcher import identity
            current = identity(pid)
            expected = str(attempt.get("starttime") or "")
            if current is None or current[1] == "Z" or (expected and current[0] != expected):
                return ShutdownReport("unexpected-exit", pid, reason="Process ended before cleanup")
        return ShutdownReport("running", pid)

    if event == "window-close":
        choices = [
            str(record.get("decision") or "")
            for record in related
            if record.get("event") == "window-close-choice"
        ]
        decision = choices[-1] if choices else ""
        if decision == "cancel":
            return ShutdownReport("cancelled", pid)
        if decision in {"tray", "automatic-tray"} or (
            not decision
            and bool(attempt.get("close_to_tray"))
            and not bool(attempt.get("explicit"))
        ):
            return ShutdownReport("continued-in-tray", pid)
        if decision == "minimized":
            return (ShutdownReport("unexpected-exit", pid, reason="Process ended after window minimize")
                    if "parent-gone" in events else ShutdownReport("running", pid))
        if "exit-request" not in events:
            return ShutdownReport("incomplete", pid, reason="Window closed without exit request")

    active_phases: list[str] = []
    for record in related:
        record_event = str(record.get("event") or "")
        phase = str(record.get("phase") or "")
        if record_event == "phase-start" and phase:
            active_phases.append(phase)
        elif record_event in {"phase-done", "phase-failed"} and phase:
            active_phases = [item for item in active_phases if item != phase]

    if "qt-loop-returned" in events:
        if failed_reason:
            return ShutdownReport("cleanup-failed", pid, reason=failed_reason)
        return ShutdownReport("clean", pid)
    if "parent-gone" in events:
        return ShutdownReport("ended-without-qt-confirmation", pid, active_phases[-1] if active_phases else "", failed_reason or "Qt event loop did not return")
    if "parent-still-alive" in events:
        return ShutdownReport("stuck", pid, active_phases[-1] if active_phases else "", failed_reason or "Parent still alive")
    return ShutdownReport("incomplete", pid, active_phases[-1] if active_phases else "", failed_reason or "No process exit confirmation")


def _read_records(path: Path, limit: int = 256 * 1024) -> list[dict[str, object]]:
    if path.is_symlink():
        return []
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as stream:
            size = os.fstat(stream.fileno()).st_size
            if size > limit:
                stream.seek(-limit, os.SEEK_END)
                stream.readline()
            payload = stream.read(limit)
    except OSError:
        return []
    records: list[dict[str, object]] = []
    for line in payload.decode("utf-8", errors="replace").splitlines():
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def latest_shutdown_report(path: Path | None = None) -> ShutdownReport:
    journal = path or application_state_directory() / "shutdown.jsonl"
    return classify_records(_read_records(journal))


def has_confirmed_tray_choice(path: Path | None = None) -> bool:
    """Return true only after the user explicitly chose tray continuation."""
    journal = path or application_state_directory() / "shutdown.jsonl"
    return any(
        record.get("event") == "window-close-choice"
        and record.get("decision") == "tray"
        for record in _read_records(journal)
    )
