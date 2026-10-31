#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step-by-step NCT6687 driver, DKMS signing and MOK enrollment wizard."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Callable

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QApplication, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget,
    QWizard, QWizardPage,
)

from .distribution import DistributionInfo, setup_plan
from .model import MokStatus, privileged_terminal_spec, setup_step_completion


GUIDE_HTML = """<h3>NCT6687 schrittweise einrichten</h3><ol><li>Treiber installieren.</li><li>DKMS-Zertifikat prüfen oder erzeugen.</li><li>MOK bei aktivem Secure Boot registrieren.</li><li>Neu starten und im blauen MOK Manager „Enroll MOK“ → „Continue“ physisch bestätigen.</li><li>Treiber laden und Status prüfen.</li></ol><p>Erledigte Schritte werden übersprungen; die jeweils nötige Aktion bleibt anklickbar. OHC sieht kein Passwort, deaktiviert Secure Boot nicht und startet nicht selbst neu.</p>"""


class SetupStepPage(QWizardPage):
    """One status-gated page whose action disappears once it is complete."""

    def __init__(self, title: str, action_text: str = "") -> None:
        super().__init__()
        self.setTitle(title)
        layout = QVBoxLayout(self)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        layout.addStretch()
        self.action_button = QPushButton(action_text)
        self.action_button.setVisible(bool(action_text))
        layout.addWidget(self.action_button)
        self._complete = False

    def isComplete(self) -> bool:
        return self._complete

    def set_state(self, text: str, *, complete: bool, action_visible: bool, action_enabled: bool) -> None:
        changed = self._complete != bool(complete)
        self._complete = bool(complete)
        self.status_label.setText(text)
        self.action_button.setVisible(bool(action_visible))
        self.action_button.setEnabled(bool(action_enabled))
        if changed:
            self.completeChanged.emit()


