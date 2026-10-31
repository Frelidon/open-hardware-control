#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit GPU ARGB controller and zone routing."""

from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout,
)

from .gpu_routing import normalize_gpu_routes, route_source, route_zone, render_zone_frame, gpu_zone_overrides
from .gpu_led_editor import configure_gpu_header
from .argb_store import retain_manual_headers
from .slot_routes import slot_routes

class GpuLightingMixin:
    """Compose GPU setup and delegate real LED bounds/writes to the zone editor."""

    def update_rgb_visual_elapsed(self, wall_elapsed):
        """Advance every Direct component smoothly from one shared clock."""
        from .gpu_motion import paced_elapsed
        previous = getattr(self, "rgb_last_wall_elapsed", None)
        elapsed = (0. if previous is None else paced_elapsed(
            getattr(self, "rgb_visual_elapsed", 0.), max(0., wall_elapsed - previous)))
        self.rgb_visual_elapsed = self.rgb_gpu_visual_elapsed = elapsed
        self.rgb_last_wall_elapsed = self.rgb_gpu_last_wall_elapsed = wall_elapsed
        return elapsed

    def update_rgb_gpu_visual_elapsed(self, wall_elapsed):
        """Compatibility entry point for the GPU motion editor and tests."""
        previous = getattr(self, "rgb_gpu_last_wall_elapsed", None)
        if not hasattr(self, "rgb_last_wall_elapsed"):
            self.rgb_last_wall_elapsed = previous
            self.rgb_visual_elapsed = getattr(self, "rgb_gpu_visual_elapsed", 0.)
        elapsed = GpuLightingMixin.update_rgb_visual_elapsed(self, wall_elapsed)
        self.rgb_gpu_last_wall_elapsed = wall_elapsed
        return elapsed

    def rgb_worker_render_payload(self, stable_id, device, config, count, sizes, elapsed):
        from .render_plan import build
        return {"render_plan": build(self, stable_id, device, config, elapsed)}

    def rgb_packet_role(self, stable_id):
        device = next((
            item for item in self.openrgb_devices
            if self.openrgb_stable_ids.get(item.index) == stable_id
        ), None)
        if device is not None and getattr(self, "is_rgb_ram_device", lambda _device: False)(device):
            return "ram"
        if any(route_source(route) == stable_id for route in self.rgb_gpu_routes.values()):
            return "gpu"
        if route_source(slot_routes(self).get("gpu-support", {})) == stable_id:
            return "support"
        return ""

    def load_gpu_routes(self):
        try:
            raw = json.loads(str(self.settings.value("rgb_studio/gpu_routes", "{}")))
        except (TypeError, ValueError):
            raw = {}
        return normalize_gpu_routes(raw)

    def build_gpu_setup_button(self, layout):
        # The host captures canonical static captions before applying the saved language.
        self.openrgb_gpu_setup_button = QPushButton("Grafikkarte: Steuerweg und LEDs")
        self.openrgb_gpu_setup_button.clicked.connect(lambda _checked=False: self.configure_gpu_lighting())
        layout.addWidget(self.openrgb_gpu_setup_button)

    def configure_gpu_lighting(self, target_device=None) -> None:
        candidates = [device for device in self.openrgb_devices
                      if device.device_type.casefold() == "gpu"
                      or "sapphire" in device.name.casefold()]
        if target_device is None:
            from .argb_controls import edit_slot_header, external_gpu_setup_slot
            slot = external_gpu_setup_slot(self)
            if slot is not None and not any(
                    self.openrgb_stable_ids.get(device.index) in slot.device_ids for device in candidates):
                # The external 5-V strip belongs to its real reported Direct
                # controller, even when no native GPU controller is discovered.
                edit_slot_header(self, slot.slot_id or slot.position, route_only=True)
                return
        if target_device not in candidates:
            selected = self.selected_openrgb_device()
            target_device = selected if selected in candidates else next(iter(candidates), None)
        if target_device is None:
            self.show_error(self.tr_static("Keine OpenRGB-Grafikkarte erkannt."))
            return
        if target_device.supports_direct:
            self.configure_openrgb_zones(target_device)
            return
        gpu_id = self.openrgb_stable_ids.get(target_device.index)
        if not gpu_id:
            return
        sources = [device for device in self.openrgb_devices
                   if device.supports_direct and not self.openrgb_device_conflict(device)
                   and device.device_type.casefold() in {"motherboard", "led strip", "unknown", "unbekannt"}
                   and self.openrgb_stable_ids.get(device.index)]
        dialog, source_combo, zone_combo, save, edit = self.build_gpu_lighting_dialog(target_device, gpu_id, sources)

        def commit(edit_leds=False):
            source_id = source_combo.currentData()
            if source_id:
                if not zone_combo.currentData():
                    return
                self.rgb_gpu_routes[gpu_id] = {"controller": source_id, "zone": zone_combo.currentData()}
                # Selection is explicit in this dialog, never inferred from a profile.
                self.rgb_selected_devices.add(source_id)
                self.rgb_selected_devices.add(gpu_id)
            else:
                self.rgb_gpu_routes[gpu_id] = {"controller": "", "zone": ""}
            from .gpu_support_sync import KEY
            from .gpu_motion import save as save_gpu_motion
            from .gpu_motion_editor import GpuMotionEditor
            sync = dialog.findChild(QCheckBox, "gpuSupportSync")
            editor = dialog.findChild(GpuMotionEditor, "gpuMotionEditor")
            if hasattr(self, "settings"):
                self.settings.setValue(KEY, sync.isChecked())
                save_gpu_motion(self, editor.values())
                self.settings.sync()
                self.rgb_last_effect_request_signature = None
            self.select_gpu_route_sources()
            self.save_rgb_workspace()
            self.rebuild_rgb_workspace()
            dialog.accept()
            if edit_leds and source_id:
                source = next((device for device in sources
                               if self.openrgb_stable_ids.get(device.index) == source_id), None)
                if source is not None:
                    configure_gpu_header(self, target_device, source, zone_combo.currentData())

        save.clicked.connect(lambda _checked=False: commit())
        edit.clicked.connect(lambda _checked=False: commit(True))
        from modules.pc_case_profiles.v1_5.inline_editor import present_editor
        if not present_editor(self, dialog): dialog.exec()

    def build_gpu_lighting_dialog(self, target_device, gpu_id, sources):
        tr = self.tr_static
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Grafikkarte: Steuerweg und LEDs"))
        dialog.setMinimumWidth(700)
        layout = QVBoxLayout(dialog)
        info = QLabel(tr(
            "Native GPU-Effekte benötigen kein Kabel. Manuelle LED-Zahlen gehören zum angeschlossenen 5-V-ARGB-Kanal."
        ))
        info.setWordWrap(True)
        layout.addWidget(info)
        gpu_name = QLabel(f'{tr("Komponente")}: {target_device.name} · {target_device.reported_led_count}')
        gpu_name.setTextFormat(Qt.TextFormat.PlainText)
        gpu_name.setMinimumHeight(22)
        gpu_name.setWordWrap(True)
        layout.addWidget(gpu_name)
        source_combo = QComboBox()
        source_combo.addItem(tr("Automatisch: native GPU-Hardwareeffekte"), "")
        if any(mode.casefold() == "external control" for mode in target_device.modes):
            for source in sources:
                source_combo.addItem(self.rgb_device_display_name(source),
                                     self.openrgb_stable_ids[source.index])
        route = self.rgb_gpu_routes.get(gpu_id, {})
        source_combo.setObjectName("gpuController")
        source_combo.setCurrentIndex(max(0, source_combo.findData(route_source(route))))
        layout.addWidget(source_combo)
        layout.addWidget(QLabel(tr("ARGB-Anschluss")))
        zone_combo = QComboBox()
        zone_combo.setObjectName("gpuZone")
        layout.addWidget(zone_combo)
        warning = QLabel(tr(
            "Wähle Controller und ARGB-Anschluss. Effekte nutzen eigene Zonenlängen; LED-Zahlen und Steuerwege bleiben beim Profilwechsel erhalten."
        ))
        warning.setWordWrap(True)
        layout.addWidget(warning)
        from .gpu_support_sync import enabled
        sync = QCheckBox(tr("GPU und Halterung synchronisieren"))
        sync.setObjectName("gpuSupportSync"); sync.setChecked(enabled(self))
        layout.addWidget(sync)
        note = QLabel(tr("Verwendet den zugeordneten ARGB-Anschluss der GPU-Halterung. Beide Geräte müssen ausgewählt sein; LED-Zahlen und Sichttests bleiben getrennt."))
        note.setWordWrap(True); layout.addWidget(note)
        from .gpu_motion_editor import GpuMotionEditor
        motion = GpuMotionEditor(self, gpu_id, dialog)
        dialog.finished.connect(lambda _result: motion.clear_live_preview())
        motion.set_sync_enabled(sync.isChecked())
        sync.toggled.connect(motion.set_sync_enabled)
        layout.addWidget(motion)
        edit = QPushButton(tr("LED-Anzahl am ARGB-Anschluss ändern"))
        layout.addWidget(edit)
        buttons = QDialogButtonBox()
        save = buttons.addButton(tr("Steuerweg speichern"), QDialogButtonBox.ButtonRole.AcceptRole)
        motion.calibration_saved = save.click
        buttons.addButton(tr("Abbrechen"), QDialogButtonBox.ButtonRole.RejectRole)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        def update_zone():
            previous = zone_combo.currentData()
            zone_combo.clear()
            zone_combo.addItem(tr("Bitte ARGB-Anschluss auswählen"), "")
            source = next((source for source in sources if self.openrgb_stable_ids[source.index] == source_combo.currentData()), None)
            if source is not None:
                for name in source.zones:
                    zone_combo.addItem(name, name)
                target = route_zone(route, source) if route_source(route) == source_combo.currentData() else previous
                zone_combo.setCurrentIndex(max(0, zone_combo.findData(target)))
            zone_combo.setEnabled(source is not None)
            motion.set_route(source_combo.currentData(), zone_combo.currentData())
            update_buttons()

        zone_combo.currentIndexChanged.connect(
            lambda _index: motion.set_route(source_combo.currentData(), zone_combo.currentData()))

        def update_buttons():
            valid = bool(source_combo.currentData() and zone_combo.currentData())
            edit.setEnabled(valid)
            save.setEnabled(valid or not source_combo.currentData())

        source_combo.currentIndexChanged.connect(lambda _index: update_zone())
        zone_combo.currentIndexChanged.connect(lambda _index: update_buttons())
        update_zone()
        return dialog, source_combo, zone_combo, save, edit

    def render_gpu_controller_frame(self, stable_id, device, config, count, sizes, elapsed):
        from .gpu_motion import load as load_gpu_motion
        overrides = gpu_zone_overrides(self, stable_id, device, config)
        gpu_zones, sync_counts = set(overrides), {}
        gpu_roles = {zone: "gpu" for zone in overrides}
        from .gpu_support_sync import pair
        linked = pair(self, config)
        if linked is not None:
            for role, (controller, zone) in (("gpu", linked["gpu"]), ("support", linked["support"])):
                if controller == stable_id:
                    overrides[zone] = linked["config"]
                    gpu_zones.add(zone); sync_counts[zone] = linked["count"]
                    gpu_roles[zone] = role
        from .led_topology_store import paths, direction, case_rectangles
        declared = paths(self).get(stable_id, {})
        movement = direction(self)
        rectangles = case_rectangles(self, stable_id) if any(
            path.get("direction", movement) != "local" for path in declared.values()) else {}
        return render_zone_frame(config, count, sizes, device.zones, overrides, elapsed,
                                 paths=declared, direction=movement, rectangles=rectangles,
                                 gpu_zones=gpu_zones, sync_counts=sync_counts,
                                 gpu_motion=getattr(self, "rgb_gpu_motion_preview", None) or load_gpu_motion(self),
                                 gpu_elapsed=getattr(self, "rgb_gpu_visual_elapsed", elapsed),
                                 gpu_roles=gpu_roles)

    def restore_gpu_profile_hardware(self, rgb, startup=False):
        """The current physical cabling/counts take precedence over design snapshots."""
        current = normalize_gpu_routes(self.rgb_gpu_routes)
        imported = normalize_gpu_routes(rgb.get("studio_gpu_routes", {}))
        self.rgb_gpu_routes = {**imported, **current}
        incoming = rgb.get("studio_zone_configurations")
        if incoming is not None:
            from rgb_devices import normalize_zone_configurations
            restored = normalize_zone_configurations(incoming)
            for route in current.values():
                controller = route_source(route)
                if controller in self.rgb_zone_configurations:
                    saved = self.rgb_zone_configurations[controller]
                    name = route.get("zone", "")
                    retained = {key: dict(value) for key, value in saved.items()
                                if not name or key.casefold() == name.casefold()}
                    restored[controller] = {**saved, **restored.get(controller, {}), **retained}
            self.rgb_zone_configurations = retain_manual_headers(self, restored)

    def select_gpu_route_sources(self):
        from dataclasses import replace
        for gpu_id, route in normalize_gpu_routes(self.rgb_gpu_routes).items():
            source = route_source(route)
            if gpu_id in self.rgb_selected_devices and source:
                self.rgb_selected_devices.add(source)
            zone = route.get("zone", "")
            if zone:
                self.rgb_layout_slots = [replace(slot, connection=zone)
                                         if slot.position == "gpu" and gpu_id in slot.device_ids else slot
                                         for slot in self.rgb_layout_slots]

    def migrate_flori_gpu_header(self):
        """One-time owner-confirmed personal wiring; never a board-wide inference."""
        if str(self.settings.value("rgb_studio/layout_profile", "")) != "flori":
            return
        key = "rgb_studio/flori_gpu_header_342982"
        if self.settings.value(key, False, type=bool):
            return
        gpus = [d for d in self.openrgb_devices if "sapphire" in d.name.casefold()
                and "9070" in d.name and not d.supports_direct]
        sources = [d for d in self.openrgb_devices if d.supports_direct
                   and "msi" in d.name.casefold() and "mystic" in d.name.casefold()
                   and any("".join(z.split()).casefold() == "jargb1" for z in d.zones)]
        if len(gpus) != 1 or len(sources) != 1:
            return
        gpu, source = gpus[0], sources[0]
        gpu_id, source_id = self.openrgb_stable_ids.get(gpu.index), self.openrgb_stable_ids.get(source.index)
        if not gpu_id or not source_id:
            return
        existing = normalize_gpu_routes(self.rgb_gpu_routes).get(gpu_id, {})
        if existing and (route_source(existing) != source_id or existing.get("zone")):
            self.settings.setValue(key, True)
            return
        zone = next(z for z in source.zones if "".join(z.split()).casefold() == "jargb1")
        self.rgb_gpu_routes[gpu_id] = {"controller": source_id, "zone": zone}
        self.rgb_selected_devices.update((gpu_id, source_id))
        configuration = self.rgb_zone_configurations.get(source_id, {})
        for name, values in configuration.items():
            if name.casefold() == zone.casefold() and values.get("units") == 3 and values.get("leds_per_unit") in (80, 90):
                # Owner entered 80/90 for ONE GPU, not three chained devices.
                configuration[name] = {"units": 1, "leds_per_unit": values["leds_per_unit"]}
        from dataclasses import replace
        self.rgb_layout_slots = [replace(slot, connection="JARGB_V2_1")
                                 if slot.position == "gpu" else slot for slot in self.rgb_layout_slots]
        self.settings.setValue(key, True)
        self.save_rgb_workspace()
