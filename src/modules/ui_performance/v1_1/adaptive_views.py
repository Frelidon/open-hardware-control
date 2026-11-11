# SPDX-License-Identifier: GPL-3.0-or-later
"""Event-driven list sizing, bounded by rows, without polling or rebuilding."""
from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QListView, QTreeView, QTableView, QSizePolicy
from shiboken6 import isValid


class ContentHeight(QObject):
    def __init__(self, view, maximum=340):
        super().__init__(view)
        self.view, self.maximum = view, maximum
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fit)
        view.installEventFilter(self)
        model = view.model()
        if model is not None:
            for signal in (model.rowsInserted, model.rowsRemoved, model.modelReset,
                           model.layoutChanged, model.dataChanged):
                signal.connect(self.queue)
        if isinstance(view, QTreeView):
            view.expanded.connect(self.queue)
            view.collapsed.connect(self.queue)
        self.queue()

    def queue(self, *_args):
        if not self.timer.isActive():
            self.timer.start(0)

    def eventFilter(self, watched, event):
        if event.type() in {QEvent.Type.Show, QEvent.Type.FontChange,
                            QEvent.Type.StyleChange, QEvent.Type.LayoutRequest}:
            self.queue()
        return False

    def fit(self):
        view = self.view
        if not isValid(view) or view.property("keepViewportHeight"):
            return
        model = view.model()
        if model is None:
            return
        font_row = view.fontMetrics().height() + 16
        header = 0
        if isinstance(view, QTableView):
            header = view.horizontalHeader().sizeHint().height() if not view.horizontalHeader().isHidden() else 0
        elif isinstance(view, QTreeView):
            header = view.header().sizeHint().height() if not view.isHeaderHidden() else 0
        height = header + 2 * view.frameWidth() + 4
        count = model.rowCount(view.rootIndex())
        if isinstance(view, QTreeView) and count:
            index = model.index(0, 0, view.rootIndex())
            visited = 0
            while index.isValid() and height < self.maximum and visited < 24:
                height += max(font_row, view.sizeHintForIndex(index).height())
                index = view.indexBelow(index)
                visited += 1
        else:
            for row in range(min(count, 24)):
                height += max(font_row, view.sizeHintForRow(row))
                if height >= self.maximum:
                    break
        if count == 0:
            height += font_row
        if view.horizontalScrollBar().isVisible():
            height += view.horizontalScrollBar().sizeHint().height()
        height = min(self.maximum, height)
        if view.minimumHeight() != height or view.maximumHeight() != height:
            view.setFixedHeight(height)
            view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


def install_content_heights(root):
    """Attach once to lists/tables, excluding navigation and combo popups."""
    for view in root.findChildren(QAbstractItemView):
        if not isinstance(view, (QListView, QTreeView, QTableView)):
            continue
        if view.objectName() in {"hardwareNavigation", "helpTopicTree"} or view.property("keepViewportHeight"):
            continue
        parent = view.parentWidget()
        popup = False
        while parent is not None and parent is not root:
            if isinstance(parent, QComboBox):
                popup = True
                break
            parent = parent.parentWidget()
        if popup or hasattr(view, "_ohc_content_height"):
            continue
        view._ohc_content_height = ContentHeight(view)
