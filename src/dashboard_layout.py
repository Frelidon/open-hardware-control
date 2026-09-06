#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware-aware dashboard card layout orchestration."""

from __future__ import annotations

from ui_layout import DASHBOARD_CARD_DEFAULTS, dashboard_card_hardware_available


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
