# SPDX-License-Identifier: GPL-3.0-or-later
"""Top-anchored topic library; every article remains in the existing help API."""
from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import (QAbstractItemView, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QTextBrowser, QTreeWidget, QVBoxLayout, QWidget)
from .topics import TopicDelegate
from .controller import populate


class HelpAppearance(QObject):
    """Coalesce theme/font changes; no polling or hardware lifecycle hooks."""
    def __init__(self, host, parent):
        super().__init__(parent); self.host = host
        self.timer = QTimer(self); self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.refresh)

    def eventFilter(self, watched, event):
        if event.type() in {QEvent.Type.PaletteChange, QEvent.Type.FontChange, QEvent.Type.StyleChange}:
            if not self.timer.isActive(): self.timer.start(0)
        return False

    def refresh(self):
        previous = self.host.help_browser.verticalScrollBar().value()
        populate(self.host)
        self.host.help_browser.verticalScrollBar().setValue(previous)


def build_page(host):
    page = QWidget(); root = QVBoxLayout(page)
    root.setContentsMargins(16, 14, 22, 22); root.setSpacing(14)
    root.addWidget(host.make_module_hero("?", "Hilfe & Anleitungen",
        "Schritt-für-Schritt-Anleitungen für die wichtigsten Bereiche. Über Links kannst du direkt zum passenden Bereich springen.", "Integriert"))
    host.help_search = QLineEdit(); host.help_search.setPlaceholderText("Hilfe durchsuchen …")
    host.help_search.setMinimumHeight(40)
    host.help_search.textChanged.connect(lambda *_args: populate(host))
    root.addWidget(host.help_search)
    body = QHBoxLayout(); body.setSpacing(16)
    library = QFrame(); library.setObjectName("dashboardSection")
    library.setMinimumWidth(260); library.setMaximumWidth(360)
    left = QVBoxLayout(library); left.setContentsMargins(12, 14, 12, 12); left.setSpacing(10)
    title = QLabel("Themen"); title.setObjectName("sectionTitle"); left.addWidget(title)
    tree = host.help_topic_tree = QTreeWidget()
    tree.setObjectName("helpTopicTree"); tree.setProperty("keepViewportHeight", True)
    tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    tree.setHeaderHidden(True); tree.setRootIsDecorated(False); tree.setIndentation(0)
    tree.setFrameShape(QFrame.Shape.NoFrame); tree.setMouseTracking(True)
    tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    tree.setAccessibleName("Anleitung auswählen")
    tree.setItemDelegate(TopicDelegate(tree)); left.addWidget(tree, 1)
    tree.currentItemChanged.connect(host.on_help_topic_selected)
    body.addWidget(library)
    article = QFrame(); article.setObjectName("dashboardSection")
    article_layout = QVBoxLayout(article); article_layout.setContentsMargins(8, 8, 8, 8)
    host.help_browser = QTextBrowser(); host.help_browser.setFrameShape(QFrame.Shape.NoFrame)
    host.help_browser.setOpenLinks(False); host.help_browser.setOpenExternalLinks(False)
    host.help_browser.document().setDocumentMargin(22)
    host.help_browser.anchorClicked.connect(host.on_help_link_clicked)
    article_layout.addWidget(host.help_browser)
    page.appearance = HelpAppearance(host, page)
    tree.installEventFilter(page.appearance)
    host.help_browser.installEventFilter(page.appearance)
    body.addWidget(article, 1); root.addLayout(body, 1)
    populate(host)
    return page
