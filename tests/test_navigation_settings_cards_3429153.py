#!/usr/bin/env python3
"""Regression: module visibility uses live status cards, not a plain checkbox grid."""

from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QWidget  # noqa: E402
from modules.navigation_settings.v1_0.panel import (  # noqa: E402
    MODULE_ROWS,
    build_module_visibility_settings,
)


class Host(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.navigation_user_hidden = {"about"}
        self.changes: list[tuple[str, bool]] = []

    @staticmethod
    def tr_static(text: str) -> str:
        return text

    def set_navigation_module_enabled(self, key: str, enabled: bool) -> None:
        self.changes.append((key, enabled))
        if enabled:
            self.navigation_user_hidden.discard(key)
        else:
            self.navigation_user_hidden.add(key)

    def show_all_navigation_modules(self) -> None:
        self.navigation_user_hidden.clear()


def test_module_visibility_cards_with_real_qt() -> None:
    app = QApplication.instance() or QApplication([])
    host = Host()
    panel = build_module_visibility_settings(host)
    panel.show()
    app.processEvents()

    cards = panel.findChildren(QFrame, "moduleVisibilityCard")
    assert len(cards) == len(MODULE_ROWS) == 17
    assert len(host.navigation_module_checkboxes) == 17
    assert len(host.navigation_module_status_dots) == 17
    lifecycle_badges = panel.findChildren(QLabel, "featureLifecycleBadge")
    assert len(lifecycle_badges) == 17
    assert any(label.text() == "Release Candidate · v0.9.0-rc1" for label in lifecycle_badges)
    assert not host.navigation_module_checkboxes["about"].isChecked()
    assert host.navigation_module_status_dots["about"].objectName() == "moduleVisibilityDotOff"

    host.navigation_module_checkboxes["about"].setChecked(True)
    app.processEvents()
    assert host.changes[-1] == ("about", True)
    assert host.navigation_module_status_dots["about"].objectName() == "moduleVisibilityDotOn"

    host.navigation_module_checkboxes["automations"].setChecked(False)
    app.processEvents()
    assert host.changes[-1] == ("automations", False)
    assert host.navigation_module_status_dots["automations"].objectName() == "moduleVisibilityDotOff"
    assert "automations" in host.navigation_user_hidden


if __name__ == "__main__":
    test_module_visibility_cards_with_real_qt()
    print("Module visibility cards, status dots, and switches stay synchronized.")
