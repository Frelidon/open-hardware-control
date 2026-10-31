#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""User-declared component distances for the case view; settings only."""

from __future__ import annotations

import json
import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QSpinBox, QVBoxLayout,
)
from modules.rgb_studio.v1_15.led_topology_store import direction, paths, set_case_direction

DISTANCES_KEY = "case_workspace/distances_v1"
UNIT_KEY = "case_workspace/distance_unit"
VALID_UNITS = {"mm", "in"}
VALID_KINDS = {"distance", "depth"}
MM_PER_INCH = 25.4


def normalize_unit(value: object) -> str:
    return str(value) if str(value) in VALID_UNITS else "mm"


def display_distance(millimeters: float, unit: object) -> float:
    value = max(0.0, float(millimeters))
    return value / MM_PER_INCH if normalize_unit(unit) == "in" else value


def millimeters(value: float, unit: object) -> float:
    number = max(0.0, float(value))
    return number * MM_PER_INCH if normalize_unit(unit) == "in" else number


def normalize_links(raw: object, valid_ids: set[str] | None = None) -> list[dict[str, object]]:
    if not isinstance(raw, list):
        return []
    result: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in raw[:128]:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source", ""))[:96]
        target = str(item.get("target", ""))[:96]
        kind = str(item.get("kind", "distance"))
        try:
            distance_mm = float(item.get("distance_mm", 0.0))
        except (TypeError, ValueError):
            continue
        key = (source, target, kind)
        if (not source or not target or source == target or kind not in VALID_KINDS
                or key in seen or not math.isfinite(distance_mm)
                or not 1.0 <= distance_mm <= 5000.0):
            continue
        if valid_ids is not None and (source not in valid_ids or target not in valid_ids):
            continue
        seen.add(key)
        result.append({
            "source": source,
            "target": target,
            "kind": kind,
            "distance_mm": round(distance_mm, 3),
        })
    return result


def read_links(settings: object, valid_ids: set[str] | None = None) -> list[dict[str, object]]:
    try:
        raw = json.loads(str(settings.value(DISTANCES_KEY, "[]") or "[]"))
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError):
        return []
    return normalize_links(raw, valid_ids)


def write_links(settings: object, links: list[dict[str, object]]) -> None:
    settings.setValue(
        DISTANCES_KEY,
        json.dumps(normalize_links(links), ensure_ascii=False, separators=(",", ":")),
    )
    settings.sync()


def upsert_link(settings: object, source: str, target: str, kind: str,
                value: float, unit: object, valid_ids: set[str]) -> bool:
    candidate = normalize_links([{
        "source": source,
        "target": target,
        "kind": kind,
        "distance_mm": millimeters(value, unit),
    }], valid_ids)
    if not candidate:
        return False
    links = read_links(settings, valid_ids)
    key = (source, target, kind)
    reverse = (target, source, kind)
    links = [item for item in links if (
        item["source"], item["target"], item["kind"]
    ) not in {key, reverse}]
    links.append(candidate[0])
    write_links(settings, links)
    return True


