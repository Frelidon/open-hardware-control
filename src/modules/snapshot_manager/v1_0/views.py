#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Snapshot Manager's restored views, independent of process orchestration."""

from __future__ import annotations

import os
from PySide6.QtCore import QDateTime, QSignalBlocker, QTime, Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDateTimeEdit, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QSlider, QSpinBox, QTableWidget, QVBoxLayout, QWidget,
)
from .program_manager import ProgramManagerPanel


class SnapshotViewMixin:
    def _build(self) -> None:
        self.setWidgetResizable(True)
        self.setObjectName("snapshotManagerPage")
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(14)

        hero = QFrame(objectName="moduleHeroCard")
        hero_layout = QHBoxLayout(hero)
        hero_copy = QVBoxLayout()
        title = QLabel(self.tr("Snapshot-Manager"), objectName="heroTitle")
        intro = QLabel(self.tr(
            "Erkennt Linux-Snapshot-Systeme, begrenzt Btrfs-Aufräumlast und verhindert neue automatische Läufe während Spielen."
        ))
        intro.setWordWrap(True)
        hero_copy.addWidget(title)
        hero_copy.addWidget(intro)
        hero_layout.addLayout(hero_copy, 1)
        self.hero_state = QLabel(self.tr("DESKTOP · AUTOMATIK BEREIT"))
        self.hero_state.setObjectName("snapshotStateBadge")
        self.hero_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hero_state.setMinimumWidth(240)
        hero_layout.addWidget(self.hero_state)
        layout.addWidget(hero)

        columns = QHBoxLayout()
        columns.setSpacing(14)
        columns.addWidget(self._build_automation_card(), 3)
        columns.addWidget(self._build_system_card(), 2)
        layout.addLayout(columns)

        manual = QFrame(objectName="settingsCard")
        manual_layout = QVBoxLayout(manual)
        manual_layout.addWidget(self._section_title("Manuelle Sperre"))
        explanation = QLabel(self.tr(
            "Blockiert neue automatische Snapshots und geplante Bereinigungen. Bereits laufende Btrfs-Kernelarbeit wird nur gedrosselt, nicht gewaltsam beendet."
        ))
        explanation.setWordWrap(True)
        explanation.setObjectName("muted")
        manual_layout.addWidget(explanation)
        deadline = QFrame(objectName="snapshotTimePicker")
        deadline_layout = QVBoxLayout(deadline)
        deadline_layout.setContentsMargins(12, 10, 12, 10)
        deadline_layout.setSpacing(8)
        deadline_header = QHBoxLayout()
        deadline_header.addWidget(QLabel(self.tr("Bis Datum/Uhrzeit blockieren")))
        deadline_header.addStretch()
        self.until_time_value = QLabel(objectName="snapshotTimeValue")
        deadline_header.addWidget(self.until_time_value)
        deadline_layout.addLayout(deadline_header)
        initial_deadline = QDateTime.currentDateTime().addSecs(7200)
        initial_deadline.setTime(QTime(
            initial_deadline.time().hour(), (initial_deadline.time().minute() // 5) * 5,
        ))
        self.until_edit = QDateTimeEdit(initial_deadline)
        self.until_edit.setCalendarPopup(True)
        self.until_edit.setDisplayFormat("dd.MM.yyyy · HH:mm")
        self.until_edit.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))
        deadline_layout.addWidget(self.until_edit)
        time_sliders = QGridLayout()
        time_sliders.setHorizontalSpacing(10)
        self.until_hour_slider = QSlider(Qt.Orientation.Horizontal)
        self.until_hour_slider.setObjectName("snapshotTimeSlider")
        self.until_hour_slider.setRange(0, 23)
        self.until_minute_slider = QSlider(Qt.Orientation.Horizontal)
        self.until_minute_slider.setObjectName("snapshotTimeSlider")
        self.until_minute_slider.setRange(0, 11)
        time_sliders.addWidget(QLabel("HH"), 0, 0)
        time_sliders.addWidget(QLabel("00"), 0, 1)
        time_sliders.addWidget(self.until_hour_slider, 0, 2)
        time_sliders.addWidget(QLabel("23"), 0, 3)
        time_sliders.addWidget(QLabel("MM"), 1, 0)
        time_sliders.addWidget(QLabel("00"), 1, 1)
        time_sliders.addWidget(self.until_minute_slider, 1, 2)
        time_sliders.addWidget(QLabel("55"), 1, 3)
        time_sliders.setColumnStretch(2, 1)
        deadline_layout.addLayout(time_sliders)
        self.until_edit.dateTimeChanged.connect(self._sync_manual_time_sliders)
        self.until_hour_slider.valueChanged.connect(self._update_manual_time_from_sliders)
        self.until_minute_slider.valueChanged.connect(self._update_manual_time_from_sliders)
        self._sync_manual_time_sliders(initial_deadline)
        manual_layout.addWidget(deadline)

        manual_actions = QHBoxLayout()
        self.pause_hour_button = QPushButton(self.tr("Für 1 Stunde blockieren"))
        self.pause_hour_button.clicked.connect(lambda: self.block_until(QDateTime.currentDateTime().addSecs(3600)))
        self.until_button = QPushButton(self.tr("Bis Datum/Uhrzeit blockieren"))
        self.until_button.clicked.connect(lambda: self.block_until(self.until_edit.dateTime()))
        self.forever_button = QPushButton(self.tr("Dauerhaft blockieren"))
        self.forever_button.setObjectName("dangerAction")
        self.forever_button.clicked.connect(self.block_forever)
        self.resume_button = QPushButton(self.tr("Jetzt fortsetzen"))
        self.resume_button.setObjectName("primaryAction")
        self.resume_button.clicked.connect(self.resume_now)
        for widget in (self.pause_hour_button, self.until_button, self.forever_button, self.resume_button):
            manual_actions.addWidget(widget)
        manual_layout.addLayout(manual_actions)
        self.manual_status = QLabel(self.tr("Keine manuelle Sperre aktiv."))
        self.manual_status.setObjectName("infoText")
        manual_layout.addWidget(self.manual_status)
        layout.addWidget(manual)

        snapshots = QFrame(objectName="settingsCard")
        snapshots_layout = QVBoxLayout(snapshots)
        snapshot_header = QHBoxLayout()
        snapshot_header.addWidget(self._section_title("Snapshots und Wiederherstellung"))
        snapshot_header.addStretch()
        self.config_combo = QComboBox()
        self.config_combo.setMinimumWidth(190)
        self.snapshot_refresh = QPushButton(self.tr("Liste mit Administratorrechten laden"))
        self.snapshot_refresh.clicked.connect(self.load_snapshots)
        self.snapshot_filter = QComboBox()
        self.snapshot_filter.addItem(self.tr("Alle Snapshots"), "all")
        self.snapshot_filter.addItem(self.tr("Von Open Hardware Control"), "ohc")
        self.snapshot_filter.addItem(self.tr("Vom System oder anderen Programmen"), "system")
        self.snapshot_filter.currentIndexChanged.connect(self._render_snapshot_rows)
        snapshot_header.addWidget(self.config_combo)
        snapshot_header.addWidget(self.snapshot_filter)
        snapshot_header.addWidget(self.snapshot_refresh)
        snapshots_layout.addLayout(snapshot_header)
        create_row = QHBoxLayout()
        self.snapshot_description = QLineEdit()
        self.snapshot_description.setMaxLength(160)
        self.snapshot_description.setPlaceholderText(self.tr("Beschreibung für den neuen Snapshot"))
        self.snapshot_description.setText(self.tr("Manueller Snapshot aus Open Hardware Control"))
        self.snapshot_create = QPushButton(self.tr("Snapshot jetzt erstellen"))
        self.snapshot_create.setObjectName("primaryAction")
        self.snapshot_create.clicked.connect(self.create_snapshot_now)
        create_row.addWidget(self.snapshot_description, 1)
        create_row.addWidget(self.snapshot_create)
        snapshots_layout.addLayout(create_row)
        self.snapshot_table = QTableWidget(0, 6)
        self.snapshot_table.setObjectName("diagnosticTable")
        self.snapshot_table.setHorizontalHeaderLabels(tuple(map(self.tr, (
            "Nr.", "Erstellt", "Beschreibung", "Herkunft", "Bereinigung", "Status",
        ))))
        self.snapshot_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.snapshot_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.snapshot_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.snapshot_table.itemSelectionChanged.connect(self._snapshot_selection_changed)
        self.snapshot_table.verticalHeader().hide()
        self.snapshot_table.setMinimumHeight(220)
        header = self.snapshot_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        snapshots_layout.addWidget(self.snapshot_table)
        snapshot_actions = QHBoxLayout()
        snapshot_actions.setSpacing(10)
        status_copy = QVBoxLayout()
        self.snapshot_action_status = QLabel(self.tr("Snapshot auswählen, um ihn zu löschen."))
        self.snapshot_action_status.setObjectName("infoText")
        self.snapshot_export_hint = QLabel(self.tr(
            "Der JSON-Export enthält Snapshot-Metadaten, nicht den gesicherten Dateiinhalt."
        ))
        self.snapshot_export_hint.setObjectName("muted")
        self.snapshot_export_hint.setWordWrap(True)
        status_copy.addWidget(self.snapshot_action_status)
        status_copy.addWidget(self.snapshot_export_hint)
        snapshot_actions.addLayout(status_copy, 1)
        self.snapshot_export = QPushButton(self.tr("Liste als JSON exportieren"))
        self.snapshot_export.setObjectName("snapshotSecondaryAction")
        self.snapshot_export.setEnabled(False)
        self.snapshot_export.clicked.connect(self.export_snapshot_list)
        self.snapshot_delete = QPushButton(self.tr("Ausgewählten Snapshot löschen"))
        self.snapshot_delete.setObjectName("dangerAction")
        self.snapshot_delete.setEnabled(False)
        self.snapshot_delete.clicked.connect(self.delete_selected_snapshot)
        snapshot_actions.addWidget(self.snapshot_export)
        snapshot_actions.addWidget(self.snapshot_delete)
        snapshots_layout.addLayout(snapshot_actions)
        restore = QLabel(self.tr(
            "Wiederherstellen: Einen Snapshot zuerst schreibgeschützt einhängen und Dateien prüfen. Ein vollständiger Snapper-Rollback verändert das Startsystem und bleibt deshalb bewusst außerhalb eines Ein-Klick-Knopfs."
        ))
        restore.setWordWrap(True)
        restore.setObjectName("warningText")
        snapshots_layout.addWidget(restore)
        layout.addWidget(snapshots)
        layout.addStretch()
        self.setWidget(body)

    def _section_title(self, text: str) -> QLabel:
        label = QLabel(self.tr(text))
        label.setObjectName("sectionTitle")
        return label

    def _sync_manual_time_sliders(self, deadline: QDateTime) -> None:
        """Synchronize the graphical time tracks."""

        selected = deadline.time()
        with QSignalBlocker(self.until_hour_slider), QSignalBlocker(self.until_minute_slider):
            self.until_hour_slider.setValue(selected.hour())
            self.until_minute_slider.setValue(min(11, selected.minute() // 5))
        self.until_time_value.setText(selected.toString("HH:mm"))

    def _update_manual_time_from_sliders(self, _value: int = 0) -> None:
        selected = self.until_edit.dateTime()
        selected.setTime(QTime(
            self.until_hour_slider.value(), self.until_minute_slider.value() * 5,
        ))
        self.until_edit.setDateTime(selected)
        self._sync_manual_time_sliders(self.until_edit.dateTime())

    def _build_automation_card(self) -> QFrame:
        card = QFrame(objectName="settingsCard")
        layout = QVBoxLayout(card)
        layout.addWidget(self._section_title("Spiel- und Leistungsautomatik"))
        self.auto_check = QCheckBox(self.tr("Snapshot-Arbeit bei Spielen automatisch pausieren"))
        self.auto_check.setChecked(self.policy.automatic_game_pause)
        self.fullscreen_check = QCheckBox(self.tr("KDE-Vollbildanwendungen als Spielsignal verwenden"))
        self.fullscreen_check.setChecked(self.policy.fullscreen_signal)
        self.load_check = QCheckBox(self.tr("CPU- und GPU-Last als vorsichtigen Zusatz verwenden"))
        self.load_check.setChecked(self.policy.load_heuristic)
        for checkbox in (self.auto_check, self.fullscreen_check, self.load_check):
            checkbox.setObjectName("snapshotToggle")
            checkbox.toggled.connect(self._automation_option_changed)
            layout.addWidget(checkbox)
        layout.addSpacing(4)
        thresholds = QGridLayout()
        thresholds.setHorizontalSpacing(10)
        thresholds.setVerticalSpacing(10)
        cpu_card, self.cpu_threshold = self._metric_control(
            "CPU-Erkennungsschwelle", "Pausensignal bei hoher Mehrkernlast · kein CPU-Limit",
            self.policy.cpu_threshold, 30, 100, " %",
        )
        gpu_card, self.gpu_threshold = self._metric_control(
            "GPU-Schwelle", "Zusätzliche Grafiklast",
            self.policy.gpu_threshold, 30, 100, " %",
        )
        desktop_card, self.desktop_rate = self._metric_control(
            "Desktop-Limit", "Normale Btrfs-Aufräumrate",
            self.policy.desktop_kbps // 1024, 8, 64, " MiB/s",
        )
        game_card, self.game_rate = self._metric_control(
            "Spiel-Limit", "Schonende Rate während eines Spiels",
            self.policy.game_kbps // 1024, 1, 64, " MiB/s",
        )
        for spin in (self.cpu_threshold, self.gpu_threshold, self.desktop_rate, self.game_rate):
            spin.valueChanged.connect(self.save_policy)
        thresholds.addWidget(cpu_card, 0, 0)
        thresholds.addWidget(gpu_card, 0, 1)
        thresholds.addWidget(desktop_card, 1, 0)
        thresholds.addWidget(game_card, 1, 1)
        core_card, self.snapshot_core_limit = self._metric_control(
            "Maximale logische CPUs", "Snapper läuft nur auf dieser kleinen CPU-Gruppe",
            min(self.policy.cpu_core_limit, max(1, os.cpu_count() or 1)),
            1, min(8, max(1, os.cpu_count() or 1)), "",
        )
        percent_card, self.snapshot_cpu_percent = self._metric_control(
            "CPU-Anteil je CPU", "Harte systemd-Grenze je ausgewählter logischer CPU",
            self.policy.cpu_percent_per_core, 10, 100, " %",
        )
        for spin in (self.snapshot_core_limit, self.snapshot_cpu_percent):
            spin.valueChanged.connect(self.save_policy)
        thresholds.addWidget(core_card, 2, 0)
        thresholds.addWidget(percent_card, 2, 1)
        layout.addLayout(thresholds)
        resource_row = QHBoxLayout()
        self.resource_status = QLabel(self.tr(
            "Standard: 2 CPUs × 50 % = höchstens 100 % eines Prozessorkerns. "
            "Die Grenze wird beim Fortsetzen automatisch gesetzt."
        ))
        self.resource_status.setObjectName("infoText")
        self.resource_status.setWordWrap(True)
        self.resource_apply = QPushButton(self.tr("Ressourcenlimit jetzt anwenden"))
        self.resource_apply.clicked.connect(self.apply_resource_limits_now)
        resource_row.addWidget(self.resource_status, 1)
        resource_row.addWidget(self.resource_apply)
        layout.addLayout(resource_row)
        program_row = QHBoxLayout()
        self.process_names = QLineEdit()
        self.process_names.setReadOnly(True)
        self.process_names.setPlaceholderText(self.tr("Noch kein Programm ausgewählt"))
        self.process_names.setText(str(self.host.settings.value("snapshot_manager/process_names", "") or ""))
        self.program_manager_button = QPushButton(self.tr("Programme verwalten …"))
        self.program_manager_button.clicked.connect(self._toggle_program_manager)
        program_row.addWidget(self.process_names, 1)
        program_row.addWidget(self.program_manager_button)
        layout.addLayout(program_row)
        self.program_manager = ProgramManagerPanel(
            self.tr, self.process_names.text(),
            self.host.settings.value("snapshot_manager/process_paths", ""),
            self._program_selection_changed, card,
        )
        self.program_manager.close_button.clicked.connect(self._toggle_program_manager)
        self.program_manager.hide()
        layout.addWidget(self.program_manager)
        auth_row = QHBoxLayout()
        self.auth_state = QLabel("")
        self.auth_state.setWordWrap(True)
        self.grant_button = QPushButton(self.tr("Automatik einmalig autorisieren"))
        self.grant_button.clicked.connect(self.toggle_authorization)
        auth_row.addWidget(self.auth_state, 1)
        auth_row.addWidget(self.grant_button)
        layout.addLayout(auth_row)
        self.activity_status = QLabel(self.tr("Aktivität wird gelesen …"))
        self.activity_status.setObjectName("infoText")
        self.activity_status.setWordWrap(True)
        layout.addWidget(self.activity_status)
        self._refresh_authorization_state()
        return card

    def _metric_control(
        self, title: str, hint: str, value: int, minimum: int, maximum: int,
        suffix: str,
    ) -> tuple[QFrame, QSpinBox]:
        card = QFrame(objectName="snapshotMetricCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 11)
        card_layout.setSpacing(7)
        heading = QHBoxLayout()
        copy = QVBoxLayout()
        label = QLabel(self.tr(title), objectName="snapshotMetricLabel")
        description = QLabel(self.tr(hint), objectName="snapshotMetricHint")
        description.setWordWrap(True)
        copy.addWidget(label)
        copy.addWidget(description)
        heading.addLayout(copy, 1)
        spin = QSpinBox()
        spin.setObjectName("snapshotMetricSpin")
        spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        spin.setRange(minimum, maximum)
        spin.setSuffix(suffix)
        spin.setValue(value)
        spin.setMinimumWidth(105)
        heading.addWidget(spin, 0, Qt.AlignmentFlag.AlignTop)
        card_layout.addLayout(heading)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setObjectName("snapshotMetricSlider")
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)
        card_layout.addWidget(slider)
        return card, spin

    def _build_system_card(self) -> QFrame:
        card = QFrame(objectName="settingsCard")
        layout = QVBoxLayout(card)
        top = QHBoxLayout()
        top.addWidget(self._section_title("Erkanntes System"))
        top.addStretch()
        refresh = QPushButton(self.tr("Neu erkennen"))
        refresh.clicked.connect(self.refresh_system)
        top.addWidget(refresh)
        layout.addLayout(top)
        self.os_label = QLabel(self.tr("Betriebssystem wird erkannt …"))
        self.os_label.setObjectName("cardValue")
        layout.addWidget(self.os_label)
        self.backend_table = QTableWidget(0, 2)
        self.backend_table.setObjectName("compactTable")
        self.backend_table.setHorizontalHeaderLabels(tuple(map(self.tr, ("System", "Zustand"))))
        self.backend_table.verticalHeader().hide()
        self.backend_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.backend_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.backend_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.backend_table.setMinimumHeight(190)
        layout.addWidget(self.backend_table)
        self.discard_label = QLabel(self.tr("Btrfs-Aufräumstatus wird gelesen …"))
        self.discard_label.setObjectName("muted")
        self.discard_label.setWordWrap(True)
        layout.addWidget(self.discard_label)
        self.snapper_setup_status = QLabel(self.tr(
            "Wenn Snapper installiert, aber noch nicht eingerichtet ist, kann OHC eine feste Root-Konfiguration anlegen."
        ))
        self.snapper_setup_status.setObjectName("muted")
        self.snapper_setup_status.setWordWrap(True)
        layout.addWidget(self.snapper_setup_status)
        self.snapper_setup_button = QPushButton(self.tr("Snapper für das Root-Dateisystem einrichten"))
        self.snapper_setup_button.clicked.connect(self.setup_snapper_root)
        self.snapper_setup_button.hide()
        layout.addWidget(self.snapper_setup_button)
        return card
