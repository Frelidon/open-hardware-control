# SPDX-License-Identifier: GPL-3.0-or-later
"""One movable parent with fixed paired-design/game/automation children."""
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtWidgets import QTreeWidgetItem

FIXED_CHILDREN = {"paired_designs", "games", "automations"}


def install(host):
    parent = host.navigation_items["design_hub"]
    parent.setData(0, Qt.ItemDataRole.UserRole, host.design_hub_page_index)
    for key, caption, page in (
        ("paired_designs", "Abgestimmte Designs", host.design_hub_page_index),
        ("games", "Spieleintegration", host.games_page_index),
        ("automations", "Automationszentrale", host.design_automation_page_index),
    ):
        item = host.navigation_items.get(key)
        if item is None:
            item = QTreeWidgetItem([host.tr_static(caption), ""])
            host.navigation_items[key] = item
        if item.parent() is not None:
            item.parent().removeChild(item)
        else:
            index = host.navigation.indexOfTopLevelItem(item)
            if index >= 0:
                host.navigation.takeTopLevelItem(index)
        item.setData(0, Qt.ItemDataRole.UserRole, page)
        item.setData(0, Qt.ItemDataRole.UserRole.value + 1, key)
        item.setData(0, Qt.ItemDataRole.UserRole.value + 2, caption)
        item.setFlags((item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                      & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsDropEnabled
                      & ~Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(1, Qt.ItemDataRole.CheckStateRole, None)
        parent.addChild(item)
    parent.setExpanded(False)


def sync(host, page):
    if not hasattr(host, "design_hub_page_index"):
        return False
    keys = {host.design_hub_page_index: "paired_designs", host.games_page_index: "games",
            host.design_automation_page_index: "automations"}
    parent = host.navigation_items["design_hub"]
    parent.setExpanded(page in keys)
    if page not in keys:
        return False
    with QSignalBlocker(host.navigation):
        host.navigation.setCurrentItem(host.navigation_items[keys[page]])
    return True
