#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware Fix profile UI embedded below Hardware Checker."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QProcess, QTimer
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from .profile import MSI_VRR_PROFILE, STATE_ROOT, os_family, terminal_spec
from .status import HardwareFixStatus, inspect_status


class HardwareFixPanel(QScrollArea):
    """Model-specific fixes; every mutating action is fixed and confirmed."""

    def __init__(self, host: QWidget, translate: Callable[[str], str]) -> None:
        super().__init__(host)
        self.host = host
        self.translate = translate
        self.last_status: HardwareFixStatus | None = None
        self.result_timer = QTimer(self)
        self.result_timer.setInterval(1200)
        self.result_timer.timeout.connect(self._poll_result)
        self._last_job_id = ""
        self._build()
        QTimer.singleShot(0, self, self.refresh_status)

    def tr(self, text: str) -> str:
        return self.translate(text)

    def _build(self) -> None:
        self.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        hero = QFrame(objectName="moduleHeroCard")
        hero_layout = QVBoxLayout(hero)
        title = QLabel("Hardware Fix")
        title.setObjectName("heroTitle")
        intro = QLabel(
            "Gezielte, rücknehmbare Korrekturen für exakt erkannte Hardware. "
            "Keine Firmware wird in das Gerät geflasht."
        )
        intro.setWordWrap(True)
        hero_layout.addWidget(title)
        hero_layout.addWidget(intro)
        layout.addWidget(hero)

        card = QFrame(objectName="settingsCard")
        card_layout = QVBoxLayout(card)
        model = QLabel("Unterstützter Monitor: MSI MAG 274QPF X30MV")
        model.setObjectName("sectionTitle")
        scope = QLabel(
            "Fix: korrigierte VRR-Kennung in einer anonymisierten EDID für DisplayPort. "
            "Die persönliche Monitor-Seriennummer ist nicht enthalten. HDMI bleibt unverändert."
        )
        scope.setWordWrap(True)
        warning = QLabel(
            "Achtung: Das Profil weist die MSI-EDID allen DisplayPort-Anschlüssen zu. "
            "Andere, gleichzeitig angeschlossene DP-Monitore vorher trennen oder die Aktion abbrechen."
        )
        warning.setObjectName("warningText")
        warning.setWordWrap(True)
        card_layout.addWidget(model)
        card_layout.addWidget(scope)
        card_layout.addWidget(warning)

        provider_row = QHBoxLayout()
        provider_row.addWidget(QLabel("Anbieter auswählen"))
        self.provider_combo = QComboBox()
        self.provider_combo.setProperty("i18nTranslateItems", False)
        self.provider_combo.addItem("Lokal", "local")
        self.provider_combo.addItem("Open Hardware Control", "open_hardware_control")
        self.provider_apply = QPushButton("Auswahl anwenden")
        self.provider_apply.clicked.connect(self.apply_provider)
        provider_row.addWidget(self.provider_combo)
        provider_row.addWidget(self.provider_apply)
        provider_row.addStretch()
        card_layout.addLayout(provider_row)

        action_row = QHBoxLayout()
        self.status_button = QPushButton("Status prüfen")
        self.status_button.clicked.connect(self.refresh_status)
        self.activate_button = QPushButton("Für Ubuntu aktivieren")
        self.activate_button.setObjectName("primaryAction")
        self.activate_button.clicked.connect(lambda: self._start_action("install"))
        self.desktop_button = QPushButton("Desktop-VRR einrichten")
        self.desktop_button.clicked.connect(lambda: self._start_action("desktop"))
        self.game_button = QPushButton("VRR im Spiel testen")
        self.game_button.clicked.connect(lambda: self._start_action("game-test"))
        for button in (self.status_button, self.activate_button, self.desktop_button, self.game_button):
            action_row.addWidget(button)
        action_row.addStretch()
        card_layout.addLayout(action_row)

        service_row = QHBoxLayout()
        self.automation_button = QPushButton("Ubuntu-Automatik installieren / übernehmen")
        self.automation_button.clicked.connect(lambda: self._start_action("automation-install"))
        self.disable_button = QPushButton("Automatik deaktivieren")
        self.disable_button.clicked.connect(lambda: self._start_action("automation-remove"))
        self.uninstall_button = QPushButton("Fix deinstallieren")
        self.uninstall_button.clicked.connect(lambda: self._start_action("uninstall"))
        for button in (self.automation_button, self.disable_button, self.uninstall_button):
            service_row.addWidget(button)
        service_row.addStretch()
        card_layout.addLayout(service_row)
        layout.addWidget(card)

        self.summary = QLabel("Status wird geprüft …")
        self.summary.setObjectName("infoText")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.details = QLabel("")
        self.details.setWordWrap(True)
        self.details.setTextInteractionFlags(self.details.textInteractionFlags())
        layout.addWidget(self.details)
        self.log_button = QPushButton("Details / Protokoll")
        self.log_button.clicked.connect(self.show_log)
        layout.addWidget(self.log_button)
        layout.addStretch()
        self.setWidget(body)

    def refresh_status(self) -> None:
        try:
            status = inspect_status()
        except Exception as error:
            self.summary.setText(f"Statusprüfung fehlgeschlagen: {error}")
            return
        self.last_status = status
        family = status.os_family
        self.activate_button.setText(
            "Für Fedora aktivieren" if family == "fedora" else "Für Ubuntu aktivieren"
        )
        supported = family in {"ubuntu", "fedora"} and status.resources_valid
        self.activate_button.setEnabled(supported)
        ubuntu = family == "ubuntu"
        self.automation_button.setEnabled(ubuntu and status.resources_valid)
        self.disable_button.setEnabled(ubuntu and status.automation_installed)
        self.desktop_button.setEnabled(ubuntu and status.corrected_edid_loaded)
        self.game_button.setEnabled(status.corrected_edid_loaded)
        self.uninstall_button.setEnabled(
            status.boot_configuration_present or status.firmware_present or status.automation_installed
        )
        index = self.provider_combo.findData(status.selected_provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        monitor = ", ".join(status.monitor_connectors) if status.monitor_connectors else "nicht erkannt"
        installation = (
            "von Open Hardware Control verwaltet"
            if status.actual_provider == "open_hardware_control"
            else "lokal installiert" if status.boot_configuration_present or status.automation_installed
            else "nicht installiert"
        )
        reboot = " · Neustart erforderlich" if status.reboot_required else ""
        self.summary.setText(
            f"MSI MAG 274QPF X30MV: {monitor} · {installation}{reboot}"
        )
        self.details.setText(
            "\n".join((
                f"System: {family}",
                f"Korrigierte EDID geladen: {'ja' if status.corrected_edid_loaded else 'nein'}",
                f"Anonymisierte Profil-EDID installiert: {'ja' if status.firmware_valid else 'nein'}",
                f"Bootparameter aktiv / gespeichert: {'ja' if status.boot_parameter_running else 'nein'} / "
                f"{'ja' if status.boot_configuration_present else 'nein'}",
                f"Ubuntu-Automatik installiert / aktiv: {'ja' if status.automation_installed else 'nein'} / "
                f"{'ja' if status.automation_active else 'nein'}",
                f"Anbieter gewählt / tatsächlich: {status.selected_provider} / {status.actual_provider}",
                status.detail,
            ))
        )

    def apply_provider(self) -> None:
        provider = str(self.provider_combo.currentData() or "")
        if provider not in {"local", "open_hardware_control"}:
            return
        if provider == "open_hardware_control":
            answer = QMessageBox.question(
                self, "Vorhandenen Fix übernehmen?",
                "Open Hardware Control übernimmt den bekannten MSI-Fix und verwendet weiterhin genau "
                "den vorhandenen Dienst msi-vrr-games.service. Es wird kein zweiter Wächter gestartet.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                action = "automation-install" if (self.last_status or inspect_status()).os_family == "ubuntu" else "install"
                self._start_action(action, confirmed=True)
            return
        STATE_ROOT.mkdir(parents=True, exist_ok=True)
        path = STATE_ROOT / "provider.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps({"selected": "local", "actual": "local"}), encoding="utf-8")
        os.replace(temporary, path)
        self.refresh_status()

    def _start_action(self, action: str, *, confirmed: bool = False) -> None:
        status = self.last_status or inspect_status()
        descriptions = {
            "install": (
                "MSI MAG 274QPF X30MV – VRR aktivieren?",
                "Die anonymisierte EDID wird als Boot-Ressource eingerichtet. Das Profil gilt für alle "
                "DisplayPort-Anschlüsse; HDMI bleibt unverändert. Das sudo-Passwort wird ausschließlich "
                "im Terminal eingegeben. Es erfolgt kein automatischer Neustart.",
            ),
            "desktop": ("Desktop-VRR einrichten?", "GNOME übernimmt den variablen Modus als normaler Benutzer."),
            "automation-install": (
                "Ubuntu-Automatik installieren / übernehmen?",
                "Der vorhandene Benutzerdienst wird kontrolliert übernommen. Es wird kein zweiter Dienst gestartet.",
            ),
            "automation-remove": (
                "Automatik deaktivieren?",
                "Vorher alle Spiele beenden. Der Boot-/EDID-Fix bleibt installiert.",
            ),
            "game-test": (
                "VRR im Spiel testen?",
                "Nach zehn Sekunden werden 60 Sekunden lang echte DRM-Werte gemessen. Wechsel jetzt in das fokussierte Spiel.",
            ),
            "uninstall": (
                "MSI-VRR-Fix deinstallieren?",
                "Alle Spiele vorher beenden. Nur eindeutig zu diesem Profil gehörende Bootdateien, der exakte "
                "Kernelparameter und die MSI-EDID werden entfernt. Andere Einstellungen bleiben bestehen. "
                "Die Änderung wird erst nach einem bestätigten Neustart wirksam.",
            ),
        }
        if action.startswith("automation") and status.os_family != "ubuntu":
            QMessageBox.warning(self, "Nicht verfügbar", "Fedora bleibt von der Ubuntu-Automatik unverändert.")
            return
        if not confirmed:
            title, body = descriptions[action]
            answer = QMessageBox.question(
                self, title, body,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        spec = terminal_spec(action)
        started = QProcess.startDetached(spec[0], spec[1]) if spec else False
        launched = started[0] if isinstance(started, tuple) else bool(started)
        if not launched:
            QMessageBox.warning(
                self, "Terminal konnte nicht geöffnet werden",
                "Ein unterstütztes Terminal und Python 3 werden benötigt.",
            )
            return
        self.summary.setText("Hardware-Fix-Aktion läuft im Terminal …")
        self.result_timer.start()

    def _poll_result(self) -> None:
        path = STATE_ROOT / "last-result.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return
        job_id = str(payload.get("job_id") or "")
        if not payload.get("finished"):
            self._last_job_id = job_id
            return
        if job_id and job_id == self._last_job_id:
            self.result_timer.stop()
            self.refresh_status()
            if payload.get("success") is not True:
                QMessageBox.warning(self, "Hardware Fix", "Die Aktion wurde nicht erfolgreich abgeschlossen. Details stehen im Protokoll.")

    def show_log(self) -> None:
        path = STATE_ROOT / "last-result.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            log_path = Path(str(payload.get("log_path") or ""))
            text = log_path.read_text(encoding="utf-8", errors="replace")[-20_000:]
        except (OSError, ValueError, TypeError):
            text = "Noch kein Hardware-Fix-Protokoll vorhanden."
        QMessageBox.information(self, "Hardware Fix · Protokoll", text)

    def refresh_language(self) -> None:
        self.refresh_status()
