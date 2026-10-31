# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded read-only GPU metrics and hardware tables."""
from __future__ import annotations

from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

from .client import LactError


class GpuTableMixin:
    @staticmethod
    def _table() -> QTableWidget:
        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels(["Merkmal", "Wert"])
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setWordWrap(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        return table

    @staticmethod
    def _flatten(value: object, prefix: str = "", depth: int = 0) -> list[tuple[str, str]]:
        if depth > 3:
            return []
        if isinstance(value, dict):
            rows = []
            for key, item in list(value.items())[:80]:
                rows.extend(GpuTableMixin._flatten(item, f"{prefix} · {key}" if prefix else str(key), depth + 1))
            return rows
        if isinstance(value, list):
            return [(prefix, f"{len(value)} Einträge")]
        if value is None:
            return []
        return [(prefix, str(value)[:220])]

    def _fill_table(self, table: QTableWidget, value: object) -> None:
        rows = self._flatten(value)[:90]
        table.setRowCount(len(rows))
        for index, (key, data) in enumerate(rows):
            table.setItem(index, 0, QTableWidgetItem(key))
            table.setItem(index, 1, QTableWidgetItem(data))
        table.resizeRowsToContents()

    def refresh_metrics(self) -> None:
        if not self.gpu_id:
            return
        if self._request_gpu_read("metrics", self.gpu_id):
            return
        try:
            self.stats = self.client.stats(self.gpu_id)
            self._fill_table(self.metrics, self.stats)
            self._refresh_gpu_dashboard()
        except LactError as exc:
            self.status.setText(self.tr("GPU-Messwerte fehlen: {reason}").format(reason=exc))
