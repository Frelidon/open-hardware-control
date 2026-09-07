#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""In-page expand helpers for RGB Studio devices/effects and native channels."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


def build_native_hardware_channel_panel(owner: object) -> QWidget:
    """Full-width native-channel list that expands inside the RGB page."""

    owner.rgb_native_results_count = 0
    owner.rgb_native_results_ok = True
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 4, 0, 0)
    layout.setSpacing(8)
    button = QPushButton("Native Hardwarekanäle anzeigen ⌄")
    button.setCheckable(True)
    button.setMinimumHeight(40)
    button.setToolTip(
        "Blendet die native Hardwarekanal-Liste in dieser Seite ein. Es wird kein Extra-Fenster geöffnet."
    )
    tree = QTreeWidget()
    tree.setHeaderLabels(["Gerät / Kanal", "Hardwaremodus", "Status"])
    tree.setRootIsDecorated(True)
    tree.setAlternatingRowColors(True)
    tree.setUniformRowHeights(True)
    tree.setItemsExpandable(True)
    tree.setAnimated(True)
    tree.setMinimumHeight(320)
    tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    tree.setColumnWidth(0, 320)
    tree.setColumnWidth(1, 220)
    tree.setVisible(False)
    button.toggled.connect(owner.set_rgb_native_results_expanded)
    layout.addWidget(button)
    layout.addWidget(tree, 1)
    owner.rgb_native_results_button = button
    owner.rgb_native_results_list = tree
    return panel


class RgbStudioExpandMixin:
    """Keep Geräte/Effekte and native channels as in-page panels, never extra windows."""

    def set_rgb_devices_effects_expanded(self, expanded: bool) -> None:
        if not hasattr(self, "rgb_devices_effects_panel"):
            return
        expanded = bool(expanded)
        toggle = getattr(self, "rgb_devices_effects_toggle", None)
        if toggle is not None and toggle.isChecked() != expanded:
            toggle.blockSignals(True)
            toggle.setChecked(expanded)
            toggle.blockSignals(False)
        self.rgb_devices_effects_panel.setVisible(expanded)
        if toggle is not None:
            toggle.setText(
                "Geräte und Effekte ausblenden ⌄" if expanded else "Geräte und Effekte anzeigen ⌄"
            )
        if hasattr(self, "settings"):
            self.settings.setValue("rgb_studio/devices_effects_expanded", expanded)

    def refresh_rgb_native_results_caption(self) -> None:
        if not hasattr(self, "rgb_native_results_button"):
            return
        count = int(getattr(self, "rgb_native_results_count", 0) or 0)
        expanded = bool(self.rgb_native_results_button.isChecked())
        verb = "ausblenden" if expanded else "anzeigen"
        if count:
            summary = "erfolgreich" if getattr(self, "rgb_native_results_ok", True) else "mit Fehlern"
            caption = f"Native Hardwarekanäle {verb} · {count} · {summary} ⌄"
        else:
            caption = f"Native Hardwarekanäle {verb} ⌄"
        self.rgb_native_results_button.setText(caption)

    def set_rgb_native_results_expanded(self, expanded: bool) -> None:
        if not hasattr(self, "rgb_native_results_list"):
            return
        expanded = bool(expanded)
        button = self.rgb_native_results_button
        if button.isChecked() != expanded:
            button.blockSignals(True)
            button.setChecked(expanded)
            button.blockSignals(False)
        self.rgb_native_results_list.setVisible(expanded)
        if expanded:
            self.set_rgb_devices_effects_expanded(True)
        self.refresh_rgb_native_results_caption()
        if hasattr(self, "settings"):
            self.settings.setValue("rgb_studio/native_results_expanded", expanded)

    def update_rgb_native_results(
        self, entries: list[tuple[str, str]], successful: bool
    ) -> None:
        if not hasattr(self, "rgb_native_results_list"):
            return
        self.rgb_native_results_list.clear()
        status = "Erfolgreich" if successful else "Fehler · Details im Fehlerbereich"
        grouped: dict[str, list[QTreeWidgetItem]] = {}
        for device_name, mode_name in entries:
            vendor = self.rgb_vendor_bucket(device_name, "openrgb")
            grouped.setdefault(vendor, []).append(QTreeWidgetItem([device_name, mode_name, status]))
        for vendor in sorted(grouped, key=self.rgb_vendor_bucket_sort_key):
            children = grouped[vendor]
            parent = QTreeWidgetItem([f"{vendor} · {len(children)}", "", ""])
            parent.setFirstColumnSpanned(True)
            parent.setExpanded(True)
            for child in children:
                parent.addChild(child)
            self.rgb_native_results_list.addTopLevelItem(parent)
        self.rgb_native_results_count = len(entries)
        self.rgb_native_results_ok = bool(successful)
        if entries:
            self.set_rgb_native_results_expanded(True)
        else:
            self.refresh_rgb_native_results_caption()
