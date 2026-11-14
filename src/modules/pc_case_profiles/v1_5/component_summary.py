# SPDX-License-Identifier: GPL-3.0-or-later
"""Selected-component drafts; existing route/profile writers remain authoritative."""
from dataclasses import replace
from PySide6.QtCore import QEvent, QSignalBlocker, Qt
from PySide6.QtWidgets import QFormLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget
from modules.rgb_studio.v1_15.fan_profiles import profile_for_slot, remember_profile, FAN_POSITIONS
from modules.rgb_studio.v1_15.argb_controls import build_slot_led_button, build_slot_route_button
from modules.navigation_settings.v1_0.artwork import category_icon
from modules.ui_sections.v1_0.cards import Surface, heading
from .topology_labels import display_header_targets


class ComponentSummary(Surface):
    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.ApplicationPaletteChange):
            icon = getattr(self, 'empty_icon', None)
            if icon is not None:
                icon.setPixmap(category_icon('case', self.palette(), 70).pixmap(70, 70))

    def __init__(self, host):
        super().__init__()
        self.host = host; self.slot_id = ''; self.dirty = False; self.loaded = None
        self.setMinimumWidth(260); self.setMaximumWidth(420)
        root = QVBoxLayout(self); root.setContentsMargins(20, 20, 20, 20); root.setSpacing(14)
        heading(host.tr_static('Ausgewählte Komponente'), root)
        self.empty_icon = QLabel(); self.empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_icon.setPixmap(category_icon('case', self.palette(), 70).pixmap(70, 70))
        root.addWidget(self.empty_icon)
        self.name = QLabel(); self.name.setWordWrap(True); root.addWidget(self.name)
        self.details = QWidget(); inside = QVBoxLayout(self.details)
        inside.setContentsMargins(0, 0, 0, 0); inside.setSpacing(12)
        form = QFormLayout(); form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form.setVerticalSpacing(12)
        self.count = QSpinBox(); self.count.setRange(1, 12); self.count.setMinimumHeight(40)
        self.leds = QSpinBox(); self.leds.setRange(0, 512); self.leds.setSpecialValueText('—'); self.leds.setMinimumHeight(40)
        self.total = QLabel(); self.connection = QLabel(); self.connection.setWordWrap(True)
        for title, field in (('Anzahl Lüfter', self.count), ('LEDs je Lüfter', self.leds),
                             ('Gesamt', self.total), ('Anschluss', self.connection)):
            form.addRow(host.tr_static(title), field)
        inside.addLayout(form); self.form = form
        self.save = QPushButton(host.tr_static('Änderungen speichern')); self.save.setObjectName('profilePrimary')
        self.save.clicked.connect(self.commit)
        self.led_button = build_slot_led_button(host)
        route = build_slot_route_button(host)
        edit = QPushButton(host.tr_static('Ausgewählten Block bearbeiten')); edit.clicked.connect(host.edit_selected_rgb_layout_slot)
        for control in (self.save, self.led_button, route, edit):
            control.setMinimumHeight(40); inside.addWidget(control)
        root.addWidget(self.details); root.addStretch()
        self.count.valueChanged.connect(self.changed); self.leds.valueChanged.connect(self.changed)
        self.refresh()

    def slot(self):
        return next((s for s in self.host.rgb_layout_slots if (s.slot_id or s.position) == self.host.rgb_layout_selected_slot_id), None)

    def refresh(self):
        slot = self.slot()
        self.details.setVisible(slot is not None); self.empty_icon.setVisible(slot is None)
        if slot is None:
            self.name.setText(self.host.tr_static('Bitte zuerst einen Block in der PC-Ansicht anklicken.'))
            self.save.setEnabled(False)
            self.slot_id = ''; self.loaded = None; self.dirty = False
            return
        identity = slot.slot_id or slot.position
        profile = profile_for_slot(self.host, slot)
        signature = (identity, slot.count, profile['leds_per_fan'])
        self.name.setText(slot.name)
        if identity != self.slot_id or not self.dirty and signature != self.loaded:
            self.slot_id = identity; self.loaded = signature; self.dirty = False
            with QSignalBlocker(self.count): self.count.setValue(max(1, slot.count))
            with QSignalBlocker(self.leds): self.leds.setValue(profile['leds_per_fan'])
        fan = slot.position in FAN_POSITIONS
        for field in (self.count, self.leds, self.total):
            field.setVisible(fan); self.form.labelForField(field).setVisible(fan)
        self.save.setVisible(fan)
        targets = display_header_targets(self.host, slot)
        self.connection.setText(' · '.join(name for _source, name, _gpu in targets) or slot.connection or '—')
        self.total.setText(f'{self.count.value()*self.leds.value()} LEDs' if self.leds.value() else '—')
        self.save.setEnabled(self.dirty)

    def changed(self, *_args):
        if self.slot() is None: return
        self.dirty = True
        self.total.setText(f'{self.count.value()*self.leds.value()} LEDs')
        self.save.setEnabled(True)

    def set_led_draft(self, count):
        slot = self.slot()
        if slot is None or slot.position not in FAN_POSITIONS:
            self.host.show_error(self.host.tr_static('Bitte zuerst einen Lüfterblock auswählen.')); return
        self.leds.setValue(count)
        self.host.case_sections.setCurrentIndex(0)

    def commit(self):
        slot = self.slot()
        if slot is None or (slot.slot_id or slot.position) != self.slot_id: return
        profile = profile_for_slot(self.host, slot); profile['leds_per_fan'] = self.leds.value()
        remember_profile(self.host, self.slot_id, profile)
        updated = replace(slot, count=self.count.value())
        self.host.rgb_layout_slots = [updated if s is slot else s for s in self.host.rgb_layout_slots]
        self.dirty = False
        self.host.save_rgb_workspace(); self.host.refresh_rgb_layout_editor()