class CaseSpatialPanel(QGroupBox):
    """Compact editor for measured fan/component spacing and depth."""

    def __init__(self, host):
        super().__init__(host.tr_static("Räumliche Abstände und Tiefe"))
        self.host = host
        self.setObjectName("caseSpatialPanel")
        outer = QVBoxLayout(self)
        note = QLabel(host.tr_static(
            "Nur selbst gemessene Werte werden gespeichert. Sie ändern weder PWM- noch RGB-Zuordnungen."
        ))
        note.setWordWrap(True)
        note.setObjectName("muted")
        outer.addWidget(note)

        flow = QFormLayout()
        self.flow_direction = QComboBox()
        for label, value in (
            (host.tr_static("Wie bisher (pro Anschluss)"), "local"),
            (host.tr_static("Links → rechts"), "left-right"),
            (host.tr_static("Rechts → links"), "right-left"),
            (host.tr_static("Oben → unten"), "top-bottom"),
            (host.tr_static("Unten → oben"), "bottom-top"),
            (host.tr_static("Oben links → unten rechts"), "top-left-bottom-right"),
            (host.tr_static("Unten rechts → oben links"), "bottom-right-top-left"),
            (host.tr_static("Oben rechts → unten links"), "top-right-bottom-left"),
            (host.tr_static("Unten links → oben rechts"), "bottom-left-top-right"),
        ):
            self.flow_direction.addItem(label, value)
        movement, speed = self._read_flow()
        self.flow_direction.setCurrentIndex(max(0, self.flow_direction.findData(movement)))
        self.flow_speed = QSpinBox()
        self.flow_speed.setRange(10, 200)
        self.flow_speed.setSuffix(" %")
        self.flow_speed.setValue(speed)
        self._saved_flow = (movement, speed)
        flow.addRow(host.tr_static("Räumliche Laufrichtung"), self.flow_direction)
        flow.addRow(host.tr_static("Geschwindigkeit"), self.flow_speed)
        outer.addLayout(flow)
        flow_actions = QHBoxLayout()
        save_flow = QPushButton(host.tr_static("Räumlichen Ablauf speichern"))
        save_flow.setObjectName("gpuPrimaryAction")
        edit_order = QPushButton(host.tr_static("LED- und Lüfterreihenfolge bearbeiten"))
        save_flow.clicked.connect(self.save_flow)
        edit_order.clicked.connect(self.edit_selected_order)
        flow_actions.addWidget(save_flow)
        flow_actions.addWidget(edit_order)
        outer.addLayout(flow_actions)
        order_note = QLabel(host.tr_static(
            "Die Reihenfolge wird am gewählten Komponentenblock anhand des echten LED-Verlaufs festgelegt."
        ))
        order_note.setWordWrap(True)
        order_note.setObjectName("muted")
        outer.addWidget(order_note)

        form = QFormLayout()
        self.kind = QComboBox()
        self.kind.addItem(host.tr_static("Direkter Abstand"), "distance")
        self.kind.addItem(host.tr_static("Tiefe"), "depth")
        self.source = QComboBox()
        self.target = QComboBox()
        self.source.setProperty("i18nTranslateItems", False)
        self.target.setProperty("i18nTranslateItems", False)
        self.unit = QComboBox()
        self.unit.addItem(host.tr_static("Millimeter"), "mm")
        self.unit.addItem(host.tr_static("Inch"), "in")
        saved_unit = normalize_unit(host.settings.value(UNIT_KEY, "mm"))
        self.unit.setCurrentIndex(max(0, self.unit.findData(saved_unit)))
        self.value = QDoubleSpinBox()
        self.value.setObjectName("caseDistanceSpin")
        self.value.setDecimals(1)
        self.value.setValue(100.0 if saved_unit == "mm" else 4.0)
        form.addRow(host.tr_static("Messart"), self.kind)
        form.addRow(host.tr_static("Von Lüfter / Komponente"), self.source)
        form.addRow(host.tr_static("Zu Lüfter / Komponente"), self.target)
        value_row = QHBoxLayout()
        value_row.addWidget(self.value, 1)
        value_row.addWidget(self.unit)
        form.addRow(host.tr_static("Abstand"), value_row)
        outer.addLayout(form)

        actions = QHBoxLayout()
        save = QPushButton(host.tr_static("Abstand speichern"))
        save.setObjectName("gpuPrimaryAction")
        delete = QPushButton(host.tr_static("Ausgewählten Abstand löschen"))
        delete.setObjectName("gpuDangerAction")
        save.clicked.connect(self.save_current)
        delete.clicked.connect(self.delete_current)
        actions.addWidget(save)
        actions.addWidget(delete)
        outer.addLayout(actions)
        self.links = QListWidget()
        self.links.setObjectName("caseDistanceList")
        self.links.setMinimumHeight(108)
        self.links.currentItemChanged.connect(self.load_selected)
        outer.addWidget(self.links)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setObjectName("muted")
        outer.addWidget(self.status)
        self.unit.currentIndexChanged.connect(self.change_unit)
        self.refresh()
        self._apply_unit(saved_unit)

    def slot_map(self) -> dict[str, str]:
        return {
            str(slot.slot_id or slot.position): str(slot.name)
            for slot in getattr(self.host, "rgb_layout_slots", ())[:64]
        }

    def refresh(self) -> None:
        saved_flow = self._read_flow()
        if saved_flow != self._saved_flow:
            # Profile loads must update the editor, but ordinary inventory or
            # diagram refreshes must not discard an unfinished direction draft.
            movement, speed = saved_flow
            self.flow_direction.setCurrentIndex(max(0, self.flow_direction.findData(movement)))
            self.flow_speed.setValue(speed)
            self._saved_flow = saved_flow
        names = self.slot_map()
        selected_source = str(self.source.currentData() or "")
        selected_target = str(self.target.currentData() or "")
        for combo in (self.source, self.target):
            combo.blockSignals(True)
            combo.clear()
            for slot_id, name in names.items():
                combo.addItem(name, slot_id)
            combo.blockSignals(False)
        self.source.setCurrentIndex(max(0, self.source.findData(selected_source)))
        target_index = self.target.findData(selected_target)
        self.target.setCurrentIndex(target_index if target_index >= 0 else min(1, self.target.count() - 1))
        self.links.blockSignals(True)
        self.links.clear()
        unit = normalize_unit(self.unit.currentData())
        suffix = "in" if unit == "in" else "mm"
        for link in read_links(self.host.settings, set(names)):
            value = display_distance(float(link["distance_mm"]), unit)
            kind = self.host.tr_static("Tiefe") if link["kind"] == "depth" else self.host.tr_static("Abstand")
            item = QListWidgetItem(
                f"{kind} · {names[link['source']]} ↔ {names[link['target']]} · {value:.2f} {suffix}"
            )
            item.setData(Qt.ItemDataRole.UserRole, dict(link))
            self.links.addItem(item)
        self.links.blockSignals(False)

    def _read_flow(self) -> tuple[str, int]:
        try:
            speed = int(self.host.settings.value("rgb_studio/speed", 100))
        except (TypeError, ValueError):
            speed = 100
        return direction(self.host), max(10, min(200, speed))

    def _apply_unit(self, unit: str) -> None:
        if unit == "in":
            self.value.setRange(0.04, 196.85)
            self.value.setDecimals(2)
            self.value.setSingleStep(0.1)
            self.value.setSuffix(" in")
        else:
            self.value.setRange(1.0, 5000.0)
            self.value.setDecimals(1)
            self.value.setSingleStep(1.0)
            self.value.setSuffix(" mm")

    def change_unit(self, _index: int) -> None:
        previous = normalize_unit(self.host.settings.value(UNIT_KEY, "mm"))
        current = normalize_unit(self.unit.currentData())
        mm_value = millimeters(self.value.value(), previous)
        self._apply_unit(current)
        self.value.setValue(display_distance(mm_value, current))
        self.host.settings.setValue(UNIT_KEY, current)
        self.host.settings.sync()
        self.refresh()
        self._refresh_diagrams()

    def save_current(self) -> None:
        names = self.slot_map()
        saved = upsert_link(
            self.host.settings,
            str(self.source.currentData() or ""),
            str(self.target.currentData() or ""),
            str(self.kind.currentData() or "distance"),
            self.value.value(), self.unit.currentData(), set(names),
        )
        self.status.setText(self.host.tr_static(
            "Abstand gespeichert."
        ) if saved else self.host.tr_static(
            "Bitte zwei unterschiedliche Komponenten und einen gültigen Abstand wählen."
        ))
        if saved:
            self.refresh()
            self._refresh_diagrams()

    def delete_current(self) -> None:
        item = self.links.currentItem()
        data = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if not isinstance(data, dict):
            return
        names = self.slot_map()
        key = (data.get("source"), data.get("target"), data.get("kind"))
        remaining = [link for link in read_links(self.host.settings, set(names))
                     if (link["source"], link["target"], link["kind"]) != key]
        write_links(self.host.settings, remaining)
        self.refresh()
        self._refresh_diagrams()

    def load_selected(self, current: QListWidgetItem | None, _previous=None) -> None:
        data = current.data(Qt.ItemDataRole.UserRole) if current is not None else None
        if not isinstance(data, dict):
            return
        self.source.setCurrentIndex(max(0, self.source.findData(data["source"])))
        self.target.setCurrentIndex(max(0, self.target.findData(data["target"])))
        self.kind.setCurrentIndex(max(0, self.kind.findData(data["kind"])))
        self.value.setValue(display_distance(float(data["distance_mm"]), self.unit.currentData()))

    def _refresh_diagrams(self) -> None:
        from .case_page import refresh_case_views
        refresh_case_views(self.host)

    def save_flow(self) -> None:
        movement = str(self.flow_direction.currentData() or "local")
        if not set_case_direction(self.host, movement):
            return
        speed = self.flow_speed.value()
        self.host.settings.setValue("rgb_studio/speed", speed)
        self.host.settings.sync()
        self._saved_flow = (movement, speed)
        editor = getattr(self.host, "rgb_studio_speed", None)
        if editor is not None:
            editor.setValue(speed)
        declared_paths = sum(len(zones) for zones in paths(self.host).values())
        message = "Räumlicher Ablauf gespeichert."
        if movement != "local" and not declared_paths:
            message = (
                "Räumlicher Ablauf gespeichert. Bitte zuerst den LED-Verlauf am Anschluss festlegen; "
                "ohne ihn bleibt die Beleuchtung lokal."
            )
        self.status.setText(self.host.tr_static(message))
        if hasattr(self.host, "log_message"):
            self.host.log_message(
                f"ARGB-DIAG: op=case-direction-save · case_direction={movement} · "
                f"declared_paths={declared_paths} · speed_percent={speed} · "
                "settings-only · physical_readback=unavailable"
            )
        self._refresh_diagrams()
        if (getattr(self.host, "openrgb_write_enabled", False)
                and getattr(self.host, "rgb_selected_devices", ())
                and hasattr(self.host, "request_rgb_direct_apply")):
            self.host.request_rgb_direct_apply(delay_ms=360)

    def edit_selected_order(self) -> None:
        from modules.rgb_studio.v1_15.argb_controls import edit_slot_header
        slot_id = str(self.source.currentData() or "")
        if slot_id:
            edit_slot_header(self.host, slot_id)
