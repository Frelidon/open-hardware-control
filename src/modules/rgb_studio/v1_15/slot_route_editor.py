# SPDX-License-Identifier: GPL-3.0-or-later
"""Choose a physical header directly from a case block, then edit/test LEDs."""
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import QTimer
from .gpu_led_editor import configure_argb_header
from .slot_routes import reported_sources, remember_slot_route, slot_routes


def build_slot_route_dialog(host, slot, targets, *, suggested_count=None, suggested_units=None):
    tr = host.tr_static
    key = slot.slot_id or slot.position
    sources = reported_sources(host)
    dialog = QDialog(host)
    dialog.setObjectName("slotArgbRouteDialog")
    dialog.setWindowTitle(f'{tr("ARGB-Anschluss")} · {slot.name}')
    dialog.setMinimumWidth(580)
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel(tr("Gerät")))
    controller = QComboBox()
    controller.setObjectName("slotArgbController")
    controller.addItem(tr("Kein ARGB-Anschluss zugeordnet"), "")
    for d in sources:
        controller.addItem(d.name, host.openrgb_stable_ids[d.index])
    layout.addWidget(controller)
    layout.addWidget(QLabel(tr("ARGB-Anschluss")))
    zone = QComboBox()
    zone.setObjectName("slotArgbZone")
    layout.addWidget(zone)
    note = QLabel(tr("Die LED-Anzahl ist manuell; OHC erkennt die physische Länge nicht. Nur dieser Anschluss wird geändert."))
    note.setWordWrap(True)
    layout.addWidget(note)
    recovery = QPushButton(tr("↻ RGB-Steuerung neu übernehmen"))
    recovery.setObjectName("slotArgbRecoverEngine")
    recovery.setMinimumHeight(38)
    layout.addWidget(recovery)
    recovery.clicked.connect(lambda _checked=False: host.restart_rgb_engine_and_refresh())
    edit = QPushButton(tr("LED-Anzahl am ARGB-Anschluss ändern"))
    edit.setMinimumHeight(38)
    edit.setObjectName("slotArgbEditLeds")
    layout.addWidget(edit)
    test = QPushButton(tr("Eine LED testen"))
    test.setMinimumHeight(38)
    test.setObjectName("slotArgbTestLed")
    layout.addWidget(test)
    buttons = QDialogButtonBox()
    save = buttons.addButton(tr("Steuerweg speichern"), QDialogButtonBox.ButtonRole.AcceptRole)
    buttons.addButton(tr("Abbrechen"), QDialogButtonBox.ButtonRole.RejectRole)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    stored = slot_routes(host).get(key)
    # Only an unambiguous existing assignment is preselected; never guess a port.
    if stored is None and len(targets) == 1:
        d, name, _gpu = targets[0]
        stored = {"controller": host.openrgb_stable_ids.get(d.index, ""), "zone": name}
    stored = stored or {}

    def update_buttons():
        valid = bool(controller.currentData() and zone.currentData())
        writable = (getattr(host, "openrgb_server_reachable", True)
                    and not getattr(host, "openrgb_external_server_detected", False))
        edit.setEnabled(valid and writable)
        test.setEnabled(valid and writable)
        save.setEnabled(valid or not controller.currentData())
        recovery.setVisible(not writable or not sources)
        if not writable:
            note.setText(tr("Die eigene RGB-Engine muss erreichbar sein."))
        else:
            note.setText(tr("Die LED-Anzahl ist manuell; OHC erkennt die physische Länge nicht. Nur dieser Anschluss wird geändert."))

    def update_zones():
        zone.clear()
        zone.addItem(tr("Bitte ARGB-Anschluss auswählen"), "")
        d = next((d for d in sources if host.openrgb_stable_ids[d.index] == controller.currentData()), None)
        if d is not None:
            for name in d.zones:
                zone.addItem(name, name)
            if controller.currentData() == stored.get("controller"):
                zone.setCurrentIndex(max(0, zone.findData(stored.get("zone"))))
        zone.setEnabled(d is not None)
        update_buttons()

    def commit(open_leds=False):
        if not remember_slot_route(host, key, controller.currentData(), zone.currentData() or ""):
            update_buttons()
            return
        stop_inventory_timer()
        dialog.accept()
        if open_leds:
            from .argb_controls import slot_header_targets
            targets_now = slot_header_targets(host, slot)
            if targets_now:
                source, name, gpu = targets_now[0]
                kwargs = {}
                if suggested_count is not None: kwargs["suggested_count"] = suggested_count
                if suggested_units is not None: kwargs["suggested_units"] = suggested_units
                configure_argb_header(host, source, name, gpu=gpu, component_name=slot.name, **kwargs)

    controller.currentIndexChanged.connect(lambda _index: update_zones())
    zone.currentIndexChanged.connect(lambda _index: update_buttons())
    controller.setCurrentIndex(max(0, controller.findData(stored.get("controller", ""))))
    update_zones()
    save.clicked.connect(lambda _checked=False: commit())
    edit.clicked.connect(lambda _checked=False: commit(True))
    test.clicked.connect(lambda _checked=False: commit(True))
    timer = QTimer(dialog)
    timer.setObjectName("slotArgbInventoryTimer")
    dialog._inventory_timer = timer  # Keep the Python wrapper alive with its dialog.
    timer_connected = True

    def stop_inventory_timer(*_args):
        nonlocal timer_connected
        try:
            timer.stop()
        except RuntimeError:
            return
        if timer_connected:
            try:
                timer.timeout.disconnect(refresh_inventory)
            except (RuntimeError, TypeError):
                pass
            timer_connected = False

    def refresh_inventory():
        nonlocal sources
        try:
            dialog.objectName()
            controller.currentData()
            zone.currentData()
        except RuntimeError:
            stop_inventory_timer()
            return
        current_sources = reported_sources(host)
        if current_sources != sources:
            chosen, chosen_zone = controller.currentData(), zone.currentData()
            sources = current_sources
            stored.update(controller=chosen, zone=chosen_zone)
            controller.blockSignals(True)
            controller.clear()
            controller.addItem(tr("Kein ARGB-Anschluss zugeordnet"), "")
            for d in sources:
                controller.addItem(d.name, host.openrgb_stable_ids[d.index])
            controller.setCurrentIndex(max(0, controller.findData(chosen)))
            controller.blockSignals(False)
            update_zones()
        update_buttons()
    timer.timeout.connect(refresh_inventory)
    dialog.finished.connect(stop_inventory_timer)
    timer.start(300)
    return dialog


def choose_slot_header(host, slot, targets, *, suggested_count=None, suggested_units=None):
    from modules.pc_case_profiles.v1_5.inline_editor import present_editor
    dialog = build_slot_route_dialog(host, slot, targets, suggested_count=suggested_count,
                                     suggested_units=suggested_units)
    if not present_editor(host, dialog): dialog.exec()
