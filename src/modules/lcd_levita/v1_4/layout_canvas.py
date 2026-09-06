#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qt canvas for draggable Levita layer-2 blocks."""

from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QSizePolicy,
    QWidget,
)

from thermalright_display import (
    DEFAULT_BACKGROUND_OFFSET_X,
    DEFAULT_BACKGROUND_OFFSET_Y,
    DEFAULT_NOTCH_MASK_WIDTH,
    DEFAULT_OVERLAYS,
    LEVITA_CUTOUT_HEIGHT,
    LEVITA_CUTOUT_WIDTH,
    LEVITA_CUTOUT_Y,
    LEVITA_HEIGHT,
    LEVITA_WIDTH,
    OverlaySpec,
    bounded_notch_width,
    clamp_overlay_outside_cutout,
    notch_safe_right_x,
)

from .layout_model import EditableLayout, LayoutBlock
from .panel_geometry import (
    DEFAULT_INNER_CORNER_RADIUS,
    DEFAULT_OUTER_CORNER_RADIUS,
    bounded_inner_corner_radius,
)


def outer_right_corner_wedges() -> QPainterPath:
    """Cover only the two outer-right display corners in preview coordinates."""

    radius = float(DEFAULT_OUTER_CORNER_RADIUS)
    path = QPainterPath()
    top = QPainterPath()
    top.addRect(LEVITA_WIDTH - radius, 0.0, radius, radius)
    top_circle = QPainterPath()
    top_circle.addEllipse(LEVITA_WIDTH - 2 * radius, 0.0, 2 * radius, 2 * radius)
    path.addPath(top.subtracted(top_circle))
    bottom = QPainterPath()
    bottom.addRect(LEVITA_WIDTH - radius, LEVITA_HEIGHT - radius, radius, radius)
    bottom_circle = QPainterPath()
    bottom_circle.addEllipse(
        LEVITA_WIDTH - 2 * radius, LEVITA_HEIGHT - 2 * radius, 2 * radius, 2 * radius,
    )
    path.addPath(bottom.subtracted(bottom_circle))
    return path


MODULE_VERSION = "1.4"


