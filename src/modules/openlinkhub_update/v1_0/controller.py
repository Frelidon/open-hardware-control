#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qt orchestration mixin for confirmed OpenLinkHub updates."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from .policy import update_plan
from modules.ui_performance.v1_1.compact_panels import Disclosure
from modules.openlinkhub_nexus.v1_0 import (
    discover_openlinkhub_root,
    install_nexus_design,
    list_nexus_profiles,
)

OPENLINKHUB_URL = "https://github.com/jurkovic-nikola/OpenLinkHub"
OPENLINKHUB_API_DOCS_URL = f"{OPENLINKHUB_URL}/blob/main/api/README.md"
OPENLINKHUB_USER_INSTALL_URL = f"{OPENLINKHUB_URL}/blob/main/install-user-space.sh"
UPDATE_GUIDE_URL = f"{OPENLINKHUB_URL}#installation-recommended"


class OpenLinkHubUpdateMixin:
    """Connect a host window's existing backend and widgets to update policy."""

    def make_openlinkhub_tab(self) -> QWidget:
        page = QScrollArea()
        page.setWidgetResizable(True)
        page.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        page.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 14, 22, 22)
        status_box = QGroupBox("OpenLinkHub-Status")
        status_layout = QGridLayout(status_box)
        self.openlinkhub_version_label = QLabel("Installation: wird geprüft …")
        self.openlinkhub_service_label = QLabel("Dienstkontext: wird geprüft …")
        self.openlinkhub_api_label = QLabel("Lokale API: wird geprüft …")
        self.openlinkhub_warning_label = QLabel("")
        self.openlinkhub_warning_label.setWordWrap(True)
        self.openlinkhub_warning_label.setObjectName("warningText")
        status_layout.addWidget(self.openlinkhub_version_label, 0, 0)
        status_layout.addWidget(self.openlinkhub_service_label, 0, 1)
        status_layout.addWidget(self.openlinkhub_api_label, 1, 0, 1, 2)
        status_layout.addWidget(self.openlinkhub_warning_label, 2, 0, 1, 2)
        layout.addWidget(status_box)

        actions = QGridLayout()
        self.openlinkhub_refresh_button = QPushButton("↻ OpenLinkHub aktualisieren")
        self.openlinkhub_refresh_button.clicked.connect(self.refresh_openlinkhub_status)
        dashboard = QPushButton("Web-Dashboard öffnen")
        dashboard.clicked.connect(self.open_openlinkhub_dashboard)
        self.openlinkhub_start_button = QPushButton("Benutzerdienst starten")
        self.openlinkhub_start_button.clicked.connect(lambda: self.run_openlinkhub_user_action("start"))
        self.openlinkhub_stop_button = QPushButton("Benutzerdienst stoppen")
        self.openlinkhub_stop_button.clicked.connect(lambda: self.run_openlinkhub_user_action("stop"))
        self.openlinkhub_restart_button = QPushButton("Benutzerdienst neu starten")
        self.openlinkhub_restart_button.clicked.connect(lambda: self.run_openlinkhub_user_action("restart"))
        self.openlinkhub_enable_button = QPushButton("Beim Login aktivieren")
        self.openlinkhub_enable_button.clicked.connect(lambda: self.run_openlinkhub_user_action("enable"))
        for widget, row, column in (
            (self.openlinkhub_refresh_button, 0, 0), (dashboard, 0, 1), (self.openlinkhub_enable_button, 0, 2),
            (self.openlinkhub_start_button, 1, 0), (self.openlinkhub_stop_button, 1, 1),
            (self.openlinkhub_restart_button, 1, 2),
        ):
            actions.addWidget(widget, row, column)
        actions.setColumnStretch(3, 1)
        service_body = QWidget()
        service_layout = QVBoxLayout(service_body)
        service_layout.addLayout(actions)

        update_box = QGroupBox("OpenLinkHub und Web-UI aktualisieren")
        update_layout = QVBoxLayout(update_box)
        self.openlinkhub_latest_label = QLabel("Neueste offizielle OpenLinkHub-Version wurde noch nicht geprüft.")
        self.openlinkhub_latest_label.setWordWrap(True)
        update_actions = QHBoxLayout()
        self.openlinkhub_check_update_button = QPushButton("Neueste Version prüfen")
        self.openlinkhub_check_update_button.clicked.connect(self.check_openlinkhub_updates)
        self.openlinkhub_install_update_button = QPushButton("OpenLinkHub jetzt aktualisieren")
        self.openlinkhub_install_update_button.setEnabled(False)
        self.openlinkhub_install_update_button.clicked.connect(self.install_openlinkhub_update)
        update_actions.addWidget(self.openlinkhub_check_update_button)
        update_actions.addWidget(self.openlinkhub_install_update_button)
        update_actions.addStretch()
        update_note = QLabel(
            "Das Web-Dashboard ist Bestandteil von OpenLinkHub und wird mit demselben Paket aktualisiert. "
            "OHC verwendet ausschließlich bereits eingerichtete DNF-/APT-Paketquellen und zeigt vor der "
            "Administratorabfrage den vollständigen Aktualisierungsweg. Manuelle und immutable Installationen "
            "bleiben bei der offiziellen OpenLinkHub-Anleitung."
        )
        update_note.setWordWrap(True)
        update_note.setObjectName("muted")
        update_layout.addWidget(self.openlinkhub_latest_label)
        update_layout.addLayout(update_actions)
        update_layout.addWidget(update_note)
        service_layout.addWidget(update_box)

        write_box = QGroupBox("Direkte Gerätesteuerung")
        write_layout = QVBoxLayout(write_box)
        self.openlinkhub_write_checkbox = QCheckBox("Direkte OpenLinkHub-Schreibzugriffe für diese Programmsitzung aktivieren")
        self.openlinkhub_write_checkbox.toggled.connect(self.set_openlinkhub_writes_enabled)
        self.openlinkhub_write_status_label = QLabel("Gesperrt · erst aktivieren, wenn genau eine OpenLinkHub-Instanz läuft.")
        self.openlinkhub_write_status_label.setWordWrap(True)
        self.openlinkhub_write_status_label.setObjectName("warningText")
        write_layout.addWidget(self.openlinkhub_write_checkbox)
        write_layout.addWidget(self.openlinkhub_write_status_label)
        layout.addWidget(write_box)

        self.openlinkhub_devices_table = QTableWidget(0, 7)
        self.openlinkhub_devices_table.setHorizontalHeaderLabels(
            ["Gerät", "Kanal", "Temperatur", "Drehzahl", "Profil", "RGB", "Firmware"]
        )
        self.openlinkhub_devices_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.openlinkhub_devices_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.openlinkhub_devices_table.setAccessibleName("Von OpenLinkHub erkannte Corsair-Geräte")
        self.openlinkhub_devices_table.setMinimumHeight(230)
        devices_body = self.openlinkhub_devices_table

        nexus_box = QGroupBox("iCUE NEXUS · OHC-Designmanager")
        nexus_layout = QVBoxLayout(nexus_box)
        nexus_note = QLabel(
            "OHC kann statische 640×48-Hintergründe und validierte Touch-Schaltflächen in eine lokale "
            "OpenLinkHub-Benutzerinstallation übernehmen. OpenLinkHub bleibt der einzige USB-Treiber; vor jeder "
            "Änderung wird nexus.json gesichert. Neue dynamische Sensoransichten benötigen weiterhin Unterstützung "
            "direkt in OpenLinkHub."
        )
        nexus_note.setWordWrap(True)
        nexus_note.setObjectName("muted")
        nexus_layout.addWidget(nexus_note)
        nexus_actions = QHBoxLayout()
        self.openlinkhub_nexus_device_combo = QComboBox()
        self.openlinkhub_nexus_device_combo.setMinimumWidth(220)
        self.openlinkhub_nexus_device_combo.setProperty("i18nTranslateItems", False)
        self.openlinkhub_nexus_profile_combo = QComboBox()
        self.openlinkhub_nexus_profile_combo.setMinimumWidth(220)
        self.openlinkhub_nexus_profile_combo.setProperty("i18nTranslateItems", False)
        self.openlinkhub_nexus_import_button = QPushButton("Design / Paket importieren")
        self.openlinkhub_nexus_import_button.clicked.connect(self.import_openlinkhub_nexus_design)
        self.openlinkhub_nexus_activate_button = QPushButton("Auf NEXUS anzeigen")
        self.openlinkhub_nexus_activate_button.clicked.connect(self.activate_openlinkhub_nexus_profile)
        nexus_actions.addWidget(self.openlinkhub_nexus_device_combo)
        nexus_actions.addWidget(self.openlinkhub_nexus_profile_combo)
        nexus_actions.addWidget(self.openlinkhub_nexus_import_button)
        nexus_actions.addWidget(self.openlinkhub_nexus_activate_button)
        nexus_layout.addLayout(nexus_actions)
        self.openlinkhub_nexus_status_label = QLabel("NEXUS-Installation und Gerät werden beim Aktualisieren geprüft.")
        self.openlinkhub_nexus_status_label.setWordWrap(True)
        self.openlinkhub_nexus_status_label.setObjectName("infoText")
        nexus_layout.addWidget(self.openlinkhub_nexus_status_label)
        nexus_section = Disclosure(self.tr_static("iCUE NEXUS · OHC-Designmanager"), nexus_box)
        self.refresh_openlinkhub_nexus_widgets([])
        layout.addWidget(self.make_openlinkhub_control_tabs())

        help_box = QGroupBox("Dienstkontext und Hilfe")
        help_layout = QVBoxLayout(help_box)
        help_text = QLabel(
            "Für Medienwiedergabe und virtuelles Audio muss OpenLinkHub im Benutzerkontext laufen. "
            "Open Hardware Control verändert oder entfernt den systemweiten Dienst nicht automatisch, damit niemals "
            "zwei OpenLinkHub-Instanzen gleichzeitig auf dieselbe Hardware zugreifen. Dasselbe Corsair-Gerät darf "
            "auch nicht gleichzeitig von OpenLinkHub und ckb-next gesteuert werden."
        )
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        migration_help = QPushButton("Migrationshilfe: System → Benutzer")
        migration_help.clicked.connect(self.show_openlinkhub_migration_help)
        help_layout.addWidget(migration_help)
        links = QHBoxLayout()
        links.addWidget(self.make_external_link("Offizielles OpenLinkHub-Projekt", OPENLINKHUB_URL))
        links.addWidget(self.make_external_link("API-Dokumentation", OPENLINKHUB_API_DOCS_URL))
        links.addWidget(self.make_external_link("Offizielle Benutzerinstallation", OPENLINKHUB_USER_INSTALL_URL))
        links.addStretch()
        help_layout.addLayout(links)
        service_layout.addWidget(help_box)
        layout.addWidget(Disclosure(self.tr_static("Erkannte Geräte"), devices_body))
        layout.addWidget(nexus_section)
        layout.addWidget(Disclosure(self.tr_static("Dienst und Aktualisierung"), service_body))
        layout.addStretch()
        return page

    def refresh_openlinkhub_nexus_widgets(self, devices: list[object]) -> None:
        if not hasattr(self, "openlinkhub_nexus_profile_combo"):
            return
        previous_device = str(self.openlinkhub_nexus_device_combo.currentData() or "")
        self.openlinkhub_nexus_device_combo.clear()
        for raw in devices:
            if not isinstance(raw, dict):
                continue
            product = str(raw.get("product") or "")
            if int(raw.get("product_type") or 0) != 9 and "nexus" not in product.casefold():
                continue
            control_id = str(raw.get("control_id") or "")
            if control_id:
                self.openlinkhub_nexus_device_combo.addItem(product or "iCUE NEXUS", control_id)
        device_index = self.openlinkhub_nexus_device_combo.findData(previous_device)
        self.openlinkhub_nexus_device_combo.setCurrentIndex(max(0, device_index))

        previous_profile = str(self.openlinkhub_nexus_profile_combo.currentData() or "")
        root = discover_openlinkhub_root()
        self.openlinkhub_nexus_profile_combo.clear()
        for profile_id, name in list_nexus_profiles(root):
            self.openlinkhub_nexus_profile_combo.addItem(name, profile_id)
        profile_index = self.openlinkhub_nexus_profile_combo.findData(previous_profile)
        self.openlinkhub_nexus_profile_combo.setCurrentIndex(max(0, profile_index))
        has_installation = root is not None
        has_device = self.openlinkhub_nexus_device_combo.count() > 0
        has_profile = self.openlinkhub_nexus_profile_combo.count() > 0
        self.openlinkhub_nexus_import_button.setEnabled(has_installation)
        self.openlinkhub_nexus_activate_button.setEnabled(has_device and has_profile)
        if not has_installation:
            status = "Keine unterstützte OpenLinkHub-Benutzerinstallation gefunden."
        elif not has_device:
            status = f"Designordner bereit: {root} · aktuell kein iCUE NEXUS über die lokale API erkannt."
        else:
            status = f"iCUE NEXUS erkannt · {self.openlinkhub_nexus_profile_combo.count()} Design(s) verfügbar."
        self.openlinkhub_nexus_status_label.setText(status)

    def import_openlinkhub_nexus_design(self) -> None:
        source, _selected_filter = QFileDialog.getOpenFileName(
            self,
            self.tr_static("NEXUS-Design importieren"),
            str(Path.home() / "Bilder"),
            self.tr_static("NEXUS-Designs (*.png *.jpg *.jpeg *.webp *.json)"),
        )
        if not source:
            return
        answer = QMessageBox.question(
            self,
            self.tr_static("NEXUS-Design übernehmen"),
            self.tr_static(
                "Das Design wird auf 640×48 vorbereitet und in die lokale OpenLinkHub-Benutzerinstallation kopiert. "
                "nexus.json wird vorher gesichert und der Benutzerdienst danach neu gestartet. Fortfahren?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            result = install_nexus_design(Path(source))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self.show_error(f"Das NEXUS-Design konnte nicht importiert werden: {exc}")
            return
        self.openlinkhub_nexus_status_label.setText(
            f"„{result.name}“ wurde importiert · OpenLinkHub wird neu gestartet."
        )
        self.log_message(
            f"OPENLINKHUB-NEXUS: Design {result.profile_id} importiert · Backup {result.backup.name}"
        )
        self.refresh_openlinkhub_nexus_widgets(getattr(self, "openlinkhub_last_status", {}).get("devices", []))
        profile_index = self.openlinkhub_nexus_profile_combo.findData(result.profile_id)
        if profile_index >= 0:
            self.openlinkhub_nexus_profile_combo.setCurrentIndex(profile_index)
        self.run_openlinkhub_user_action("restart")

    def activate_openlinkhub_nexus_profile(self) -> None:
        control_id = str(self.openlinkhub_nexus_device_combo.currentData() or "")
        profile = str(self.openlinkhub_nexus_profile_combo.currentData() or "")
        if not control_id or not profile:
            self.show_error(self.tr_static("Bitte zuerst NEXUS-Gerät und Design auswählen."))
            return
        self.run_openlinkhub_write(
            "lcd-profile", {"control_id": control_id, "profile": profile},
            f"NEXUS-Design „{self.openlinkhub_nexus_profile_combo.currentText()}“ anzeigen",
        )

    @staticmethod
    def openlinkhub_update_helper_path() -> Path:
        return Path(__file__).resolve().parent / "check.py"

    def check_openlinkhub_updates(self) -> None:
        if not hasattr(self, "openlinkhub_check_update_button"):
            return
        self.openlinkhub_check_update_button.setEnabled(False)
        self.openlinkhub_install_update_button.setEnabled(False)
        self.openlinkhub_latest_label.setText(self.tr_static("Neueste offizielle OpenLinkHub-Version wird geprüft …"))

        def done(result) -> None:
            self.openlinkhub_check_update_button.setEnabled(True)
            try:
                payload = json.loads(result.stdout)
                if not result.ok or not isinstance(payload, dict) or not payload.get("ok"):
                    raise ValueError(str(payload.get("error") or result.combined or "Versionsprüfung fehlgeschlagen"))
            except (json.JSONDecodeError, ValueError) as exc:
                self.openlinkhub_update_status = {}
                self.openlinkhub_latest_label.setText(f"{self.tr_static('OpenLinkHub-Version konnte nicht geprüft werden:')} {exc}")
                return
            self.openlinkhub_update_status = payload
            installed = str(payload.get("installed_version") or "nicht erkannt")
            latest = str(payload.get("latest_version") or "nicht erkannt")
            automatic = bool(payload.get("automatic"))
            available = bool(payload.get("update_available"))
            state = self.tr_static(
                "Aktualisierung verfügbar" if available else "bereits aktuell" if automatic else "manueller Aktualisierungsweg"
            )
            self.openlinkhub_latest_label.setText(
                self.tr_static("Installiert: {installed} · Offiziell aktuell: {latest} · {state}").format(
                    installed=installed, latest=latest, state=state,
                )
            )
            self.openlinkhub_install_update_button.setText(
                self.tr_static("OpenLinkHub jetzt aktualisieren" if automatic else "Offizielle Aktualisierungsanleitung öffnen")
            )
            self.openlinkhub_install_update_button.setEnabled(available if automatic else True)
            self.log_message(f"OPENLINKHUB-UPDATE: installiert={installed} · aktuell={latest} · Weg={payload.get('method')}")

        self.backend.run_async(
            [sys.executable, str(self.openlinkhub_update_helper_path())], callback=done, timeout=15, log_output=False,
        )

    def install_openlinkhub_update(self) -> None:
        plan = update_plan()
        if not plan.automatic:
            if not QDesktopServices.openUrl(QUrl(UPDATE_GUIDE_URL)):
                self.show_error(self.tr_static("Die offizielle OpenLinkHub-Aktualisierungsanleitung konnte nicht geöffnet werden."))
            return
        latest = str(self.openlinkhub_update_status.get("latest_version") or "neueste verfügbare Version")
        commands = [" ".join(Path(part).name if index == 0 else part for index, part in enumerate(command)) for command in plan.commands]
        if plan.method == "user-space":
            commands = [self.tr_static(
                "Offizielles GitHub-Archiv laden · veröffentlichte SHA-256 prüfen · Benutzerdienst mit lokalem Backup aktualisieren"
            )]
        answer = QMessageBox.question(
            self, self.tr_static("OpenLinkHub aktualisieren"),
            self.tr_static(
                "OpenLinkHub einschließlich Web-UI wird auf {latest} aktualisiert.\n\n"
                "Aktualisierungsweg: {method}\nSchritte/Befehl(e):\n{commands}\n\n"
                "Die Aktualisierung beginnt erst nach dieser Bestätigung; falls Administratorrechte nötig sind, folgt danach die Systemabfrage. "
                "Eigene OpenLinkHub-Profile bleiben erhalten. Fortfahren?"
            ).format(latest=latest, method=plan.method.upper(), commands="\n".join(commands)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.openlinkhub_install_update_button.setEnabled(False)
        self.openlinkhub_check_update_button.setEnabled(False)
        self.openlinkhub_latest_label.setText(self.tr_static("OpenLinkHub und Web-UI werden aktualisiert …"))
        if plan.method == "user-space":
            self._prepare_openlinkhub_user_space_update()
            return
        self._openlinkhub_update_commands = [list(command) for command in plan.commands]
        self._run_next_openlinkhub_update_command()

    def _prepare_openlinkhub_user_space_update(self) -> None:
        cache_root = self.app_config_dir / "updates/openlinkhub"
        helper = self.openlinkhub_update_helper_path()

        def prepared(result) -> None:
            try:
                payload = json.loads(result.stdout)
                stage = Path(str(payload.get("stage") or ""))
                if not result.ok or not payload.get("ok") or not stage.is_dir():
                    raise ValueError(str(payload.get("error") or result.combined or "OpenLinkHub-Archiv konnte nicht vorbereitet werden"))
            except (json.JSONDecodeError, ValueError) as exc:
                self._openlinkhub_update_failed(str(exc))
                return
            apply_helper = helper.with_name("apply_user_space.py")

            def applied(apply_result) -> None:
                try:
                    apply_payload = json.loads(apply_result.stdout)
                except json.JSONDecodeError:
                    apply_payload = {"ok": False, "error": apply_result.combined}
                if not apply_result.ok or not apply_payload.get("ok"):
                    self._openlinkhub_update_failed(str(
                        apply_payload.get("error") or self.tr_static("OpenLinkHub konnte nicht aktualisiert werden.")
                    ))
                    return
                self._openlinkhub_update_commands = []
                self._run_next_openlinkhub_update_command()

            self.backend.run_async(
                [sys.executable, str(apply_helper), "--stage", str(stage), "--cache-root", str(cache_root)],
                callback=applied, timeout=180, log_output=False,
            )

        self.backend.run_async(
            [sys.executable, str(helper), "--prepare-user-space", str(cache_root)],
            callback=prepared, timeout=90, log_output=False,
        )

    def _openlinkhub_update_failed(self, detail: str) -> None:
        self.openlinkhub_check_update_button.setEnabled(True)
        self.openlinkhub_install_update_button.setEnabled(True)
        self.openlinkhub_latest_label.setText(self.tr_static("OpenLinkHub-Aktualisierung wurde abgebrochen oder ist fehlgeschlagen."))
        self.show_error(detail)

    def _run_next_openlinkhub_update_command(self) -> None:
        commands = getattr(self, "_openlinkhub_update_commands", [])
        if not commands:
            self.openlinkhub_check_update_button.setEnabled(True)
            self.openlinkhub_latest_label.setText(self.tr_static(
                "OpenLinkHub und Web-UI wurden aktualisiert. Dienststatus wird neu gelesen; bei alter Web-Ansicht bitte den Browser-Cache leeren."
            ))
            self.log_message("OPENLINKHUB-UPDATE: Paketaktualisierung abgeschlossen")
            QTimer.singleShot(700, self.refresh_openlinkhub_status)
            QTimer.singleShot(1000, self.check_openlinkhub_updates)
            return
        command = commands.pop(0)

        def done(result) -> None:
            if not result.ok:
                self._openlinkhub_update_commands = []
                self._openlinkhub_update_failed(result.combined or self.tr_static("OpenLinkHub konnte nicht aktualisiert werden."))
                return
            self._run_next_openlinkhub_update_command()

        self.backend.run_async(command, callback=done, timeout=900, log_output=False)
