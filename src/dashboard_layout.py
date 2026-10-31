#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware-aware dashboard card layout and overview status hints."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QCheckBox, QFrame, QHBoxLayout, QLabel, QPushButton, QTreeWidget, QVBoxLayout, QWidget

from ui_layout import DASHBOARD_CARD_DEFAULTS, dashboard_card_hardware_available, sanitize_dashboard_cards


DASHBOARD_HINT_OK = "OK"
DASHBOARD_HINT_FAULT = "Fehlerhaft"
DASHBOARD_HINT_DETAIL_COLOR = "#8f9cad"
DASHBOARD_HINT_KEYS = ("cooling", "sensors", "profiles", "privacy")


@dataclass(frozen=True)
class DashboardHintRow:
    """One Overview 'Status & Hinweise' row with a right-hand OK/fault badge."""

    key: str
    title: str
    detail: str
    ok: bool
    translate_detail: bool = True

    @property
    def badge_text(self) -> str:
        return DASHBOARD_HINT_OK if self.ok else DASHBOARD_HINT_FAULT

    @property
    def object_name(self) -> str:
        return "healthGood" if self.ok else "healthCritical"


def dashboard_hint_html(title: str, detail: str) -> str:
    """Render a hardware-list-style title and muted detail line."""

    return (
        f"<b>{escape(title)}</b><br>"
        f"<span style='color:{DASHBOARD_HINT_DETAIL_COLOR}'>{escape(detail)}</span>"
    )


def dashboard_status_hints(
    *,
    thermalright: bool,
    cooling_ready: bool,
    kraken_connected: bool,
    kraken_health_text: str = "",
    kraken_health_ok: bool = False,
    sensors_ok: bool,
) -> tuple[DashboardHintRow, ...]:
    """Return Overview status rows from current cooling and sensor state.

    Confirmed Levita PWM tests flip the cooling row from fault to OK. This
    function performs no hardware discovery or writes.
    """

    if thermalright and cooling_ready:
        cooling = DashboardHintRow(
            key="cooling",
            title="Levita-Kühlung bestätigt",
            detail="Pumpe und Radiator sind nach zwei PWM-Tests steuerbar.",
            ok=True,
        )
    elif thermalright:
        cooling = DashboardHintRow(
            key="cooling",
            title="Levita erkannt",
            detail="Pumpe und Radiator werden erst nach zwei bestätigten PWM-Tests steuerbar.",
            ok=False,
        )
    elif kraken_connected:
        cooling = DashboardHintRow(
            key="cooling",
            title="Kraken-Kühlung",
            detail=kraken_health_text or "Kühlung arbeitet normal.",
            ok=kraken_health_ok,
            translate_detail=not bool(kraken_health_text),
        )
    else:
        cooling = DashboardHintRow(
            key="cooling",
            title="Kühlung",
            detail=kraken_health_text or "Gerät wird geprüft …",
            ok=False,
            translate_detail=not bool(kraken_health_text),
        )
    if sensors_ok:
        sensors = DashboardHintRow(
            key="sensors",
            title="Sensoren synchronisiert",
            detail="Lokale Hardwarewerte werden fortlaufend aktualisiert.",
            ok=True,
        )
    else:
        sensors = DashboardHintRow(
            key="sensors",
            title="Sensoren nicht aktuell",
            detail="Lokale Hardwarewerte konnten nicht gelesen werden.",
            ok=False,
        )
    return (
        cooling,
        sensors,
        DashboardHintRow(
            key="profiles",
            title="Profile verfügbar",
            detail="Leise, Ausbalanciert und Leistung können direkt angewendet werden.",
            ok=True,
        ),
        DashboardHintRow(
            key="privacy",
            title="Keine Cloud erforderlich",
            detail="Steuerung bleibt lokal auf diesem System.",
            ok=True,
        ),
    )


