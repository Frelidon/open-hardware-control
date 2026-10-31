#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qt page and bounded process orchestration for Hardware Checker 1.0."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QProcess, QTimer, Qt
from PySide6.QtGui import QColor
from shiboken6 import isValid
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QFormLayout, QFrame, QGridLayout, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSpinBox, QTableWidget, QTableWidgetItem,
    QTabWidget, QVBoxLayout, QWidget,
)

from modules.hardware_fix.v1_0 import HardwareFixPanel

from .model import (
    Assessment, assess_memory, assess_nvme_link, assess_pcie_link,
    parse_dmidecode_inventory,
)
from .cards import HardwareOverviewMixin, ResultCard
from modules.platform_support.v1_0 import IS_WINDOWS, helper_command


STATE_PRESENTATION = {
    "pass": ("✓", "#4ade80"), "warning": ("!", "#facc15"),
    "fail": ("✕", "#fb7185"), "unknown": ("?", "#94a3b8"),
    "info": ("i", "#60a5fa"),
}


def gpu_load_command(tools: object) -> tuple[str, list[str]]:
    """Prefer a larger Vulkan benchmark; retain the bounded cube fallback."""
    if not isinstance(tools, dict):
        return "", []
    for key in ("vkmark", "glmark2", "vkcube"):
        executable = str(tools.get(key) or "")
        if not executable or not Path(executable).is_absolute():
            continue
        name = Path(executable).name
        if key == "vkmark" and name == "vkmark":
            arguments = ["--size", "1600x900", "--present-mode", "immediate",
                         "--run-forever", "-b", "shading:duration=5.0"]
            if os.environ.get("XDG_SESSION_TYPE") == "wayland":
                arguments.extend(("--winsys", "wayland"))
            return executable, arguments
        if key == "glmark2" and name.startswith("glmark2"):
            return executable, ["--off-screen", "--run-forever", "--benchmark", "refract"]
        if key == "vkcube" and name == "vkcube":
            arguments = ["--c", "100000", "--width", "640", "--height", "480", "--suppress_popups"]
            if os.environ.get("XDG_SESSION_TYPE") == "wayland":
                arguments.extend(("--wsi", "wayland"))
            return executable, arguments
    return "", []


