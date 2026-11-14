#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small reusable actions for OHC's general and hardware log views."""

from __future__ import annotations

from pathlib import Path
import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QFileDialog, QPlainTextEdit, QTabWidget

from modules.runtime_logging.v1_0 import (
    RollingLogBuffer,
    is_error_log_message,
)
from modules.crash_recovery.v1_0 import append_crash_context
from privacy_logging import application_state_directory, append_error_event, redact_private_text


RGB_FAN_LOG_PREFIXES = (
    "ARGB:",
    "ARGB-DIAG:",
    "GPU-LACT:",
    "GPU-LACT-FEHLER:",
    "MAINBOARD-FAN:",
    "MAINBOARD-FAN-ASSISTENT:",
    "MAINBOARD-FAN-FEHLER:",
    "MAINBOARD-FAN-KALIBRIERUNG:",
    "MAINBOARD-FAN-LAYOUT:",
    "MAINBOARD-FAN-PROFIL:",
    "MAINBOARD-FAN-WATCHDOG:",
    "RGB-",
)


def is_rgb_fan_log_message(message: str) -> bool:
    """Select RGB, physical LED mapping and fan-control diagnostics."""
    normalized = str(message).lstrip().upper()
    if normalized.startswith(RGB_FAN_LOG_PREFIXES):
        return True
    # Replayed crash lines carry a short prefix before the original event.
    return any(f" {prefix}" in normalized for prefix in RGB_FAN_LOG_PREFIXES)


def build_log_category_tabs(host) -> QTabWidget:
    """Build bounded complete, RGB/fan and anomaly log surfaces."""
    host.log_view = QPlainTextEdit()
    host.rgb_fan_log_view = QPlainTextEdit()
    host.hardware_log_view = QPlainTextEdit()
    for view in (host.log_view, host.rgb_fan_log_view, host.hardware_log_view):
        view.setReadOnly(True)
        view.setMaximumBlockCount(30000)
    host.hardware_log_view.setPlaceholderText(
        "Keine auffälligen Hardwarewerte erkannt. Hier erscheinen nur Fehler, "
        "unplausible Werte und deren Ursache – keine sekündlichen Messreihen."
    )
    tabs = QTabWidget()
    tabs.addTab(host.log_view, host.tr_static("Gesamt"))
    tabs.addTab(host.rgb_fan_log_view, "RGB · " + host.tr_static("Lüfter"))
    tabs.addTab(host.hardware_log_view, "Hardware · Auffälligkeiten")
    tabs.currentChanged.connect(host._trim_log_to_character_limit)
    return tabs


