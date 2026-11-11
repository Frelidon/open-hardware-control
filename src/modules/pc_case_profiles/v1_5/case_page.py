#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Central case page and shared read-only topology in RGB/cooling views."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QGroupBox, QHeaderView, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QDialog, QDialogButtonBox, QTabWidget,
)
from modules.rgb_studio.v1_15.argb_controls import build_slot_led_button, slot_header_targets, edit_slot_header
from .catalog import case_template
from .diagram import PCLayoutDiagram
from .view_state import cooling_slots, layout_synchronized, move_cooling_slot, resize_cooling_slot, set_synchronized
from .channel_labels import channel_caption, channel_details
from .topology_labels import slot_topology_label, display_header_targets, slot_led_path
from .case_animation import build_specs as build_case_led_animations
from .spatial_layout import CaseSpatialPanel, UNIT_KEY, normalize_unit, read_links

FAN_POSITIONS = {"top", "front", "side", "bottom", "rear"}


def slot_supports_pwm(slot) -> bool:
    if slot.position == "pump":
        return True
    return slot.position in FAN_POSITIONS and slot.size_mm > 0 and slot.count > 0


def slot_build_caption(slot) -> str:
    if slot.position == "pump" and any(word in slot.connection.casefold() for word in ("display", "lcd")):
        return "Display / Pumpenkopf"
    if slot_supports_pwm(slot):
        return f"{slot.count} × {slot.size_mm} mm"
    return f"{slot.count} × Komponente" if slot.count > 1 else "Komponente"


def slot_declares_lighting(slot, targets) -> bool:
    if targets:
        return True
    detail = f"{slot.name} {slot.connection}".casefold()
    return any(word in detail for word in ("argb", "rgb-hub", "rgb hub", " leds", "beleuchtung"))


def analyze_case_topology(host) -> str:
    slots = list(getattr(host, "rgb_layout_slots", ()))[:64]
    assignments = getattr(host, "mainboard_layout_assignments", {})
    fan_slots = [slot for slot in slots if slot_supports_pwm(slot)]
    pwm_mapped = sum(bool(next((key for key, value in assignments.items()
                                if value == (slot.slot_id or slot.position)), "")) for slot in fan_slots)
    lit_slots = [slot for slot in slots if slot_declares_lighting(slot, display_header_targets(host, slot))]
    routed = sum(bool(display_header_targets(host, slot)) for slot in lit_slots)
    paths = sum(slot_led_path(host, slot) is not None for slot in lit_slots)
    translate = getattr(host, "tr_static", lambda source: source)
    return translate(
        "{devices} Geräte · {pwm_mapped}/{fans} PWM zugeordnet · "
        "{routed}/{lit} ARGB verbunden · {paths} LED-Pfade eingerichtet"
    ).format(devices=len(slots), pwm_mapped=pwm_mapped, fans=len(fan_slots),
             routed=routed, lit=len(lit_slots), paths=paths)


def build_case_preview(host):
    box = QGroupBox("PC-Ansicht · Gehäuse, Profile und Komponentenpositionen")
    layout = QVBoxLayout(box)
    host.rgb_case_preview_diagram = PCLayoutDiagram()
    diagram = host.rgb_case_preview_diagram
    diagram.slot_moved.connect(host.move_rgb_layout_slot)
    diagram.slot_resized.connect(host.resize_rgb_layout_slot)
    diagram.device_dropped.connect(host.assign_rgb_device_to_layout_slot)
    diagram.slot_focused.connect(host.focus_rgb_layout_slot)
    diagram.slot_selected.connect(host.open_rgb_layout_slot_device_editor)
    diagram.fan_order_changed.connect(host.reorder_rgb_layout_slot_devices)
    diagram.setMinimumSize(620, 440)
    layout.addWidget(diagram)
    row = QHBoxLayout()
    open_case = QPushButton("Gehäuse")
    open_case.clicked.connect(lambda _checked=False: host.tabs.setCurrentIndex(host.case_page_index))
    row.addWidget(open_case)
    row.addWidget(build_slot_led_button(host))
    layout.addLayout(row)
    return box


class CasePage(QScrollArea):
    def __init__(self, host):
        super().__init__()
        self.host = host
        self.setWidgetResizable(True)

    def showEvent(self, event):
        refresh_case_views(self.host)
        super().showEvent(event)

    def hideEvent(self, event):
        inspector = getattr(self.host, "case_inspector", None)
        if inspector is not None: inspector.dismiss()
        super().hideEvent(event)


