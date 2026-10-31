# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit local-input and current LACT-profile reset actions."""
from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from .client import LactError
from .snapshot import forget_snapshot


class GpuResetUiMixin:
    def discard_gpu_inputs(self) -> None:
        """Reload the current LACT state; never write a GPU setting."""
        self.refresh()
        self.status.setText(self.tr("Eingaben verworfen; aktuelle LACT-Werte neu geladen."))
        self._gpu_log("GPU-LACT: ungespeicherte Eingaben verworfen · LACT-Werte neu geladen")

    def reset_lact_profile(self) -> None:
        """Clear only the selected GPU's active LACT profile after confirmation."""
        if not self._write_allowed():
            return
        if not self.gpu_id or self.baseline is None or self.preview_active or self.stress_process is not None:
            return
        if not self.refresh_ownership():
            self.status.setText(self.tr("GPU-Lüfter in CoolerControl zuerst auf „Unmanaged“ stellen und erneut prüfen."))
            return
        try:
            current = self.client.config(self.gpu_id)
        except LactError as exc:
            self.status.setText(self.tr("GPU-Daten konnten nicht gelesen werden: {reason}").format(reason=exc))
            return
        if current != self.baseline:
            self.status.setText(self.tr("LACT-Werte wurden außerhalb von OHC geändert. Bitte zuerst aktualisieren."))
            return
        if not current:
            self.status.setText(self.tr("LACT-Profil hat bereits Standardwerte."))
            return
        answer = QMessageBox.question(
            self, self.tr("LACT-Werte zurücksetzen"),
            self.tr("Alle Tuning- und Lüfterwerte des ausgewählten GPU-Profils in LACT auf Standard zurücksetzen?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        pending = False
        try:
            if self.client.config(self.gpu_id) != current:
                raise LactError("LACT GPU profile changed while the reset confirmation was open")
            self.client.set_config(self.gpu_id, {})
            pending = True
            if self.client.config(self.gpu_id):
                raise LactError("LACT did not apply default GPU values")
            self.client.pending("confirm")
            pending = False
            if self.client.config(self.gpu_id):
                raise LactError("LACT did not confirm default GPU values")
            forget_snapshot(self.host.settings, self.gpu_id)
            self._gpu_log("GPU-LACT: ausgewähltes GPU-Profil nach Bestätigung auf LACT-Standardwerte gesetzt")
            self.refresh()
            self.status.setText(self.tr("LACT-Standardwerte für diese GPU bestätigt."))
        except LactError as exc:
            if pending:
                try:
                    self.client.pending("revert")
                except LactError as rollback_error:
                    self._gpu_log(f"GPU-LACT-FEHLER: Rückstellung des fehlgeschlagenen Resets · {rollback_error}")
            self.status.setText(self.tr("GPU-Freigabe fehlgeschlagen: {reason}").format(reason=exc))
            self._gpu_log(f"GPU-LACT-FEHLER: LACT-Standardwerte nicht bestätigt · {exc}")
            self.refresh()
