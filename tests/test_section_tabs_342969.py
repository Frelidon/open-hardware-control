#!/usr/bin/env python3
"""Regression coverage for synchronized LCD in-page navigation."""

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.section_tabs.v1_0 import SectionTabsController  # noqa: E402


def test_section_tab_bars_share_pages_without_recursive_navigation() -> None:
    app = QApplication.instance() or QApplication([])
    selected: list[int] = []
    controller = SectionTabsController(
        (("Display & Layout", 3), ("Display-Effekte", 11)),
        selected.append,
        lambda text: text,
    )
    first = controller.create_bar()
    second = controller.create_bar()
    first.setCurrentIndex(1)
    assert selected == [11]
    controller.set_page(11)
    assert first.currentIndex() == second.currentIndex() == 1
    assert selected == [11]
    controller.set_page(3)
    assert first.currentIndex() == second.currentIndex() == 0
    app.processEvents()
