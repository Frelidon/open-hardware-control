#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware-aware dashboard card layout and overview status hints."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

from ui_layout import DASHBOARD_CARD_DEFAULTS, dashboard_card_hardware_available


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
        visible = [
            card for key, _title, card in getattr(self, "dashboard_card_entries", [])
            if key in enabled_cards and dashboard_card_hardware_available(
                key,
                kraken_connected=bool(getattr(self, "devices_ready", False)),
                liquid_temperature=getattr(self, "current_liquid_temp", None),
            )
        ]
        for index, card in enumerate(visible):
            self.dashboard_cards_layout.addWidget(card, index // columns, index % columns)

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
