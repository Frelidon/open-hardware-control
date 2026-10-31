# SPDX-License-Identifier: GPL-3.0-or-later
"""GPU fan-curve editor; LACT remains the only GPU fan writer."""
from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMenu, QPushButton, QSpinBox, QVBoxLayout, QWidget

from .fan_profile import (DEFAULT_SPEEDS, DEFAULT_TEMPERATURES, displayed_curve,
                          fan_curve_supported, proposed_fan_settings, proposed_static_fan_settings)
from .visuals import GpuFanCurvePreview, WrappedCheckBox


class GpuFanUiMixin:
    def _build_fan(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        workflow = QGroupBox("Lüfter sicher übernehmen")
        workflow.setObjectName("gpuWorkflowCard")
        self.fan_workflow_group = workflow
        workflow_layout = QVBoxLayout(workflow)
        self.fan_workflow_layout = workflow_layout
        self.fan_workflow_status = QLabel("1 · Kurve einstellen   →   2 · testen   →   3 · dauerhaft übernehmen")
        self.fan_workflow_status.setObjectName("gpuWorkflowStatus")
        self.fan_workflow_status.setWordWrap(True)
        workflow_layout.addWidget(self.fan_workflow_status)

        control_group = QGroupBox(self.tr("Lüftersteuerung"))
        control_group.setObjectName("gpuControlCard")
        self.fan_control_group = control_group
        controls = QVBoxLayout(control_group)
        self.owner_status = QLabel("GPU-Lüfterbesitz noch nicht geprüft.")
        self.owner_status.setWordWrap(True)
        controls.addWidget(self.owner_status)
        self.lact_fan = QCheckBox("LACT")
        self.lact_fan.setToolTip("GPU-Lüfter durch LACT steuern")
        self.lact_fan.toggled.connect(self._fan_toggle)
        controls.addWidget(self.lact_fan)
        mode_row = QGridLayout()
        self.fan_mode = QComboBox()
        self.fan_mode.setToolTip(self.tr("Lüftermodus"))
        self.fan_mode.addItem(self.tr("Lüfterkurve"), "curve")
        self.fan_mode.addItem(self.tr("Konstante Drehzahl"), "static")
        self.fan_mode.currentIndexChanged.connect(self._fan_toggle)
        mode_row.addWidget(self.fan_mode, 0, 0, 1, 2)
        self.fan_static_speed = QSpinBox()
        self.fan_static_speed.setObjectName("gpu_fan_static_speed")
        self.fan_static_speed.setRange(35, 100)
        self.fan_static_speed.setSuffix(" %")
        self.fan_static_speed.setValue(45)
        self.fan_static_speed.valueChanged.connect(self._invalidate_test)
        mode_row.addWidget(self.fan_static_speed, 1, 0)
        mode_row.setColumnStretch(1, 1)
        controls.addLayout(mode_row)

        presets = QHBoxLayout()
        for title, key, tooltip in ((self.tr("Leise"), "quiet", self.tr("Leise")),
                                    (self.tr("Normal"), "balanced", self.tr("Ausgeglichen")),
                                    ("Max.", "performance", self.tr("Leistung"))):
            button = QPushButton(title)
            button.setToolTip(tooltip)
            button.setMinimumWidth(button.sizeHint().width())
            button.clicked.connect(lambda _checked=False, preset=key: self._apply_fan_preset(preset))
            presets.addWidget(button, 1)
        controls.addLayout(presets)

        curve = QWidget()
        grid = QGridLayout(curve)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.addWidget(QLabel(self.tr("Temperatur")), 0, 0)
        grid.addWidget(QLabel(self.tr("Drehzahl")), 0, 1)
        self.fan_points = []
        for index, (temp, speed) in enumerate(zip(DEFAULT_TEMPERATURES, DEFAULT_SPEEDS), start=1):
            temperature = QSpinBox()
            temperature.setObjectName("gpuFanSpin")
            temperature.setRange(25, 100)
            temperature.setSuffix(" °C")
            temperature.setValue(temp)
            percent = QSpinBox()
            percent.setObjectName("gpuFanSpin")
            percent.setRange(35, 100)
            percent.setSuffix(" %")
            percent.setValue(speed)
            temperature.valueChanged.connect(self._invalidate_test)
            percent.valueChanged.connect(self._invalidate_test)
            self.fan_points.append((temperature, percent))
            grid.addWidget(temperature, index, 0)
            grid.addWidget(percent, index, 1)
        grid.setColumnStretch(2, 1)
        self.fan_curve_editor = curve
        note = QLabel(
            "Wenn CoolerControl läuft, muss der GPU-Lüfter dort auf „Unmanaged“ stehen. Gehäuselüfter können weiter bei CoolerControl bleiben. Jede LACT-Lüfterübernahme durchläuft denselben Kurztest wie das Tuning."
        )
        note.setWordWrap(True)

        check = QPushButton("Besitz erneut prüfen")
        check.clicked.connect(self.refresh_ownership_async)
        open_cc = QPushButton("CoolerControl öffnen")
        open_cc.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("http://127.0.0.1:11987")))
        self.free_fan_button = QPushButton("GPU-Lüfter freigeben")
        self.free_fan_button.clicked.connect(self.release_gpu_fan)
        to_cc = QPushButton("GPU-Lüfter an CoolerControl übergeben")
        to_cc.clicked.connect(self.handoff_to_coolercontrol)
        ownership_menu_button = QPushButton(self.tr("Lüftersteuerung"))
        ownership_menu = QMenu(ownership_menu_button)
        ownership_menu.addAction(check.text(), self.refresh_ownership_async)
        ownership_menu.addAction(open_cc.text(), open_cc.click)
        self.free_fan_action = ownership_menu.addAction(self.free_fan_button.text(), self.free_fan_button.click)
        ownership_menu.addAction(to_cc.text(), to_cc.click)
        ownership_menu_button.setMenu(ownership_menu)
        controls.addWidget(ownership_menu_button)

        preview_group = QGroupBox(self.tr("Lüfterkurve") + " · " + self.tr("Live-Vorschau"))
        preview_group.setObjectName("gpuPreviewCard")
        preview_box = QVBoxLayout(preview_group)
        self.fan_edit_hint = QLabel()
        self.fan_edit_hint.setObjectName("warningText")
        self.fan_edit_hint.setWordWrap(True)
        preview_box.addWidget(self.fan_edit_hint)
        preview_layout = QHBoxLayout()
        self.fan_visual = GpuFanCurvePreview(
            lambda: tuple((temperature.value(), speed.value())
                          for temperature, speed in self.fan_points),
            lambda: self.fan_static_speed.value() if self.fan_mode.currentData() == "static"
            else round(sum(speed.value() for _temperature, speed in self.fan_points) / len(self.fan_points)),
            set_point=self._set_fan_curve_point,
            editable=lambda: bool(self.lact_fan.isChecked() and self.fan_mode.currentData() == "curve"),
            temperature=self._fan_live_temperature,
            rpm=self._fan_live_rpm,
            locked_text=lambda: "",
        )
        preview_layout.addWidget(self.fan_visual, 3)
        preview_layout.addWidget(curve, 2)
        preview_box.addLayout(preview_layout)

        self.fan_test_button = QPushButton(self.tr("Test"))
        self.fan_test_button.setToolTip(self.tr("GPU-Lüfter mit LACT testen"))
        self.fan_test_button.setObjectName("gpuCommitAction")
        self.fan_test_button.setMinimumHeight(44)
        self.fan_test_button.clicked.connect(self.prepare_lact_fan)
        self.fan_test_apply_button = QPushButton(self.tr("Testen + anwenden"))
        self.fan_test_apply_button.setObjectName("gpuPrimaryAction")
        self.fan_test_apply_button.setMinimumHeight(48)
        self.fan_test_apply_button.clicked.connect(self.prepare_lact_fan_and_persist)
        self.fan_workflow_layout.addWidget(self.fan_test_apply_button)
        self.fan_apply_button = QPushButton(self.tr("Speichern"))
        self.fan_apply_button.setToolTip(self.tr("Getestete Änderung dauerhaft speichern"))
        self.fan_apply_button.setObjectName("gpuPrimaryAction")
        self.fan_apply_button.setMinimumHeight(44)
        self.fan_apply_button.clicked.connect(self.save_tested)
        self.fan_apply_button.setEnabled(False)
        self.fan_persist_after_test = WrappedCheckBox(
            self.tr("Nach bestandenem Test dauerhaft in LACT speichern")
        )
        self.fan_persist_after_test.setToolTip(self.tr(
            "Aus: LACT stellt den Test automatisch zurück. Ein: Nur ein bestätigter reiner Lüftertest wird anschließend dauerhaft gespeichert."
        ))
        self.fan_persist_after_test.setChecked(False)
        workflow_actions = QHBoxLayout()
        workflow_actions.addWidget(self.fan_test_button)
        workflow_actions.addWidget(self.fan_apply_button)
        self.fan_workflow_layout.addLayout(workflow_actions)
        self.fan_workflow_layout.addWidget(self.fan_persist_after_test)
        note.setToolTip(note.text())
        note.setText(self.tr("CoolerControl: GPU-Lüfter muss dort „Unmanaged“ sein."))
        controls.addWidget(note)
        self.fan_top_grid = QGridLayout()
        self.fan_top_grid.setSpacing(8)
        self.fan_top_grid.addWidget(workflow, 0, 0)
        self.fan_top_grid.addWidget(control_group, 0, 1)
        layout.addLayout(self.fan_top_grid)
        layout.addWidget(preview_group)
        self.fan_page = page
        self.sections.addTab(page, "Lüfter")
        self._fan_toggle(False)

    def _layout_fan_controls(self) -> None:
        """Keep complete labels reachable when the cockpit column is narrow."""
        grid = self.fan_top_grid
        while grid.count():
            grid.takeAt(0)
        stacked = self.fan_page.width() < 540
        grid.addWidget(self.fan_workflow_group, 0, 0)
        grid.addWidget(self.fan_control_group, 1 if stacked else 0, 0 if stacked else 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 0 if stacked else 1)

    def _set_fan_curve_point(self, index: int, temperature: int, speed: int) -> None:
        if not 0 <= index < len(self.fan_points):
            return
        temperature_box, speed_box = self.fan_points[index]
        temperature_box.setValue(temperature)
        speed_box.setValue(speed)

    def _apply_fan_preset(self, preset: str) -> None:
        curves = {
            "quiet": ((40, 35), (50, 35), (60, 45), (72, 65), (85, 95)),
            "balanced": tuple(zip(DEFAULT_TEMPERATURES, DEFAULT_SPEEDS)),
            "performance": ((35, 45), (45, 55), (55, 70), (65, 85), (75, 100)),
        }
        points = curves.get(preset)
        if points is None:
            return
        if not self.lact_fan.isChecked():
            self.lact_fan.setChecked(True)
        self.fan_mode.setCurrentIndex(max(0, self.fan_mode.findData("curve")))
        for (temperature_box, speed_box), (temperature, speed) in zip(self.fan_points, points):
            temperature_box.setValue(temperature)
            speed_box.setValue(speed)
        self.fan_visual.update()

    def _update_fan_workflow(self) -> None:
        label = getattr(self, "fan_workflow_status", None)
        if label is None:
            return
        changes = self._fan_changes()
        fan_candidate = bool(self.candidate and self.baseline and (
            self.candidate.get("fan_control_enabled") != self.baseline.get("fan_control_enabled")
            or self.candidate.get("fan_control_settings") != self.baseline.get("fan_control_settings")
        ))
        if self.preview_active:
            text = "2/3 · Lüftertest läuft · LACT stellt bei einem Fehler automatisch zurück"
        elif self.tested and fan_candidate:
            text = "✓ Test bestanden · 3/3 jetzt dauerhaft übernehmen oder Entwurf ändern"
        elif changes:
            text = "1/3 · Entwurf bereit · nur testen oder direkt „Testen + übernehmen“ wählen"
        elif self.baseline and self.baseline.get("fan_control_enabled"):
            text = "✓ LACT-Lüftersteuerung aktiv · Änderungen beginnen wieder als sicherer Entwurf"
        else:
            text = "1/3 · LACT-Steuerung aktivieren und Kurve oder konstante Drehzahl einstellen"
        label.setText(self.tr(text))

    def _fan_toggle(self, _checked: bool) -> None:
        enabled = self.lact_fan.isEnabled() and self.lact_fan.isChecked()
        self.fan_mode.setEnabled(enabled)
        self.fan_curve_editor.setEnabled(enabled and self.fan_mode.currentData() == "curve")
        self.fan_static_speed.setEnabled(enabled and self.fan_mode.currentData() == "static")
        if hasattr(self, "fan_visual"):
            self.fan_visual.update()
        if hasattr(self, "fan_edit_hint"):
            self.fan_edit_hint.setText(self._fan_curve_locked_text())
            self.fan_edit_hint.setObjectName(
                "infoText" if enabled and self.fan_mode.currentData() == "curve" else "warningText"
            )
            self.fan_edit_hint.style().unpolish(self.fan_edit_hint)
            self.fan_edit_hint.style().polish(self.fan_edit_hint)
        self._invalidate_test()

    @staticmethod
    def _live_number(value: object) -> float | None:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        if isinstance(value, dict):
            current = value.get("current")
            if isinstance(current, (int, float)) and not isinstance(current, bool):
                return float(current)
        return None

    def _fan_live_temperature(self) -> float | None:
        stats = self.stats if isinstance(getattr(self, "stats", None), dict) else {}
        temps = stats.get("temps") if isinstance(stats.get("temps"), dict) else {}
        return self._live_number(temps.get("edge"))

    def _fan_live_rpm(self) -> float | None:
        stats = self.stats if isinstance(getattr(self, "stats", None), dict) else {}
        fan = stats.get("fan") if isinstance(stats.get("fan"), dict) else {}
        return self._live_number(fan.get("speed_current"))

    def _fan_curve_locked_text(self) -> str:
        if not self.lact_fan.isEnabled():
            return self.tr("LACT meldet keine bearbeitbare GPU-Lüfterkurve.")
        if not self.lact_fan.isChecked():
            return self.tr("Oben zuerst LACT aktivieren. Danach lassen sich die Punkte direkt ziehen.")
        if self.fan_mode.currentData() != "curve":
            return self.tr("Oben Lüfterkurve wählen, um die Punkte zu bearbeiten.")
        return self.tr("Kurvenpunkte direkt ziehen oder Temperatur und Drehzahl rechts exakt einstellen.")

    def _populate_fan_controls(self) -> None:
        baseline = self.baseline or {}
        supported = fan_curve_supported(self.stats)
        self.lact_fan.setEnabled(supported)
        fan = self.stats.get("fan") if isinstance(self.stats.get("fan"), dict) else {}
        reported = fan.get("temperature_range")
        lower, upper = (int(reported[0]), int(reported[1])) if supported else (25, 100)
        for (temperature, percent), (temp, speed) in zip(self.fan_points, displayed_curve(baseline, self.stats)):
            temperature.setRange(lower, upper)
            temperature.setValue(temp)
            percent.setValue(speed)
        settings = baseline.get("fan_control_settings")
        mode = settings.get("mode") if isinstance(settings, dict) else "curve"
        index = self.fan_mode.findData(mode)
        self.fan_mode.setCurrentIndex(index if index >= 0 else 0)
        speed = settings.get("static_speed") if isinstance(settings, dict) else None
        self.fan_static_speed.setValue(round(float(speed) * 100) if isinstance(speed, (int, float)) else 45)
        self.lact_fan.setChecked(bool(baseline.get("fan_control_enabled")))
        self._fan_toggle(self.lact_fan.isChecked())
        self.free_fan_button.setEnabled(bool(self.gpu_id))

    def _fan_changes(self) -> dict[str, object]:
        if self.baseline is None or not self.lact_fan.isEnabled():
            return {}
        enabled = self.lact_fan.isChecked()
        result: dict[str, object] = {}
        if enabled != bool(self.baseline.get("fan_control_enabled")):
            result["fan_control_enabled"] = enabled
        if enabled:
            if self.fan_mode.currentData() == "static":
                requested: object = {"mode": "static", "speed": self.fan_static_speed.value()}
                try:
                    candidate = proposed_static_fan_settings(self.baseline, self.fan_static_speed.value(), self.stats)
                except ValueError:
                    candidate = None
            else:
                requested = tuple((temperature.value(), speed.value())
                                  for temperature, speed in self.fan_points)
                try:
                    candidate = proposed_fan_settings(self.baseline, requested, self.stats)
                except ValueError:
                    candidate = None
            if candidate is None or candidate != self.baseline.get("fan_control_settings"):
                result["fan_control_settings"] = requested
        return result

    def prepare_lact_fan(self) -> None:
        if not self.refresh_ownership():
            self.status.setText(self.tr("GPU-Lüfter in CoolerControl zuerst auf „Unmanaged“ stellen und erneut prüfen."))
            return
        if not self.lact_fan.isEnabled():
            self.status.setText(self.tr("Lüfterkurve") + " · " + self.tr("Nicht verfügbar"))
            return
        self.sections.setCurrentIndex(1)
        if not self.lact_fan.isChecked():
            self.lact_fan.setChecked(True)
        if not self._fan_changes():
            self.status.setText(self.tr("GPU-Lüfterwert ist bereits in LACT aktiv."))
            return
        self.start_preview()

    def prepare_lact_fan_and_persist(self) -> None:
        """One explicit action: trial first, commit only after verified response."""
        self.fan_persist_after_test.setChecked(True)
        self.prepare_lact_fan()
        if not self.preview_active:
            self.fan_persist_after_test.setChecked(False)
