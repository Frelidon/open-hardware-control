#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Case workspace composition extracted from RGB Studio without changing callbacks."""

from PySide6.QtWidgets import QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from thermalright_cooling import LEVITA_DISPLAY_NAME
from modules.rgb_studio.v1_15.argb_controls import build_slot_led_button, build_slot_route_button, build_case_gpu_setup_button
from .diagram import PCLayoutDiagram


def build_case_workspace(self):
    pc_layout_box = QGroupBox("PC-Ansicht · Gehäuse, Profile und Komponentenpositionen")
    pc_layout = QVBoxLayout(pc_layout_box)
    pc_layout.setSpacing(12)
    pc_workspace = QWidget()
    pc_workspace_layout = QHBoxLayout(pc_workspace)
    pc_workspace_layout.setContentsMargins(0, 0, 0, 0)
    pc_workspace_layout.setSpacing(14)
    pc_profile_panel = QFrame()
    pc_profile_panel.setObjectName("compactPanel")
    pc_profile_panel.setMinimumWidth(360)
    pc_profile_panel.setMaximumWidth(520)
    pc_profile_layout = QVBoxLayout(pc_profile_panel)
    pc_profile_layout.setContentsMargins(14, 14, 14, 14)
    pc_profile_layout.setSpacing(12)
    # Keep the internal ``flori`` key for compatibility with already saved profiles.
    layout_aio_name = LEVITA_DISPLAY_NAME if self.is_thermalright_cooling() else "Kraken 360"
    case_actions, layout_actions = self.build_rgb_case_profile_controls(layout_aio_name)
    pc_profile_layout.addLayout(layout_actions)
    pc_profile_layout.addLayout(case_actions)
    layout_edit_actions = QGridLayout()
    layout_edit_actions.setSpacing(7)
    add_layout_slot = QPushButton("+ Lüfterblock hinzufügen")
    add_layout_slot.clicked.connect(self.add_rgb_layout_slot)
    edit_layout_slot = QPushButton("Ausgewählten Block bearbeiten")
    edit_layout_slot.clicked.connect(self.edit_selected_rgb_layout_slot)
    remove_layout_slot = QPushButton("Ausgewählten Block entfernen")
    remove_layout_slot.clicked.connect(self.remove_selected_rgb_layout_slot)
    arrange_layout = QPushButton("Automatisch anordnen")
    arrange_layout.clicked.connect(self.auto_arrange_rgb_layout)
    reverse_layout = QPushButton("Luftstrom umkehren")
    reverse_layout.clicked.connect(self.reverse_selected_rgb_layout_slot)
    split_layout = QPushButton("Block in Einzellüfter teilen")
    split_layout.clicked.connect(self.split_selected_rgb_layout_slot)
    for index, button in enumerate((add_layout_slot, edit_layout_slot, reverse_layout, split_layout, remove_layout_slot, arrange_layout)):
        layout_edit_actions.addWidget(button, index // 2, index % 2)
    pc_profile_layout.addLayout(layout_edit_actions)
    pc_profile_layout.addWidget(build_slot_led_button(self))
    pc_profile_layout.addWidget(build_slot_route_button(self))
    pc_profile_layout.addWidget(build_case_gpu_setup_button(self))
    pc_profile_hint = QLabel(
        "Block ziehen = verschieben; Eckgriff ziehen = Größe ändern. Doppelklick = bearbeiten, auch ohne RGB-Gerät."
    )
    pc_profile_hint.setWordWrap(True)
    pc_profile_hint.setObjectName("muted")
    pc_profile_layout.addWidget(pc_profile_hint)
    pc_profile_layout.addStretch()
    pc_workspace_layout.addWidget(pc_profile_panel, 2)
    self.rgb_layout_diagram = PCLayoutDiagram()
    self.rgb_layout_diagram.slot_moved.connect(self.move_rgb_layout_slot)
    self.rgb_layout_diagram.slot_resized.connect(self.resize_rgb_layout_slot)
    self.rgb_layout_diagram.fan_order_changed.connect(self.reorder_rgb_layout_slot_devices)
    self.rgb_layout_diagram.device_dropped.connect(self.assign_rgb_device_to_layout_slot)
    self.rgb_layout_diagram.slot_selected.connect(self.open_rgb_layout_slot_device_editor)
    self.rgb_layout_diagram.slot_focused.connect(self.focus_rgb_layout_slot)
    pc_workspace_layout.addWidget(self.rgb_layout_diagram, 3)
    from .inline_editor import CaseInspector
    self.case_inspector = CaseInspector(self, pc_profile_panel, self.rgb_layout_diagram)
    pc_workspace_layout.addWidget(self.case_inspector, 2)
    pc_layout.addWidget(pc_workspace)
    layout_note = QLabel(
        "Lüfterblöcke und Komponenten direkt im Bild an ihre reale Position ziehen; OHC erkennt daraus automatisch "
        "Oben, Front, Rückwand/Seite, Boden oder Heck und speichert die Lage. Eine Gerätekachel kann direkt aus "
        "dem Gruppenbereich auf den passenden Block gezogen werden. Ein Klick markiert ihn zum Bearbeiten; "
        "ein Doppelklick öffnet das zugeordnete Gerät samt LED-Zonen direkt zum Bearbeiten. "
        "Cyan = Ansaugung, Orange = Abluft. Meldet ein Hub nur eine logische LED, "
        "kann OHC alle daran gespiegelten Lüfter gemeinsam, aber nicht als getrennte Hardwarekanäle färben. "
        + (
            "Die Thermalright Levita Vision 360 wird als aktuelle Wasserkühlung mit eigenem Pumpen-/Displayblock angezeigt."
            if self.is_thermalright_cooling()
            else "Am Kraken-Radiator zeigt jede Lüftermitte ihre echte NZXT-Kanalnummer; diese Nummern lassen sich "
                 "zwischen Heck, Mitte und Front ziehen und werden in Einstellungen sowie Profilen gespeichert."
        )
    )
    layout_note.setWordWrap(True)
    layout_note.setObjectName("muted")
    pc_layout.addWidget(layout_note)
    self.rgb_case_template_note = QLabel(
        "Thermaltake Retro 360 TG: exakte Herstellerdaten (493 × 235 × 467 mm, ATX/Micro-ATX/Mini-ITX, "
        "bis 360-mm-Radiator und 400-mm-GPU). Die übrigen Gehäuse sind eigene, frei anpassbare "
        "OHC-Schemazeichnungen ohne eingebettete Herstellerbilder."
    )
    self.rgb_case_template_note.setWordWrap(True)
    self.rgb_case_template_note.setObjectName("infoText")
    pc_layout.addWidget(self.rgb_case_template_note)
    self.rgb_layout_status_label = QLabel("PC-Ansicht bereit · Positionen lassen sich direkt verschieben")
    self.rgb_layout_status_label.setWordWrap(True)
    self.rgb_layout_status_label.setObjectName("warningText")
    pc_layout.addWidget(self.rgb_layout_status_label)
    return pc_layout_box
