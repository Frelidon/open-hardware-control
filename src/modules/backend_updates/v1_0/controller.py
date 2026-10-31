#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qt presentation for the read-only backend release audit."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton
from shiboken6 import isValid
from modules.platform_support.v1_0 import helper_command

SUMMARY_PENDING = "Noch nicht geprüft. Die Prüfung liest nur lokale Versionen und die offiziellen stabilen Release-Metadaten."
AUDIT_NOTE = (
    "OHC installiert dabei nichts. OpenLinkHub und das KDE-Wallpaper-Plugin verwenden ihre eigenen bestätigten OHC-Updater; "
    "alle anderen Backends bleiben bei der eingerichteten Paketverwaltung. Es werden keine fremden Paketquellen hinzugefügt."
)


class BackendUpdatesMixin:
    @staticmethod
    def backend_updates_helper_path() -> Path:
        return Path(__file__).resolve().parent / "check.py"

    def populate_backend_update_box(self, layout: QGridLayout) -> None:
        self.backend_update_rows: list[tuple[QLabel, QPushButton]] = []
        self.backend_update_components: list[dict] = []
        self.backend_update_summary = QLabel()
        self.backend_update_summary.setWordWrap(True)
        layout.addWidget(self.backend_update_summary, 0, 0, 1, 3)
        self.backend_update_check_button = QPushButton("Alle Backend-Versionen prüfen")
        self.backend_update_check_button.clicked.connect(self.check_backend_updates)
        layout.addWidget(self.backend_update_check_button, 1, 0)
        note = self.backend_update_note = QLabel()
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note, 2, 0, 1, 3)
        layout.setColumnStretch(1, 1)
        self._set_backend_update_summary(SUMMARY_PENDING)
        self.refresh_backend_update_language()

    def _set_backend_update_summary(self, source: str, **values) -> None:
        self.backend_update_summary_source = source
        self.backend_update_summary_values = values
        self.backend_update_summary.setText(self.tr_static(source).format(**values))

    def refresh_backend_update_language(self) -> None:
        if not hasattr(self, "backend_update_summary"):
            return
        self.backend_update_check_button.setText(self.tr_static("Alle Backend-Versionen prüfen"))
        self.backend_update_note.setText(self.tr_static(AUDIT_NOTE))
        self._set_backend_update_summary(
            self.backend_update_summary_source, **self.backend_update_summary_values
        )
        for item, (label, button) in zip(self.backend_update_components, self.backend_update_rows):
            name = escape(str(item.get("name") or "Backend"))
            installed = self.tr_static(str(item.get("installed") or "nicht erkannt"))
            latest = self.tr_static(str(item.get("latest") or "nicht erkannt"))
            if item.get("missing"):
                state = self.tr_static("nicht installiert")
            elif item.get("latest") == "Prüfung fehlgeschlagen":
                state = self.tr_static("Online-Prüfung fehlgeschlagen")
            elif not item.get("version_known", True):
                state = self.tr_static("Version nicht vergleichbar")
            elif item.get("update_available"):
                state = self.tr_static("Update verfügbar · Weg: {route}").format(
                    route=self.tr_static(str(item.get("route") or "Paketverwaltung"))
                )
            else:
                state = self.tr_static("aktuell")
            label.setText(self.tr_static(
                "<b>{name}</b> · installiert: {installed} · offiziell stabil: {latest}<br>{state}"
            ).format(name=name, installed=escape(installed), latest=escape(latest), state=escape(state)))
            button.setText(self.tr_static("Offizielle Releases"))

    def check_backend_updates(self) -> None:
        self.backend_update_check_button.setEnabled(False)
        self._set_backend_update_summary("Offizielle stabile Backend-Versionen werden geprüft …")
        for label, button in self.backend_update_rows:
            label.deleteLater()
            button.deleteLater()
        self.backend_update_rows.clear()
        self.backend_update_components.clear()

        def done(result) -> None:
            if not isValid(self) or getattr(self, "exit_cleanup_in_progress", False):
                return
            self.backend_update_check_button.setEnabled(True)
            try:
                payload = json.loads(result.stdout)
                components = payload.get("components")
                if not result.ok or not payload.get("ok") or not isinstance(components, list):
                    raise ValueError(str(payload.get("error") or result.combined or self.tr_static("Versionsprüfung fehlgeschlagen")))
            except (json.JSONDecodeError, ValueError) as exc:
                self._set_backend_update_summary("Backend-Versionen konnten nicht vollständig geprüft werden: {error}", error=exc)
                self.log_message(f"BACKEND-UPDATE: Prüfung fehlgeschlagen · {exc}")
                return

            available = sum(1 for item in components if isinstance(item, dict) and item.get("update_available"))
            errors = payload.get("errors")
            source_count = len(errors) if isinstance(errors, list) else 0
            self._set_backend_update_summary(
                "Prüfung abgeschlossen · {updates} Aktualisierung(en) gegenüber dem offiziellen stabilen Stand erkannt · {sources} Quelle(n) nicht erreichbar.",
                updates=available, sources=source_count,
            )
            grid = self.backend_update_summary.parentWidget().layout()
            first_row = 3
            for offset, item in enumerate(components):
                if not isinstance(item, dict):
                    continue
                label = QLabel()
                label.setWordWrap(True)
                button = QPushButton("Offizielle Releases")
                url = str(item.get("release_url") or "")
                button.setEnabled(url.startswith("https://"))
                button.clicked.connect(lambda _checked=False, target=url: QDesktopServices.openUrl(QUrl(target)))
                grid.addWidget(label, first_row + offset, 0, 1, 2)
                grid.addWidget(button, first_row + offset, 2)
                self.backend_update_rows.append((label, button))
                self.backend_update_components.append(item)
                self.log_message(
                    f"BACKEND-UPDATE: {item.get('name')} · installiert={item.get('installed')} · stabil={item.get('latest')} · update={item.get('update_available')}"
                )
            self.refresh_backend_update_language()

        program, arguments = helper_command(self.backend_updates_helper_path())
        self.backend.run_async(
            [program, *arguments], callback=done, timeout=60, log_output=False,
        )
