# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit static-card recognition; no control or measurement state is changed."""
from .model import recognition, topology_counts


def initialize(host, *, cpu_model, cpu_topology, gpu_model, gpu_memory, gpu_path):
    host.dashboard_inventory = dict(cpu_model=cpu_model, cpu_topology=cpu_topology,
        gpu_model=gpu_model, gpu_memory=gpu_memory, gpu_path=gpu_path)
    refresh(host)


def refresh(host):
    inventory = getattr(host, "dashboard_inventory", None)
    if not inventory: return
    states = recognition(**inventory)
    tr = host.tr_static
    for key, recognized in states.items():
        card = getattr(host, key + "_card", None)
        if card is None: continue
        card.set_status(True if recognized else None)
        label = tr("Erkannt" if recognized else "Nicht verfügbar")
        card.status_dot.setText(("● " if recognized else "○ ") + label)
        card.status_dot.setAccessibleName(label)
        explanation = (tr("Lokale Hardwaredaten sind verfügbar. Die Steuerfreigabe wird im jeweiligen Modul geprüft.")
                       if recognized else tr("Keine bestätigten lokalen Hardwaredaten verfügbar."))
        if recognized:
            explanation += "\n" + tr("Die Erkennung beschreibt das Gerät. Aktuelle Sensormesswerte stehen in den Messwertkarten.")
        card.status_dot.setToolTip(explanation); card.setToolTip(explanation)
        card.setAccessibleDescription(explanation)
    cores, threads = topology_counts(inventory["cpu_topology"])
    if threads is not None:
        text = f"{threads} {tr('Threads')}"
        if cores is not None: text = f"{cores} {tr('Kerne')} · " + text
        host.cpu_topology_card.value_label.setText(text)
        host.cpu_topology_card.hint_label.setText("Linux /proc/cpuinfo")
    for key in ("cpu_model", "gpu_model", "gpu_memory"):
        value = str(inventory[key])
        if value in {"Prozessor nicht erkannt", "Grafikkarte nicht erkannt", "VRAM nicht gemeldet"}:
            getattr(host, key + "_card").value_label.setText(tr(value))
    from .device_rows import refresh as refresh_rows
    refresh_rows(host, **getattr(host, "dashboard_hardware_detection", {}))
