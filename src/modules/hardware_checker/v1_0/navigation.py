# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware section subnavigation, sharing the existing diagnostic pages."""
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtWidgets import QTreeWidgetItem

CHILDREN=(("hardware_fix","Hardware Fix",1),("supported_devices","Von OHC unterstützte Geräte",2))


def install(host):
    parent=host.navigation_items["hardware_checker"]
    for key,caption,section in CHILDREN:
        item=QTreeWidgetItem([host.tr_static(caption),""])
        item.setData(0,Qt.ItemDataRole.UserRole,host.hardware_checker_page_index)
        item.setData(0,Qt.ItemDataRole.UserRole.value+1,key)
        item.setData(0,Qt.ItemDataRole.UserRole.value+2,caption)
        item.setFlags((item.flags()|Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled)
                      &~Qt.ItemFlag.ItemIsDragEnabled&~Qt.ItemFlag.ItemIsDropEnabled)
        parent.addChild(item);host.navigation_items[key]=item
    parent.setExpanded(False)
    host.hardware_checker_page.section_tabs.tabBar().hide()
    host.hardware_checker_page.section_tabs.currentChanged.connect(lambda _i: sync(host))


def select(host,item):
    if not hasattr(host,"hardware_checker_page"):return
    parent=host.navigation_items["hardware_checker"]
    inside=item is parent or item.parent() is parent
    parent.setExpanded(inside)
    if inside:
        key=host.navigation_item_key(item)
        index=next((section for child,_caption,section in CHILDREN if child==key),0)
        with QSignalBlocker(host.hardware_checker_page.section_tabs):
            host.hardware_checker_page.section_tabs.setCurrentIndex(index)
        host.hardware_checker_page._section_geometry(index)
        host.update_page_header(host.hardware_checker_page_index)


def sync(host):
    if not hasattr(host,"hardware_checker_page") or host.tabs.currentIndex()!=host.hardware_checker_page_index:
        return
    index=host.hardware_checker_page.section_tabs.currentIndex()
    key=next((child for child,_caption,section in CHILDREN if section==index),"hardware_checker")
    with QSignalBlocker(host.navigation):host.navigation.setCurrentItem(host.navigation_items[key])
    host.navigation_items["hardware_checker"].setExpanded(True)
    host.update_page_header(host.hardware_checker_page_index)
