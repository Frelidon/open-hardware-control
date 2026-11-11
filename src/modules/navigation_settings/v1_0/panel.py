# SPDX-License-Identifier: GPL-3.0-or-later
"""Modern settings cards for the existing customizable navigation."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from modules.feature_lifecycle.v1_0 import feature_lifecycle


MODULE_ROWS = (
    ("gpu", "◈", "Grafikkarte"),
    ("case", "▥", "Gehäuse"),
    ("hardware_checker", "▣✓", "Hardware-Prüfung"),
    ("snapshot_manager", "◫", "Snapshot-Manager"),
    ("automations", "⌁", "Automationszentrale"),
    ("programs", "▦", "Programme"),
    ("cooling", "▥◉", "Kühlung"),
    ("rgb_studio", "◉", "RGB-Studio"),
    ("design_hub", "◈", "Designs & Spiele"),
    ("lcd", "▣", "LCD"),
    ("display_effects", "✦", "Display-Effekte"),
    ("wallpaper_engine", "▧", "Wallpaper Engine"),
    ("openlinkhub", "⇄", "Corsair · OpenLinkHub"),
    ("profiles", "☷", "Profile"),
    ("desktop_designs", "◇", "Desktop-Designs"),
    ("settings", "⚙", "Einstellungen"),
    ("about", "ⓘ", "Über"),
    ("log", "▤", "Log"),
)


def _set_status_dot(dot: QLabel, enabled: bool) -> None:
    dot.setText("●" if enabled else "○")
    dot.setObjectName("moduleVisibilityDotOn" if enabled else "moduleVisibilityDotOff")
    dot.style().unpolish(dot)
    dot.style().polish(dot)


def build_module_visibility_settings(host) -> QGroupBox:
    """Build a second, explicit entrance to navigation module visibility.

    The sidebar customization control remains the recovery anchor.  This panel
    deliberately changes visibility only; it never starts or stops hardware.
    """

    box = QGroupBox(host.tr_static("Module im Seitenmenü"))
    layout = QVBoxLayout(box)
    note = QLabel(host.tr_static(
        "Module hier ein- oder ausblenden. Übersicht, Einstellungen, Navigationseinstellung und Hilfe bleiben immer erreichbar. "
        "Das Ausblenden allein beendet keine laufende Hardwaresteuerung."
    ))
    note.setWordWrap(True)
    note.setObjectName("muted")
    layout.addWidget(note)
    grid = QGridLayout()
    grid.setHorizontalSpacing(10)
    grid.setVerticalSpacing(8)
    host.navigation_module_checkboxes = {}
    host.navigation_module_status_dots = {}
    for index, (key, icon, title) in enumerate(MODULE_ROWS):
        enabled = key == "settings" or key not in host.navigation_user_hidden
        card = QFrame()
        card.setObjectName("moduleVisibilityCard")
        card.setMinimumHeight(54)
        row = QHBoxLayout(card)
        row.setContentsMargins(10, 7, 10, 7)
        row.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setObjectName("moduleVisibilityIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(34, 34)
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title_label = QLabel(host.tr_static(title))
        title_label.setObjectName("moduleVisibilityTitle")
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        lifecycle = feature_lifecycle(key)
        lifecycle_label = QLabel(
            f"{host.tr_static(lifecycle.stage)} · v{lifecycle.version}" if lifecycle else ""
        )
        lifecycle_label.setObjectName("featureLifecycleBadge")
        title_box.addWidget(title_label)
        title_box.addWidget(lifecycle_label)
        dot = QLabel()
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dot.setFixedWidth(20)
        _set_status_dot(dot, enabled)
        row.addWidget(icon_label)
        row.addLayout(title_box, 1)
        row.addWidget(dot)
        if key != "settings":
            checkbox = QCheckBox()
            checkbox.setObjectName("moduleVisibilitySwitch")
            checkbox.setAccessibleName(host.tr_static(title))
            checkbox.setChecked(enabled)
            checkbox.toggled.connect(
                lambda checked, module_key=key, status_dot=dot: (
                    _set_status_dot(status_dot, checked),
                    host.set_navigation_module_enabled(module_key, checked),
                )
            )
            row.addWidget(checkbox)
            host.navigation_module_checkboxes[key] = checkbox
        host.navigation_module_status_dots[key] = dot
        grid.addWidget(card, index // 2, index % 2)
    layout.addLayout(grid)
    show_all = QPushButton(host.tr_static("Alle Module anzeigen"))
    show_all.setObjectName("moduleVisibilityReset")
    show_all.clicked.connect(host.show_all_navigation_modules)
    layout.addWidget(show_all, 0, Qt.AlignmentFlag.AlignRight)
    return box
