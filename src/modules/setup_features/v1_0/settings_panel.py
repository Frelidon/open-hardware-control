# SPDX-License-Identifier: GPL-3.0-or-later
"""Compact feature and owner settings shared by Linux and Windows."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QFrame, QGridLayout, QGroupBox, QLabel, QVBoxLayout

from modules.control_authority.v1_0.model import authority_choices
from .model import feature_choices
from .widgets import FeatureCard


DOMAIN_TITLES = {
    "rgb": "RGB",
    "lcd": "LCD",
    "cooling": "Kühlung",
    "gpu": "Grafikkarte",
    "wallpaper": "Wallpaper",
}


def build_feature_settings(host, parent_layout) -> None:
    translate = getattr(host, "tr_static", lambda text: text)

    feature_box = QGroupBox(translate("Funktionen & Bereiche"))
    feature_layout = QVBoxLayout(feature_box)
    feature_note = QLabel(translate(
        "Ausgeschaltete Bereiche geben OHC-Schreibzugriffe frei und verschwinden aus der Navigation. "
        "Sie können jederzeit wieder aktiviert werden."
    ))
    feature_note.setWordWrap(True)
    feature_note.setObjectName("infoText")
    feature_layout.addWidget(feature_note)
    grid = QGridLayout()
    selected = set(host.enabled_features)
    host.feature_setting_cards = {}
    for index, feature in enumerate(feature_choices()):
        card = FeatureCard(feature, translate)
        card.toggle.setChecked(feature.key in selected)
        card.toggle.toggled.connect(
            lambda checked, key=feature.key: host.set_feature_enabled(key, checked)
        )
        host.feature_setting_cards[feature.key] = card
        grid.addWidget(card, index // 2, index % 2)
    feature_layout.addLayout(grid)
    parent_layout.addWidget(feature_box)

    authority_box = QGroupBox(translate("Steuerungszuständigkeit"))
    authority_layout = QVBoxLayout(authority_box)
    authority_note = QLabel(translate(
        "Pro Bereich schreibt genau ein Programm. Bei einem externen Besitzer oder „Nur überwachen“ "
        "beendet OHC seinen eigenen Schreibpfad und bleibt lesend."
    ))
    authority_note.setWordWrap(True)
    authority_note.setObjectName("infoText")
    authority_layout.addWidget(authority_note)
    host.authority_combos = {}
    for domain, title in DOMAIN_TITLES.items():
        row = QFrame(objectName="settingsCard")
        row_layout = QGridLayout(row)
        label = QLabel(translate(title))
        label.setObjectName("cardTitle")
        combo = QComboBox()
        for choice in authority_choices(domain):
            combo.addItem(translate(choice.label), choice.key)
            if not choice.available:
                combo.model().item(combo.count() - 1).setEnabled(False)
        current = str(host.control_authority.get(domain, "auto"))
        combo.setCurrentIndex(max(0, combo.findData(current)))
        status = QLabel()
        status.setObjectName("muted")
        status.setWordWrap(True)
        host.authority_combos[domain] = combo
        host.authority_status_labels[domain] = status
        combo.currentIndexChanged.connect(
            lambda _index, key=domain, control=combo: host.set_control_authority(
                key, control.currentData()
            )
        )
        row_layout.addWidget(label, 0, 0)
        row_layout.addWidget(combo, 0, 1)
        row_layout.addWidget(status, 1, 0, 1, 2)
        authority_layout.addWidget(row)
    parent_layout.addWidget(authority_box)
    host.refresh_authority_status()


def refresh_feature_settings(host) -> None:
    """Refresh captions and current choices without emitting writer signals."""
    translate = getattr(host, "tr_static", str)
    for key, card in getattr(host, "feature_setting_cards", {}).items():
        card.refresh_language(translate)
        card.toggle.blockSignals(True)
        card.toggle.setChecked(key in host.enabled_features)
        card.toggle.blockSignals(False)
    for domain, combo in getattr(host, "authority_combos", {}).items():
        combo.blockSignals(True)
        for index, choice in enumerate(authority_choices(domain)):
            if index < combo.count():
                combo.setItemText(index, translate(choice.label))
        combo.setCurrentIndex(max(0, combo.findData(host.control_authority.get(domain, "auto"))))
        combo.blockSignals(False)
    host.refresh_authority_status()