class LogViewActionsMixin:
    def _ensure_log_buffers(self) -> None:
        if not hasattr(self, "_application_log_history"):
            self._application_log_history = RollingLogBuffer()
            self._rgb_fan_log_history = RollingLogBuffer()
            self._hardware_log_history = RollingLogBuffer()
            self._last_log_prune_at = 0.0

    def _start_log_retention_timer(self) -> None:
        if hasattr(self, "log_retention_timer"):
            return
        self.log_retention_timer = QTimer(self)
        self.log_retention_timer.setInterval(60_000)
        self.log_retention_timer.timeout.connect(self._trim_log_to_character_limit)
        self.log_retention_timer.start()
        self._trim_log_to_character_limit(force=True)

    def clear_application_log(self) -> None:
        self._ensure_log_buffers()
        active = self._active_log_view()
        if active is getattr(self, "hardware_log_view", None):
            self._hardware_log_history.clear()
        elif active is getattr(self, "rgb_fan_log_view", None):
            self._rgb_fan_log_history.clear()
        else:
            self._application_log_history.clear()
        active.clear()
        self._update_log_counter()
        self.log_message("LOG: Protokoll wurde geleert")

    def copy_application_log(self) -> None:
        self._trim_log_to_character_limit(force=True)
        QApplication.clipboard().setText(self._active_log_view().toPlainText())
        self.log_message("LOG: Protokoll wurde in die Zwischenablage kopiert")

    def save_application_log(self) -> None:
        self._trim_log_to_character_limit(force=True)
        active = self._active_log_view()
        suffix = (
            "-hardware" if active is getattr(self, "hardware_log_view", None)
            else "-rgb-fans" if active is getattr(self, "rgb_fan_log_view", None)
            else ""
        )
        default_name = Path.home() / f"open-hardware-control{suffix}-{time.strftime('%Y%m%d-%H%M%S')}.log"
        filename, _ = QFileDialog.getSaveFileName(
            self, "Open-Hardware-Control-Log speichern", str(default_name), "Logdateien (*.log *.txt)",
        )
        if not filename:
            self.log_message("LOG: Speichern abgebrochen")
            return
        try:
            Path(filename).write_text(self._active_log_view().toPlainText() + "\n", encoding="utf-8")
            self.log_message(f"LOG: Protokoll gespeichert als {Path(filename).name}")
        except OSError as exc:
            self.show_error(f"Log konnte nicht gespeichert werden:\n{exc}")

    def _active_log_view(self) -> QPlainTextEdit:
        tabs = getattr(self, "log_category_tabs", None)
        if tabs is not None:
            active = tabs.currentWidget()
            if isinstance(active, QPlainTextEdit):
                return active
        return self.log_view

    def _buffer_for_log_view(self, view: QPlainTextEdit) -> RollingLogBuffer:
        if view is getattr(self, "hardware_log_view", None):
            return self._hardware_log_history
        if view is getattr(self, "rgb_fan_log_view", None):
            return self._rgb_fan_log_history
        return self._application_log_history

    def _set_log_view_text(self, view: QPlainTextEdit, text: str) -> None:
        try:
            view.setPlainText(text)
            cursor = view.textCursor()
            cursor.setPosition(len(text))
            view.setTextCursor(cursor)
        except RuntimeError:
            return

    def _trim_log_to_character_limit(
        self,
        _tab_index: int | None = None,
        *,
        force: bool = False,
    ) -> None:
        self._ensure_log_buffers()
        now = time.monotonic()
        if not force and now - self._last_log_prune_at < 60.0:
            self._update_log_counter()
            return
        self._last_log_prune_at = now
        general_removed = self._application_log_history.prune(now)
        rgb_fan_removed = self._rgb_fan_log_history.prune(now)
        hardware_removed = self._hardware_log_history.prune(now)
        if hasattr(self, "log_view") and (force or general_removed):
            self._set_log_view_text(self.log_view, self._application_log_history.text())
        hardware = getattr(self, "hardware_log_view", None)
        if hardware is not None and (force or hardware_removed):
            self._set_log_view_text(hardware, self._hardware_log_history.text())
        rgb_fan = getattr(self, "rgb_fan_log_view", None)
        if rgb_fan is not None and (force or rgb_fan_removed):
            self._set_log_view_text(rgb_fan, self._rgb_fan_log_history.text())
        self._update_log_counter()

    def _update_log_counter(self) -> None:
        label = getattr(self, "log_counter_label", None)
        if label is None:
            return
        self._ensure_log_buffers()
        buffer = self._buffer_for_log_view(self._active_log_view())
        template = "Letzte 60 Minuten: {lines} Zeilen · {characters} Zeichen"
        translate = getattr(self, "tr_static", lambda source: source)
        label.setText(translate(template).format(
            lines=buffer.line_count,
            characters=buffer.character_count,
        ))

    def log_message(self, message: str, *, persist_error: bool = True) -> None:
        if not message:
            return
        stamp = time.strftime("%H:%M:%S")
        line = f"[{stamp}] {redact_private_text(message).rstrip()}"
        append_crash_context(
            application_state_directory() / "crash-context-current.jsonl", line,
        )
        now = time.monotonic()
        self._ensure_log_buffers()
        general_removed = self._application_log_history.append(
            line, now=now, prune_expired=False,
        )
        rgb_fan_message = is_rgb_fan_log_message(message)
        rgb_fan_removed = 0
        if rgb_fan_message:
            rgb_fan_removed = self._rgb_fan_log_history.append(
                line, now=now, prune_expired=False,
            )
        hardware_message = message.lstrip().startswith("HARDWARE:")
        hardware_removed = 0
        if hardware_message:
            hardware_removed = self._hardware_log_history.append(
                line, now=now, prune_expired=False,
            )
        log_view = getattr(self, "log_view", None)
        try:
            if log_view is not None:
                if general_removed:
                    self._set_log_view_text(log_view, self._application_log_history.text())
                else:
                    log_view.appendPlainText(line)
            if hardware_message:
                hardware_view = getattr(self, "hardware_log_view", None)
                if hardware_view is not None:
                    if hardware_removed:
                        self._set_log_view_text(hardware_view, self._hardware_log_history.text())
                    else:
                        hardware_view.appendPlainText(line)
            if rgb_fan_message:
                rgb_fan_view = getattr(self, "rgb_fan_log_view", None)
                if rgb_fan_view is not None:
                    if rgb_fan_removed:
                        self._set_log_view_text(rgb_fan_view, self._rgb_fan_log_history.text())
                    else:
                        rgb_fan_view.appendPlainText(line)
        except RuntimeError:
            pass
        if self.session_log_path is not None:
            try:
                with self.session_log_path.open("a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
            except OSError:
                self.session_log_path = None
        if persist_error and is_error_log_message(message):
            append_error_event(message, notify=False)
        self._trim_log_to_character_limit()

    def restore_previous_crash_context(self, lines: list[str], snapshot_path: Path) -> None:
        """Replay recovered lines without adding them to the new crash ring."""
        if not lines:
            return
        self._ensure_log_buffers()
        header = (
            f"ABSTURZDIAGNOSE: letzte fünf Minuten der vorherigen Sitzung · "
            f"Datei={snapshot_path.name}"
        )
        restored = [header, *(f"VORHERIGER ABSTURZ · {line}" for line in lines)]
        now = time.monotonic()
        for line in restored:
            self._application_log_history.append(line, now=now, prune_expired=False)
            if is_rgb_fan_log_message(line):
                self._rgb_fan_log_history.append(line, now=now, prune_expired=False)
            try:
                self.log_view.appendPlainText(line)
                rgb_fan_view = getattr(self, "rgb_fan_log_view", None)
                if rgb_fan_view is not None and is_rgb_fan_log_message(line):
                    rgb_fan_view.appendPlainText(line)
            except RuntimeError:
                pass
        if self.session_log_path is not None:
            try:
                with self.session_log_path.open("a", encoding="utf-8") as handle:
                    handle.write("\n".join(restored) + "\n")
            except OSError:
                self.session_log_path = None
        self._trim_log_to_character_limit(force=True)
