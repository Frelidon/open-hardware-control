# SPDX-License-Identifier: GPL-3.0-or-later
"""Polished GPU header and live metric cards."""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class GpuDashboardUiMixin:
    def _metric_card(self, icon: str, title: str, initial: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("gpuMetricCard")
        card.setMinimumHeight(76)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(8, 9, 8, 9)
        layout.setSpacing(6)
        glyph = QLabel(icon)
        glyph.setObjectName("gpuMetricIcon")
        glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        glyph.setFixedSize(30, 30)
        copy = QVBoxLayout()
        copy.setSpacing(2)
        caption = QLabel(title)
        caption.setObjectName("gpuMetricTitle")
        value = QLabel(initial)
        value.setObjectName("gpuMetricValue")
        copy.addWidget(caption)
        copy.addWidget(value)
        layout.addWidget(glyph)
        layout.addLayout(copy, 1)
        return card, value

    def _build_gpu_dashboard(self, outer: QVBoxLayout) -> None:
        hero = QFrame()
        hero.setObjectName("gpuHeroCard")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(14, 8, 14, 8)
        hero_layout.setSpacing(12)

        copy = QVBoxLayout()
        copy.setSpacing(4)
        eyebrow = QLabel("OPEN HARDWARE CONTROL · GPU")
        eyebrow.setObjectName("gpuEyebrow")
        title = QLabel(self.tr("Grafikkarte"))
        title.setObjectName("gpuHeroTitle")
        subtitle = QLabel(self.tr(
            "GPU-Informationen, LACT-Tuning und Lüfterbesitz mit testweiser Rückstellung."
        ))
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        copy.addWidget(eyebrow)
        copy.addWidget(title)
        copy.addWidget(subtitle)
        hero_layout.addLayout(copy, 1)

        service = QVBoxLayout()
        service.setSpacing(5)
        service.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        badge = self.gpu_service_badge = QLabel()
        badge.setObjectName("muted")
        badge.setMinimumHeight(34)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        service.addWidget(badge)
        self.gpu_service_note = QLabel(self.tr("Lesestatus"), objectName="muted")
        service.addWidget(self.gpu_service_note)
        from .read_status import set_state
        set_state(self, "unknown")
        hero_layout.addLayout(service)
        outer.addWidget(hero)
        self.gpu_hero_card = hero

        metrics_host = QWidget()
        metrics_host.setObjectName("gpuMetricsPanel")
        metrics = QGridLayout(metrics_host)
        metrics.setContentsMargins(0, 0, 0, 0)
        metrics.setHorizontalSpacing(10)
        metrics.setVerticalSpacing(10)
        definitions = (
            ("●", "GPU", "— °C", "gpu_temperature_value"),
            ("♨", "Hotspot", "— °C", "gpu_hotspot_value"),
            ("✣", self.tr("Lüfter"), "— RPM", "gpu_fan_rpm_value"),
            ("ϟ", self.tr("Leistungsaufnahme"), "— W", "gpu_power_value"),
        )
        for column, (icon, title, value, attr) in enumerate(definitions):
            card, label = self._metric_card(icon, title, value)
            setattr(self, attr, label)
            metrics.addWidget(card, column // 2, column % 2)
            metrics.setColumnStretch(column % 2, 1)
        self.gpu_metrics_panel = metrics_host
        outer.addWidget(metrics_host)

    @staticmethod
    def _number(value: Any) -> float | None:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        if isinstance(value, dict):
            current = value.get("current")
            if isinstance(current, (int, float)) and not isinstance(current, bool):
                return float(current)
        return None

    def _refresh_gpu_dashboard(self) -> None:
        stats = self.stats if isinstance(getattr(self, "stats", None), dict) else {}
        temps = stats.get("temps") if isinstance(stats.get("temps"), dict) else {}
        fan = stats.get("fan") if isinstance(stats.get("fan"), dict) else {}
        power = stats.get("power") if isinstance(stats.get("power"), dict) else {}
        edge = self._number(temps.get("edge"))
        hotspot = self._number(temps.get("junction"))
        if hotspot is None:
            hotspot = self._number(temps.get("hotspot"))
        rpm = self._number(fan.get("speed_current"))
        watts = self._number(power.get("average"))
        self.gpu_temperature_value.setText("— °C" if edge is None else f"{edge:.0f} °C")
        self.gpu_hotspot_value.setText("— °C" if hotspot is None else f"{hotspot:.0f} °C")
        self.gpu_fan_rpm_value.setText("— RPM" if rpm is None else f"{rpm:,.0f} RPM".replace(",", "."))
        self.gpu_power_value.setText("— W" if watts is None else f"{watts:.0f} W")
        if hasattr(self, "stress_live_temperature"):
            clocks = stats.get("clockspeed") if isinstance(stats.get("clockspeed"), dict) else {}
            busy = self._number(stats.get("busy_percent"))
            clock = self._number(clocks.get("gpu_clockspeed"))
            self.stress_live_load.setText(self.tr("GPU-Auslastung") + ("\n— %" if busy is None else f"\n{busy:.0f} %"))
            self.stress_live_clock.setText(self.tr("GPU-Taktrate") + ("\n— MHz" if clock is None else f"\n{clock:.0f} MHz"))
            self.stress_live_temperature.setText(self.tr("Temperatur") + ("\n— °C" if edge is None else f"\n{edge:.0f} °C"))
            self.stress_live_power.setText(self.tr("Leistungsaufnahme") + ("\n— W" if watts is None else f"\n{watts:.0f} W"))
