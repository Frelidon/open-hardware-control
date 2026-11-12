#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Base page for procedural effects, responsive layout cards and Levita hand-off."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time
from typing import Callable

from PySide6.QtCore import QProcess, QProcessEnvironment, QSettings, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from modules.lcd_levita.v1_7.layout_canvas import ThermalrightCanvas
from modules.responsive_gallery.v1_0 import ViewportResizeRelay, reflow_grid, responsive_column_count

from .library import StockEffectsLibrary
from .model import DIRECTIONS, PRESETS, SmokeSettings
from .smoke_renderer import render_smoke_frame


class DisplayEffectsPage(QWidget):
    """Preview, configure and safely export local display animations."""

    def __init__(
        self,
        settings: QSettings,
        studio: object,
        *,
        hero_factory: Callable[[str, str, str, str], QFrame],
        translator: Callable[[str], str] | None = None,
        logger: Callable[[str], None] | None = None,
        process_tracker: Callable[..., object] | None = None,
        section_bar: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self.studio = studio
        self.hero_factory = hero_factory
        self.tr = translator or (lambda source: source)
        self.logger = logger or (lambda _message: None)
        self.process_tracker = process_tracker
        self._phase_started = time.monotonic()
        self._playing = True
        self._syncing_layer2 = False
        self._syncing_effect_selection = False
        self._layer2_cards: dict[str, QToolButton] = {}
        self._layer2_columns = 1
        self._layer2_signature: tuple[tuple[str, str], ...] | None = None
        self._custom_settings = self._load_settings()
        self.export_process = QProcess(self)
        self.export_process.finished.connect(self._export_finished)
        self.export_process.readyReadStandardError.connect(self._read_export_error)
        self._export_errors: list[str] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setMinimumWidth(980)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 14, 22, 22)
        layout.setSpacing(14)
        if section_bar is not None:
            layout.addWidget(section_bar)
        self.hero = hero_factory(
            "✦",
            "Display-Effekte",
            "Dynamische Animationen gestalten, mit Ebene 2 kombinieren und über den geschützten Levita-Pfad übertragen.",
            "Levita Vision",
        )
        layout.addWidget(self.hero)

        selector = QHBoxLayout()
        selector.addWidget(QLabel("Gerät:"))
        self.device_combo = QComboBox()
        self.device_combo.setProperty("i18nTranslateItems", False)
        self.device_combo.addItem("Thermalright Levita Vision · 1600 × 720", "thermalright-levita")
        selector.addWidget(self.device_combo, 1)
        layout.addLayout(selector)

        workspace = QHBoxLayout()
        workspace.setSpacing(14)
        preview_column = QVBoxLayout()
        self.preview_canvas = ThermalrightCanvas(
            lambda _ident, _x, _y: None,
            lambda: None,
            lambda _width: None,
        )
        self.preview_canvas.setToolTip("Vorschau aus Effekt-Ebene 1 und dem aktuellen Sensorlayout aus Ebene 2")
        preview_column.addWidget(self.preview_canvas, alignment=Qt.AlignmentFlag.AlignTop)

        self.preview_actions = preview_actions = QHBoxLayout()
        self.play_button = QPushButton("Pause")
        self.play_button.clicked.connect(self.toggle_playback)
        self.restart_button = QPushButton("↺  Animation neu starten")
        self.restart_button.clicked.connect(self.restart_preview)
        preview_actions.addWidget(self.play_button)
        preview_actions.addWidget(self.restart_button)
        preview_actions.addWidget(QLabel("Vorschau · an Display angepasst"))
        preview_actions.addStretch()
        preview_column.addLayout(preview_actions)

        layer_box = QGroupBox("Ebene 2 · Sensorlayout")
        layer_layout = QVBoxLayout(layer_box)
        self.layer2_current_label = QLabel()
        self.layer2_current_label.setObjectName("muted")
        layer_layout.addWidget(self.layer2_current_label)
        self.layer2_combo = QComboBox()
        self.layer2_combo.hide()
        self.layer2_combo.setProperty("i18nTranslateItems", False)
        self.layer2_combo.currentIndexChanged.connect(self._layer2_changed)
        self.layer2_cards_widget = QWidget()
        self.layer2_cards_grid = QGridLayout(self.layer2_cards_widget)
        self.layer2_cards_grid.setContentsMargins(0, 0, 0, 0)
        self.layer2_cards_grid.setSpacing(8)
        self.layer2_cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layer2_cards_scroll = QScrollArea()
        self.layer2_cards_scroll.setWidgetResizable(True)
        self.layer2_cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.layer2_cards_scroll.setMinimumHeight(150)
        self.layer2_cards_scroll.setMaximumHeight(292)
        self.layer2_cards_scroll.setWidget(self.layer2_cards_widget)
        self._layer2_resize_relay = ViewportResizeRelay(self._relayout_layer2_cards, self)
        self.layer2_cards_scroll.viewport().installEventFilter(self._layer2_resize_relay)
        layer_layout.addWidget(self.layer2_cards_scroll)
        self.layer2_animation_checkbox = QCheckBox("Dekor-Animation")
        self.layer2_animation_checkbox.toggled.connect(self._layer2_animation_changed)
        layer_layout.addWidget(self.layer2_animation_checkbox)
        self.edit_layer2_button = QPushButton("Ebene 2 im LCD-Studio bearbeiten")
        self.edit_layer2_button.clicked.connect(self._open_lcd_studio)
        layer_layout.addWidget(self.edit_layer2_button)
        preview_column.addWidget(layer_box)
        workspace.addLayout(preview_column, 1)

        controls = QGroupBox("Effekt-Einstellungen")
        controls.setMinimumWidth(310)
        control_layout = QVBoxLayout(controls)
        effect_type = QGroupBox("Effekt")
        effect_type_layout = QHBoxLayout(effect_type)
        self.effect_combo = QComboBox()
        self.effect_combo.addItem("Rauch", "smoke")
        self.effect_combo.addItem("Designbibliothek", "library")
        self.effect_combo.currentIndexChanged.connect(self._effect_type_changed)
        effect_type_layout.addWidget(self.effect_combo, 1)
        control_layout.addWidget(effect_type)
        self.stock_library = StockEffectsLibrary(self.tr)
        self.stock_library.selection_changed.connect(self._library_selection_changed)
        control_layout.addWidget(self.stock_library)
        self.procedural_widget = QWidget()
        procedural_layout = QVBoxLayout(self.procedural_widget)
        procedural_layout.setContentsMargins(0, 0, 0, 0)
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Voreinstellung:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Glutrauch", "ember")
        self.preset_combo.addItem("Eisnebel", "ice")
        self.preset_combo.addItem("Plasmawirbel", "plasma")
        self.preset_combo.addItem("Benutzerdefiniert", "custom")
        self.preset_combo.currentIndexChanged.connect(self._preset_changed)
        preset_row.addWidget(self.preset_combo, 1)
        procedural_layout.addLayout(preset_row)

        color_grid = QGridLayout()
        color_grid.addWidget(QLabel("Primärfarbe"), 0, 0)
        color_grid.addWidget(QLabel("Sekundärfarbe"), 0, 1)
        self.primary_button = QPushButton()
        self.secondary_button = QPushButton()
        self.primary_button.clicked.connect(lambda: self._choose_color("primary"))
        self.secondary_button.clicked.connect(lambda: self._choose_color("secondary"))
        color_grid.addWidget(self.primary_button, 1, 0)
        color_grid.addWidget(self.secondary_button, 1, 1)
        procedural_layout.addLayout(color_grid)

        self.sliders: dict[str, QSlider] = {}
        self.value_labels: dict[str, QLabel] = {}
        for key, title, description, minimum in (
            ("sharpness", "Schärfe", "Betont feine Konturen und Details.", 50),
            ("density", "Rauchdichte", "Steuert die Anzahl sichtbarer Rauchbahnen.", 20),
            ("speed", "Geschwindigkeit", "Legt das Tempo der Animation fest.", 10),
            ("turbulence", "Turbulenz", "Verändert Wirbel und Strömung.", 0),
            ("glow", "Leuchten", "Fügt den Konturen einen weichen Lichtschein hinzu.", 0),
        ):
            title_row = QHBoxLayout()
            title_label = QLabel(title)
            value_label = QLabel("0 %")
            value_label.setObjectName("muted")
            title_row.addWidget(title_label)
            title_row.addStretch()
            title_row.addWidget(value_label)
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(minimum, 100)
            slider.valueChanged.connect(lambda _value, name=key: self._control_changed(name))
            hint = QLabel(description)
            hint.setWordWrap(True)
            hint.setObjectName("muted")
            procedural_layout.addLayout(title_row)
            procedural_layout.addWidget(slider)
            procedural_layout.addWidget(hint)
            self.sliders[key] = slider
            self.value_labels[key] = value_label

        direction_row = QHBoxLayout()
        direction_row.addWidget(QLabel("Richtung:"))
        self.direction_combo = QComboBox()
        for value, label in (("right", "Nach rechts"), ("left", "Nach links"), ("up", "Nach oben"), ("down", "Nach unten")):
            self.direction_combo.addItem(label, value)
        self.direction_combo.currentIndexChanged.connect(lambda _index: self._control_changed("direction"))
        direction_row.addWidget(self.direction_combo, 1)
        procedural_layout.addLayout(direction_row)

        self.save_button = QPushButton("Einstellungen als eigene Voreinstellung speichern")
        self.save_button.clicked.connect(self.save_custom_settings)
        self.apply_button = QPushButton("Effekt auf Gerät anwenden")
        self.apply_button.setObjectName("primaryButton")
        self.apply_button.clicked.connect(self.apply_to_device)
        self.remember_button = QPushButton("Als Startdesign vormerken")
        self.remember_button.clicked.connect(self.remember_for_profile_start)
        procedural_layout.addWidget(self.save_button)
        control_layout.addWidget(self.procedural_widget)
        control_layout.addStretch()
        control_layout.addWidget(self.remember_button)
        control_layout.addWidget(self.apply_button)
        self.restore_original_button = QPushButton("Thermalright-Originalanzeige wiederherstellen")
        restore_firmware = getattr(self.studio, "restore_firmware_display", None)
        self.restore_original_button.setEnabled(callable(restore_firmware))
        if callable(restore_firmware):
            self.restore_original_button.clicked.connect(restore_firmware)
        control_layout.addWidget(self.restore_original_button)
        self.profile_hint = QLabel(
            "Das gespeicherte Levita-Startdesign wird beim nächsten Programmstart automatisch verwendet."
        )
        self.profile_hint.setWordWrap(True)
        self.profile_hint.setObjectName("warningText")
        control_layout.addWidget(self.profile_hint)
        workspace.addWidget(controls)
        layout.addLayout(workspace)

        self.status_label = QLabel(
            "Bereit · die Vorschau ist lokal. Erst „Effekt auf Gerät anwenden“ erzeugt das Video und nutzt den LCD-Gerätepfad."
        )
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("infoText")
        layout.addWidget(self.status_label)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.preview_timer = QTimer(self)
        self.preview_timer.setInterval(50)
        self.preview_timer.timeout.connect(self.render_preview)
        preview_fps_combo = getattr(self.studio, "preview_fps_combo", None)
        if preview_fps_combo is not None:
            preview_fps_combo.currentIndexChanged.connect(self._sync_preview_fps)
        self.studio.hardware_design_combo.currentIndexChanged.connect(self._source_layer2_changed)
        if hasattr(self.studio, "media_combo"):
            self.studio.media_combo.currentIndexChanged.connect(self._source_effect_media_changed)
        if hasattr(self.studio, "library_ready"):
            self.studio.library_ready.connect(self._refresh_layer2_choices)
        self.sync_layer2_choices()
        self._apply_settings(self._custom_settings)
        self.sync_active_selection()

    def _load_settings(self) -> SmokeSettings:
        raw = self.settings.value("display_effects/smoke/settings", "")
        try:
            values = json.loads(str(raw)) if raw else {}
        except (TypeError, json.JSONDecodeError):
            values = {}
        return SmokeSettings.from_mapping(values if isinstance(values, dict) else {})

    def current_settings(self) -> SmokeSettings:
        return SmokeSettings.from_mapping({
            "primary_color": self.primary_button.property("color") or "#FF6A00",
            "secondary_color": self.secondary_button.property("color") or "#F5F7FA",
            **{key: slider.value() for key, slider in self.sliders.items()},
            "direction": self.direction_combo.currentData() or "right",
        })

    def _apply_settings(self, values: SmokeSettings) -> None:
        controls = [*self.sliders.values(), self.direction_combo]
        for control in controls:
            control.blockSignals(True)
        for key, slider in self.sliders.items():
            slider.setValue(int(getattr(values, key)))
            self.value_labels[key].setText(f"{slider.value()} %")
        direction_index = self.direction_combo.findData(values.direction)
        self.direction_combo.setCurrentIndex(max(0, direction_index))
        for control in controls:
            control.blockSignals(False)
        self._set_color_button(self.primary_button, values.primary_color)
        self._set_color_button(self.secondary_button, values.secondary_color)
        self.restart_preview()

    @staticmethod
    def _set_color_button(button: QPushButton, value: str) -> None:
        color = QColor(value)
        text = "#111111" if color.lightness() > 155 else "#FFFFFF"
        button.setProperty("color", value)
        button.setText(value)
        button.setStyleSheet(f"QPushButton {{ background: {value}; color: {text}; min-height: 30px; }}")

    def _choose_color(self, which: str) -> None:
        button = self.primary_button if which == "primary" else self.secondary_button
        selected = QColorDialog.getColor(QColor(str(button.property("color"))), self, self.tr("Farbe für Display-Effekt wählen"))
        if selected.isValid():
            self._set_color_button(button, selected.name().upper())
            self._control_changed(which)

    def _preset_changed(self, _index: int) -> None:
        preset = str(self.preset_combo.currentData() or "custom")
        if preset in PRESETS:
            self._apply_settings(PRESETS[preset])

    def _control_changed(self, key: str) -> None:
        if key in self.sliders:
            self.value_labels[key].setText(f"{self.sliders[key].value()} %")
        custom = self.preset_combo.findData("custom")
        if custom >= 0 and self.preset_combo.currentIndex() != custom:
            self.preset_combo.blockSignals(True)
            self.preset_combo.setCurrentIndex(custom)
            self.preset_combo.blockSignals(False)
        self.render_preview()

    def toggle_playback(self) -> None:
        self._playing = not self._playing
        if self._playing:
            self._phase_started = time.monotonic()
            self.preview_timer.start()
            self.play_button.setText(self.tr("Pause"))
        else:
            self.preview_timer.stop()
            self.play_button.setText(self.tr("Wiedergabe"))

    def restart_preview(self) -> None:
        self._phase_started = time.monotonic()
        if self.isVisible():
            self.render_preview()

    def _sync_preview_fps(self, _index: int = -1) -> None:
        fps = max(10, min(20, int(getattr(self.studio, "preview_fps", 60))))
        self.preview_timer.setInterval(max(50, round(1000 / fps)))

    def render_preview(self) -> None:
        if self.effect_combo.currentData() == "library":
            frame = self.stock_library.current_preview()
            background = frame.scaled(
                1600, 720, Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.studio.sync_effect_preview(self.preview_canvas, background)
            return
        phase = ((time.monotonic() - self._phase_started) * (0.08 + self.current_settings().speed / 360.0)) % 1.0
        frame = render_smoke_frame(self.current_settings(), phase, width=800, height=360)
        background = QPixmap.fromImage(frame).scaled(1600, 720, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.studio.sync_effect_preview(self.preview_canvas, background)

    def _refresh_layer2_choices(self) -> None:
        self.sync_layer2_choices(force=True)

    def sync_layer2_choices(self, *, force: bool = False) -> None:
        source = self.studio.hardware_design_combo
        current = str(source.currentData() or "")
        signature = tuple(
            (source.itemText(index), str(source.itemData(index) or ""))
            for index in range(source.count())
        )
        if not force and signature == self._layer2_signature:
            self._sync_layer2_selection()
            return
        self._layer2_signature = signature
        self._syncing_layer2 = True
        self.layer2_combo.clear()
        while self.layer2_cards_grid.count():
            item = self.layer2_cards_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._layer2_cards.clear()
        provider = getattr(self.studio, "layer2_preview_choices", None)
        choices = provider() if callable(provider) else [
            (source.itemText(index), str(source.itemData(index) or ""), QPixmap())
            for index in range(source.count())
        ]
        for position, (label, path, preview) in enumerate(choices):
            self.layer2_combo.addItem(label, path)
            button = QToolButton()
            button.setObjectName("layer2PreviewCard")
            button.setCheckable(True)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setIcon(QIcon(preview))
            button.setIconSize(QSize(164, 74))
            title = label.rsplit("/", 1)[-1].replace("▣", "").strip()
            button.setText(f"{title[:27]}\nLive-Layout")
            button.setToolTip(label)
            button.setFixedSize(180, 116)
            button.clicked.connect(lambda _checked=False, value=path: self._select_layer2_card(value))
            self._layer2_cards[path] = button
        self._relayout_layer2_cards(force=True)
        target = self.layer2_combo.findData(current)
        self.layer2_combo.setCurrentIndex(max(0, target))
        self._syncing_layer2 = False
        self._sync_layer2_selection()
        if self.isVisible():
            self.render_preview()

    def _relayout_layer2_cards(self, *, force: bool = False) -> None:
        width = max(
            self.layer2_cards_scroll.viewport().width(),
            self.layer2_cards_scroll.width(),
        )
        columns = responsive_column_count(width, card_width=180, gap=8, maximum=10)
        if not force and columns == self._layer2_columns:
            return
        self._layer2_columns = columns
        reflow_grid(self.layer2_cards_grid, self._layer2_cards.values(), columns)

    def _select_layer2_card(self, path: str) -> None:
        index = self.layer2_combo.findData(path)
        if index >= 0:
            self.layer2_combo.setCurrentIndex(index)

    def _source_layer2_changed(self, _index: int) -> None:
        if self._syncing_layer2:
            return
        source_path = str(self.studio.hardware_design_combo.currentData() or "")
        target = self.layer2_combo.findData(source_path)
        if target >= 0 and target != self.layer2_combo.currentIndex():
            self._syncing_layer2 = True
            self.layer2_combo.setCurrentIndex(target)
            self._syncing_layer2 = False
        self._sync_layer2_selection()
        self.render_preview()

    def _sync_layer2_selection(self) -> None:
        current = str(self.layer2_combo.currentData() or "")
        for path, button in self._layer2_cards.items():
            button.setChecked(path == current)
        self.layer2_current_label.setText(self.layer2_combo.currentText())
        source_toggle = getattr(self.studio, "layer2_motion_checkbox", None)
        if source_toggle is not None:
            self.layer2_animation_checkbox.blockSignals(True)
            self.layer2_animation_checkbox.setEnabled(source_toggle.isEnabled())
            self.layer2_animation_checkbox.setChecked(source_toggle.isChecked())
            self.layer2_animation_checkbox.blockSignals(False)

    def _layer2_animation_changed(self, enabled: bool) -> None:
        source_toggle = getattr(self.studio, "layer2_motion_checkbox", None)
        if source_toggle is not None and source_toggle.isEnabled():
            source_toggle.setChecked(bool(enabled))
            self.render_preview()

    def _layer2_changed(self, _index: int) -> None:
        if self._syncing_layer2:
            return
        source = self.studio.hardware_design_combo
        index = source.findData(self.layer2_combo.currentData())
        if index >= 0:
            source.setCurrentIndex(index)
        self._sync_layer2_selection()
        self.render_preview()

    def _open_lcd_studio(self) -> None:
        window = self.window()
        tabs = getattr(window, "tabs", None)
        if tabs is not None:
            workspace = getattr(window, "lcd_workspace", None)
            if workspace is not None:
                workspace.select_device("thermalright")
            worktabs = getattr(self.studio, "workspace_tabs", None)
            if worktabs is not None:
                worktabs.setCurrentIndex(1)
            tabs.setCurrentIndex(3)
            scroll = getattr(window, "lcd_scroll_page", None)
            if scroll is not None:
                scroll.verticalScrollBar().setValue(0)

    def save_custom_settings(self) -> None:
        values = self.current_settings()
        self.settings.setValue("display_effects/smoke/settings", json.dumps(values.as_dict(), sort_keys=True))
        self.settings.sync()
        self._custom_settings = values
        self.status_label.setText(self.tr("Eigene Rauch-Voreinstellung gespeichert."))

    def _effect_type_changed(self, _index: int) -> None:
        library = self.effect_combo.currentData() == "library"
        self.stock_library.setVisible(library)
        self.procedural_widget.setVisible(not library)
        self.restart_preview()
        if not self._syncing_effect_selection:
            self.settings.setValue("display_effects/type", "library" if library else "smoke")

    def _library_selection_changed(self) -> None:
        self.render_preview()
        if self.effect_combo.currentData() == "library" and not self._syncing_effect_selection:
            self.settings.setValue(
                "display_effects/library_media", str(self.stock_library.current_video()),
            )

    def _source_effect_media_changed(self, _index: int = -1) -> None:
        self.sync_active_selection()

    def sync_active_selection(self) -> None:
        """Mirror an active OHC effect without treating the sync as a user action."""

        provider = getattr(self.studio, "current_media_path", None)
        active = provider() if callable(provider) else None
        target_type = ""
        target_media: Path | None = None
        if isinstance(active, Path) and self.stock_library.select_video(active):
            target_type = "library"
            target_media = active
        elif isinstance(active, Path):
            try:
                active.resolve().relative_to(self.studio.generated_effect_directory().resolve())
                if active.name.startswith("smoke-") and active.suffix.casefold() == ".mp4":
                    target_type = "smoke"
            except (OSError, ValueError):
                pass
        if not target_type:
            saved_type = str(self.settings.value("display_effects/type", "smoke") or "smoke")
            saved_media = Path(str(self.settings.value("display_effects/library_media", "") or ""))
            if saved_type == "library" and self.stock_library.select_video(saved_media):
                target_type = "library"
                target_media = saved_media
            else:
                target_type = "smoke"
        self._syncing_effect_selection = True
        try:
            self.effect_combo.blockSignals(True)
            self.effect_combo.setCurrentIndex(max(0, self.effect_combo.findData(target_type)))
            self.effect_combo.blockSignals(False)
            self._effect_type_changed(self.effect_combo.currentIndex())
        finally:
            self._syncing_effect_selection = False
        if target_media is not None:
            self.settings.setValue("display_effects/type", "library")
            self.settings.setValue("display_effects/library_media", str(target_media.resolve()))

    def _stage_current_library_effect(self) -> bool:
        try:
            return self.studio.remember_effect_startup_design(
                self.stock_library.current_video(), bundled=True,
            )
        except (OSError, ValueError) as exc:
            self.logger(f"DISPLAY-EFFEKT: Startvormerkung fehlgeschlagen · {exc}")
            return False

    def remember_for_profile_start(self) -> None:
        if self.effect_combo.currentData() == "library":
            staged = self._stage_current_library_effect()
        else:
            values = self.current_settings()
            output = self.studio.generated_effect_directory() / f"smoke-{values.cache_key()}.mp4"
            if not output.is_file() or output.stat().st_size < 4096:
                self.status_label.setText(self.tr(
                    "Den Rauch-Effekt zuerst auf das Gerät anwenden, damit das Startvideo erzeugt wird."
                ))
                return
            try:
                staged = self.studio.remember_effect_startup_design(output, bundled=False)
            except (OSError, ValueError) as exc:
                self.status_label.setText(f"{self.tr('Display-Effekt konnte nicht ausgewählt werden:')} {exc}")
                return
        if staged:
            self.status_label.setText(self.tr("Display-Effekt als Levita-Startdesign gespeichert."))
        else:
            self.status_label.setText(self.tr("Den Rauch-Effekt zuerst auf das Gerät anwenden, damit das Startvideo erzeugt wird."))

    def apply_to_device(self) -> None:
        if self.effect_combo.currentData() == "library":
            design = self.stock_library.current_design()
            variant = self.stock_library.current_variant()
            self._select_and_apply(
                self.stock_library.current_video(),
                f"{design.title} · {self.tr(variant.label)}",
                bundled=True,
            )
            return
        if self.export_process.state() != QProcess.ProcessState.NotRunning:
            self.status_label.setText(self.tr("Der Display-Effekt wird bereits erzeugt …"))
            return
        values = self.current_settings()
        cache_root = self.studio.generated_effect_directory()
        cache_root.mkdir(parents=True, exist_ok=True)
        output = cache_root / f"smoke-{values.cache_key()}.mp4"
        if output.is_file() and output.stat().st_size >= 4096:
            self._select_and_apply(output, self.tr("Rauch"))
            return
        config = cache_root / f"smoke-{values.cache_key()}.json"
        temporary = config.with_suffix(".json.part")
        temporary.write_text(json.dumps(values.as_dict(), sort_keys=True), encoding="utf-8")
        temporary.replace(config)
        self._pending_output = output
        self._export_errors.clear()
        self.apply_button.setEnabled(False)
        self.status_label.setText(self.tr("Rauch-Animation wird lokal erzeugt …"))
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("QT_QPA_PLATFORM", "offscreen")
        self.export_process.setProcessEnvironment(environment)
        worker = Path(__file__).resolve().with_name("worker.py")
        arguments = [
            str(worker), "--settings", str(config), "--output", str(output), "--cache-root", str(cache_root),
        ]
        if self.process_tracker is not None:
            self.process_tracker(self.export_process)
        self.export_process.start(sys.executable, arguments)
        self.logger(f"DISPLAY-EFFEKT: Rauch-Export gestartet · Cache {values.cache_key()}")

    def _read_export_error(self) -> None:
        text = bytes(self.export_process.readAllStandardError()).decode("utf-8", errors="replace").strip()
        if text:
            self._export_errors.append(text)

    def _export_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self.apply_button.setEnabled(True)
        output = getattr(self, "_pending_output", None)
        if exit_code == 0 and isinstance(output, Path) and output.is_file() and output.stat().st_size >= 4096:
            self.logger(f"DISPLAY-EFFEKT: Rauch-Export abgeschlossen · {output.name}")
            self._select_and_apply(output, self.tr("Rauch"))
            return
        detail = self._export_errors[-1].splitlines()[-1] if self._export_errors else self.tr("unbekannter Exportfehler")
        self.status_label.setText(f"{self.tr('Display-Effekt konnte nicht erzeugt werden:')} {detail}")
        self.logger(f"DISPLAY-EFFEKT: Export fehlgeschlagen · {detail}")

    def _select_and_apply(self, output: Path, title: str, *, bundled: bool = False) -> None:
        try:
            if bundled:
                self.studio.select_bundled_effect_media(output, title)
            else:
                self.studio.select_generated_effect_media(output, title)
        except (OSError, ValueError) as exc:
            self.status_label.setText(f"{self.tr('Display-Effekt konnte nicht ausgewählt werden:')} {exc}")
            self.logger(f"DISPLAY-EFFEKT: Auswahl fehlgeschlagen · {exc}")
            return
        self.status_label.setText(self.tr("Effekt vorbereitet · Übergabe an den geschützten LCD-Gerätepfad."))
        self.logger(f"DISPLAY-EFFEKT: {title} ausgewählt · geschützte Levita-Übergabe startet")
        self.studio.stage_profile_startup_design()
        self.studio.apply_design()

    def refresh_language(self) -> None:
        self.play_button.setText(self.tr("Pause" if self._playing else "Wiedergabe"))
        self.sync_layer2_choices(force=True)

    def showEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().showEvent(event)
        self.sync_layer2_choices()

    def hideEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.preview_timer.stop()
        super().hideEvent(event)

    def shutdown(self) -> None:
        self.preview_timer.stop()
        if self.export_process.state() != QProcess.ProcessState.NotRunning:
            self.export_process.terminate()
            if not self.export_process.waitForFinished(1200):
                self.export_process.kill()
                self.export_process.waitForFinished(600)
