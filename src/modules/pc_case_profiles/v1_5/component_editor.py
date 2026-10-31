# SPDX-License-Identifier: GPL-3.0-or-later
"""Asynchronous component form and settings-only commit, outside the root UI."""
import time
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QLineEdit, QSpinBox, QVBoxLayout,
)
from rgb_devices import RGBLayoutSlot, sanitize_group_name
from modules.gpu_profiles.v1_0.visual_catalog import GPU_VISUAL_PROFILES
from modules.rgb_studio.v1_15.argb_controls import build_slot_led_button, build_slot_route_button, build_case_gpu_setup_button
from modules.rgb_studio.v1_15.fan_profile_editor import FanProfileEditor
from modules.rgb_studio.v1_15.fan_profiles import FAN_POSITIONS, remember_profile
from .case_page import build_slot_pwm_button
from .case_geometry import arrange_case_slots
from .inline_editor import present_editor
from .editor_sections import EditorSections


def build_dialog(host, slot=None):
    tr = host.tr_static
    dialog = QDialog(host)
    dialog.setWindowTitle((tr("Lüfter-/Komponentenblock bearbeiten") + f" · {slot.name}")
                          if slot else tr("Lüfterblock hinzufügen"))
    dialog.setObjectName("caseComponentEditor")
    root = QVBoxLayout(dialog)
    general = QGroupBox(tr("Eigenschaften"))
    form = QFormLayout(general)
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    name = QLineEdit(slot.name if slot else tr("Neuer Lüfterblock"))
    position = QComboBox()
    for label, value in (("Oben", "top"), ("Front", "front"), ("Rückwand/Seite", "side"),
                         ("Netzteilabdeckung/Boden", "bottom"), ("Heck", "rear"),
                         ("Grafikkarte", "gpu"), ("Grafikkartenhalterung", "gpu-support"),
                         ("Arbeitsspeicher", "ram"), ("Pumpenkopf", "pump")):
        position.addItem(tr(label), value)
    position.setCurrentIndex(max(0, position.findData(slot.position if slot else "side")))
    count = QSpinBox(); count.setRange(1, 12); count.setValue(max(1, slot.count if slot else 1))
    scale = QSpinBox(); scale.setObjectName("caseSlotScale"); scale.setRange(25, 200)
    scale.setSuffix(" %"); scale.setValue(round((slot.scale if slot else 1) * 100))
    size = QComboBox()
    for value in (120, 140): size.addItem(f"{value} mm", value)
    size.setCurrentIndex(max(0, size.findData(slot.size_mm if slot and slot.size_mm else 120)))
    airflow = QComboBox()
    for label, value in (("Ansaugung / Intake", "intake"), ("Abluft / Exhaust", "exhaust"),
                         ("Komponente ohne Luftstrom", "component")):
        airflow.addItem(tr(label), value)
    airflow.setCurrentIndex(max(0, airflow.findData(slot.airflow if slot else "intake")))
    visual = QComboBox(); visual.setObjectName("caseSlotVisualKind")
    for label, value in (("Automatisch", "auto"), ("Lüfter", "fans"), ("LED-Streifen", "strip"),
                         ("LED-Ring", "ring"), ("Komponente", "component")):
        visual.addItem(tr(label), value)
    visual.setCurrentIndex(max(0, visual.findData(slot.visual_kind if slot else "auto")))
    visual.setToolTip(tr("Nur die Darstellung im Gehäusebild wird geändert; echte LED-Anzahl und Anschlüsse bleiben unverändert."))
    gpu_visual = QComboBox(); gpu_visual.setObjectName("caseSlotGpuVisual")
    gpu_visual.addItem(tr("Automatisch anhand des Komponentennamens"), "auto")
    for profile in GPU_VISUAL_PROFILES:
        gpu_visual.addItem(tr(profile.label), profile.profile_id)
    gpu_visual.setCurrentIndex(max(0, gpu_visual.findData(slot.gpu_visual if slot else "auto")))
    gpu_visual.setToolTip(tr("Originale OHC-Vektorzeichnung des Kühlers und der Beleuchtung; keine Herstellerbilder und keine Änderung der Hardwaresteuerung."))
    group = QComboBox(); group.setProperty("i18nTranslateItems", False)
    for item in host.rgb_groups: group.addItem(item.name, item.group_id)
    group.setCurrentIndex(max(0, group.findData(slot.group_id if slot else host.rgb_group_picker.currentData())))
    connection = QLineEdit(slot.connection if slot else "")
    connection.setPlaceholderText(tr("z. B. RGB-Hub B7 · PWM SYS-FAN6"))
    for label, widget in (("Name", name), ("Position", position), ("Anzahl", count), ("Größe", size),
                          ("Ansichtsgröße", scale), ("Luftstrom", airflow), ("Darstellung", visual),
                          ("Grafikkarten-Design", gpu_visual), ("RGB-Gruppe", group),
                          ("Anschluss / Notiz", connection)):
        form.addRow(tr(label), widget)
    def sync_gpu_visual():
        visible = position.currentData() == "gpu"
        gpu_visual.setVisible(visible)
        form.labelForField(gpu_visual).setVisible(visible)
    position.currentIndexChanged.connect(sync_gpu_visual)
    sync_gpu_visual()
    fan = FanProfileEditor(host, slot, count) if slot is None or slot.position in FAN_POSITIONS else None
    if fan is not None:
        root.addWidget(EditorSections(host, [("Eigenschaften", general), ("Lüfter", fan)]), 1)
    else:
        root.addWidget(general, 1)
    if slot is not None:
        root.addWidget(build_slot_led_button(
            host, slot.slot_id or slot.position,
            led_count=fan.total if fan else None,
            unit_count=(lambda: count.value()) if fan else None,
        ))
        root.addWidget(build_slot_route_button(host, slot.slot_id or slot.position))
        if slot.position in {"gpu", "gpu-support"}:
            root.addWidget(build_case_gpu_setup_button(host, slot.slot_id or slot.position))
        root.addWidget(build_slot_pwm_button(host, slot.slot_id or slot.position))
    buttons = QDialogButtonBox()
    buttons.addButton(tr("Speichern"), QDialogButtonBox.ButtonRole.AcceptRole)
    buttons.addButton(tr("Abbrechen"), QDialogButtonBox.ButtonRole.RejectRole)
    buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject)
    root.addWidget(buttons)

    def collect():
        slot_id = slot.slot_id or slot.position if slot else f"custom-{time.time_ns()}"
        if fan is not None and position.currentData() in FAN_POSITIONS: remember_profile(host, slot_id, fan.values())
        return RGBLayoutSlot(str(position.currentData()), sanitize_group_name(name.text()), count.value(),
                             str(group.currentData()), " ".join(connection.text().split())[:96],
                             slot.device_ids if slot else (), slot_id, slot.x if slot else .5,
                             slot.y if slot else .5, str(airflow.currentData()), int(size.currentData()), scale.value() / 100,
                             str(visual.currentData()), str(gpu_visual.currentData()))
    return dialog, collect


