"""Default-all RGB selection, explicit subsets and locked-device guards."""
import os
import sys
from pathlib import Path
from types import SimpleNamespace
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from modules.rgb_studio.v1_15.selection import (
    build_selection_mode, choose_device, configure_selection_row, refresh_selection,
    set_individual, selection_item_changed,
)
from test_case_workspace_342983 import Settings

APP = QApplication.instance() or QApplication([])


def host_fixture():
    devices = [{"id": "msi", "writable": True}, {"id": "ram", "writable": True},
               {"id": "locked", "writable": False}]
    calls = []
    host = SimpleNamespace(settings=Settings(), rgb_individual_selection=False,
                           rgb_selected_devices={"msi"}, rgb_logical_devices=lambda: devices,
                           save_rgb_workspace=lambda: calls.append("save"),
                           rebuild_rgb_workspace=lambda: calls.append("rebuild"))
    return host, devices, calls


def test_default_all_handles_new_inventory_and_rejects_locked_selection():
    host, devices, _ = host_fixture()
    choose_device(host, "msi", True)
    assert host.rgb_selected_devices == {"msi", "ram"}
    choose_device(host, "locked", True)
    assert host.rgb_selected_devices == {"msi", "ram"}
    devices.append({"id": "new", "writable": True})
    refresh_selection(host)
    assert host.rgb_selected_devices == {"msi", "ram", "new"}
    devices[0]["writable"] = False
    refresh_selection(host)
    assert host.rgb_selected_devices == {"ram", "new"}


def test_individual_subsets_and_empty_selection_do_not_auto_refill():
    host, _, _ = host_fixture()
    checkbox = build_selection_mode(host)
    assert not checkbox.isChecked()
    choose_device(host, "msi", False)
    assert checkbox.isChecked() and host.rgb_individual_selection
    refresh_selection(host)
    assert host.rgb_selected_devices == set()
    choose_device(host, "ram", True)
    refresh_selection(host)
    assert host.rgb_selected_devices == {"ram"}
    checkbox.setChecked(False)
    assert host.rgb_selected_devices == {"msi", "ram"}
    assert not host.settings.data["rgb_studio/individual_selection"]


def test_one_ram_bank_selection_expands_to_all_physical_dimms():
    host, devices, _ = host_fixture()
    devices[:] = [
        {"id": "ram-a", "writable": True},
        {"id": "ram-b", "writable": True},
        {"id": "locked", "writable": False},
    ]
    host.rgb_expand_ui_device_id = lambda value: (
        ("ram-a", "ram-b") if value == "openrgb-bank:ram" else (value,)
    )
    set_individual(host, True)
    assert choose_device(host, "openrgb-bank:ram", True)
    assert host.rgb_selected_devices == {"msi", "ram-a", "ram-b"}
    row = QTreeWidgetItem(["Arbeitsspeicher"])
    row.setData(0, Qt.ItemDataRole.UserRole, "openrgb-bank:ram")
    row.setCheckState(0, Qt.CheckState.Unchecked)
    calls = []
    host.set_rgb_device_selected = lambda *args: calls.append(args)
    selection_item_changed(host, row, 0)
    assert calls == [("openrgb-bank:ram", False)]


def test_checkable_list_keeps_device_identity_and_excludes_locked_rows():
    host, devices, _ = host_fixture()
    set_individual(host, True)
    tree = QTreeWidget()
    tree.setColumnCount(3)
    rows = []
    for device in devices:
        row = QTreeWidgetItem([device["id"]])
        configure_selection_row(host, row, device)
        tree.addTopLevelItem(row)
        rows.append(row)
    calls = []
    host.set_rgb_device_selected = lambda *args: calls.append(args)
    assert rows[0].checkState(0) == Qt.CheckState.Checked
    rows[1].setCheckState(0, Qt.CheckState.Checked)
    selection_item_changed(host, rows[1], 0)
    selection_item_changed(host, rows[2], 0)
    assert calls == [("ram", True)]
    assert rows[2].data(0, Qt.ItemDataRole.UserRole) == "locked"
    tree.close()
