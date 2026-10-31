# SPDX-License-Identifier: GPL-3.0-or-later
"""One visual-only resize gesture; commit once on release, Escape cancels."""
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen
from rgb_devices import normalize_layout_scale


class ResizeInteraction:
    def init_resize(self):
        self.resize_slot_id = ""
        self.resize_scale = None
        self.resize_origin = None
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def resize_handle(self, slot):
        corner = self.slot_rect(slot).bottomRight()
        return QRectF(corner.x() - 7, corner.y() - 7, 14, 14)

    def draw_resize_handle(self, painter):
        slot = next((s for s in self.slots if (s.slot_id or s.position) == self.selected_slot_id), None)
        if slot is not None:
            painter.setPen(QPen(QColor("#e0f8ff"), 1))
            painter.setBrush(QColor("#2095bb"))
            painter.drawRoundedRect(self.resize_handle(slot).adjusted(2, 2, -2, -2), 2, 2)

    def begin_resize(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        slot = next((s for s in self.slots if (s.slot_id or s.position) == self.selected_slot_id), None)
        if slot is None or not self.resize_handle(slot).contains(event.position()):
            return False
        self.resize_slot_id = slot.slot_id or slot.position
        self.resize_scale = normalize_layout_scale(slot.scale)
        center = self.slot_rect(slot).center()
        self.resize_origin = (center, event.position() - center, self.resize_scale)
        self.drag_slot_id = self.drag_fan_slot_id = ""
        self.drag_position = None
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        event.accept()
        return True

    def update_resize(self, event):
        if not self.resize_slot_id:
            slot = next((s for s in self.slots if (s.slot_id or s.position) == self.selected_slot_id), None)
            self.setCursor(Qt.CursorShape.SizeFDiagCursor if slot and self.resize_handle(slot).contains(event.position())
                           else Qt.CursorShape.ArrowCursor)
            return False
        center, vector, initial = self.resize_origin
        delta = event.position() - center
        ratio = QPointF.dotProduct(delta, vector) / max(1, QPointF.dotProduct(vector, vector))
        self.resize_scale = normalize_layout_scale(initial * max(.01, ratio))
        self.update()
        event.accept()
        return True

    def finish_resize(self, event):
        if not self.resize_slot_id or event.button() != Qt.MouseButton.LeftButton:
            return False
        slot_id, scale = self.resize_slot_id, self.resize_scale
        self.cancel_resize()
        self.slot_resized.emit(slot_id, scale)
        event.accept()
        return True

    def cancel_resize(self):
        self.resize_slot_id = ""
        self.resize_scale = self.resize_origin = None
        self.unsetCursor()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.resize_slot_id:
            self.cancel_resize()
            event.accept()
        else:
            super().keyPressEvent(event)

    def hideEvent(self, event):
        self.cancel_resize()
        super().hideEvent(event)
