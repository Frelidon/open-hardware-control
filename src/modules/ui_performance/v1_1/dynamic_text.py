# SPDX-License-Identifier: GPL-3.0-or-later
"""Canonical text tracking for late-built cards and inline forms."""
from weakref import WeakKeyDictionary
from PySide6.QtWidgets import QAbstractButton, QComboBox, QGroupBox, QLabel, QLineEdit, QTabWidget
from localization_catalog import UI_TRANSLATIONS


def canonical(host, text):
    translations = UI_TRANSLATIONS.get(getattr(host, "ui_language", "de"), {})
    reverse = {translated: source for source, translated in translations.items()}
    if text in reverse: return reverse[text]
    if "\n" in text:
        title, subtitle = text.rsplit("\n", 1)
        return title + "\n" + reverse.get(subtitle, subtitle)
    if " · " in text:
        prefix, suffix = text.split(" · ", 1)
        return reverse.get(prefix, prefix) + " · " + suffix
    return text


def remember(host, widget, **fields):
    if not hasattr(host, "ui_language"): return
    if not hasattr(host, "dynamic_ui_texts"): host.dynamic_ui_texts = WeakKeyDictionary()
    host.dynamic_ui_texts[widget] = fields


def capture_form(host, root):
    from .adaptive_views import install_content_heights
    install_content_heights(root)
    for widget in [root, *root.findChildren(QLabel), *root.findChildren(QAbstractButton),
                   *root.findChildren(QComboBox), *root.findChildren(QGroupBox), *root.findChildren(QLineEdit),
                   *root.findChildren(QTabWidget)]:
        fields = {}
        if isinstance(widget, (QLabel, QAbstractButton)): fields["text"] = canonical(host, widget.text())
        if isinstance(widget, QGroupBox): fields["title"] = canonical(host, widget.title())
        if isinstance(widget, QLineEdit): fields["placeholder"] = canonical(host, widget.placeholderText())
        if isinstance(widget, QComboBox) and widget.property("i18nTranslateItems") is not False:
            fields["items"] = [canonical(host, widget.itemText(i)) for i in range(widget.count())]
        if isinstance(widget, QTabWidget) and widget.count():
            fields["tabs"] = [canonical(host, widget.tabText(i)) for i in range(widget.count())]
        if widget.toolTip(): fields["tooltip"] = canonical(host, widget.toolTip())
        if fields: remember(host, widget, **fields)


def refresh(host):
    from shiboken6 import isValid
    for widget, fields in tuple(getattr(host, "dynamic_ui_texts", {}).items()):
        if not isValid(widget):
            host.dynamic_ui_texts.pop(widget, None)
            continue
        for field, source in fields.items():
            if field == "items":
                for index, caption in enumerate(source):
                    if index < widget.count(): widget.setItemText(index, host.tr_static(caption))
            elif field == "tabs":
                for index, caption in enumerate(source):
                    if index < widget.count(): widget.setTabText(index, host.tr_static(caption))
            elif field == "text":
                translated = host.tr_static(source)
                if " · " in source and translated == source:
                    prefix, suffix = source.split(" · ", 1)
                    translated = host.tr_static(prefix) + " · " + suffix
                widget.setText(translated)
            elif field == "title": widget.setTitle(host.tr_static(source))
            elif field == "placeholder": widget.setPlaceholderText(host.tr_static(source))
            elif field == "tooltip": widget.setToolTip(host.tr_static(source))
