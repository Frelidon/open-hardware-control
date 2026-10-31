# SPDX-License-Identifier: GPL-3.0-or-later
"""Dashboard visibility and flat ordering stay local, persisted and resettable."""

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
from dashboard_layout import DashboardLayoutMixin

APP = QApplication.instance() or QApplication([])


class Settings:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value

    def remove(self, key):
        self.values.pop(key, None)

    def sync(self):
        pass


class DashboardHost(DashboardLayoutMixin, QWidget):
    def __init__(self, values=None):
        super().__init__()
        self.settings = Settings(values)
        self.display_layout = "16:9"
        self.devices_ready = False
        self.current_liquid_temp = None
        self.dashboard_card_entries = [
            ("cpu_temperature", "CPU", QFrame(self)),
            ("gpu_temperature", "GPU", QFrame(self)),
            ("cpu_model", "Processor", QFrame(self)),
        ]
        root = QVBoxLayout(self)
        status = QHBoxLayout()
        root.addLayout(status)
        self.dashboard_cards_layout = QGridLayout()
        root.addLayout(self.dashboard_cards_layout)
        self.install_dashboard_card_customization(root, status)
        self.apply_dashboard_card_visibility(save=False)


def test_dashboard_cards_restore_visibility_and_flat_order_without_hardware():
    host = DashboardHost({
        "dashboard/card_order": ["cpu_model", "gpu_temperature", "cpu_temperature"],
        "dashboard/visible_cards": ["gpu_temperature", "cpu_temperature"],
    })
    assert host.dashboard_card_order() == ["cpu_model", "gpu_temperature", "cpu_temperature"]
    assert host.dashboard_card_entries[2][2].isHidden()
    tree = host.dashboard_card_editor
    assert all(not (tree.topLevelItem(index).flags() & Qt.ItemFlag.ItemIsDropEnabled)
               for index in range(tree.topLevelItemCount()))
    cpu_model = tree.topLevelItem(0)
    cpu_model.setCheckState(0, Qt.CheckState.Checked)
    assert "cpu_model" in host.settings.values["dashboard/visible_cards"]
    tree.insertTopLevelItem(0, tree.takeTopLevelItem(2))
    host.dashboard_card_order_changed()
    assert host.settings.values["dashboard/card_order"] == ["cpu_temperature", "cpu_model", "gpu_temperature"]
    assert host.dashboard_cards_layout.itemAt(1).widget() is host.dashboard_card_entries[2][2]
    host.reset_dashboard_card_editor()
    assert "dashboard/card_order" not in host.settings.values
    assert host.dashboard_card_order() == ["cpu_temperature", "gpu_temperature", "cpu_model"]
    assert all(checkbox.isChecked() for checkbox in host.dashboard_card_checkboxes.values())
    host.deleteLater()


def test_dashboard_rejects_duplicate_saved_order_instead_of_duplicating_cards():
    host = DashboardHost({"dashboard/card_order": ["cpu_model", "gpu_temperature", "cpu_temperature", "cpu_model"]})
    assert host.dashboard_card_order() == ["cpu_temperature", "gpu_temperature", "cpu_model"]
    assert host.dashboard_cards_layout.count() == 3
    host.deleteLater()
