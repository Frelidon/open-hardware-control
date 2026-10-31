# SPDX-License-Identifier: GPL-3.0-or-later
"""GPU profile cards, model artwork and guarded application workflow."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import time

from PySide6.QtCore import QStandardPaths, Qt, QTimer
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from modules.gpu_profiles.v1_0 import (
    GPU_MODELS, append_or_replace_profile, config_digest, detect_model,
    load_profiles, model_by_id, normalize_profile, remove_profile, save_profiles,
    zero_rpm_state,
)
from modules.gpu_profiles.v1_0.artwork import import_transparent_artwork, remove_managed_artwork

from .client import LactError, config_equivalent, healthy_stats
from .fan_profile import displayed_curve
from .snapshot import read_snapshot, write_snapshot


class GpuProfileUiMixin:
    def _managed_gpu_art_directory(self) -> Path:
        config = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation))
        return config / "gpu-art"

    def _build_profiles(self) -> None:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setSpacing(14)

        card = QGroupBox(self.tr("Grafikkartenprofil"))
        card.setObjectName("gpuProfileCard")
        card_row = QHBoxLayout(card)
        self.gpu_profile_art = QLabel()
        self.gpu_profile_art.setObjectName("gpuProfileArtwork")
        self.gpu_profile_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gpu_profile_art.setMinimumSize(460, 245)
        card_row.addWidget(self.gpu_profile_art, 3)
        form_host = QWidget()
        form = QFormLayout(form_host)
        self.gpu_model_combo = QComboBox()
        self.gpu_model_combo.addItem(self.tr("Automatisch nach Gerätename"), "")
        for row in GPU_MODELS:
            self.gpu_model_combo.addItem(
                f"{row['vendor']} · {row['generation']} · {row['name']}", row["id"],
            )
        self.gpu_model_combo.currentIndexChanged.connect(self._update_gpu_profile_art)
        self.gpu_orientation = QComboBox()
        self.gpu_orientation.addItem(self.tr("Horizontal · Lüfter unten"), "horizontal")
        self.gpu_orientation.addItem(self.tr("Vertikal · Lüfter vorn"), "vertical")
        self.gpu_orientation.currentIndexChanged.connect(self._update_gpu_profile_art)
        self.gpu_profile_combo = QComboBox()
        self.gpu_profile_combo.currentIndexChanged.connect(self._gpu_profile_selected)
        self.gpu_profile_name = QLineEdit()
        self.gpu_profile_name.setPlaceholderText(self.tr("z. B. Leise, Gaming, Rendering"))
        self.gpu_profile_autostart = QCheckBox(self.tr("Beim Programmstart aktivieren"))
        self.gpu_profile_zero_rpm = QLabel(self.tr("Zero-RPM: von erkannter Karte"))
        self.gpu_profile_zero_rpm.setWordWrap(True)
        form.addRow(self.tr("Kartenmodell"), self.gpu_model_combo)
        form.addRow(self.tr("Einbau"), self.gpu_orientation)
        form.addRow(self.tr("GPU-Unterprofil"), self.gpu_profile_combo)
        form.addRow(self.tr("Profilname"), self.gpu_profile_name)
        form.addRow(self.gpu_profile_autostart)
        form.addRow(self.gpu_profile_zero_rpm)
        card_row.addWidget(form_host, 2)
        outer.addWidget(card)

        artwork = QGroupBox(self.tr("Eigenes Grafikkartenbild"))
        artwork.setObjectName("gpuArtworkCard")
        artwork_row = QHBoxLayout(artwork)
        import_button = QPushButton(self.tr("Transparentes PNG/WebP importieren"))
        import_button.clicked.connect(self.import_gpu_profile_artwork)
        remove_art = QPushButton(self.tr("Eigenes Bild entfernen"))
        remove_art.clicked.connect(self.remove_gpu_profile_artwork)
        artwork_row.addWidget(import_button)
        artwork_row.addWidget(remove_art)
        artwork_row.addWidget(QLabel(self.tr("Original bleibt erhalten; OHC verwaltet eine Kopie.")), 1)
        outer.addWidget(artwork)

        actions = QHBoxLayout()
        save = QPushButton(self.tr("GPU-Werte als Profil speichern"))
        save.setObjectName("gpuPrimaryAction")
        save.clicked.connect(self.save_current_gpu_profile)
        load = QPushButton(self.tr("Als sicheren Entwurf laden"))
        load.clicked.connect(self.load_selected_gpu_profile_draft)
        apply_button = QPushButton(self.tr("Geprüftes GPU-Profil aktivieren"))
        apply_button.setObjectName("gpuPrimaryAction")
        apply_button.clicked.connect(self.apply_selected_gpu_profile)
        delete = QPushButton(self.tr("GPU-Profil löschen"))
        delete.setObjectName("gpuDangerAction")
        delete.clicked.connect(self.delete_selected_gpu_profile)
        for button in (save, load, apply_button, delete):
            actions.addWidget(button)
        actions.addStretch()
        outer.addLayout(actions)
        self.gpu_profile_status = QLabel(self.tr(
            "Taktung, Leistung, Lüfterkurve, Zero-RPM und Lasttest werden gespeichert."
        ))
        self.gpu_profile_status.setWordWrap(True)
        self.gpu_profile_status.setObjectName("muted")
        outer.addWidget(self.gpu_profile_status)
        outer.addStretch()
        self.sections.addTab(page, self.tr("Profile"))

        self.gpu_profiles = load_profiles(self.host.settings)
        self.gpu_profile_artwork = ""
        self._pending_main_gpu_profile: tuple[dict, bool, bool] | None = None
        self._startup_gpu_profile_attempted = False
        self.refresh_gpu_profile_list()
        if any(row["activate_at_start"] for row in self.gpu_profiles):
            QTimer.singleShot(0, self, self.refresh)

    def refresh_gpu_profile_list(self, selected_id: str = "") -> None:
        selected = selected_id or str(self.host.settings.value(
            "gpu_control/selected_profile/v1", "",
        ))
        self.gpu_profile_combo.blockSignals(True)
        self.gpu_profile_combo.clear()
        self.gpu_profile_combo.addItem(self.tr("Neues GPU-Profil"), "")
        for profile in self.gpu_profiles:
            suffix = self.tr(" · geprüft") if profile["verified"] else self.tr(" · Entwurf")
            self.gpu_profile_combo.addItem(profile["name"] + suffix, profile["id"])
        self.gpu_profile_combo.setCurrentIndex(max(0, self.gpu_profile_combo.findData(selected)))
        self.gpu_profile_combo.blockSignals(False)
        self._gpu_profile_selected()

    def _selected_gpu_profile(self) -> dict | None:
        profile_id = str(self.gpu_profile_combo.currentData() or "")
        return next((row for row in self.gpu_profiles if row["id"] == profile_id), None)

    def _gpu_profile_selected(self, _index: int = -1) -> None:
        profile = self._selected_gpu_profile()
        if profile is None:
            self.gpu_profile_name.clear()
            self.gpu_profile_autostart.setChecked(False)
            self.gpu_profile_artwork = ""
            self._select_detected_gpu_model()
            self._update_gpu_profile_art()
            return
        self.host.settings.setValue("gpu_control/selected_profile/v1", profile["id"])
        self.gpu_profile_name.setText(profile["name"])
        self.gpu_profile_autostart.setChecked(profile["activate_at_start"])
        self.gpu_profile_artwork = profile.get("artwork", "")
        self.gpu_model_combo.setCurrentIndex(max(0, self.gpu_model_combo.findData(profile["model_id"])))
        self.gpu_orientation.setCurrentIndex(max(0, self.gpu_orientation.findData(profile["orientation"])))
        self._apply_stress_profile_values(profile)
        self._show_zero_rpm_state(profile["config"])
        self._update_gpu_profile_art()

    def _select_detected_gpu_model(self) -> None:
        detected = detect_model(self.devices.currentText() if hasattr(self, "devices") else "")
        model_id = detected["id"] if detected is not None else ""
        self.gpu_model_combo.setCurrentIndex(max(0, self.gpu_model_combo.findData(model_id)))

    def _profile_art_path(self) -> Path | None:
        custom = Path(self.gpu_profile_artwork) if self.gpu_profile_artwork else None
        managed = self._managed_gpu_art_directory()
        if custom is not None:
            try:
                if custom.is_file() and not custom.is_symlink() and custom.parent.resolve() == managed.resolve():
                    return custom
            except OSError:
                pass
        model = model_by_id(self.gpu_model_combo.currentData())
        vendor = model["vendor"] if model else ("NVIDIA" if getattr(self, "gpu_vendor", "") == "NVIDIA" else "AMD")
        filename = "gpu-family-nvidia-green.png" if vendor == "NVIDIA" else "gpu-family-amd-red.png"
        return Path(__file__).resolve().parents[3] / "assets" / "gpu" / filename

    def _update_gpu_profile_art(self, _index: int = -1) -> None:
        path = self._profile_art_path()
        pixmap = QPixmap(str(path)) if path is not None else QPixmap()
        if pixmap.isNull():
            self.gpu_profile_art.setText(self.tr("Keine GPU-Abbildung"))
            self.gpu_profile_art.setPixmap(QPixmap())
            if hasattr(self, "_update_tuning_artwork"):
                self._update_tuning_artwork()
            return
        if self.gpu_orientation.currentData() == "vertical":
            transform = pixmap.transformed(
                QTransform().rotate(90),
                Qt.TransformationMode.SmoothTransformation,
            )
            pixmap = transform
        self.gpu_profile_art.setPixmap(pixmap.scaled(
            self.gpu_profile_art.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))
        self.gpu_profile_art.setText("")
        if hasattr(self, "_update_tuning_artwork"):
            self._update_tuning_artwork()

    def import_gpu_profile_artwork(self) -> None:
        filename, _filter = QFileDialog.getOpenFileName(
            self, self.tr("Transparentes GPU-Bild importieren"), "",
            self.tr("Transparente Bilder (*.png *.webp)"),
        )
        if not filename:
            return
        try:
            imported = import_transparent_artwork(Path(filename), self._managed_gpu_art_directory())
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, self.tr("Bild konnte nicht importiert werden"), str(exc))
            return
        self.gpu_profile_artwork = str(imported)
        self._update_gpu_profile_art()
        self.gpu_profile_status.setText(self.tr(
            "Eigenes Bild eingefügt. Zum Zuordnen GPU-Profil speichern."
        ))

    def remove_gpu_profile_artwork(self) -> None:
        path = Path(self.gpu_profile_artwork) if self.gpu_profile_artwork else None
        if path is None:
            return
        if QMessageBox.question(
            self, self.tr("Eigenes Bild entfernen"),
            self.tr("Nur die OHC-Kopie wird gelöscht; das Original bleibt."),
        ) != QMessageBox.StandardButton.Yes:
            return
        removed = remove_managed_artwork(path, self._managed_gpu_art_directory())
        if removed:
            for profile in self.gpu_profiles:
                if profile.get("artwork") == str(path):
                    profile["artwork"] = ""
            self.gpu_profiles = save_profiles(self.host.settings, self.gpu_profiles)
        self.gpu_profile_artwork = ""
        self._update_gpu_profile_art()

    def _show_zero_rpm_state(self, config: object) -> None:
        state = zero_rpm_state(config)
        text = (
            self.tr("Zero-RPM: unterstützt und aktiviert") if state is True else
            self.tr("Zero-RPM: unterstützt und deaktiviert") if state is False else
            self.tr("Zero-RPM: von dieser Karte nicht gemeldet")
        )
        self.gpu_profile_zero_rpm.setText(text)

    def _apply_stress_profile_values(self, profile: dict) -> None:
        for widget, value in (
            (self.stress_duration, profile["stress_duration"]),
            (self.stress_size, profile["stress_size"]),
            (self.stress_presentation, profile["stress_presentation"]),
        ):
            index = widget.findData(value)
            if index >= 0:
                widget.setCurrentIndex(index)

    def save_current_gpu_profile(self) -> None:
        if self.baseline is None or not self.gpu_id:
            self.gpu_profile_status.setText(self.tr("Zuerst GPU mit LACT aktualisieren."))
            return
        existing = self._selected_gpu_profile()
        profile_id = existing["id"] if existing else f"gpu-{int(time.time() * 1000)}"
        snapshot = read_snapshot(self.host.settings, self.gpu_id)
        verified = not self.baseline or bool(
            snapshot and config_equivalent(snapshot["saved"], self.baseline)
        )
        profile = {
            "id": profile_id,
            "name": self.gpu_profile_name.text().strip() or self.devices.currentText()[:80],
            "gpu_id": self.gpu_id,
            "model_id": str(self.gpu_model_combo.currentData() or ""),
            "orientation": str(self.gpu_orientation.currentData() or "horizontal"),
            "artwork": self.gpu_profile_artwork,
            "config": deepcopy(self.baseline),
            "config_digest": config_digest(self.baseline),
            "verified": verified,
            "activate_at_start": self.gpu_profile_autostart.isChecked(),
            "stress_duration": int(self.stress_duration.currentData() or 30),
            "stress_size": str(self.stress_size.currentData() or "3840x2160"),
            "stress_presentation": str(self.stress_presentation.currentData() or "maximized"),
        }
        try:
            self.gpu_profiles = append_or_replace_profile(self.host.settings, profile)
        except ValueError as exc:
            self.gpu_profile_status.setText(str(exc))
            return
        self.refresh_gpu_profile_list(profile_id)
        self.gpu_profile_status.setText(
            self.tr("GPU-Profil gespeichert und geprüft.") if verified else
            self.tr("Entwurf gespeichert. Vor Autostart einmal testen und speichern.")
        )

    def load_selected_gpu_profile_draft(self) -> None:
        profile = self._selected_gpu_profile()
        if profile is None or self.baseline is None or profile["gpu_id"] != self.gpu_id:
            self.gpu_profile_status.setText(self.tr("Profil passt nicht zur gewählten GPU."))
            return
        config = profile["config"]
        self._apply_stress_profile_values(profile)
        from .client import clock_controls
        controls = clock_controls(self.baseline, self.clocks)
        power = config.get("power_cap")
        if self.power.isEnabled() and isinstance(power, (int, float)) and self.power.minimum() <= power <= self.power.maximum():
            self.power.setValue(float(power))
        for key, widget in (("max_core_clock", self.core), ("max_memory_clock", self.memory)):
            value = config.get(key)
            if key in controls and isinstance(value, (int, float)) and widget.minimum() <= value <= widget.maximum():
                widget.setValue(int(value))
        offsets = config.get("gpu_clock_offsets")
        offset = offsets.get("0", offsets.get(0)) if isinstance(offsets, dict) else None
        if "gpu_clock_offset_0" in controls and isinstance(offset, (int, float)):
            self.offset.setValue(int(offset))
        self.lact_fan.setChecked(bool(config.get("fan_control_enabled")))
        settings = config.get("fan_control_settings")
        mode = settings.get("mode") if isinstance(settings, dict) else "curve"
        self.fan_mode.setCurrentIndex(max(0, self.fan_mode.findData(mode)))
        for (temperature, speed), (temp, percent) in zip(self.fan_points, displayed_curve(config, self.stats)):
            temperature.setValue(temp)
            speed.setValue(percent)
        static_speed = settings.get("static_speed") if isinstance(settings, dict) else None
        if isinstance(static_speed, (int, float)):
            self.fan_static_speed.setValue(round(float(static_speed) * 100))
        self._show_zero_rpm_state(config)
        self._invalidate_test()
        self.gpu_profile_status.setText(self.tr(
            "Entwurf geladen. Kurz testen, dann speichern."
        ))

    def _apply_gpu_profile(self, profile: dict, *, startup: bool = False) -> bool:
        if not self._write_allowed():
            return False
        if (self.baseline is None or profile["gpu_id"] != self.gpu_id
                or not profile["verified"]):
            self.gpu_profile_status.setText(self.tr("Nur ein lokal geprüftes Profil dieser GPU darf starten."))
            return False
        candidate = profile["config"]
        if config_equivalent(candidate, self.baseline):
            self.gpu_profile_status.setText(self.tr("GPU-Profil ist bereits aktiv."))
            return True
        if not self._power_candidate_allowed(candidate):
            self.gpu_profile_status.setText(self.tr("Leistungslimit über LACT-Standard nicht freigeschaltet."))
            return False
        fan_changed = any(candidate.get(key) != self.baseline.get(key)
                          for key in ("fan_control_enabled", "fan_control_settings"))
        if fan_changed and not self.refresh_ownership():
            self.gpu_profile_status.setText(self.tr("Speichern gesperrt: CoolerControl-GPU-Besitz nicht freigegeben."))
            return False
        pending = False
        original = deepcopy(self.baseline)
        try:
            if self.client.config(self.gpu_id) != self.baseline:
                raise LactError("GPU settings changed outside OHC; refresh first")
            self.client.set_config(self.gpu_id, candidate)
            pending = True
            if not config_equivalent(candidate, self.client.config(self.gpu_id)):
                raise LactError("LACT did not apply the selected GPU profile")
            good, reason = healthy_stats(self.client.stats(self.gpu_id))
            if not good:
                raise LactError(reason)
            self.client.pending("confirm")
            pending = False
            saved = self.client.config(self.gpu_id)
            if not config_equivalent(candidate, saved):
                raise LactError("LACT did not confirm the selected GPU profile")
            write_snapshot(self.host.settings, self.gpu_id, original, saved)
            self.baseline = saved
            self._populate_controls()
            self.gpu_profile_status.setText(self.tr("GPU-Profil sicher aktiviert."))
            self._gpu_log(f"GPU-LACT: Profil aktiviert · {profile['name']} · Start={startup}")
            return True
        except (LactError, OSError, TypeError, ValueError) as exc:
            if pending:
                try:
                    self.client.pending("revert")
                except LactError:
                    pass
            self.gpu_profile_status.setText(self.tr("Aktivierung fehlgeschlagen: {reason}").format(reason=exc))
            self._gpu_log(f"GPU-LACT-FEHLER: Profilaktivierung · {exc}")
            return False

    def apply_selected_gpu_profile(self) -> None:
        profile = self._selected_gpu_profile()
        if profile is not None:
            self._apply_gpu_profile(profile)

    def apply_startup_gpu_profile(self) -> None:
        if self._startup_gpu_profile_attempted or self.baseline is None:
            return
        self._startup_gpu_profile_attempted = True
        profile = next((row for row in self.gpu_profiles
                        if row["gpu_id"] == self.gpu_id and row["activate_at_start"]), None)
        if profile is not None:
            self._apply_gpu_profile(profile, startup=True)

    def delete_selected_gpu_profile(self) -> None:
        profile = self._selected_gpu_profile()
        if profile is None or QMessageBox.question(
            self, self.tr("GPU-Profil löschen"),
            self.tr("Gewähltes GPU-Unterprofil löschen?"),
        ) != QMessageBox.StandardButton.Yes:
            return
        self.gpu_profiles = remove_profile(self.host.settings, profile["id"])
        self.refresh_gpu_profile_list()

    def profile_payload_for_main_profile(self) -> dict | None:
        profile = self._selected_gpu_profile()
        if profile is None:
            return None
        payload = deepcopy(profile)
        payload["activate_at_start"] = self.gpu_profile_autostart.isChecked()
        return payload

    def restore_main_profile_payload(self, payload: object, *, startup: bool) -> None:
        imported = normalize_profile(payload)
        if imported is None:
            return
        existing = next((row for row in self.gpu_profiles if row["id"] == imported["id"]), None)
        trusted = bool(existing and existing["verified"]
                       and existing["config_digest"] == imported["config_digest"]
                       and existing["gpu_id"] == imported["gpu_id"])
        if not trusted:
            imported["verified"] = False
        self.gpu_profiles = append_or_replace_profile(self.host.settings, imported)
        self.refresh_gpu_profile_list(imported["id"])
        activate = bool(imported["activate_at_start"] if startup else True)
        self._pending_main_gpu_profile = (imported, startup, trusted and activate)
        if self.baseline is None:
            if activate:
                QTimer.singleShot(0, self, self.refresh)
            return
        self._consume_pending_main_gpu_profile()

    def _consume_pending_main_gpu_profile(self) -> None:
        pending, self._pending_main_gpu_profile = self._pending_main_gpu_profile, None
        if pending is None:
            return
        profile, startup, may_apply = pending
        self._apply_stress_profile_values(profile)
        if may_apply:
            self._apply_gpu_profile(profile, startup=startup)
        else:
            self.gpu_profile_status.setText(self.tr(
                "Aus Hauptprofil geladen; vor Hardwareaktivierung lokal testen."
            ))
