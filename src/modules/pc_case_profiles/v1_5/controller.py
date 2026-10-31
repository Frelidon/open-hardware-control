#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Host mixin for local case profiles and schematic template application."""

from __future__ import annotations
from dataclasses import replace
import json

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from mainboard_fan_control import CurveState as MainboardCurveState
from rgb_devices import (
    RGBGroup,
    RGBLayoutSlot,
    normalize_group_assignments,
    normalize_layout_slots,
    normalize_rgb_groups,
    normalize_layout_scale,
    normalize_zone_configurations,
)

from .catalog import CASE_TEMPLATES, DEFAULT_CASE_ID, case_template
from .profiles import encode_profiles, new_profile_id, normalize_hardware_snapshot
from .case_geometry import mount_point


class PcCaseProfilesMixin:
    """Connect pure case/profile data to the existing RGB layout host API."""

    def resize_rgb_layout_slot(self, slot_id, scale):
        slot = next((s for s in self.rgb_layout_slots if (s.slot_id or s.position) == slot_id), None)
        if slot is None:
            return
        value = normalize_layout_scale(scale)
        self.rgb_layout_slots = [replace(s, scale=value) if s is slot else s for s in self.rgb_layout_slots]
        self.save_rgb_workspace()
        self.refresh_rgb_layout_editor()
        self.log_message(f"RGB-LAYOUT: visual-scale · slot={slot_id} · factor={value:.3f} · hardware unchanged")

    def reset_chassis_fan_assignments(self) -> None:
        """Forget physical chassis mappings while preserving reusable curves."""
        if self.mainboard_calibration_channel_id:
            self.show_error("Eine Lüfterprüfung läuft noch. Warte bitte bis zur sicheren Wiederherstellung.")
            return
        answer = QMessageBox.question(
            self,
            self.tr_static("Lüfterzuordnungen zurücksetzen?"),
            self.tr_static(
                "Alle Gehäuseplätze, Bestätigungen und Aktivierungen werden zurückgesetzt. "
                "Gespeicherte Lüfterkurven bleiben erhalten. Eine laufende OHC-Regelung wird beendet "
                "und die Lüfter werden vorher an Firmware/BIOS zurückgegeben."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if self.mainboard_control_active:
            self.toggle_mainboard_master_control(False, silent=True)
        channels = self.chassis_mainboard_channels()
        for channel in channels:
            profile = self.mainboard_profile_for(channel)
            profile["name"] = channel.display_name
            profile["calibrated"] = False
            profile["enabled"] = False
            self.mainboard_curve_states[channel.stable_id] = MainboardCurveState()
        self.mainboard_layout_assignments.clear()
        self.mainboard_selected_channel_id = channels[0].stable_id if channels else ""
        self.mainboard_expanded_channel_id = ""
        self.cooling_layout_selected_slot_id = ""
        self.save_mainboard_fan_settings()
        if hasattr(self, "cooling_layout_diagram"):
            self.cooling_layout_diagram.set_channel_assignments({})
        self.refresh_mainboard_fan_table()
        self.update_thermalright_cooling_ui()
        self.refresh_rgb_layout_editor()
        self.footer_status.setText(self.tr_static("Alle Lüfterzuordnungen wurden zurückgesetzt"))
        self.log_message(
            f"MAINBOARD-FAN: Gehäusezuordnung zurückgesetzt · {len(channels)} Kanal/Kanäle · "
            "Kalibrierung und Aktivierung entfernt · Kurven erhalten"
        )

    def select_cooling_layout_slot(self, slot_id: str) -> None:
        self.cooling_layout_selected_slot_id = str(slot_id)
        if hasattr(self, "assistant_slot_label"):
            slot = next((item for item in self.rgb_layout_slots if (item.slot_id or item.position) == slot_id), None)
            self.assistant_slot_label.setText(f"Ausgewählter Einbauplatz: {slot.name}" if slot else f"Einbauplatz: {slot_id}")

    def _fan_layout_slot(self, slot_id: str) -> RGBLayoutSlot | None:
        slot = next((item for item in self.rgb_layout_slots if (item.slot_id or item.position) == slot_id), None)
        if slot is None:
            return None
        if slot.position == "pump":
            return slot
        if slot.position not in {"top", "front", "side", "bottom", "rear"}:
            return None
        if slot.count <= 0 or slot.size_mm <= 0:
            return None
        return slot

    def case_mappable_mainboard_channels(self):
        """Expose every reported connector to the settings-only case mapper.

        The calibration assistant remains chassis-only.  The case page also
        needs CPU_FAN and PUMP_FAN so an AIO pump and radiator can be recorded
        in a PC profile without enabling or writing either channel.
        """

        return sorted(self.mainboard_channels.values(), key=lambda channel: channel.index)

    def sync_selected_rgb_case_profile_pwm_assignments(self) -> bool:
        """Persist current PWM topology into the selected local PC profile."""

        profile_id = str(self.settings.value("rgb_studio/layout_profile", "") or "")
        combo = getattr(self, "rgb_layout_profile_combo", None)
        if combo is not None and str(combo.currentData() or "").startswith("user-"):
            profile_id = str(combo.currentData())
        if not profile_id.startswith("user-"):
            return False
        index = next(
            (i for i, item in enumerate(getattr(self, "rgb_case_profiles", ())) if item.get("id") == profile_id),
            -1,
        )
        if index < 0:
            return False
        profile = dict(self.rgb_case_profiles[index])
        hardware = normalize_hardware_snapshot(profile.get("hardware", {})) or self._profile_hardware_snapshot()
        slot_ids = {slot.slot_id or slot.position for slot in self.rgb_layout_slots}
        hardware["pwm_assignments"] = {
            key: value for key, value in self.mainboard_layout_assignments.items()
            if value in slot_ids
        }
        hardware["aio_channels"] = {
            role: getattr(self, f"thermalright_{role}_channel_id", "")
            for role in ("pump", "radiator")
        }
        profile["hardware"] = normalize_hardware_snapshot(hardware)
        self.rgb_case_profiles[index] = profile
        self.persist_rgb_case_profiles()
        return True

    def migrate_reference_pc_fan_assignments(self) -> bool:
        """Store the owner-confirmed MSI wiring once, matched by board labels.

        No pwm index is guessed.  Existing assignments win, and the migration
        never runs on another mainboard model.
        """

        marker = "mainboard_fans/flori_reference_pwm_v1"
        if self.settings.value(marker, False, type=bool):
            return False
        dmi = getattr(self, "mainboard_dmi", None)
        if dmi is None or not dmi.is_msi_mag_x870_tomahawk:
            return False
        expected = {
            "CPU Fan": "radiator-top",
            "Pump Fan": "pump",
            "System Fan #1": "fan-rear",
            "System Fan #2": "fans-side",
            "System Fan #4": "fans-front",
            "System Fan #6": "fans-psu-shroud",
        }
        slots = {slot.slot_id or slot.position for slot in getattr(self, "rgb_layout_slots", ())}
        resolved = {}
        for reported_name, slot_id in expected.items():
            matches = [
                channel for channel in self.mainboard_channels.values()
                if channel.display_name.casefold() == reported_name.casefold()
            ]
            if len(matches) != 1 or slot_id not in slots:
                return False
            resolved[matches[0].stable_id] = slot_id
        used_slots = set(self.mainboard_layout_assignments.values())
        changed = False
        for channel_id, slot_id in resolved.items():
            if channel_id in self.mainboard_layout_assignments or slot_id in used_slots:
                continue
            self.mainboard_layout_assignments[channel_id] = slot_id
            used_slots.add(slot_id)
            changed = True
        pump_id = next(key for key, value in resolved.items() if value == "pump")
        radiator_id = next(key for key, value in resolved.items() if value == "radiator-top")
        if not self.thermalright_pump_channel_id:
            self.thermalright_pump_channel_id = pump_id
            changed = True
        if not self.thermalright_radiator_channel_id:
            self.thermalright_radiator_channel_id = radiator_id
            changed = True
        self.settings.setValue("thermalright_cooling/pump_channel", self.thermalright_pump_channel_id)
        self.settings.setValue("thermalright_cooling/radiator_channel", self.thermalright_radiator_channel_id)
        self.settings.setValue(marker, True)
        self.save_mainboard_fan_settings()
        self.sync_selected_rgb_case_profile_pwm_assignments()
        self.log_message(
            "MAINBOARD-FAN: bestätigte MSI MAG X870 TOMAHAWK WIFI-Zuordnung im aktiven PC-Profil gespeichert · "
            "CPU_FAN=Radiator · PUMP_FAN=Pumpe · SYS_FAN1/2/4/6=Gehäusegruppen · keine Hardwareänderung"
        )
        return changed

    def assign_selected_channel_to_cooling_slot(self) -> None:
        channel = self.selected_mainboard_channel()
        slot = self._fan_layout_slot(self.cooling_layout_selected_slot_id)
        if channel is None or slot is None:
            self.show_error("Bitte zuerst einen Mainboard-Anschluss und anschließend einen Lüfter- oder Pumpenplatz in der Grafik auswählen.")
            return
        slot_id = slot.slot_id or slot.position
        conflicts = [
            (channel_id, mapped_slot)
            for channel_id, mapped_slot in self.mainboard_layout_assignments.items()
            if (mapped_slot == slot_id and channel_id != channel.stable_id)
            or (channel_id == channel.stable_id and mapped_slot != slot_id)
        ]
        if conflicts:
            answer = QMessageBox.question(
                self,
                self.tr_static("Vorhandene Lüfterzuordnung ersetzen?"),
                self.tr_static(
                    "Der Anschluss oder Einbauplatz ist bereits zugeordnet. Soll die bisherige Zuordnung ersetzt werden?"
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        # Moving an AIO connector or replacing its slot must also forget the
        # old role; otherwise cooling would keep addressing a reassigned fan,
        # or a connector moved to the pump could retain both AIO roles.
        affected_channels = {channel.stable_id, *(key for key, _slot in conflicts)}
        for role in ("pump", "radiator"):
            attribute = f"thermalright_{role}_channel_id"
            if getattr(self, attribute, "") in affected_channels:
                setattr(self, attribute, "")
                self.settings.setValue(f"thermalright_cooling/{role}_channel", "")
        for channel_id, slot_id in list(self.mainboard_layout_assignments.items()):
            if slot_id == (slot.slot_id or slot.position) and channel_id != channel.stable_id:
                self.mainboard_layout_assignments.pop(channel_id, None)
        self.mainboard_layout_assignments[channel.stable_id] = slot.slot_id or slot.position
        if slot.position == "pump":
            self.thermalright_pump_channel_id = channel.stable_id
            self.settings.setValue("thermalright_cooling/pump_channel", channel.stable_id)
        elif slot.position == "top" or (slot.slot_id or "") == "radiator-top":
            self.thermalright_radiator_channel_id = channel.stable_id
            self.settings.setValue("thermalright_cooling/radiator_channel", channel.stable_id)
        profile = self.mainboard_profile_for(channel)
        if not str(profile.get("name", "")).strip() or str(profile.get("name", "")) == channel.display_name:
            profile["name"] = slot.name
        self.save_mainboard_fan_settings()
        self.sync_selected_rgb_case_profile_pwm_assignments()
        for diagram_name in ("cooling_layout_diagram", "assistant_layout_diagram"):
            if hasattr(self, diagram_name):
                getattr(self, diagram_name).set_channel_assignments(self.mainboard_layout_assignments)
        self.refresh_chassis_assistant_summary()
        self.refresh_mainboard_fan_table()
        self.log_message(f"MAINBOARD-FAN-LAYOUT: {channel.stable_id} → {slot.name} ({slot.slot_id or slot.position})")
        self.refresh_rgb_layout_editor()
        self.footer_status.setText(f"Gehäusezuordnung gespeichert: {channel.stable_id} → {slot.name}")

    def refresh_chassis_assistant_summary(self) -> None:
        layout = getattr(self, "assistant_summary_layout", None)
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        for channel in self.chassis_mainboard_channels():
            slot_id = self.mainboard_layout_assignments.get(channel.stable_id, "")
            slot = next((item for item in self.rgb_layout_slots if (item.slot_id or item.position) == slot_id), None)
            position = slot.name if slot else "noch nicht zugeordnet"
            profile = self.mainboard_profile_for(channel)
            layout.addWidget(QLabel(f"PWM {channel.index}  ·  {profile.get('name') or channel.display_name}  →  {position}"))

    def assistant_continue_with_next_fan(self) -> None:
        combo = getattr(self, "assistant_channel_combo", None)
        wizard = getattr(self, "chassis_fan_wizard", None)
        if combo is None or wizard is None or combo.count() < 1:
            return
        current = combo.currentIndex()
        ordered = [((current + offset) % combo.count()) for offset in range(1, combo.count() + 1)]
        target = next((
            index for index in ordered
            if str(combo.itemData(index) or "") not in self.mainboard_layout_assignments
            or not bool(self.mainboard_fan_profiles.get(str(combo.itemData(index) or ""), {}).get("calibrated", False))
        ), ordered[0])
        combo.setCurrentIndex(target)
        self.cooling_layout_selected_slot_id = ""
        if hasattr(self, "assistant_slot_label"):
            self.assistant_slot_label.setText("Ausgewählter Einbauplatz: noch keiner")
        wizard.setCurrentId(1)

    def assistant_select_channel(self, channel_id: str) -> None:
        self.mainboard_selected_channel_id = str(channel_id)
        self.load_selected_mainboard_fan_editor()
        if hasattr(self, "assistant_channel_status"):
            channel = self.selected_mainboard_channel()
            self.assistant_channel_status.setText(
                f"Aktueller Testkanal: {channel.display_name}" if channel else "Kein Kanal ausgewählt"
            )

    def open_rgb_layout_slot_device_editor(self, slot_id: str) -> None:
        """Select a mapped component and open its real LED editor on double-click."""

        slot = next(
            (
                item for item in self.rgb_layout_slots
                if (item.slot_id or item.position) == str(slot_id)
            ),
            None,
        )
        if slot is None:
            return
        self.focus_rgb_layout_slot(str(slot_id))
        if not slot.device_ids:
            # An unassigned case block still has an editable topology.  Avoid
            # touching the live OpenRGB inventory until a device is actually
            # mapped; this also keeps the editor usable while detection is
            # still starting up.
            self.edit_selected_rgb_layout_slot()
            return
        ram_devices = [
            device for device in getattr(self, "openrgb_devices", ())
            if getattr(self, "openrgb_stable_ids", {}).get(device.index) in slot.device_ids
            and self.is_rgb_ram_device(device)
        ]
        if slot.position == "ram" and ram_devices:
            # The case contains one logical memory bank.  Keep every module's
            # stable ID for persistence and transport, but never make users
            # configure otherwise identical DIMMs through separate dialogs.
            member_ids = {
                self.openrgb_stable_ids.get(device.index, f"openrgb:index-{device.index}")
                for device in ram_devices
            }
            self.rgb_selected_devices.update(member_ids)
            self.save_rgb_workspace()
            self.rebuild_rgb_workspace()
            self.set_rgb_devices_effects_expanded(True)
            self.configure_openrgb_ram_bank(ram_devices)
            return
        if getattr(self, "case_inspector", None) is not None:
            from .component_editor import open_component
            open_component(self, slot)
            return
        logical_by_id = {
            str(item["id"]): item
            for item in self.rgb_logical_devices()
            if str(item.get("id", "")) in slot.device_ids
        }
        if not logical_by_id:
            self.edit_selected_rgb_layout_slot()
            return
        device_id = next(iter(logical_by_id))
        if len(logical_by_id) > 1:
            choices = [
                f"{item.get('title') or candidate_id} · {item.get('subtitle') or item.get('backend') or ''}".rstrip(" ·")
                for candidate_id, item in logical_by_id.items()
            ]
            choice, accepted = QInputDialog.getItem(
                self,
                self.tr_static("Zugeordnetes RGB-Gerät bearbeiten"),
                self.tr_static("Gerät"),
                choices,
                0,
                False,
            )
            if not accepted:
                return
            device_id = tuple(logical_by_id)[choices.index(choice)]

        logical = logical_by_id[device_id]
        if bool(logical.get("writable", False)):
            self.rgb_selected_devices = {device_id}
            self.save_rgb_workspace()
            self.rebuild_rgb_workspace()
        self.set_rgb_devices_effects_expanded(True)
        if hasattr(self, "rgb_page_scroll") and hasattr(self, "rgb_devices_effects_panel"):
            self.rgb_page_scroll.ensureWidgetVisible(self.rgb_devices_effects_panel, 24, 24)

        openrgb_device = next(
            (
                device for device in self.openrgb_devices
                if self.openrgb_stable_ids.get(device.index) == device_id
            ),
            None,
        )
        if openrgb_device is None:
            self.rgb_layout_status_label.setText(self.tr_static(
                "Gerät ausgewählt · Effekte und Hardwaremodi sind unten geöffnet"
            ))
            return
        if hasattr(self, "openrgb_device_combo"):
            combo_index = self.openrgb_device_combo.findData(openrgb_device.index)
            if combo_index >= 0:
                self.openrgb_device_combo.setCurrentIndex(combo_index)
        if not openrgb_device.supports_direct:
            if openrgb_device.device_type.casefold() == "gpu" or "sapphire" in openrgb_device.name.casefold():
                self.configure_gpu_lighting(openrgb_device)
                return
            QMessageBox.information(
                self,
                self.tr_static("LED-Anzahl nicht frei einstellbar"),
                self.tr_static(
                    "Dieses Gerät bietet OpenRGB keinen Direct Mode. OHC kann deshalb nur die gemeldeten Hardwaremodi verwenden und keine zusätzlichen einzeln animierten LEDs erfinden."
                ),
            )
            return
        self.rgb_layout_status_label.setText(self.tr_static(
            "Gerät ausgewählt · LED-Zonen werden zur Bearbeitung geöffnet"
        ))
        self.configure_openrgb_zones(openrgb_device)

    def personal_layout_needs_cooler_refresh(self, active: bool) -> bool:
        return bool(
            active and self.is_thermalright_cooling()
            and any("kraken" in f"{slot.name} {slot.connection}".casefold() for slot in self.rgb_layout_slots)
        )

    def build_rgb_case_profile_controls(self, aio_name: str) -> tuple[QVBoxLayout, QVBoxLayout]:
        case_actions = QVBoxLayout()
        case_actions.setSpacing(7)
        case_actions.addWidget(QLabel("Gehäuse"))
        self.rgb_case_template_combo = QComboBox()
        self.rgb_case_template_combo.setProperty("i18nTranslateItems", False)
        for template in CASE_TEMPLATES:
            self.rgb_case_template_combo.addItem(
                template.title + (" · ✓" if template.exact else " · ◇"), template.case_id
            )
        self.rgb_case_template_combo.setCurrentIndex(max(0, self.rgb_case_template_combo.findData(self.rgb_case_template_id)))
        self.rgb_case_template_combo.currentIndexChanged.connect(self.preview_rgb_case_template)
        apply_case = QPushButton("Gehäusevorlage anwenden")
        apply_case.clicked.connect(self.apply_rgb_case_template)
        source = QPushButton("Herstellerquelle öffnen")
        source.clicked.connect(self.open_rgb_case_template_source)
        case_actions.addWidget(self.rgb_case_template_combo, 1)
        case_buttons = QHBoxLayout()
        case_buttons.addWidget(apply_case)
        case_buttons.addWidget(source)
        case_actions.addLayout(case_buttons)
        case_actions.addWidget(QLabel("CPU-Kühlung in der Ansicht"))
        self.rgb_case_cooling_combo = QComboBox()
        self.rgb_case_cooling_combo.addItem("Automatisch erkannt", "auto")
        self.rgb_case_cooling_combo.addItem("Wasserkühlung (AIO)", "aio")
        self.rgb_case_cooling_combo.addItem("Luftkühlung", "air")
        cooling_visual = str(self.settings.value("rgb_studio/cooling_visual", "auto") or "auto")
        self.rgb_case_cooling_combo.setCurrentIndex(max(0, self.rgb_case_cooling_combo.findData(cooling_visual)))
        self.rgb_case_cooling_combo.currentIndexChanged.connect(self.update_rgb_case_cooling_visual)
        case_actions.addWidget(self.rgb_case_cooling_combo)

        profile_actions = QVBoxLayout()
        profile_actions.setSpacing(7)
        profile_actions.addWidget(QLabel("Profil"))
        self.rgb_layout_profile_combo = QComboBox()
        self.rgb_layout_profile_combo.setProperty("i18nTranslateItems", False)
        self.rgb_layout_profile_combo.addItem(f"Frelidon PC · Thermaltake Retro 360 TG / {aio_name}", "flori")
        for profile in self.rgb_case_profiles:
            self.rgb_layout_profile_combo.addItem(str(profile["name"]), str(profile["id"]))
        profile_actions.addWidget(self.rgb_layout_profile_combo)
        profile_buttons = QGridLayout()
        profile_buttons.setSpacing(7)
        for index, (caption, callback) in enumerate((
            ("Thermaltake-Profil neu laden", self.load_builtin_rgb_layout_profile),
            ("+ Neues PC-Profil", self.create_rgb_case_profile),
            ("PC-Profil speichern", self.save_selected_rgb_case_profile),
            ("PC-Profil löschen", self.delete_selected_rgb_case_profile),
        )):
            button = QPushButton(caption)
            button.clicked.connect(callback)
            profile_buttons.addWidget(button, index // 2, index % 2)
        self.rgb_layout_profile_combo.currentIndexChanged.connect(self.load_selected_rgb_case_profile)
        profile_actions.addLayout(profile_buttons)
        return case_actions, profile_actions

    def rgb_layout_slots_payload(self) -> list[dict[str, object]]:
        return [{
            "position": slot.position, "name": slot.name, "count": slot.count,
            "group_id": slot.group_id, "connection": slot.connection,
            "device_ids": list(slot.device_ids), "slot_id": slot.slot_id,
            "x": slot.x, "y": slot.y, "airflow": slot.airflow, "size_mm": slot.size_mm, "scale": slot.scale,
            "visual_kind": slot.visual_kind, "gpu_visual": slot.gpu_visual,
        } for slot in self.rgb_layout_slots]

    def persist_rgb_case_profiles(self) -> None:
        self.settings.setValue("rgb_studio/case_profiles", encode_profiles(self.rgb_case_profiles))
        self.settings.sync()

    def _profile_snapshot(self, ident: str, name: str) -> dict[str, object]:
        return {
            "id": ident, "name": name,
            "case_id": str(self.rgb_case_template_combo.currentData() or DEFAULT_CASE_ID),
            "cooling_visual": str(self.rgb_case_cooling_combo.currentData() or "auto"),
            "groups": [{"id": group.group_id, "name": group.name} for group in self.rgb_groups],
            "slots": self.rgb_layout_slots_payload(),
            "hardware": self._profile_hardware_snapshot(),
        }

    def _profile_hardware_snapshot(self) -> dict[str, object]:
        """Capture only settings topology; never read or write live hardware."""
        from modules.rgb_studio.v1_15.argb_store import manual_headers
        from modules.rgb_studio.v1_15.fan_profiles import profile_for_slot
        from modules.rgb_studio.v1_15.gpu_routing import normalize_gpu_routes
        from modules.rgb_studio.v1_15.led_topology_store import direction, paths
        from modules.rgb_studio.v1_15.slot_routes import slot_routes

        slot_ids = {slot.slot_id or slot.position for slot in self.rgb_layout_slots}
        routes = {key: value for key, value in slot_routes(self).items() if key in slot_ids}
        for slot in self.rgb_layout_slots:
            key = slot.slot_id or slot.position
            route = routes.get(key, {})
            if len(slot.device_ids) > 1 and route.get("controller") in slot.device_ids:
                routes.pop(key, None)
        fans = {}
        for slot in self.rgb_layout_slots:
            key = slot.slot_id or slot.position
            resolved = profile_for_slot(self, slot)
            if resolved.get("brand") or resolved.get("model") or resolved.get("leds_per_fan"):
                fans[key] = resolved
        controllers = {route["controller"] for route in routes.values() if route.get("controller")}
        devices = {device for slot in self.rgb_layout_slots for device in slot.device_ids}
        gpu_routes = normalize_gpu_routes(self.rgb_gpu_routes)
        devices.update(gpu_routes)
        controllers.update(
            route["controller"] for route in gpu_routes.values() if route.get("controller")
        )
        relevant = controllers | devices
        snapshot = {
            "slot_routes": routes,
            "fan_profiles": fans,
            "zone_configurations": {
                key: value for key, value in self.rgb_zone_configurations.items() if key in relevant
            },
            "gpu_routes": gpu_routes,
            "led_paths": {key: value for key, value in paths(self).items() if key in relevant},
            "manual_headers": {
                key: value for key, value in manual_headers(self).items() if key in relevant
            },
            "group_assignments": {
                key: value for key, value in self.rgb_group_assignments.items() if key in devices
            },
            "device_aliases": {
                key: value for key, value in self.rgb_device_aliases.items() if key in devices
            },
            "selected_devices": sorted(self.rgb_selected_devices & relevant),
            "pwm_assignments": {
                key: value for key, value in self.mainboard_layout_assignments.items()
                if value in slot_ids
            },
            "aio_channels": {
                role: getattr(self, f"thermalright_{role}_channel_id", "")
                for role in ("pump", "radiator")
            },
            "case_direction": direction(self),
        }
        return normalize_hardware_snapshot(snapshot)

    def _restore_profile_hardware(self, profile: dict[str, object]) -> None:
        """Restore a validated topology without authorizing a hardware write."""
        hardware = normalize_hardware_snapshot(profile.get("hardware", {}))
        self._restore_profile_aio_channels(hardware)
        if not hardware:
            return
        self.settings.setValue(
            "rgb_studio/slot_argb_routes_v1",
            json.dumps(hardware["slot_routes"], ensure_ascii=False),
        )
        self.settings.setValue(
            "rgb_studio/fan_profiles_v1",
            json.dumps(hardware["fan_profiles"], ensure_ascii=False),
        )
        self.settings.setValue(
            "rgb_studio/led_paths_v1",
            json.dumps(hardware["led_paths"], ensure_ascii=False),
        )
        self.settings.setValue(
            "rgb_studio/manual_zone_counts",
            json.dumps(hardware["manual_headers"], ensure_ascii=False),
        )
        self.settings.setValue("rgb_studio/case_effect_direction_v1", hardware["case_direction"])
        self.rgb_zone_configurations = normalize_zone_configurations(hardware["zone_configurations"])
        self.rgb_gpu_routes = dict(hardware["gpu_routes"])
        self.rgb_group_assignments = normalize_group_assignments(
            hardware["group_assignments"], self.rgb_groups,
        )
        self.rgb_device_aliases.update(hardware["device_aliases"])
        self.rgb_selected_devices = set(hardware["selected_devices"])
        self.mainboard_layout_assignments = dict(hardware["pwm_assignments"])
        self.save_mainboard_fan_settings()

    def _restore_profile_aio_channels(self, hardware: dict[str, object]) -> None:
        """Load only this profile's explicit or unambiguous legacy AIO roles."""
        known = set(getattr(self, "mainboard_channels", {}))
        roles = hardware.get("aio_channels")
        if roles is None:
            roles = {}
            assignments = hardware.get("pwm_assignments", {})
            for role in ("pump", "radiator"):
                slot_ids = {
                    slot.slot_id or slot.position for slot in self.rgb_layout_slots
                    if (slot.position == "pump" if role == "pump" else slot.slot_id == "radiator-top")
                }
                candidates = {
                    key for key, slot_id in assignments.items()
                    if key in known and slot_id in slot_ids
                }
                roles[role] = next(iter(candidates)) if len(candidates) == 1 else ""
        pump = roles.get("pump", "")
        radiator = roles.get("radiator", "")
        self.thermalright_pump_channel_id = pump if pump in known else ""
        self.thermalright_radiator_channel_id = (
            radiator if radiator in known and radiator != self.thermalright_pump_channel_id else ""
        )
        self.settings.setValue("thermalright_cooling/pump_channel", self.thermalright_pump_channel_id)
        self.settings.setValue("thermalright_cooling/radiator_channel", self.thermalright_radiator_channel_id)
        self.settings.sync()

    def create_rgb_case_profile(self) -> None:
        name, accepted = QInputDialog.getText(
            self, "Neues PC-Profil", "Name für die aktuelle Gehäuse- und Komponentenansicht"
        )
        clean_name = " ".join(name.split())[:64]
        if not accepted or not clean_name:
            return
        profile = self._profile_snapshot(new_profile_id(clean_name), clean_name)
        self.rgb_case_profiles.append(profile)
        self.persist_rgb_case_profiles()
        self.rgb_layout_profile_combo.addItem(clean_name, profile["id"])
        self.rgb_layout_profile_combo.setCurrentIndex(self.rgb_layout_profile_combo.findData(profile["id"]))
        self.rgb_layout_status_label.setText(f"PC-Profil „{clean_name}“ wurde lokal angelegt")

    def save_selected_rgb_case_profile(self) -> None:
        profile_id = str(self.rgb_layout_profile_combo.currentData() or "")
        if profile_id == "flori":
            self.create_rgb_case_profile()
            return
        index = next((i for i, item in enumerate(self.rgb_case_profiles) if item["id"] == profile_id), -1)
        if index < 0:
            return
        name = str(self.rgb_case_profiles[index]["name"])
        self.rgb_case_profiles[index] = self._profile_snapshot(profile_id, name)
        self.persist_rgb_case_profiles()
        self.rgb_layout_status_label.setText(f"PC-Profil „{name}“ gespeichert")

    def load_selected_rgb_case_profile(self, _index: int = -1) -> None:
        profile_id = str(self.rgb_layout_profile_combo.currentData() or "")
        if not profile_id.startswith("user-"):
            return
        profile = next((item for item in self.rgb_case_profiles if item["id"] == profile_id), None)
        if profile is None:
            return
        groups = normalize_rgb_groups(profile.get("groups", []))
        if not groups:
            return
        self.rgb_groups = groups
        self.rgb_layout_slots = normalize_layout_slots(profile.get("slots", []), groups)
        self.settings.setValue("rgb_studio/layout_profile", profile_id)
        self._restore_profile_hardware(profile)
        sync_gpu = getattr(self, "select_gpu_route_sources", None)
        if callable(sync_gpu):
            sync_gpu()
        self.rgb_case_template_id = case_template(profile.get("case_id")).case_id
        self.rgb_case_template_combo.blockSignals(True)
        self.rgb_case_template_combo.setCurrentIndex(max(0, self.rgb_case_template_combo.findData(self.rgb_case_template_id)))
        self.rgb_case_template_combo.blockSignals(False)
        cooling_visual = str(profile.get("cooling_visual", "auto") or "auto")
        self.rgb_case_cooling_combo.setCurrentIndex(max(0, self.rgb_case_cooling_combo.findData(cooling_visual)))
        self.settings.setValue("rgb_studio/case_template", self.rgb_case_template_id)
        self.save_rgb_workspace()
        self.rebuild_rgb_workspace()
        self.refresh_rgb_layout_editor()
        self.rgb_layout_status_label.setText(f"PC-Profil „{profile['name']}“ geladen · keine Hardwarefarbe geschrieben")

    def delete_selected_rgb_case_profile(self) -> None:
        profile_id = str(self.rgb_layout_profile_combo.currentData() or "")
        profile = next((item for item in self.rgb_case_profiles if item["id"] == profile_id), None)
        if profile is None:
            return
        answer = QMessageBox.question(
            self, "PC-Profil löschen", f"PC-Profil „{profile['name']}“ wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.rgb_case_profiles = [item for item in self.rgb_case_profiles if item["id"] != profile_id]
        self.persist_rgb_case_profiles()
        index = self.rgb_layout_profile_combo.findData(profile_id)
        if index >= 0:
            self.rgb_layout_profile_combo.removeItem(index)
        self.rgb_layout_profile_combo.setCurrentIndex(0)

    def open_rgb_case_template_source(self) -> None:
        QDesktopServices.openUrl(QUrl(case_template(self.rgb_case_template_combo.currentData()).source_url))

    def preview_rgb_case_template(self, _index: int = -1) -> None:
        if hasattr(self, "rgb_layout_diagram"):
            self.rgb_layout_diagram.set_case_template(
                case_template(self.rgb_case_template_combo.currentData())
            )

    def update_rgb_case_cooling_visual(self, _index: int = -1) -> None:
        visual = str(self.rgb_case_cooling_combo.currentData() or "auto")
        self.settings.setValue("rgb_studio/cooling_visual", visual)
        if hasattr(self, "rgb_layout_diagram"):
            self.rgb_layout_diagram.set_cooling_visual(visual)

    def apply_rgb_case_template(self) -> None:
        template = case_template(self.rgb_case_template_combo.currentData())
        if template.case_id == DEFAULT_CASE_ID:
            self.rgb_layout_profile_combo.setCurrentIndex(max(0, self.rgb_layout_profile_combo.findData("flori")))
            self.load_builtin_rgb_layout_profile()
            self.rgb_case_template_id = template.case_id
            self.settings.setValue("rgb_studio/case_template", template.case_id)
            return
        answer = QMessageBox.question(
            self, "Gehäusevorlage anwenden",
            f"Die schematische Startvorlage „{template.title}“ anwenden? Lüfterpositionen werden ersetzt; "
            "GPU, Halterung, RAM und Pumpenkopf bleiben erhalten. Es wird keine Hardwarefarbe geschrieben.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        components = [slot for slot in self.rgb_layout_slots if slot.position in {"gpu", "gpu-support", "ram", "pump"}]
        previous = {slot.position: slot for slot in self.rgb_layout_slots}
        groups = {group.group_id: group for group in self.rgb_groups}
        titles = {"front": "Front", "side": "Seite", "top": "Oben", "rear": "Heck", "bottom": "Boden"}
        fan_slots: list[RGBLayoutSlot] = []
        for position, count in template.fan_layout:
            group_id = f"case-{position}"
            groups.setdefault(group_id, RGBGroup(group_id, f"{titles[position]}lüfter"))
            x, y = mount_point(template.case_id, position)
            airflow = "exhaust" if position in {"top", "rear"} else "intake"
            fan_slots.append(RGBLayoutSlot(
                position, f"{titles[position]} · {count}× 120/140 mm", count, group_id,
                "Anschluss und Lüftergröße prüfen", previous[position].device_ids if position in previous else (),
                f"case-{position}", x, y, airflow, 120,
                previous[position].scale if position in previous else 1.0,
                previous[position].visual_kind if position in previous else "auto",
                previous[position].gpu_visual if position in previous else "auto",
            ))
        self.rgb_groups = list(groups.values())
        self.rgb_layout_slots = [*fan_slots, *components]
        self.rgb_case_template_id = template.case_id
        self.settings.setValue("rgb_studio/case_template", template.case_id)
        self.save_rgb_workspace()
        self.rebuild_rgb_workspace()
        self.refresh_rgb_layout_editor()
        self.rgb_layout_status_label.setText(f"{template.title}: schematische Startpositionen geladen · bitte reale Montage prüfen")
