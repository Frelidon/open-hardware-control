#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Synchronized in-page tab bars for sidebar sections with child pages."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtWidgets import QTabBar


class SectionTabsController:
    """Keep several browser-like tab bars mapped to the same main pages."""

    def __init__(
        self,
        entries: Sequence[tuple[str, int]],
        select_page: Callable[[int], None],
        translator: Callable[[str], str],
    ) -> None:
        self.entries = tuple(entries)
        self.select_page = select_page
        self.translator = translator
        self.bars: list[QTabBar] = []
        self._syncing = False

    def create_bar(self) -> QTabBar:
        bar = QTabBar()
        bar.setObjectName("sectionTabBar")
        bar.setDocumentMode(True)
        bar.setExpanding(False)
        for source, page in self.entries:
            bar.addTab(self.translator(source))
            bar.setTabData(bar.count() - 1, page)
        bar.currentChanged.connect(lambda index, owner=bar: self._selected(owner, index))
        self.bars.append(bar)
        return bar

    def _selected(self, bar: QTabBar, index: int) -> None:
        if self._syncing or index < 0:
            return
        page = bar.tabData(index)
        if isinstance(page, int):
            self.select_page(page)

    def set_page(self, page: int) -> None:
        self._syncing = True
        try:
            for bar in self.bars:
                target = next(
                    (index for index in range(bar.count()) if bar.tabData(index) == page),
                    -1,
                )
                if target >= 0:
                    bar.setCurrentIndex(target)
        finally:
            self._syncing = False

    def refresh_language(self) -> None:
        for bar in self.bars:
            for index, (source, _page) in enumerate(self.entries):
                bar.setTabText(index, self.translator(source))
