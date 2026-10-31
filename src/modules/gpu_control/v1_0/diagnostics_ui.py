# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded OHC/LACT diagnostic view with a user-initiated local export."""
from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import shutil
import tempfile

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from .client import LactError


class GpuDiagnosticsUiMixin:
    def _build_diagnostics(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        note = QLabel(self.tr("OHC-Aktionen und LACT-Dienstmeldungen. Das Protokoll kann Systemdetails enthalten; vor Weitergabe prüfen."))
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QHBoxLayout()
        sample = QPushButton(self.tr("GPU-Zustand erfassen"))
        sample.clicked.connect(self.capture_gpu_diagnostics)
        self.journal_button = QPushButton(self.tr("LACT-Dienstprotokoll laden"))
        self.journal_button.clicked.connect(self.load_lact_journal)
        copy_ohc = QPushButton(self.tr("OHC-Aktionen und Messwerte"))
        copy_ohc.setToolTip("Dieses OHC-Protokoll in die Zwischenablage kopieren.")
        copy_ohc.clicked.connect(lambda: self.copy_gpu_diagnostics("ohc"))
        copy_lact = QPushButton(self.tr("LACT-Dienstmeldungen"))
        copy_lact.setToolTip("Das geladene LACT-Protokoll in die Zwischenablage kopieren.")
        copy_lact.clicked.connect(lambda: self.copy_gpu_diagnostics("lact"))
        copy_all = QPushButton(self.tr("Alles kopieren"))
        copy_all.setObjectName("gpuPrimaryAction")
        copy_all.clicked.connect(lambda: self.copy_gpu_diagnostics("all"))
        export = QPushButton(self.tr("GPU-Diagnose speichern"))
        export.clicked.connect(self.export_gpu_diagnostics)
        for button in (sample, self.journal_button, copy_ohc, copy_lact, copy_all, export):
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)
        layout.addWidget(QLabel(self.tr("OHC-Aktionen und Messwerte")))
        self.gpu_events = QPlainTextEdit()
        self.gpu_events.setReadOnly(True)
        self.gpu_events.document().setMaximumBlockCount(500)
        layout.addWidget(self.gpu_events, 1)
        layout.addWidget(QLabel(self.tr("LACT-Dienstmeldungen")))
        self.lact_journal = QPlainTextEdit()
        self.lact_journal.setReadOnly(True)
        layout.addWidget(self.lact_journal, 1)
        self.sections.addTab(page, self.tr("LACT-Protokoll"))
        self.diagnostics_index = self.sections.count() - 1
        self.sections.currentChanged.connect(self._diagnostics_tab_changed)
        self.journal_process: QProcess | None = None

    def copy_gpu_diagnostics(self, scope: str = "all") -> None:
        ohc = self.gpu_events.toPlainText()
        lact = self.lact_journal.toPlainText()
        if scope == "ohc":
            text = ohc
            label = "OHC-Aktionen"
        elif scope == "lact":
            text = lact
            label = "LACT-Dienstprotokoll"
        else:
            text = (self.tr("OHC-Aktionen und Messwerte") + "\n" + ohc
                    + "\n\n" + self.tr("LACT-Dienstmeldungen") + "\n" + lact)
            label = "GPU-/LACT-Protokoll"
        QApplication.clipboard().setText(text)
        self.status.setText(f"{label} wurde in die Zwischenablage kopiert.")

    def _diagnostics_tab_changed(self, index: int) -> None:
        if index == self.diagnostics_index:
            self.capture_gpu_diagnostics()
            self.load_lact_journal()

    def record_fan_sample(self, stats: dict, phase: str) -> None:
        fan = stats.get("fan") if isinstance(stats.get("fan"), dict) else {}
        if fan:
            self._gpu_log(f"GPU-LACT: Lüftermessung · {phase}"
                          f" · Ist={fan.get('speed_current', '-')} RPM"
                          f" · PWM={fan.get('pwm_current', '-')}"
                          f" · LACT-Modus={fan.get('control_mode', '-')}")

    def _gpu_log(self, message: str) -> None:
        self.host.log_message(message)
        if hasattr(self, "gpu_events"):
            self.gpu_events.appendPlainText(f"[{datetime.now().astimezone().isoformat(timespec='seconds')}] {message}")

    def capture_gpu_diagnostics(self) -> None:
        if not self.gpu_id:
            self._gpu_log("GPU-LACT: Diagnose · keine GPU ausgewählt")
            return
        try:
            config = self.client.config(self.gpu_id)
            stats = self.client.stats(self.gpu_id)
        except LactError as exc:
            self._gpu_log(f"GPU-LACT-FEHLER: Diagnoseabfrage · {exc}")
            return
        fan = stats.get("fan") if isinstance(stats.get("fan"), dict) else {}
        settings = config.get("fan_control_settings") if isinstance(config.get("fan_control_settings"), dict) else {}
        temps = stats.get("temps") if isinstance(stats.get("temps"), dict) else {}
        edge = temps.get("edge") if isinstance(temps.get("edge"), dict) else {}
        speed = settings.get("static_speed")
        target = (f"{round(speed * 100)} %" if config.get("fan_control_enabled")
                  and isinstance(speed, (int, float)) else "-")
        pmfw = fan.get("pmfw_info") if isinstance(fan.get("pmfw_info"), dict) else {}
        self._gpu_log(
            "GPU-LACT: Zustand"
            f" · GPU={self.gpu_id} · Profil-Lüfter={config.get('fan_control_enabled', False)}"
            f" · Modus={settings.get('mode', 'auto')}"
            f" · Soll={target}"
            f" · Ist={fan.get('speed_current', '-')} RPM"
            f" · PWM={fan.get('pwm_current', '-')}"
            f" · Verzögerung={settings.get('spindown_delay_ms', 0)} ms"
            f" · ZeroRPM={pmfw.get('zero_rpm_enable', '-')}"
            f" · Temperatur={edge.get('current', '-')} °C"
            f" · Last={stats.get('busy_percent', '-')} %"
        )

    def load_lact_journal(self) -> None:
        if self.journal_process is not None:
            return
        executable = shutil.which("journalctl")
        if not executable:
            self.lact_journal.setPlainText(self.tr("journalctl ist nicht verfügbar."))
            return
        process = QProcess(self)
        self.journal_process = process
        self.journal_button.setEnabled(False)
        process.finished.connect(self._journal_finished)
        process.start(executable, ["--no-pager", "--unit=lactd.service", "--boot",
                                   "--lines=200", "--output=short-iso"])

    def _journal_finished(self, _exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        process, self.journal_process = self.journal_process, None
        self.journal_button.setEnabled(True)
        if process is None:
            return
        output = bytes(process.readAllStandardOutput())[-131072:].decode("utf-8", "replace")
        error = bytes(process.readAllStandardError())[-2048:].decode("utf-8", "replace")
        self.lact_journal.setPlainText(output or error or self.tr("Keine LACT-Dienstmeldungen verfügbar."))
        process.deleteLater()

    def export_gpu_diagnostics(self) -> None:
        selected, _ = QFileDialog.getSaveFileName(
            self, self.tr("GPU-Diagnose speichern"),
            str(Path.home() / "GPU-LACT-Diagnose.txt"), "Text (*.txt)")
        if not selected:
            return
        target = Path(selected)
        data = ("Open Hardware Control · GPU/LACT\n\n"
                + self.tr("OHC-Aktionen und Messwerte") + "\n" + self.gpu_events.toPlainText()
                + "\n\n" + self.tr("LACT-Dienstmeldungen") + "\n" + self.lact_journal.toPlainText() + "\n")
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                             prefix=".gpu-lact-", delete=False) as temp:
                temp_name = temp.name
                temp.write(data)
            os.chmod(temp_name, 0o600)
            os.replace(temp_name, target)
        except OSError as exc:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
            self._gpu_log(f"GPU-LACT-FEHLER: Diagnoseexport · {type(exc).__name__}")
            return
        self._gpu_log("GPU-LACT: Diagnose vom Nutzer lokal gespeichert")
