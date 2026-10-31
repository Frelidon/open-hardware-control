# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit per-header LED geometry, true physical test numbering and preview."""
from PySide6.QtCore import QEvent, QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget
from .led_topology import POINTS, path_points
from .led_topology_store import KEY, direction, paths, remember_path
import json

POINT_LABELS = {"left": "Links", "right": "Rechts", "top": "Oben", "bottom": "Unten",
                "top-left": "Oben links", "top-right": "Oben rechts", "bottom-left": "Unten links", "bottom-right": "Unten rechts"}
MOVEMENT_LABELS = {"local": "Wie bisher (pro Anschluss)", "left-right": "Links → rechts", "right-left": "Rechts → links",
                   "top-bottom": "Oben → unten", "bottom-top": "Unten → oben",
                   "top-left-bottom-right": "Oben links → unten rechts", "bottom-right-top-left": "Unten rechts → oben links",
                   "top-right-bottom-left": "Oben rechts → unten links", "bottom-left-top-right": "Unten links → oben rechts"}
UNIT_ORDER_LABELS = {False: "LED 1 am oberen/linken Lüfter", True: "LED 1 am unteren/rechten Lüfter"}


class _DraftPathGroup(QGroupBox):
    """Keep the optional commit flag without Qt's implicit draft-field lock."""
    def __init__(self, title, editor):
        super().__init__(title)
        self.editor = editor

    def childEvent(self, event):  # noqa: N802
        super().childEvent(event)
        # QGroupBox also disables newly polished children, after construction
        # and again when the form is first shown/reparented into the inspector.
        if event.polished() and getattr(self.editor, "_draft_controls_ready", False):
            self.editor.update_preview()

    def changeEvent(self, event):  # noqa: N802
        super().changeEvent(event)
        # Parent disable/enable also reapplies the unchecked group's lock.
        # Restore draft flags only after the real parent is enabled again.
        if (event.type() == QEvent.Type.EnabledChange and self.isEnabled()
                and getattr(self.editor, "_draft_controls_ready", False)):
            self.editor.update_preview()


