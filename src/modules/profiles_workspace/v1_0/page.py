# SPDX-License-Identifier: GPL-3.0-or-later
"""Profile library, responsive saved-content cards and explicit edit/import panels."""
from PySide6.QtCore import Qt, QSignalBlocker, QTimer
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QFormLayout,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QApplication, QScrollArea, QTableWidget, QTableWidgetItem, QTreeWidget, QVBoxLayout, QWidget)
from modules.ui_performance.v1_1.compact_panels import Disclosure, ResponsiveColumns
from modules.navigation_settings.v1_0.artwork import category_icon
from .cards import ProfileCard
from .model import matches, summaries


def button(text, callback, layout):
    widget = QPushButton(text); widget.clicked.connect(callback)
    layout.addWidget(widget)
    return widget


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().hide(); item.widget().deleteLater()


class ProfileWorkspace(QWidget):
    def __init__(self, host):
        super().__init__()
        self.host, self.cards = host, {}
        self.selected_id = ""
        self.initializing = True
        outer = QVBoxLayout(self); outer.setContentsMargins(16, 14, 22, 22); outer.setSpacing(12)
        outer.addWidget(host.make_module_hero("☷", "Profile", "Deine Einstellungen. Ein Profil.", "Profile"))
        top = QHBoxLayout()
        top.addWidget(QLabel("Profil beim Start"))
        host.profile_startup_combo = QComboBox(); host.profile_startup_combo.setProperty("i18nTranslateItems", False)
        host.profile_startup_combo.currentIndexChanged.connect(host.profile_startup_changed)
        top.addWidget(host.profile_startup_combo, 1)
        button("Neues Profil", self.new_profile, top)
        outer.addLayout(top)
        note = QLabel("Kühlungsprofile werden erst nach erfolgreicher Kraken-Erkennung übertragen.")
        note.setObjectName("muted"); note.setWordWrap(True); outer.addWidget(note)
        columns = ResponsiveColumns(880); outer.addWidget(columns)
        library = QWidget(); library.setMinimumWidth(240)
        left = QVBoxLayout(library); left.setContentsMargins(0, 0, 0, 0)
        self.search = QLineEdit(); self.search.setPlaceholderText("Profile durchsuchen …")
        self.search.setAccessibleName("Profile durchsuchen …"); left.addWidget(self.search)
        self.filter = QComboBox()
        for ident, title in (("all", "Alle Profile"), ("user", "Eigene Profile"), ("builtin", "Standardprofile")):
            self.filter.addItem(title, ident)
        left.addWidget(self.filter)
        scroller = self.library_scroll = QScrollArea(); scroller.setWidgetResizable(True); scroller.setMinimumHeight(225); scroller.setMaximumHeight(490)
        scroller.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget(); self.card_layout = QVBoxLayout(content); self.card_layout.setContentsMargins(0, 0, 4, 0)
        self.card_layout.setAlignment(Qt.AlignmentFlag.AlignTop); scroller.setWidget(content); left.addWidget(scroller)
        self.count = QLabel(); self.count.setObjectName("muted"); left.addWidget(self.count)
        columns.addWidget(library, 3)
        detail = QWidget(); right = QVBoxLayout(detail); right.setContentsMargins(0, 0, 0, 0); right.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.title = QLabel(); font = self.title.font(); font.setPointSize(19); font.setBold(True); self.title.setFont(font)
        self.title.setStyleSheet("font-size: 22px; font-weight: 700; background: transparent;")
        self.title.setWordWrap(True); right.addWidget(self.title)
        self.description = QLabel(); self.description.setWordWrap(True); self.description.setObjectName("muted"); right.addWidget(self.description)
        actions = QHBoxLayout()
        self.apply = button("Profil anwenden", host.apply_selected_profile, actions)
        self.edit = button("Bearbeiten", lambda: self.open_editor(True), actions)
        self.duplicate = button("Duplizieren", host.duplicate_selected_profile, actions)
        right.addLayout(actions)
        more = QHBoxLayout()
        self.rename = button("Umbenennen", host.rename_selected_profile, more)
        self.delete = button("Löschen", host.delete_selected_profile, more)
        self.export = button("Exportieren", host.export_selected_profile, more)
        right.addLayout(more)
        self.summary_container = QWidget(); self.summary_grid = QGridLayout(self.summary_container)
        self.summary_grid.setContentsMargins(0, 4, 0, 4); self.summary_grid.setSpacing(10)
        right.addWidget(self.summary_container)
        host.profile_contents_summary = QLabel(); host.profile_contents_summary.setWordWrap(True)
        right.addWidget(host.profile_contents_summary)
        columns.addWidget(detail, 7)
        self.editor = self.build_editor(); outer.addWidget(self.editor)
        contents_box = QGroupBox("Gespeicherter Profilinhalt")
        contents = QVBoxLayout(contents_box)
        host.profile_contents_tree = QTreeWidget(); host.profile_contents_tree.setHeaderLabels(["Bereich / Einstellung", "Gespeicherter Wert"])
        host.profile_contents_tree.setMinimumHeight(190); host.profile_contents_tree.setMaximumHeight(350)
        host.profile_contents_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        contents.addWidget(host.profile_contents_tree)
        outer.addWidget(Disclosure("Technische Details", contents_box))
        transfers = QWidget(); transfer_layout = QVBoxLayout(transfers)
        row = QHBoxLayout(); button("Importieren", host.import_profiles, row); button("Exportieren", host.export_selected_profile, row)
        transfer_layout.addLayout(row)
        from modules.profile_bundle.v1_0.controller import build_bundle_controls
        build_bundle_controls(host, transfer_layout)
        self.transfers = Disclosure("Import, Export & Sicherung", transfers)
        outer.addWidget(self.transfers)
        host.profile_status_label = QLabel("Noch kein Profil ausgewählt."); host.profile_status_label.setObjectName("muted"); host.profile_status_label.setWordWrap(True)
        outer.addWidget(host.profile_status_label)
        # Parent-owned compatibility adapter for the existing ID-based CRUD/import API.
        host.profiles_table = QTableWidget(0, 4, self)
        host.profiles_table.setHorizontalHeaderLabels(["Name", "Kategorie", "Beschreibung", "Typ"])
        host.profiles_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        host.profiles_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        host.profiles_table.itemSelectionChanged.connect(host.on_profile_selection_changed)
        host.profiles_table.hide()
        self.search.textChanged.connect(self.filter_cards); self.filter.currentIndexChanged.connect(self.filter_cards)
        self.initializing = False

    def build_editor(self):
        host = self.host
        body = QGroupBox("Profil erstellen oder aktualisieren"); form = QFormLayout(body)
        host.profile_name_input = QLineEdit(); host.profile_name_input.setPlaceholderText("z. B. Gaming, Leise Nacht oder Sommer")
        host.profile_description_input = QLineEdit(); host.profile_description_input.setPlaceholderText("Kurze Beschreibung")
        host.profile_category_combo = QComboBox()
        for category in ("Gesamt", "Kühlung", "GPU", "LCD", "RGB", "Design", "Benutzerdefiniert"):
            host.profile_category_combo.addItem(category, category)
        form.addRow("Name", host.profile_name_input); form.addRow("Kategorie", host.profile_category_combo); form.addRow("Beschreibung", host.profile_description_input)
        areas = QWidget(); grid = QGridLayout(areas); grid.setContentsMargins(0, 0, 0, 0)
        host.profile_section_checks = {}
        for index, (key, title) in enumerate((("cooling", "Kühlung"), ("gpu", "GPU"), ("lcd", "LCD"), ("rgb", "RGB"), ("design", "Design & Anzeige"))):
            check = QCheckBox(title); check.setChecked(True); check.toggled.connect(host.on_profile_sections_changed)
            host.profile_section_checks[key] = check; grid.addWidget(check, index // 3, index % 3)
        host.profile_category_combo.currentIndexChanged.connect(host.apply_profile_category_to_sections)
        form.addRow("Gespeicherte Bereiche", areas)
        note = QLabel("Speichern übernimmt die aktuellen Einstellungen der gewählten Bereiche.")
        note.setWordWrap(True); note.setObjectName("muted"); form.addRow(note)
        actions = QHBoxLayout(); button("Als neues Profil speichern", host.create_profile_from_current, actions)
        self.update = button("Ausgewähltes Profil aktualisieren", host.update_selected_profile, actions); form.addRow(actions)
        return Disclosure("Profil bearbeiten", body)

    def open_editor(self, opened):
        self.editor.button.setChecked(opened)
        if opened: self.host.profile_name_input.setFocus()

    def new_profile(self):
        host = self.host
        host.profiles_table.clearSelection(); host.profiles_table.setCurrentCell(-1, -1)
        self.selected_id = ""
        host.profile_name_input.clear(); host.profile_description_input.clear()
        host.profile_category_combo.setCurrentIndex(0)
        for check in host.profile_section_checks.values(): check.setChecked(True)
        self.show_profile(None); self.open_editor(True)

    def select(self, ident):
        table = self.host.profiles_table
        for row in range(table.rowCount()):
            if table.item(row, 0).data(Qt.ItemDataRole.UserRole) == ident:
                table.selectRow(row); return

    def refresh(self):
        host = self.host; tr = host.tr_static
        profiles = host.all_profiles(); table = host.profiles_table
        previous = host.selected_profile()
        target = str(previous.get("id", "")) if previous else str(host.current_profile_id)
        with QSignalBlocker(table):
            table.setRowCount(len(profiles))
            for row, profile in enumerate(profiles):
                for col, field in enumerate(("name", "category", "description", "builtin")):
                    item = QTableWidgetItem(str(profile.get(field, "")))
                    if col == 0: item.setData(Qt.ItemDataRole.UserRole, str(profile.get("id", "")))
                    table.setItem(row, col, item)
            table.clearSelection(); table.setCurrentCell(-1, -1)
        combo = host.profile_startup_combo
        with QSignalBlocker(combo):
            combo.clear(); combo.addItem(tr("Kein automatisches Profil"), "none"); combo.addItem(tr("Zuletzt verwendetes Profil"), "last")
            for profile in profiles:
                name = str(profile.get("name", "Profil")); combo.addItem(tr(name) if profile.get("builtin") else name, str(profile.get("id", "")))
            combo.setCurrentIndex(max(0, combo.findData(str(host.settings.value("profiles/startup", "none")))))
        clear_layout(self.card_layout); self.cards = {}
        for profile in profiles:
            card = ProfileCard(profile, tr); card.selected.connect(self.select)
            self.cards[str(profile.get("id", ""))] = card; self.card_layout.addWidget(card)
        self.empty = QLabel(tr("Keine passenden Profile.")); self.empty.setWordWrap(True); self.card_layout.addWidget(self.empty)
        self.select(target)
        if not host.selected_profile() and profiles: self.select(str(profiles[0].get("id", "")))
        self.show_profile(host.selected_profile()); self.filter_cards()

    def filter_cards(self, *_args):
        profiles = self.host.all_profiles(); visible = 0
        for profile in profiles:
            card = self.cards.get(str(profile.get("id", "")))
            if card:
                match = matches(profile, self.search.text(), self.filter.currentData())
                card.setVisible(match); visible += int(match)
        if hasattr(self, "empty"): self.empty.setVisible(visible == 0)
        self.count.setText(f"{visible} / {len(profiles)}")
        self.library_scroll.setFixedHeight(min(490, max(85, visible * 72 + 8)))

    def show_profile(self, profile):
        tr = self.host.tr_static
        self.selected_id = str(profile.get("id", "")) if profile else ""
        for ident, card in self.cards.items(): card.set_selected(ident == self.selected_id)
        if self.selected_id in self.cards:
            card = self.cards[self.selected_id]
            QTimer.singleShot(0, lambda: self.library_scroll.ensureWidgetVisible(card, 0, 8) if self.cards.get(self.selected_id) is card else None)
        builtin = bool(profile and profile.get("builtin"))
        self.apply.setEnabled(bool(profile)); self.duplicate.setEnabled(bool(profile)); self.export.setEnabled(bool(profile))
        for control in (self.edit, self.rename, self.delete, self.update): control.setEnabled(bool(profile) and not builtin)
        name = str(profile.get("name", "")) if profile else "Profil auswählen"
        self.title.setText(tr(name) if builtin or not profile else name)
        desc = str(profile.get("description", "")) if profile else "Profil auswählen, um alle gespeicherten Bereiche und Werte zu sehen."
        self.description.setText(tr(desc) if builtin or not profile else desc)
        clear_layout(self.summary_grid)
        self.summary_icons = []
        for index, (_key, title, icon, lines) in enumerate(summaries(profile.get("payload"), tr) if profile else []):
            box = QGroupBox(tr(title)); box.setObjectName("profileSummaryTile"); layout = QHBoxLayout(box)
            symbol = QLabel(); symbol.setPixmap(category_icon(icon, self.palette(), 40).pixmap(40, 40)); layout.addWidget(symbol)
            self.summary_icons.append((symbol, icon))
            text = QLabel("\n".join(lines)); text.setWordWrap(True); text.setMinimumWidth(0); layout.addWidget(text, 1)
            self.summary_grid.addWidget(box, index // 2, index % 2)
        self.host.profile_contents_summary.setText(tr("Auswahl verändert keine Geräte. Erst Anwenden lädt das Profil."))

    def refresh_palette(self):
        for card in self.cards.values(): card.set_selected(card._selected)
        for label, icon in getattr(self, 'summary_icons', []):
            label.setPixmap(category_icon(icon, QApplication.palette(), 40).pixmap(40,40))

    def refresh_language(self):
        if self.initializing: return
        # Rebuild data captions while retaining an unsaved edit and the selection.
        host = self.host
        draft = (host.profile_name_input.text(), host.profile_description_input.text(), host.profile_category_combo.currentData(), {key: check.isChecked() for key, check in host.profile_section_checks.items()})
        self.refresh()
        host._syncing_profile_sections = True
        try:
            host.profile_name_input.setText(draft[0]); host.profile_description_input.setText(draft[1])
            host.profile_category_combo.setCurrentIndex(max(0, host.profile_category_combo.findData(draft[2])))
            for key, checked in draft[3].items(): host.profile_section_checks[key].setChecked(checked)
        finally: host._syncing_profile_sections = False


def build_page(host):
    host.profile_workspace = ProfileWorkspace(host)
    host.load_profiles(); host.profile_workspace.refresh()
    return host.profile_workspace
