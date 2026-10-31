# SPDX-License-Identifier: GPL-3.0-or-later
"""Cancellable, monitored load test of an already confirmed LACT profile."""
from __future__ import annotations

import shutil
import time

from PySide6.QtCore import QProcess, QProcessEnvironment, QTimer, Qt
from PySide6.QtWidgets import QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .client import LactError
from .power_policy import reported_power_bounds, sustained_power_excess
from .snapshot import read_snapshot
from .stress import (benchmark_command, benchmark_gpu_environment, command_uses_vkmark,
                     load_sample, vkmark_reported_gpu)
from .stress_window import request_stress_window_state


class GpuStressUiMixin:
    def _build_stress(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QGroupBox(self.tr("Lasttest"))
        card.setObjectName("gpuControlCard")
        card_layout = QVBoxLayout(card)
        note = QLabel(self.tr("LACT-Werte testen; offene Eingaben bleiben ungetestet. Abbrechbar."))
        note.setWordWrap(True)
        card_layout.addWidget(note)
        row = QGridLayout()
        self.stress_duration = QComboBox()
        for seconds in (15, 30, 60, 120):
            self.stress_duration.addItem(str(seconds), seconds)
        self.stress_size = QComboBox()
        self.stress_size.addItem(self.tr("4K · hohe Last"), "3840x2160")
        self.stress_size.addItem(self.tr("8K · maximale Last"), "7680x4320")
        self.stress_size.setCurrentIndex(1)
        self.stress_presentation = QComboBox()
        self.stress_presentation.addItem(self.tr("Max. Fenster · Taskleiste sichtbar"), "maximized")
        self.stress_presentation.addItem(self.tr("Minimiert · Test läuft weiter"), "minimized")
        self.stress_presentation.addItem(self.tr("Vollbild · Taskleiste verborgen"), "fullscreen")
        saved_presentation = str(self.host.settings.value(
            "gpu_control/stress_presentation", "maximized",
        ))
        self.stress_presentation.setCurrentIndex(max(
            0, self.stress_presentation.findData(saved_presentation),
        ))
        self.stress_presentation.currentIndexChanged.connect(
            lambda _index: self.host.settings.setValue(
                "gpu_control/stress_presentation", self.stress_presentation.currentData(),
            )
        )
        self.stress_button = QPushButton(self.tr("GPU-Lasttest starten"))
        self.stress_button.setObjectName("gpuPrimaryAction")
        self.stress_button.setMinimumHeight(44)
        self.stress_button.clicked.connect(self.start_stress)
        self.stress_cancel = QPushButton(self.tr("Abbrechen"))
        self.stress_cancel.clicked.connect(lambda: self.stop_stress("Vom Nutzer abgebrochen"))
        self.stress_cancel.setEnabled(False)
        self.stress_install = QPushButton(self.tr("vkmark installieren"))
        self.stress_install.clicked.connect(self.install_stress_tool)
        row.addWidget(QLabel(self.tr("Sekunden")), 0, 0)
        row.addWidget(self.stress_duration, 0, 1)
        row.addWidget(QLabel("Auflösung"), 1, 0)
        row.addWidget(self.stress_size, 1, 1)
        row.addWidget(QLabel("Darstellung"), 2, 0)
        row.addWidget(self.stress_presentation, 2, 1)
        row.addWidget(self.stress_button, 3, 0, 1, 2)
        row.addWidget(self.stress_cancel, 4, 0)
        row.addWidget(self.stress_install, 4, 1)
        row.setColumnStretch(1, 1)
        card_layout.addLayout(row)
        live = QGroupBox("Live-Daten")
        live.setObjectName("gpuPreviewCard")
        live_grid = QGridLayout(live)
        self.stress_live_load = QLabel("Last\n— %")
        self.stress_live_temperature = QLabel("Temperatur\n— °C")
        self.stress_live_clock = QLabel("Takt\n— MHz")
        self.stress_live_power = QLabel("Leistung\n— W")
        for column, value in enumerate((self.stress_live_load, self.stress_live_temperature,
                                        self.stress_live_clock, self.stress_live_power)):
            value.setObjectName("gpuStressMetric")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            live_grid.addWidget(value, 0, column)
            live_grid.setColumnStretch(column, 1)
        card_layout.addWidget(live)
        self.stress_status = QLabel(self.tr("GPU-Lasttest bereit"))
        self.stress_status.setWordWrap(True)
        card_layout.addWidget(self.stress_status)
        layout.addWidget(card)
        layout.addStretch()
        self.stress_page = page
        self.sections.addTab(page, self.tr("Lasttest"))
        self.stress_process: QProcess | None = None
        self.stress_timer = QTimer(self)
        self.stress_timer.setInterval(1000)
        self.stress_timer.timeout.connect(self._stress_tick)
        self.stress_deadline = 0.0
        self.stress_peak_load = 0.0
        self.stress_busy_samples: list[float] = []
        self.stress_gpu_id = ""
        self.stress_reference: dict | None = None
        self.stress_has_snapshot = False
        self.stress_executable = ""
        self.stress_vkmark = False
        self.stress_high_power_samples = 0

    def _stress_command(self) -> tuple[str, list[str]]:
        screen = self.screen()
        available = screen.availableGeometry() if screen is not None else None
        output_size = (f"{available.width()}x{available.height()}" if available is not None
                       and available.width() >= 640 and available.height() >= 480 else "1920x1080")
        return benchmark_command({key: shutil.which(key) or "" for key in ("vkmark", "glmark2", "gamescope")},
                                 size=str(self.stress_size.currentData()),
                                 duration_seconds=int(self.stress_duration.currentData() or 15) + 15,
                                 presentation=str(self.stress_presentation.currentData() or "maximized"),
                                 output_size=output_size)

    def start_stress(self) -> None:
        if self.stress_process is not None or self.preview_active or not self.gpu_id:
            return
        record = read_snapshot(self.host.settings, self.gpu_id)
        executable, args = self._stress_command()
        if not executable:
            self.stress_status.setText(self.tr("vkmark oder glmark2 fehlt. Installiere vkmark für den Lasttest."))
            return
        try:
            current = self.client.config(self.gpu_id)
            if record and current != record["saved"]:
                raise LactError("GPU-Werte wurden außerhalb von OHC geändert; bitte aktualisieren")
            ok, reason, _busy = load_sample(self.client.stats(self.gpu_id))
            if not ok:
                raise LactError(reason)
        except LactError as exc:
            self.stress_status.setText(str(exc))
            return
        process = QProcess(self)
        environment = QProcessEnvironment.systemEnvironment()
        try:
            selected = benchmark_gpu_environment(self.gpu_id, executable)
        except ValueError as exc:
            self.stress_status.setText(str(exc))
            return
        environment.remove("DRI_PRIME")
        environment.remove("MESA_VK_DEVICE_SELECT")
        for key, value in selected.items():
            environment.insert(key, value)
        process.setProcessEnvironment(environment)
        self.stress_process = process
        self.stress_executable = executable
        self.stress_vkmark = command_uses_vkmark(executable, args)
        self.stress_gpu_id = self.gpu_id
        self.stress_reference = current
        self.stress_has_snapshot = bool(record)
        self.stress_peak_load = 0.0
        self.stress_busy_samples = []
        self.stress_high_power_samples = 0
        self.stress_deadline = time.monotonic() + int(self.stress_duration.currentData() or 15)
        process.start(executable, args)
        if not process.waitForStarted(1000):
            self.stop_stress("Benchmark konnte nicht gestartet werden")
            return
        request_stress_window_state(
            self, process, str(self.stress_presentation.currentData() or "maximized"),
        )
        self.stress_timer.start()
        self.stress_cancel.setEnabled(True)
        self.stress_status.setText(self.tr("GPU-Lasttest läuft") + f" · {int(self.stress_duration.currentData())} s")
        self._gpu_log(f"GPU-LACT: längerer Lasttest gestartet · {int(self.stress_duration.currentData())} s"
                      f" · {self.stress_size.currentData()} · Darstellung={self.stress_presentation.currentData()}"
                      f" · {executable} · GPU-Auswahl={selected}")
        self._sync_buttons()

    def _stress_tick(self) -> None:
        process = self.stress_process
        if process is None:
            return
        if process.state() == QProcess.ProcessState.NotRunning:
            self.stop_stress("Benchmark wurde vorzeitig beendet")
            return
        try:
            stats = self.client.stats(self.stress_gpu_id)
            self.stats = stats
            self._refresh_gpu_dashboard()
            ok, reason, busy = load_sample(stats)
            if not ok:
                self.stop_stress(reason, rollback=True)
                return
            self.stress_peak_load = max(self.stress_peak_load, busy)
            self.stress_busy_samples.append(busy)
            edge = stats.get("temps", {}).get("edge", {})
            temp = edge.get("current", "-") if isinstance(edge, dict) else edge
            clocks = stats.get("clockspeed") if isinstance(stats.get("clockspeed"), dict) else {}
            power = stats.get("power") if isinstance(stats.get("power"), dict) else {}
            self.stress_live_load.setText(f"Last\n{busy:.0f} %")
            self.stress_live_temperature.setText(f"Temperatur\n{temp} °C")
            self.stress_live_clock.setText(f"Takt\n{clocks.get('gpu_clockspeed', '—')} MHz")
            self.stress_live_power.setText(f"Leistung\n{power.get('average', '—')} W")
            if not self.power_unlock.isChecked() and sustained_power_excess(
                    power.get("average"), reported_power_bounds(stats)):
                self.stress_high_power_samples += 1
            else:
                self.stress_high_power_samples = 0
            self._gpu_log(f"GPU-LACT: Lasttest-Messung · Last={busy:.0f} % · Temperatur={temp} °C"
                          f" · GPU-Takt={clocks.get('gpu_clockspeed', '-')} MHz"
                          f" · Ziel-Takt={clocks.get('target_gpu_clockspeed', '-')} MHz"
                          f" · Leistung={power.get('average', '-')} W"
                          f" · Limit={power.get('cap_current', '-')} W"
                          f" · Drosselung={stats.get('throttle_info', '-')}")
            if self.stress_high_power_samples >= 10:
                self.stop_stress(self.tr("GPU-Leistung länger als 10 s über LACT-Standard: {watts} W.").format(
                    watts=power.get("average")), rollback=True)
                return
            if self.client.config(self.stress_gpu_id) != self.stress_reference:
                self.stop_stress("GPU-Profil wurde während des Tests verändert")
                return
        except (LactError, TypeError, KeyError) as exc:
            self.stop_stress(f"Messwerte konnten nicht geprüft werden: {exc}", rollback=True)
            return
        remaining = max(0, round(self.stress_deadline - time.monotonic()))
        self.stress_status.setText(self.tr("GPU-Lasttest läuft") + f" · {remaining} s · GPU {busy:.0f} %")
        if remaining == 0:
            self.stop_stress("")

    def stop_stress(self, reason: str = "", *, rollback: bool = False) -> None:
        process, self.stress_process = self.stress_process, None
        if process is None:
            return
        self.stress_timer.stop()
        self.stress_cancel.setEnabled(False)
        already_finished = process.state() == QProcess.ProcessState.NotRunning
        exit_code = process.exitCode() if already_finished else None
        if process.state() != QProcess.ProcessState.NotRunning:
            process.terminate()
            if not process.waitForFinished(400):
                process.kill()
                process.waitForFinished(400)
        stdout = bytes(process.readAllStandardOutput())[-4096:].decode("utf-8", "replace")
        stderr = bytes(process.readAllStandardError())[-1000:].decode("utf-8", "replace").strip()
        process.deleteLater()
        average = (sum(self.stress_busy_samples) / len(self.stress_busy_samples)
                   if self.stress_busy_samples else 0.0)
        if not reason and (len(self.stress_busy_samples) < 3 or average < 90 or self.stress_peak_load < 95):
            reason = (f"GPU-Last zu niedrig · Mittel {average:.0f} % / Spitze {self.stress_peak_load:.0f} %"
                      " · Test nicht aussagekräftig")
        if reason.startswith("Benchmark"):
            reason += f" · Exit {exit_code}"
            useful_error = "\n".join(line for line in stderr.splitlines()
                                     if "radv is not a conformant Vulkan implementation" not in line)
            if useful_error:
                reason += " · " + useful_error[-300:]
        if self.stress_vkmark:
            reported = vkmark_reported_gpu(stdout)
            expected = ":".join(self.stress_gpu_id.split("-", 1)[0].lower().split(":")[:2])
            self._gpu_log(f"GPU-LACT: vkmark-Gerät · erwartet={expected} · gemeldet={reported or '-'}"
                          f" · Exit={exit_code if already_finished else 'OHC-Stopp'}"
                          f" · Ausgabe={stdout.strip()[-500:] or '-'}")
            if not reason and reported != expected:
                reason = self.tr("Vulkan-GPU nicht bestätigt: erwartet {expected}, gemeldet {actual}.").format(
                    expected=expected, actual=reported or "-")
        if rollback and self.stress_has_snapshot:
            try:
                record = read_snapshot(self.host.settings, self.stress_gpu_id)
                if record and self.client.config(self.stress_gpu_id) == record["saved"]:
                    self.restore_baseline()
                    if (self.client.config(self.stress_gpu_id) == record["original"]
                            and read_snapshot(self.host.settings, self.stress_gpu_id) is None):
                        reason += " · vorherige GPU-Werte wiederhergestellt"
                    else:
                        reason += " · Rückstellung nicht bestätigt"
                else:
                    reason += " · Rückstellung nicht möglich: GPU-Profil extern geändert"
            except LactError as exc:
                reason += f" · Rückstellung fehlgeschlagen: {exc}"
        message = reason or (f"Lasttest bestanden · mittlere GPU-Auslastung {average:.0f} %"
                             f" · Spitze {self.stress_peak_load:.0f} %")
        self.stress_status.setText(message)
        self._gpu_log(f"GPU-LACT: Lasttest beendet · {message}")
        self.stress_reference = None
        self.stress_has_snapshot = False
        self.stress_executable = ""
        self._sync_buttons()

    def install_stress_tool(self) -> None:
        # The helper asks before installing and uses configured distribution repos.
        from pathlib import Path
        from app_constants import helper_script_path
        if self.benchmark_install_active:
            return
        if shutil.which("vkmark"):
            self.status.setText(self.tr("GPU-Lasttest bereit"))
            self.stress_status.setText(self.tr("GPU-Lasttest bereit"))
            return
        script = helper_script_path(Path(__file__).resolve().parents[3] / "kraken_control.py", "install-dependencies.sh")
        if not script.is_file() or not hasattr(self.host, "backend"):
            self.status.setText(self.tr("GPU-Kurztest nicht möglich: {reason}").format(reason="install-dependencies.sh"))
            return
        self.benchmark_install_active = True
        self._sync_buttons()

        def done(result) -> None:
            self.benchmark_install_active = False
            if result.ok and shutil.which("vkmark"):
                message = self.tr("GPU-Lasttest bereit")
                self._gpu_log("GPU-LACT: vkmark installiert · GPU-Kurztest kann erneut gestartet werden")
            else:
                detail = (result.combined or "vkmark")[-300:]
                message = self.tr("GPU-Kurztest nicht möglich: {reason}").format(reason=detail)
                self._gpu_log(f"GPU-LACT-FEHLER: vkmark-Installation nicht abgeschlossen · {detail}")
            self.status.setText(message)
            self.stress_status.setText(message)
            self._sync_buttons()

        self.host.backend.run_async([str(script), "--check-gpu-benchmark-and-install"],
                                    callback=done, timeout=900)
