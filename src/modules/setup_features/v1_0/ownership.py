# SPDX-License-Identifier: GPL-3.0-or-later
"""Feature ownership, persistence and writer release, separate from UI layout."""

import json

from modules.control_authority.v1_0 import authority_choices, normalize_authority
from modules.control_authority.v1_0.model import ohc_may_write
from .model import feature_choices, normalize_selection
from .settings_panel import refresh_feature_settings


class FeatureOwnershipMixin:
    def load_enabled_features(self) -> tuple[str, ...]:
        raw = self.settings.value("features/enabled", None)
        if raw is None or raw == "":
            return normalize_selection(None)
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except (TypeError, ValueError, json.JSONDecodeError):
                return normalize_selection(None)
        return normalize_selection(raw if isinstance(raw, (list, tuple, set)) else None)

    def feature_enabled(self, key: str) -> bool:
        return str(key) in self.enabled_features

    def set_feature_enabled(self, key: str, enabled: bool) -> None:
        feature = next((item for item in feature_choices() if item.key == key), None)
        if feature is None or (enabled and not feature.available):
            return
        if enabled:
            self.enabled_features.add(key)
            if key == "automation" and hasattr(self, "design_automation_controller"):
                self.design_automation_controller.start()
        else:
            self.enabled_features.discard(key)
            self.release_feature_writers(key)
        self.settings.setValue(
            "features/enabled", json.dumps(sorted(self.enabled_features), ensure_ascii=False)
        )
        self.settings.sync()
        self.update_navigation_visibility()
        refresh_feature_settings(self)
        self.footer_status.setText(
            self.tr_static("Funktion aktiviert") if enabled else self.tr_static("Funktion deaktiviert · OHC-Steuerung freigegeben")
        )

    def release_feature_writers(self, key: str) -> None:
        """Stop only OHC-owned writers before hiding a feature."""
        if key == "rgb":
            self.stop_openrgb_effect("RGB-Funktion deaktiviert · OHC-Animation beendet")
            self.stop_managed_rgb_engine(wait=False)
        elif key == "lcd":
            self.stop_clock_mode(update_status=False, clear_marker=False)
            self.stop_hardware_lcd_mode(update_status=False, clear_marker=False)
            self.stop_imported_lcd_mode(update_status=False, clear_marker=False)
            self.stop_gif_stream()
            studio = getattr(self, "thermalright_display_studio", None)
            if studio is not None:
                studio.restore_firmware_display()
        elif key == "cooling":
            if hasattr(self, "mainboard_master_enable"):
                self.mainboard_master_enable.setChecked(False)
            if hasattr(self, "cpu_curve_timer"):
                self.cpu_curve_timer.stop()
            if getattr(self, "mainboard_control_active", False):
                self.toggle_mainboard_master_control(False, silent=True)
        elif key == "gpu" and hasattr(self, "gpu_control_page"):
            self.gpu_control_page.shutdown()
        elif key == "snapshots" and hasattr(self, "snapshot_manager_page"):
            self.snapshot_manager_page.stop_processes()
        elif key == "automation" and hasattr(self, "design_automation_controller"):
            self.design_automation_controller.shutdown()

    def set_control_authority(self, domain: str, value: object) -> None:
        selected = normalize_authority(domain, value)
        if not ohc_may_write(domain, selected):
            feature_key = {"rgb": "rgb", "lcd": "lcd", "cooling": "cooling", "gpu": "gpu"}.get(domain)
            if feature_key:
                self.release_feature_writers(feature_key)
            if domain == "gpu" and hasattr(self, "gpu_control_page"):
                page = self.gpu_control_page
                if getattr(page, "gpu_id", "") and getattr(page, "baseline", None):
                    page.release_gpu_fan()
        self.control_authority[domain] = selected
        self.settings.setValue(f"control_authority/{domain}", selected)
        self.settings.sync()
        self.refresh_authority_status()
        self.log_message(f"STEUERUNGSZUSTÄNDIGKEIT: {domain}={selected}")

    def refresh_authority_status(self) -> None:
        for domain, label in self.authority_status_labels.items():
            selected = self.control_authority.get(domain, "auto")
            choice = next((item for item in authority_choices(domain) if item.key == selected), None)
            if choice is None:
                continue
            state = "OHC darf schreiben" if choice.ohc_writes else "OHC bleibt nur lesend"
            label.setText(f"{self.tr_static(choice.label)} · {self.tr_static(state)}")