def build_case_page(host):
    page = CasePage(host)
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(18, 18, 18, 18)
    host.case_sync_checkbox = QCheckBox("RGB und Kühlung synchronisieren")
    host.case_sync_checkbox.setChecked(layout_synchronized(host))
    def synchronize(enabled):
        set_synchronized(host, enabled)
        host.refresh_rgb_layout_editor()
    host.case_sync_checkbox.toggled.connect(synchronize)
    # Shared toolbar keeps the diagram close to the page header.
    note = QLabel("Getrennt: Position und Ansichtsgröße; PWM/LED bleiben gemeinsam. Keine Regelungsaktivierung.")
    note.setWordWrap(True)
    host.case_sync_checkbox.setToolTip(note.text())
    note.hide()
    analysis_row = QHBoxLayout()
    analyze = QPushButton(host.tr_static("Gehäuse analysieren"))
    host.case_analysis_label = QLabel()
    host.case_analysis_label.setWordWrap(True)
    host.case_analysis_label.setObjectName("muted")
    analyze.clicked.connect(lambda _checked=False: host.case_analysis_label.setText(analyze_case_topology(host)))
    analysis_row.addWidget(host.case_sync_checkbox)
    analysis_row.addWidget(analyze)
    analysis_row.addWidget(host.case_analysis_label, 1)
    layout.addLayout(analysis_row)
    controls = QGroupBox(host.tr_static("Lüfteranschluss zuordnen"))
    controls_layout = QHBoxLayout(controls)
    host.case_pwm_combo = QComboBox()
    host.case_pwm_combo.setProperty("i18nTranslateItems", False)
    controls_layout.addWidget(host.case_pwm_combo, 1)
    assign = QPushButton(host.tr_static("Zuordnen"))
    assign.clicked.connect(lambda _checked=False: assign_pwm(host))
    controls_layout.addWidget(assign)
    host.case_sections = QTabWidget()
    host.case_sections.setObjectName("caseSections")
    overview = QWidget(); overview_layout = QVBoxLayout(overview)
    components = QWidget(); components_layout = QVBoxLayout(components)
    overview_layout.addWidget(host.case_workspace)
    components_layout.addWidget(controls)
    host.case_spatial_panel = CaseSpatialPanel(host)
    host.case_sections.addTab(overview, host.tr_static("Übersicht"))
    host.case_sections.addTab(components, host.tr_static("Komponenten"))
    host.case_sections.addTab(host.case_spatial_panel, host.tr_static("Abstände und Tiefe"))
    layout.addWidget(host.case_sections)
    topology_box = QGroupBox(host.tr_static("Geräte im Gehäuse"))
    topology_layout = QVBoxLayout(topology_box)
    host.case_topology_table = QTableWidget(0, 4)
    host.case_topology_table.setObjectName("diagnosticTable")
    host.case_topology_table.setHorizontalHeaderLabels([
        host.tr_static("Gerät"), host.tr_static("Aufbau"),
        host.tr_static("Beleuchtung"), host.tr_static("Kühlung"),
    ])
    host.case_topology_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    host.case_topology_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    host.case_topology_table.setMinimumHeight(220)
    host.case_topology_table.setAlternatingRowColors(True)
    host.case_topology_table.setShowGrid(False)
    host.case_topology_table.setWordWrap(True)
    host.case_topology_table.verticalHeader().hide()
    host.case_topology_table.verticalHeader().setDefaultSectionSize(42)
    case_header = host.case_topology_table.horizontalHeader()
    case_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    case_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
    case_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
    case_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
    host.case_topology_table.cellClicked.connect(lambda row, _column: host.focus_rgb_layout_slot(
        str(host.case_topology_table.item(row, 0).data(Qt.ItemDataRole.UserRole))))
    host.case_topology_table.cellDoubleClicked.connect(
        lambda row, column: activate_case_table_cell(host, row, column)
    )
    topology_layout.addWidget(host.case_topology_table)
    components_layout.addWidget(topology_box)
    components_layout.addStretch()
    host.case_cooling_box = QGroupBox("Getrennte Positionen für RGB und Kühlung")
    separate = QVBoxLayout(host.case_cooling_box)
    host.case_cooling_diagram = PCLayoutDiagram()
    host.case_cooling_diagram.slot_moved.connect(lambda slot_id, x, y, pos: move_cooling_slot(host, slot_id, x, y, pos))
    host.case_cooling_diagram.slot_resized.connect(lambda slot_id, scale: resize_cooling_slot(host, slot_id, scale))
    host.case_cooling_diagram.slot_focused.connect(host.focus_rgb_layout_slot)
    host.case_cooling_diagram.slot_selected.connect(lambda _slot_id: host.edit_selected_rgb_layout_slot())
    separate.addWidget(host.case_cooling_diagram)
    overview_layout.addWidget(host.case_cooling_box)
    from modules.rgb_studio.v1_15.generic_fans import FanCatalog
    host.case_fan_catalog = FanCatalog(host)
    overview_layout.addWidget(host.case_fan_catalog)
    page.setWidget(content)
    refresh_case_views(host)
    return page


