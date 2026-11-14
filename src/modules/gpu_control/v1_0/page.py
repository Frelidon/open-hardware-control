# SPDX-License-Identifier: GPL-3.0-or-later
"""GPU page: LACT discovery, bounded preview, explicit commit and ownership."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import time
from typing import Any

from PySide6.QtCore import QProcess, QProcessEnvironment, QTimer, QUrl, Qt
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QMenu, QMessageBox, QPushButton, QScrollArea, QSlider, QSpinBox, QTabWidget,
    QVBoxLayout, QWidget, QLayout,
)

from .client import LactClient, LactError, clock_controls, config_equivalent, healthy_stats, proposed_config
from .diagnostics_ui import GpuDiagnosticsUiMixin
from .dashboard_ui import GpuDashboardUiMixin
from .fan_ui import GpuFanUiMixin
from .fan_profile import fan_preview_verified
from .ownership import coolercontrol_gpu_claim
from .power_ui import GpuPowerUiMixin
from .profile_ui import GpuProfileUiMixin
from .reset_ui import GpuResetUiMixin
from .read_ui import GpuReadUiMixin
from .cockpit_ui import GpuCockpitUiMixin
from .read_worker import read_device
from .read_status import set_state
from .snapshot import forget_snapshot, read_snapshot, write_snapshot
from .stress import benchmark_command, benchmark_gpu_environment
from .stress_ui import GpuStressUiMixin
from .tables import GpuTableMixin
from .workspace_layout import WorkspaceSections


def fan_preview_change_requested(changes: dict[str, Any]) -> bool:
    """Return whether a preview must verify physical fan response."""
    return bool({"fan_control_settings", "fan_control_enabled"} & set(changes))


def fan_only_change_requested(changes: dict[str, Any]) -> bool:
    """Allow automatic persistence only when no tuning field is mixed in."""
    fields = set(changes)
    return bool(fields) and fields <= {"fan_control_settings", "fan_control_enabled"}


def preview_requires_graphics_load(changes: dict[str, Any]) -> bool:
    """Only tuning fields authorize a graphics helper during the short trial."""
    return bool(set(changes) & {
        "power_cap", "max_core_clock", "max_memory_clock", "gpu_clock_offset_0",
    })


class GpuControlPage(GpuCockpitUiMixin, GpuReadUiMixin, GpuDashboardUiMixin, GpuTableMixin, GpuPowerUiMixin, GpuFanUiMixin, GpuStressUiMixin, GpuProfileUiMixin,
                     GpuResetUiMixin, GpuDiagnosticsUiMixin, QScrollArea):
    """No automatic GPU write occurs when this page is shown or refreshed."""

    def __init__(self, host: QWidget):
        super().__init__(host)
        self.host = host
        self.client = LactClient()
        self._init_gpu_reads()
        self.gpu_id = ""
        self.baseline: dict[str, Any] | None = None
        self.stats: dict[str, Any] = {}
        self.clocks: dict[str, Any] = {}
        self.overdrive_enabled: bool | None = None
        self.gpu_vendor = ""
        self.candidate: dict[str, Any] | None = None
        self.tested = False
        self.preview_active = False
        self.load_process: QProcess | None = None
        self.overdrive_process: QProcess | None = None
        self.overdrive_prepared = False
        self.preview_deadline = 0.0
        self.preview_peak_load = 0.0
        self.preview_needs_load = False
        self.preview_fan_test = False
        self.preview_fan_only_changes = False
        self.preview_fan_initial_rpm = 0
        self.preview_fan_peak_rpm = 0
        self.preview_fan_pwm_seen = False
        self.benchmark_install_active = False
        self.preview_timer = QTimer(self)
        self.preview_timer.setInterval(400)
        self.preview_timer.timeout.connect(self._sample_preview)
        self.setWidgetResizable(True)
        self.setFrameShape(self.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        content = QWidget()
        content.setMaximumWidth(1800)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 10, 14, 12)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self._build_gpu_dashboard(layout)
        self.status = QLabel("LACT wird erst beim Öffnen dieser Seite abgefragt.")
        self.status.setObjectName("muted")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        toolbar = self.gpu_toolbar = QWidget()
        toolbar.setObjectName("gpuToolbar")
        bar = QGridLayout(toolbar)
        bar.setContentsMargins(12, 10, 12, 10)
        bar.setHorizontalSpacing(10)
        bar.setVerticalSpacing(8)
        self.gpu_toolbar_layout = bar
        self.devices = QComboBox()
        self.devices.currentIndexChanged.connect(self._select_device)
        self.refresh_button = QPushButton("GPU und LACT aktualisieren")
        self.refresh_button.clicked.connect(self.refresh)
        self.install_button = QPushButton("LACT für GPU-Tuning installieren oder aktualisieren")
        self.install_button.clicked.connect(self.install_lact)
        self.open_lact_button = QPushButton(self.tr("LACT öffnen"))
        self.open_lact_button.clicked.connect(self.open_lact)
        self.overdrive_button = QPushButton(self.tr("AMD-Overdrive vorbereiten"))
        self.overdrive_button.clicked.connect(self.prepare_overdrive)
        self.overdrive_button.setEnabled(False)
        bar.addWidget(self.devices, 0, 0, 1, 2)
        bar.addWidget(self.refresh_button, 0, 2)
        bar.addWidget(self.open_lact_button, 0, 3)
        bar.addWidget(self.install_button, 0, 4)
        bar.addWidget(self.overdrive_button, 0, 5)
        bar.setColumnStretch(0, 1)
        bar.setColumnStretch(1, 1)
        layout.addWidget(toolbar)

        self.sections = WorkspaceSections(self)
        self.sections.setObjectName("gpuSections")
        layout.addWidget(self.sections)
        self._build_tuning()
        self._build_fan()
        self._build_stress()
        self._build_profiles()
        self._build_metrics()
        self._build_hardware()
        self._build_diagnostics()
        self._assemble_control_cockpit()
        self.setWidget(content)
        self._sync_buttons()

    def tr(self, source: str) -> str:
        return self.host.tr_static(source)


    def showEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().showEvent(event)
        if not self.devices.count():
            QTimer.singleShot(0, self, self.refresh)

    def refresh(self) -> None:
        if self.preview_active or getattr(self, "stress_process", None) is not None:
            return
        self.refresh_rgb_lighting_inventory()
        set_state(self, "loading")
        if self._request_gpu_read("inventory"):
            self.baseline = None
            self.overdrive_enabled = None
            self._sync_buttons()
            return
        try:
            rows = self.client.devices()
        except LactError as exc:
            self._gpu_read_failed("inventory", str(exc))
            return
        self._populate_gpu_devices(rows)

    def _select_device(self, _index: int = -1) -> None:
        if getattr(self, "stress_process", None) is not None:
            return
        gpu_id = str(self.devices.currentData() or "")
        self.gpu_id = gpu_id
        self.tuning_gpu_name.setText(self.devices.currentText() or self.tr("Grafikkarte"))
        self.stats = {}
        self._refresh_gpu_dashboard()
        vendor_id = gpu_id.split(":", 1)[0].casefold()
        self.gpu_vendor = "AMD" if vendor_id == "1002" else "NVIDIA" if vendor_id == "10de" else ""
        self._update_tuning_artwork()
        self.baseline = None
        self.clocks = {}
        self.overdrive_enabled = None
        self.candidate = None
        self.tested = False
        self.power_unlock.blockSignals(True)
        self.power_unlock.setChecked(False)
        self.power_unlock.blockSignals(False)
        self.power_unlock_confirmed = False
        self.power_unlock_panel.hide()
        for widget in (self.power, self.core, self.memory, self.offset, self.lact_fan):
            widget.setEnabled(False)
        self._sync_tuning_sliders()
        self.free_fan_button.setEnabled(False)
        if not gpu_id:
            set_state(self, "empty")
            self.status.setText(self.tr("LACT meldet keine Grafikkarte."))
            self._sync_buttons()
            return
        if self._request_gpu_read("device", gpu_id):
            self._sync_buttons()
            return
        set_state(self, "loading")
        try:
            self._apply_gpu_read(read_device(self.client, gpu_id, ownership_reader=coolercontrol_gpu_claim))
        except LactError as exc:
            self._gpu_read_failed("device", str(exc))
            self._refresh_gpu_dashboard()
        self._sync_buttons()

    def refresh_rgb_lighting_inventory(self) -> None:
        """Use OpenRGB's own GPU classification, independent of LACT tuning."""
        self.rgb_devices.clear()
        for device in getattr(self.host, "openrgb_devices", ()):
            if str(getattr(device, "device_type", "")).casefold() != "gpu":
                continue
            mode = "Direct" if device.supports_direct else self.tr("Automatisch: native GPU-Hardwareeffekte")
            self.rgb_devices.addItem(f"{device.name} · {mode}", device.index)
        if not self.rgb_devices.count():
            self.rgb_devices.addItem(self.tr("Keine OpenRGB-Grafikkarte erkannt."), None)

    def open_rgb_lighting(self) -> None:
        index = self.rgb_devices.currentData()
        self.host.tabs.setCurrentIndex(2)
        if index is None:
            return
        device = next((row for row in getattr(self.host, "openrgb_devices", ())
                       if row.index == index and row.device_type.casefold() == "gpu"), None)
        if device is not None:
            self.host.configure_gpu_lighting(device)

    def _populate_controls(self) -> None:
        if self.baseline is None:
            return
        self._populate_power_controls()
        controls = clock_controls(self.baseline, self.clocks)
        for field, widget in (("max_core_clock", self.core), ("max_memory_clock", self.memory),
                              ("gpu_clock_offset_0", self.offset)):
            control = controls.get(field)
            widget.setEnabled(self.overdrive_enabled is True and control is not None)
            if control is not None:
                widget.setRange(control[1], control[2])
                widget.setValue(control[0])
            else:
                widget.setValue(0)
        self.core.setToolTip(self.tr("RDNA4 meldet keinen direkten GPU-Maximaltakt. Nutze den GPU-Taktversatz."))
        self.tuning_note.setText(
            self.tuning_base_note + ("\n" + self.core.toolTip()
                                     if "gpu_clock_offset_0" in controls and "max_core_clock" not in controls else "")
        )
        self._populate_fan_controls()
        self._sync_tuning_sliders()

    def refresh_ownership(self) -> bool:
        claimed, reason = coolercontrol_gpu_claim()
        self._display_gpu_ownership(claimed, reason)
        return not claimed

    def _display_gpu_ownership(self, claimed: bool, reason: str) -> None:
        if claimed:
            self.owner_status.setText(self.tr("CoolerControl steuert möglicherweise den GPU-Lüfter: {reason}. In CoolerControl auf „Unmanaged“ stellen und erneut prüfen.").format(reason=reason))
        elif reason == "CoolerControl service is inactive":
            self.owner_status.setText(self.tr("CoolerControl ist aus; kein GPU-Lüfterkonflikt."))
        else:
            self.owner_status.setText(self.tr("GPU-Lüfter für LACT frei: {reason}").format(reason=reason))
        self._sync_buttons()

    def _changes(self) -> dict[str, Any]:
        if self.baseline is None:
            return {}
        result: dict[str, Any] = {}
        result.update(self._power_change())
        controls = clock_controls(self.baseline, self.clocks)
        for field, widget in (("max_core_clock", self.core), ("max_memory_clock", self.memory)):
            if widget.isEnabled() and field in controls and widget.value() != controls[field][0]:
                result[field] = widget.value()
        old_offset = controls.get("gpu_clock_offset_0")
        if self.offset.isEnabled() and old_offset is not None and self.offset.value() != old_offset[0]:
            result["gpu_clock_offset_0"] = self.offset.value()
        result.update(self._fan_changes())
        return result

    def _invalidate_test(self, *_args) -> None:
        self.tested = False
        self.candidate = None
        self._sync_buttons()

    def _sync_buttons(self) -> None:
        stress_active = getattr(self, "stress_process", None) is not None
        write_allowed = self._write_allowed()
        ready = bool(write_allowed and self.gpu_id and self.baseline is not None and self.overdrive_enabled is True
                     and not self.preview_active and not stress_active)
        self.overdrive_button.setEnabled(bool(write_allowed and self.gpu_vendor != "NVIDIA" and self.gpu_id and self.overdrive_enabled is False
                                              and self.overdrive_process is None and not self.overdrive_prepared))
        self.test_button.setEnabled(ready and bool(self._changes()))
        self.save_button.setEnabled(ready and self.tested and self.candidate is not None)
        if hasattr(self, "power_unlock"):
            self.power_unlock.setEnabled(ready and self.power.isEnabled())
        snapshot = read_snapshot(self.host.settings, self.gpu_id) if self.gpu_id else None
        self.release_button.setEnabled(bool(write_allowed and self.gpu_id and self.baseline is not None and snapshot
                                            and not self.preview_active and not stress_active))
        self.release_button.setToolTip(self.tr("Nur für zuvor in OHC gespeicherte GPU-Werte."))
        self.discard_button.setEnabled(ready and bool(self._changes()))
        self.factory_button.setEnabled(bool(write_allowed and self.gpu_id and self.baseline and not self.preview_active
                                            and not stress_active))
        for action_name, button in (
            ("discard_menu_action", self.discard_button),
            ("release_menu_action", self.release_button),
            ("factory_menu_action", self.factory_button),
        ):
            action = getattr(self, action_name, None)
            if action is not None:
                action.setEnabled(button.isEnabled())
        if hasattr(self, "free_fan_button"):
            self.free_fan_button.setEnabled(bool(write_allowed and self.gpu_id and not self.preview_active and not stress_active))
            if hasattr(self, "free_fan_action"):
                self.free_fan_action.setEnabled(self.free_fan_button.isEnabled())
            fan_changes = fan_only_change_requested(self._changes())
            self.fan_test_button.setEnabled(bool(ready and self.lact_fan.isEnabled() and fan_changes))
            self.fan_test_apply_button.setEnabled(bool(ready and self.lact_fan.isEnabled() and fan_changes))
            self.fan_persist_after_test.setEnabled(bool(
                ready and fan_changes
            ))
            fan_candidate = bool(self.candidate and self.baseline and (
                self.candidate.get("fan_control_enabled") != self.baseline.get("fan_control_enabled")
                or self.candidate.get("fan_control_settings") != self.baseline.get("fan_control_settings")
            ))
            self.fan_apply_button.setEnabled(bool(ready and self.tested and fan_candidate))
            self._update_fan_workflow()
        self.preview_cancel.setEnabled(self.preview_active)
        self.preview_install.setEnabled(not self.benchmark_install_active and not self.preview_active)
        if hasattr(self, "install_menu_action"):
            self.install_menu_action.setEnabled(self.preview_install.isEnabled())
        if hasattr(self, "stress_button"):
            self.stress_button.setEnabled(bool(self.gpu_id and self.baseline is not None
                                               and not self.preview_active and not stress_active))
            self.stress_duration.setEnabled(not stress_active)
            self.stress_size.setEnabled(not stress_active)
            self.stress_presentation.setEnabled(not stress_active)
            self.devices.setEnabled(not stress_active)
            self.refresh_button.setEnabled(not stress_active)

    def _load_helper(self) -> tuple[str, list[str]]:
        available = {key: shutil.which(key) or "" for key in ("vkmark", "glmark2")}
        return benchmark_command(available)

    def start_preview(self) -> None:
        if not self._write_allowed():
            return
        if self.preview_active or getattr(self, "stress_process", None) is not None or self.baseline is None or not self.gpu_id:
            return
        if self.overdrive_enabled is not True:
            self.status.setText(self.tr("AMD-Overdrive ist aus. In LACT aktivieren, neu starten und hier aktualisieren."))
            return
        if not self.refresh_ownership():
            self.status.setText(self.tr("Kurztest gesperrt: GPU-Lüfterbesitz bei CoolerControl nicht freigegeben."))
            return
        pending_write = False
        try:
            changes = self._changes()
            self.preview_needs_load = preview_requires_graphics_load(changes)
            executable, arguments = "", []
            selected: dict[str, str] = {}
            if not fan_only_change_requested(changes):
                executable, arguments = self._load_helper()
                if not executable:
                    message = self.tr("vkmark oder glmark2 fehlt. Installiere vkmark für den Lasttest.")
                    self.status.setText(message)
                    self.stress_status.setText(message)
                    self._gpu_log("GPU-LACT: Last-Kurztest wartet auf vkmark oder glmark2; Installation angeboten")
                    self.install_stress_tool()
                    return
                try:
                    selected = benchmark_gpu_environment(self.gpu_id, executable)
                except ValueError as exc:
                    raise LactError(str(exc)) from exc
            candidate = proposed_config(self.baseline, changes, self.stats, self.clocks)
            if not self._power_candidate_allowed(candidate):
                raise LactError("GPU power limit exceeds locked LACT device default")
            if self.client.config(self.gpu_id) != self.baseline:
                raise LactError("GPU settings changed outside OHC; refresh first")
            self._gpu_log(f"GPU-LACT: Kurztest angefordert · Felder={','.join(sorted(changes))}"
                          f" · Lüftermodus={self.fan_mode.currentData()}"
                          f" · Soll={self.fan_static_speed.value()} %")
            self.preview_fan_test = fan_preview_change_requested(changes)
            self.preview_fan_only_changes = fan_only_change_requested(changes)
            self.preview_fan_initial_rpm = 0
            self.preview_fan_peak_rpm = 0
            self.preview_fan_pwm_seen = False
            if self.preview_fan_test:
                before = self.client.stats(self.gpu_id)
                self.record_fan_sample(before, "vor Kurztest")
                fan_before = before.get("fan") if isinstance(before.get("fan"), dict) else {}
                initial_rpm = fan_before.get("speed_current")
                if isinstance(initial_rpm, (int, float)) and not isinstance(initial_rpm, bool):
                    self.preview_fan_initial_rpm = max(0, int(initial_rpm))
            seconds = self.client.set_config(self.gpu_id, candidate)
            pending_write = True
            self.preview_deadline = time.monotonic() + seconds
            if seconds < 4.0:
                raise LactError("LACT rollback window is too short for the protected test")
            if not config_equivalent(candidate, self.client.config(self.gpu_id)):
                raise LactError("LACT did not apply the trial GPU settings")
            self.candidate = candidate
            self.preview_active = True
            self.tested = False
            self.preview_peak_load = 0.0
            if self.preview_needs_load:
                self.load_process = QProcess(self)
                self.load_process.setStandardOutputFile(QProcess.nullDevice())
                self.load_process.setStandardErrorFile(QProcess.nullDevice())
                environment = QProcessEnvironment.systemEnvironment()
                environment.remove("DRI_PRIME")
                environment.remove("MESA_VK_DEVICE_SELECT")
                for key, value in selected.items():
                    environment.insert(key, value)
                self.load_process.setProcessEnvironment(environment)
                self.load_process.start(executable, arguments)
                if not self.load_process.waitForStarted(900):
                    self._finish_preview(failure="GPU load helper did not start")
                    return
                test_caption = self.tr("GPU-Last-Kurztest läuft · LACT stellt die Änderung automatisch zurück.")
            else:
                self.load_process = None
                test_caption = self.tr("GPU-Lüfter-Kurztest läuft · ohne Grafiklast; LACT stellt die Änderung automatisch zurück.")
            self.status.setText(test_caption)
            self._gpu_log(f"GPU-LACT: testweises Profil gesetzt · automatische LACT-Rückstellung aktiv"
                          + (f" · GPU-Auswahl={selected}" if self.preview_needs_load
                             else " · reiner Lüftertest ohne Grafiklast"))
            self._sync_buttons()
            self.preview_timer.start()
            remaining = self.preview_deadline - time.monotonic()
            QTimer.singleShot(max(1, int(min(3.8, remaining - 0.6) * 1000)), self, self._finish_preview)
        except LactError as exc:
            if pending_write:
                try:
                    self.client.pending("revert")
                except LactError as rollback_error:
                    self._gpu_log(f"GPU-LACT-FEHLER: Test-Rückstellung nicht bestätigt · {rollback_error}")
            self.candidate = None
            self.status.setText(self.tr("GPU-Kurztest nicht möglich: {reason}").format(reason=exc))
            self._gpu_log(f"GPU-LACT-FEHLER: Kurztest abgebrochen · {exc}")
            self._sync_buttons()

    def _sample_preview(self) -> None:
        if not self.preview_active:
            return
        try:
            stats = self.client.stats(self.gpu_id)
            measured = stats.get("busy_percent")
            if isinstance(measured, (int, float)) and not isinstance(measured, bool) and 0 <= measured <= 100:
                self.preview_peak_load = max(self.preview_peak_load, float(measured))
            if self.candidate and self.candidate.get("fan_control_settings") != self.baseline.get("fan_control_settings"):
                self.record_fan_sample(stats, "während Kurztest")
            if self.preview_fan_test:
                fan = stats.get("fan") if isinstance(stats.get("fan"), dict) else {}
                rpm = fan.get("speed_current")
                pwm = fan.get("pwm_current")
                if isinstance(rpm, (int, float)) and not isinstance(rpm, bool):
                    self.preview_fan_peak_rpm = max(self.preview_fan_peak_rpm, int(rpm))
                if isinstance(pwm, (int, float)) and not isinstance(pwm, bool) and pwm > 0:
                    self.preview_fan_pwm_seen = True
        except LactError:
            pass

    def _stop_load(self) -> bool:
        process, self.load_process = self.load_process, None
        if process is None:
            return False
        running = process.state() == QProcess.ProcessState.Running
        if process.state() != QProcess.ProcessState.NotRunning:
            process.terminate()
            if not process.waitForFinished(300):
                process.kill()
                process.waitForFinished(300)
        process.deleteLater()
        return running

    def _finish_preview(self, failure: str = "") -> None:
        if not self.preview_active:
            return
        self._sample_preview()
        self.preview_active = False
        self.preview_timer.stop()
        helper_running = self._stop_load()
        reason = failure or ("GPU load helper ended early"
                             if self.preview_needs_load and not helper_running else "")
        if not reason and self.preview_needs_load and self.preview_peak_load < 50:
            reason = f"GPU-Auslastung nur {self.preview_peak_load:.0f} %; Test nicht aussagekräftig"
        if not reason and self.preview_fan_test:
            self._gpu_log(f"GPU-LACT: Lüfter-Kurztest · Ausgang={self.preview_fan_initial_rpm} RPM"
                          f" · Spitze={self.preview_fan_peak_rpm} RPM · PWM aktiv={self.preview_fan_pwm_seen}")
            newly_enabled = not self.baseline.get("fan_control_enabled") and self.candidate.get("fan_control_enabled")
            if not fan_preview_verified(newly_enabled=newly_enabled,
                    baseline_rpm=self.preview_fan_initial_rpm,
                    peak_rpm=self.preview_fan_peak_rpm,
                    pwm_seen=self.preview_fan_pwm_seen):
                reason = self.tr("Lüfterreaktion nicht bestätigt: {rpm} RPM nach Kurztest.").format(
                    rpm=self.preview_fan_peak_rpm)
        try:
            if not reason:
                good, reason = healthy_stats(self.client.stats(self.gpu_id))
                if good:
                    reason = ""
            try:
                self.client.pending("revert")
            except LactError:
                # LACT may have reached its own automatic rollback deadline.
                pass
            if self.client.config(self.gpu_id) != self.baseline:
                reason = "LACT did not restore the previous GPU settings"
        except LactError as exc:
            reason = str(exc)
        self.tested = not bool(reason)
        if reason:
            self.candidate = None
            self.status.setText(self.tr("GPU-Kurztest fehlgeschlagen oder Rückstellung nicht bestätigt: {reason}").format(reason=reason))
            self._gpu_log(f"GPU-LACT-FEHLER: {reason}")
        else:
            self.status.setText(self.tr("GPU-Kurztest bestanden und vorherige Werte wiederhergestellt. Dauerhaftes Speichern bleibt eine eigene Entscheidung; Langzeitstabilität ist nicht bewiesen."))
            completed = "Lüfter-Kurztest" if self.preview_fan_only_changes else "Last-Kurztest"
            self._gpu_log(f"GPU-LACT: {completed} bestanden · LACT-Basiswerte wiederhergestellt"
                          " · dauerhaft noch nicht aktiv")
            if self.candidate and self.candidate.get("fan_control_settings") != self.baseline.get("fan_control_settings"):
                self.capture_gpu_diagnostics()
        self._sync_buttons()
        if (not reason and self.preview_fan_test and self.preview_fan_only_changes
                and self.fan_persist_after_test.isChecked()):
            self.fan_persist_after_test.setChecked(False)
            self._gpu_log("GPU-LACT: bestätigten Lüftertest auf Nutzerwunsch dauerhaft speichern")
            QTimer.singleShot(0, self, self.save_tested)

    def save_tested(self) -> None:
        if not self._write_allowed():
            return
        if not self.tested or self.candidate is None or self.baseline is None:
            return
        if not self._power_candidate_allowed(self.candidate):
            self.status.setText(self.tr("Leistungslimit über LACT-Standard nicht freigeschaltet."))
            self.tested = False
            self._sync_buttons()
            return
        if self.overdrive_enabled is not True:
            self.status.setText(self.tr("AMD-Overdrive ist aus. In LACT aktivieren, neu starten und hier aktualisieren."))
            return
        if not self.refresh_ownership():
            self.status.setText(self.tr("Speichern gesperrt: CoolerControl-GPU-Besitz nicht freigegeben."))
            return
        pending = False
        confirmed = False
        try:
            if self.client.config(self.gpu_id) != self.baseline:
                raise LactError("GPU settings changed outside OHC; refresh first")
            previous = read_snapshot(self.host.settings, self.gpu_id)
            original = (previous["original"] if previous and previous["saved"] == self.baseline
                        else self.baseline)
            self.client.set_config(self.gpu_id, self.candidate)
            pending = True
            if not config_equivalent(self.candidate, self.client.config(self.gpu_id)):
                raise LactError("LACT did not apply the tested configuration")
            good, reason = healthy_stats(self.client.stats(self.gpu_id))
            if not good:
                raise LactError(reason)
            self.client.pending("confirm")
            pending = False
            confirmed = True
            saved = self.client.config(self.gpu_id)
            if not config_equivalent(self.candidate, saved):
                raise LactError("LACT did not confirm the saved configuration")
            write_snapshot(self.host.settings, self.gpu_id, original, saved)
        except (LactError, OSError, TypeError, ValueError) as exc:
            rollback_error = ""
            if pending:
                try:
                    self.client.pending("revert")
                except LactError as error:
                    rollback_error = str(error)
            elif confirmed:
                try:
                    if config_equivalent(self.candidate, self.client.config(self.gpu_id)):
                        self.client.set_config(self.gpu_id, self.baseline)
                        self.client.pending("confirm")
                except LactError as error:
                    rollback_error = str(error)
            try:
                restored = self.client.config(self.gpu_id) == self.baseline
            except LactError as error:
                restored = False
                rollback_error = rollback_error or str(error)
            detail = str(exc) if restored else f"{exc}; rollback unverified: {rollback_error or 'GPU values differ from baseline'}"
            self.status.setText(self.tr("GPU-Einstellung konnte nicht dauerhaft gespeichert werden: {reason}").format(reason=detail))
            self._gpu_log(f"GPU-LACT-FEHLER: dauerhaftes Speichern fehlgeschlagen · {detail}")
            self.tested = False
            self._sync_buttons()
            return
        self.status.setText(self.tr("Getestete GPU-Einstellung ist in LACT gespeichert. „Vorherige Werte wiederherstellen“ gibt sie wieder frei."))
        fan_saved = bool(self.candidate.get("fan_control_enabled") != self.baseline.get("fan_control_enabled")
                         or self.candidate.get("fan_control_settings") != self.baseline.get("fan_control_settings"))
        self._gpu_log("GPU-LACT: getestete Einstellung ausdrücklich dauerhaft in LACT bestätigt"
                      + (" · Lüftersteuerung aktiv" if fan_saved else ""))
        self.baseline = deepcopy(saved)
        self.tested = False
        self._populate_controls()
        self._sync_buttons()

    def restore_baseline(self) -> None:
        if not self._write_allowed():
            return
        if not self.gpu_id:
            return
        record = read_snapshot(self.host.settings, self.gpu_id)
        if not record:
            return
        try:
            if record["original"].get("fan_control_enabled") and not self.refresh_ownership():
                raise LactError("CoolerControl GPU fan ownership must be released first")
            if self.client.config(self.gpu_id) != record["saved"]:
                raise LactError("GPU settings changed outside OHC; refresh before restoring")
            self.client.set_config(self.gpu_id, record["original"])
            self.client.pending("confirm")
            if not config_equivalent(record["original"], self.client.config(self.gpu_id)):
                raise LactError("LACT did not confirm the restored baseline")
            forget_snapshot(self.host.settings, self.gpu_id)
            self.status.setText(self.tr("Vorherige GPU-Werte in LACT wiederhergestellt."))
            self._gpu_log("GPU-LACT: vorherige GPU-Werte wiederhergestellt")
            self.refresh()
        except LactError as exc:
            self.status.setText(self.tr("GPU-Freigabe fehlgeschlagen: {reason}").format(reason=exc))
            self._gpu_log(f"GPU-LACT-FEHLER: Rückstellung fehlgeschlagen · {exc}")
        self.tested = False
        self._sync_buttons()

    def release_gpu_fan(self) -> None:
        if not self._write_allowed():
            return
        if not self.gpu_id:
            return
        try:
            current = self.client.config(self.gpu_id)
            if not current.get("fan_control_enabled"):
                self.status.setText(self.tr("GPU-Lüfter ist bereits freigegeben."))
                self._gpu_log("GPU-LACT: GPU-Lüfter bereits freigegeben · keine LACT-Änderung")
                return
            self.capture_gpu_diagnostics()
            candidate = deepcopy(current)
            candidate["fan_control_enabled"] = False
            self.client.set_config(self.gpu_id, candidate)
            self.client.pending("confirm")
            if self.client.config(self.gpu_id).get("fan_control_enabled"):
                raise LactError("LACT GPU fan control remained active")
            record = read_snapshot(self.host.settings, self.gpu_id)
            if record and record["saved"] == current:
                original = deepcopy(record["original"])
                original["fan_control_enabled"] = False
                write_snapshot(self.host.settings, self.gpu_id, original, candidate)
            self._gpu_log("GPU-LACT: GPU-Lüfter ausdrücklich an Firmware freigegeben")
            self.refresh()
            self.capture_gpu_diagnostics()
            self.status.setText(self.tr("LACT hat den GPU-Lüfter freigegeben; Firmware kann wieder steuern."))
        except LactError as exc:
            self.status.setText(self.tr("GPU-Lüfter konnte nicht freigegeben werden: {reason}").format(reason=exc))
            self._gpu_log(f"GPU-LACT-FEHLER: Lüfterfreigabe fehlgeschlagen · {exc}")

    def handoff_to_coolercontrol(self) -> None:
        """Release LACT's fan channel before CC can be configured to manage it."""
        self.release_gpu_fan()
        try:
            if self.gpu_id and self.client.config(self.gpu_id).get("fan_control_enabled"):
                return
        except LactError:
            return
        QDesktopServices.openUrl(QUrl("http://127.0.0.1:11987"))
        self.status.setText(self.tr("LACT-Lüftersteuerung ist aus. GPU-Lüfter in CoolerControl ausdrücklich neu zuweisen."))

    def install_lact(self) -> None:
        if hasattr(self.host, "install_optional_backend"):
            self.host.install_optional_backend("lact")
        else:
            QDesktopServices.openUrl(QUrl("https://github.com/ilya-zlobintsev/LACT#installation"))

    def open_lact(self) -> None:
        executable = shutil.which("lact")
        if executable:
            QProcess.startDetached(executable, ["gui"])
        else:
            self.status.setText(self.tr("LACT-Dienst nicht erreichbar: {reason}").format(reason="lact"))

    def prepare_overdrive(self) -> None:
        """Only an explicit confirmation may ask LACT to alter its boot setup."""
        if not self._write_allowed():
            return
        if not self.gpu_id or self.overdrive_enabled is not False or self.overdrive_process is not None:
            return
        answer = QMessageBox.question(
            self, self.tr("AMD-Overdrive vorbereiten"),
            self.tr("LACT richtet AMD-Overdrive im Bootsystem ein und aktualisiert nötigenfalls das Startabbild. Danach ist ein Neustart erforderlich. Jetzt vorbereiten?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        process = QProcess(self)
        self.overdrive_process = process
        process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        process.finished.connect(lambda *_args: self._overdrive_finished(process))
        process.errorOccurred.connect(lambda _error: self._overdrive_finished(process)
                                      if process.state() == QProcess.ProcessState.NotRunning else None)
        worker = Path(__file__).with_name("overdrive_worker.py")
        process.start(sys.executable, [str(worker)])
        QTimer.singleShot(250_000, process, lambda: process.kill()
                          if self.overdrive_process is process
                          and process.state() == QProcess.ProcessState.Running else None)
        self.status.setText(self.tr("LACT bereitet AMD-Overdrive vor. Das kann einige Minuten dauern."))
        self._gpu_log("GPU-LACT: AMD-Overdrive-Vorbereitung nach ausdrücklicher Bestätigung gestartet")
        self._sync_buttons()

    def _overdrive_finished(self, process: QProcess) -> None:
        if self.overdrive_process is not process:
            return
        self.overdrive_process = None
        try:
            result = json.loads(bytes(process.readAllStandardOutput()).decode("utf-8", "replace").splitlines()[-1])
        except (ValueError, IndexError):
            result = {}
        if process.exitStatus() == QProcess.ExitStatus.NormalExit and process.exitCode() == 0 and result.get("ok") is True:
            self.overdrive_prepared = True
            message = self.tr("AMD-Overdrive ist vorbereitet. Bitte den Rechner neu starten und danach GPU und LACT aktualisieren.")
            self.status.setText(message)
            self._gpu_log("GPU-LACT: AMD-Overdrive vorbereitet · Neustart durch Nutzer erforderlich")
            QMessageBox.information(self, self.tr("AMD-Overdrive vorbereiten"), message)
        else:
            reason = str(result.get("reason") or "LACT setup process failed")[:300]
            self.status.setText(self.tr("AMD-Overdrive konnte nicht vorbereitet werden: {reason}").format(reason=reason))
            self._gpu_log(f"GPU-LACT-FEHLER: Overdrive-Vorbereitung · {reason}")
        process.deleteLater()
        self._sync_buttons()

    def shutdown(self) -> None:
        self.gpu_read_probe.cancel()
        self.gpu_owner_probe.cancel()
        if getattr(self, "stress_process", None) is not None:
            self.stop_stress("Programm wird beendet")
        if self.overdrive_process is not None:
            self._gpu_log("GPU-LACT: OHC beendet während Overdrive-Vorbereitung · LACT-Status beim nächsten Start prüfen")
            self.overdrive_process.kill()
            self.overdrive_process.waitForFinished(1000)
            self.overdrive_process = None
        if self.preview_active:
            self._finish_preview(failure="Application is closing")
        else:
            self._stop_load()
