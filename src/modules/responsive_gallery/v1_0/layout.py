#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small reusable helpers for width-aware Qt card galleries."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QGridLayout, QWidget


def responsive_column_count(
    width: int,
    *,
    card_width: int = 180,
    gap: int = 8,
    minimum: int = 1,
    maximum: int = 12,
) -> int:
    """Return the number of complete cards that fit in the current viewport."""

    bounded_card = max(40, int(card_width))
    bounded_gap = max(0, int(gap))
    usable = max(bounded_card, int(width) - 12)
    fitted = max(1, (usable + bounded_gap) // (bounded_card + bounded_gap))
    return max(max(1, minimum), min(max(minimum, maximum), fitted))


def reflow_grid(
    grid: QGridLayout,
    widgets: Iterable[QWidget],
    columns: int,
    *,
    centered: bool = True,
) -> None:
    """Reinsert existing widgets and distribute spare width across columns."""

    while grid.count():
        grid.takeAt(0)
    count = max(1, int(columns))
    for column in range(count):
        grid.setColumnStretch(column, 1)
    alignment = Qt.AlignmentFlag.AlignHCenter if centered else Qt.AlignmentFlag.AlignLeft
    for position, widget in enumerate(widgets):
        grid.addWidget(widget, position // count, position % count, alignment)


class ViewportResizeRelay(QObject):
    """Coalesce viewport resize/show events into one gallery relayout callback."""

    def __init__(self, callback: Callable[[], None], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._callback = callback
        self._pending = False

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() in {QEvent.Type.Resize, QEvent.Type.Show} and not self._pending:
            self._pending = True
            QTimer.singleShot(0, self._dispatch)
        return super().eventFilter(watched, event)

    def _dispatch(self) -> None:
        self._pending = False
        self._callback()
