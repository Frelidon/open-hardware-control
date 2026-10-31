#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Automation Center UI and read-only trigger monitor."""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import shlex
import sys
import time
import uuid

from PySide6.QtCore import QObject, QProcess, QTimer, Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from window_diagnostics import track_qprocess
from modules.platform_support.v1_0 import helper_command
from .model import AutomationRule, winning_process_rule

MAX_RULES = 64
TRIGGER_LABELS = {
    "process": "Anwendung läuft",
    "game": "Spiel läuft",
    "time": "Feste Uhrzeit",
    "interval": "Alle … Minuten",
}


class AutomationController(QObject):
    """Probe running processes asynchronously and apply only existing OHC profiles."""

    def __init__(self, host, page: "AutomationPage") -> None:
        super().__init__(host)
        self.host = host
        self.page = page
        self.process = track_qprocess(QProcess(self))
        self.process.setObjectName("ohcDesignAutomationProbe")
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.process.finished.connect(self._probe_finished)
        self.timer = QTimer(self)
        self.timer.setInterval(5_000)
        self.timer.timeout.connect(self.poll)
        self.active_rule_id = ""
        self.previous_profile_id = ""
        self._last_one_shot: dict[str, str] = {}

    def start(self) -> None:
        if (os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1"
                or getattr(self.host, "exit_cleanup_in_progress", False)
                or (hasattr(self.host, "feature_enabled") and not self.host.feature_enabled("automation"))):
            return
        self.timer.start()
        self.poll()

    def poll(self) -> None:
        if (getattr(self.host, "exit_cleanup_in_progress", False)
                or (hasattr(self.host, "feature_enabled") and not self.host.feature_enabled("automation"))):
            return
        if self.process.state() != QProcess.ProcessState.NotRunning:
            return
        helper = Path(__file__).with_name("probe.py")
        program, arguments = helper_command(helper)
        self.process.start(program, arguments)

    def _probe_finished(self, _code: int, _status) -> None:
        try:
            payload = json.loads(bytes(self.process.readAllStandardOutput()).decode("utf-8", "replace"))
            names = tuple(str(item) for item in payload.get("processes", []))
        except (ValueError, TypeError):
            names = ()
        self.evaluate(names)

    def evaluate(self, process_names: tuple[str, ...]) -> None:
        if (getattr(self.host, "exit_cleanup_in_progress", False)
                or (hasattr(self.host, "feature_enabled") and not self.host.feature_enabled("automation"))):
            return
        rules = tuple(self.page.rules)
        winner = winning_process_rule(rules, process_names)
        if winner is not None:
            if winner.rule_id != self.active_rule_id:
                self._activate(winner, sustained=True)
            return
        if self.active_rule_id:
            active = next((rule for rule in rules if rule.rule_id == self.active_rule_id), None)
            self.active_rule_id = ""
            if active and active.restore_previous and self.previous_profile_id:
                if self._apply_profile(self.previous_profile_id, "Vorheriges Profil"):
                    self.page.set_runtime_status("Anwendung beendet · vorheriges Gesamtprofil wiederhergestellt.", "ready")
            self.previous_profile_id = ""

        now = datetime.now()
        for rule in sorted(rules, key=lambda item: item.priority, reverse=True):
            if not rule.enabled or rule.trigger not in {"time", "interval"}:
                continue
            if rule.trigger == "time":
                marker = now.strftime("%Y-%m-%d %H:%M")
                due = now.strftime("%H:%M") == rule.trigger_value
            else:
                minutes = max(1, int(rule.trigger_value))
                marker = str(int(time.time() // (minutes * 60)))
                due = True
            if due and self._last_one_shot.get(rule.rule_id) != marker:
                self._last_one_shot[rule.rule_id] = marker
                self._activate(rule, sustained=False)
                break

    def _activate(self, rule: AutomationRule, *, sustained: bool) -> None:
        if not rule.profile_id:
            self.page.set_runtime_status(self.page.tr_format("Regel „{name}“ hat noch kein Gesamtprofil.", name=rule.name), "warning")
            return
        previous_profile_id = str(getattr(self.host, "current_profile_id", ""))
        if not self._apply_profile(rule.profile_id, rule.name):
            self.page.set_runtime_status(self.page.tr_format("Regel „{name}“ verweist auf ein nicht mehr vorhandenes Profil.", name=rule.name), "warning")
            return
        if sustained:
            if not self.active_rule_id:
                self.previous_profile_id = previous_profile_id
            self.active_rule_id = rule.rule_id
        self.page.set_runtime_status(self.page.tr_format("Aktiv: {name} · Gesamtprofil angewendet.", name=rule.name), "active")
        if hasattr(self.host, "log_user_action"):
            self.host.log_user_action("AUTOMATION", f"Regel '{rule.name}' · Profil-ID={rule.profile_id}")

    def _apply_profile(self, profile_id: str, name: str) -> bool:
        profile = next((item for item in self.host.all_profiles() if str(item.get("id", "")) == profile_id), None)
        if profile is None:
            return False
        payload = profile.get("payload", {}) if isinstance(profile, dict) else {}
        self.host.apply_profile_by_id(profile_id)
        if isinstance(payload, dict) and "rgb" in payload and hasattr(self.host, "start_rgb_profile_automatically"):
            self.host.start_rgb_profile_automatically(name)
        display_studio = getattr(self.host, "thermalright_display_studio", None)
        if isinstance(payload, dict) and "levita_display" in payload and display_studio is not None and hasattr(display_studio, "activate_staged_profile_design"):
            display_studio.activate_staged_profile_design()
        return True

    def shutdown(self) -> None:
        self.timer.stop()
        self.active_rule_id = ""
        self.previous_profile_id = ""
        self._last_one_shot.clear()
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(300):
                self.process.kill()


class AutomationPage(QWidget):
    def __init__(self, host) -> None:
        super().__init__()
        self.host = host
        self.rules = self._load_rules()
        self._build()

    def _load_rules(self) -> list[AutomationRule]:
        try:
            raw = json.loads(str(self.host.settings.value("automation/rules_json", "[]")))
        except (ValueError, TypeError):
            raw = []
        rules = [AutomationRule.from_mapping(item) for item in raw[:MAX_RULES]] if isinstance(raw, list) else []
        return [rule for rule in rules if rule is not None]

    def tr_format(self, source: str, **values: object) -> str:
        return self.host.tr_static(source).format(**values)

    def _save(self) -> None:
        self.host.settings.setValue("automation/rules_json", json.dumps([rule.to_mapping() for rule in self.rules]))

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)
        root.addWidget(self.host.make_module_hero(
            "⌁", "Automationszentrale",
            "Gesamtprofile zeitgesteuert oder beim Start einer Anwendung beziehungsweise eines Spiels wechseln.",
            "Profile · RGB · LCD",
        ))

        summary = QFrame(); summary.setObjectName("automationSummaryCard")
        summary_layout = QGridLayout(summary)
        self.enabled_summary = QLabel(); self.enabled_summary.setObjectName("metricValue")
        self.runtime_status = QLabel("Bereit · Anwendungen werden lokal und ohne Netzwerkzugriff erkannt.")
        self.runtime_status.setWordWrap(True); self.runtime_status.setObjectName("muted")
        summary_layout.addWidget(QLabel("AKTIVE REGELN"), 0, 0)
        summary_layout.addWidget(self.enabled_summary, 1, 0)
        summary_layout.addWidget(self.runtime_status, 0, 1, 2, 1)
        root.addWidget(summary)

        workspace = QFrame(); workspace.setObjectName("automationWorkspaceCard")
        workspace_layout = QVBoxLayout(workspace)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(("An", "Name", "Auslöser", "Wert", "Gesamtprofil", "Priorität"))
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.load_selection)
        self.table.horizontalHeader().setStretchLastSection(True)
        workspace_layout.addWidget(self.table)

        editor = QGroupBox("Regel bearbeiten")
        form = QFormLayout(editor)
        self.name_input = QLineEdit(); self.name_input.setMaxLength(80)
        self.name_input.setPlaceholderText("Zum Beispiel Spieleabend")
        self.trigger_combo = QComboBox()
        for key, label in TRIGGER_LABELS.items(): self.trigger_combo.addItem(label, key)
        self.trigger_combo.currentIndexChanged.connect(self._update_trigger_help)
        self.value_input = QLineEdit(); self.value_input.setMaxLength(260)
        self.value_help = QLabel(); self.value_help.setWordWrap(True); self.value_help.setObjectName("muted")
        self.profile_combo = QComboBox()
        self.priority_spin = QSpinBox(); self.priority_spin.setRange(0, 100); self.priority_spin.setValue(50)
        self.enabled_check = QCheckBox("Regel aktivieren"); self.enabled_check.setChecked(True)
        self.restore_check = QCheckBox("Nach Programmende vorheriges Profil wiederherstellen"); self.restore_check.setChecked(True)
        form.addRow("Name", self.name_input); form.addRow("Auslöser", self.trigger_combo)
        form.addRow("Auslöserwert", self.value_input); form.addRow(self.value_help)
        form.addRow("Gesamtprofil", self.profile_combo); form.addRow("Priorität", self.priority_spin)
        form.addRow(self.enabled_check); form.addRow(self.restore_check)
        note = QLabel("Ein Gesamtprofil bündelt Kühlung, RGB, LCD, Display-Effekte und Design. Dadurch schaltet eine Regel alle gewünschten Bereiche konsistent und über die vorhandenen Sicherheitsprüfungen um. Für automatisches RGB muss im Profil die Startprofil-Automatik ausdrücklich aktiviert sein.")
        note.setWordWrap(True); note.setObjectName("inlineNotice"); form.addRow(note)
        buttons = QHBoxLayout()
        add_button = QPushButton("Als neue Regel speichern"); add_button.setObjectName("primaryAction")
        update_button = QPushButton("Ausgewählte Regel aktualisieren")
        delete_button = QPushButton("Ausgewählte Regel löschen"); delete_button.setObjectName("dangerAction")
        add_button.clicked.connect(self.add_rule); update_button.clicked.connect(self.update_rule); delete_button.clicked.connect(self.delete_rule)
        buttons.addWidget(add_button); buttons.addWidget(update_button); buttons.addWidget(delete_button); buttons.addStretch()
        form.addRow(buttons)
        workspace_layout.addWidget(editor)
        root.addWidget(workspace, 1)

        self._build_mangohud(root)
        self.refresh_profiles(); self.refresh_table(); self._update_trigger_help()

    def _build_mangohud(self, root: QVBoxLayout) -> None:
        box = QGroupBox("MangoHud pro Spiel")
        form = QFormLayout(box)
        self.game_path_input = QLineEdit(); self.game_path_input.setPlaceholderText("/pfad/zum/spiel")
        self.overlay_preset_combo = QComboBox()
        self.overlay_preset_combo.addItem("Kompakt · FPS, GPU, CPU", "compact")
        self.overlay_preset_combo.addItem("Ausführlich · FPS, Temperaturen, Auslastung, RAM", "detailed")
        self.overlay_preset_combo.addItem("Nur Bildrate und Frametime", "fps")
        create_button = QPushButton("MangoHud-Startoption erzeugen")
        create_button.clicked.connect(self.generate_mangohud_option)
        self.mangohud_result = QLineEdit(); self.mangohud_result.setReadOnly(True)
        self.mangohud_result.setPlaceholderText("Hier erscheint die sichere Startoption für Steam oder einen Launcher.")
        note = QLabel("OHC hängt sich nicht nachträglich in ein laufendes Spiel ein. Die erzeugte Startoption aktiviert MangoHud sauber beim nächsten Spielstart.")
        note.setWordWrap(True); note.setObjectName("muted")
        form.addRow("Spielpfad", self.game_path_input); form.addRow("Overlay", self.overlay_preset_combo)
        form.addRow(create_button); form.addRow("Startoption", self.mangohud_result); form.addRow(note)
        root.addWidget(box)

    def generate_mangohud_option(self) -> None:
        path = self.game_path_input.text().strip()
        if not path.startswith("/") or len(path) > 260 or "\n" in path:
            self.mangohud_result.setText("Bitte einen absoluten Spielpfad ohne Zeilenumbruch angeben.")
            return
        preset = str(self.overlay_preset_combo.currentData())
        options = {
            "compact": "fps,gpu_stats,cpu_stats,position=top-left",
            "detailed": "fps,frametime,gpu_stats,gpu_temp,cpu_stats,cpu_temp,ram,vram,position=top-left",
            "fps": "fps,frametime,position=top-left",
        }[preset]
        config_dir = Path(self.host.app_config_dir) / "mangohud"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / f"{preset}.conf"
        config_path.write_text(options.replace(",", "\n") + "\n", encoding="utf-8")
        self.mangohud_result.setText(
            f"MANGOHUD_CONFIGFILE={shlex.quote(str(config_path))} mangohud {shlex.quote(path)}"
        )

    def showEvent(self, event) -> None:  # noqa: N802 - Qt API
        self.refresh_profiles()
        super().showEvent(event)

    def refresh_profiles(self) -> None:
        current = self.profile_combo.currentData() if self.profile_combo.count() else ""
        self.profile_combo.clear()
        self.profile_combo.addItem("Profil auswählen …", "")
        for profile in self.host.all_profiles():
            self.profile_combo.addItem(str(profile.get("name", "Profil")), str(profile.get("id", "")))
        self.profile_combo.setCurrentIndex(max(0, self.profile_combo.findData(current)))

    def _update_trigger_help(self) -> None:
        trigger = str(self.trigger_combo.currentData())
        hints = {
            "process": "Dateiname des Programms, zum Beispiel blender oder obs.",
            "game": "Prozessname des Spiels, zum Beispiel game.x86_64. Es werden keine Fensterinhalte gelesen.",
            "time": "Uhrzeit im Format HH:MM, zum Beispiel 18:30.",
            "interval": "Abstand in Minuten von 1 bis 1440.",
        }
        self.value_help.setText(hints[trigger])
        self.restore_check.setEnabled(trigger in {"process", "game"})

    def _editor_rule(self, rule_id: str | None = None) -> AutomationRule | None:
        payload = {
            "rule_id": rule_id or f"rule-{uuid.uuid4().hex}", "name": self.name_input.text(),
            "enabled": self.enabled_check.isChecked(), "trigger": self.trigger_combo.currentData(),
            "trigger_value": self.value_input.text(), "profile_id": self.profile_combo.currentData(),
            "priority": self.priority_spin.value(), "restore_previous": self.restore_check.isChecked(),
        }
        return AutomationRule.from_mapping(payload)

    def add_rule(self) -> None:
        if len(self.rules) >= MAX_RULES: self.set_runtime_status("Maximal 64 Regeln sind zulässig.", "warning"); return
        rule = self._editor_rule()
        if rule is None: return
        self.rules.append(rule); self._save(); self.refresh_table(); self.set_runtime_status("Neue Automationsregel gespeichert.", "ready")

    def update_rule(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.rules): self.set_runtime_status("Bitte zuerst eine Regel auswählen.", "warning"); return
        rule = self._editor_rule(self.rules[row].rule_id)
        if rule is None: return
        self.rules[row] = rule; self._save(); self.refresh_table(); self.table.selectRow(row)

    def delete_rule(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.rules): return
        self.rules.pop(row); self._save(); self.refresh_table(); self.set_runtime_status("Automationsregel gelöscht.", "ready")

    def load_selection(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.rules): return
        rule = self.rules[row]
        self.name_input.setText(rule.name); self.trigger_combo.setCurrentIndex(max(0, self.trigger_combo.findData(rule.trigger)))
        self.value_input.setText(rule.trigger_value); self.profile_combo.setCurrentIndex(max(0, self.profile_combo.findData(rule.profile_id)))
        self.priority_spin.setValue(rule.priority); self.enabled_check.setChecked(rule.enabled); self.restore_check.setChecked(rule.restore_previous)

    def refresh_table(self) -> None:
        self.table.setRowCount(len(self.rules))
        profile_names = {str(item.get("id", "")): str(item.get("name", "Profil")) for item in self.host.all_profiles()}
        for row, rule in enumerate(self.rules):
            values = ("●" if rule.enabled else "○", rule.name, self.host.tr_static(TRIGGER_LABELS[rule.trigger]), rule.trigger_value, profile_names.get(rule.profile_id, self.host.tr_static("Nicht gewählt")), str(rule.priority))
            for column, value in enumerate(values): self.table.setItem(row, column, QTableWidgetItem(value))
        self.enabled_summary.setText(str(sum(rule.enabled for rule in self.rules)))

    def set_runtime_status(self, text: str, state: str) -> None:
        self.runtime_status.setText(self.host.tr_static(text))
        self.runtime_status.setProperty("automationState", state)
        self.runtime_status.style().unpolish(self.runtime_status); self.runtime_status.style().polish(self.runtime_status)


def build_page(host) -> AutomationPage:
    page = AutomationPage(host)
    host.design_automation_controller = AutomationController(host, page)
    QTimer.singleShot(0, host.design_automation_controller, host.design_automation_controller.start)
    return page
