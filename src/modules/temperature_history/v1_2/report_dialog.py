#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qt manager for bounded, user-triggered temperature report exports."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
import math
from pathlib import Path

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from .model import TemperatureHistoryBuffer
from .report import temperature_report_rows, write_temperature_report


class TemperatureReportDialog(QDialog):
    def __init__(
        self,
        history: TemperatureHistoryBuffer,
        catalog: dict[str, tuple[str, str, str]],
        translator: Callable[[str], str] | None = None,
        parent=None,
    ) -> None:  # type: ignore[no-untyped-def]
        super().__init__(parent)
        self.history = history
        self.catalog = catalog
        self.tr_text = translator or (lambda text: text)
        self.exported_path: Path | None = None
        self.setWindowTitle(self.tr_text("Bericht"))
        self.setMinimumSize(760, 560)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        samples = history.samples
        first = math.floor(samples[0].timestamp) if samples else datetime.now().timestamp() - 3600
        last = math.ceil(samples[-1].timestamp) if samples else datetime.now().timestamp()
        self.start_edit = self._date_edit(first, first, last)
        self.end_edit = self._date_edit(last, first, last)
        self.format_combo = QComboBox()
        self.format_combo.addItem("CSV", "csv")
        self.format_combo.addItem("JSON", "json")
        form.addRow(self.tr_text("Start"), self.start_edit)
        form.addRow(self.tr_text("Ende"), self.end_edit)
        form.addRow(self.tr_text("Format"), self.format_combo)
        layout.addLayout(form)
        layout.addWidget(QLabel(self.tr_text("Sensoren im Diagramm")))
        self.sensor_tree = QTreeWidget()
        self.sensor_tree.setHeaderLabels([
            self.tr_text("Hardware / Sensor"), self.tr_text("Quelle"),
        ])
        self.sensor_tree.setAlternatingRowColors(True)
        self.sensor_tree.header().setStretchLastSection(True)
        for key, (label, group, source) in sorted(
            catalog.items(), key=lambda item: (item[1][1], item[1][0].casefold()),
        ):
            item = QTreeWidgetItem([self.tr_text(label), source])
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked)
            item.setToolTip(0, group)
            self.sensor_tree.addTopLevelItem(item)
        self.sensor_tree.resizeColumnToContents(0)
        layout.addWidget(self.sensor_tree, 1)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("muted")
        layout.addWidget(self.status_label)
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton(self.tr_text("Abbrechen"))
        cancel.clicked.connect(self.reject)
        export = QPushButton(self.tr_text("Exportieren"))
        export.setObjectName("primaryAction")
        export.clicked.connect(self.export_report)
        actions.addWidget(cancel)
        actions.addWidget(export)
        layout.addLayout(actions)

    @staticmethod
    def _date_edit(value: float, first: float, last: float) -> QDateTimeEdit:
        edit = QDateTimeEdit(QDateTime.fromSecsSinceEpoch(round(value)))
        edit.setCalendarPopup(True)
        edit.setDisplayFormat("dd.MM.yyyy HH:mm:ss")
        edit.setMinimumDateTime(QDateTime.fromSecsSinceEpoch(round(first)))
        edit.setMaximumDateTime(QDateTime.fromSecsSinceEpoch(round(last)))
        return edit

    def selected_keys(self) -> set[str]:
        return {
            str(self.sensor_tree.topLevelItem(index).data(0, Qt.ItemDataRole.UserRole))
            for index in range(self.sensor_tree.topLevelItemCount())
            if self.sensor_tree.topLevelItem(index).checkState(0) == Qt.CheckState.Checked
        }

    def export_report(self) -> None:
        keys = self.selected_keys()
        if not keys:
            self.status_label.setText(self.tr_text("Keine Auswahl"))
            return
        start = self.start_edit.dateTime().toSecsSinceEpoch()
        end = self.end_edit.dateTime().toSecsSinceEpoch()
        rows = temperature_report_rows(self.history, start, end, keys, self.catalog)
        if not rows:
            self.status_label.setText(self.tr_text("Keine Daten"))
            return
        mode = str(self.format_combo.currentData() or "csv")
        default = Path.home() / f"OHC-Temperaturen-{datetime.now():%Y-%m-%d}.{mode}"
        selected, _filter = QFileDialog.getSaveFileName(
            self, self.tr_text("Bericht"), str(default),
            "CSV (*.csv)" if mode == "csv" else "JSON (*.json)",
        )
        if not selected:
            return
        try:
            self.exported_path = write_temperature_report(Path(selected), rows, mode)
        except OSError as exc:
            self.status_label.setText(f"{self.tr_text('Exportfehler')}: {exc}")
            return
        self.accept()
