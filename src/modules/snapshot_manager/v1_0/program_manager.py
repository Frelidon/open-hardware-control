#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Installed/running application picker for Snapshot Manager rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shlex
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QVBoxLayout, QWidget,
)

from .model import normalize_process_names


@dataclass(frozen=True)
class ProgramChoice:
    name: str
    executable: str
    source: str


def _desktop_value(lines: list[str], key: str) -> str:
    prefix = f"{key}="
    return next((line[len(prefix):].strip() for line in lines if line.startswith(prefix)), "")


def installed_programs(roots: tuple[Path, ...] | None = None) -> tuple[ProgramChoice, ...]:
    """Read bounded desktop entries without launching or trusting their commands."""
    locations = roots or (
        Path.home() / ".local/share/applications",
        Path("/usr/local/share/applications"),
        Path("/usr/share/applications"),
    )
    choices: dict[str, ProgramChoice] = {}
    for root in locations:
        try:
            entries = sorted(root.glob("*.desktop"))[:1200]
        except OSError:
            continue
        for entry in entries:
            try:
                lines = entry.read_text(encoding="utf-8", errors="replace").splitlines()[:300]
            except OSError:
                continue
            if _desktop_value(lines, "NoDisplay").casefold() == "true":
                continue
            display_name = _desktop_value(lines, "Name")[:120]
            raw_exec = _desktop_value(lines, "Exec")[:1024]
            try:
                tokens = shlex.split(raw_exec, posix=True)
            except ValueError:
                continue
            executable = next((token for token in tokens if token and not token.startswith("%")), "")
            launcher = Path(executable).name
            if launcher == "env":
                executable = next((
                    token for token in tokens[1:]
                    if token and not token.startswith("-") and "=" not in token and not token.startswith("%")
                ), executable)
            elif launcher in {"flatpak", "snap"}:
                candidates = [
                    token for token in tokens[1:]
                    if token not in {"run"} and not token.startswith("-") and not token.startswith("%")
                ]
                executable = candidates[-1] if candidates else executable
            process_name = Path(executable).name
            normalized = normalize_process_names(process_name)
            if not display_name or not normalized:
                continue
            key = normalized[0]
            choices.setdefault(key, ProgramChoice(display_name, key, "installed"))
    return tuple(sorted(choices.values(), key=lambda item: item.name.casefold()))


def running_programs(proc_root: Path = Path("/proc")) -> tuple[ProgramChoice, ...]:
    choices: dict[str, ProgramChoice] = {}
    try:
        entries = list(proc_root.iterdir())[:32768]
    except OSError:
        return ()
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            name = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        normalized = normalize_process_names(name)
        if normalized:
            key = normalized[0]
            choices.setdefault(key, ProgramChoice(name[:120], key, "running"))
    return tuple(sorted(choices.values(), key=lambda item: item.name.casefold()))


def recent_running_programs(
    proc_root: Path = Path("/proc"), *, limit: int = 20,
) -> tuple[ProgramChoice, ...]:
    """Return up to 20 recently started executables without launching them."""

    candidates: list[tuple[int, ProgramChoice]] = []
    try:
        entries = list(proc_root.iterdir())[:32768]
    except OSError:
        return ()
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            name = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()
            fields = (entry / "stat").read_text(encoding="utf-8", errors="replace").split()
            started = int(fields[21])
        except (OSError, ValueError, IndexError):
            continue
        normalized = normalize_process_names(name)
        if normalized:
            key = normalized[0]
            candidates.append((started, ProgramChoice(name[:120], key, "recent")))
    result: list[ProgramChoice] = []
    seen: set[str] = set()
    for _started, choice in sorted(candidates, key=lambda item: item[0], reverse=True):
        if choice.executable in seen:
            continue
        seen.add(choice.executable)
        result.append(choice)
        if len(result) >= max(1, min(20, int(limit))):
            break
    return tuple(result)


