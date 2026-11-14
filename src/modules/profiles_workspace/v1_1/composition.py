# SPDX-License-Identifier: GPL-3.0-or-later
"""Profile-local composition. Operations delegate to existing host controllers."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QButtonGroup, QCheckBox, QComboBox,
    QFormLayout, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QMenu, QPushButton, QScrollArea, QSizePolicy, QTableWidget,
    QTreeWidget, QVBoxLayout, QWidget)
from modules.navigation_settings.v1_0.artwork import category_icon
from .layout import WorkspaceColumns, SummaryGrid
from .surfaces import Surface, SectionCard, heading


def button(title, callback, layout, *, primary=False):
    control = QPushButton(title); control.setMinimumHeight(40)
    if primary: control.setObjectName('profilePrimary')
    control.clicked.connect(callback); layout.addWidget(control)
    return control


def build_library(page):
    panel = Surface(); panel.setObjectName('profileLibraryPanel')
    layout = QVBoxLayout(panel); layout.setContentsMargins(16, 18, 16, 18); layout.setSpacing(12)
    heading('Profilbibliothek', layout)
    page.search = QLineEdit(); page.search.setPlaceholderText('Profile durchsuchen …')
    page.search.setAccessibleName('Profile durchsuchen …'); page.search.setMinimumHeight(40)
    layout.addWidget(page.search)
    page.filter = QComboBox(panel); page.filter.hide()
    for ident, title in (('all', 'Alle Profile'), ('user', 'Eigene Profile'), ('builtin', 'Standardprofile')):
        page.filter.addItem(title, ident)
    row = QHBoxLayout(); row.setSpacing(6)
    page.filter_group = QButtonGroup(page); page.filter_buttons = {}
    for ident, title in (('all', 'Alle'), ('user', 'Eigene'), ('builtin', 'Standard')):
        control = QPushButton(title); control.setCheckable(True); control.setMinimumHeight(36)
        control.clicked.connect(lambda _checked=False, key=ident: page.filter.setCurrentIndex(page.filter.findData(key)))
        page.filter_group.addButton(control); page.filter_buttons[ident] = control; row.addWidget(control)
    layout.addLayout(row)
    page.library_scroll = QScrollArea(); page.library_scroll.setWidgetResizable(True)
    page.library_scroll.setFrameShape(QFrame.Shape.NoFrame)
    page.library_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    page.library_scroll.viewport().setAutoFillBackground(False)
    content = QWidget(); page.card_layout = QVBoxLayout(content)
    page.card_layout.setContentsMargins(0, 0, 4, 0); page.card_layout.setSpacing(9)
    page.card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    page.library_scroll.setWidget(content); layout.addWidget(page.library_scroll)
    page.count = QLabel(); page.count.setObjectName('muted'); layout.addWidget(page.count)
    return panel


def build_editor(page):
    host = page.host
    content = QWidget(); form = QFormLayout(content); form.setContentsMargins(0, 0, 0, 0)
    form.setVerticalSpacing(12); form.setHorizontalSpacing(18)
    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
    host.profile_name_input = QLineEdit(); host.profile_name_input.setMinimumHeight(38)
    host.profile_name_input.setPlaceholderText('z. B. Gaming, Leise Nacht oder Sommer')
    host.profile_description_input = QLineEdit(); host.profile_description_input.setMinimumHeight(38)
    host.profile_description_input.setPlaceholderText('Kurze Beschreibung')
    host.profile_category_combo = QComboBox(); host.profile_category_combo.setMinimumHeight(38)
    for category in ('Gesamt', 'Kühlung', 'GPU', 'LCD', 'RGB', 'Design', 'Benutzerdefiniert'):
        host.profile_category_combo.addItem(category, category)
    form.addRow('Name', host.profile_name_input); form.addRow('Beschreibung', host.profile_description_input)
    form.addRow('Kategorie', host.profile_category_combo)
    areas = QWidget(); grid = QGridLayout(areas); grid.setContentsMargins(0, 0, 0, 0); grid.setSpacing(10)
    host.profile_section_checks = {}
    for index, (key, title) in enumerate((('cooling', 'Kühlung'), ('gpu', 'GPU'), ('lcd', 'LCD'), ('rgb', 'RGB'), ('design', 'Design & Anzeige'))):
        check = QCheckBox(title); check.setChecked(True); check.setMinimumHeight(30)
        check.toggled.connect(host.on_profile_sections_changed)
        host.profile_section_checks[key] = check; grid.addWidget(check, index // 2, index % 2)
    host.profile_category_combo.currentIndexChanged.connect(host.apply_profile_category_to_sections)
    form.addRow('Gespeicherte Bereiche', areas)
    actions = QVBoxLayout(); actions.setSpacing(10)
    create = button('Als neues Profil speichern', host.create_profile_from_current, actions, primary=True)
    create.setMaximumWidth(390)
    page.update = button('Ausgewähltes Profil aktualisieren', host.update_selected_profile, actions)
    page.update.setMaximumWidth(390); form.addRow(actions)
    return SectionCard('Profil bearbeiten', 'Speichern übernimmt die aktuellen Einstellungen der gewählten Bereiche.', 'profiles', content)


def build_details(page):
    host = page.host
    content = QWidget(); layout = QVBoxLayout(content); layout.setContentsMargins(0, 0, 0, 0)
    heading('Gespeicherter Profilinhalt', layout)
    host.profile_contents_tree = QTreeWidget()
    host.profile_contents_tree.setHeaderLabels(['Bereich / Einstellung', 'Gespeicherter Wert'])
    host.profile_contents_tree.setMinimumHeight(220); host.profile_contents_tree.setMaximumHeight(380)
    host.profile_contents_tree.setProperty('keepViewportHeight', True)
    host.profile_contents_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(host.profile_contents_tree)
    return SectionCard('Technische Details', 'Alle gespeicherten Werte des ausgewählten Profils ansehen.', 'settings', content)


def build_transfers(page):
    host = page.host
    profiles = Surface(); left = QVBoxLayout(profiles); left.setContentsMargins(16, 16, 16, 16); left.setSpacing(12)
    heading('Einzelne Profile', left)
    note = QLabel('Profile als JSON-Datei importieren oder das ausgewählte Profil exportieren.')
    note.setWordWrap(True); note.setObjectName('muted'); left.addWidget(note)
    button('Importieren', host.import_profiles, left)
    button('Exportieren', host.export_selected_profile, left); left.addStretch()
    backup = Surface(); right = QVBoxLayout(backup); right.setContentsMargins(16, 16, 16, 16); right.setSpacing(12)
    heading('Komplettsicherung', right)
    from modules.profile_bundle.v1_0.controller import build_bundle_controls
    build_bundle_controls(host, right)
    right.addStretch()
    from modules.ui_performance.v1_1.compact_panels import ResponsiveColumns
    columns = ResponsiveColumns(700); columns.addWidget(profiles); columns.addWidget(backup)
    columns.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
    return SectionCard('Import, Export & Sicherung', 'Einzelne Profile übertragen oder alle OHC-Einstellungen sichern.', 'snapshot_manager', columns)


def build_detail(page):
    host = page.host
    panel = Surface(); panel.setObjectName('profileDetailPanel')
    layout = QVBoxLayout(panel); layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(18)
    header = QHBoxLayout(); header.setSpacing(16)
    page.profile_icon = QLabel(); page.profile_icon.setFixedSize(64, 64); header.addWidget(page.profile_icon)
    captions = QVBoxLayout(); captions.setSpacing(7)
    page.title = QLabel(); page.title.setWordWrap(True)
    page.title.setStyleSheet('font-size: 24px; font-weight: 700; background: transparent;')
    page.description = QLabel(); page.description.setWordWrap(True); page.description.setObjectName('muted')
    page.badge = QLabel(); page.badge.setWordWrap(True); page.badge.setObjectName('muted')
    captions.addWidget(page.title); captions.addWidget(page.description); captions.addWidget(page.badge)
    header.addLayout(captions, 1); layout.addLayout(header)
    actions = QHBoxLayout(); actions.setSpacing(10)
    page.apply = button('Profil anwenden', host.apply_selected_profile, actions, primary=True)
    page.apply.setMaximumWidth(260)
    page.edit = button('Bearbeiten', lambda: page.open_editor(True), actions); page.edit.setMaximumWidth(170)
    page.more_button = QPushButton('Weitere Aktionen'); page.more_button.setMinimumHeight(40)
    page.more_menu = QMenu(page.more_button)
    for attr, title, callback in (('duplicate', 'Duplizieren', host.duplicate_selected_profile),
                                  ('rename', 'Umbenennen', host.rename_selected_profile),
                                  ('export', 'Exportieren', host.export_selected_profile),
                                  ('delete', 'Löschen', host.delete_selected_profile)):
        action = page.more_menu.addAction(title); action.triggered.connect(callback); setattr(page, attr, action)
    page.more_button.setMenu(page.more_menu); actions.addWidget(page.more_button); actions.addStretch()
    layout.addLayout(actions)
    page.summary_container = SummaryGrid(); page.summary_grid = page.summary_container.grid
    layout.addWidget(page.summary_container)
    host.profile_contents_summary = QLabel(); host.profile_contents_summary.setWordWrap(True)
    host.profile_contents_summary.setObjectName('muted'); layout.addWidget(host.profile_contents_summary)
    page.editor = build_editor(page); page.details = build_details(page); page.transfers = build_transfers(page)
    for section in (page.editor, page.details, page.transfers): layout.addWidget(section)
    host.profile_status_label = QLabel('Noch kein Profil ausgewählt.')
    host.profile_status_label.setWordWrap(True); host.profile_status_label.setObjectName('muted')
    layout.addWidget(host.profile_status_label)
    return panel


def build_workspace(page):
    host = page.host
    outer = QVBoxLayout(page); outer.setContentsMargins(0, 0, 0, 0)
    page.scroll = QScrollArea(); page.scroll.setObjectName('profileWorkspaceScroll')
    page.scroll.setWidgetResizable(True); page.scroll.setFrameShape(QFrame.Shape.NoFrame)
    page.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    page.scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
    page.scroll.viewport().setAutoFillBackground(False)
    page.content = QWidget(); page.content.setMaximumWidth(1660)
    layout = QVBoxLayout(page.content); layout.setContentsMargins(20, 18, 20, 24); layout.setSpacing(18)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop); layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
    hero_row = QHBoxLayout()
    hero_row.addWidget(host.make_module_hero('☷', 'Profile', 'Deine Einstellungen. Ein Profil.', 'Profile'), 1)
    button('Neues Profil', page.new_profile, hero_row, primary=True)
    layout.addLayout(hero_row)
    startup = Surface(); startup_row = QHBoxLayout(startup); startup_row.setContentsMargins(16, 12, 16, 12)
    page.startup_icon = QLabel(); page.startup_icon.setPixmap(category_icon('automations', page.palette(), 28).pixmap(28, 28)); startup_row.addWidget(page.startup_icon)
    startup_row.addWidget(QLabel('Profil beim Start')); startup_row.addStretch()
    host.profile_startup_combo = QComboBox(); host.profile_startup_combo.setMinimumHeight(38)
    host.profile_startup_combo.setMinimumWidth(250); host.profile_startup_combo.setMaximumWidth(430)
    host.profile_startup_combo.setProperty('i18nTranslateItems', False)
    host.profile_startup_combo.currentIndexChanged.connect(host.profile_startup_changed)
    startup_row.addWidget(host.profile_startup_combo, 1); layout.addWidget(startup)
    note = QLabel('Kühlungsprofile werden erst nach erfolgreicher Kraken-Erkennung übertragen.')
    note.setObjectName('muted'); note.setWordWrap(True); layout.addWidget(note)
    library, detail = build_library(page), build_detail(page)
    page.columns = WorkspaceColumns(library, detail); layout.addWidget(page.columns)
    page.scroll.setWidget(page.content); outer.addWidget(page.scroll)
    host.profiles_table = QTableWidget(0, 4, page)
    host.profiles_table.setHorizontalHeaderLabels(['Name', 'Kategorie', 'Beschreibung', 'Typ'])
    host.profiles_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    host.profiles_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    host.profiles_table.itemSelectionChanged.connect(host.on_profile_selection_changed); host.profiles_table.hide()
    page.search.textChanged.connect(page.filter_cards); page.filter.currentIndexChanged.connect(page.filter_cards)
