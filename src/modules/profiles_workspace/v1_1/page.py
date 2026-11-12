# SPDX-License-Identifier: GPL-3.0-or-later
"""Stable-ID profile selection/drafts around a scrollable profile workspace."""
from PySide6.QtCore import Qt, QSignalBlocker, QTimer
from PySide6.QtWidgets import QLabel, QTableWidgetItem, QWidget
from modules.navigation_settings.v1_0.artwork import category_icon
from .cards import ProfileCard
from .model import matches, summaries
from .composition import build_workspace
from .summary import SummaryTile


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget(): item.widget().hide(); item.widget().deleteLater()


class ProfileWorkspace(QWidget):
    def __init__(self, host):
        super().__init__()
        self.host, self.cards = host, {}
        self.selected_id = ""
        self.new_draft = False
        self.initializing = True
        self.summary_tiles = []
        build_workspace(self)
        self.initializing = False

    def open_editor(self, opened):
        was_opened = self.editor.button.isChecked()
        self.editor.button.setChecked(opened)
        if opened:
            self.host.profile_name_input.setFocus()
            from modules.ui_sections.v1_0.reveal import scroller
            controller = scroller(self.editor)
            if controller is not None:
                if was_opened: controller.opened(self.editor)
            else:
                QTimer.singleShot(0, lambda: self.scroll.ensureWidgetVisible(self.host.profile_name_input, 12, 18))

    def new_profile(self):
        host = self.host
        self.new_draft = True
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
                self.new_draft = False
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
        for profile in sorted(profiles, key=lambda item: bool(item.get("builtin"))):
            card = ProfileCard(profile, tr); card.selected.connect(self.select)
            self.cards[str(profile.get("id", ""))] = card; self.card_layout.addWidget(card)
        self.empty = QLabel(tr("Keine passenden Profile.")); self.empty.setWordWrap(True); self.card_layout.addWidget(self.empty)
        if not self.new_draft:
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
        self.library_scroll.setFixedHeight(min(540, max(105, visible * 94 + 8)))
        selected_filter = self.filter.currentData()
        for ident, control in self.filter_buttons.items(): control.setChecked(ident == selected_filter)

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
        payload = profile.get("payload") if profile else {}
        payload = payload if isinstance(payload, dict) else {}
        self.summary_tiles = [SummaryTile(key, title, icon, lines, payload, tr)
                              for key, title, icon, lines in summaries(payload, tr)]
        self.summary_container.set_tiles(self.summary_tiles)
        self.badge.setText(tr("Standardprofil" if builtin else "Eigenes Profil") + " · " +
                           tr(str(profile.get("category", "Gesamt"))) if profile else "")
        self.refresh_palette()
        self.host.profile_contents_summary.setText(tr("Auswahl verändert keine Geräte. Erst Anwenden lädt das Profil."))

    def refresh_palette(self):
        for card in self.cards.values(): card.set_selected(card._selected)
        for tile in self.summary_tiles: tile.refresh_palette()
        for section in (self.editor, self.details, self.transfers): section.refresh_palette()
        self.startup_icon.setPixmap(category_icon("automations", self.palette(), 28).pixmap(28, 28))
        self.profile_icon.setPixmap(category_icon("profiles", self.palette(), 64).pixmap(64, 64))

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
