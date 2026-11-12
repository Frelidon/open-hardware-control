# SPDX-License-Identifier: GPL-3.0-or-later
"""Embedded reference editor; Save delegates persistence, never device writes."""
from __future__ import annotations

from pathlib import Path
from itertools import islice
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QAbstractItemView, QFileDialog, QFrame, QHBoxLayout,
    QGridLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)
from .model import DesignLibraryState, SUPPORTED_SUFFIXES, friendly_media_name, library_media_items


class DesignLibraryPanel(QFrame):
    """Draft-only media/source manager usable directly inside either LCD page.

    Pass an already indexed media snapshot for an embedded page. Opening the
    panel then performs no recursive scan. The compatibility dialog can omit it.
    """
    saved = Signal(object)
    canceled = Signal()

    def __init__(self, state, translator=None, parent=None, *, known_media=None):
        super().__init__(parent)
        self.tr_text = translator or (lambda text: text)
        self.setObjectName('lcdMediaManagerPanel')
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet('QFrame#lcdMediaManagerPanel {border: 1px solid palette(mid); border-radius: 12px; background: palette(base);}')
        self._captions = []
        outer = QVBoxLayout(self); outer.setContentsMargins(18, 16, 18, 16); outer.setSpacing(12)
        header = QHBoxLayout()
        title = self._label('LCD-Manager'); title.setStyleSheet('font-size: 18px; font-weight: 650; background: transparent;')
        header.addWidget(title); header.addStretch()
        self.close_button = self._button('Schließen', self.canceled.emit); header.addWidget(self.close_button)
        outer.addLayout(header)
        note = self._label('Quellen und Medien verwalten · Änderungen erst mit Speichern übernehmen.')
        note.setWordWrap(True); note.setObjectName('muted'); outer.addWidget(note)
        actions = QGridLayout(); actions.setSpacing(8)
        self.add_folder_button = self._button('Ordner hinzufügen', self.add_folder)
        self.add_files_button = self._button('Dateien hinzufügen', self.add_files)
        self.rename_button = self._button('Umbenennen', self.rename_selected)
        self.remove_button = self._button('Aus Bibliothek entfernen', self.remove_selected)
        for index, control in enumerate((self.add_folder_button, self.add_files_button, self.rename_button, self.remove_button)):
            actions.addWidget(control, index // 2, index % 2)
        outer.addLayout(actions)
        self.tree = QTreeWidget(); self.tree.setObjectName('lcdManagerSources'); self.tree.setColumnCount(3)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.setAlternatingRowColors(True); self.tree.setProperty('keepViewportHeight', True)
        self.tree.setMinimumHeight(86); self.tree.setMaximumHeight(360)
        self.tree.header().setStretchLastSection(True)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tree.itemExpanded.connect(self._fit_tree_height)
        self.tree.itemCollapsed.connect(self._fit_tree_height)
        self.tree.itemDoubleClicked.connect(lambda *_args: self.rename_selected())
        self.tree.itemSelectionChanged.connect(self._update_actions)
        outer.addWidget(self.tree)
        self.empty_label = self._label('Noch keine eigenen Quellen. Füge einen Ordner oder einzelne Medien hinzu.')
        self.empty_label.setWordWrap(True); self.empty_label.setObjectName('muted'); outer.addWidget(self.empty_label)
        self.alias_row = QWidget(); rename = QHBoxLayout(self.alias_row); rename.setContentsMargins(0, 0, 0, 0)
        rename.addWidget(self._label('Anzeigename'))
        self.alias_input = QLineEdit(); self.alias_input.setMaxLength(96); rename.addWidget(self.alias_input, 1)
        self.alias_input.returnPressed.connect(self.apply_alias)
        rename.addWidget(self._button('Namen übernehmen', self.apply_alias)); outer.addWidget(self.alias_row)
        self.alias_row.hide(); self._alias_path = None
        safe = self._label('Entfernen blendet nur in OHC aus. Originaldateien bleiben unverändert.')
        safe.setWordWrap(True); safe.setObjectName('muted'); outer.addWidget(safe)
        self.count_label = QLabel(); self.count_label.setObjectName('muted'); outer.addWidget(self.count_label)
        footer = QHBoxLayout(); footer.addStretch()
        self.cancel_button = self._button('Abbrechen', self.canceled.emit); footer.addWidget(self.cancel_button)
        self.save_button = self._button('Speichern', self.commit); self.save_button.setObjectName('primaryAction')
        footer.addWidget(self.save_button); outer.addLayout(footer)
        self.set_state(state, known_media=known_media)

    def _label(self, source):
        label = QLabel(self.tr_text(source)); self._captions.append((label, source)); return label

    def _button(self, source, callback):
        control = QPushButton(self.tr_text(source)); control.setMinimumHeight(36)
        control.clicked.connect(callback); self._captions.append((control, source)); return control

    def set_state(self, state, *, known_media=None):
        self._folders = list(state.folders); self._files = list(state.files)
        self._aliases = dict(state.aliases); self._excluded = list(state.excluded)
        self._baseline = self.state()
        self._known_media = tuple(islice(known_media, 2500)) if known_media is not None else None
        self._alias_path = None; self.alias_row.hide(); self._refresh()

    def state(self):
        return DesignLibraryState(tuple(self._folders), tuple(self._files), dict(self._aliases), tuple(self._excluded))

    @staticmethod
    def _folder_media(folder):
        return list(library_media_items(DesignLibraryState((folder,), (), {}, ())))

    def _refresh(self):
        selected = {item.data(0, Qt.ItemDataRole.UserRole) for item in self.tree.selectedItems()}
        expanded = {self.tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
                    for i in range(self.tree.topLevelItemCount()) if self.tree.topLevelItem(i).isExpanded()}
        self.tree.clear(); excluded = set(self._excluded); visible = 0
        for folder in self._folders:
            item = self._item('Ordner', folder); self.tree.addTopLevelItem(item)
            media = (path for path in self._known_media if path.is_relative_to(folder)) if self._known_media is not None else self._folder_media(folder)
            for path in media:
                if path not in excluded and path != folder:
                    item.addChild(self._item('Design', path)); visible += 1
            item.setExpanded(item.data(0, Qt.ItemDataRole.UserRole) in expanded)
        for path in self._files:
            if path not in excluded:
                self.tree.addTopLevelItem(self._item('Datei', path)); visible += 1
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            for candidate in [item] + [item.child(i) for i in range(item.childCount())]:
                candidate.setSelected(candidate.data(0, Qt.ItemDataRole.UserRole) in selected)
        count = len(self._folders) + len(self._files)
        self.empty_label.setVisible(count == 0)
        self._visible_count = visible
        self.tree.setVisible(count > 0)
        self._fit_tree_height()
        self.refresh_language(); self._update_actions()

    def _fit_tree_height(self, *_args):
        rows = sum(1 + (self.tree.topLevelItem(index).childCount() if self.tree.topLevelItem(index).isExpanded() else 0)
                   for index in range(self.tree.topLevelItemCount()))
        self.tree.setFixedHeight(min(360, max(86, rows * 30 + 38)))

    def _item(self, kind, path):
        item = QTreeWidgetItem([self.tr_text(kind), friendly_media_name(path, self._aliases.get(str(path), '')), str(path)])
        item.setData(0, Qt.ItemDataRole.UserRole, (kind, str(path)))
        item.setToolTip(1, item.text(1)); item.setToolTip(2, str(path)); return item

    def _update_actions(self):
        selected = self.tree.selectedItems()
        self.rename_button.setEnabled(len(selected) == 1); self.remove_button.setEnabled(bool(selected))
        self.save_button.setEnabled(self.state() != self._baseline)
        self.add_folder_button.setEnabled(len(self._folders) < 32)
        self.add_files_button.setEnabled(len(self._files) < 500)

    def refresh_language(self):
        self.count_label.setText(f"{self.tr_text('Quellen')}: {len(self._folders) + len(self._files)} · {self.tr_text('Medien')}: {self._visible_count}")
        for widget, source in self._captions: widget.setText(self.tr_text(source))
        self.tree.setHeaderLabels([self.tr_text(source) for source in ('Typ', 'Name', 'Quelle')])
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            for candidate in [item] + [item.child(i) for i in range(item.childCount())]:
                kind, _path = candidate.data(0, Qt.ItemDataRole.UserRole)
                candidate.setText(0, self.tr_text(kind))

    def add_folder(self):
        selected = QFileDialog.getExistingDirectory(self, self.tr_text('Importieren'), str(Path.home()))
        if not selected: return
        raw = Path(selected).expanduser()
        if raw.is_symlink(): return
        path = raw.resolve()
        if path.is_dir() and path not in self._folders and len(self._folders) < 32:
            self._folders.append(path); self._refresh()

    def add_files(self):
        suffixes = ' '.join(f'*{suffix}' for suffix in sorted(SUPPORTED_SUFFIXES))
        selected, _filter = QFileDialog.getOpenFileNames(self, self.tr_text('Importieren'), str(Path.home()), f"{self.tr_text('Medien')} ({suffixes})")
        for value in selected[:500]:
            raw = Path(value).expanduser()
            if raw.is_symlink(): continue
            path = raw.resolve()
            if path.is_file() and path.suffix.casefold() in SUPPORTED_SUFFIXES and path not in self._files and len(self._files) < 500:
                self._files.append(path)
            if path in self._excluded: self._excluded.remove(path)
        self._refresh()

    def rename_selected(self):
        selected = self.tree.selectedItems()
        if len(selected) != 1: return
        _kind, raw_path = selected[0].data(0, Qt.ItemDataRole.UserRole)
        self._alias_path = raw_path
        self.alias_input.setText(self._aliases.get(raw_path, friendly_media_name(Path(raw_path))))
        self.alias_row.show(); self.alias_input.setFocus(); self.alias_input.selectAll()

    def apply_alias(self):
        if not self._alias_path: return
        clean = self.alias_input.text().replace('\n', ' ').replace('\r', ' ').strip()[:96]
        if clean and clean != friendly_media_name(Path(self._alias_path)):
            self._aliases[self._alias_path] = clean
        else: self._aliases.pop(self._alias_path, None)
        self.alias_row.hide(); self._alias_path = None; self._refresh()

    def remove_selected(self):
        for item in self.tree.selectedItems():
            kind, raw_path = item.data(0, Qt.ItemDataRole.UserRole); path = Path(raw_path)
            if kind == 'Ordner':
                if path in self._folders: self._folders.remove(path)
                self._excluded = [entry for entry in self._excluded if not entry.is_relative_to(path)]
                self._aliases = {key: value for key, value in self._aliases.items() if not Path(key).is_relative_to(path)}
            elif kind == 'Datei':
                if path in self._files: self._files.remove(path)
                self._aliases.pop(raw_path, None)
            elif path not in self._excluded: self._excluded.append(path)
        self.alias_row.hide(); self._alias_path = None; self._refresh()

    def commit(self):
        if self._alias_path is not None: self.apply_alias()
        self.saved.emit(self.state())
