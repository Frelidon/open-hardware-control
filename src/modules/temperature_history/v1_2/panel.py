#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resizable temperature-history UI and read-only sampling integration."""

from __future__ import annotations

import json
from datetime import datetime

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox, QFrame, QHeaderView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from temperature_utils import celsius_to_display, temperature_symbol

from .chart import TemperatureHistoryChart
from .gauge import TemperatureGauge
from .model import TemperatureHistoryBuffer
from .sensors import read_linux_temperature_sensors
from .report_dialog import TemperatureReportDialog
from .selection import SensorTree, sensor_icon
from .readings import ReadingList


class TemperatureRecordingMixin:
    """Compose and update the detailed recording page without owning controls."""

    def initialize_temperature_recording(self) -> None:
        self.temperature_history = TemperatureHistoryBuffer(max_age_seconds=86_400, max_samples=28_800)
        self.temperature_sensor_catalog: dict[str, tuple[str, str, str]] = {
            "cpu": ("CPU", "cpu", "OHC CPU-Sensor"),
            "gpu": ("GPU", "gpu", "OHC GPU-Sensor"),
            "liquid": ("Kühlmittel", "cooling", "Kühlgerät"),
        }
        self.temperature_sensor_signature: tuple[str, ...] = ()

    def install_temperature_recording_navigation(self, page_item) -> None:
        """Attach the two cooling views as explicit sidebar children."""
        self.nav_cooling_controls = page_item(
            "cooling_controls", "Steuerung & Profile", 1, fixed=True
        )
        self.nav_temperature_recording = page_item(
            "temperature_recording", "Temperaturaufzeichnung", 1, fixed=True
        )
        self.restore_temperature_recording_navigation()

    def restore_temperature_recording_navigation(self) -> None:
        self.nav_nzxt.addChild(self.nav_cooling_controls)
        self.nav_nzxt.addChild(self.nav_temperature_recording)
        self.nav_nzxt.setExpanded(False)

    def sync_cooling_navigation_to_subtab(self, index: int) -> None:
        if not hasattr(self, "navigation") or self.tabs.currentIndex() != 1:
            return
        target = self.nav_temperature_recording if index == 1 else self.nav_cooling_controls
        self.navigation.blockSignals(True)
        self.navigation.setCurrentItem(target)
        self.nav_nzxt.setExpanded(True)
        self.navigation.blockSignals(False)

    def on_navigation_changed(self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None) -> None:
        if current is None:
            return
        from modules.hardware_checker.v1_0.navigation import select
        select(self, current)
        in_lcd_section = current is self.nav_lcd or current.parent() is self.nav_lcd
        in_cooling_section = current is self.nav_nzxt or current.parent() is self.nav_nzxt
        self.nav_lcd.setExpanded(in_lcd_section)
        self.nav_nzxt.setExpanded(in_cooling_section)
        if hasattr(self, "cooling_subtabs"):
            if current is self.nav_temperature_recording:
                self.cooling_subtabs.setCurrentIndex(1)
            elif current in {self.nav_nzxt, self.nav_cooling_controls}:
                self.cooling_subtabs.setCurrentIndex(0)
        page = current.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(page, int):
            self.tabs.setCurrentIndex(page)

    def sync_navigation_to_page(self, page: int) -> None:
        if page != 2 and hasattr(self, "rgb_selection_list"):
            self.rgb_selection_list.collapseAll()
        if not hasattr(self, "navigation"):
            return
        if page == 8 and hasattr(self, "openlinkhub_check_update_button") and not self.openlinkhub_update_status:
            QTimer.singleShot(0, self.check_openlinkhub_updates)
        from modules.design_hub.v1_1.navigation import sync as sync_design_navigation
        if sync_design_navigation(self, page):
            self.nav_lcd.setExpanded(False)
            self.nav_nzxt.setExpanded(False)
            self.navigation_items["hardware_checker"].setExpanded(False)
            return
        if hasattr(self, "hardware_checker_page"):
            self.navigation_items["hardware_checker"].setExpanded(page == self.hardware_checker_page_index)
            if page == self.hardware_checker_page_index:
                from modules.hardware_checker.v1_0.navigation import sync
                sync(self)
                return
        self.nav_lcd.setExpanded(page in {3, 11})
        self.nav_nzxt.setExpanded(page == 1)
        if page == 1:
            index = self.cooling_subtabs.currentIndex() if hasattr(self, "cooling_subtabs") else 0
            self.sync_cooling_navigation_to_subtab(index)
            return
        if page == 3 and not self.nav_lcd_studio.isHidden():
            self.navigation.blockSignals(True)
            self.navigation.setCurrentItem(self.nav_lcd_studio)
            self.navigation.blockSignals(False)
            return
        root = self.navigation.invisibleRootItem()
        pending = [root.child(i) for i in range(root.childCount())]
        while pending:
            item = pending.pop(0)
            if item.data(0, Qt.ItemDataRole.UserRole) == page and not item.isHidden():
                self.navigation.blockSignals(True)
                self.navigation.setCurrentItem(item)
                self.navigation.blockSignals(False)
                return
            pending.extend(item.child(i) for i in range(item.childCount()))

    def update_temperature_history_options(self, _value: object = None) -> None:
        if not hasattr(self, "temperature_history_chart"):
            return
        visible = {
            key for key, checkbox in self.temperature_history_checks.items()
            if checkbox.isChecked()
        }
        self.temperature_history_chart.set_visible_series(visible)
        self.temperature_history_chart.set_window_seconds(
            self.temperature_history_range_combo.currentData()
        )
        current_range = self.temperature_history_range_combo.currentData()
        self.settings.setValue("temperature_history/range_seconds", int(current_range or 0))
        for key, checkbox in self.temperature_history_checks.items():
            self.settings.setValue(f"temperature_history/show_{key}", checkbox.isChecked())

    def record_temperature_history(self) -> None:
        values: dict[str, float | None] = {
            "cpu": self.current_cpu_temp,
            "gpu": self.current_gpu_temp,
            "liquid": self.current_liquid_temp,
        }
        sensors = self.process_runtime.sensors() if hasattr(self, "process_runtime") else read_linux_temperature_sensors()
        for sensor in sensors:
            values[sensor.key] = sensor.value_c
            self.temperature_sensor_catalog[sensor.key] = (
                sensor.label,
                sensor.group,
                sensor.source,
            )
        for source, card_name in (("cpu", "cpu_temp_card"), ("gpu", "gpu_temp_card"), ("liquid", "temp_card")):
            card = getattr(self, card_name, None)
            gauge = getattr(card, "temperature_gauge", None)
            if gauge is not None:
                gauge.set_value(values.get(source))
            if hasattr(self, "temperature_live_gauges"):
                self.temperature_live_gauges[source].set_value(values.get(source))
                self.temperature_live_labels[source].setText(self.format_temperature(values.get(source)))
        if hasattr(self, "cooling_cpu_gauge"):
            self.cooling_cpu_gauge.set_value(values.get("cpu"))
        recorded = self.temperature_history.append(values)
        if recorded and hasattr(self, "temperature_history_chart"):
            self.temperature_history_chart.update()
        if recorded and hasattr(self, "temperature_detail_chart"):
            signature = tuple(sorted(self.temperature_sensor_catalog))
            if signature != self.temperature_sensor_signature:
                self.temperature_sensor_signature = signature
                self.refresh_temperature_sensor_tree()
            self.refresh_temperature_detail_view()

    def make_temperature_recording_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(10, 12, 10, 10)
        hero = QFrame(objectName="moduleHeroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.addWidget(QLabel("Temperaturaufzeichnung", objectName="heroTitle"))
        intro = QLabel(
            "Alle verfügbaren Temperaturquellen werden ausschließlich lesend über Linux-hwmon erfasst. "
            "Die Kurven bleiben bis zum Programmende im Arbeitsspeicher; es entstehen keine dauerhaften Protokolldateien."
        )
        intro.setWordWrap(True)
        intro.setObjectName("infoText")
        hero_layout.addWidget(intro)
        outer.addWidget(hero)

        live_row = QHBoxLayout()
        self.temperature_live_gauges = {}
        self.temperature_live_labels = {}
        for source, title in (("cpu", "CPU"), ("gpu", "GPU"), ("liquid", "Kühlmittel")):
            card = QFrame(objectName="coolingSummaryCard")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(title, objectName="coolingCardTitle"))
            value_label = QLabel(self.format_temperature(None), objectName="cardValue")
            card_layout.addWidget(value_label)
            gauge = TemperatureGauge(source, card)
            card_layout.addWidget(gauge)
            self.temperature_live_gauges[source] = gauge
            self.temperature_live_labels[source] = value_label
            live_row.addWidget(card, 1)
        outer.addLayout(live_row)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Zeitraum"))
        self.temperature_detail_range_combo = QComboBox()
        for title, seconds in (
            ("Letzte 5 Minuten", 300),
            ("Letzte 15 Minuten", 900),
            ("Letzte 60 Minuten", 3600),
            ("Letzte 6 Stunden", 21_600),
            ("Gesamte Sitzung", None),
        ):
            self.temperature_detail_range_combo.addItem(title, seconds)
        saved_range = int(self.settings.value("temperature_history/detail_range_seconds", 3600))
        selected_range = None if saved_range <= 0 else saved_range
        self.temperature_detail_range_combo.setCurrentIndex(
            max(0, self.temperature_detail_range_combo.findData(selected_range))
        )
        self.temperature_detail_range_combo.currentIndexChanged.connect(self.update_temperature_detail_options)
        controls.addWidget(self.temperature_detail_range_combo)
        controls.addWidget(QLabel("Sensorgruppe"))
        self.temperature_detail_group_combo = QComboBox()
        for title, key in (
            ("Alle Sensoren", "all"), ("CPU", "cpu"), ("GPU", "gpu"),
            ("Kühlung", "cooling"), ("Arbeitsspeicher", "memory"),
            ("SSD / NVMe", "storage"), ("Mainboard / VRM", "mainboard"),
            ("Weitere", "other"),
        ):
            self.temperature_detail_group_combo.addItem(title, key)
        self.temperature_detail_group_combo.currentIndexChanged.connect(self.refresh_temperature_sensor_tree)
        controls.addWidget(self.temperature_detail_group_combo)
        controls.addStretch()
        report_button = QPushButton("Exportieren")
        report_button.clicked.connect(self.open_temperature_report_manager)
        controls.addWidget(report_button)
        outer.addLayout(controls)

        self.temperature_vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.temperature_vertical_splitter.setChildrenCollapsible(False)
        self.temperature_detail_chart = TemperatureHistoryChart(self.temperature_history)
        self.temperature_detail_chart.setMinimumHeight(180)
        self.temperature_detail_chart.set_temperature_unit(self.temperature_unit)
        self.temperature_detail_chart.set_empty_text("Noch keine Temperaturwerte in dieser Sitzung")
        self.temperature_vertical_splitter.addWidget(self.temperature_detail_chart)

        self.temperature_lower_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.temperature_lower_splitter.setChildrenCollapsible(False)
        self.temperature_lower_splitter.setMinimumHeight(260)
        sensor_box = QGroupBox("Sensoren im Diagramm")
        sensor_layout = QVBoxLayout(sensor_box)
        self.temperature_sensor_tree = SensorTree()
        self.temperature_sensor_tree.setObjectName("sensorSelectionTree")
        self.temperature_sensor_tree.setHeaderLabels(["Hardware / Sensor", "Quelle"])
        self.temperature_sensor_tree.setRootIsDecorated(True)
        self.temperature_sensor_tree.setAlternatingRowColors(True)
        self.temperature_sensor_tree.header().setStretchLastSection(True)
        self.temperature_sensor_tree.itemChanged.connect(self.on_temperature_sensor_item_changed)
        sensor_layout.addWidget(self.temperature_sensor_tree)
        add_sensor = QPushButton("Ausgewählte Sensoren hinzufügen")
        add_sensor.clicked.connect(lambda: self.choose_temperature_sensors(
            [item.data(0, Qt.ItemDataRole.UserRole) for item in self.temperature_sensor_tree.selectedItems()], True))
        sensor_layout.addWidget(add_sensor)
        self.temperature_sensor_tree.keysDropped.connect(lambda keys: self.choose_temperature_sensors(keys, False))
        self.temperature_lower_splitter.addWidget(sensor_box)

        statistics_box = QGroupBox("Messwerte im gewählten Zeitraum")
        statistics_layout = QVBoxLayout(statistics_box)
        self.temperature_statistics_table = QTableWidget(0, 6, statistics_box)
        self.temperature_statistics_table.setObjectName("diagnosticTable")
        self.temperature_statistics_table.setHorizontalHeaderLabels(
            ["Sensor", "Aktuell", "Minimum", "Maximum", "Zeitpunkt", "Quelle"]
        )
        self.temperature_statistics_table.verticalHeader().setVisible(False)
        self.temperature_statistics_table.setAlternatingRowColors(True)
        self.temperature_statistics_table.setShowGrid(False)
        self.temperature_statistics_table.verticalHeader().setDefaultSectionSize(38)
        stats_header = self.temperature_statistics_table.horizontalHeader()
        for column in range(5):
            stats_header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        stats_header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.temperature_statistics_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.temperature_statistics_table.hide()  # Compatibility/export model, not a second visible table.
        self.temperature_readings = ReadingList(self.tr_static)
        self.temperature_readings.keysDropped.connect(lambda keys: self.choose_temperature_sensors(keys, True))
        self.temperature_readings.removeRequested.connect(lambda keys: self.choose_temperature_sensors(keys, False))
        statistics_layout.addWidget(self.temperature_readings)
        self.temperature_lower_splitter.addWidget(statistics_box)
        self.temperature_lower_splitter.setStretchFactor(0, 2)
        self.temperature_lower_splitter.setStretchFactor(1, 3)
        self.temperature_vertical_splitter.addWidget(self.temperature_lower_splitter)
        self.temperature_vertical_splitter.setStretchFactor(0, 1)
        self.temperature_vertical_splitter.setStretchFactor(1, 1)
        self.temperature_vertical_splitter.setSizes([260, 320])
        vertical_state = self.settings.value("temperature_history/vertical_splitter")
        horizontal_state = self.settings.value("temperature_history/horizontal_splitter")
        if vertical_state:
            self.temperature_vertical_splitter.restoreState(vertical_state)
        if horizontal_state:
            self.temperature_lower_splitter.restoreState(horizontal_state)
        self.temperature_vertical_splitter.splitterMoved.connect(
            lambda _position, _index: self.settings.setValue(
                "temperature_history/vertical_splitter", self.temperature_vertical_splitter.saveState(),
            )
        )
        self.temperature_lower_splitter.splitterMoved.connect(
            lambda _position, _index: self.settings.setValue(
                "temperature_history/horizontal_splitter", self.temperature_lower_splitter.saveState(),
            )
        )
        outer.addWidget(self.temperature_vertical_splitter, 1)

        raw_selection = str(self.settings.value("temperature_history/detail_selected", ""))
        try:
            decoded_selection = json.loads(raw_selection) if raw_selection else []
        except json.JSONDecodeError:
            decoded_selection = []
        self.temperature_detail_user_configured = bool(raw_selection)
        self.temperature_detail_selected = (
            {str(key) for key in decoded_selection if isinstance(key, str)}
            if self.temperature_detail_user_configured else {"cpu", "gpu", "liquid"}
        )
        self.refresh_temperature_sensor_tree()
        self.update_temperature_detail_options()
        return page

    def open_temperature_report_manager(self) -> None:
        dialog = TemperatureReportDialog(
            self.temperature_history,
            dict(self.temperature_sensor_catalog),
            self.tr_static,
            self,
        )
        if dialog.exec() and dialog.exported_path is not None:
            self.footer_status.setText(
                f"{self.tr_static('Gespeichert')}: {dialog.exported_path}"
            )

    @staticmethod
    def temperature_group_title(group: str) -> str:
        return {
            "cpu": "CPU", "gpu": "GPU", "cooling": "Kühlung",
            "memory": "Arbeitsspeicher", "storage": "SSD / NVMe",
            "mainboard": "Mainboard / VRM", "other": "Weitere",
        }.get(group, "Weitere")

    def refresh_temperature_sensor_tree(self, _value: object = None) -> None:
        if not hasattr(self, "temperature_sensor_tree"):
            return
        group_filter = str(self.temperature_detail_group_combo.currentData() or "all")
        if not self.temperature_detail_user_configured:
            self.temperature_detail_selected.update(self.temperature_sensor_catalog)
        self.temperature_sensor_tree.known_keys = set(self.temperature_sensor_catalog)
        self.temperature_readings.known_keys = set(self.temperature_sensor_catalog)
        self.temperature_sensor_tree.blockSignals(True)
        self.temperature_sensor_tree.clear()
        parents: dict[str, QTreeWidgetItem] = {}
        ordered_sensors = sorted(
            self.temperature_sensor_catalog.items(),
            key=lambda item: (item[1][1], item[1][0].casefold()),
        )
        for key, (label, group, source) in ordered_sensors:
            if group_filter != "all" and group != group_filter:
                continue
            parent = parents.get(group)
            if parent is None:
                parent = QTreeWidgetItem([self.tr_static(self.temperature_group_title(group)), ""])
                parent.setFlags(parent.flags() & ~Qt.ItemFlag.ItemIsUserCheckable & ~Qt.ItemFlag.ItemIsDragEnabled)
                parent.setData(0, Qt.ItemDataRole.UserRole.value + 1, group)
                parent.setIcon(0, sensor_icon(group, self.palette()))
                self.temperature_sensor_tree.addTopLevelItem(parent)
                parents[group] = parent
            item = QTreeWidgetItem([self.tr_static(label), source])
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            item.setData(0, Qt.ItemDataRole.UserRole.value + 1, group)
            item.setIcon(0, sensor_icon(group, self.palette()))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checked = key in self.temperature_detail_selected
            item.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            parent.addChild(item)
        for parent in parents.values():
            parent.setExpanded(True)
        self.temperature_sensor_tree.blockSignals(False)
        self.temperature_sensor_tree.resizeColumnToContents(0)
        self.refresh_temperature_detail_view()

    def choose_temperature_sensors(self, keys, selected):
        valid = {key for key in keys if isinstance(key, str) and key in self.temperature_sensor_catalog}
        if not valid:
            return
        self.temperature_detail_user_configured = True
        if selected:
            self.temperature_detail_selected.update(valid)
        else:
            self.temperature_detail_selected.difference_update(valid)
        self.update_temperature_detail_options()
        self.refresh_temperature_sensor_tree()

    def on_temperature_sensor_item_changed(self, item: QTreeWidgetItem, _column: int) -> None:
        key = str(item.data(0, Qt.ItemDataRole.UserRole) or "")
        if not key:
            return
        self.temperature_detail_user_configured = True
        if item.checkState(0) == Qt.CheckState.Checked:
            self.temperature_detail_selected.add(key)
        else:
            self.temperature_detail_selected.discard(key)
        self.update_temperature_detail_options()

    def update_temperature_detail_options(self, _value: object = None) -> None:
        if not hasattr(self, "temperature_detail_chart"):
            return
        seconds = self.temperature_detail_range_combo.currentData()
        self.temperature_detail_chart.set_window_seconds(seconds)
        self.temperature_detail_chart.set_visible_series(set(self.temperature_detail_selected))
        self.settings.setValue("temperature_history/detail_range_seconds", int(seconds or 0))
        self.settings.setValue(
            "temperature_history/detail_selected",
            json.dumps(sorted(self.temperature_detail_selected)),
        )
        self.refresh_temperature_detail_view()

    def refresh_temperature_detail_view(self) -> None:
        if not hasattr(self, "temperature_detail_chart"):
            return
        metadata = {
            key: (self.tr_static(label), group)
            for key, (label, group, _source) in self.temperature_sensor_catalog.items()
        }
        self.temperature_detail_chart.set_series_metadata(metadata)
        self.temperature_detail_chart.set_visible_series(set(self.temperature_detail_selected))
        seconds = self.temperature_detail_range_combo.currentData()
        selected = [
            key for key in self.temperature_detail_selected
            if key in self.temperature_sensor_catalog
        ]
        self.temperature_statistics_table.setRowCount(len(selected))
        symbol = temperature_symbol(self.temperature_unit)
        ordered = sorted(
            selected,
            key=lambda key: self.temperature_sensor_catalog[key][0].casefold(),
        )
        readings = {}
        for row, key in enumerate(ordered):
            label, _group, source = self.temperature_sensor_catalog[key]
            statistics = self.temperature_history.statistics(key, seconds)
            latest = self.temperature_history.latest(key, seconds)
            values = ("—", "—", "—") if statistics is None else tuple(
                f"{celsius_to_display(value, self.temperature_unit):.1f} {symbol}"
                for value in statistics
            )
            measured = (
                datetime.fromtimestamp(latest.timestamp).strftime("%d.%m.%Y %H:%M:%S")
                if latest is not None else "—"
            )
            readings[key] = (self.tr_static(label), _group, source, *values, measured)
            for column, value in enumerate((self.tr_static(label), *values, measured, source)):
                self.temperature_statistics_table.setItem(row, column, QTableWidgetItem(str(value)))
        self.temperature_readings.update_readings(readings)
        self.temperature_statistics_table.resizeColumnsToContents()
        self.temperature_statistics_table.resizeRowsToContents()
