#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Responsive Qt selector for bundled, attributed display-effect media."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .catalog import CATEGORY_LABELS, DESIGNS, EffectDesign, EffectVariant, designs_for_category, validated_asset
from modules.responsive_gallery.v1_0 import ViewportResizeRelay, reflow_grid, responsive_column_count


class StockEffectsLibrary(QGroupBox):
    """Expose category/colour selection without owning hardware or networking."""

    selection_changed = Signal()
    user_selected = Signal()
    selection_cleared = Signal()

    def __init__(self, translator: Callable[[str], str], parent=None) -> None:  # type: ignore[no-untyped-def]
        super().__init__(translator("Freie Designbibliothek"), parent)
        self.tr = translator
        self._design_cards: dict[str, QToolButton] = {}
        self._preview_cache: dict[Path, QPixmap] = {}
        self._columns = 1
        self._selection_active = False
        self._language_signature = translator('Originalquelle')
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.category_combo = QComboBox()
        self.category_combo.setProperty("i18nTranslateItems", False)
        for key, label in CATEGORY_LABELS:
            self.category_combo.addItem(translator(label), key)
        self.design_combo = QComboBox()
        self.design_combo.setProperty("i18nTranslateItems", False)
        self.design_combo.hide()
        self.variant_combo = QComboBox()
        self.variant_combo.setProperty("i18nTranslateItems", False)
        form.addRow(translator("Kategorie:"), self.category_combo)
        form.addRow(translator("Farbvariante:"), self.variant_combo)
        layout.addLayout(form)
        layout.addWidget(QLabel(translator("Hauptdesign:")))
        self.cards_widget = QWidget()
        self.cards_grid = QGridLayout(self.cards_widget)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setHorizontalSpacing(8)
        self.cards_grid.setVerticalSpacing(8)
        self.cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setObjectName("effectDesignCards")
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cards_scroll.setMinimumHeight(270)
        self.cards_scroll.setMaximumHeight(408)
        self.cards_scroll.setWidget(self.cards_widget)
        self._resize_relay = ViewportResizeRelay(self._relayout_cards, self)
        self.cards_scroll.viewport().installEventFilter(self._resize_relay)
        layout.addWidget(self.cards_scroll)
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setObjectName("muted")
        layout.addWidget(self.description_label)
        self.credit_label = QLabel()
        self.credit_label.setWordWrap(True)
        self.credit_label.setOpenExternalLinks(True)
        self.credit_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.credit_label)
        self.category_combo.currentIndexChanged.connect(self._category_changed)
        self.design_combo.currentIndexChanged.connect(self._design_changed)
        self.variant_combo.currentIndexChanged.connect(self._variant_changed)
        self._category_changed(0)

    def current_design(self) -> EffectDesign:
        ident = str(self.design_combo.currentData() or "")
        return next((item for item in DESIGNS if item.ident == ident), DESIGNS[0])

    def current_variant(self) -> EffectVariant:
        design = self.current_design()
        ident = str(self.variant_combo.currentData() or "")
        return next((item for item in design.variants if item.ident == ident), design.variants[0])

    def current_video(self):  # type: ignore[no-untyped-def]
        return validated_asset(self.current_variant())

    def current_preview(self) -> QPixmap:
        return self._preview_pixmap(validated_asset(self.current_variant(), preview=True))

    def _preview_pixmap(self, path: Path) -> QPixmap:
        clean = path.resolve()
        cached = self._preview_cache.get(clean)
        if cached is None:
            cached = QPixmap(str(clean))
            self._preview_cache[clean] = cached
        return cached

    def select_video(self, path: Path) -> bool:
        """Select the exact catalog variant for *path* without emitting a user change."""

        try:
            candidate = path.expanduser().resolve()
        except OSError:
            return False
        match = next(
            (
                (design, variant)
                for design in DESIGNS
                for variant in design.variants
                if variant.video_path.resolve() == candidate
            ),
            None,
        )
        if match is None:
            return False
        design, variant = match
        self._selection_active = True
        self.blockSignals(True)
        try:
            self.category_combo.blockSignals(True)
            self.category_combo.setCurrentIndex(
                max(0, self.category_combo.findData(design.category))
            )
            self.category_combo.blockSignals(False)
            self._category_changed(self.category_combo.currentIndex())
            self.design_combo.setCurrentIndex(
                max(0, self.design_combo.findData(design.ident))
            )
            self.variant_combo.setCurrentIndex(
                max(0, self.variant_combo.findData(variant.ident))
            )
        finally:
            self.blockSignals(False)
        self._selection_active = True
        self._sync_card_selection()
        return True

    @staticmethod
    def _clear_grid(grid: QGridLayout) -> None:
        while grid.count():
            item = grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _variant_for_design(self, design: EffectDesign) -> EffectVariant:
        selected = str(self.variant_combo.currentData() or "original")
        return next(
            (variant for variant in design.variants if variant.ident == selected),
            design.variants[0],
        )

    def _rebuild_design_cards(self) -> None:
        self._clear_grid(self.cards_grid)
        self._design_cards.clear()
        category = str(self.category_combo.currentData() or "all")
        self._columns = self._column_count()
        for position, design in enumerate(designs_for_category(category)):
            variant = self._variant_for_design(design)
            preview = self._preview_pixmap(validated_asset(variant, preview=True))
            button = QToolButton()
            button.setObjectName("effectDesignCard")
            button.setCheckable(True)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setIcon(QIcon(preview))
            button.setIconSize(QSize(164, 74))
            title = self.tr(design.title)
            button.setText(title)
            button.setToolTip(f"{title}\n{self.tr(design.description)}")
            button.setFixedSize(180, 112)
            button.setStyleSheet(
                "QToolButton { padding: 5px; border: 1px solid rgba(90,145,185,90); "
                "border-radius: 10px; background: rgba(7,20,32,170); } "
                "QToolButton:hover { border-color: #4dbdff; background: rgba(12,39,60,210); } "
                "QToolButton:checked { border: 2px solid #20aaff; "
                "background: rgba(13,66,99,220); }"
            )
            button.clicked.connect(
                lambda _checked=False, ident=design.ident: self._select_design_card(ident)
            )
            self.cards_grid.addWidget(
                button, position // self._columns, position % self._columns,
                Qt.AlignmentFlag.AlignHCenter,
            )
            self._design_cards[design.ident] = button
        for column in range(6):
            self.cards_grid.setColumnStretch(column, 1 if column < self._columns else 0)
        self._sync_card_selection()

    def _column_count(self) -> int:
        width = max(self.cards_scroll.viewport().width(), self.cards_scroll.width())
        return responsive_column_count(width, card_width=180, gap=8, maximum=6)

    def _relayout_cards(self) -> None:
        columns = self._column_count()
        if columns != self._columns:
            self._columns = columns
            reflow_grid(self.cards_grid, self._design_cards.values(), columns)

    def _select_design_card(self, ident: str) -> None:
        if self._selection_active and ident == self.design_combo.currentData():
            self.clear_selection()
            self.selection_cleared.emit()
            return
        self._selection_active = True
        target = self.design_combo.findData(ident)
        if target >= 0:
            self.design_combo.setCurrentIndex(target)
            self._sync_card_selection()
            self.user_selected.emit()

    def clear_selection(self):
        self._selection_active = False
        self._sync_card_selection()

    def _sync_card_selection(self) -> None:
        current = str(self.design_combo.currentData() or "")
        for ident, button in self._design_cards.items():
            button.setChecked(self._selection_active and ident == current)

    def _category_changed(self, _index: int) -> None:
        previous = str(self.design_combo.currentData() or "")
        category = str(self.category_combo.currentData() or "all")
        self.design_combo.blockSignals(True)
        self.design_combo.clear()
        for design in designs_for_category(category):
            self.design_combo.addItem(self.tr(design.title), design.ident)
        target = self.design_combo.findData(previous)
        if target < 0: self._selection_active = False
        self.design_combo.setCurrentIndex(max(0, target))
        self.design_combo.blockSignals(False)
        self._rebuild_design_cards()
        self._design_changed(self.design_combo.currentIndex())

    def _design_changed(self, _index: int) -> None:
        design = self.current_design()
        previous = str(self.variant_combo.currentData() or "original")
        self.variant_combo.blockSignals(True)
        self.variant_combo.clear()
        for variant in design.variants:
            self.variant_combo.addItem(self.tr(variant.label), variant.ident)
        target = self.variant_combo.findData(previous)
        self.variant_combo.setCurrentIndex(max(0, target))
        self.variant_combo.blockSignals(False)
        self.description_label.setText(self.tr(design.description))
        self.credit_label.setText(
            f'{escape(self.tr("Design von"))} '
            f'<a href="{escape(design.creator_url)}">{escape(design.creator)}</a><br>'
            f'<a href="{escape(design.source_url)}">{escape(self.tr("Originalquelle"))}</a> · '
            f'<a href="{escape(design.license_url)}">{escape(design.license_name)}</a>'
        )
        self._sync_card_selection()
        self.selection_changed.emit()

    def _variant_changed(self, _index: int) -> None:
        self._rebuild_design_cards()
        self.selection_changed.emit()
        if self._selection_active: self.user_selected.emit()

    def refresh_language(self):
        self.setTitle(self.tr('Freie Designbibliothek'))
        for index in range(self.category_combo.count()):
            key = self.category_combo.itemData(index)
            label = next(label for value, label in CATEGORY_LABELS if value == key)
            self.category_combo.setItemText(index, self.tr(label))
        for index in range(self.design_combo.count()):
            design = next(d for d in DESIGNS if d.ident == self.design_combo.itemData(index))
            self.design_combo.setItemText(index, self.tr(design.title))
        self.blockSignals(True)
        try: self._design_changed(self.design_combo.currentIndex())
        finally: self.blockSignals(False)
        signature = self.tr('Originalquelle')
        if self._language_signature != signature:
            self._language_signature = signature
            self._rebuild_design_cards()