def open_component(host, slot=None):
    if not host.rgb_groups:
        host.show_error(host.tr_static("Bitte zuerst mindestens eine RGB-Gruppe anlegen."))
        return
    dialog, collect = build_dialog(host, slot)
    def commit():
        # A deleted/replaced slot cannot be resurrected by a stale editor.
        if slot is not None and slot not in host.rgb_layout_slots: return
        updated = collect()
        if slot is None:
            updated = arrange_case_slots([*host.rgb_layout_slots, updated], host.rgb_case_template_id)[-1]
            host.rgb_layout_slots.append(updated)
            host.rgb_layout_selected_slot_id = updated.slot_id
            caption = "Hinzugefügt und gespeichert: "
        else:
            target = slot.slot_id or slot.position
            host.rgb_layout_slots = [updated if (item.slot_id or item.position) == target else item for item in host.rgb_layout_slots]
            host.select_gpu_route_sources()
            for device_id in updated.device_ids: host.rgb_group_assignments[device_id] = updated.group_id
            caption = "Bearbeitet und gespeichert: "
        host.save_rgb_workspace(); host.refresh_rgb_layout_editor()
        host.rgb_layout_status_label.setText(host.tr_static(caption + updated.name))
    dialog.accepted.connect(commit)
    if not present_editor(host, dialog): dialog.exec()