class HardwareCheckerPage(HardwareOverviewMixin, QScrollArea):
    """One-click read-only system check with optional privileged DMI details."""

    def __init__(self, host: QWidget, translate: Callable[[str], str]) -> None:
        super().__init__(host)
        self.host = host
        self.translate = translate
        self.report: dict[str, object] = {}
        self.memory_modules: tuple[dict[str, object], ...] = ()
        self.socket_name = "Nicht gemeldet"
        self.socket_source = ""
        self.cards = {}
        self._card_columns = 0
        self.scan_process: QProcess | None = None
        self.dmi_process: QProcess | None = None
        self.stress_process: QProcess | None = None
        self.stress_started = False
        self.gpu_test_interrupted = False
        self.pending_gpu_test = False
        self.scan_under_load = False
        self.last_scan_under_load = False
        self.dmi_started = False
        self.dmi_complete = False
        self._build()
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.stop_processes)

    def tr(self, text: str) -> str:
        return self.translate(text)

    def _build(self) -> None:
        self.setWidgetResizable(True)
        body = QWidget()
        outer_layout = QVBoxLayout(body)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.section_tabs = QTabWidget()
        checker = QWidget()
        layout = QVBoxLayout(checker)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        hero = QFrame(objectName="moduleHeroCard")
        hero_layout = QVBoxLayout(hero)
        title = QLabel("Hardware-Checker")
        title.setObjectName("heroTitle")
        intro = QLabel(
            "Prüft CPU/SMT, PCIe-Anbindung von Grafikkarten, NVMe-SSDs und RAM. "
            "Es werden keine BIOS-, Takt-, Spannungs- oder Lüfterwerte verändert."
        )
        intro.setWordWrap(True)
        hero_layout.addWidget(title)
        hero_layout.addWidget(intro)
        layout.addWidget(hero)

        actions = QHBoxLayout()
        self.start_button = QPushButton("Vollständigen Hardware-Check starten")
        self.start_button.setObjectName("primaryAction")
        self.start_button.clicked.connect(self.start_full_check)
        self.gpu_button = QPushButton("GPU-Lasttest starten · 10 s")
        self.gpu_button.setEnabled(True)
        self.gpu_button.clicked.connect(self.start_gpu_test)
        actions.addWidget(self.start_button)
        actions.addWidget(self.gpu_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.status_label = QLabel("Bereit · der Check startet erst nach einem Klick.")
        self.status_label.setObjectName("infoText")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.gpu_availability_label = QLabel("")
        self.gpu_availability_label.setObjectName("warningText")
        self.gpu_availability_label.setWordWrap(True)
        self.gpu_availability_label.hide()
        layout.addWidget(self.gpu_availability_label)

        self.card_grid = QGridLayout()
        self.card_grid.setSpacing(10)
        for key in self.CARD_KEYS:
            self.cards[key] = ResultCard(key, checker)
        layout.addLayout(self.card_grid)
        self._reflow_cards(3)

        manual = QFrame(objectName="settingsCard")
        form = QFormLayout(manual)
        self.ram_model = QLineEdit()
        self.ram_model.setPlaceholderText("Optional, falls DMI kein Modell meldet")
        self.ram_model.setText(str(self.host.settings.value("hardware_checker/ram_model", "") or ""))
        self.ram_target = QSpinBox()
        self.ram_target.setRange(0, 20_000)
        self.ram_target.setSingleStep(100)
        self.ram_target.setSpecialValueText("Automatisch")
        self.ram_target.setSuffix(" MT/s")
        self.ram_target.setValue(self.host.settings.value("hardware_checker/ram_target_mts", 0, type=int))
        form.addRow("RAM-Hersteller / Modell", self.ram_model)
        form.addRow("Erwartete RAM-Taktrate", self.ram_target)
        self.ram_model.editingFinished.connect(self._save_manual_ram)
        self.ram_target.valueChanged.connect(self._save_manual_ram)
        layout.addWidget(manual)

        self.table = QTableWidget(0, 4)
        self.table.setObjectName("diagnosticTable")
        self.table.setHorizontalHeaderLabels(("Status", "Prüfung", "Ist-Wert", "Bewertung"))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setWordWrap(True)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setMinimumHeight(420)
        details = QCheckBox(self.tr("Details / Protokoll"))
        details.toggled.connect(self.table.setVisible)
        layout.addWidget(details)
        self.table.hide()
        layout.addWidget(self.table)
        note = QLabel(
            "PCIe kann im Leerlauf drosseln. Erst der gestartete GPU-Lasttest bewertet den Link unter Last. "
            "Dafür dienen vkmark, glmark2 oder vkcube."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note)
        layout.addStretch()
        self.hardware_fix_panel = HardwareFixPanel(self.host, self.translate)
        self.section_tabs.addTab(checker, "Hardware-Prüfung")
        self.section_tabs.addTab(self.hardware_fix_panel, "Hardware Fix")
        outer_layout.addWidget(self.section_tabs)
        self.setWidget(body)
        self._populate_cards()

    def start_full_check(self) -> None:
        if self.scan_process is not None or self.dmi_process is not None:
            return
        self.start_button.setEnabled(False)
        self.status_label.setText(self.tr("Hardware wird gelesen …"))
        self.dmi_started = False
        self.dmi_complete = False
        self._start_scan(under_load=False)
        if os.environ.get("OHC_DISABLE_HARDWARE_IO") != "1":
            self._start_dmi_probe()

    def _start_scan(self, *, under_load: bool) -> None:
        process = QProcess(self)
        self.scan_process = process
        self.scan_under_load = bool(under_load)
        process.finished.connect(lambda code, status: self._scan_finished(code, status, process))
        process.errorOccurred.connect(lambda error: self._scan_failed(error, process))
        program, arguments = helper_command(Path(__file__).with_name("probe.py"), ["--json"])
        process.start(program, arguments)
        QTimer.singleShot(12_000, process, lambda: self._expire_process(process))

    def _start_dmi_probe(self) -> None:
        if IS_WINDOWS:
            return
        pkexec = self._system_tool(("/usr/bin/pkexec", "/bin/pkexec"))
        dmidecode = self._system_tool(("/usr/sbin/dmidecode", "/usr/bin/dmidecode"))
        if not pkexec or not dmidecode:
            return
        process = QProcess(self)
        self.dmi_process = process
        self.dmi_started = True
        process.finished.connect(lambda code, status: self._dmi_finished(code, status, process))
        process.errorOccurred.connect(lambda error: self._dmi_failed(error, process))
        process.start(pkexec, [dmidecode, "--type", "4,17"])
        QTimer.singleShot(60_000, process, lambda: self._expire_process(process))

    @staticmethod
    def _system_tool(candidates: tuple[str, ...]) -> str:
        """Return only a fixed distribution-owned executable path."""
        for candidate in candidates:
            path = Path(candidate)
            if path.is_file() and os.access(path, os.X_OK):
                return os.fspath(path)
        return ""

    @staticmethod
    def _expire_process(process: QProcess) -> None:
        if isValid(process) and process.state() != QProcess.ProcessState.NotRunning:
            process.kill()

    def _scan_finished(self, exit_code: int, _status: QProcess.ExitStatus,
                       source: QProcess | None = None) -> None:
        if source is not None and source is not self.scan_process:
            return
        process = self.scan_process
        under_load = (self.scan_under_load and self.stress_process is not None
                      and self.stress_process.state() == QProcess.ProcessState.Running)
        self.scan_process = None
        if process is None or exit_code != 0:
            self._scan_failed(None)
            return
        try:
            self.report = json.loads(bytes(process.readAllStandardOutput()).decode("utf-8"))
            if not isinstance(self.report, dict):
                raise TypeError("Invalid hardware inventory")
        except (UnicodeError, json.JSONDecodeError, TypeError):
            self._scan_failed(None)
            return
        self.last_scan_under_load = under_load
        if isinstance(self.report.get("memory_modules"), list):
            self.memory_modules = tuple(row for row in self.report["memory_modules"] if isinstance(row, dict))
        self.socket_name = str(self.report.get("socket") or self.socket_name)
        self.socket_source = str(self.report.get("socket_source") or self.socket_source)
        self._populate(under_load=under_load)
        if under_load:
            self._stop_gpu_test()
            self.status_label.setText(self.tr("GPU-Lasttest abgeschlossen · PCIe-Link unter Last ausgewertet."))
        elif self.gpu_test_interrupted:
            self.status_label.setText(self.tr("GPU-Lasttest wurde beendet; PCIe-Link bleibt als Leerlaufwert markiert."))
        elif self.dmi_started and not self.dmi_complete:
            self.status_label.setText(self.tr("Grundprüfung abgeschlossen · RAM-Details folgen nach Administratorabfrage."))
        elif self.dmi_started and not self.memory_modules:
            self.status_label.setText(self.tr("Grundprüfung abgeschlossen · RAM-DMI wurde nicht freigegeben."))
        else:
            self.status_label.setText(self.tr("Hardware-Check abgeschlossen."))
        self._sync_ready_state()
        if self.pending_gpu_test:
            self.pending_gpu_test = False
            if gpu_load_command(self.report.get("tools", {}))[0] and self.report.get("gpus"):
                self.start_gpu_test()
            elif self.report.get("gpus"):
                self.status_label.setText(self.tr("GPU-Lasttest nicht verfügbar: Benchmark installieren."))

    def _scan_failed(self, _error, source: QProcess | None = None) -> None:
        if source is not None and source is not self.scan_process:
            return
        self.scan_process = None
        self.pending_gpu_test = False
        self._stop_gpu_test()
        self.status_label.setText(self.tr("Hardware-Check konnte nicht vollständig ausgeführt werden."))
        self._sync_ready_state()

    def _dmi_finished(self, exit_code: int, _status: QProcess.ExitStatus,
                      source: QProcess | None = None) -> None:
        if source is not None and source is not self.dmi_process:
            return
        process = self.dmi_process
        self.dmi_process = None
        self.dmi_complete = True
        if process is not None and exit_code == 0:
            raw = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
            inventory = parse_dmidecode_inventory(raw[:2_000_000])
            self.memory_modules = inventory.memory
            self.socket_name = inventory.socket
            self.socket_source = inventory.socket_source
            self._populate(under_load=self.last_scan_under_load)
            self.status_label.setText(self.tr("Hardware-Check abgeschlossen."))
        elif self.report:
            self.status_label.setText(self.tr("Grundprüfung abgeschlossen · RAM-DMI wurde nicht freigegeben."))
        self._sync_ready_state()

    def _dmi_failed(self, _error, source: QProcess | None = None) -> None:
        if source is not None and source is not self.dmi_process:
            return
        self.dmi_process = None
        self.dmi_complete = True
        if self.report:
            self.status_label.setText(self.tr("Grundprüfung abgeschlossen · RAM-DMI wurde nicht freigegeben."))
        self._sync_ready_state()

    def _sync_ready_state(self) -> None:
        busy = self.scan_process is not None or self.dmi_process is not None
        self.start_button.setEnabled(not busy and self.stress_process is None)
        tools = self.report.get("tools", {}) if isinstance(self.report, dict) else {}
        can_stress = bool(gpu_load_command(tools)[0] and self.report.get("gpus"))
        self.gpu_button.setEnabled((not self.report or can_stress) and not busy and self.stress_process is None)
        if self.report and self.report.get("gpus") and not can_stress and not busy:
            message = self.tr("GPU-Lasttest nicht verfügbar: Benchmark installieren.")
            self.gpu_button.setToolTip(message)
            self.gpu_availability_label.setText(message)
            self.gpu_availability_label.show()
        else:
            self.gpu_button.setToolTip("")
            self.gpu_availability_label.hide()

    def start_gpu_test(self) -> None:
        if self.scan_process is not None or self.dmi_process is not None or self.stress_process is not None:
            return
        if not self.report:
            self.pending_gpu_test = True
            self.status_label.setText(self.tr("Hardware wird gelesen …"))
            self._start_scan(under_load=False)
            self._sync_ready_state()
            return
        tools = self.report.get("tools", {}) if isinstance(self.report, dict) else {}
        executable, arguments = gpu_load_command(tools)
        if not executable or self.stress_process is not None:
            return
        process = QProcess(self)
        self.stress_process = process
        self.stress_started = False
        self.gpu_test_interrupted = False
        process.started.connect(lambda: setattr(self, "stress_started", True)
                                if self.stress_process is process else None)
        process.finished.connect(lambda *_args: self._gpu_ended_early(process))
        process.errorOccurred.connect(lambda _error: self._gpu_ended_early(process))
        process.start(executable, arguments)
        self.status_label.setText(self.tr("GPU-Lasttest läuft · keine Takt- oder Lüftereinstellung wird verändert."))
        self._sync_ready_state()
        QTimer.singleShot(9_000, process, lambda: self._scan_gpu_under_load(process))
        QTimer.singleShot(12_000, process, lambda: self._stop_gpu_test(process))

    def _scan_gpu_under_load(self, source: QProcess | None = None) -> None:
        if source is not None and source is not self.stress_process:
            return
        if (self.stress_process is not None and self.stress_started
                and self.stress_process.state() == QProcess.ProcessState.Running
                and self.scan_process is None):
            self._start_scan(under_load=True)

    def _gpu_ended_early(self, source: QProcess | None = None) -> None:
        if source is not None and source is not self.stress_process:
            return
        if self.stress_process is None:
            return
        self.stress_process = None
        self.scan_under_load = False
        self.gpu_test_interrupted = True
        if self.scan_process is None:
            self.status_label.setText(self.tr("GPU-Lasttest wurde beendet; PCIe-Link bleibt als Leerlaufwert markiert."))
        self._sync_ready_state()

    def _stop_gpu_test(self, source: QProcess | None = None) -> None:
        if source is not None and source is not self.stress_process:
            return
        process = self.stress_process
        if self.scan_under_load and self.scan_process is not None:
            self.gpu_test_interrupted = True
            self.scan_under_load = False
        self.stress_process = None
        if process is not None and process.state() != QProcess.ProcessState.NotRunning:
            process.kill()
        self._sync_ready_state()

    def _save_manual_ram(self, *_args) -> None:
        self.host.settings.setValue("hardware_checker/ram_model", self.ram_model.text().strip()[:160])
        self.host.settings.setValue("hardware_checker/ram_target_mts", self.ram_target.value())
        self.host.settings.sync()
        if self.report:
            self._populate(under_load=self.last_scan_under_load)

    def _populate(self, *, under_load: bool) -> None:
        rows: list[tuple[str, str, Assessment]] = []
        cpu = self.report.get("cpu", {})
        if isinstance(cpu, dict):
            rows.append(("info", "Prozessor", Assessment("info", str(cpu.get("model", "Unbekannt")), "Erkanntes CPU-Modell.")))
            smt = str(cpu.get("smt_state", "unknown"))
            topology = f"{cpu.get('cores') or '—'} Kerne · {cpu.get('logical') or '—'} Threads"
            if smt == "enabled":
                assessment = Assessment("pass", topology, "SMT / Hyper-Threading ist aktiv.")
            elif smt == "disabled":
                assessment = Assessment("fail", topology, "SMT wird unterstützt, ist aber deaktiviert.")
            elif smt == "unsupported":
                assessment = Assessment("info", topology, "Der Prozessor meldet keine SMT-Unterstützung.")
            else:
                assessment = Assessment("unknown", topology, "SMT-Zustand konnte nicht sicher bestimmt werden.")
            rows.append((assessment.state, "SMT / Hyper-Threading", assessment))
            virtualization = str(cpu.get("virtualization_state", "unknown"))
            virtualization_type = str(cpu.get("virtualization_type", ""))
            if virtualization == "enabled":
                assessment = Assessment("pass", virtualization_type, "AMD-V / SVM oder Intel VT-x ist aktiv.")
            elif virtualization == "disabled":
                assessment = Assessment("fail", virtualization_type, "AMD-V / SVM oder Intel VT-x ist nicht aktiv oder wird vom System nicht bereitgestellt.")
            else:
                assessment = Assessment("unknown", "Nicht prüfbar", "CPU-Virtualisierung konnte nicht sicher bestimmt werden.")
            rows.append((assessment.state, "CPU-Virtualisierung", assessment))
        board = self.report.get("board", "Unbekannt")
        board_text = str(board.get("display", "Unbekannt")) if isinstance(board, dict) else str(board)
        rows.append(("info", "Mainboard", Assessment("info", board_text, "Nur Identifikation; keine BIOS-Änderung.")))
        for index, gpu in enumerate(self.report.get("gpus", ()) if isinstance(self.report.get("gpus"), list) else ()):
            if isinstance(gpu, dict):
                load_target = bool(gpu.get("boot_vga")) or len(self.report.get("gpus", ())) == 1
                assessed = assess_pcie_link(gpu, under_load=under_load and load_target)
                title = f"{self.tr('Grafikkarte')} {index + 1} · PCIe"
                rows.append((assessed.state, title, Assessment(assessed.state, assessed.value, f"{gpu.get('name', '')} · {self._translate_detail(assessed.detail)}")))
        for index, drive in enumerate(self.report.get("nvmes", ()) if isinstance(self.report.get("nvmes"), list) else ()):
            if isinstance(drive, dict):
                assessed = assess_nvme_link(drive)
                title = f"{self.tr('NVMe-SSD')} {index + 1} · PCIe"
                rows.append((assessed.state, title, Assessment(assessed.state, assessed.value, f"{drive.get('name', '')} · {self._translate_detail(assessed.detail)}")))
        rows.append(("info", "Arbeitsspeicher", Assessment("info", str(self.report.get("memory_total", "Unbekannt")), self.ram_model.text().strip() or "Hersteller/Modell noch nicht angegeben.")))
        ram_assessment = assess_memory(self.memory_modules, expected_mts=self.ram_target.value())
        rows.append((ram_assessment.state, "RAM-Taktrate", ram_assessment))
        if self.memory_modules:
            names = sorted({" ".join(str(item.get(key, "")).strip() for key in ("manufacturer", "part")).strip() for item in self.memory_modules})
            detected = ", ".join(name for name in names if name and name.casefold() not in {"unknown", "not specified"})
            if detected and not self.ram_model.text().strip():
                self.ram_model.setText(detected[:160])
        self.table.setRowCount(len(rows))
        for row, (state, title, assessment) in enumerate(rows):
            icon, color = STATE_PRESENTATION.get(state, STATE_PRESENTATION["unknown"])
            values = (icon, self.tr(title), assessment.value, self._translate_detail(assessment.detail))
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                if column == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QColor(color))
                self.table.setItem(row, column, item)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.resizeRowsToContents()
        self._populate_cards()

    def refresh_language(self) -> None:
        if self.report:
            self._populate(under_load=self.last_scan_under_load)
        self.hardware_fix_panel.refresh_language()

    def _translate_detail(self, detail: str) -> str:
        dynamic = (
            (r"^Aktueller Link entspricht dem gemeldeten Maximum (.+)\.$", "Aktueller Link entspricht dem gemeldeten Maximum."),
            (r"^Unter Last unter dem gemeldeten Maximum (.+)\.$", "Unter Last unter dem gemeldeten Maximum."),
            (r"^Leerlaufwert; Maximum (.+)\. Für eine belastbare Bewertung Lasttest starten\.$", "Leerlaufwert; für eine belastbare Bewertung Lasttest starten."),
            (r"^Weniger Lanes als das gemeldete Maximum (.+)\.$", "Weniger Lanes als das gemeldete Maximum."),
            (r"^Eingetragener Sollwert: (.+)\.$", "Eingetragener Sollwert."),
            (r"^DMI-Modulangabe: (.+); bitte Sollwert prüfen\.$", "DMI-Modulangabe; bitte Sollwert prüfen."),
        )
        import re
        for pattern, source in dynamic:
            match = re.match(pattern, detail)
            if match:
                return f"{self.tr(source)} {match.group(1)}"
        return self.tr(detail)

    def stop_processes(self) -> None:
        processes = (self.scan_process, self.dmi_process, self.stress_process)
        # Clear identity before stopping: queued finish/error callbacks and
        # a previous test's deadlines must never act on a replacement process.
        self.scan_process = self.dmi_process = self.stress_process = None
        self.pending_gpu_test = False
        self.scan_under_load = False
        self.stress_started = False
        for process in processes:
            if process is not None and isValid(process):
                if process.state() != QProcess.ProcessState.NotRunning:
                    process.kill()
                    process.waitForFinished(500)
                process.deleteLater()


def build_page(host: QWidget) -> HardwareCheckerPage:
    return HardwareCheckerPage(host, getattr(host, "tr_static", lambda text: text))