def open_spatial_editor(host) -> None:
    """Open and reveal the settings-only spatial editor on the Case page."""
    if not hasattr(host, "case_page_index"):
        return
    host.tabs.setCurrentIndex(host.case_page_index)
    if hasattr(host, "case_sections"):
        host.case_sections.setCurrentIndex(2)
    panel = getattr(host, "case_spatial_panel", None)
    if panel is not None:
        panel.refresh()
        page = host.tabs.widget(host.case_page_index)
        if isinstance(page, QScrollArea):
            page.ensureWidgetVisible(panel, 24, 24)


def activate_case_table_cell(host, row: int, column: int) -> None:
    item = host.case_topology_table.item(row, 0)
    slot_id = str(item.data(Qt.ItemDataRole.UserRole)) if item is not None else ""
    slot = next((entry for entry in host.rgb_layout_slots
                 if (entry.slot_id or entry.position) == slot_id), None)
    if slot is None:
        return
    targets = display_header_targets(host, slot)
    if column == 2 and slot_declares_lighting(slot, targets):
        edit_slot_header(host, slot_id)
    elif column == 3 and slot_supports_pwm(slot):
        build_slot_pwm_button(host, slot_id).click()
    else:
        host.edit_selected_rgb_layout_slot()


def build_slot_pwm_button(host, slot_id):
    button = QPushButton(host.tr_static("Lüfteranschluss zuordnen"))
    def choose():
        channels = host.case_mappable_mainboard_channels()
        choices = ["—", *(channel_caption(host, c) for c in channels)]
        current = next((key for key, value in host.mainboard_layout_assignments.items() if value == slot_id), "")
        ids = ["", *(c.stable_id for c in channels)]
        dialog = QDialog(host)
        dialog.setWindowTitle(host.tr_static("Lüfteranschluss zuordnen"))
        layout = QVBoxLayout(dialog)
        combo = QComboBox()
        combo.setObjectName("caseInlinePwm")
        combo.setProperty("i18nTranslateItems", False)
        for label, key in zip(choices, ids): combo.addItem(label, key)
        combo.setCurrentIndex(ids.index(current) if current in ids else 0)
        layout.addWidget(combo)
        buttons = QDialogButtonBox()
        buttons.addButton(host.tr_static("Speichern"), QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(host.tr_static("Abbrechen"), QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject)
        dialog.accepted.connect(lambda: assign_pwm(host, channel_id=combo.currentData(), slot_id=slot_id))
        layout.addWidget(buttons)
        from .inline_editor import present_editor
        if not present_editor(host, dialog): dialog.exec()
    button.clicked.connect(choose)
    return button


def assign_pwm(host, *, channel_id=None, slot_id=None):
    # Settings-only mapping. Never calibrate, enable or write PWM.
    channel_id = host.case_pwm_combo.currentData() if channel_id is None else channel_id
    slot_id = host.rgb_layout_selected_slot_id if slot_id is None else slot_id
    if host.mainboard_calibration_channel_id:
        host.show_error(host.tr_static("Eine Lüfterprüfung läuft noch. Warte bitte bis zur sicheren Wiederherstellung."))
        return
    slot = host._fan_layout_slot(slot_id)
    if slot is None:
        host.show_error(host.tr_static("Bitte zuerst einen Mainboard-Anschluss und anschließend einen Lüfter- oder Pumpenplatz in der Grafik auswählen."))
        return
    if channel_id == "":
        for key, value in list(host.mainboard_layout_assignments.items()):
            if value == slot_id:
                host.mainboard_layout_assignments.pop(key)
                if key == host.thermalright_pump_channel_id:
                    host.thermalright_pump_channel_id = ""
                    host.settings.setValue("thermalright_cooling/pump_channel", "")
                if key == host.thermalright_radiator_channel_id:
                    host.thermalright_radiator_channel_id = ""
                    host.settings.setValue("thermalright_cooling/radiator_channel", "")
        host.save_mainboard_fan_settings()
        host.sync_selected_rgb_case_profile_pwm_assignments()
        host.refresh_mainboard_fan_table()
    else:
        channel_reader = getattr(host, "case_mappable_mainboard_channels", None)
        channels = (
            channel_reader()
            if callable(channel_reader)
            else host.chassis_mainboard_channels()
        )
    if channel_id and channel_id in {channel.stable_id for channel in channels}:
        host.mainboard_selected_channel_id = channel_id
        host.cooling_layout_selected_slot_id = slot_id
        host.assign_selected_channel_to_cooling_slot()
    host.refresh_rgb_layout_editor()


def refresh_case_views(host):
    if not hasattr(host, "rgb_layout_slots"):
        return
    assignments = getattr(host, "mainboard_layout_assignments", {})
    labels = {slot.slot_id or slot.position: slot_topology_label(host, slot) for slot in host.rgb_layout_slots[:64]}
    led_paths = {slot.slot_id or slot.position: path for slot in host.rgb_layout_slots[:64]
                 if (path := slot_led_path(host, slot)) is not None}
    led_animations = build_case_led_animations(host, host.rgb_layout_slots, led_paths)
    valid_slot_ids = {str(slot.slot_id or slot.position) for slot in host.rgb_layout_slots[:64]}
    distance_links = read_links(host.settings, valid_slot_ids)
    distance_unit = normalize_unit(host.settings.value(UNIT_KEY, "mm"))
    for key in ("rgb_layout_diagram", "rgb_case_preview_diagram", "case_cooling_diagram",
                "cooling_layout_diagram", "assistant_layout_diagram"):
        diagram = getattr(host, key, None)
        if diagram is None:
            continue
        diagram.set_case_template(case_template(host.rgb_case_template_id))
        diagram.set_cooling_visual(str(host.settings.value("rgb_studio/cooling_visual", "auto")))
        diagram.set_slots(cooling_slots(host) if "cooling" in key or "assistant" in key else host.rgb_layout_slots)
        diagram.set_channel_assignments(assignments)
        diagram.set_channel_names({c.stable_id: channel_caption(host, c) for c in host.case_mappable_mainboard_channels()})
        diagram.set_topology_labels(labels)
        diagram.set_led_paths(led_paths)
        diagram.set_distance_links(distance_links, distance_unit)
        diagram.set_led_animations(led_animations, host)
        if key in {"rgb_layout_diagram", "rgb_case_preview_diagram", "case_cooling_diagram"}:
            diagram.set_selected_slot(host.rgb_layout_selected_slot_id)
    if hasattr(host, "case_component_summary"):
        host.case_component_summary.refresh()
    if not hasattr(host, "case_topology_table"):
        return
    if hasattr(host, "case_spatial_panel"):
        host.case_spatial_panel.refresh()
    host.case_cooling_box.setVisible(not layout_synchronized(host))
    combo = host.case_pwm_combo
    combo.blockSignals(True)
    combo.clear()
    combo.addItem("—", "")
    for channel in host.case_mappable_mainboard_channels():
        combo.addItem(channel_caption(host, channel), channel.stable_id)
        combo.setItemData(combo.count() - 1, channel_details(channel), Qt.ItemDataRole.ToolTipRole)
    current = next((key for key, value in assignments.items() if value == host.rgb_layout_selected_slot_id), "")
    combo.setCurrentIndex(max(0, combo.findData(current)))
    combo.blockSignals(False)
    table = host.case_topology_table
    table.blockSignals(True)
    table.setRowCount(len(host.rgb_layout_slots[:64]))
    for row, slot in enumerate(host.rgb_layout_slots[:64]):
        slot_id = slot.slot_id or slot.position
        channels = [key for key, value in assignments.items() if value == slot_id]
        channel_by_id = {c.stable_id: c for c in host.case_mappable_mainboard_channels()}
        pwm = " · ".join(channel_caption(host, channel_by_id[key]) for key in channels if key in channel_by_id)
        targets = display_header_targets(host, slot)
        lighting = " | ".join(f"{source.name} · {name}" for source, name, _gpu in targets)
        counts = []
        for source, name, _gpu in targets:
            stored = host.rgb_zone_configurations.get(host.openrgb_stable_ids.get(source.index), {})
            values = next((v for key, v in stored.items() if key.casefold() == name.casefold()), None)
            if values:
                counts.append(str(values["units"] * values["leds_per_unit"]))
        if lighting and counts:
            lighting += f" · {' | '.join(counts)} LEDs"
        elif not lighting and slot_declares_lighting(slot, targets):
            lighting = slot.connection
        cooling = pwm if slot_supports_pwm(slot) else ""
        if slot_supports_pwm(slot) and not cooling:
            cooling = host.tr_static("Lüfteranschluss zuordnen")
        for column, text in enumerate((slot.name, host.tr_static(slot_build_caption(slot)), lighting, cooling)):
            item = QTableWidgetItem(text)
            if column == 3:
                item.setToolTip(" | ".join(channel_details(channel_by_id[key]) for key in channels if key in channel_by_id))
            if not text and column in {2, 3}:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            if column == 0: item.setData(Qt.ItemDataRole.UserRole, slot_id)
            table.setItem(row, column, item)
        if slot_id == host.rgb_layout_selected_slot_id:
            table.selectRow(row)
    table.resizeRowsToContents()
    table.blockSignals(False)
    if hasattr(host, "case_analysis_label"):
        host.case_analysis_label.setText(analyze_case_topology(host))
