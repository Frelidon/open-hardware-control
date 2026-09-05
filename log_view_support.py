#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small reusable actions for OHC's general and hardware log views."""

from __future__ import annotations

from pathlib import Path
import time

from PySide6.QtWidgets import QApplication, QFileDialog, QPlainTextEdit

from privacy_logging import redact_private_text


class LogViewActionsMixin:
    def clear_application_log(self) -> None:
        self._active_log_view().clear()
        self._trim_log_to_character_limit()
        self.log_message("LOG: Protokoll wurde geleert")

    def copy_application_log(self) -> None:
        QApplication.clipboard().setText(self._active_log_view().toPlainText())
        self.log_message("LOG: Protokoll wurde in die Zwischenablage kopiert")

    def save_application_log(self) -> None:
        suffix = "-hardware" if self._active_log_view() is getattr(self, "hardware_log_view", None) else ""
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
        hardware = getattr(self, "hardware_log_view", None)
        if tabs is not None and tabs.currentIndex() == 1 and hardware is not None:
            return hardware
        return self.log_view

    def _trim_log_to_character_limit(self) -> None:
        if not hasattr(self, "log_view"):
            return
        try:
            limit = int(getattr(self, "log_char_limit", 10000))
            views = [self.log_view]
            hardware = getattr(self, "hardware_log_view", None)
            if hardware is not None:
                views.append(hardware)
            for view in views:
                text = view.toPlainText()
                if len(text) <= limit:
                    continue
                lines = text.splitlines()
                while lines and len("\n".join(lines)) > limit:
                    lines.pop(0)
                view.setPlainText("\n".join(lines))
                cursor = view.textCursor()
                cursor.setPosition(len(view.toPlainText()))
                view.setTextCursor(cursor)
            if hasattr(self, "log_counter_label"):
                count = len(self._active_log_view().toPlainText())
                self.log_counter_label.setText(
                    f"Log: {count:,} / {limit:,} Zeichen".replace(",", ".")
                )
        except RuntimeError:
            return

    def log_message(self, message: str) -> None:
        if not message:
            return
        stamp = time.strftime("%H:%M:%S")
        line = f"[{stamp}] {redact_private_text(message).rstrip()}"
        log_view = getattr(self, "log_view", None)
        try:
            if log_view is not None:
                log_view.appendPlainText(line)
            if message.lstrip().startswith("HARDWARE:"):
                hardware_view = getattr(self, "hardware_log_view", None)
                if hardware_view is not None:
                    hardware_view.appendPlainText(line)
        except RuntimeError:
            pass
        if self.session_log_path is not None:
            try:
                with self.session_log_path.open("a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
            except OSError:
                self.session_log_path = None
        self._trim_log_to_character_limit()