class Nct6687SetupDialog(QWizard):
    INTRO, DRIVER, CERTIFICATE, MOK, LOAD, PERMISSION, FINISH = range(7)

    def __init__(
        self,
        parent: QWidget,
        translate: Callable[[str], str],
        *,
        initial_status: MokStatus | None = None,
    ) -> None:
        super().__init__(parent)
        self.translate = translate
        self.status: MokStatus | None = None
        self._status_process: QProcess | None = None
        self.setWindowTitle(self.tr_text("NCT6687 · Treiber- und MOK-Assistent"))
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.WizardOption.HaveCustomButton1, True)
        self.setButtonText(QWizard.WizardButton.BackButton, self.tr_text("◀  Zurück"))
        self.setButtonText(QWizard.WizardButton.NextButton, self.tr_text("Weiter  ▶"))
        self.setButtonText(QWizard.WizardButton.FinishButton, self.tr_text("Schließen"))
        self.setButtonText(QWizard.WizardButton.CancelButton, self.tr_text("Abbrechen"))
        self.setButtonText(QWizard.WizardButton.CustomButton1, self.tr_text("Status erneut prüfen"))
        self.setMinimumSize(820, 560)

        self.intro_page = SetupStepPage(self.tr_text("Aktueller Secure-Boot-/MOK-Status"))
        self.intro_page.status_label.setText(self.tr_text(GUIDE_HTML))
        self.driver_page = SetupStepPage(
            self.tr_text("1 · Passende Treiberbefehle kopieren"),
            self.tr_text("1 · Passende Treiberbefehle kopieren"),
        )
        self.certificate_page = SetupStepPage(
            self.tr_text("2 · DKMS-Schlüssel erzeugen"), self.tr_text("2 · DKMS-Schlüssel erzeugen")
        )
        self.mok_page = SetupStepPage(
            self.tr_text("3 · MOK-Import im Terminal starten"), self.tr_text("3 · MOK-Import im Terminal starten")
        )
        self.load_page = SetupStepPage(
            self.tr_text("4 · Treiber nach Neustart laden"), self.tr_text("4 · Treiber nach Neustart laden")
        )
        self.permission_page = SetupStepPage(
            self.tr_text("5 · Dauerhafte Lüfterberechtigung"),
            self.tr_text("Dauerhafte Berechtigung erteilen"),
        )
        self.finish_page = SetupStepPage(self.tr_text("NCT6687 · Treiber- und MOK-Assistent"))
        for page_id, page in enumerate((
            self.intro_page, self.driver_page, self.certificate_page,
            self.mok_page, self.load_page, self.permission_page, self.finish_page,
        )):
            self.setPage(page_id, page)

        self.driver_page.action_button.clicked.connect(self.copy_driver_commands)
        self.certificate_page.action_button.clicked.connect(lambda: self.run_action("generate"))
        self.mok_page.action_button.clicked.connect(lambda: self.run_action("import"))
        self.load_page.action_button.clicked.connect(lambda: self.run_action("load"))
        self.permission_page.action_button.clicked.connect(self.open_persistent_permission)
        self.button(QWizard.WizardButton.CustomButton1).clicked.connect(self.refresh_status)
        if initial_status is None:
            self.refresh_status()
        else:
            self.apply_status(initial_status)

    def tr_text(self, source: str) -> str:
        return self.translate(source)

    def refresh_status(self) -> None:
        if self._status_process is not None:
            return
        checking = self.tr_text("Einrichtungsstatus wird geprüft …")
        for page in self._step_pages():
            page.set_state(checking, complete=False, action_visible=False, action_enabled=False)
        self.button(QWizard.WizardButton.CustomButton1).setEnabled(False)
        process = QProcess(self)
        self._status_process = process
        process.finished.connect(self._status_finished)
        process.errorOccurred.connect(self._status_failed)
        process.start(sys.executable, [str(Path(__file__).with_name("model.py")), "--status-json"])

    def _status_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        process = self._status_process
        self._status_process = None
        self.button(QWizard.WizardButton.CustomButton1).setEnabled(True)
        if process is None or exit_code != 0:
            self._show_unknown_status()
            return
        try:
            payload = json.loads(bytes(process.readAllStandardOutput()).decode("utf-8"))
            self.apply_status(MokStatus(**payload))
        except (TypeError, ValueError, UnicodeError, json.JSONDecodeError):
            self._show_unknown_status()

    def _status_failed(self, _error: QProcess.ProcessError) -> None:
        if self._status_process is None:
            return
        self._status_process = None
        self.button(QWizard.WizardButton.CustomButton1).setEnabled(True)
        self._show_unknown_status()

    def _show_unknown_status(self) -> None:
        unknown = self.tr_text("Unbekannt")
        for page in self._step_pages():
            page.set_state(unknown, complete=False, action_visible=False, action_enabled=False)

    def _step_pages(self) -> tuple[SetupStepPage, ...]:
        return (
            self.intro_page, self.driver_page, self.certificate_page,
            self.mok_page, self.load_page, self.permission_page, self.finish_page,
        )

    def _state(self, label: str, value: str) -> str:
        return f"<b>{self.tr_text(label)}:</b> {self.tr_text(value)}"

    def apply_status(self, status: MokStatus) -> None:
        self.status = status
        driver_done, certificate_done, mok_done, load_done = setup_step_completion(status)
        boot = {"enabled": "Aktiviert", "disabled": "Deaktiviert"}.get(status.secure_boot, "Unbekannt")
        enrollment = "Registriert" if status.enrolled is True else (
            "Nicht registriert" if status.enrolled is False else "Nicht prüfbar"
        )
        module = "Geladen" if status.module_loaded else (
            "Vorhanden" if status.module_available else "Nicht gefunden"
        )
        all_lines = (
            self._state("Erkannte Distribution", status.distribution_name),
            self._state("Erkanntes Mainboard", status.board_name),
            self._state("Secure Boot", boot),
            self._state("DKMS-Zertifikat", "Vorhanden" if status.certificate_exists else "Fehlt"),
            self._state("MOK-Schlüssel", enrollment),
            self._state("nct6687", module),
            self._state("Modulsignatur", status.module_signer or "Nicht gefunden"),
        )
        self.intro_page.set_state(
            self.tr_text(GUIDE_HTML) + "<hr>" + "<br>".join(all_lines),
            complete=True, action_visible=False, action_enabled=False,
        )
        distribution = DistributionInfo(
            status.distribution_id, status.distribution_name, status.distribution_family
        )
        plan = setup_plan(distribution, msi_x870=status.msi_x870_family)
        driver_lines = [
                self._state("Erkannte Distribution", status.distribution_name),
                self._state("Erkanntes Mainboard", status.board_name),
                self._state("nct6687", module),
                self._state("Modulsignatur", status.module_signer or "Nicht gefunden"),
        ]
        if plan is None:
            driver_lines.append(self.tr_text(
                "Für diese Distribution gibt es keinen festen Installationsbefehl. Unterstützt werden Fedora, Ubuntu und Arch Linux."
            ))
        elif plan.family == "arch":
            driver_lines.append(self.tr_text(
                "Arch Linux: linux-headers gilt für den Standardkernel. Bei linux-lts oder linux-zen muss das passende Headerpaket verwendet werden."
            ))
        elif plan.family == "ubuntu":
            driver_lines.append(self.tr_text(
                "Ubuntu: Paketlisten-Aktualisierung und Paketinstallation sind getrennte Schritte. Eine fehlerhafte Fremdquelle wird gemeldet, aber OHC verändert sie nicht automatisch."
            ))
        self.driver_page.set_state(
            "<br>".join(driver_lines),
            complete=driver_done, action_visible=not driver_done,
            action_enabled=plan is not None,
        )
        self.certificate_page.set_state(
            "<br>".join((
                self._state("DKMS-Zertifikat", "Vorhanden" if status.certificate_exists else "Fehlt"),
                self._state("DKMS", "Vorhanden" if status.dkms_available else "Fehlt"),
            )),
            complete=certificate_done,
            action_visible=not certificate_done,
            action_enabled=status.dkms_available and status.sudo_available and status.terminal_available,
        )
        self.mok_page.set_state(
            "<br>".join((
                self._state("Secure Boot", boot),
                self._state("MOK-Schlüssel", enrollment),
                self._state("mokutil", "Vorhanden" if status.mokutil_available else "Fehlt"),
            )),
            complete=mok_done,
            action_visible=not mok_done,
            action_enabled=(
                status.certificate_exists and status.mokutil_available
                and status.sudo_available and status.terminal_available
            ),
        )
        self.load_page.set_state(
            "<br>".join((
                self._state("nct6687", module),
                self._state("modprobe", "Vorhanden" if status.modprobe_available else "Fehlt"),
            )),
            complete=load_done,
            action_visible=not load_done,
            action_enabled=(
                driver_done and mok_done and status.modprobe_available
                and status.sudo_available and status.terminal_available
            ),
        )
        from mainboard_fan_control import (
            persistent_fan_authorization_enabled,
            privileged_fan_helper_available,
        )
        persistent_permission = persistent_fan_authorization_enabled()
        helper_available = privileged_fan_helper_available()
        permission_text = self.tr_text(
            "Die dauerhafte Lüfterfreigabe ist aktiv und bleibt bei OHC-Updates sowie Neustarts erhalten."
            if persistent_permission else
            "Richte die optionale Dauerfreigabe einmalig ein. Sie gilt nur für den begrenzten NCT6687-Lüfterhelfer; Paketinstallationen bleiben normale Administratoraktionen."
        )
        self.permission_page.set_state(
            permission_text,
            complete=True,
            action_visible=not persistent_permission,
            action_enabled=helper_available and not persistent_permission,
        )
        finish_lines = (*all_lines, self._state(
            "Dauerhafte Lüfterberechtigung",
            "Aktiviert" if persistent_permission else "Nicht aktiviert",
        ))
        self.finish_page.set_state(
            "<br>".join(finish_lines), complete=load_done,
            action_visible=False, action_enabled=False,
        )

    def copy_driver_commands(self) -> None:
        if self.status is None:
            return
        distribution = DistributionInfo(
            self.status.distribution_id,
            self.status.distribution_name,
            self.status.distribution_family,
        )
        plan = setup_plan(distribution, msi_x870=self.status.msi_x870_family)
        if plan is None:
            QMessageBox.warning(self, self.tr_text("Distribution nicht unterstützt"), self.tr_text(
                "Für diese Distribution gibt es keinen festen Installationsbefehl. Unterstützt werden Fedora, Ubuntu und Arch Linux."
            ))
            return
        QApplication.clipboard().setText("\n".join(plan.commands))
        QMessageBox.information(self, self.tr_text("Treiberbefehle kopiert"), self.tr_text(
            "Die zustandsfesten Befehle für {distribution} wurden kopiert. Führe sie der Reihe nach aus; ein vorhandener Git-Checkout wird aktualisiert. Behebe gemeldete fehlerhafte Paketquellen separat und kehre danach für die MOK-Schritte hierher zurück."
        ).format(distribution=plan.label))

    def open_persistent_permission(self) -> None:
        host = self.parentWidget()
        action = getattr(host, "set_persistent_mainboard_fan_authorization", None)
        if not callable(action):
            QMessageBox.warning(
                self,
                self.tr_text("Dauerhafte Lüfterberechtigung"),
                self.tr_text("Die Dauerfreigabe kann nur aus dem Hauptfenster von Open Hardware Control eingerichtet werden."),
            )
            return
        self.accept()
        action(True)

    def run_action(self, action: str) -> None:
        explanation = {
            "generate": "DKMS erzeugt jetzt nur dann ein neues Schlüsselpaar, wenn noch kein Zertifikat vorhanden ist.",
            "import": "Der Import wird nur vorgemerkt. Merke dir das gleich zweimal eingegebene einmalige MOK-Passwort für den blauen Bildschirm nach dem Neustart.",
            "load": "Der signierte nct6687-Treiber wird jetzt geladen. Bei einer erneuten Schlüsselablehnung bleibt Secure Boot unverändert aktiv.",
        }[action]
        answer = QMessageBox.question(
            self, self.tr_text("Systemaktion im Terminal starten?"), self.tr_text(explanation),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        spec = privileged_terminal_spec(action)
        started = QProcess.startDetached(spec[0], spec[1]) if spec is not None else False
        launched = started[0] if isinstance(started, tuple) else bool(started)
        if not launched:
            QMessageBox.warning(self, self.tr_text("Terminal konnte nicht geöffnet werden"), self.tr_text(
                "Prüfe, ob mokutil, DKMS, sudo und ein unterstütztes Terminal installiert sind."
            ))
            return
        QMessageBox.information(self, self.tr_text("Terminal gestartet"), self.tr_text(
            "Schließe die Terminalaktion vollständig ab und wähle danach „Status erneut prüfen“. Nach einem MOK-Import ist ein Neustart mit physischer Bestätigung erforderlich."
        ))


def show_nct6687_setup_assistant(parent: QWidget) -> None:
    translator = getattr(parent, "tr_static", lambda text: text)
    Nct6687SetupDialog(parent, translator).exec()
