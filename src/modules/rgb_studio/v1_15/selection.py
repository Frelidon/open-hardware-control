# SPDX-License-Identifier: GPL-3.0-or-later
"""Selection only: all writable devices by default, explicit individual mode."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox

MODE_KEY = "rgb_studio/individual_selection"


def writable_ids(host):
    return {str(d["id"]) for d in host.rgb_logical_devices() if d.get("writable", False)}


def set_individual(host, enabled):
    host.rgb_individual_selection = bool(enabled)
    checkbox = getattr(host, "rgb_individual_checkbox", None)
    if checkbox is not None:
        previous = checkbox.blockSignals(True)
        checkbox.setChecked(bool(enabled))
        checkbox.blockSignals(previous)
    host.settings.setValue(MODE_KEY, bool(enabled))


def refresh_selection(host):
    if not getattr(host, "rgb_individual_selection", False):
        host.rgb_selected_devices = writable_ids(host)


def build_selection_mode(host):
    checkbox = QCheckBox("Einzelne Geräte auswählen")
    host.rgb_individual_checkbox = checkbox
    checkbox.setChecked(host.rgb_individual_selection)
    def changed(enabled):
        set_individual(host, enabled)
        refresh_selection(host)
        host.save_rgb_workspace()
        host.rebuild_rgb_workspace()
    checkbox.toggled.connect(changed)
    return checkbox


def choose_device(host, device_id, selected):
    writable = writable_ids(host)
    members = set(getattr(host, "rgb_expand_ui_device_id", lambda value: (value,))(device_id))
    if not members or not members.issubset(writable):
        return False
    # A deliberate deselection opts into individual control. Selecting a tile
    # in default mode selects the entire writable inventory, never locked rows.
    if not selected:
        set_individual(host, True)
        host.rgb_selected_devices.difference_update(members)
    elif getattr(host, "rgb_individual_selection", False):
        host.rgb_selected_devices.update(members)
    else:
        host.rgb_selected_devices = writable
    return True


def selection_item_changed(host, item, column):
    if column != 0 or not host.rgb_individual_selection:
        return
    device_id = str(item.data(0, Qt.ItemDataRole.UserRole) or "")
    members = set(getattr(host, "rgb_expand_ui_device_id", lambda value: (value,))(device_id))
    if members and members.issubset(writable_ids(host)):
        host.set_rgb_device_selected(device_id, item.checkState(0) == Qt.CheckState.Checked)


def configure_selection_row(host, row, device):
    device_id = str(device["id"])
    row.setData(0, Qt.ItemDataRole.UserRole, device_id)
    if getattr(host, "rgb_individual_selection", False) and device.get("writable", False):
        row.setFlags(row.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        selected = getattr(host, "rgb_ui_item_selected", lambda item: device_id in host.rgb_selected_devices)(device)
        row.setCheckState(0, Qt.CheckState.Checked if selected else Qt.CheckState.Unchecked)
