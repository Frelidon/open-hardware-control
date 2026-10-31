"""Deferred LCD work belongs to the page, not an orphaned Qt single-shot."""

from __future__ import annotations

import ast
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]


def _lcd_timer_calls():
    tree = ast.parse((ROOT / "src/thermalright_display_ui.py").read_text())
    return [node for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "QTimer"
            and node.func.attr == "singleShot"]


def test_all_deferred_lcd_callbacks_have_their_page_as_context():
    calls = _lcd_timer_calls()
    assert len(calls) >= 14
    assert all(len(call.args) == 3 and isinstance(call.args[1], ast.Name)
               and call.args[1].id == "self" for call in calls)


def test_deleted_page_cancels_initial_library_and_progress_callbacks():
    from PySide6.QtCore import QCoreApplication, QEvent, QTimer
    from PySide6.QtWidgets import QApplication, QLabel, QWidget
    from shiboken6 import isValid

    app = QApplication.instance() or QApplication([])
    callbacks = []

    class Receiver(QWidget):
        def __init__(self):
            super().__init__()
            self.label = QLabel(self)

        def load_initial_library(self):
            callbacks.append("initial-library")
            self.label.setText("library")

        def _hide_thumbnail_progress_if_idle(self):
            callbacks.append("thumbnail-progress")
            self.label.hide()

    targets = ("load_initial_library", "_hide_thumbnail_progress_if_idle")
    calls = [call for call in _lcd_timer_calls()
             if isinstance(call.args[-1], ast.Attribute) and call.args[-1].attr in targets]
    assert len(calls) == 2

    def enqueue(owner):
        # Execute the real production scheduling expressions. Accelerating only
        # the delay exercises both overload/lifetime contracts without a 4s wait.
        timers = SimpleNamespace(singleShot=lambda _delay, context, callback:
                                 QTimer.singleShot(0, context, callback))
        for call in calls:
            exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.Expr(call)], type_ignores=[])),
                         "real-lcd-timer", "exec"), {"QTimer": timers, "self": owner})

    deleted = Receiver()
    enqueue(deleted)
    deleted.deleteLater()
    QCoreApplication.sendPostedEvents(deleted, QEvent.Type.DeferredDelete)
    assert not isValid(deleted)
    app.processEvents()
    assert callbacks == []

    alive = Receiver()
    enqueue(alive)
    app.processEvents()
    assert sorted(callbacks) == ["initial-library", "thumbnail-progress"]
    alive.deleteLater()
    QCoreApplication.sendPostedEvents(alive, QEvent.Type.DeferredDelete)
    assert not isValid(alive)