class PathPreview(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setMinimumHeight(140)

    def paintEvent(self, _event):
        editor = self.editor
        # Combo boxes briefly expose a transitional selection while their
        # native popup closes. Validate and calculate before constructing a
        # native QPainter so that this state can never race widget teardown.
        try: points = path_points(editor.values(), editor.count.value(), editor.horizontal)
        except ValueError: return
        if not points: return
        painter = QPainter(self)
        if not painter.isActive(): return
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            area = self.rect().adjusted(24, 25, -24, -25)
            points = [QPointF(area.left() + x * area.width(), area.top() + y * area.height()) for x, y in points]
            painter.setPen(QPen(QColor("#378bd0"), 1))
            for a, b in zip(points, points[1:]): painter.drawLine(a, b)
            for i, point in enumerate(points):
                color = "#ff9d34" if i == editor.index.value() - 1 else "#29c99a" if i == 0 else "#378bd0"
                painter.setBrush(QColor(color)); painter.drawEllipse(point, 3, 3)
            painter.setPen(self.palette().windowText().color())
            painter.drawText(points[0] + QPointF(5, -7), "LED 1")
            if len(points) > 1: painter.drawText(points[-1] + QPointF(-50, 19), f"LED {len(points)}")
        finally:
            painter.end()


class LedTopologyEditor(QWidget):
    def __init__(self, host, source, name, count, index, units=1, *, fan_units=None):
        super().__init__(host)
        self.host, self.source, self.name, self.count, self.index = host, source, name, count, index
        self.stable_id = host.openrgb_stable_ids[source.index]
        self.horizontal = True
        if hasattr(host, "rgb_layout_slots"):
            from .led_topology_store import case_rectangles
            self.horizontal = case_rectangles(host, self.stable_id).get(name, (None, True))[1]
        tr = host.tr_static
        layout = QVBoxLayout(self)
        self._draft_controls_ready = False
        self.group = _DraftPathGroup(tr("LED-Verlauf"), self)
        self.group.setObjectName("ledPathEnabled")
        self.group.setCheckable(True)
        old = paths(host).get(self.stable_id, {}).get(name)
        self.group.setChecked(old is not None)
        layout.addWidget(self.group)
        form = QFormLayout(self.group)
        self.kind = QComboBox(); self.kind.setObjectName("ledPathKind")
        self.kind.addItem(tr("Reihe"), "line"); self.kind.addItem(tr("Ring"), "ring")
        self.start, self.end = QComboBox(), QComboBox()
        self.start.setObjectName("ledPathStart"); self.end.setObjectName("ledPathEnd")
        for key, caption in POINT_LABELS.items():
            self.start.addItem(tr(caption), key); self.end.addItem(tr(caption), key)
        self.units = QSpinBox(); self.units.setObjectName("ledPathUnits"); self.units.setRange(1, 64)
        self.clockwise = QComboBox(); self.clockwise.setObjectName("ledPathClockwise")
        self.clockwise.addItem(tr("Im Uhrzeigersinn"), True); self.clockwise.addItem(tr("Gegen den Uhrzeigersinn"), False)
        self.unit_order = QComboBox(); self.unit_order.setObjectName("ledPathUnitOrder")
        for key, caption in UNIT_ORDER_LABELS.items(): self.unit_order.addItem(tr(caption), key)
        value = dict(old) if old else dict(kind="line", start="left", end="right",
                                           units=max(1, min(64, units)), clockwise=True)
        # Fan count and physical LED layout are independent.  The case block
        # supplies the exact segmentation, but must never turn a user-selected
        # row into rings (or overwrite an explicitly saved ring layout).
        if (type(fan_units) is int and 1 <= fan_units <= 64
                and count.value() % fan_units == 0):
            value["units"] = fan_units
        self.unit_order.setCurrentIndex(self.unit_order.findData(value.get("reverse_units", False)))
        for combo, field in ((self.kind, "kind"), (self.start, "start"), (self.end, "end"), (self.clockwise, "clockwise")):
            combo.setCurrentIndex(max(0, combo.findData(value[field])))
        self.units.setValue(value["units"])
        form.addRow(tr("Anordnung"), self.kind)
        form.addRow(tr("LED 1 beginnt"), self.start)
        form.addRow(tr("Letzte LED endet"), self.end)
        form.addRow(tr("Anzahl Lüfter"), self.units)
        form.addRow(tr("Richtung"), self.clockwise)
        form.addRow(tr("Lüfterreihenfolge"), self.unit_order)
        self.reverse_effect = QPushButton()
        self.reverse_effect.setObjectName("ledPathReverseEffect")
        self.reverse_effect.setCheckable(True)
        self.reverse_effect.setChecked(value.get("reverse_effect", False))
        self.reverse_effect.toggled.connect(self._update_reverse_caption)
        self._update_reverse_caption(self.reverse_effect.isChecked())
        form.addRow(tr("Laufrichtung im Gehäuse"), self.reverse_effect)
        self.preview = PathPreview(self)
        form.addRow(self.preview)
        self.movement = QComboBox(); self.movement.setObjectName("ledCaseDirection")
        for key, caption in MOVEMENT_LABELS.items(): self.movement.addItem(tr(caption), key)
        self.movement.setCurrentIndex(max(0, self.movement.findData(value.get("direction", direction(host)))))
        layout.addWidget(QLabel(tr("Laufrichtung im Gehäuse")))
        layout.addWidget(self.movement)
        note = QLabel(tr("Positionen gelten im Komponentenblock. Der Sichttest nutzt die echte LED-Nummer. Räumliche Effekte brauchen einen gespeicherten LED-Verlauf."))
        note.setWordWrap(True); layout.addWidget(note)
        self.error = QLabel(); self.error.setWordWrap(True); layout.addWidget(self.error)
        for combo in (self.kind, self.start, self.end, self.clockwise, self.unit_order): combo.currentIndexChanged.connect(self.update_preview)
        for combo in (self.kind, self.start, self.end, self.clockwise, self.unit_order, self.movement):
            combo.activated.connect(self._activate_draft)
        for spin in (self.units, self.count, self.index): spin.valueChanged.connect(self.update_preview)
        self.units.valueChanged.connect(self._activate_draft)
        self.reverse_effect.clicked.connect(self._activate_draft)
        self.reverse_effect.toggled.connect(self.update_preview)
        self.movement.currentIndexChanged.connect(self.update_preview)
        self.group.toggled.connect(self.update_preview)
        self._draft_controls_ready = True
        self.update_preview()

    def values(self):
        value = dict(kind=self.kind.currentData(), start=self.start.currentData(), end=self.end.currentData(),
                     units=self.units.value(), clockwise=self.clockwise.currentData())
        if self.unit_order.currentData(): value["reverse_units"] = True
        if self.reverse_effect.isChecked(): value["reverse_effect"] = True
        return value

    def _update_reverse_caption(self, checked):
        self.reverse_effect.setText("↶  " + self.host.tr_static("Rückwärts") if checked
                                    else "↷  " + self.host.tr_static("Vorwärts"))

    def update_preview(self, _value=None):
        self.error.clear()
        ring = self.kind.currentData() == "ring"
        # A checkable QGroupBox otherwise disables every draft field when no
        # physical path has been saved yet. Keep editing independent from the
        # commit checkbox; only explicit user changes activate the new draft.
        for widget in (self.kind, self.start, self.reverse_effect, self.preview):
            widget.setEnabled(True)
        self.end.setEnabled(not ring); self.units.setEnabled(ring); self.clockwise.setEnabled(ring)
        self.unit_order.setEnabled(ring)
        self.preview.update()

    def _activate_draft(self, _value=None):
        self.group.setChecked(True)
        self.update_preview()

    def commit(self):
        if self.group.isChecked():
            if not remember_path(self.host, self.stable_id, self.name, self.values(), self.movement.currentData(), self.count.value()):
                self.error.setText(self.host.tr_static("LED-Verlauf ungültig: Start und Ende müssen verschieden sein; Ringe brauchen gleich viele LEDs."))
                return False
        else:
            raw = paths(self.host)
            raw.get(self.stable_id, {}).pop(self.name, None)
            self.host.settings.setValue(KEY, json.dumps(raw, ensure_ascii=False))
            self.host.settings.sync()
            self.host.rgb_last_effect_request_signature = None
        return True
