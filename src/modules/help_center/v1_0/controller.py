# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only help filtering and formatting; stable IDs are never translated."""
from html import escape
from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QTreeWidgetItem
from modules.navigation_settings.v1_0.artwork import category_icon
from .topics import INTRO_ROLE, TOPIC_ICONS


def populate(host):
    if not hasattr(host, "help_topic_tree"): return
    tree = host.help_topic_tree
    query = host.help_search.text().strip().casefold()
    current = tree.currentItem()
    selected_id = current.data(0, Qt.ItemDataRole.UserRole) if current else ""
    first = selected = None
    with QSignalBlocker(tree):
        tree.clear()
        for ident, topic in host.help_topics_for_language().items():
            title, intro = str(topic.get("title", ident)), str(topic.get("intro", ""))
            haystack = " ".join((title, intro, *map(str, topic.get("steps", ())))).casefold()
            if query and query not in haystack: continue
            item = QTreeWidgetItem([title]); item.setData(0, Qt.ItemDataRole.UserRole, ident)
            item.setData(0, INTRO_ROLE, intro); item.setToolTip(0, intro)
            item.setIcon(0, category_icon(TOPIC_ICONS.get(ident, "help"), tree.palette(), 26))
            tree.addTopLevelItem(item)
            if first is None: first = item
            if ident == selected_id: selected = item
        target = selected or first
        tree.setCurrentItem(target)
    tree.doItemsLayout()
    if target is not None:
        show_topic(host, str(target.data(0, Qt.ItemDataRole.UserRole)))
    else:
        host.help_browser.setHtml(f"<h2>{escape(host.tr_static('Keine passende Anleitung gefunden.'))}</h2>")


def show_topic(host, ident):
    if not hasattr(host, "help_browser"): return
    topics = host.help_topics_for_language()
    topic = topics.get(ident, topics.get("getting_started", {}))
    title, intro = escape(str(topic.get("title", "Hilfe"))), escape(str(topic.get("intro", "")))
    palette = host.help_browser.palette()
    accent = palette.color(QPalette.ColorRole.Highlight).name()
    text = palette.color(QPalette.ColorRole.Text).name()
    muted = palette.color(QPalette.ColorRole.PlaceholderText).name()
    rows = "".join(
        f'<tr><td width="38" valign="top" style="color:{accent};font-weight:700">{index:02}</td>'
        f'<td style="padding-bottom:18px">{escape(str(step))}</td></tr>'
        for index, step in enumerate(topic.get("steps", ()), 1)
    )
    action = ""
    if isinstance(topic.get("page"), int):
        action = (f'<p><a href="ohc://page/{topic["page"]}" style="color:{accent}"><b>'
                  f'→ {escape(host.tr_static("Passenden Bereich öffnen"))}</b></a></p>')
    host.help_browser.setHtml(
        f'<body style="color:{text};font-size:14px"><h1 style="font-size:25px">{title}</h1>'
        f'<p style="color:{muted};line-height:150%">{intro}</p>'
        f'<h3>{escape(host.tr_static("Schritt für Schritt"))}</h3>'
        f'<table cellspacing="0" cellpadding="7" width="100%">{rows}</table>{action}'
        f'<p style="color:{muted};font-size:11px">{escape(host.tr_static("Open Hardware Control · integrierte Hilfe"))}</p></body>'
    )
    host.help_browser.verticalScrollBar().setValue(0)


def open_help(host, ident="getting_started"):
    if hasattr(host, "help_page_index"): host.tabs.setCurrentIndex(host.help_page_index)
    # A requested deep link must also be discoverable when a previous search
    # filtered its topic out. Clearing search changes no user settings.
    if host.help_search.text(): host.help_search.clear()
    tree = host.help_topic_tree
    for index in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(index)
        if item.data(0, Qt.ItemDataRole.UserRole) == ident:
            tree.setCurrentItem(item); tree.scrollToItem(item); break
    show_topic(host, ident)