class _MovableOverlayItem(QGraphicsSimpleTextItem):
    """Existing OHC overlay item; coordinates are stored at its visual centre."""

    def __init__(
        self,
        spec: OverlaySpec,
        move_started: Callable[[], None],
        moved: Callable[[str, int, int], None],
        safe_right_x: int,
    ) -> None:
        super().__init__(spec.sample or spec.label)
        self.ident = spec.ident
        self._move_started = move_started
        self._moved = moved
        self._safe_right_x = safe_right_x
        font = QFont()
        font.setPixelSize(spec.size)
        font.setBold(spec.bold)
        self.setFont(font)
        self.setBrush(QColor(spec.color))
        self.setPen(QPen(QColor(0, 0, 0, 210), max(1, spec.size // 18)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        rect = self.boundingRect()
        self.setPos(spec.x - rect.width() / 2, spec.y - rect.height() / 2)
        self.setToolTip(f"{spec.label} · mit der Maus verschieben")
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: object) -> object:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and isinstance(value, QPointF):
            rect = self.boundingRect()
            x = max(0.0, min(float(self._safe_right_x) - rect.width() - 8.0, value.x()))
            y = max(0.0, min(float(LEVITA_HEIGHT) - rect.height(), value.y()))
            return QPointF(x, y)
        return super().itemChange(change, value)

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._move_started()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().mouseReleaseEvent(event)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        rect = self.boundingRect()
        self._moved(
            self.ident,
            round(self.pos().x() + rect.width() / 2),
            round(self.pos().y() + rect.height() / 2),
        )


class _MovableLayoutBlockItem(QGraphicsSimpleTextItem):
    """One imported live-value block; its label and value move together."""

    def __init__(
        self,
        block: LayoutBlock,
        offset: tuple[int, int],
        safe_right_x: int,
        move_started: Callable[[], None],
        moved: Callable[[str, int, int], None],
        edit_requested: Callable[[LayoutBlock], None],
    ) -> None:
        super().__init__(block.preview_text)
        self.block = block
        self._offset = offset
        self._safe_right_x = safe_right_x
        self._move_started = move_started
        self._moved = moved
        self._edit_requested = edit_requested
        font = QFont(block.font) if block.font else QFont()
        font.setPixelSize(block.size)
        font.setBold(block.bold)
        font.setItalic(block.italic)
        self.setFont(font)
        self.setBrush(QColor(block.color))
        self.setPen(QPen(QColor(0, 0, 0, 205), max(1, block.size // 18)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        rect = self.boundingRect()
        self.setPos(
            block.x + offset[0] - rect.width() / 2,
            block.y + offset[1] - rect.height() / 2,
        )
        self.setZValue(12)
        self.setToolTip(f"{block.label} · ziehen · Rechtsklick zum Anpassen")
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: object) -> object:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and isinstance(value, QPointF):
            rect = self.boundingRect()
            x = max(0.0, min(float(self._safe_right_x) - rect.width() - 8.0, value.x()))
            y = max(0.0, min(float(LEVITA_HEIGHT) - rect.height(), value.y()))
            return QPointF(x, y)
        return super().itemChange(change, value)

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.button() == Qt.MouseButton.LeftButton:
            self._move_started()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().mouseReleaseEvent(event)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        if event.button() == Qt.MouseButton.LeftButton:
            rect = self.boundingRect()
            self._moved(
                self.block.ident,
                round(self.pos().x() + rect.width() / 2 - self._offset[0]),
                round(self.pos().y() + rect.height() / 2 - self._offset[1]),
            )

    def contextMenuEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._edit_requested(self.block)
        event.accept()


class _MovableNotchItem(QGraphicsPathItem):
    """Right bar with draggable width and rounded inner image corners."""

    def __init__(
        self,
        width: int,
        top_radius: int,
        bottom_radius: int,
        resized: Callable[[int], None],
    ) -> None:
        bounded = bounded_notch_width(width)
        super().__init__()
        self._width = bounded
        self._top_radius = bounded_inner_corner_radius(top_radius)
        self._bottom_radius = bounded_inner_corner_radius(bottom_radius)
        self._resized = resized
        self._update_path()
        self.setPos(LEVITA_WIDTH - bounded, 0)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setCursor(Qt.CursorShape.SizeHorCursor)

    def _update_path(self) -> None:
        width = float(self._width)
        height = float(LEVITA_HEIGHT)
        top = float(self._top_radius)
        bottom = float(self._bottom_radius)
        outer = min(float(DEFAULT_OUTER_CORNER_RADIUS), width / 2)
        path = QPainterPath()
        path.moveTo(-top, 0.0)
        if top:
            path.quadTo(0.0, 0.0, 0.0, top)
        path.lineTo(0.0, height - bottom)
        if bottom:
            path.quadTo(0.0, height, -bottom, height)
        path.lineTo(width - outer, height)
        path.quadTo(width, height, width, height - outer)
        path.lineTo(width, outer)
        path.quadTo(width, 0.0, width - outer, 0.0)
        path.closeSubpath()
        self.setPath(path)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: object) -> object:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and isinstance(value, QPointF):
            x = max(float(LEVITA_WIDTH - 800), min(float(LEVITA_WIDTH - LEVITA_CUTOUT_WIDTH), value.x()))
            self._width = bounded_notch_width(round(LEVITA_WIDTH - x))
            self._update_path()
            return QPointF(x, 0)
        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().mouseReleaseEvent(event)
        self._resized(bounded_notch_width(LEVITA_WIDTH - round(self.pos().x())))

class ThermalrightCanvas(QGraphicsView):
    """1600x720 Levita surface with editable OHC and imported data blocks."""

    def __init__(
        self,
        moved: Callable[[str, int, int], None],
        move_started: Callable[[], None],
        notch_resized: Callable[[int], None],
        *,
        layout_moved: Callable[[str, int, int], None] | None = None,
        layout_edit_requested: Callable[[LayoutBlock], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(0, 0, LEVITA_WIDTH, LEVITA_HEIGHT, self)
        self.setScene(self._scene)
        self._moved = moved
        self._move_started = move_started
        self._notch_resized = notch_resized
        self._layout_moved = layout_moved or (lambda _ident, _x, _y: None)
        self._layout_edit_requested = layout_edit_requested or (lambda _block: None)
        self._background = QPixmap()
        self._background_item: QGraphicsPixmapItem | None = None
        self._hardware_layer = QPixmap()
        self._specs: tuple[OverlaySpec, ...] = tuple(DEFAULT_OVERLAYS)
        self._layout: EditableLayout | None = None
        self._split_mode = 0
        self._background_x = DEFAULT_BACKGROUND_OFFSET_X
        self._background_y = DEFAULT_BACKGROUND_OFFSET_Y
        self._notch_visible = True
        self._notch_width = DEFAULT_NOTCH_MASK_WIDTH
        self._notch_top_radius = DEFAULT_INNER_CORNER_RADIUS
        self._notch_bottom_radius = DEFAULT_INNER_CORNER_RADIUS
        self._layer1_intensity = 100
        self._layer2_intensity = 100
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setBackgroundBrush(QColor("#07111d"))
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumSize(680, 306)
        self.setMaximumSize(960, 432)
        policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        self.setStyleSheet(
            "ThermalrightCanvas { background: #07111d; border: 2px solid #278bc4; border-radius: 12px; }"
        )
        # The canvas edits individual blocks only.  Rubber-band selection can
        # steal the first movement from large clock items, especially after a
        # rebuild, so background dragging is deliberately disabled.
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setToolTip("Datenblöcke ziehen; Rechtsklick ändert Text, Farbe und Schriftgröße")
        self.rebuild()

    def sizeHint(self) -> QSize:
        return QSize(880, 396)

    def minimumSizeHint(self) -> QSize:
        return QSize(680, 306)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return max(1, round(int(width) * LEVITA_HEIGHT / LEVITA_WIDTH))

    def set_background(self, pixmap: QPixmap) -> None:
        had_background = not self._background.isNull()
        self._background = pixmap
        if had_background and not pixmap.isNull() and self._background_item is not None:
            # Video preview frames must not clear/recreate draggable blocks.
            # Replacing only the pixmap keeps an active drag gesture intact.
            self._background_item.setPixmap(pixmap)
            self._background_item.setPos(self._background_x, self._background_y)
            return
        self.rebuild()

    def has_background(self) -> bool:
        return not self._background.isNull()

    def set_hardware_layer(self, pixmap: QPixmap) -> None:
        if pixmap.cacheKey() == self._hardware_layer.cacheKey():
            return
        self._hardware_layer = pixmap
        self.rebuild()

    def set_specs(self, specs: Iterable[OverlaySpec]) -> None:
        values = tuple(specs)
        if values == self._specs:
            return
        self._specs = values
        self.rebuild()

    def set_editable_layout(self, layout: EditableLayout | None) -> None:
        if layout == self._layout:
            return
        self._layout = layout
        self.rebuild()

    def set_background_offset(self, x: int, y: int) -> None:
        self._background_x = max(-600, min(600, int(x)))
        self._background_y = max(-300, min(300, int(y)))
        if self._background_item is not None:
            self._background_item.setPos(self._background_x, self._background_y)

    def set_notch_mask(
        self,
        visible: bool,
        width: int,
        top_radius: int = DEFAULT_INNER_CORNER_RADIUS,
        bottom_radius: int = DEFAULT_INNER_CORNER_RADIUS,
    ) -> None:
        new_visible = bool(visible)
        new_width = bounded_notch_width(width)
        new_top = bounded_inner_corner_radius(top_radius)
        new_bottom = bounded_inner_corner_radius(bottom_radius)
        if (
            new_visible == self._notch_visible
            and new_width == self._notch_width
            and new_top == self._notch_top_radius
            and new_bottom == self._notch_bottom_radius
        ):
            return
        self._notch_visible = new_visible
        self._notch_width = new_width
        self._notch_top_radius = new_top
        self._notch_bottom_radius = new_bottom
        self.rebuild()

    def set_split_mode(self, mode: int) -> None:
        value = max(0, min(3, int(mode)))
        if value == self._split_mode:
            return
        self._split_mode = value
        self.rebuild()

    def set_layer_intensities(self, layer1: int, layer2: int) -> None:
        first = max(25, min(150, int(layer1)))
        second = max(25, min(150, int(layer2)))
        if (first, second) == (self._layer1_intensity, self._layer2_intensity):
            return
        self._layer1_intensity, self._layer2_intensity = first, second
        self.rebuild()

    def rebuild(self) -> None:
        self._background_item = None
        self._scene.clear()
        if self._background.isNull():
            background = QGraphicsRectItem(0, 0, LEVITA_WIDTH, LEVITA_HEIGHT)
            background.setBrush(QColor("#07111d"))
            background.setPen(QPen(QColor("#315a78"), 3))
            background.setZValue(-20)
            self._scene.addItem(background)
            placeholder = self._scene.addSimpleText("Lokales Bild, Video oder TRCC-Layout auswählen")
            placeholder.setBrush(QColor("#8ba2b5"))
            font = QFont()
            font.setPixelSize(42)
            placeholder.setFont(font)
            placeholder.setPos(LEVITA_WIDTH / 2 - placeholder.boundingRect().width() / 2, 270)
        else:
            item = self._scene.addPixmap(self._background)
            item.setPos(self._background_x, self._background_y)
            item.setZValue(-20)
            item.setOpacity(min(1.0, self._layer1_intensity / 100.0))
            self._background_item = item

        if not self._hardware_layer.isNull():
            hardware_layer = self._scene.addPixmap(self._hardware_layer)
            hardware_layer.setZValue(-10)
            hardware_layer.setOpacity(min(1.0, self._layer2_intensity / 100.0))

        if self._split_mode:
            guide_width = {1: 360, 2: 480, 3: 620}.get(self._split_mode, 480)
            guide = QGraphicsRectItem((LEVITA_WIDTH - guide_width) / 2, 18, guide_width, 76)
            guide.setBrush(QColor(0, 200, 255, 34))
            guide.setPen(QPen(QColor(0, 200, 255, 170), 3, Qt.PenStyle.DashLine))
            guide.setZValue(5)
            self._scene.addItem(guide)

        safe_right_x = notch_safe_right_x(self._notch_width, visible=self._notch_visible)
        if self._layout is not None:
            offset = (self._layout.offset_x, self._layout.offset_y)
            for block in self._layout.blocks:
                self._scene.addItem(_MovableLayoutBlockItem(
                    block, offset, safe_right_x, self._move_started,
                    self._layout_moved, self._layout_edit_requested,
                ))
        else:
            for spec in self._specs:
                if spec.visible:
                    safe = clamp_overlay_outside_cutout(spec, safe_right_x=safe_right_x)
                    self._scene.addItem(_MovableOverlayItem(
                        safe, self._move_started, self._moved, safe_right_x,
                    ))

        cutout_width = self._notch_width if self._notch_visible else LEVITA_CUTOUT_WIDTH
        cutout = _MovableNotchItem(
            cutout_width,
            self._notch_top_radius,
            self._notch_bottom_radius,
            self._notch_resized,
        )
        cutout.setPos(LEVITA_WIDTH - cutout_width, LEVITA_CUTOUT_Y)
        cutout.setEnabled(self._notch_visible)
        cutout.setBrush(QColor(0, 0, 0, 235))
        cutout.setPen(QPen(QColor("#00c8ff" if self._notch_visible else "#ff526f"), 4))
        cutout.setZValue(30)
        cutout.setToolTip(f"Schwarzer Kamera-/Notch-Balken · {cutout_width} px")
        self._scene.addItem(cutout)
        cutout_label = self._scene.addSimpleText(f"NOTCH · {cutout_width} px")
        cutout_label.setBrush(QColor("#00c8ff" if self._notch_visible else "#ff526f"))
        cutout_label.setRotation(-90)
        cutout_label.setPos(LEVITA_WIDTH - cutout_width / 2 + 12, 430)
        cutout_label.setZValue(31)
        cover = QGraphicsPathItem(outer_right_corner_wedges())
        cover.setBrush(QColor("#07111d"))
        cover.setPen(QPen(Qt.PenStyle.NoPen))
        cover.setZValue(80)
        cover.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._scene.addItem(cover)
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
