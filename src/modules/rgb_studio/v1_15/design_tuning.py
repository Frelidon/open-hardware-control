# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-design colour/speed persistence and compact RGB Studio controls."""

from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QSlider, QVBoxLayout

from rgb_effects import BUILTIN_DESIGNS, RGBEffectConfig, effect_color_count


class DesignTuningMixin:
    """Keep per-design tuning outside the main window orchestrator."""

    def load_rgb_design_tuning(self) -> None:
        try:
            raw = json.loads(str(self.settings.value("rgb_studio/design_speed_scales", "{}") or "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            raw = {}
        self.rgb_design_speed_scales: dict[int, int] = {}
        if not isinstance(raw, dict):
            return
        for raw_index, raw_scale in list(raw.items())[:len(BUILTIN_DESIGNS)]:
            try:
                design_index = int(raw_index)
                scale = max(25, min(200, int(raw_scale)))
            except (TypeError, ValueError):
                continue
            if 0 <= design_index < len(BUILTIN_DESIGNS):
                self.rgb_design_speed_scales[design_index] = scale

    def build_rgb_design_speed_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("rgbDesignSpeedPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)
        header = QHBoxLayout()
        header.addWidget(QLabel("Design-Geschwindigkeit"))
        self.rgb_design_speed_value = QLabel("100 % · Designstandard")
        self.rgb_design_speed_value.setObjectName("rgbDesignSpeedValue")
        header.addStretch()
        header.addWidget(self.rgb_design_speed_value)
        layout.addLayout(header)
        self.rgb_design_speed_scale = QSlider(Qt.Orientation.Horizontal)
        self.rgb_design_speed_scale.setRange(25, 200)
        self.rgb_design_speed_scale.setValue(100)
        self.rgb_design_speed_scale.setSingleStep(5)
        self.rgb_design_speed_scale.setPageStep(25)
        self.rgb_design_speed_scale.setToolTip(
            "100 % verwendet das für dieses Design abgestimmte Originaltempo. "
            "Langsamere Werte helfen besonders bei kurzen LED-Ringen und vielen Direct-Geräten."
        )
        self.rgb_design_speed_scale.valueChanged.connect(self.set_rgb_design_speed_scale)
        layout.addWidget(self.rgb_design_speed_scale)
        presets = QHBoxLayout()
        presets.addWidget(QLabel("Vorschläge:"))
        for scale in (50, 75, 100, 125, 150):
            button = QPushButton(f"{scale} %")
            button.setToolTip("Empfohlen" if scale == 100 else f"Design mit {scale} % des Standardtempos")
            button.clicked.connect(lambda _checked=False, value=scale: self.rgb_design_speed_scale.setValue(value))
            presets.addWidget(button)
        self.rgb_design_speed_reset = QPushButton("Auf 100 % zurücksetzen")
        self.rgb_design_speed_reset.clicked.connect(lambda: self.rgb_design_speed_scale.setValue(100))
        presets.addWidget(self.rgb_design_speed_reset)
        presets.addStretch()
        layout.addLayout(presets)
        return panel

    def persist_rgb_design_tuning(self) -> None:
        self.settings.setValue("rgb_studio/design_color_overrides", json.dumps({
            str(index): self.rgb_config_payload(config)
            for index, config in sorted(self.rgb_design_overrides.items())
        }))
        self.settings.setValue("rgb_studio/design_speed_scales", json.dumps({
            str(index): scale for index, scale in sorted(self.rgb_design_speed_scales.items())
        }))
        self.settings.sync()

    def current_rgb_design_config(self, design_index: int) -> RGBEffectConfig:
        _title, base = BUILTIN_DESIGNS[design_index]
        current = self.current_rgb_studio_config()
        return RGBEffectConfig(
            effect_id=current.effect_id, primary=current.primary, secondary=current.secondary,
            brightness=current.brightness, speed=current.speed, direction=current.direction,
            seed=base.seed,
        ).normalized()

    def sync_rgb_design_speed_control(self, design_index: int, config: RGBEffectConfig) -> None:
        if not hasattr(self, "rgb_design_speed_scale"):
            return
        _title, base = BUILTIN_DESIGNS[design_index]
        scale = self.rgb_design_speed_scales.get(
            design_index, max(25, min(200, round(config.speed * 100 / max(1, base.speed))))
        )
        self.rgb_design_speed_scale.blockSignals(True)
        self.rgb_design_speed_scale.setValue(scale)
        self.rgb_design_speed_scale.blockSignals(False)
        detail = self.tr_static("Designstandard") if scale == 100 else f"{self.tr_static('Effekttempo')} {config.speed} %"
        self.rgb_design_speed_value.setText(f"{scale} % · {detail}")
        self.rgb_design_speed_scale.setEnabled(True)
        self.rgb_design_speed_reset.setEnabled(scale != 100)

    def set_rgb_design_speed_scale(self, scale: int) -> None:
        if getattr(self, "_loading_rgb_design", False):
            return
        data = self.rgb_studio_design_combo.currentData()
        if not isinstance(data, int) or not (0 <= data < len(BUILTIN_DESIGNS)):
            self.rgb_design_speed_value.setText(self.tr_static("Bitte Design auswählen"))
            return
        scale = max(25, min(200, int(scale)))
        _title, base = BUILTIN_DESIGNS[data]
        actual_speed = max(10, min(200, round(base.speed * scale / 100)))
        self._loading_rgb_design = True
        try:
            self.rgb_studio_speed.setValue(actual_speed)
        finally:
            self._loading_rgb_design = False
        self.rgb_design_speed_scales[data] = scale
        self.rgb_design_overrides[data] = self.current_rgb_design_config(data)
        self.rgb_design_gallery.set_design_overrides(self.rgb_design_overrides)
        detail = self.tr_static("Designstandard") if scale == 100 else f"{self.tr_static('Effekttempo')} {actual_speed} %"
        self.rgb_design_speed_value.setText(f"{scale} % · {detail}")
        self.rgb_design_speed_reset.setEnabled(scale != 100)
        self.persist_rgb_design_tuning()
        self.update_rgb_design_selection_status("")
        if self.openrgb_write_enabled and self.rgb_selected_devices:
            self.request_rgb_direct_apply(delay_ms=360)

    def reset_rgb_design_colors(self, design_index: int) -> None:
        _title, base = BUILTIN_DESIGNS[design_index]
        current = self.current_rgb_design_config(design_index)
        self.rgb_design_overrides[design_index] = RGBEffectConfig(
            effect_id=current.effect_id, primary=base.primary, secondary=base.secondary,
            brightness=current.brightness, speed=current.speed, direction=current.direction, seed=base.seed,
        ).normalized()
        self.persist_rgb_design_tuning()
        self.load_rgb_studio_design()
        self.rgb_design_gallery.set_design_overrides(self.rgb_design_overrides)
        self.request_rgb_direct_apply()

    def reset_rgb_design_completely(self, design_index: int) -> None:
        self.rgb_design_overrides.pop(design_index, None)
        self.rgb_design_speed_scales.pop(design_index, None)
        self.persist_rgb_design_tuning()
        self.load_rgb_studio_design()
        self.rgb_design_gallery.set_design_overrides(self.rgb_design_overrides)
        self.request_rgb_direct_apply()

    def show_rgb_effect_color_menu(self, effect_id: str, title: str, global_position) -> None:
        color_count = effect_color_count(effect_id)
        index = self.rgb_studio_effect_combo.findData(effect_id)
        if index >= 0 and index != self.rgb_studio_effect_combo.currentIndex():
            self.rgb_studio_effect_combo.setCurrentIndex(index)
        self.sync_rgb_studio_mode_controls()
        if hasattr(self, "rgb_right_click_hint_label"):
            if color_count == 0:
                hint = f"⌖ {title}: Farbspektrum wird automatisch erzeugt. Kein Extra-Fenster: Bearbeitung bleibt direkt im RGB-Studio."
            elif color_count == 1:
                hint = f"⌖ {title}: Rechtsklick erkannt. Farbe 1 jetzt direkt unten bei Modusfarben ändern (Hex, Preset oder Farbwähler)."
            else:
                hint = f"⌖ {title}: Rechtsklick erkannt. Farbe 1 und Farbe 2 jetzt direkt unten bei Modusfarben ändern (Hex, Preset oder Farbwähler)."
            self.rgb_right_click_hint_label.setText(hint)
        menu = QMenu(self)
        heading = menu.addAction(title)
        heading.setEnabled(False)
        menu.addSeparator()
        primary = menu.addAction("Hauptfarbe ändern …")
        primary.setEnabled(color_count >= 1)
        primary.triggered.connect(lambda: self.pick_rgb_studio_color("primary"))
        secondary = menu.addAction("Zweitfarbe ändern …")
        secondary.setEnabled(color_count >= 2)
        secondary.triggered.connect(lambda: self.pick_rgb_studio_color("secondary"))
        data = self.rgb_studio_design_combo.currentData()
        if isinstance(data, int) and 0 <= data < len(BUILTIN_DESIGNS):
            menu.addSeparator()
            reset_colors = menu.addAction(self.tr_static("Farben auf Designstandard zurücksetzen"))
            reset_colors.setEnabled(color_count >= 1)
            reset_colors.triggered.connect(lambda: self.reset_rgb_design_colors(data))
            menu.addAction(self.tr_static("Tempo auf 100 % zurücksetzen")).triggered.connect(
                lambda: self.rgb_design_speed_scale.setValue(100)
            )
            menu.addAction(self.tr_static("Design vollständig zurücksetzen")).triggered.connect(
                lambda: self.reset_rgb_design_completely(data)
            )
        self.openrgb_effect_status.setText(f"{title}: Farbanpassung per Rechtsklick geöffnet")
        menu.exec(global_position)