class DashboardLayoutMixin:
    """Compose selected cards without exposing unavailable hardware values."""

    def adapt_dashboard_layout(self) -> None:
        if not hasattr(self, "dashboard_cards_layout"):
            return
        layout_mode = self.display_layout
        if layout_mode == "auto":
            width = self.width()
            columns = 5 if width >= 1220 else 4 if width >= 980 else 2
        else:
            columns = {"16:10": 4, "16:9": 5, "21:9": 5, "32:9": 5}.get(layout_mode, 4)
        while self.dashboard_cards_layout.count():
            self.dashboard_cards_layout.takeAt(0)
        enabled_cards = {
            key for key, checkbox in getattr(self, "dashboard_card_checkboxes", {}).items()
            if checkbox.isChecked()
        }
        entries = {key: (title, card) for key, title, card in getattr(self, "dashboard_card_entries", [])}
        order = self.dashboard_card_order()
        visible = [
            entries[key][1] for key in order if key in entries
            if key in enabled_cards and dashboard_card_hardware_available(
                key,
                kraken_connected=bool(getattr(self, "devices_ready", False)),
                liquid_temperature=getattr(self, "current_liquid_temp", None),
            )
        ]
        for index, card in enumerate(visible):
            self.dashboard_cards_layout.addWidget(card, index // columns, index % columns)

    def install_dashboard_card_customization(self, page_layout, status_layout) -> None:
        """Install the visible ordering editor while retaining the checkbox model."""
        customize = QPushButton("Karten anpassen")
        customize.setCheckable(True)
        customize.setAccessibleName("Dashboard-Karten anpassen")
        status_layout.addWidget(customize)
        self.dashboard_card_checkboxes = {}
        visible_cards = set(sanitize_dashboard_cards(self.settings.value("dashboard/visible_cards")))
        self.dashboard_fields_hidden = QWidget()
        hidden_layout = QVBoxLayout(self.dashboard_fields_hidden)
        for key, title, _card in self.dashboard_card_entries:
            checkbox = QCheckBox(title)
            checkbox.setChecked(key in visible_cards)
            checkbox.toggled.connect(lambda checked, value=key: self.set_dashboard_card_visible(value, checked))
            self.dashboard_card_checkboxes[key] = checkbox
            hidden_layout.addWidget(checkbox)
        self.dashboard_fields_hidden.setVisible(False)

        self.dashboard_editor_panel = QFrame()
        self.dashboard_editor_panel.setObjectName("dashboardSection")
        editor_layout = QVBoxLayout(self.dashboard_editor_panel)
        editor_header = QHBoxLayout()
        title = QLabel("Dashboard-Karten"); title.setObjectName("sectionTitle")
        hint = QLabel("Ziehen zum Sortieren · Haken zum Ein- oder Ausblenden"); hint.setObjectName("muted")
        editor_header.addWidget(title); editor_header.addWidget(hint, 1)
        reset = QPushButton("Standard wiederherstellen")
        reset.clicked.connect(self.reset_dashboard_card_editor)
        editor_header.addWidget(reset); editor_layout.addLayout(editor_header)
        self.dashboard_card_editor = QTreeWidget()
        self.dashboard_card_editor.setHeaderHidden(True)
        self.dashboard_card_editor.setRootIsDecorated(False)
        self.dashboard_card_editor.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.dashboard_card_editor.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.dashboard_card_editor.setMinimumHeight(220)
        self.dashboard_card_editor.itemChanged.connect(self.dashboard_card_editor_changed)
        self.dashboard_card_editor.model().rowsMoved.connect(self.dashboard_card_order_changed)
        editor_layout.addWidget(self.dashboard_card_editor)
        self.dashboard_editor_panel.setVisible(False)
        customize.toggled.connect(self.dashboard_editor_panel.setVisible)
        page_layout.addWidget(self.dashboard_editor_panel)
        self.populate_dashboard_card_editor()

    def dashboard_card_order(self) -> list[str]:
        fallback = [key for key, _title, _card in getattr(self, "dashboard_card_entries", [])]
        tree = getattr(self, "dashboard_card_editor", None)
        if tree is not None and tree.topLevelItemCount():
            order = [str(tree.topLevelItem(index).data(0, Qt.ItemDataRole.UserRole)) for index in range(tree.topLevelItemCount())]
            if len(order) == len(fallback) and set(order) == set(fallback):
                return order
        saved = self.settings.value("dashboard/card_order") if hasattr(self, "settings") else None
        if isinstance(saved, str):
            saved = [part for part in saved.split(",") if part]
        if isinstance(saved, (list, tuple)) and len(saved) == len(fallback) and set(map(str, saved)) == set(fallback):
            return [str(part) for part in saved]
        return fallback

    def dashboard_card_editor_changed(self, item, _column: int = 0) -> None:
        if getattr(self, "_dashboard_editor_syncing", False):
            return
        key = str(item.data(0, Qt.ItemDataRole.UserRole) or "")
        self.set_dashboard_card_visible(key, item.checkState(0) == Qt.CheckState.Checked)

    def dashboard_card_order_changed(self, *_args) -> None:
        order = self.dashboard_card_order()
        self.settings.setValue("dashboard/card_order", order)
        self.settings.sync()
        self.adapt_dashboard_layout()

    def reset_dashboard_card_editor(self) -> None:
        self.settings.remove("dashboard/card_order")
        # A live reordered tree must not supersede the just-reset setting.
        self.dashboard_card_editor.clear()
        self.reset_dashboard_card_visibility()

    def populate_dashboard_card_editor(self) -> None:
        tree = getattr(self, "dashboard_card_editor", None)
        if tree is None:
            return
        entries = {key: title for key, title, _card in self.dashboard_card_entries}
        order = self.dashboard_card_order()
        self._dashboard_editor_syncing = True
        tree.clear()
        from PySide6.QtWidgets import QTreeWidgetItem
        for key in order:
            item = QTreeWidgetItem([entries[key]])
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            item.setFlags((item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsDragEnabled) & ~Qt.ItemFlag.ItemIsDropEnabled)
            checkbox = self.dashboard_card_checkboxes[key]
            item.setCheckState(0, Qt.CheckState.Checked if checkbox.isChecked() else Qt.CheckState.Unchecked)
            tree.addTopLevelItem(item)
        self._dashboard_editor_syncing = False

    def set_dashboard_card_visible(self, key: str, visible: bool) -> None:
        checkbox = getattr(self, "dashboard_card_checkboxes", {}).get(key)
        if checkbox is not None and checkbox.isChecked() != bool(visible):
            checkbox.blockSignals(True)
            checkbox.setChecked(bool(visible))
            checkbox.blockSignals(False)
        self.apply_dashboard_card_visibility(save=True)

    def apply_dashboard_card_visibility(self, *, save: bool) -> None:
        if not hasattr(self, "dashboard_card_entries"):
            return
        selected: list[str] = []
        for key, _title, card in self.dashboard_card_entries:
            checkbox = self.dashboard_card_checkboxes.get(key)
            selected_by_user = bool(checkbox and checkbox.isChecked())
            available = dashboard_card_hardware_available(
                key,
                kraken_connected=bool(getattr(self, "devices_ready", False)),
                liquid_temperature=getattr(self, "current_liquid_temp", None),
            )
            card.setVisible(selected_by_user and available)
            if selected_by_user:
                selected.append(key)
        if save:
            self.settings.setValue("dashboard/visible_cards", selected)
            self.settings.sync()
        self.adapt_dashboard_layout()

    def reset_dashboard_card_visibility(self) -> None:
        for key in DASHBOARD_CARD_DEFAULTS:
            checkbox = self.dashboard_card_checkboxes.get(key)
            if checkbox is not None:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)
        self.apply_dashboard_card_visibility(save=True)
        if hasattr(self, "dashboard_card_editor"):
            self.populate_dashboard_card_editor()

    def update_dashboard_status_hints(self) -> None:
        widgets = getattr(self, "dashboard_hint_widgets", None)
        if not widgets:
            return
        translate = getattr(self, "tr_static", lambda source: source)
        thermalright = bool(
            self.is_thermalright_cooling()
        ) if hasattr(self, "is_thermalright_cooling") else False
        kraken_connected = bool(getattr(self, "devices_ready", False))
        cooling_ready = False
        if thermalright and hasattr(self, "thermalright_channel") and hasattr(self, "mainboard_profile_for"):
            pump = self.thermalright_channel("pump")
            radiator = self.thermalright_channel("fan")
            cooling_ready = bool(
                pump
                and radiator
                and self.mainboard_profile_for(pump).get("calibrated", False)
                and self.mainboard_profile_for(radiator).get("calibrated", False)
            )
        sensors_ok = any(
            getattr(self, name, None) is not None
            for name in ("current_cpu_temp", "current_gpu_temp", "current_liquid_temp")
        ) or thermalright or kraken_connected or bool(getattr(self, "last_status_ok", False))
        rows = dashboard_status_hints(
            thermalright=thermalright,
            cooling_ready=cooling_ready,
            kraken_connected=kraken_connected,
            kraken_health_text=str(getattr(self, "dashboard_kraken_health_text", "") or ""),
            kraken_health_ok=bool(getattr(self, "dashboard_kraken_health_ok", False)),
            sensors_ok=sensors_ok,
        )
        for row in rows:
            title_label, badge = widgets[row.key]
            title = translate(row.title)
            detail = translate(row.detail) if row.translate_detail else row.detail
            title_label.setText(dashboard_hint_html(title, detail))
            badge.setText(f"● {translate(row.badge_text)}")
            badge.setObjectName(row.object_name)
            badge.style().unpolish(badge)
            badge.style().polish(badge)
            if row.key == "cooling":
                self.health_label = title_label
                self.health_badge = badge
