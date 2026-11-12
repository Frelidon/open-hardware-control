# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit unlock of GPU power limits above LACT's device default."""
from __future__ import annotations

import math

from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .power_policy import power_cap_allowed, reported_power_bounds
from .visuals import WrappedCheckBox


class GpuPowerUiMixin:
    def _build_power_guard(self, form) -> None:
        self.power_unlock_confirmed = False
        self.power_unlock = WrappedCheckBox(self.tr("Leistungslimit über LACT-Standard freischalten"))
        self.power_unlock.toggled.connect(self._power_unlock_toggled)
        self.power_default_note = QLabel()
        self.power_default_note.setWordWrap(True)
        guard = QWidget()
        row = QVBoxLayout(guard)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(self.power_unlock)
        row.addWidget(self.power_default_note, 1)
        form.addRow(guard)
        self.power_unlock_panel = QWidget()
        confirmation = QVBoxLayout(self.power_unlock_panel)
        confirmation.setContentsMargins(18, 6, 0, 8)
        self.power_unlock_warning = QLabel()
        self.power_unlock_warning.setObjectName("warningText")
        self.power_unlock_warning.setWordWrap(True)
        confirmation.addWidget(self.power_unlock_warning)
        actions = QHBoxLayout()
        self.power_unlock_confirm = QPushButton(self.tr("Freischaltung bestätigen"))
        self.power_unlock_confirm.setObjectName("dangerAction")
        self.power_unlock_confirm.clicked.connect(self._confirm_power_unlock)
        cancel = QPushButton(self.tr("Abbrechen"))
        cancel.clicked.connect(self._cancel_power_unlock)
        actions.addWidget(self.power_unlock_confirm)
        actions.addWidget(cancel)
        actions.addStretch()
        confirmation.addLayout(actions)
        self.power_unlock_panel.hide()
        form.addRow(self.power_unlock_panel)

    def _populate_power_controls(self, *, preserve_input: bool = False) -> None:
        bounds = reported_power_bounds(self.stats)
        allowed = self.overdrive_enabled is True and bounds is not None
        self.power.setEnabled(allowed)
        self.power_unlock.setEnabled(bool(allowed and bounds.maximum > bounds.factory))
        if bounds is None:
            self.power_unlock_panel.hide()
            self.power_default_note.setText(self.tr("LACT meldet kein gültiges Standard-Leistungslimit."))
            return
        active = self.baseline.get("power_cap") or self.stats["power"].get("cap_current") or bounds.factory
        if isinstance(active, bool) or not isinstance(active, (int, float)) or not math.isfinite(active):
            active = bounds.factory
        current = self.power.value() if preserve_input else active
        note = self.tr("LACT-Standard: {watts} W. Höhere Limits benötigen eine Freischaltung.").format(
            watts=f"{bounds.factory:g}")
        if not self.power_unlock.isChecked() and float(active) > bounds.factory:
            note += " " + self.tr("In LACT aktiv: {watts} W; der Standardwert ist erst nach Test und Speichern aktiv.").format(
                watts=f"{float(active):g}")
        self.power_default_note.setText(note)
        self.power_default_note.setToolTip(note)
        self.power.setRange(bounds.minimum, bounds.maximum if self.power_unlock.isChecked() else bounds.factory)
        self.power.setValue(float(current))

    def _power_unlock_toggled(self, enabled: bool) -> None:
        if enabled and not self.power_unlock_confirmed:
            bounds = reported_power_bounds(self.stats)
            self.power_unlock.blockSignals(True)
            self.power_unlock.setChecked(False)
            self.power_unlock.blockSignals(False)
            if bounds is not None:
                self.power_unlock_warning.setText(self.tr(
                    "Ein höheres GPU-Leistungslimit erhöht die elektrische und thermische Last. "
                    "LACT-Standard: {watts} W. Erst nach Prüfung der Stromversorgung bestätigen."
                ).format(watts=f"{bounds.factory:g}"))
                self.power_unlock_panel.show()
        elif not enabled:
            self.power_unlock_confirmed = False
            self.power_unlock_panel.hide()
        self._populate_power_controls(preserve_input=True)
        if hasattr(self, "_sync_tuning_sliders"):
            self._sync_tuning_sliders()
        self._invalidate_test()

    def _confirm_power_unlock(self) -> None:
        if reported_power_bounds(self.stats) is None:
            self._cancel_power_unlock()
            return
        self.power_unlock_confirmed = True
        self.power_unlock_panel.hide()
        self.power_unlock.blockSignals(True)
        self.power_unlock.setChecked(True)
        self.power_unlock.blockSignals(False)
        self._populate_power_controls(preserve_input=True)
        if hasattr(self, "_sync_tuning_sliders"):
            self._sync_tuning_sliders()
        self._invalidate_test()

    def _cancel_power_unlock(self) -> None:
        self.power_unlock_confirmed = False
        self.power_unlock_panel.hide()
        self.power_unlock.blockSignals(True)
        self.power_unlock.setChecked(False)
        self.power_unlock.blockSignals(False)
        self._populate_power_controls(preserve_input=True)
        if hasattr(self, "_sync_tuning_sliders"):
            self._sync_tuning_sliders()
        self._invalidate_test()

    def _power_change(self) -> dict[str, float]:
        if self.baseline is None or not self.power.isEnabled():
            return {}
        power = self.stats.get("power") if isinstance(self.stats.get("power"), dict) else {}
        current = self.baseline.get("power_cap") or power.get("cap_current")
        if not isinstance(current, (int, float)) or abs(self.power.value() - current) < .05:
            return {}
        bounds = reported_power_bounds(self.stats)
        if power_cap_allowed(self.power.value(), bounds, unlocked=self.power_unlock.isChecked()):
            return {"power_cap": self.power.value()}
        return {}

    def _power_candidate_allowed(self, candidate: dict) -> bool:
        cap = candidate.get("power_cap")
        if cap is None:
            return True
        return power_cap_allowed(cap, reported_power_bounds(self.stats),
                                 unlocked=self.power_unlock.isChecked())
