# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware-list badges consume existing confirmed inventories, not capabilities."""
from html import escape
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from .model import recognition


def build(host, layout):
    host.dashboard_hardware_widgets = {}
    for key in ("cooling", "mainboard", "rgb", "gpu"):
        row = QFrame(); row.setObjectName("hardwareListRow")
        content = QHBoxLayout(row); content.setContentsMargins(10, 8, 10, 8)
        text = QLabel(); text.setWordWrap(True); status = QLabel()
        content.addWidget(text, 1); content.addWidget(status)
        layout.addWidget(row); host.dashboard_hardware_widgets[key] = (text, status)
    refresh(host)


def refresh(host, *, thermalright=False, kraken_connected=None):
    widgets = getattr(host, "dashboard_hardware_widgets", None)
    if not widgets: return
    tr = host.tr_static
    connected = bool(getattr(host, "devices_ready", False)) if kraken_connected is None else bool(kraken_connected)
    thermalright_present = bool(thermalright and getattr(host, "dashboard_thermalright_present", False))
    host.dashboard_hardware_detection = dict(thermalright=bool(thermalright), kraken_connected=connected)
    inventory = getattr(host, "dashboard_inventory", {})
    gpu = bool(inventory and recognition(**inventory)["gpu_model"])
    channels = getattr(host, "mainboard_channels", {})
    devices = getattr(host, "openrgb_devices", ())
    cooler = "Thermalright Levita Vision" if thermalright else "NZXT Kraken" if connected else tr("Kühlung")
    rows = {
        "cooling": (cooler, tr("Kühlmittel · Pumpe · Radiator · LCD") if connected else
                    "1600 × 720 · LCD" if thermalright_present else tr("Nicht verfügbar"), bool(thermalright_present or connected)),
        "mainboard": (tr("Mainboard / PWM"), tr("Sensoren · Systemlüfter · PWM") if channels else tr("Nicht verfügbar"), bool(channels)),
        "rgb": ("OpenRGB", f"{len(devices)} {tr('Erkannte Geräte')}" if devices else tr("Nicht verfügbar"), bool(devices)),
        "gpu": (tr("Grafikkarte"), str(inventory.get("gpu_model", "")) if gpu else tr("Nicht verfügbar"), gpu),
    }
    for key, (title, detail, detected) in rows.items():
        text, badge = widgets[key]
        text.setText(f"<b>{escape(title)}</b><br>{escape(detail)}")
        badge.setText(("● " if detected else "○ ") + tr("Erkannt" if detected else "Nicht verfügbar"))
        badge.setObjectName("healthGood" if detected else "muted")
        badge.setToolTip(tr("Lokale Hardwaredaten sind verfügbar. Die Steuerfreigabe wird im jeweiligen Modul geprüft.")
                         if detected else tr("Keine bestätigten lokalen Hardwaredaten verfügbar."))
        badge.style().unpolish(badge); badge.style().polish(badge)
