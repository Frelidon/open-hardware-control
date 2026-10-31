#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-window integration for responsive, fail-closed owner detection."""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from cooling_ownership import (
    CoolingOwnerStatus,
    disable_coolercontrol,
    enable_coolercontrol,
    start_coolercontrol,
    stop_coolercontrol,
)

from .probe import CoolingOwnershipProbe


class ResponsiveStartupMixin:
    """Keep CoolerControl probes off the Qt GUI thread and preserve ownership."""

    def initialize_responsive_startup(self, process_tracker=None) -> None:
        # Unknown is intentionally represented as occupied until the first
        # successful result. No fan write is authorized by an optimistic guess.
        self.cooling_owner_status = CoolingOwnerStatus(True, True, False)
        self.cooling_owner_status_known = False
        self.cooling_owner_callbacks = []
        self.cooling_owner_probe = CoolingOwnershipProbe(
            process_tracker=process_tracker,
            parent=self,
        )
        self.cooling_owner_probe.result_ready.connect(self._cooling_owner_probe_ready)
        self.cooling_owner_probe.failed.connect(self._cooling_owner_probe_failed)

    def refresh_cooling_ownership_status(self, callback=None) -> None:
        if callback is not None:
            self.cooling_owner_callbacks.append(callback)
        self.cooling_owner_probe.request()

    def _cooling_owner_probe_ready(self, status: CoolingOwnerStatus) -> None:
        self.cooling_owner_status = status
        self.cooling_owner_status_known = True
        self._apply_cooling_ownership_status()
        callbacks, self.cooling_owner_callbacks = self.cooling_owner_callbacks, []
        for callback in callbacks:
            callback()

    def _cooling_owner_probe_failed(self, detail: str) -> None:
        self.log_message(
            "KÜHLUNGSBESITZ: Hintergrundprüfung fehlgeschlagen · "
            f"vorheriger/fail-closed Status bleibt aktiv · {detail}"
        )
        if self.cooling_owner_callbacks and hasattr(self, "footer_status"):
            self.footer_status.setText(
                self.tr_static("CoolerControl-Status nicht verfügbar · OHC bleibt read-only")
            )
        self.cooling_owner_callbacks.clear()

    def _apply_cooling_ownership_status(self) -> None:
        conflict = self.cooling_owner_status.coolercontrol_active
        autostart = self.cooling_owner_status.coolercontrol_service_enabled
        if conflict and getattr(self, "mainboard_control_active", False):
            self.log_message(
                "KÜHLUNGSBESITZ: CoolerControl während aktiver OHC-Regelung erkannt · "
                "OHC gibt PWM-Kanäle frei"
            )
            self.mainboard_master_enable.setChecked(False)
        if hasattr(self, "cooling_ownership_label"):
            if conflict:
                source = (
                    "⚠ Der CoolerControl-Hintergrunddienst coolercontrold ist aktiv – auch wenn das Programmfenster geschlossen ist. "
                    "Der Dienst ist für den Systemstart aktiviert. OHC überwacht die Mainboardlüfter nur und schreibt keine PWM-Werte, "
                    "bis du die Steuerung ausdrücklich übernimmst."
                    if autostart else
                    "⚠ Der CoolerControl-Hintergrunddienst coolercontrold ist aktiv – auch wenn das Programmfenster geschlossen ist. "
                    "Der Dienst wurde manuell gestartet; sein Systemstart ist deaktiviert. OHC überwacht die Mainboardlüfter nur und "
                    "schreibt keine PWM-Werte, bis du die Steuerung ausdrücklich übernimmst."
                )
                self.cooling_ownership_label.setText(self.tr_static(source))
                self.cooling_ownership_label.setObjectName("warningText")
            else:
                source = (
                    "✓ Kein konkurrierender CoolerControl-Hintergrunddienst aktiv. Der Dienst ist momentan gestoppt, startet beim nächsten "
                    "Systemstart aber erneut. OHC darf nach Kalibrierung die bestätigten System-Fan-Kanäle übernehmen."
                    if autostart else
                    "✓ Kein konkurrierender CoolerControl-Hintergrunddienst aktiv. Der automatische Systemstart von CoolerControl ist dauerhaft "
                    "deaktiviert. OHC darf nach Kalibrierung die bestätigten System-Fan-Kanäle übernehmen."
                )
                self.cooling_ownership_label.setText(self.tr_static(source))
                self.cooling_ownership_label.setObjectName("healthGood")
            self.cooling_ownership_label.style().unpolish(self.cooling_ownership_label)
            self.cooling_ownership_label.style().polish(self.cooling_ownership_label)
        if hasattr(self, "cooling_takeover_button"):
            self.cooling_takeover_button.setEnabled(conflict)
        if hasattr(self, "cooling_release_button"):
            self.cooling_release_button.setEnabled(not conflict)
        if hasattr(self, "cooling_autostart_button"):
            self.cooling_autostart_button.setText(
                self.tr_static(
                    "CoolerControl dauerhaft deaktivieren" if autostart
                    else "CoolerControl dauerhaft aktivieren"
                )
            )
            self.cooling_autostart_button.setToolTip(
                self.tr_static(
                    "Ändert nach ausdrücklicher Bestätigung den systemweiten Autostart von coolercontrold und benötigt Administratorrechte."
                )
            )
        if hasattr(self, "mainboard_master_enable"):
            self.mainboard_master_enable.setEnabled(not conflict)
        if hasattr(self, "cooling_auto_case_button"):
            self.cooling_auto_case_button.setEnabled(not conflict)
        self.refresh_cooling_dashboard_summary()

    def take_over_cooling_from_coolercontrol(self) -> None:
        self.refresh_cooling_ownership_status(self._confirm_cooling_takeover)

    def _confirm_cooling_takeover(self) -> None:
        if not self.cooling_owner_status.coolercontrol_active:
            self.footer_status.setText(
                self.tr_static("CoolerControl ist bereits inaktiv · OHC kann die bestätigten Lüfter übernehmen")
            )
            return
        answer = QMessageBox.question(
            self, self.tr_static("Lüftersteuerung mit OHC übernehmen"),
            self.tr_static(
                "CoolerControl läuft derzeit und kann dieselben hwmon/PWM-Kanäle bedienen. OHC wird niemals parallel dagegen schreiben.\n\n"
                "CoolerControl jetzt über systemd/Polkit beenden und die Mainboard-Lüfter für Open Hardware Control freigeben? "
                "Die OHC-Regelung startet dadurch noch nicht automatisch; du aktivierst sie anschließend bewusst."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        ok, detail = stop_coolercontrol()
        if not ok:
            self.show_error(f"{self.tr_static('CoolerControl konnte nicht beendet werden:')} {detail}")
            return
        self.coolercontrol_stopped_by_ohc = True
        from modules.application_shutdown.v1_1.journal import record
        record("coolercontrol-stopped-for-ohc")
        self.log_message("KÜHLUNGSBESITZ: CoolerControl beendet · Mainboard-PWM für OHC freigegeben")
        self.footer_status.setText(
            self.tr_static("CoolerControl beendet · OHC kann bestätigte Gehäuselüfter übernehmen")
        )
        QTimer.singleShot(700, self.refresh_cooling_ownership_status)

    def release_cooling_to_coolercontrol(self) -> None:
        if self.mainboard_control_active:
            self.mainboard_master_enable.setChecked(False)
        self.restore_all_mainboard_fans_to_firmware(quiet=True)
        ok, detail = start_coolercontrol()
        if not ok:
            self.show_error(f"{self.tr_static('CoolerControl konnte nicht gestartet werden:')} {detail}")
            return
        self.coolercontrol_stopped_by_ohc = False
        from modules.application_shutdown.v1_1.journal import record
        record("coolercontrol-returned")
        self.log_message("KÜHLUNGSBESITZ: OHC hat alle Kanäle an Firmware zurückgegeben · CoolerControl gestartet")
        self.footer_status.setText(self.tr_static("Mainboard-Lüfter an CoolerControl zurückgegeben"))
        QTimer.singleShot(700, self.refresh_cooling_ownership_status)

    def restore_coolercontrol_on_quit(self) -> None:
        """Return a service that this OHC session explicitly stopped for takeover."""
        if not self.coolercontrol_stopped_by_ohc:
            return
        ok, detail = start_coolercontrol()
        if not ok:
            raise RuntimeError(f"CoolerControl could not be restored: {detail}")
        self.coolercontrol_stopped_by_ohc = False
        from modules.application_shutdown.v1_1.journal import record
        record("coolercontrol-returned")
        self.log_message("KÜHLUNGSBESITZ: CoolerControl nach OHC-Ende wieder gestartet")

    def toggle_coolercontrol_autostart(self) -> None:
        self.refresh_cooling_ownership_status(self._confirm_coolercontrol_autostart)

    def _confirm_coolercontrol_autostart(self) -> None:
        enable = not self.cooling_owner_status.coolercontrol_service_enabled
        if enable:
            title = self.tr_static("CoolerControl dauerhaft aktivieren")
            message = self.tr_static(
                "CoolerControl für den automatischen Systemstart aktivieren und den Hintergrunddienst jetzt starten?\n\n"
                "Eine aktive OHC-Mainboardregelung wird vorher beendet und die Lüfter werden an Firmware/BIOS zurückgegeben. "
                "Für diese systemweite Änderung ist eine Administrator-Bestätigung erforderlich."
            )
        else:
            title = self.tr_static("CoolerControl dauerhaft deaktivieren")
            message = self.tr_static(
                "Den CoolerControl-Hintergrunddienst jetzt beenden und seinen automatischen Systemstart dauerhaft deaktivieren?\n\n"
                "OHC startet dadurch keine Lüfterregelung automatisch. Bestätigte Kanäle können anschließend bewusst in OHC aktiviert werden. "
                "Für diese systemweite Änderung ist eine Administrator-Bestätigung erforderlich."
            )
        answer = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if enable:
            if self.mainboard_control_active:
                self.mainboard_master_enable.setChecked(False)
            self.restore_all_mainboard_fans_to_firmware(quiet=True)
            ok, detail = enable_coolercontrol()
        else:
            ok, detail = disable_coolercontrol()
        if not ok:
            source = (
                "CoolerControl konnte nicht dauerhaft aktiviert werden:"
                if enable else "CoolerControl konnte nicht dauerhaft deaktiviert werden:"
            )
            self.show_error(f"{self.tr_static(source)} {detail}")
            return
        # This is a durable user choice, not a temporary OHC takeover lease.
        self.coolercontrol_stopped_by_ohc = False
        from modules.application_shutdown.v1_1.journal import record
        record("coolercontrol-explicit-setting", enabled=enable)
        state_source = "dauerhaft aktiviert und gestartet" if enable else "beendet und dauerhaft deaktiviert"
        self.log_message(f"KÜHLUNGSBESITZ: CoolerControl {state_source}")
        self.footer_status.setText(f"CoolerControl {self.tr_static(state_source)}")
        QTimer.singleShot(700, self.refresh_cooling_ownership_status)

    def shutdown_responsive_startup(self) -> None:
        if hasattr(self, "cooling_owner_probe"):
            self.cooling_owner_probe.shutdown()
