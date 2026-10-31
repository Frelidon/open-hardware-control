#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-destructive manager dialog for local LCD folders and media files."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from .model import DesignLibraryState, SUPPORTED_SUFFIXES, friendly_media_name, library_media_items


class DesignLibraryDialog(QDialog):
    """Manage references only; removing an item never deletes its source."""

    def __init__(
        self,
        state: DesignLibraryState,
        translator: Callable[[str], str] | None = None,
        parent=None,
    ) -> None:  # type: ignore[no-untyped-def]
        super().__init__(parent)
        self.tr_text = translator or (lambda text: text)
        self._folders = list(state.folders)
        self._files = list(state.files)
        self._aliases = dict(state.aliases)
        self._excluded = list(state.excluded)
        self.setWindowTitle(self.tr_text("LCD-Manager"))
        self.setMinimumSize(860, 520)
        layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            self.tr_text("Typ"), self.tr_text("Name"), self.tr_text("Quelle"),
        ])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.setAlternatingRowColors(True)
        self.tree.header().setStretchLastSection(True)
        self.tree.itemDoubleClicked.connect(lambda _item, _column: self.rename_selected())
        layout.addWidget(self.tree, 1)
        actions = QHBoxLayout()
        add_folder = QPushButton(self.tr_text("Ordner"))
        add_folder.clicked.connect(self.add_folder)
        add_files = QPushButton(self.tr_text("Datei"))
        add_files.clicked.connect(self.add_files)
        rename = QPushButton(self.tr_text("Umbenennen"))
        rename.clicked.connect(self.rename_selected)
        remove = QPushButton(self.tr_text("Entfernen"))
        remove.clicked.connect(self.remove_selected)
        for button in (add_folder, add_files, rename, remove):
            actions.addWidget(button)
        actions.addStretch()
        layout.addLayout(actions)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(self.tr_text("Speichern"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(self.tr_text("Abbrechen"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._refresh()

    def state(self) -> DesignLibraryState:
        return DesignLibraryState(
            tuple(self._folders), tuple(self._files), dict(self._aliases), tuple(self._excluded),
        )

    @staticmethod
    def _folder_media(folder: Path) -> list[Path]:
        return list(library_media_items(DesignLibraryState((folder,), (), {}, ())))

    def _refresh(self) -> None:
        self.tree.clear()
        excluded = set(self._excluded)
        for path in self._folders:
            item = QTreeWidgetItem([
                self.tr_text("Ordner"), friendly_media_name(path, self._aliases.get(str(path), "")), str(path),
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, ("Ordner", str(path)))
            self.tree.addTopLevelItem(item)
            for media in self._folder_media(path):
                if media in excluded:
                    continue
                child = QTreeWidgetItem([
                    self.tr_text("Design"), friendly_media_name(media, self._aliases.get(str(media), "")), str(media),
                ])
                child.setData(0, Qt.ItemDataRole.UserRole, ("Design", str(media)))
                item.addChild(child)
        for path in self._files:
            if path in excluded:
                continue
            item = QTreeWidgetItem([
                self.tr_text("Datei"), friendly_media_name(path, self._aliases.get(str(path), "")), str(path),
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, ("Datei", str(path)))
            self.tree.addTopLevelItem(item)
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)

    def add_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, self.tr_text("Importieren"), str(Path.home()))
        if not selected:
            return
        path = Path(selected).expanduser().resolve()
        if path.is_dir() and not path.is_symlink() and path not in self._folders and len(self._folders) < 32:
            self._folders.append(path)
            self._refresh()

    def add_files(self) -> None:
        suffixes = " ".join(f"*{suffix}" for suffix in sorted(SUPPORTED_SUFFIXES))
        selected, _filter = QFileDialog.getOpenFileNames(
            self, self.tr_text("Importieren"), str(Path.home()),
            f"{self.tr_text('Medien')} ({suffixes})",
        )
        for value in selected[:500]:
            path = Path(value).expanduser().resolve()
            if path.is_file() and not path.is_symlink() and path.suffix.casefold() in SUPPORTED_SUFFIXES and path not in self._files:
                self._files.append(path)
            if path in self._excluded:
                self._excluded.remove(path)
        self._refresh()

    def rename_selected(self) -> None:
        selected = self.tree.selectedItems()
        if len(selected) != 1:
            return
        item = selected[0]
        _kind, raw_path = item.data(0, Qt.ItemDataRole.UserRole)
        path = Path(raw_path)
        current = self._aliases.get(raw_path, friendly_media_name(path))
        value, accepted = QInputDialog.getText(
            self, self.tr_text("Umbenennen"), self.tr_text("Name"), text=current,
        )
        clean = value.replace("\n", " ").replace("\r", " ").strip()[:96]
        if accepted:
            if clean and clean != friendly_media_name(path):
                self._aliases[raw_path] = clean
            else:
                self._aliases.pop(raw_path, None)
            self._refresh()

    def remove_selected(self) -> None:
        for item in self.tree.selectedItems():
            kind, raw_path = item.data(0, Qt.ItemDataRole.UserRole)
            path = Path(raw_path)
            if kind == "Ordner":
                if path in self._folders:
                    self._folders.remove(path)
                self._excluded = [item for item in self._excluded if not item.is_relative_to(path)]
                self._aliases = {
                    key: value for key, value in self._aliases.items()
                    if not Path(key).is_relative_to(path)
                }
            elif kind == "Datei":
                if path in self._files:
                    self._files.remove(path)
                self._aliases.pop(raw_path, None)
            elif path not in self._excluded:
                self._excluded.append(path)
        self._refresh()
