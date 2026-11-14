# SPDX-License-Identifier: GPL-3.0-or-later
"""Width-aware profile columns and minimum-height summary grid."""
from PySide6.QtCore import QSize, QTimer, Qt
from PySide6.QtWidgets import QBoxLayout, QGridLayout, QSizePolicy, QWidget


class WorkspaceColumns(QWidget):
    def __init__(self, library, detail):
        super().__init__()
        self.library, self.detail = library, detail
        self.box = QBoxLayout(QBoxLayout.Direction.LeftToRight, self)
        self.box.setContentsMargins(0, 0, 0, 0); self.box.setSpacing(18)
        self.box.addWidget(library, 3); self.box.addWidget(detail, 7)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

    def minimumSizeHint(self):
        return QSize(0, self.box.minimumSize().height())

    def resizeEvent(self, event):
        narrow = self.width() < 950
        self.box.setDirection(QBoxLayout.Direction.TopToBottom if narrow else QBoxLayout.Direction.LeftToRight)
        self.library.setMaximumWidth(16777215 if narrow else 350)
        self.library.setMinimumWidth(0 if narrow else 260)
        self.box.setAlignment(self.library, Qt.AlignmentFlag.AlignTop)
        super().resizeEvent(event)


class SummaryGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.grid = QGridLayout(self); self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(12); self.tiles = []; self.columns = 0
        self.relayout_timer = QTimer(self); self.relayout_timer.setSingleShot(True)
        self.relayout_timer.timeout.connect(self.reflow)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

    def set_tiles(self, tiles):
        while self.grid.count(): self.grid.takeAt(0)
        for tile in self.tiles: tile.hide(); tile.deleteLater()
        self.tiles = tiles; self.columns = 0; self.reflow()

    def reflow(self):
        columns = 3 if self.width() >= 730 and len(self.tiles) >= 5 else 2 if self.width() >= 520 else 1
        if columns != self.columns:
            while self.grid.count(): self.grid.takeAt(0)
            for index, tile in enumerate(self.tiles):
                row, col, span = self.placement(index, columns)
                self.grid.addWidget(tile, row, col, 1, span); tile.show()
            for col in range(3): self.grid.setColumnStretch(col, 1 if col < columns else 0)
            self.columns = columns
        width = max(1, (self.width() - (columns-1)*self.grid.horizontalSpacing()) // columns)
        heights = {}
        for index, tile in enumerate(self.tiles):
            row, _col, span = self.placement(index, columns)
            tile_width = width * span + (span-1)*self.grid.horizontalSpacing()
            heights[row] = max(heights.get(row, 0), tile.minimumHeight(),
                               tile.minimumSizeHint().height(), tile.layout().totalHeightForWidth(tile_width))
        self.setMinimumHeight(sum(heights.values()) + max(0, len(heights)-1)*self.grid.verticalSpacing())
        self.updateGeometry()

    def placement(self, index, columns):
        if columns == 3 and len(self.tiles) == 5:
            if index == 3: return 1, 0, 2
            if index == 4: return 1, 2, 1
        return index // columns, index % columns, 1

    def resizeEvent(self, event):
        if not self.relayout_timer.isActive(): self.relayout_timer.start(0)
        super().resizeEvent(event)
