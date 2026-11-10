# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared RAM-bank inspection/dialog orchestration, without a second writer."""
from __future__ import annotations

import json
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QSpinBox, QVBoxLayout
from command_backend import CommandResult
from openrgb_integration import OpenRGBDevice, OpenRGBError


class RgbRamBankMixin:
    def configure_openrgb_ram_bank(
        self, target_devices: list[OpenRGBDevice] | tuple[OpenRGBDevice, ...] | None = None,
    ) -> None:
        """Inspect and edit all RGB DIMMs through one shared bank dialog."""

        if not self.openrgb_server_reachable or self.openrgb_external_server_detected:
            self.show_error(
                "Die von OHC verwaltete OpenRGB-Engine muss erreichbar sein. Bitte ein separates OpenRGB-Fenster "
                "schließen und danach die Geräte neu erkennen."
            )
            return
        devices = list(target_devices or [
            device for device in self.openrgb_devices
            if self.is_rgb_ram_device(device) and not self.openrgb_device_conflict(device)
        ])
        devices = [
            device for device in devices
            if self.is_rgb_ram_device(device) and not self.openrgb_device_conflict(device)
        ]
        if not devices:
            self.show_error("Es wurde kein schreibbereiter RGB-Arbeitsspeicher erkannt.")
            return
        inspections: list[tuple[OpenRGBDevice, dict[str, object]]] = []
        pending = list(devices)
        self.footer_status.setText(
            f"RGB-Studio: gemeinsame RAM-Bank mit {len(devices)} Riegel(n) wird gelesen …"
        )

        def inspect_next() -> None:
            if not pending:
                self.show_openrgb_ram_bank_dialog(inspections)
                return
            device = pending.pop(0)
            try:
                command = self.openrgb_client.sdk_inspect_command(device.index)
            except (OpenRGBError, ValueError) as exc:
                self.show_error(str(exc))
                return

            def inspected(result: CommandResult, current: OpenRGBDevice = device) -> None:
                if not result.ok:
                    self.show_error(
                        f"Die RAM-Zone von {self.rgb_device_display_name(current)} konnte nicht gelesen werden:\n"
                        + (result.combined or f"Exit-Code {result.returncode}")[:800]
                    )
                    return
                try:
                    payload = json.loads(result.stdout.strip())
                except (TypeError, ValueError, json.JSONDecodeError):
                    self.show_error("Der OpenRGB-Zonenbericht des Arbeitsspeichers war nicht gültig.")
                    return
                if not isinstance(payload, dict) or not isinstance(payload.get("zones"), list):
                    self.show_error("OpenRGB hat keine auswertbare RAM-Zonenliste geliefert.")
                    return
                inspections.append((current, payload))
                inspect_next()

            self.backend.run_async(command, callback=inspected, timeout=8, log_output=False)

        inspect_next()

    def show_openrgb_ram_bank_dialog(
        self, inspections: list[tuple[OpenRGBDevice, dict[str, object]]],
    ) -> None:
        rows: list[tuple[OpenRGBDevice, str, int, int, int]] = []
        for device, inspection in inspections:
            zones = [zone for zone in inspection.get("zones", []) if isinstance(zone, dict)]
            if not zones:
                self.show_error(f"{self.rgb_device_display_name(device)} meldet keine RAM-LED-Zone.")
                return
            zone = zones[0]
            name = str(zone.get("name", device.zones[0] if device.zones else "Unknown"))
            current = max(1, int(zone.get("current", device.led_count or 1)))
            minimum = max(1, int(zone.get("minimum", current)))
            maximum = max(minimum, min(512, int(zone.get("maximum", current))))
            rows.append((device, name, current, minimum, maximum))
        lower = max(row[3] for row in rows)
        upper = min(row[4] for row in rows)
        if lower > upper:
            self.show_error("Die erkannten RAM-Riegel haben keinen gemeinsamen erlaubten LED-Bereich.")
            return
        stored_counts = []
        for device, zone, current, _minimum, _maximum in rows:
            stable_id = self.openrgb_stable_ids.get(device.index, f"openrgb:index-{device.index}")
            saved = self.rgb_zone_configurations.get(stable_id, {}).get(zone, {})
            stored_counts.append(int(saved.get("leds_per_unit", current) or current))
        initial = stored_counts[0] if len(set(stored_counts)) == 1 else rows[0][2]
        initial = max(lower, min(upper, initial))

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Arbeitsspeicher gemeinsam einrichten · {len(rows)} Riegel")
        dialog.setMinimumWidth(620)
        layout = QVBoxLayout(dialog)
        note = QLabel(
            "Alle erkannten RGB-Riegel werden als eine RAM-Bank gesteuert. Die Einstellung gilt gemeinsam, "
            "wird intern aber für jeden Riegel separat gespeichert und übertragen. Später erkannte weitere "
            "Riegel erscheinen automatisch in derselben Bank."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QFormLayout()
        led_spin = QSpinBox()
        led_spin.setRange(lower, upper)
        led_spin.setValue(initial)
        led_spin.setSuffix(" LEDs je Riegel")
        form.addRow("LED-Anzahl", led_spin)
        form.addRow("Erkannte Riegel", QLabel(str(len(rows))))
        form.addRow("OpenRGB erlaubt gemeinsam", QLabel(f"{lower}–{upper} LEDs je Riegel"))
        layout.addLayout(form)
        details = QLabel("\n".join(
            f"• {self.rgb_device_display_name(device)} · OpenRGB #{device.index} · {current} LEDs gemeldet"
            for device, _zone, current, _minimum, _maximum in rows
        ))
        details.setObjectName("muted")
        layout.addWidget(details)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Speichern und gemeinsam anwenden" if self.openrgb_write_enabled else "Gemeinsam speichern"
        )
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        def save_bank() -> None:
            count = led_spin.value()
            member_ids: set[str] = set()
            for device, zone, _current, minimum, maximum in rows:
                if not minimum <= count <= maximum:
                    self.show_error(
                        f"{self.rgb_device_display_name(device)} erlaubt {minimum}–{maximum} LEDs."
                    )
                    return
                stable_id = self.openrgb_stable_ids.get(device.index, f"openrgb:index-{device.index}")
                configuration = dict(self.rgb_zone_configurations.get(stable_id, {}))
                configuration[zone] = {"units": 1, "leds_per_unit": count}
                self.rgb_zone_configurations[stable_id] = configuration
                self.rgb_group_assignments[stable_id] = "arbeitsspeicher"
                self.openrgb_sdk_ready_devices.discard(stable_id)
                member_ids.add(stable_id)
            self.rgb_selected_devices.update(member_ids)
            self.save_rgb_workspace()
            dialog.accept()
            self.rebuild_rgb_workspace()
            self.log_message(
                f"RGB-RAM-BANK: {len(rows)} Riegel gemeinsam gespeichert · je {count} LEDs · "
                "ein Menü, getrennte Geräteframes"
            )
            if not self.openrgb_write_enabled:
                self.openrgb_effect_status.setText(
                    f"RAM-Bank gespeichert · {len(rows)} Riegel mit je {count} LEDs"
                )
                return

            def apply_after_ene_reclaim() -> None:
                self.request_rgb_direct_apply(80)

            if any(self.is_ene_dram_device(device) for device, *_rest in rows):
                for device, *_rest in rows:
                    stable_id = self.openrgb_stable_ids.get(device.index, "")
                    self.ene_dram_cli_prime_done.discard(stable_id)
                self.prime_ene_dram_cold_start(apply_after_ene_reclaim, force_all=True)
            else:
                apply_after_ene_reclaim()

        buttons.accepted.connect(save_bank)
        dialog.exec()
