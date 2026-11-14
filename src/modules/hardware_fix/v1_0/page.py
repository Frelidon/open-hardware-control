#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Two primary actions for local, model-specific Hardware Fix setup."""
from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Callable
import uuid

from PySide6.QtCore import QEvent, QProcess, QTimer, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMenu, QMessageBox, QPushButton,
    QScrollArea, QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)
from modules.ui_performance.v1_1.compact_panels import Disclosure
from modules.ui_themes.v1_0.registry import resolve_theme
from privacy_logging import redact_private_text
from .profile import STATE_ROOT, terminal_spec
from .status import HardwareFixStatus, inspect_status


class HardwareFixPanel(QScrollArea):
    def __init__(self, host: QWidget, translate: Callable[[str], str]) -> None:
        super().__init__(host)
        self.host, self.translate = host, translate
        self.last_status: HardwareFixStatus | None = None
        self._texts = []
        self._job_id = ""
        self._started_at = 0.0
        self._busy = False
        self.result_timer = QTimer(self)
        self.result_timer.setInterval(1200)
        self.result_timer.timeout.connect(self._poll_result)
        self._build()
        QTimer.singleShot(0, self, self.refresh_status)

    def tr(self, text: str) -> str:
        return self.translate(text)

    def _text(self, widget, source):
        self._texts.append((widget, source))
        widget.setText(source)
        return widget

    def _label(self, text):
        label = self._text(QLabel(), text)
        label.setWordWrap(True)
        label.setMinimumWidth(0)
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        label.setTextFormat(Qt.TextFormat.PlainText)
        return label

    def _build(self):
        self.setWidgetResizable(True)
        self.viewport().setAutoFillBackground(False)
        body = QWidget()
        body.setAutoFillBackground(False)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(14)
        hero = QFrame(objectName="moduleHeroCard")
        hero_layout = QVBoxLayout(hero)
        title = self._label("Hardware Fix")
        title.setObjectName("heroTitle")
        hero_layout.addWidget(title)
        hero_layout.addWidget(self._label("Gezielte, rücknehmbare Korrekturen für exakt erkannte Hardware. Keine Firmware wird in das Gerät geflasht."))
        layout.addWidget(hero)

        card = QFrame(objectName="settingsCard")
        content = QVBoxLayout(card)
        content.setContentsMargins(20, 18, 20, 18)
        content.setSpacing(14)
        model = self._label("Unterstützter Monitor: MSI MAG 274QPF X30MV")
        model.setObjectName("sectionTitle")
        content.addWidget(model)
        status_row = QHBoxLayout()
        self.summary = self._label("")
        self.summary.setText(self.tr("Status wird geprüft …"))
        self.summary.setObjectName("infoText")
        status_row.addWidget(self.summary, 1)
        self.status_button = QToolButton()
        self.status_button.setText("↻")
        self.status_button.setAccessibleName(self.tr("Status prüfen"))
        self.status_button.setToolTip(self.tr("Status prüfen"))
        self.status_button.clicked.connect(self.refresh_status)
        status_row.addWidget(self.status_button)
        content.addLayout(status_row)
        content.addWidget(self._label("Lokale Installation · empfohlen"))
        content.addWidget(self._label("Der Fix läuft unabhängig von Open Hardware Control. Installieren richtet die benötigten Schritte ein oder aktualisiert den vorhandenen lokalen Dienst."))
        content.addWidget(self._label("Fix: korrigierte VRR-Kennung in einer anonymisierten EDID für DisplayPort. Die persönliche Monitor-Seriennummer ist nicht enthalten. HDMI bleibt unverändert."))
        warning = self._label("Achtung: Das Profil weist die MSI-EDID allen DisplayPort-Anschlüssen zu. Andere, gleichzeitig angeschlossene DP-Monitore vorher trennen oder die Aktion abbrechen.")
        warning.setObjectName("warningText")
        self.warning = warning
        content.addWidget(warning)
        self.next_step = self._label("")
        content.addWidget(self.next_step)
        buttons = QHBoxLayout()
        self.activate_button = self._text(QPushButton(), "Installieren")
        self.activate_button.setObjectName("primaryAction")
        self.activate_button.setMinimumHeight(40)
        self.activate_button.clicked.connect(lambda: self._start_action("install-local"))
        self.uninstall_button = self._text(QPushButton(), "Deinstallieren")
        self.uninstall_button.setMinimumHeight(40)
        self.uninstall_button.clicked.connect(lambda: self._start_action("uninstall"))
        buttons.addWidget(self.activate_button)
        buttons.addWidget(self.uninstall_button)
        buttons.addStretch()
        content.addLayout(buttons)
        layout.addWidget(card)

        self.options_button = self._text(QToolButton(), "Weitere Optionen")
        self.options_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self.options_button)
        self.option_actions = {}
        for action, label in (
            ("game-test", "VRR im Spiel testen"),
            ("status", "Ausführliche Diagnose"),
            ("desktop", "Desktop-VRR einrichten"),
            ("automation-install", "Ubuntu-Automatik reparieren"),
            ("automation-remove", "Nur die Ubuntu-Automatik entfernen"),
            ("install", "Boot-Fix erneut installieren"),
        ):
            item = menu.addAction(label)
            self._texts.append((item, label))
            item.triggered.connect(lambda checked=False, key=action: self._start_action(key))
            self.option_actions[action] = item
        menu.addSeparator()
        item = menu.addAction("Protokoll anzeigen")
        self._texts.append((item, "Protokoll anzeigen"))
        item.triggered.connect(self.show_log)
        self.options_button.setMenu(menu)
        layout.addWidget(self.options_button, 0, Qt.AlignmentFlag.AlignLeft)
        self.details = self._label("")
        self.details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.technical = Disclosure("Technischer Status", self.details)
        self._texts.append((self.technical.button, "Technischer Status"))
        layout.addWidget(self.technical)
        layout.addStretch()
        self.setWidget(body)
        body.setAutoFillBackground(False)
        self._refresh_warning()

    def _refresh_warning(self):
        palette = QApplication.palette()
        theme = resolve_theme(getattr(self.host, "theme_mode", "system"),
                              getattr(self.host, "system_palette", palette), QColor("#00aaff"))
        warning_color = "#e9b748" if theme.dark else "#875900"
        self.warning.setStyleSheet(f"QLabel#warningText {{ color: {warning_color}; }}")

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in {QEvent.Type.PaletteChange, QEvent.Type.StyleChange} and hasattr(self, "host") and self.widget():
            self._refresh_warning()

    def refresh_status(self):
        try:
            status = inspect_status()
        except Exception:
            self.summary.setText(self.tr("Statusprüfung fehlgeschlagen. Diagnose und Protokoll öffnen."))
            self.activate_button.setEnabled(False)
            self.uninstall_button.setEnabled(False)
            return
        self.last_status = status
        supported = status.os_family in {"ubuntu", "fedora"} and status.resources_valid
        installed = status.boot_configuration_present or status.firmware_present or status.automation_installed
        self.activate_button.setEnabled(not self._busy and supported and bool(status.monitor_connectors))
        self.uninstall_button.setEnabled(not self._busy and supported and installed)
        for action, item in self.option_actions.items():
            allowed = supported
            if action.startswith("automation") or action == "desktop":
                allowed = allowed and status.os_family == "ubuntu"
            if action in {"desktop", "game-test"}:
                allowed = allowed and status.corrected_edid_loaded
            if action == "automation-remove":
                allowed = allowed and status.automation_installed
            item.setEnabled(not self._busy and allowed)
        if not self._busy:
            self.summary.setText(self.tr("Lokal installiert") if installed else self.tr("Noch nicht installiert"))
        if not status.resources_valid:
            next_step = "Profilressourcen sind beschädigt. Open Hardware Control erneut installieren."
        elif not status.monitor_connectors:
            next_step = "MSI-Monitor über DisplayPort anschließen."
        elif status.reboot_required:
            next_step = "Neustart erforderlich. Danach mit Installieren die Einrichtung abschließen."
        elif status.os_family not in {"ubuntu", "fedora"}:
            next_step = "Dieser Fix unterstützt Ubuntu und Fedora."
        elif installed:
            next_step = "Installieren prüft und aktualisiert die Einrichtung. Deinstallieren entfernt den Fix einschließlich der Ubuntu-Automatik."
        else:
            next_step = "Mit Installieren beginnen. Eine nötige Administratorabfrage öffnet sich im Terminal."
        self.next_step.setText(self.tr(next_step))
        yes = lambda value: self.tr("ja") if value else self.tr("nein")
        self.details.setText("\n".join((
            self.tr("System: {system}").format(system=status.os_family),
            self.tr("Monitor: {monitor}").format(monitor=", ".join(status.monitor_connectors) or self.tr("nicht erkannt")),
            self.tr("Korrigierte EDID geladen: {value}").format(value=yes(status.corrected_edid_loaded)),
            self.tr("Boot-Fix gespeichert: {value}").format(value=yes(status.boot_configuration_present and status.firmware_valid)),
            self.tr("Ubuntu-Automatik installiert / aktiv: {installed} / {active}").format(installed=yes(status.automation_installed), active=yes(status.automation_active)),
        )))

    def _start_action(self, action):
        if self._busy:
            return
        status = self.last_status or inspect_status()
        if action.startswith("automation") and status.os_family != "ubuntu":
            return
        if action not in {"status", "game-test"}:
            body = ("Alle Spiele vorher beenden. Der lokale Dienst und die eindeutig zu diesem Profil gehörenden Bootdateien werden entfernt. Ein nötiger Neustart erfolgt nicht automatisch."
                    if action == "uninstall" else
                    "Der Fix wird lokal eingerichtet. Ubuntu/GNOME erhält zusätzlich Desktop-VRR und die Spielautomatik. Andere DP-Monitore vorher trennen. Ein nötiger Neustart erfolgt nicht automatisch."
                    if action == "install-local" else
                    "Dieser einzelne Reparaturschritt verändert die vorhandene Einrichtung. Vor dem Entfernen der Automatik alle Spiele beenden.")
            if QMessageBox.question(self, "Hardware Fix", self.tr(body),
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
        job_id = uuid.uuid4().hex
        spec = terminal_spec(action, job_id)
        started = QProcess.startDetached(spec[0], spec[1]) if spec else False
        if not (started[0] if isinstance(started, tuple) else bool(started)):
            QMessageBox.warning(self, "Hardware Fix", self.tr("Terminal konnte nicht geöffnet werden. Ein unterstütztes Terminal und Python 3 werden benötigt."))
            return
        self._job_id, self._started_at, self._busy = job_id, time.monotonic(), True
        self.refresh_status()
        self.summary.setText(self.tr("Hardware-Fix-Aktion läuft im Terminal …"))
        self.result_timer.start()

    def _poll_result(self):
        try:
            payload = json.loads((STATE_ROOT / "last-result.json").read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            payload = {}
        if not isinstance(payload, dict) or payload.get("job_id") != self._job_id:
            if time.monotonic() - self._started_at > 30:
                self._finish(False, missing=True)
            return
        if payload.get("finished") is True:
            self._finish(payload.get("success") is True)
        elif time.monotonic() - self._started_at > 1800:
            self._finish(False, missing=True)

    def _finish(self, success, *, missing=False):
        self.result_timer.stop()
        self._busy = False
        self.refresh_status()
        if not success:
            text = ("Kein Ergebnis vom Terminal erhalten. Terminal und Protokoll prüfen."
                    if missing else "Die Aktion wurde nicht erfolgreich abgeschlossen. Details stehen im Protokoll.")
            QMessageBox.warning(self, "Hardware Fix", self.tr(text))

    def show_log(self):
        try:
            payload = json.loads((STATE_ROOT / "last-result.json").read_text(encoding="utf-8"))
            job = payload.get("job_id", "")
            if not isinstance(job, str) or len(job) != 32 or any(char not in "0123456789abcdef" for char in job):
                raise ValueError("Invalid job")
            path = STATE_ROOT / (job + ".log")
            if path.is_symlink():
                raise ValueError("Unexpected link")
            with path.open("rb") as stream:
                stream.seek(0, 2)
                stream.seek(max(0, stream.tell() - 20_000))
                text = redact_private_text(stream.read(20_000).decode("utf-8", errors="replace"))
        except (OSError, ValueError, TypeError, AttributeError):
            text = self.tr("Noch kein Hardware-Fix-Protokoll vorhanden.")
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Hardware Fix")
        dialog.setTextFormat(Qt.TextFormat.PlainText)
        dialog.setText(text)
        dialog.exec()

    def refresh_language(self):
        for widget, source in self._texts:
            widget.setText(self.tr(source))
        self.status_button.setAccessibleName(self.tr("Status prüfen"))
        self.status_button.setToolTip(self.tr("Status prüfen"))
        self.refresh_status()
        if self._busy:
            self.summary.setText(self.tr("Hardware-Fix-Aktion läuft im Terminal …"))