class ProgramManagerPanel(QFrame):
    """Inline application picker; file dialogs are used only for explicit browsing."""

    def __init__(self, translate: Callable[[str], str], initial: object,
                 initial_paths: object,
                 changed: Callable[[tuple[str, ...]], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.tr_text = translate
        self.changed = changed
        self._selected = list(normalize_process_names(initial))
        self._labels = {name: name for name in self._selected}
        for raw_path in str(initial_paths or "").splitlines():
            path = raw_path.strip()
            normalized = normalize_process_names(path)
            if normalized:
                name = normalized[0]
                if name not in self._selected:
                    self._selected.append(name)
                self._labels[name] = path[:1024]
        self._choices: tuple[ProgramChoice, ...] = ()
        self._loaded = False
        self.setObjectName("snapshotProgramManager")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        heading = QHBoxLayout()
        title = QLabel(self.tr_text("Programme für die Spielerkennung"))
        title.setObjectName("sectionTitle")
        heading.addWidget(title)
        heading.addStretch()
        self.close_button = QPushButton(self.tr_text("Manager schließen"))
        heading.addWidget(self.close_button)
        layout.addLayout(heading)
        hint = QLabel(self.tr_text(
            "Installierte oder gerade laufende Programme auswählen. Alternativ kann ein ausführbarer Pfad angegeben werden."
        ))
        hint.setWordWrap(True)
        hint.setObjectName("muted")
        layout.addWidget(hint)
        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(self.tr_text("Programmliste durchsuchen …"))
        self.search.textChanged.connect(self._filter)
        refresh = QPushButton(self.tr_text("Programmliste neu laden"))
        refresh.clicked.connect(self.refresh_choices)
        search_row.addWidget(self.search, 1)
        search_row.addWidget(refresh)
        layout.addLayout(search_row)
        self.available = QListWidget()
        self.available.setMinimumHeight(180)
        self.available.itemDoubleClicked.connect(lambda _item: self.add_available())
        layout.addWidget(self.available)
        add_row = QHBoxLayout()
        add = QPushButton(self.tr_text("Ausgewähltes Programm hinzufügen"))
        add.clicked.connect(self.add_available)
        self.path = QLineEdit()
        self.path.setPlaceholderText(self.tr_text("Pfad oder Prozessname"))
        browse = QPushButton(self.tr_text("Pfad auswählen …"))
        browse.clicked.connect(self.browse_path)
        add_path = QPushButton(self.tr_text("Pfad hinzufügen"))
        add_path.clicked.connect(self.add_path)
        add_row.addWidget(add)
        add_row.addWidget(self.path, 1)
        add_row.addWidget(browse)
        add_row.addWidget(add_path)
        layout.addLayout(add_row)
        layout.addWidget(QLabel(self.tr_text("Aktive Programmauswahl"), objectName="cardLabel"))
        self.selected = QListWidget()
        self.selected.setMinimumHeight(100)
        layout.addWidget(self.selected)
        remove = QPushButton(self.tr_text("Ausgewähltes Programm entfernen"))
        remove.clicked.connect(self.remove_selected)
        layout.addWidget(remove, 0, Qt.AlignmentFlag.AlignLeft)
        self._render_selected()

    def names(self) -> tuple[str, ...]:
        return tuple(self._selected)

    def paths(self) -> tuple[str, ...]:
        return tuple(
            label for name in self._selected
            if "/" in (label := self._labels.get(name, name))
        )

    def refresh_choices(self) -> None:
        recent = recent_running_programs()
        combined = {item.executable: item for item in recent}
        for item in installed_programs():
            combined.setdefault(item.executable, item)
        for item in running_programs():
            combined.setdefault(item.executable, item)
        recent_keys = {item.executable for item in recent}
        self._choices = tuple(sorted(
            combined.values(),
            key=lambda item: (item.executable not in recent_keys, item.name.casefold()),
        ))
        self._loaded = True
        self._filter(self.search.text())

    def ensure_loaded(self) -> None:
        if not self._loaded:
            self.refresh_choices()

    def _filter(self, query: str) -> None:
        needle = query.strip().casefold()
        self.available.clear()
        for choice in self._choices:
            if needle and needle not in choice.name.casefold() and needle not in choice.executable.casefold():
                continue
            source = (
                self.tr_text("zuletzt erkannt") if choice.source == "recent"
                else self.tr_text("läuft gerade") if choice.source == "running"
                else self.tr_text("installiert")
            )
            item = QListWidgetItem(f"{choice.name}   ·   {choice.executable}   ·   {source}")
            item.setData(Qt.ItemDataRole.UserRole, choice.executable)
            self.available.addItem(item)

    def add_available(self) -> None:
        item = self.available.currentItem()
        if item is not None:
            self._add(item.data(Qt.ItemDataRole.UserRole))

    def browse_path(self) -> None:
        filename, _selected_filter = QFileDialog.getOpenFileName(
            self, self.tr_text("Ausführbares Programm auswählen"), str(Path.home()),
        )
        if filename:
            self.path.setText(filename)

    def add_path(self) -> None:
        self._add(self.path.text())
        self.path.clear()

    def _add(self, value: object) -> None:
        display = str(value or "").strip()[:1024]
        normalized = normalize_process_names(value)
        if normalized:
            name = normalized[0]
            if name not in self._selected:
                self._selected.append(name)
            if "/" in display:
                self._labels[name] = display
            self._render_selected()
            self.changed(self.names())

    def remove_selected(self) -> None:
        row = self.selected.currentRow()
        if 0 <= row < len(self._selected):
            name = self._selected.pop(row)
            self._labels.pop(name, None)
            self._render_selected()
            self.changed(self.names())

    def _render_selected(self) -> None:
        self.selected.clear()
        self.selected.addItems(
            label if label == name else f"{label}   →   {name}"
            for name in self._selected
            for label in (self._labels.get(name, name),)
        )
