# SPDX-License-Identifier: GPL-3.0-or-later
"""GUI-thread card preparation in bounded portions; never starts hidden playback."""
from __future__ import annotations

import time
from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QApplication, QWidget


class GalleryPreparation(QObject):
    MAX_CARDS_PER_TURN = 4
    TURN_BUDGET_SECONDS = 0.008
    IDLE_SECONDS = 3.0

    def __init__(self, studio):
        super().__init__(studio)
        self.studio = studio
        self.last_input = time.monotonic()
        self.jobs = {}
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.advance)
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, watched, event):  # noqa: N802
        if event.type() in {QEvent.Type.MouseButtonPress, QEvent.Type.MouseMove,
                           QEvent.Type.KeyPress, QEvent.Type.Wheel, QEvent.Type.TouchBegin}:
            # LCD studios may store their host in an attribute named `window`,
            # shadowing QWidget.window(). Call the Qt method through its class.
            if isinstance(watched, QWidget) and QWidget.window(watched) is QWidget.window(self.studio):
                self.last_input = time.monotonic()
        return False

    def request(self, entries, *, hardware=False, reuse=False):
        studio = self.studio
        prefix = "hardware" if hardware else "media"
        grid = getattr(studio, f"{prefix}_cards_grid")
        buttons = getattr(studio, f"{prefix}_card_buttons")
        old = dict(buttons)
        chosen = list(entries)[:160 if hardware else 300]
        columns = getattr(studio, f"_{prefix}_gallery_columns")
        # Reserve final height before inserting bounded portions. Otherwise the
        # first empty/half-filled gallery repeatedly changes scroll geometry.
        if grid.parentWidget() is not None:
            rows = (len(chosen) + columns - 1) // columns
            margins = grid.contentsMargins()
            grid.parentWidget().setMinimumHeight(rows * 126 + max(0, rows - 1) * max(0, grid.verticalSpacing())
                                                 + margins.top() + margins.bottom())
        previous = self.jobs.pop(prefix, None)
        if previous is not None: old.update(previous[2])
        while grid.count():
            item = grid.takeAt(0)
            if item.widget() is not None: item.widget().hide()
        buttons.clear()
        paths = {"" if entry is None else str(entry.path) for entry in chosen}
        for path, button in tuple(old.items()):
            if not reuse or path not in paths:
                button.deleteLater()
                old.pop(path)
        self.jobs[prefix] = (chosen, 0, old, hardware)
        setattr(studio, f"_{prefix}_cards_materialized", False)
        self.timer.start(0 if studio.isVisible() else 150)

    def wake(self):
        if self.jobs and not self.studio.shutdown_started: self.timer.start(0)

    def advance(self):
        studio = self.studio
        if studio.shutdown_started:
            self.shutdown()
            return
        visible = studio.isVisible()
        if not visible and time.monotonic() - self.last_input < self.IDLE_SECONDS:
            self.timer.start(150)
            return
        started = time.monotonic()
        created = 0
        for prefix in tuple(self.jobs):
            entries, index, old, hardware = self.jobs[prefix]
            grid = getattr(studio, f"{prefix}_cards_grid")
            buttons = getattr(studio, f"{prefix}_card_buttons")
            columns = getattr(studio, f"_{prefix}_gallery_columns")
            current = str((studio.current_hardware_design_path() if hardware
                           else studio.current_media_path()) or "")
            while index < len(entries) and created < self.MAX_CARDS_PER_TURN:
                entry = entries[index]
                path = "" if entry is None else str(entry.path)
                button = old.pop(path, None)
                if button is None: button = studio._design_card(entry, hardware=hardware)
                button.setChecked(path == current)
                grid.addWidget(button, index // columns, index % columns,
                               Qt.AlignmentFlag.AlignHCenter)
                button.show()
                buttons[path] = button
                index += 1
                created += 1
                if time.monotonic() - started >= self.TURN_BUDGET_SECONDS: break
            if index == len(entries):
                self.jobs.pop(prefix)
                setattr(studio, f"_{prefix}_cards_materialized", True)
            else:
                self.jobs[prefix] = (entries, index, old, hardware)
            if created >= self.MAX_CARDS_PER_TURN or time.monotonic() - started >= self.TURN_BUDGET_SECONDS:
                break
        if self.jobs: self.timer.start(10 if visible else 50)

    def shutdown(self):
        self.timer.stop()
        for _entries, _index, old, _hardware in self.jobs.values():
            for button in old.values(): button.deleteLater()
        self.jobs.clear()
        QApplication.instance().removeEventFilter(self)
