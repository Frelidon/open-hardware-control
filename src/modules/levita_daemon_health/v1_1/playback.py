# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure parsing and bounded decisions for TRCC playback supervision."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PlaybackHealth:
    healthy: bool
    reason: str
    theme: str = ""
    failure_kind: str = ""


def recent_trcc_cause(
    log_file: Path,
    *,
    since_epoch: float = 0.0,
    max_bytes: int = 512_000,
) -> str:
    """Classify the retained TRCC tail without copying private log contents.

    TRCC can rotate a busy 15-FPS debug log within roughly one minute.  Reading
    only a bounded tail at the instant OHC notices missing playback preserves a
    useful cause category while paths, theme names and command arguments stay
    out of OHC's public protocol log.
    """

    try:
        with log_file.open("rb") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            handle.seek(max(0, size - max(4_096, min(2_000_000, int(max_bytes)))))
            decoded = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return "TRCC-Log nicht lesbar"
    lines: list[str] = []
    for line in decoded.splitlines():
        if since_epoch > 0 and len(line) >= 19:
            try:
                timestamp = datetime.strptime(line[:19], "%Y-%m-%dT%H:%M:%S").timestamp()
            except ValueError:
                timestamp = since_epoch
            if timestamp + 1 < since_epoch:
                continue
        lines.append(line.casefold())
    tail = "\n".join(lines)
    categories: list[str] = []
    rules = (
        (("autodisconnect", "auto-disconnect", "consecutive disconnect"), "USB-Schreibfehlergrenze erreicht"),
        (("devicedetached", "_on_device_detached"), "USB-Geräteabmeldung erkannt"),
        (("disconnectdevice: key=",), "expliziter TRCC-Disconnect erkannt"),
        (("unload: dropped",), "TRCC-Wiedergabeobjekt wurde entfernt"),
        (("send failed", "transporterror", "write returned false"), "USB-Sendefehler erkannt"),
        (("close: devices=", "ipc server shut down"), "TRCC-Daemon wurde beendet"),
    )
    for markers, label in rules:
        if any(marker in tail for marker in markers):
            categories.append(label)
    return " · ".join(categories) if categories else "keine passende Ursache im erhaltenen TRCC-Logausschnitt"


def parse_playback_status(output: str, device_key: str) -> PlaybackHealth:
    raw = str(output).strip()
    # A backend warning may surround the JSON on stderr.  Only the bounded
    # outer object is considered; arbitrary text is never evaluated.
    if not raw.startswith("{") or not raw.endswith("}"):
        start, end = raw.find("{"), raw.rfind("}")
        raw = raw[start:end + 1] if 0 <= start < end else raw
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return PlaybackHealth(False, "TRCC-Status war nicht lesbar", failure_kind="unreadable")
    devices = payload.get("lcd_devices") if isinstance(payload, dict) else None
    if not isinstance(devices, list):
        return PlaybackHealth(False, "TRCC meldet keinen LCD-Gerätestatus", failure_kind="unreadable")
    device = next((item for item in devices if isinstance(item, dict) and item.get("key") == device_key), None)
    if device is None:
        return PlaybackHealth(False, f"Not attached: {device_key}", failure_kind="detached")
    theme = str(device.get("current_theme") or "").strip()
    if not theme:
        return PlaybackHealth(False, "TRCC meldet keine aktive Wiedergabe", failure_kind="missing-playback")
    return PlaybackHealth(True, "Wiedergabe bestätigt", theme)


def parse_video_playback_status(output: str, device_key: str) -> PlaybackHealth:
    """Parse TRCC's read-only ``display video-status`` answer.

    Unlike the persisted ``current_theme`` value, this query reflects the
    daemon's live in-memory playback object.  It therefore detects the exact
    disconnect/black-screen case where the selected theme name survives but
    the VideoLoop has stopped.
    """

    raw = str(output)[-4096:].casefold()
    if "playing frame " in raw and "(paused)" not in raw:
        return PlaybackHealth(True, "VideoLoop-Wiedergabe bestätigt")
    if "(paused)" in raw:
        return PlaybackHealth(False, f"TRCC-Video für {device_key} ist pausiert", failure_kind="paused")
    if "no playback loaded" in raw or "no video playing" in raw:
        return PlaybackHealth(
            False,
            f"TRCC hat das geladene Video für {device_key} verloren",
            failure_kind="missing-playback",
        )
    if "not attached" in raw or "no device attached" in raw:
        return PlaybackHealth(False, f"Not attached: {device_key}", failure_kind="detached")
    return PlaybackHealth(False, "TRCC-VideoStatus war nicht lesbar", failure_kind="unreadable")


@dataclass(slots=True)
class PlaybackRecoveryPolicy:
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3
    successes_to_reset_attempts: int = 5

    def observe(self, health: PlaybackHealth) -> bool:
        if health.healthy:
            self.consecutive_failures = 0
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.successes_to_reset_attempts:
                self.recovery_attempts = 0
            return False
        self.consecutive_successes = 0
        self.consecutive_failures += 1
        if self.consecutive_failures < 2 or self.recovery_attempts >= self.max_recovery_attempts:
            return False
        self.consecutive_failures = 0
        self.recovery_attempts += 1
        return True

    def defer_recovery(self) -> None:
        """Return an unstarted recovery to the bounded retry budget."""

        if self.recovery_attempts > 0:
            self.recovery_attempts -= 1
        # One confirmed failure remains, so the next probe can retry without
        # waiting for two entirely new failures.
        self.consecutive_failures = 1
