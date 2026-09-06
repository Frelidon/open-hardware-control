#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""PySide6 editor for Thermalright Levita media and metric overlays."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
from typing import Callable, Iterable
import weakref

from PySide6.QtCore import QProcess, QProcessEnvironment, QSize, QTimer, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QProgressBar,
    QPushButton,
    QFrame,
    QScrollArea,
    QSlider,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QToolButton,
)

from thermalright_display import (
    DEFAULT_BACKGROUND_OFFSET_X,
    DEFAULT_BACKGROUND_OFFSET_Y,
    DEFAULT_NOTCH_MASK_WIDTH,
    DEFAULT_OVERLAYS,
    LEVITA_CUTOUT_HEIGHT,
    LEVITA_CUTOUT_WIDTH,
    LEVITA_CUTOUT_X,
    LEVITA_CUTOUT_Y,
    LEVITA_HEIGHT,
    LEVITA_WIDTH,
    MEDIA_CATEGORY_LABELS,
    MEDIA_SCALE_CONTAIN,
    MEDIA_SCALE_COVER,
    MediaEntry,
    OverlaySpec,
    SUPPORTED_IMAGE_SUFFIXES,
    SUPPORTED_VIDEO_SUFFIXES,
    ThermalrightCli,
    bounded_layer_intensity,
    bounded_notch_width,
    build_apply_sequence,
    clamp_overlay_outside_cutout,
    create_hardware_design_preview,
    deduplicate_media_entries,
    default_trcc_design_directory,
    create_layered_mask,
    media_category_key,
    media_catalog_sort_key,
    notch_safe_right_x,
    parse_detect_output,
    prepare_shifted_media,
    scan_media_directory,
    trcc_theme_is_supported,
)
from window_diagnostics import track_qprocess
from modules.lcd_levita.v1_4.layout_canvas import ThermalrightCanvas
from modules.lcd_levita.v1_4.panel_geometry import (
    DEFAULT_INNER_CORNER_RADIUS,
    MAX_INNER_CORNER_RADIUS,
    bounded_inner_corner_radius,
)
from modules.lcd_levita.v1_4.layout_model import (
    EditableLayout,
    LayoutBlock,
    MAX_FONT_SIZE,
    MIN_FONT_SIZE,
    adjust_layout_intensity,
    deserialize_layout_overrides,
    serialize_layout_overrides,
    restore_explicit_format_units,
)
from hardware_diagnostics import read_primary_amd_gpu_clock
from modules.lcd_levita.v1_4.runtime_policy import safe_split_mode
from modules.lcd_levita.v1_4.theme_adapter import (
    ThemeLayoutError,
    load_editable_layout,
    stage_editable_theme,
)


LEVITA_APPLY_COOLDOWN_SECONDS = 10.0
READABLE_CONTROL_HEIGHT = 36
READABLE_SPIN_WIDTH = 148
READABLE_COMBO_WIDTH = 320
DESIGN_CARD_WIDTH = 180
DESIGN_CARD_GAP = 8
MEDIA_GALLERY_COLUMNS = (4, 8)
HARDWARE_GALLERY_COLUMNS = (4, 8)


def gallery_column_count(
    width: int,
    *,
    minimum: int,
    maximum: int,
    card_width: int = DESIGN_CARD_WIDTH,
    gap: int = DESIGN_CARD_GAP,
) -> int:
    """Fit as many Levita cards as the gallery width allows, within bounds."""

    usable = max(card_width, int(width) - 24)
    columns = max(1, (usable + gap) // (card_width + gap))
    return max(minimum, min(maximum, columns))


def _readable_value_widget(widget: QWidget, *, min_width: int = READABLE_SPIN_WIDTH) -> None:
    """Keep Levita numbers and suffixes visible instead of shrinking them away."""

    widget.setMinimumWidth(min_width)
    widget.setMinimumHeight(READABLE_CONTROL_HEIGHT)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


def _readable_combo(combo: QComboBox, *, min_width: int = READABLE_COMBO_WIDTH) -> None:
    """Give Levita selection lists room for their full German labels."""

    _readable_value_widget(combo, min_width=min_width)
    combo.setMinimumContentsLength(28)
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo.setMaxVisibleItems(12)


class _PreviewCardButton(QToolButton):
    """Thumbnail card that can animate a cached video while hovered."""

    def __init__(self, entered: Callable[[], None], left: Callable[[], None]) -> None:
        super().__init__()
        self._entered = entered
        self._left = left

    def enterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._entered()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._left()
        super().leaveEvent(event)


class ThermalrightDisplayStudio(QGroupBox):
    """Integrated local-first Levita design editor and TRCC CLI frontend."""

    def __init__(
        self,
        settings,
        cache_dir: Path,
        *,
        log_callback: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Thermalright Levita Vision · Display-Studio", parent)
        self.settings = settings
        self.cache_dir = cache_dir / "thermalright-preview"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_callback = log_callback
        # The LCD page is built before the main Log page. Restoring a saved
        # media directory renders its first preview synchronously, so logging
        # must stay muted until this widget has finished constructing.
        self.log_ready = False
        self.cli = ThermalrightCli()
        self.media_entries: list[MediaEntry] = []
        self.media_duplicate_map: dict[Path, Path] = {}
        self.media_duplicate_count = 0
        self.overlay_specs = self._load_overlays()
        self.overlay_undo_stack: list[tuple[OverlaySpec, ...]] = []
        self.overlay_controls: dict[str, dict[str, QWidget]] = {}
        self._visible_media_entries: list[MediaEntry] = []
        self._visible_hardware_themes: list[MediaEntry] = []
        self._media_gallery_columns = MEDIA_GALLERY_COLUMNS[0]
        self._hardware_gallery_columns = HARDWARE_GALLERY_COLUMNS[0]
        self.layer2_overrides = deserialize_layout_overrides(str(
            self.settings.value("thermalright/layer2_overrides_v1", "") or ""
        ))
        self.layer2_originals: dict[str, EditableLayout] = {}
        self.layer2_configs: dict[str, dict[str, object]] = {}
        self.layer2_load_errors: dict[str, str] = {}
        self.layer1_intensity_percent = bounded_layer_intensity(
            self.settings.value("thermalright/layer1_intensity", 100)
        )
        try:
            saved_intensities = json.loads(str(
                self.settings.value("thermalright/layer2_intensity_overrides", "{}") or "{}"
            ))
        except (json.JSONDecodeError, TypeError):
            saved_intensities = {}
        self.layer2_intensity_overrides = {
            str(key): bounded_layer_intensity(value)
            for key, value in saved_intensities.items()
            if isinstance(key, str)
        } if isinstance(saved_intensities, dict) else {}
        self.command_queue: list[tuple[tuple[str, ...], bool]] = []
        self.command_outputs: list[str] = []
        self.current_tolerates_failure = False
        self.queue_done: Callable[[bool, str], None] | None = None
        self.test_colors = [QColor("#ef3340"), QColor("#16c172"), QColor("#2878ff"), QColor("#000000")]
        self.test_color_index = 0
        self.pending_apply_warning = ""
        self.pending_apply_sequence: list[tuple[tuple[str, ...], bool]] = []
        self.apply_retry_remaining = 0
        self.next_hardware_apply_at = 0.0
        self.media_card_buttons: dict[str, QToolButton] = {}
        self.hardware_card_buttons: dict[str, QToolButton] = {}
        self.category_buttons: dict[str, QToolButton] = {}
        self.startup_apply_active = False
        self.startup_retry_count = 0
        self.startup_apply_requested = False
        self.restoring_startup_selection = False
        standard_directory = default_trcc_design_directory()
        custom_value = str(self.settings.value("thermalright/custom_media_directory", "") or "")
        legacy_value = str(self.settings.value("thermalright/media_directory", "") or "")
        if not custom_value and legacy_value and Path(legacy_value).is_dir():
            legacy_path = Path(legacy_value).expanduser().resolve()
            if standard_directory is None or legacy_path != standard_directory:
                custom_value = str(legacy_path)
                self.settings.setValue("thermalright/custom_media_directory", custom_value)
        self.custom_media_directory = (
            Path(custom_value).expanduser().resolve()
            if custom_value and Path(custom_value).expanduser().is_dir()
            else None
        )
        try:
            layer_values = json.loads(str(self.settings.value("thermalright/background_theme_overrides", "[]") or "[]"))
        except (json.JSONDecodeError, TypeError):
            layer_values = []
        self.background_theme_overrides = {
            str(Path(value).expanduser().resolve()) for value in layer_values
            if isinstance(value, str) and Path(value).expanduser().exists()
        }
        try:
            favorite_values = json.loads(str(self.settings.value("thermalright/design_favorites", "[]") or "[]"))
        except (json.JSONDecodeError, TypeError):
            favorite_values = []
        self.design_favorites = {
            str(value) for value in favorite_values[:2500]
            if isinstance(value, str) and value
        } if isinstance(favorite_values, list) else set()

        self.command_process = track_qprocess(QProcess(self))
        self.command_process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        command_environment = QProcessEnvironment.systemEnvironment()
        # TRCC's documented daemon mode is the single USB owner.  Each CLI
        # action becomes an IPC request instead of constructing another App,
        # opening the Levita endpoints and handshaking again.
        command_environment.insert("TRCC_DAEMON", "1")
        command_environment.insert("QT_QPA_PLATFORM", "offscreen")
        self.command_process.setProcessEnvironment(command_environment)
        self.command_process.finished.connect(self._on_command_finished)
        # Long-running ``display play`` is only a daemon IPC ticker. It never
        # opens the Levita USB endpoints itself, but it must live outside the
        # finite command queue so masks/settings remain adjustable while a
        # video is playing.
        self.stream_process = track_qprocess(QProcess(self))
        self.stream_process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.stream_process.setProcessEnvironment(command_environment)
        self.stream_process.readyReadStandardOutput.connect(
            lambda: self.stream_process.readAllStandardOutput()
        )
        self.stream_process.readyReadStandardError.connect(
            lambda: self.stream_process.readAllStandardError()
        )
        self.stream_process.started.connect(self._on_stream_started)
        self.stream_process.errorOccurred.connect(self._on_stream_error)
        self.stream_process.finished.connect(self._on_stream_finished)
        self.stream_stop_requested = False
        self.stream_should_run = False
        self.pending_apply_animated = False
        self.command_step_timer = QTimer(self)
        self.command_step_timer.setSingleShot(True)
        self.command_step_timer.setInterval(350)
        self.command_step_timer.timeout.connect(self._start_next_command)
        self.apply_cooldown_timer = QTimer(self)
        self.apply_cooldown_timer.setSingleShot(True)
        self.apply_cooldown_timer.timeout.connect(self.apply_design)
        self.test_timer = QTimer(self)
        self.test_timer.setInterval(450)
        self.test_timer.timeout.connect(self._next_test_color)
        self.hover_preview_frames: list[QPixmap] = []
        self.hover_preview_frame_index = 0
        self.hover_preview_timer = QTimer(self)
        self.hover_preview_timer.setInterval(250)
        self.hover_preview_timer.timeout.connect(self._advance_hover_preview)
        self.hover_preview_media: Path | None = None
        self.hover_card_button: QToolButton | None = None
        self.hover_card_entry: MediaEntry | None = None
        self.hover_preview_debounce = QTimer(self)
        self.hover_preview_debounce.setSingleShot(True)
        self.hover_preview_debounce.setInterval(140)
        self.hover_preview_debounce.timeout.connect(self._show_pending_hover_preview)
        self.pending_hover_index = -1
        self.hover_extract_media: Path | None = None
        self.hover_extract_targets: list[Path] = []
        self.hover_extract_process = track_qprocess(QProcess(self))
        self.hover_extract_process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.hover_extract_process.finished.connect(self._on_hover_extract_finished)
        self.hover_extract_timeout = QTimer(self)
        self.hover_extract_timeout.setSingleShot(True)
        self.hover_extract_timeout.setInterval(8_000)
        self.hover_extract_timeout.timeout.connect(self._cancel_hover_extract)
        self.thumbnail_ffmpeg = shutil.which("ffmpeg")
        self.thumbnail_queue: list[tuple[str, Path, Path, Path]] = []
        self.thumbnail_queued: set[str] = set()
        self.thumbnail_waiters: dict[str, list[weakref.ReferenceType[QToolButton]]] = {}
        self.thumbnail_active: dict[QProcess, tuple[str, Path, Path, Path]] = {}
        self.thumbnail_workers: list[QProcess] = []
        self.thumbnail_worker_timeouts: dict[QProcess, QTimer] = {}
        self.thumbnail_total = 0
        self.thumbnail_finished = 0
        self.thumbnail_generated = 0
        self.thumbnail_failed = 0
        self.thumbnail_shutting_down = False
        self.shutdown_started = False
        for _worker_number in range(2):
            worker = track_qprocess(QProcess(self))
            worker.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
            worker.finished.connect(
                lambda exit_code, status, process=worker: self._on_thumbnail_finished(
                    process, exit_code, status,
                )
            )
            timeout = QTimer(self)
            timeout.setSingleShot(True)
            timeout.setInterval(8_000)
            timeout.timeout.connect(lambda process=worker: self._cancel_thumbnail_worker(process))
            self.thumbnail_workers.append(worker)
            self.thumbnail_worker_timeouts[worker] = timeout
        self.apply_start_timer = QTimer(self)
        self.apply_start_timer.setSingleShot(True)
        self.apply_start_timer.setInterval(900)
        self.apply_start_timer.timeout.connect(self._begin_pending_apply)
        self.hardware_design_active = False
        self.gpu_clock_guard_state = ""
        self.gpu_clock_guard_timer = QTimer(self)
        self.gpu_clock_guard_timer.setInterval(5000)
        self.gpu_clock_guard_timer.timeout.connect(self._guard_gpu_clock)

        self._build_ui()
        if self.custom_media_directory is not None and self.custom_media_enabled.isChecked():
            self.load_media_directory(self.custom_media_directory, quiet=True, remember_custom=False)
        else:
            self.load_default_trcc_designs(quiet=True)
        self.refresh_backend_status()
        self.log_ready = True
        self.gpu_clock_guard_timer.start()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(12)
        intro = QLabel(
            "Zwei echte Ebenen kombinieren: Bild oder Video im Hintergrund, darüber wahlweise ein komplettes "
            "TRCC-Hardwaredesign oder die frei verschiebbaren OHC-Werte. Alles lässt sich zuerst ohne USB testen."
        )
        intro.setWordWrap(True)
        intro.setObjectName("infoText")
        outer.addWidget(intro)

        status_row = QHBoxLayout()
        self.test_mode = QCheckBox("Testmodus · nur Vorschau, keine USB-Schreibzugriffe")
        self.test_mode.setChecked(self.settings.value("thermalright/test_mode", True, type=bool))
        self.test_mode.toggled.connect(self._on_test_mode_changed)
        self.backend_status = QLabel()
        self.backend_status.setWordWrap(True)
        self.backend_status.setObjectName("muted")
        detect_button = QPushButton("Backend & Gerät prüfen")
        detect_button.clicked.connect(self.detect_backend_and_device)
        status_row.addWidget(self.test_mode)
        status_row.addWidget(self.backend_status, 1)
        status_row.addWidget(detect_button)
        outer.addLayout(status_row)

        library_toolbar = QHBoxLayout()
        standard_button = QPushButton("TRCC-Standarddesigns")
        standard_button.setToolTip(
            "Lädt automatisch die für Levita 1600×720 installierten TRCC-Layouts. "
            "config1.dc übernimmt Positionen, Farben und Live-Sensorwerte direkt."
        )
        standard_button.clicked.connect(self.load_default_trcc_designs)
        import_button = QPushButton("Eigene Designs importieren · Ordner")
        import_button.setToolTip(
            "Liest Bilder, Videos und vollständige Layoutordner ein. Über das Kartenmenü legst du Ebene 1 oder 2 fest."
        )
        import_button.clicked.connect(self.choose_media_directory)
        self.remembered_media_button = QPushButton("Gemerkten Ordner anzeigen")
        self.remembered_media_button.clicked.connect(self.show_remembered_media_directory)
        self.remembered_media_button.setEnabled(self.custom_media_directory is not None)
        self.custom_media_enabled = QCheckBox("Eigenen Designordner einbeziehen")
        self.custom_media_enabled.setChecked(
            self.custom_media_directory is not None
            and self.settings.value("thermalright/custom_media_enabled", True, type=bool)
        )
        self.custom_media_enabled.setEnabled(self.custom_media_directory is not None)
        self.custom_media_enabled.setToolTip(
            "Haken entfernen: Ordner nur aus OHC ausblenden; Dateien auf der Festplatte bleiben unverändert."
        )
        self.custom_media_enabled.toggled.connect(self._toggle_custom_media_directory)
        self.favorites_only = QCheckBox("★ Nur Favoriten")
        self.favorites_only.setToolTip("Zeigt in beiden Ebenen nur als Favorit markierte Designs")
        self.favorites_only.toggled.connect(self._refresh_design_cards)
        self.geometry_toggle = QToolButton()
        self.geometry_toggle.setText("⚙ Design anpassen")
        self.geometry_toggle.setCheckable(True)
        self.geometry_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.top_apply_button = QPushButton("Design direkt anwenden")
        self.top_apply_button.setObjectName("primaryAction")
        self.top_apply_button.clicked.connect(self.apply_design)
        library_toolbar.addWidget(standard_button)
        library_toolbar.addWidget(import_button)
        library_toolbar.addWidget(self.remembered_media_button)
        library_toolbar.addWidget(self.custom_media_enabled)
        library_toolbar.addWidget(self.favorites_only)
        library_toolbar.addWidget(self.geometry_toggle)
        library_toolbar.addWidget(self.top_apply_button)
        library_toolbar.addStretch()
        self.media_filter = QLineEdit()
        self.media_filter.setPlaceholderText("Designs durchsuchen …")
        self.media_filter.setMaximumWidth(300)
        self.media_filter.textChanged.connect(self._apply_media_filter)
        library_toolbar.addWidget(self.media_filter)
        outer.addLayout(library_toolbar)

        self.thumbnail_progress_panel = QFrame()
        thumbnail_progress_layout = QHBoxLayout(self.thumbnail_progress_panel)
        thumbnail_progress_layout.setContentsMargins(0, 0, 0, 0)
        self.thumbnail_progress_label = QLabel(
            "Videovorschauen werden bei Bedarf im Hintergrund vorbereitet"
        )
        self.thumbnail_progress_label.setObjectName("muted")
        self.thumbnail_progress = QProgressBar()
        self.thumbnail_progress.setRange(0, 1)
        self.thumbnail_progress.setValue(0)
        self.thumbnail_progress.setTextVisible(True)
        self.thumbnail_progress.setMinimumWidth(280)
        thumbnail_progress_layout.addWidget(self.thumbnail_progress_label, 1)
        thumbnail_progress_layout.addWidget(self.thumbnail_progress)
        self.thumbnail_progress_panel.hide()
        outer.addWidget(self.thumbnail_progress_panel)

        # The hidden combos remain the compact state model used by the apply
        # code.  The user-facing controls are thumbnail cards, so Qt never opens
        # a desktop-sized popup for hundreds of installed TRCC entries.
        self.media_combo = QComboBox()
        self.media_combo.hide()
        self.media_combo.currentIndexChanged.connect(self.update_preview)
        self.media_combo.currentIndexChanged.connect(self._show_selected_media_preview)
        self.media_combo.currentIndexChanged.connect(self._remember_media_selection)
        self.media_category = QComboBox()
        self.media_category.hide()
        self.media_category.addItem("Alle Kategorien", "all")
        self.media_category.currentIndexChanged.connect(self._apply_media_filter)
        self.hardware_design_combo = QComboBox()
        self.hardware_design_combo.hide()
        self.hardware_design_combo.addItem("Eigene OHC-Werte · frei verschiebbar", "")
        self.hardware_design_combo.currentIndexChanged.connect(self._hardware_design_changed)

        category_frame = QFrame()
        self.category_layout = QHBoxLayout(category_frame)
        self.category_layout.setContentsMargins(0, 0, 0, 0)
        self.category_layout.setSpacing(6)
        self.category_group = QButtonGroup(self)
        self.category_group.setExclusive(True)
        outer.addWidget(category_frame)

        galleries = QHBoxLayout()
        galleries.setSpacing(12)
        self.layer1_library_box = QGroupBox("Ebene 1 · Hintergrund")
        background_box = self.layer1_library_box
        background_box.setMinimumWidth(420)
        background_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        background_layout = QVBoxLayout(background_box)
        background_header = QHBoxLayout()
        background_hint = QLabel("Bilder und Videos · Rechtsklick: Favorit oder Ebene ändern")
        background_hint.setObjectName("muted")
        self.move_to_data_button = QPushButton("Auswahl → Ebene 2")
        self.move_to_data_button.setToolTip("Ein manuell hier abgelegtes komplettes Theme wieder als Datenoberfläche verwenden")
        self.move_to_data_button.clicked.connect(self.move_selected_theme_to_data_layer)
        background_header.addWidget(background_hint, 1)
        background_header.addWidget(self.move_to_data_button)
        background_layout.addLayout(background_header)
        layer1_intensity_row = QHBoxLayout()
        layer1_intensity_row.addWidget(QLabel("Intensität Ebene 1"))
        self.layer1_intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer1_intensity_slider.setRange(25, 150)
        self.layer1_intensity_slider.setValue(self.layer1_intensity_percent)
        self.layer1_intensity_slider.setToolTip("Hintergrund von dezent (25 %) bis kräftig (150 %)")
        self.layer1_intensity_label = QLabel(f"{self.layer1_intensity_percent} %")
        self.layer1_intensity_label.setMinimumWidth(48)
        self.layer1_intensity_slider.valueChanged.connect(self._layer1_intensity_changed)
        layer1_intensity_row.addWidget(self.layer1_intensity_slider, 1)
        layer1_intensity_row.addWidget(self.layer1_intensity_label)
        background_layout.addLayout(layer1_intensity_row)
        self.media_cards_widget = QWidget()
        self.media_cards_grid = QGridLayout(self.media_cards_widget)
        self.media_cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.media_cards_grid.setSpacing(DESIGN_CARD_GAP)
        self.media_cards_scroll = QScrollArea()
        self.media_cards_scroll.setWidgetResizable(True)
        self.media_cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.media_cards_scroll.setMinimumHeight(310)
        self.media_cards_scroll.setWidget(self.media_cards_widget)
        background_layout.addWidget(self.media_cards_scroll)
        galleries.addWidget(background_box, 1)

        self.layer2_library_box = QGroupBox("Ebene 2 · Datenoberfläche")
        hardware_box = self.layer2_library_box
        hardware_box.setMinimumWidth(420)
        hardware_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        hardware_layout = QVBoxLayout(hardware_box)
        hardware_header = QHBoxLayout()
        hardware_hint = QLabel("Live-Daten · Rechtsklick: Favorit oder Ebene ändern")
        hardware_hint.setObjectName("muted")
        hardware_hint.setWordWrap(True)
        self.move_to_background_button = QPushButton("Auswahl → Ebene 1")
        self.move_to_background_button.setToolTip("Ausgewähltes Theme ausnahmsweise als vollständigen Hintergrund verwenden")
        self.move_to_background_button.clicked.connect(self.move_selected_theme_to_background_layer)
        hardware_header.addWidget(hardware_hint, 1)
        hardware_header.addWidget(self.move_to_background_button)
        hardware_layout.addLayout(hardware_header)
        layer2_intensity_row = QHBoxLayout()
        layer2_intensity_row.addWidget(QLabel("Intensität Ebene 2"))
        self.layer2_intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer2_intensity_slider.setRange(25, 150)
        self.layer2_intensity_slider.setValue(100)
        self.layer2_intensity_slider.setToolTip(
            "Datenoberfläche von dezent (25 %) bis besonders hervorgehoben (150 %); wird je Design gespeichert"
        )
        self.layer2_intensity_label = QLabel("100 %")
        self.layer2_intensity_label.setMinimumWidth(48)
        self.layer2_intensity_slider.valueChanged.connect(self._layer2_intensity_changed)
        layer2_intensity_row.addWidget(self.layer2_intensity_slider, 1)
        layer2_intensity_row.addWidget(self.layer2_intensity_label)
        hardware_layout.addLayout(layer2_intensity_row)
        self.hardware_cards_widget = QWidget()
        self.hardware_cards_grid = QGridLayout(self.hardware_cards_widget)
        self.hardware_cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.hardware_cards_grid.setSpacing(DESIGN_CARD_GAP)
        self.hardware_cards_scroll = QScrollArea()
        self.hardware_cards_scroll.setWidgetResizable(True)
        self.hardware_cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.hardware_cards_scroll.setMinimumHeight(310)
        self.hardware_cards_scroll.setWidget(self.hardware_cards_widget)
        hardware_layout.addWidget(self.hardware_cards_scroll)
        galleries.addWidget(hardware_box, 1)
        outer.addLayout(galleries)

        layer_note = QLabel(
            "Im Zwei-Ebenen-Modus wird zuerst das Hardware-Design mit config1.dc oder dem geprüften OHC-"
            "trcc.json geladen und danach nur sein Hintergrund ersetzt. Die Sensorwerte bleiben als obere Ebene live."
        )
        layer_note.setWordWrap(True)
        layer_note.setObjectName("muted")
        outer.addWidget(layer_note)

        self.layer2_editor_bar = QFrame()
        layer2_editor_layout = QHBoxLayout(self.layer2_editor_bar)
        layer2_editor_layout.setContentsMargins(0, 0, 0, 0)
        layer2_editor_hint = QLabel(
            "Ebene 2 bearbeiten: Block ziehen · Rechtsklick ändert Text, Farbe und Schriftgröße"
        )
        layer2_editor_hint.setObjectName("muted")
        self.layer2_offset_x = QSpinBox()
        self.layer2_offset_x.setRange(-1600, 1600)
        self.layer2_offset_x.setSuffix(" px")
        self.layer2_offset_y = QSpinBox()
        self.layer2_offset_y.setRange(-720, 720)
        self.layer2_offset_y.setSuffix(" px")
        self.layer2_reset_button = QPushButton("Ebene 2 zurücksetzen")
        self.layer2_offset_x.valueChanged.connect(self._layer2_offset_changed)
        self.layer2_offset_y.valueChanged.connect(self._layer2_offset_changed)
        self.layer2_reset_button.clicked.connect(self.reset_layer2_layout)
        layer2_editor_layout.addWidget(layer2_editor_hint, 1)
        layer2_editor_layout.addWidget(QLabel("Gesamt X"))
        layer2_editor_layout.addWidget(self.layer2_offset_x)
        layer2_editor_layout.addWidget(QLabel("Gesamt Y"))
        layer2_editor_layout.addWidget(self.layer2_offset_y)
        layer2_editor_layout.addWidget(self.layer2_reset_button)
        self.layer2_editor_bar.setEnabled(False)
        outer.addWidget(self.layer2_editor_bar)

        self.media_directory_label = QLabel("Noch kein lokaler Designordner importiert")
        self.media_directory_label.setObjectName("muted")
        self.media_directory_label.setWordWrap(True)
        outer.addWidget(self.media_directory_label)

        self.canvas = ThermalrightCanvas(
            self._overlay_moved,
            self._remember_overlay_state,
            self._notch_resized_in_preview,
            layout_moved=self._layer2_block_moved,
            layout_edit_requested=self._open_layer2_inline_editor,
        )
        preview_stage = QFrame()
        preview_stage.setObjectName("levitaPreviewStage")
        preview_stage.setStyleSheet(
            "QFrame#levitaPreviewStage { background: rgba(8, 48, 76, 115); border-radius: 12px; }"
            "QFrame#layer2InlineEditor { background: rgba(4, 24, 42, 225); "
            "border: 1px solid rgba(54, 174, 243, 150); border-radius: 10px; }"
        )
        preview_stage_layout = QVBoxLayout(preview_stage)
        preview_stage_layout.setContentsMargins(12, 8, 12, 12)
        preview_title = QLabel("Live-Vorschau · Levita 1600 × 720 · Hintergrund + Ebene 2")
        preview_title.setObjectName("muted")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        preview_stage_layout.addWidget(preview_title)
        self.preview_canvas_row = QHBoxLayout()
        self.preview_canvas_row.setSpacing(12)
        self.preview_canvas_row.addWidget(self.canvas, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layer2_inline_editor = QFrame()
        self.layer2_inline_editor.setObjectName("layer2InlineEditor")
        self.layer2_inline_editor.setMinimumWidth(250)
        self.layer2_inline_editor.setMaximumWidth(300)
        inline_layout = QVBoxLayout(self.layer2_inline_editor)
        inline_layout.setContentsMargins(12, 12, 12, 12)
        self.layer2_inline_title = QLabel("Datenblock bearbeiten")
        self.layer2_inline_title.setObjectName("sectionTitle")
        inline_layout.addWidget(self.layer2_inline_title)
        self.layer2_inline_hint = QLabel(
            "Änderungen bleiben im OHC-Cache; das Original-Theme bleibt unverändert."
        )
        self.layer2_inline_hint.setWordWrap(True)
        self.layer2_inline_hint.setObjectName("muted")
        inline_layout.addWidget(self.layer2_inline_hint)
        inline_layout.addWidget(QLabel("Farbe · #RRGGBB"))
        color_row = QHBoxLayout()
        self.layer2_inline_color = QLineEdit()
        self.layer2_inline_color.setMaxLength(7)
        self.layer2_inline_color.textChanged.connect(self._update_layer2_inline_color_preview)
        self.layer2_inline_color_swatch = QLabel()
        self.layer2_inline_color_swatch.setFixedSize(32, 28)
        color_row.addWidget(self.layer2_inline_color, 1)
        color_row.addWidget(self.layer2_inline_color_swatch)
        inline_layout.addLayout(color_row)
        preset_row = QHBoxLayout()
        for color in ("#ffffff", "#36aef3", "#44d7b6", "#ffd166", "#ff6b6b"):
            preset = QPushButton()
            preset.setFixedSize(28, 24)
            preset.setToolTip(color)
            preset.setStyleSheet(f"background: {color}; border: 1px solid #6f8ba3;")
            preset.clicked.connect(
                lambda _checked=False, value=color: self.layer2_inline_color.setText(value)
            )
            preset_row.addWidget(preset)
        preset_row.addStretch(1)
        inline_layout.addLayout(preset_row)
        inline_layout.addWidget(QLabel("Schriftgröße"))
        self.layer2_inline_size = QSpinBox()
        self.layer2_inline_size.setRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
        self.layer2_inline_size.setSuffix(" px")
        inline_layout.addWidget(self.layer2_inline_size)
        self.layer2_inline_text_label = QLabel("Text / Bezeichnung / Vorlage")
        self.layer2_inline_text = QLineEdit()
        self.layer2_inline_text.setMaxLength(160)
        inline_layout.addWidget(self.layer2_inline_text_label)
        inline_layout.addWidget(self.layer2_inline_text)
        inline_layout.addStretch(1)
        apply_inline = QPushButton("Übernehmen")
        apply_inline.setObjectName("primaryAction")
        apply_inline.clicked.connect(self._apply_layer2_inline_editor)
        reset_inline = QPushButton("Block zurücksetzen")
        reset_inline.clicked.connect(self._reset_layer2_inline_editor)
        cancel_inline = QPushButton("Abbrechen")
        cancel_inline.clicked.connect(self._hide_layer2_inline_editor)
        inline_layout.addWidget(apply_inline)
        inline_layout.addWidget(reset_inline)
        inline_layout.addWidget(cancel_inline)
        self.layer2_inline_block_ident = ""
        self.layer2_inline_editor.hide()
        self.preview_canvas_row.addWidget(self.layer2_inline_editor, 0, Qt.AlignmentFlag.AlignTop)
        preview_stage_layout.addLayout(self.preview_canvas_row)
        outer.addWidget(preview_stage)

        self.geometry_box = QGroupBox("Levita-Displayeinstellungen · unabhängig von der NZXT Kraken")
        self.geometry_box.setObjectName("levitaGeometryBox")
        self.geometry_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        geometry_grid = QGridLayout(self.geometry_box)
        geometry_grid.setContentsMargins(16, 18, 16, 16)
        geometry_grid.setHorizontalSpacing(18)
        geometry_grid.setVerticalSpacing(12)
        geometry_grid.setColumnStretch(1, 1)
        geometry_grid.setColumnStretch(3, 1)
        self.background_x = QSpinBox()
        self.background_x.setRange(-600, 600)
        self.background_x.setSuffix(" px")
        self.background_x.setValue(int(self.settings.value(
            "thermalright/background_x", DEFAULT_BACKGROUND_OFFSET_X,
        ) or 0))
        self.background_y = QSpinBox()
        self.background_y.setRange(-300, 300)
        self.background_y.setSuffix(" px")
        self.background_y.setValue(int(self.settings.value(
            "thermalright/background_y", DEFAULT_BACKGROUND_OFFSET_Y,
        ) or 0))
        self.notch_visible = QCheckBox("Schwarzen Balken wirklich auf das Display legen")
        self.notch_visible.setMinimumHeight(READABLE_CONTROL_HEIGHT)
        self.notch_visible.setChecked(self.settings.value(
            "thermalright/notch_visible", True, type=bool,
        ))
        self.notch_width = QSpinBox()
        self.notch_width.setRange(LEVITA_CUTOUT_WIDTH, 800)
        self.notch_width.setSuffix(" px")
        notch_width_setting = bounded_notch_width(int(self.settings.value(
            "thermalright/notch_width", DEFAULT_NOTCH_MASK_WIDTH,
        ) or DEFAULT_NOTCH_MASK_WIDTH))
        # 3.4.29.33 adopts the physically required 80-pixel cutout as the
        # space-saving default for existing installations as well.  Apply the
        # migration once; later deliberate user adjustments remain untouched.
        if not self.settings.value("migration/v342933_minimal_levita_notch", False, type=bool):
            notch_width_setting = LEVITA_CUTOUT_WIDTH
            self.settings.setValue("thermalright/notch_width", notch_width_setting)
            self.settings.setValue("migration/v342933_minimal_levita_notch", True)
        self.notch_width.setValue(notch_width_setting)
        self.notch_radius_linked = QCheckBox("Oben und unten gemeinsam einstellen")
        self.notch_radius_linked.setMinimumHeight(READABLE_CONTROL_HEIGHT)
        self.notch_radius_linked.setChecked(self.settings.value(
            "thermalright/notch_radius_linked", True, type=bool,
        ))
        self.notch_top_radius = QSpinBox()
        self.notch_top_radius.setRange(0, MAX_INNER_CORNER_RADIUS)
        self.notch_top_radius.setSuffix(" px")
        self.notch_top_radius.setValue(bounded_inner_corner_radius(int(self.settings.value(
            "thermalright/notch_top_radius", DEFAULT_INNER_CORNER_RADIUS,
        ) or 0)))
        self.notch_bottom_radius = QSpinBox()
        self.notch_bottom_radius.setRange(0, MAX_INNER_CORNER_RADIUS)
        self.notch_bottom_radius.setSuffix(" px")
        self.notch_bottom_radius.setValue(bounded_inner_corner_radius(int(self.settings.value(
            "thermalright/notch_bottom_radius", self.notch_top_radius.value(),
        ) or 0)))
        if self.notch_radius_linked.isChecked():
            self.notch_bottom_radius.setValue(self.notch_top_radius.value())
        for spin in (
            self.background_x, self.background_y, self.notch_width,
            self.notch_top_radius, self.notch_bottom_radius,
        ):
            _readable_value_widget(spin)
        geometry_grid.addWidget(QLabel("Hintergrund X"), 0, 0)
        geometry_grid.addWidget(self.background_x, 0, 1)
        geometry_grid.addWidget(QLabel("Hintergrund Y"), 0, 2)
        geometry_grid.addWidget(self.background_y, 0, 3)
        geometry_grid.addWidget(self.notch_visible, 1, 0, 1, 4)
        geometry_grid.addWidget(QLabel("Balkenbreite"), 2, 0)
        geometry_grid.addWidget(self.notch_width, 2, 1)
        geometry_grid.addWidget(QLabel("Radius oben rechts"), 3, 0)
        geometry_grid.addWidget(self.notch_top_radius, 3, 1)
        geometry_grid.addWidget(QLabel("Radius unten rechts"), 3, 2)
        geometry_grid.addWidget(self.notch_bottom_radius, 3, 3)
        geometry_grid.addWidget(self.notch_radius_linked, 4, 0, 1, 4)
        self.media_scale_mode = QComboBox()
        self.media_scale_mode.addItem(
            "Einpassen · vollständig und unverzerrt", MEDIA_SCALE_CONTAIN,
        )
        self.media_scale_mode.addItem(
            "Ausfüllen · unverzerrt, Rand beschneiden", MEDIA_SCALE_COVER,
        )
        saved_scale = str(self.settings.value(
            "thermalright/media_scale_mode", MEDIA_SCALE_CONTAIN,
        ) or MEDIA_SCALE_CONTAIN)
        scale_index = self.media_scale_mode.findData(saved_scale)
        self.media_scale_mode.setCurrentIndex(max(0, scale_index))
        _readable_combo(self.media_scale_mode)
        geometry_grid.addWidget(QLabel("Bild-/Videoskalierung"), 5, 0)
        geometry_grid.addWidget(self.media_scale_mode, 5, 1, 1, 3)
        self.levita_brightness = QSpinBox()
        self.levita_brightness.setRange(0, 100)
        self.levita_brightness.setSuffix(" %")
        brightness_value = self.settings.value("thermalright/brightness", 100)
        self.levita_brightness.setValue(int(brightness_value if brightness_value is not None else 100))
        _readable_value_widget(self.levita_brightness)
        self.levita_orientation = QComboBox()
        for degrees in (0, 90, 180, 270):
            self.levita_orientation.addItem(f"{degrees}°", degrees)
        orientation = int(self.settings.value("thermalright/orientation", 0) or 0)
        self.levita_orientation.setCurrentIndex(max(0, self.levita_orientation.findData(orientation)))
        _readable_combo(self.levita_orientation, min_width=READABLE_SPIN_WIDTH)
        self.levita_hover_preview = QCheckBox("Videos beim Darüberfahren in der Karte animieren")
        self.levita_hover_preview.setMinimumHeight(READABLE_CONTROL_HEIGHT)
        self.levita_hover_preview.setChecked(self.settings.value("thermalright/hover_preview", True, type=bool))
        self.levita_hover_preview.toggled.connect(
            lambda checked: self.settings.setValue("thermalright/hover_preview", checked)
        )
        levita_display_apply = QPushButton("Levita-Helligkeit und Ausrichtung anwenden")
        levita_display_apply.setMinimumHeight(READABLE_CONTROL_HEIGHT)
        levita_display_apply.clicked.connect(self.apply_levita_display_settings)
        geometry_grid.addWidget(QLabel("Levita-Helligkeit"), 6, 0)
        geometry_grid.addWidget(self.levita_brightness, 6, 1)
        geometry_grid.addWidget(QLabel("Levita-Ausrichtung"), 6, 2)
        geometry_grid.addWidget(self.levita_orientation, 6, 3)
        geometry_grid.addWidget(self.levita_hover_preview, 7, 0, 1, 4)
        geometry_grid.addWidget(levita_display_apply, 8, 0, 1, 4)
        wide_preset = QPushButton("Maximale Bildfläche · minimaler 80-px-Notch")
        wide_preset.setMinimumHeight(READABLE_CONTROL_HEIGHT)
        wide_preset.clicked.connect(self.apply_wide_notch_preset)
        geometry_grid.addWidget(wide_preset, 9, 0, 1, 4)
        geometry_note = QLabel(
            "X/Y verschiebt eine lokal erzeugte Arbeitskopie; das importierte Original bleibt unverändert. "
            "Der schwarze Balken lässt sich direkt in der Vorschau ziehen. Die innere Kante der Bildfläche "
            f"ist oben und unten standardmäßig mit {DEFAULT_INNER_CORNER_RADIUS} px abgerundet; beide Radien "
            "können gekoppelt oder getrennt eingestellt und als echte Maske übertragen werden."
        )
        geometry_note.setWordWrap(True)
        geometry_note.setObjectName("muted")
        geometry_grid.addWidget(geometry_note, 10, 0, 1, 4)
        self.geometry_scroll = QScrollArea()
        self.geometry_scroll.setObjectName("levitaGeometryScroll")
        self.geometry_scroll.setWidgetResizable(True)
        self.geometry_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.geometry_scroll.setMinimumWidth(400)
        self.geometry_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.geometry_scroll.setMinimumHeight(432)
        self.geometry_scroll.setWidget(self.geometry_box)
        self.geometry_scroll.setVisible(False)
        self.preview_canvas_row.insertWidget(1, self.geometry_scroll, 1)
        self.geometry_toggle.toggled.connect(self.geometry_scroll.setVisible)
        self.background_x.valueChanged.connect(self._display_geometry_changed)
        self.background_y.valueChanged.connect(self._display_geometry_changed)
        self.notch_visible.toggled.connect(self._display_geometry_changed)
        self.notch_width.valueChanged.connect(self._display_geometry_changed)
        self.notch_radius_linked.toggled.connect(self._notch_radius_link_changed)
        self.notch_top_radius.valueChanged.connect(self._notch_top_radius_changed)
        self.notch_bottom_radius.valueChanged.connect(self._notch_bottom_radius_changed)
        self.media_scale_mode.currentIndexChanged.connect(self._media_scale_mode_changed)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Notch / Dynamic Island"))
        self.split_mode = QComboBox()
        self.split_mode.addItem("Aus · nur physische rechte Aussparung", 0)
        self.split_mode.addItem("Stil A · derzeit nur Vorschau", 1)
        self.split_mode.addItem("Stil B · derzeit nur Vorschau", 2)
        self.split_mode.addItem("Stil C · derzeit nur Vorschau", 3)
        _readable_combo(self.split_mode)
        saved_split_value = self.settings.value("thermalright/split_mode", 0)
        saved_split = safe_split_mode(saved_split_value)
        self.split_mode.setCurrentIndex(saved_split)
        self.split_mode.currentIndexChanged.connect(self._split_mode_changed)
        options_row.addWidget(self.split_mode)
        options_row.addStretch()
        self.preview_status = QLabel("Vorschau bereit")
        self.preview_status.setObjectName("muted")
        options_row.addWidget(self.preview_status)
        outer.addLayout(options_row)

        split_notice = QLabel(
            "Stile A–C bleiben vorerst auf die Vorschau beschränkt: TRCC Linux 9.9.11 bricht sie mit "
            "aktuellen PySide6-Versionen beim Spiegeln ab. Auf dem Display wird sicher auf „Aus“ zurückgesetzt; "
            "die physische rechte Aussparung bleibt geschützt."
        )
        split_notice.setWordWrap(True)
        split_notice.setObjectName("muted")
        outer.addWidget(split_notice)

        self.overlays_toggle = QToolButton()
        self.overlays_toggle.setText("✦ Eigene OHC-Einblendungen gestalten")
        self.overlays_toggle.setCheckable(True)
        self.overlays_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        outer.addWidget(self.overlays_toggle)
        self.custom_overlays_box = QGroupBox("Eigene OHC-Hardware-Infos · Alternative zum kompletten Hardware-Design")
        grid = QGridLayout(self.custom_overlays_box)
        for column, title in enumerate(("Ein", "Element", "X", "Y", "Größe", "Farbe")):
            grid.addWidget(QLabel(title), 0, column)
        for row, spec in enumerate(self.overlay_specs, start=1):
            visible = QCheckBox()
            visible.setChecked(spec.visible)
            label = QLabel(spec.label)
            x_spin = QSpinBox()
            x_spin.setRange(0, max(0, self._safe_right_x() - 1))
            x_spin.setValue(spec.x)
            y_spin = QSpinBox()
            y_spin.setRange(0, LEVITA_HEIGHT - 1)
            y_spin.setValue(spec.y)
            size_spin = QSpinBox()
            size_spin.setRange(12, 160)
            size_spin.setValue(spec.size)
            color_button = QPushButton(spec.color)
            color_button.setStyleSheet(f"color: {spec.color};")
            controls: dict[str, QWidget] = {
                "visible": visible, "x": x_spin, "y": y_spin,
                "size": size_spin, "color": color_button,
            }
            self.overlay_controls[spec.ident] = controls
            visible.toggled.connect(lambda checked, ident=spec.ident: self._overlay_control_changed(ident, visible=checked))
            x_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, x=value))
            y_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, y=value))
            size_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, size=value))
            color_button.clicked.connect(lambda _checked=False, ident=spec.ident: self._choose_overlay_color(ident))
            for column, widget in enumerate((visible, label, x_spin, y_spin, size_spin, color_button)):
                grid.addWidget(widget, row, column)
        reset_button = QPushButton("Hardware-Infos zurücksetzen")
        reset_button.clicked.connect(self.reset_overlays)
        grid.addWidget(reset_button, len(self.overlay_specs) + 1, 0)
        undo_button = QPushButton("Letzten Zustand wiederherstellen")
        undo_button.clicked.connect(self.undo_overlay_change)
        self.overlay_undo_button = undo_button
        self.overlay_undo_button.setEnabled(False)
        grid.addWidget(undo_button, len(self.overlay_specs) + 1, 1)
        two_rows_button = QPushButton("Zwei saubere Reihen")
        two_rows_button.clicked.connect(lambda: self.apply_overlay_layout("two_rows"))
        grid.addWidget(two_rows_button, len(self.overlay_specs) + 1, 2, 1, 2)
        vertical_button = QPushButton("Untereinander")
        vertical_button.clicked.connect(lambda: self.apply_overlay_layout("vertical"))
        grid.addWidget(vertical_button, len(self.overlay_specs) + 1, 4, 1, 2)
        outer.addWidget(self.custom_overlays_box)
        self.custom_overlays_box.setVisible(False)
        self.overlays_toggle.toggled.connect(self.custom_overlays_box.setVisible)

        action_row = QHBoxLayout()
        preview_button = QPushButton("Vorschau neu laden")
        preview_button.clicked.connect(self.reload_selected_preview)
        test_button = QPushButton("Display-Test · Rot/Grün/Blau/Schwarz")
        test_button.clicked.connect(self.run_display_test)
        stop_button = QPushButton("Übertragung anhalten")
        stop_button.clicked.connect(self.stop_display)
        action_row.addWidget(preview_button)
        action_row.addWidget(test_button)
        action_row.addWidget(stop_button)
        outer.addLayout(action_row)

        startup_row = QHBoxLayout()
        self.autostart_enabled = QCheckBox("Ausgewähltes Levita-Design bei OHC-Start automatisch laden")
        self.autostart_enabled.setChecked(self.settings.value(
            "thermalright/autostart_enabled", False, type=bool,
        ))
        self.autostart_enabled.toggled.connect(self._autostart_toggled)
        remember_startup = QPushButton("Aktuelle Auswahl als Startdesign speichern")
        remember_startup.clicked.connect(self.remember_startup_design)
        self.startup_status = QLabel()
        self.startup_status.setObjectName("muted")
        startup_row.addWidget(self.autostart_enabled)
        startup_row.addWidget(remember_startup)
        startup_row.addWidget(self.startup_status, 1)
        outer.addLayout(startup_row)
        self._refresh_startup_status()

        safety = QLabel(
            "Hardwarezugriff erfolgt ausschließlich über das separat installierte GPL-Backend TRCC Linux. "
            "OHC lädt keine Herstellerdesigns aus dem Internet und liefert die importierten Dateien nicht mit aus."
        )
        safety.setWordWrap(True)
        safety.setObjectName("warningText")
        outer.addWidget(safety)
        self.canvas.set_specs(self.overlay_specs)
        self.canvas.set_split_mode(saved_split)
        self.canvas.set_background_offset(self.background_x.value(), self.background_y.value())
        self.canvas.set_notch_mask(
            self.notch_visible.isChecked(),
            self.notch_width.value(),
            self.notch_top_radius.value(),
            self.notch_bottom_radius.value(),
        )

    def _load_overlays(self) -> list[OverlaySpec]:
        raw = str(self.settings.value("thermalright/overlays", "") or "")
        if not raw:
            return list(DEFAULT_OVERLAYS)
        try:
            values = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return list(DEFAULT_OVERLAYS)
        defaults = {item.ident: item for item in DEFAULT_OVERLAYS}
        loaded: list[OverlaySpec] = []
        if isinstance(values, list):
            for value in values:
                if not isinstance(value, dict) or value.get("ident") not in defaults:
                    continue
                base = defaults[str(value["ident"])]
                loaded.append(replace(
                    base,
                    x=int(value.get("x", base.x)), y=int(value.get("y", base.y)),
                    size=int(value.get("size", base.size)), color=str(value.get("color", base.color)),
                    visible=bool(value.get("visible", base.visible)),
                ).bounded())
        by_id = {item.ident: item for item in loaded}
        return [by_id.get(item.ident, item) for item in DEFAULT_OVERLAYS]

    def _save_overlays(self) -> None:
        self.settings.setValue("thermalright/overlays", json.dumps([asdict(item) for item in self.overlay_specs]))

    def _log(self, message: str) -> None:
        if self.log_ready and self.log_callback:
            self.log_callback(f"THERMALRIGHT: {message}")

    def _status(self, message: str, *, error: bool = False) -> None:
        self.preview_status.setText(message)
        self.preview_status.setObjectName("warningText" if error else "muted")
        self.preview_status.style().unpolish(self.preview_status)
        self.preview_status.style().polish(self.preview_status)
        self._log(message)

    def refresh_backend_status(self) -> None:
        self.cli = ThermalrightCli()
        if self.cli.available:
            self.backend_status.setText("TRCC-Linux-Backend gefunden · Gerät noch nicht geprüft")
        else:
            self.backend_status.setText("TRCC-Linux-Backend fehlt · Testmodus und Designimport funktionieren trotzdem")

    def _on_test_mode_changed(self, checked: bool) -> None:
        self.settings.setValue("thermalright/test_mode", checked)
        self._status("Testmodus aktiv · keine USB-Schreibzugriffe" if checked else "Hardwaremodus freigegeben · Aktionen benötigen TRCC Linux")

    def _autostart_toggled(self, checked: bool) -> None:
        self.settings.setValue("thermalright/autostart_enabled", checked)
        if checked:
            self._sync_autostart_selection_if_enabled()
        self._refresh_startup_status()
        if checked and self.test_mode.isChecked():
            self._status(
                "Startdesign gespeichert, aber Testmodus verhindert weiterhin USB-Schreibzugriffe",
                error=True,
            )

    def _refresh_startup_status(self) -> None:
        if not hasattr(self, "startup_status"):
            return
        media_value = str(self.settings.value("thermalright/start_media", "") or "")
        hardware_value = str(self.settings.value("thermalright/start_hardware_design", "") or "")
        if not media_value:
            self.startup_status.setText("Noch kein Startdesign gespeichert")
            return
        media = Path(media_value)
        hardware = Path(hardware_value) if hardware_value else None
        layer = hardware.name if hardware is not None else "OHC-Einblendungen"
        state = "aktiv" if self.autostart_enabled.isChecked() else "gespeichert, Automatik aus"
        self.startup_status.setText(f"{state}: {media.name} + {layer}")

    def remember_startup_design(self, _checked: bool = False) -> None:
        media = self.current_media_path()
        if media is None:
            self._status("Für den Autostart zuerst einen Hintergrund auswählen", error=True)
            return
        hardware = self.current_hardware_design_path()
        self.settings.setValue("thermalright/start_media", str(media.resolve()))
        self.settings.setValue(
            "thermalright/start_hardware_design", str(hardware.resolve()) if hardware else "",
        )
        self.autostart_enabled.setChecked(True)
        self._refresh_startup_status()
        self._status(
            "Aktuelle Ebenen als Levita-Startdesign gespeichert · globale Kraken-LCD-Aktionen bleiben getrennt"
        )

    def _sync_autostart_selection_if_enabled(self) -> None:
        if (
            self.restoring_startup_selection
            or not hasattr(self, "autostart_enabled")
            or not self.autostart_enabled.isChecked()
        ):
            return
        media = self.current_media_path()
        hardware = self.current_hardware_design_path()
        if media is None:
            return
        self.settings.setValue("thermalright/start_media", str(media.resolve()))
        self.settings.setValue(
            "thermalright/start_hardware_design", str(hardware.resolve()) if hardware else "",
        )
        self._refresh_startup_status()

    def _restore_startup_selection(self) -> bool:
        media_value = str(self.settings.value("thermalright/start_media", "") or "")
        hardware_value = str(self.settings.value("thermalright/start_hardware_design", "") or "")
        if not media_value or not Path(media_value).exists():
            self._status("Gespeichertes Levita-Startdesign ist nicht mehr vorhanden", error=True)
            return False
        self.restoring_startup_selection = True
        try:
            self.media_filter.clear()
            all_index = self.media_category.findData("all")
            if all_index >= 0:
                self.media_category.setCurrentIndex(all_index)
            hardware_index = self.hardware_design_combo.findData(hardware_value)
            if hardware_index < 0:
                hardware_index = 0
            self.hardware_design_combo.setCurrentIndex(hardware_index)
            self._apply_media_filter()
            media_index = self.media_combo.findData(media_value)
            if media_index < 0:
                self._status(
                    "Gespeichertes Startdesign passt nicht zur gewählten Datenebene oder wurde verschoben",
                    error=True,
                )
                return False
            self.media_combo.setCurrentIndex(media_index)
            return True
        finally:
            self.restoring_startup_selection = False

    def apply_startup_design_if_enabled(self, *, competing_lcd_action: bool = False) -> None:
        """Restore exactly one explicitly saved Levita design after desktop startup."""

        if self.startup_apply_requested:
            return
        self.startup_apply_requested = True
        if not self.autostart_enabled.isChecked():
            self._log("LCD-START: Levita-Autostart ist ausgeschaltet")
            return
        if competing_lcd_action:
            self._status(
                "LCD-START: Levita-Startdesign übersprungen · ein anderes LCD-Startprofil besitzt das Display",
                error=True,
            )
            return
        if self.test_mode.isChecked():
            self._status(
                "LCD-START: Startdesign wiederhergestellt, aber wegen aktivem Testmodus nicht an USB gesendet",
                error=True,
            )
            self._restore_startup_selection()
            return
        if not self._restore_startup_selection():
            return
        self.startup_apply_active = True
        self.startup_retry_count = 0
        self._log("LCD-START: gespeichertes Levita-Design wird nach der Desktop-Ruhezeit geladen")
        self.apply_design(startup=True)

    def _schedule_startup_retry(self, detail: str) -> None:
        if not self.startup_apply_active or self.startup_retry_count >= 1:
            self.startup_apply_active = False
            self._status(f"LCD-START: Levita-Startdesign konnte nicht geladen werden: {detail}", error=True)
            return
        self.startup_retry_count += 1
        self._status(
            "LCD-START: Display war noch nicht bereit · ein zweiter, begrenzter Versuch folgt in 3 Sekunden",
            error=True,
        )
        QTimer.singleShot(3000, lambda: self.apply_design(startup=True))

    def choose_media_directory(self) -> None:
        current = str(self.custom_media_directory or Path.home())
        selected = QFileDialog.getExistingDirectory(self, "Thermalright-Designordner auswählen", current)
        if selected:
            self.load_media_directory(Path(selected), remember_custom=True)
            self._select_library_source(Path(selected), prefer_saved_custom=True)

    def show_remembered_media_directory(self) -> None:
        if self.custom_media_directory is None or not self.custom_media_directory.is_dir():
            self._status("Der gemerkte Designordner ist nicht mehr vorhanden", error=True)
            return
        self.custom_media_enabled.blockSignals(True)
        self.custom_media_enabled.setChecked(True)
        self.custom_media_enabled.blockSignals(False)
        self.settings.setValue("thermalright/custom_media_enabled", True)
        self.load_media_directory(self.custom_media_directory, remember_custom=False)
        self._select_library_source(self.custom_media_directory, prefer_saved_custom=True)

    def _toggle_custom_media_directory(self, checked: bool) -> None:
        self.settings.setValue("thermalright/custom_media_enabled", checked)
        standard = default_trcc_design_directory()
        source = self.custom_media_directory if checked and self.custom_media_directory else standard
        if source is None:
            self.media_entries = []
            self._populate_media_categories()
            self._populate_hardware_design_combo()
            self._apply_media_filter()
            return
        self.load_media_directory(source, quiet=True, remember_custom=False)
        if checked and self.custom_media_directory is not None:
            self._select_library_source(self.custom_media_directory, prefer_saved_custom=True)
            self._status("Eigener Designordner wieder eingeblendet · gespeicherte Auswahl wiederhergestellt")
        else:
            self._select_library_source(standard, prefer_theme=True)
            self._status("Eigener Designordner aus OHC ausgeblendet · Dateien auf der Festplatte bleiben erhalten")

    def load_default_trcc_designs(self, _checked: bool = False, *, quiet: bool = False) -> None:
        directory = default_trcc_design_directory()
        if directory is None:
            if not quiet:
                self._status(
                    "Keine installierten TRCC-Standarddesigns für Levita 1600×720 gefunden",
                    error=True,
                )
            return
        self.load_media_directory(directory, quiet=True, remember_custom=False)
        self._select_library_source(directory, prefer_theme=True)
        if not quiet:
            self._status(
                "TRCC-Standarddesigns angezeigt · eigener Designordner bleibt gespeichert"
            )

    def load_media_directory(
        self, directory: Path, *, quiet: bool = False, remember_custom: bool = True,
    ) -> None:
        try:
            requested = directory.expanduser().resolve()
            roots: list[tuple[str, Path]] = []
            standard = default_trcc_design_directory()
            if standard is not None:
                roots.append(("TRCC-Standard", standard))
            if remember_custom:
                self.custom_media_directory = requested
                self.settings.setValue("thermalright/custom_media_directory", str(requested))
                self.settings.setValue("thermalright/media_directory", str(requested))
                self.settings.setValue("thermalright/custom_media_enabled", True)
                self.custom_media_enabled.blockSignals(True)
                self.custom_media_enabled.setChecked(True)
                self.custom_media_enabled.blockSignals(False)
                self.custom_media_enabled.setEnabled(True)
                self.remembered_media_button.setEnabled(True)
            custom = self.custom_media_directory
            if self.custom_media_enabled.isChecked() and custom is not None and custom != standard:
                roots.append(("Eigener Ordner", custom))
            if not roots and requested.is_dir():
                roots.append(("Ausgewählter Ordner", requested))
            entries: list[MediaEntry] = []
            seen: set[Path] = set()
            builtin_dir = Path(__file__).resolve().parent / "assets" / "levita-designs"
            builtin_names = (
                ("ohc-carbon-blue.png", "Carbon Blue"),
                ("ohc-titanium-blue.png", "Titanium Blue"),
                ("ohc-plasma-circuit.png", "Plasma Circuit"),
                ("ohc-ai-neon-corridor.png", "Neon Corridor"),
                ("ohc-ai-orbital-observatory.png", "Orbital Observatory"),
                ("ohc-ai-neon-city.png", "Neon City"),
                ("ohc-ai-azure-reactor.png", "Azure Reactor"),
                ("ohc-ai-deep-space-command.png", "Deep Space Command"),
                ("ohc-ai-quantum-portal.png", "Quantum Portal"),
                ("ohc-ai-crystal-core.png", "Crystal Core"),
                ("ohc-ai-command-deck.png", "Command Deck"),
            )
            for filename, title in builtin_names:
                path = (builtin_dir / filename).resolve()
                if path.is_file():
                    entries.append(MediaEntry(path, f"OHC-Designs / {title}", "image"))
                    seen.add(path)
            builtin_video = (builtin_dir / "ohc-ai-quantum-voyage-30s.mp4").resolve()
            if builtin_video.is_file():
                entries.append(MediaEntry(
                    builtin_video,
                    "OHC-Designs / Quantum Voyage · 30 s",
                    "video",
                ))
                seen.add(builtin_video)
            for dirname, title in (
                ("ohc-nebula-drift", "Nebula Drift"),
                ("ohc-orbital-command", "Orbital Command"),
            ):
                path = (builtin_dir / dirname).resolve()
                if trcc_theme_is_supported(path):
                    entries.append(MediaEntry(path, f"OHC-Designs / {title} · TRCC-Layout", "theme"))
                    seen.add(path)
            for label, root in roots:
                for entry in scan_media_directory(root):
                    if entry.path in seen:
                        continue
                    seen.add(entry.path)
                    entries.append(MediaEntry(
                        path=entry.path,
                        relative_name=f"{label} / {entry.relative_name}" if len(roots) > 1 else entry.relative_name,
                        kind=entry.kind,
                    ))
            entries, self.media_duplicate_map = deduplicate_media_entries(entries)
            self.media_duplicate_count = len(self.media_duplicate_map)
            self.media_entries = entries
            saved_selected = str(self.settings.value("thermalright/selected_media", "") or "")
            if saved_selected:
                try:
                    replacement = self.media_duplicate_map.get(Path(saved_selected).expanduser().resolve())
                except OSError:
                    replacement = None
                if replacement is not None:
                    saved_selected = str(replacement)
                    self.settings.setValue("thermalright/selected_media", saved_selected)
                    self.settings.setValue("thermalright/custom_selected_media", saved_selected)
            if not saved_selected or not Path(saved_selected).exists():
                preferred = next(
                    (
                        entry for entry in entries
                        if entry.path.is_relative_to(requested)
                        and (entry.kind != "theme" or str(entry.path) in self.background_theme_overrides)
                    ),
                    entries[0] if entries else None,
                )
                if preferred is not None:
                    self.settings.setValue("thermalright/selected_media", str(preferred.path))
        except ValueError as exc:
            self._status(str(exc), error=True)
            return
        catalog_count = sum(
            1 for entry in self.media_entries if media_category_key(entry) != "own"
        )
        custom_text = (
            f"eigener Ordner eingeblendet: {self.custom_media_directory}"
            if self.custom_media_enabled.isChecked() and self.custom_media_directory
            else f"eigener Ordner ausgeblendet: {self.custom_media_directory}"
            if self.custom_media_directory else "kein eigener Ordner gespeichert"
        )
        self.media_directory_label.setText(
            f"TRCC-Standard + {custom_text} · {len(self.media_entries)} lokale Designs · "
            f"{catalog_count} anhand ihrer originalen TRCC-ID kategorisiert"
            + (
                f" · {self.media_duplicate_count} gleiche Dateinamen nur einmal angezeigt"
                if self.media_duplicate_count else ""
            )
        )
        if self.media_duplicate_count:
            self._log(
                f"LCD-BIBLIOTHEK: {self.media_duplicate_count} doppelte Dateinamen ausgeblendet · "
                "Originaldateien bleiben unverändert"
            )
        self._populate_media_categories()
        self._populate_hardware_design_combo()
        self._apply_media_filter()
        if not quiet:
            self._status(
                f"{len(self.media_entries)} Designs lokal eingelesen"
                + (
                    f" · {self.media_duplicate_count} Duplikate nur im Katalog ausgeblendet"
                    if self.media_duplicate_count else ""
                )
                + " · keine Dateien kopiert oder gelöscht"
            )

    def _select_library_source(
        self, root: Path | None, *, prefer_saved_custom: bool = False, prefer_theme: bool = False,
    ) -> None:
        if root is None:
            return
        resolved = root.expanduser().resolve()
        candidates = [entry for entry in self.media_entries if entry.path.is_relative_to(resolved)]
        if not candidates:
            return
        saved = str(self.settings.value("thermalright/custom_selected_media", "") or "")
        selected = next((entry for entry in candidates if prefer_saved_custom and str(entry.path) == saved), None)
        if selected is None and prefer_theme:
            selected = next((entry for entry in candidates if entry.kind == "theme"), None)
        selected = selected or candidates[0]
        self.media_filter.clear()
        all_index = self.media_category.findData("all")
        if all_index >= 0:
            self.media_category.setCurrentIndex(all_index)
        if selected.kind == "theme" and str(selected.path) not in self.background_theme_overrides:
            index = self.hardware_design_combo.findData(str(selected.path))
            if index >= 0:
                self.hardware_design_combo.setCurrentIndex(index)
        else:
            self._apply_media_filter()
            index = self.media_combo.findData(str(selected.path))
            if index >= 0:
                self.media_combo.setCurrentIndex(index)

    def _populate_media_combo(self, entries: Iterable[MediaEntry]) -> None:
        saved_path = str(self.settings.value("thermalright/selected_media", "") or "")
        current_path = self.current_media_path() or (Path(saved_path) if saved_path else None)
        ordered = sorted(
            entries,
            key=media_catalog_sort_key,
        )
        available_paths = {entry.path for entry in ordered}
        if current_path is not None and current_path not in available_paths:
            current_path = Path(saved_path) if saved_path and Path(saved_path) in available_paths else None
        self.media_combo.blockSignals(True)
        self.media_combo.clear()
        selected_index = -1
        for entry in ordered:
            icon = "▣" if entry.kind == "theme" else "▶" if entry.kind == "video" else "▧"
            self.media_combo.addItem(f"{icon}  {entry.relative_name}", str(entry.path))
            if current_path and entry.path == current_path:
                selected_index = self.media_combo.count() - 1
        if self.media_combo.count():
            self.media_combo.setCurrentIndex(max(0, selected_index))
        self.media_combo.blockSignals(False)
        if self.media_combo.count():
            self.update_preview()
            self._show_selected_media_preview(self.media_combo.currentIndex())
            self._remember_media_selection(self.media_combo.currentIndex())
        self._rebuild_media_cards(ordered)

    def _populate_hardware_design_combo(self) -> None:
        saved = str(self.settings.value("thermalright/hardware_design", "") or "")
        current = str(self.hardware_design_combo.currentData() or saved)
        themes = sorted(
            (
                entry for entry in self.media_entries
                if entry.kind == "theme" and str(entry.path) not in self.background_theme_overrides
                and (not self.favorites_only.isChecked() or str(entry.path) in self.design_favorites)
            ),
            key=media_catalog_sort_key,
        )
        self.hardware_design_combo.blockSignals(True)
        self.hardware_design_combo.clear()
        self.hardware_design_combo.addItem("Eigene OHC-Werte · frei verschiebbar", "")
        selected_index = 0
        for entry in themes:
            self.hardware_design_combo.addItem(f"▣  {entry.relative_name}", str(entry.path))
            if str(entry.path) == current:
                selected_index = self.hardware_design_combo.count() - 1
        self.hardware_design_combo.setCurrentIndex(selected_index)
        self.hardware_design_combo.blockSignals(False)
        self.custom_overlays_box.setEnabled(selected_index == 0)
        self.settings.setValue(
            "thermalright/hardware_design",
            str(self.hardware_design_combo.currentData() or ""),
        )
        self._rebuild_hardware_cards(themes)

    def _populate_media_categories(self) -> None:
        current = str(self.settings.value(
            "thermalright/media_category", self.media_category.currentData() or "all",
        ) or "all")
        counts: dict[str, int] = {}
        for entry in self.media_entries:
            if entry.kind == "theme" and str(entry.path) not in self.background_theme_overrides:
                continue
            key = media_category_key(entry)
            counts[key] = counts.get(key, 0) + 1
        self.media_category.blockSignals(True)
        self.media_category.clear()
        background_count = sum(counts.values())
        self.media_category.addItem(f"Alle Hintergründe · {background_count}", "all")
        for key, label in MEDIA_CATEGORY_LABELS.items():
            if counts.get(key):
                self.media_category.addItem(f"{label} · {counts[key]}", key)
        index = self.media_category.findData(current)
        self.media_category.setCurrentIndex(max(0, index))
        self.media_category.blockSignals(False)
        while self.category_layout.count():
            item = self.category_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.category_buttons.clear()
        for index in range(self.media_category.count()):
            key = str(self.media_category.itemData(index))
            button = QToolButton()
            button.setText(self.media_category.itemText(index))
            button.setCheckable(True)
            button.setChecked(key == current)
            button.setStyleSheet(
                "QToolButton { padding: 7px 11px; border-radius: 9px; } "
                "QToolButton:checked { background: rgba(25, 145, 230, 150); border: 1px solid #42b8ff; }"
            )
            button.clicked.connect(lambda _checked=False, value=key: self._select_media_category(value))
            self.category_group.addButton(button)
            self.category_layout.addWidget(button)
            self.category_buttons[key] = button
        self.category_layout.addStretch()

    def _apply_media_filter(self, _value: object = None) -> None:
        needle = self.media_filter.text().strip().casefold()
        category = str(self.media_category.currentData() or "all")
        self._populate_media_combo(
            entry for entry in self.media_entries
            if (category == "all" or media_category_key(entry) == category)
            and (not needle or needle in entry.relative_name.casefold())
            and (entry.kind != "theme" or str(entry.path) in self.background_theme_overrides)
            and (not self.favorites_only.isChecked() or str(entry.path) in self.design_favorites)
        )

    def _refresh_design_cards(self, _checked: bool = False) -> None:
        self._populate_hardware_design_combo()
        self._apply_media_filter()

    def _select_media_category(self, category: str) -> None:
        index = self.media_category.findData(category)
        if index >= 0:
            self.settings.setValue("thermalright/media_category", category)
            self.media_category.setCurrentIndex(index)

    @staticmethod
    def _clear_grid(layout: QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _card_thumbnail(self, entry: MediaEntry | None) -> QPixmap:
        source: Path | None = None
        if entry is not None and entry.path.is_dir():
            source = next(
                (entry.path / name for name in ("Theme.png", "00.png") if (entry.path / name).is_file()),
                None,
            )
        elif entry is not None and entry.path.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES:
            source = entry.path
        elif entry is not None and entry.kind == "video":
            source = self._video_card_thumbnail(entry.path)
        pixmap = QPixmap(str(source)) if source else QPixmap()
        if pixmap.isNull():
            pixmap = QPixmap(320, 144)
            pixmap.fill(QColor("#071522"))
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor("#36aef3"), 3))
            painter.drawRoundedRect(5, 5, 310, 134, 15, 15)
            painter.setPen(QColor("#9ad9ff"))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "▶ VIDEO" if entry else "OHC\nLIVE-WERTE")
            painter.end()
        return pixmap.scaled(
            176, 79, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        ).copy(0, 0, 176, 79)

    def _video_card_thumbnail(self, media: Path) -> Path | None:
        cache_paths = self._thumbnail_cache_paths(media)
        if cache_paths is None:
            return None
        key, target, _failure = cache_paths
        if target.is_file() and target.stat().st_size > 0:
            return target
        return None

    def _thumbnail_cache_paths(self, media: Path) -> tuple[str, Path, Path] | None:
        try:
            stat = media.stat()
        except OSError:
            return None
        fingerprint = hashlib.sha256(
            f"card:{media.resolve()}:{stat.st_size}:{stat.st_mtime_ns}".encode("utf-8")
        ).hexdigest()[:20]
        target = self.cache_dir / f"card-{fingerprint}.jpg"
        return fingerprint, target, self.cache_dir / f"card-{fingerprint}.failed"

    @staticmethod
    def _thumbnail_failure_is_recent(failure: Path) -> bool:
        try:
            return failure.is_file() and time.time() - failure.stat().st_mtime < 21_600
        except OSError:
            return False

    def _queue_video_thumbnail(
        self, media: Path, button: QToolButton | None = None,
    ) -> Path | None:
        cache_paths = self._thumbnail_cache_paths(media)
        if cache_paths is None:
            return None
        key, target, failure = cache_paths
        if target.is_file() and target.stat().st_size > 0:
            return target
        if self._thumbnail_failure_is_recent(failure) or not self.thumbnail_ffmpeg:
            return None
        if failure.exists():
            try:
                failure.unlink()
            except OSError:
                pass
        if button is not None:
            self.thumbnail_waiters.setdefault(key, []).append(weakref.ref(button))
        if key in self.thumbnail_queued:
            return None
        if not self.thumbnail_queue and not self.thumbnail_active and self.thumbnail_finished >= self.thumbnail_total:
            self.thumbnail_total = 0
            self.thumbnail_finished = 0
            self.thumbnail_generated = 0
            self.thumbnail_failed = 0
            self._log(
                "LCD-VORSCHAUCACHE: neue/geänderte Videos werden mit höchstens zwei "
                "ffmpeg-Prozessen im Hintergrund vorbereitet"
            )
        self.thumbnail_queued.add(key)
        self.thumbnail_queue.append((key, media.resolve(), target, failure))
        self.thumbnail_total += 1
        self._update_thumbnail_progress()
        self._start_thumbnail_workers()
        return None

    def _start_thumbnail_workers(self) -> None:
        if not self.thumbnail_ffmpeg or self.thumbnail_shutting_down:
            return
        for worker in self.thumbnail_workers:
            if worker in self.thumbnail_active or not self.thumbnail_queue:
                continue
            item = self.thumbnail_queue.pop(0)
            _key, media, target, _failure = item
            self.thumbnail_active[worker] = item
            worker.start(self.thumbnail_ffmpeg, [
                "-v", "error", "-nostdin", "-ss", "0.15", "-i", str(media),
                "-frames:v", "1", "-q:v", "5", "-y", str(target),
            ])
            self.thumbnail_worker_timeouts[worker].start()

    def _cancel_thumbnail_worker(self, worker: QProcess) -> None:
        if worker in self.thumbnail_active and worker.state() != QProcess.ProcessState.NotRunning:
            worker.kill()

    def _on_thumbnail_finished(
        self, worker: QProcess, exit_code: int, _status: QProcess.ExitStatus,
    ) -> None:
        if self.thumbnail_shutting_down:
            return
        self.thumbnail_worker_timeouts[worker].stop()
        item = self.thumbnail_active.pop(worker, None)
        if item is None:
            return
        key, media, target, failure = item
        pixmap = QPixmap(str(target)) if exit_code == 0 and target.is_file() else QPixmap()
        success = not pixmap.isNull()
        if success:
            self.thumbnail_generated += 1
            try:
                failure.unlink(missing_ok=True)
            except OSError:
                pass
        else:
            self.thumbnail_failed += 1
            try:
                target.unlink(missing_ok=True)
                failure.write_text("thumbnail extraction failed\n", encoding="utf-8")
            except OSError:
                pass
        self.thumbnail_queued.discard(key)
        if success:
            card_pixmap = pixmap.scaled(
                176, 79, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            ).copy(0, 0, 176, 79)
            for button_ref in self.thumbnail_waiters.pop(key, []):
                button = button_ref()
                if button is None:
                    continue
                try:
                    button.setIcon(QIcon(card_pixmap))
                except RuntimeError:
                    pass
            current = self.current_media_path()
            if current is not None and current.resolve() == media:
                self.update_preview()
        else:
            self.thumbnail_waiters.pop(key, None)
        self.thumbnail_finished += 1
        self._update_thumbnail_progress()
        self._start_thumbnail_workers()

    def _update_thumbnail_progress(self) -> None:
        if not hasattr(self, "thumbnail_progress_panel"):
            return
        self.thumbnail_progress_panel.show()
        self.thumbnail_progress.setRange(0, max(1, self.thumbnail_total))
        self.thumbnail_progress.setValue(min(self.thumbnail_finished, self.thumbnail_total))
        pending = len(self.thumbnail_queue) + len(self.thumbnail_active)
        if pending:
            self.thumbnail_progress_label.setText(
                f"Videovorschauen werden im Hintergrund geladen · {pending} ausstehend · Oberfläche bleibt bedienbar"
            )
            return
        self.thumbnail_progress_label.setText(
            f"Videovorschauen bereit · {self.thumbnail_generated} neu gespeichert"
            + (f" · {self.thumbnail_failed} nicht lesbar" if self.thumbnail_failed else "")
            + " · Cache bleibt für nächste Programmstarts erhalten"
        )
        self._log(
            f"LCD-VORSCHAUCACHE: fertig · {self.thumbnail_generated} neu gespeichert · "
            f"{self.thumbnail_failed} nicht lesbar · dauerhafter Cache={self.cache_dir}"
        )
        QTimer.singleShot(4_000, self._hide_thumbnail_progress_if_idle)

    def _hide_thumbnail_progress_if_idle(self) -> None:
        if not self.thumbnail_queue and not self.thumbnail_active:
            self.thumbnail_progress_panel.hide()

    def _design_card(self, entry: MediaEntry | None, *, hardware: bool = False) -> QToolButton:
        title = "Eigene OHC-Werte" if entry is None else entry.relative_name.rsplit("/", 1)[-1].replace(" · TRCC-Layout", "")
        subtitle = "frei verschiebbar" if entry is None else {
            "theme": "Live-Layout",
            "video": "Video",
            "image": "Bild",
        }.get(entry.kind, "Design")
        holder: dict[str, QToolButton] = {}
        button = _PreviewCardButton(
            lambda value=entry, ref=holder: self._card_hover_enter(ref.get("button"), value),
            lambda value=entry, ref=holder: self._card_hover_leave(ref.get("button"), value),
        )
        holder["button"] = button
        button.setCheckable(True)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setIcon(QIcon(self._card_thumbnail(entry)))
        button.setIconSize(QSize(DESIGN_CARD_WIDTH - 16, 79))
        favorite_key = "ohc://overlays" if entry is None else str(entry.path)
        favorite = favorite_key in self.design_favorites
        button.setText(f"{'★ ' if favorite else ''}{title[:23]}\n{subtitle}")
        button.setFixedSize(DESIGN_CARD_WIDTH, 126)
        button.setStyleSheet(
            "QToolButton { padding: 5px; border: 1px solid rgba(90,145,185,90); border-radius: 10px; "
            "background: rgba(7,20,32,170); } "
            "QToolButton:hover { border-color: #4dbdff; background: rgba(12,39,60,210); } "
            "QToolButton:checked { border: 2px solid #20aaff; background: rgba(13,66,99,220); }"
        )
        path = "" if entry is None else str(entry.path)
        if entry is not None and entry.kind == "video":
            self._queue_video_thumbnail(entry.path, button)
        if hardware:
            button.clicked.connect(lambda _checked=False, value=path: self._select_hardware_card(value))
        else:
            button.clicked.connect(lambda _checked=False, value=path: self._select_media_card(value))
        button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda point, value=entry, is_hardware=hardware, source=button:
            self._show_design_card_menu(source, point, value, is_hardware)
        )
        button.setToolTip("Linksklick: auswählen · Rechtsklick: Favorit und Ebenenzuordnung")
        return button

    def _show_design_card_menu(
        self, button: QToolButton, point, entry: MediaEntry | None, hardware: bool,
    ) -> None:
        key = "ohc://overlays" if entry is None else str(entry.path)
        menu = QMenu(button)
        favorite = menu.addAction(
            "★ Aus Favoriten entfernen" if key in self.design_favorites else "☆ Zu Favoriten hinzufügen"
        )
        favorite.triggered.connect(lambda _checked=False, value=key: self._toggle_design_favorite(value))
        if entry is not None and entry.kind == "theme":
            menu.addSeparator()
            layer1 = menu.addAction("Als Ebene 1 · Hintergrund verwenden")
            layer2 = menu.addAction("Als Ebene 2 · Datenoberfläche verwenden")
            layer1.setEnabled(hardware)
            layer2.setEnabled(not hardware)
            layer1.triggered.connect(lambda: self._move_theme_path(entry.path, to_background=True))
            layer2.triggered.connect(lambda: self._move_theme_path(entry.path, to_background=False))
        menu.exec(button.mapToGlobal(point))

    def _toggle_design_favorite(self, key: str) -> None:
        if key in self.design_favorites:
            self.design_favorites.remove(key)
        else:
            self.design_favorites.add(key)
        self.settings.setValue(
            "thermalright/design_favorites", json.dumps(sorted(self.design_favorites)),
        )
        self._refresh_design_cards()

    def _move_theme_path(self, design: Path, *, to_background: bool) -> None:
        path = str(design.resolve())
        if to_background:
            self.background_theme_overrides.add(path)
        else:
            self.background_theme_overrides.discard(path)
        self._save_theme_layer_overrides()
        self._populate_media_categories()
        self._refresh_design_cards()
        target = self.media_combo if to_background else self.hardware_design_combo
        index = target.findData(path)
        if index >= 0:
            target.setCurrentIndex(index)
        self._status(
            f"{design.name} ist jetzt {'Ebene 1 · Hintergrund' if to_background else 'Ebene 2 · Datenoberfläche'}"
        )

    def _card_hover_enter(self, button: QToolButton | None, entry: MediaEntry | None) -> None:
        if button is None or entry is None or entry.kind != "video" or not self.levita_hover_preview.isChecked():
            return
        self.hover_card_button = button
        self.hover_card_entry = entry
        self._show_path_preview_tile(entry.path, entry.kind)

    def _card_hover_leave(self, button: QToolButton | None, entry: MediaEntry | None) -> None:
        if button is None or entry is None or button is not self.hover_card_button:
            return
        button.setIcon(QIcon(self._card_thumbnail(entry)))
        self.hover_card_button = None
        self.hover_card_entry = None

    def _rebuild_media_cards(self, entries: Iterable[MediaEntry]) -> None:
        self._visible_media_entries = list(entries)[:300]
        self._media_gallery_columns = self._gallery_columns(
            self.media_cards_scroll, *MEDIA_GALLERY_COLUMNS,
        )
        self._clear_grid(self.media_cards_grid)
        self.media_card_buttons.clear()
        current = str(self.current_media_path() or "")
        columns = self._media_gallery_columns
        for position, entry in enumerate(self._visible_media_entries):
            button = self._design_card(entry)
            button.setChecked(str(entry.path) == current)
            self.media_cards_grid.addWidget(button, position // columns, position % columns)
            self.media_card_buttons[str(entry.path)] = button

    def _rebuild_hardware_cards(self, themes: Iterable[MediaEntry]) -> None:
        self._visible_hardware_themes = list(themes)
        self._hardware_gallery_columns = self._gallery_columns(
            self.hardware_cards_scroll, *HARDWARE_GALLERY_COLUMNS,
        )
        self._clear_grid(self.hardware_cards_grid)
        self.hardware_card_buttons.clear()
        current = str(self.current_hardware_design_path() or "")
        entries: list[MediaEntry | None] = [*self._visible_hardware_themes]
        if not self.favorites_only.isChecked() or "ohc://overlays" in self.design_favorites:
            entries.insert(0, None)
        columns = self._hardware_gallery_columns
        for position, entry in enumerate(entries[:160]):
            button = self._design_card(entry, hardware=True)
            path = "" if entry is None else str(entry.path)
            button.setChecked(path == current)
            self.hardware_cards_grid.addWidget(button, position // columns, position % columns)
            self.hardware_card_buttons[path] = button

    def _gallery_columns(self, area: QScrollArea, minimum: int, maximum: int) -> int:
        return gallery_column_count(max(area.viewport().width(), area.width()), minimum=minimum, maximum=maximum)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        if hasattr(self, "media_cards_scroll"):
            self._relayout_design_galleries()

    def _relayout_design_galleries(self) -> None:
        media_columns = self._gallery_columns(self.media_cards_scroll, *MEDIA_GALLERY_COLUMNS)
        hardware_columns = self._gallery_columns(self.hardware_cards_scroll, *HARDWARE_GALLERY_COLUMNS)
        if media_columns != self._media_gallery_columns:
            self._rebuild_media_cards(self._visible_media_entries)
        if hardware_columns != self._hardware_gallery_columns:
            self._rebuild_hardware_cards(self._visible_hardware_themes)

    def _select_media_card(self, path: str) -> None:
        index = self.media_combo.findData(path)
        if index >= 0:
            changed = index != self.media_combo.currentIndex()
            self.media_combo.setCurrentIndex(index)
            # Do not depend on the combo-box signal order: the clicked card
            # must paint Ebene 1 in the large preview during this event turn.
            if changed:
                self._remember_media_selection(index)
            media = Path(path)
            if media.suffix.casefold() in SUPPORTED_VIDEO_SUFFIXES:
                self._prioritize_video_thumbnail(media)
            self.reload_selected_preview()

    def _prioritize_video_thumbnail(self, media: Path) -> None:
        cache_paths = self._thumbnail_cache_paths(media)
        if cache_paths is None:
            return
        key, _target, _failure = cache_paths
        pending = [item for item in self.thumbnail_queue if item[0] == key]
        if pending:
            self.thumbnail_queue = pending + [item for item in self.thumbnail_queue if item[0] != key]
            return
        self._queue_video_thumbnail(media)

    def _select_hardware_card(self, path: str) -> None:
        index = self.hardware_design_combo.findData(path)
        if index >= 0:
            unchanged = index == self.hardware_design_combo.currentIndex()
            self.hardware_design_combo.setCurrentIndex(index)
            if unchanged:
                self.update_preview()

    def _remember_media_selection(self, _index: int = -1) -> None:
        path = str(self.current_media_path() or "")
        self.settings.setValue("thermalright/selected_media", path)
        if path and self.custom_media_directory is not None:
            try:
                Path(path).resolve().relative_to(self.custom_media_directory)
                self.settings.setValue("thermalright/custom_selected_media", path)
            except ValueError:
                pass
        for key, button in self.media_card_buttons.items():
            button.setChecked(key == path)
        self._sync_autostart_selection_if_enabled()

    def _save_theme_layer_overrides(self) -> None:
        self.settings.setValue(
            "thermalright/background_theme_overrides",
            json.dumps(sorted(self.background_theme_overrides)),
        )

    def move_selected_theme_to_background_layer(self) -> None:
        design = self.current_hardware_design_path()
        if design is None:
            self._status("In Ebene 2 zuerst ein komplettes Theme auswählen", error=True)
            return
        path = str(design.resolve())
        self.background_theme_overrides.add(path)
        self._save_theme_layer_overrides()
        self._populate_hardware_design_combo()
        self._populate_media_categories()
        self._apply_media_filter()
        index = self.media_combo.findData(path)
        if index >= 0:
            self.media_combo.setCurrentIndex(index)
        self._status(f"{design.name} bewusst nach Ebene 1 verschoben")

    def move_selected_theme_to_data_layer(self) -> None:
        media = self.current_media_path()
        if media is None or str(media.resolve()) not in self.background_theme_overrides:
            self._status("Diese Auswahl ist bereits ein normaler Hintergrund", error=True)
            return
        path = str(media.resolve())
        self.background_theme_overrides.discard(path)
        self._save_theme_layer_overrides()
        self._populate_hardware_design_combo()
        self._populate_media_categories()
        self._apply_media_filter()
        index = self.hardware_design_combo.findData(path)
        if index >= 0:
            self.hardware_design_combo.setCurrentIndex(index)
        self._status(f"{media.name} wieder als Datenoberfläche in Ebene 2 eingeordnet")

    def current_media_path(self) -> Path | None:
        raw = self.media_combo.currentData() if hasattr(self, "media_combo") else None
        return Path(str(raw)) if raw else None

    def current_hardware_design_path(self) -> Path | None:
        raw = self.hardware_design_combo.currentData() if hasattr(self, "hardware_design_combo") else None
        return Path(str(raw)) if raw else None

    @staticmethod
    def _layer2_key(design: Path) -> str:
        return str(design.expanduser().resolve())

    @staticmethod
    def _default_layer2_intensity(design: Path | None) -> int:
        # Orbital's fine cyan HUD lines need more presence on the physical
        # Levita glass. Nebula Drift deliberately keeps its quiet depth.
        return 130 if design is not None and design.name == "ohc-orbital-command" else 100

    def _current_layer2_intensity(self) -> int:
        design = self.current_hardware_design_path()
        key = self._layer2_key(design) if design is not None else "__ohc_custom__"
        return bounded_layer_intensity(
            self.layer2_intensity_overrides.get(key, self._default_layer2_intensity(design))
        )

    def _save_layer2_intensities(self) -> None:
        self.settings.setValue(
            "thermalright/layer2_intensity_overrides",
            json.dumps(self.layer2_intensity_overrides, ensure_ascii=False, sort_keys=True),
        )

    def _sync_layer2_intensity_control(self) -> None:
        value = self._current_layer2_intensity()
        self.layer2_intensity_slider.blockSignals(True)
        self.layer2_intensity_slider.setValue(value)
        self.layer2_intensity_slider.blockSignals(False)
        self.layer2_intensity_label.setText(f"{value} %")

    def _layer1_intensity_changed(self, value: int) -> None:
        self.layer1_intensity_percent = bounded_layer_intensity(value)
        self.layer1_intensity_label.setText(f"{self.layer1_intensity_percent} %")
        self.settings.setValue("thermalright/layer1_intensity", self.layer1_intensity_percent)
        self.canvas.set_layer_intensities(
            self.layer1_intensity_percent, self._current_layer2_intensity()
        )
        self.update_preview()

    def _layer2_intensity_changed(self, value: int) -> None:
        design = self.current_hardware_design_path()
        key = self._layer2_key(design) if design is not None else "__ohc_custom__"
        level = bounded_layer_intensity(value)
        self.layer2_intensity_overrides[key] = level
        self._save_layer2_intensities()
        self.layer2_intensity_label.setText(f"{level} %")
        self.canvas.set_layer_intensities(self.layer1_intensity_percent, level)
        self.update_preview()

    def _save_layer2_overrides(self) -> None:
        self.settings.setValue(
            "thermalright/layer2_overrides_v1",
            serialize_layout_overrides(self.layer2_overrides),
        )

    def _load_layer2_layout(self, design: Path) -> EditableLayout | None:
        key = self._layer2_key(design)
        if key not in self.layer2_originals and key not in self.layer2_load_errors:
            try:
                original, config = load_editable_layout(design)
            except ThemeLayoutError as exc:
                self.layer2_load_errors[key] = str(exc)
            else:
                if design.name in {"ohc-nebula-drift", "ohc-orbital-command"}:
                    original = restore_explicit_format_units(original)
                self.layer2_originals[key] = original
                self.layer2_configs[key] = dict(config)
        if key in self.layer2_load_errors:
            return None
        selected = self.layer2_overrides.get(key, self.layer2_originals.get(key))
        if selected is not None and design.name in {"ohc-nebula-drift", "ohc-orbital-command"}:
            migrated = restore_explicit_format_units(selected)
            if key in self.layer2_overrides and migrated != selected:
                self.layer2_overrides[key] = migrated
                self._save_layer2_overrides()
            selected = migrated
        return selected

    def _current_layer2_layout(self) -> EditableLayout | None:
        design = self.current_hardware_design_path()
        return self._load_layer2_layout(design) if design is not None else None

    def _store_current_layer2_layout(self, layout: EditableLayout) -> None:
        design = self.current_hardware_design_path()
        if design is None:
            return
        key = self._layer2_key(design)
        self.layer2_overrides[key] = layout.bounded(safe_right_x=self._safe_right_x())
        self._save_layer2_overrides()
        self._sync_layer2_controls()
        self.canvas.set_editable_layout(adjust_layout_intensity(
            self.layer2_overrides[key], self._current_layer2_intensity(),
        ))

    def _sync_layer2_controls(self) -> None:
        layout = self._current_layer2_layout()
        enabled = layout is not None
        self.layer2_editor_bar.setEnabled(enabled)
        for widget, value in (
            (self.layer2_offset_x, layout.offset_x if layout else 0),
            (self.layer2_offset_y, layout.offset_y if layout else 0),
        ):
            widget.blockSignals(True)
            widget.setValue(value)
            widget.blockSignals(False)

    def _layer2_offset_changed(self) -> None:
        layout = self._current_layer2_layout()
        if layout is None:
            return
        self._store_current_layer2_layout(replace(
            layout,
            offset_x=self.layer2_offset_x.value(),
            offset_y=self.layer2_offset_y.value(),
        ))
        self._status("Gesamte Ebene 2 verschoben · einzelne Blöcke bleiben gemeinsam relativ angeordnet")

    def _layer2_block_moved(self, ident: str, x: int, y: int) -> None:
        layout = self._current_layer2_layout()
        if layout is None:
            return
        self._store_current_layer2_layout(layout.replace_block(ident, x=x, y=y))
        block = next((item for item in layout.blocks if item.ident == ident), None)
        self._status(f"{block.label if block else 'Datenblock'} frei positioniert · Original-Theme bleibt unverändert")

    def _open_layer2_inline_editor(self, block: LayoutBlock) -> None:
        """Expose block properties inside the preview stage without a popup window."""

        self.layer2_inline_block_ident = block.ident
        self.layer2_inline_title.setText(f"{block.label} bearbeiten")
        for widget in (self.layer2_inline_color, self.layer2_inline_size, self.layer2_inline_text):
            widget.blockSignals(True)
        self.layer2_inline_color.setText(block.color)
        self.layer2_inline_size.setValue(block.size)
        self.layer2_inline_text.setText(block.editable_text)
        for widget in (self.layer2_inline_color, self.layer2_inline_size, self.layer2_inline_text):
            widget.blockSignals(False)
        text_editable = block.kind != "clock"
        self.layer2_inline_text_label.setVisible(text_editable)
        self.layer2_inline_text.setVisible(text_editable)
        self.layer2_inline_hint.setText(
            "Uhrinhalt bleibt live; Farbe und Schriftgröße können hier geändert werden."
            if not text_editable else
            "Text, Farbe und Größe werden nur im OHC-Cache gespeichert; das Original bleibt unverändert."
        )
        self._update_layer2_inline_color_preview(block.color)
        self.layer2_inline_editor.show()
        self._status(f"{block.label}: Bearbeitung rechts neben der Vorschau geöffnet")

    def _update_layer2_inline_color_preview(self, value: str) -> None:
        color = QColor(str(value).strip())
        valid = len(str(value).strip()) == 7 and str(value).strip().startswith("#") and color.isValid()
        fill = color.name() if valid else "#2a1018"
        border = "#8ba2b5" if valid else "#ff526f"
        self.layer2_inline_color_swatch.setStyleSheet(
            f"background: {fill}; border: 2px solid {border}; border-radius: 5px;"
        )

    def _apply_layer2_inline_editor(self, _checked: bool = False) -> None:
        layout = self._current_layer2_layout()
        ident = self.layer2_inline_block_ident
        block = next((item for item in layout.blocks if item.ident == ident), None) if layout else None
        if block is None:
            self._hide_layer2_inline_editor()
            return
        color_text = self.layer2_inline_color.text().strip()
        color = QColor(color_text)
        if len(color_text) != 7 or not color_text.startswith("#") or not color.isValid():
            self._status("Farbe bitte als #RRGGBB eingeben", error=True)
            self.layer2_inline_color.setFocus()
            return
        changes: dict[str, object] = {
            "color": color.name(),
            "size": self.layer2_inline_size.value(),
        }
        if block.kind != "clock" and self.layer2_inline_text.text().strip():
            changes["editable_text"] = self.layer2_inline_text.text().strip()
        self._layer2_block_edited(ident, changes)
        self._hide_layer2_inline_editor()

    def _reset_layer2_inline_editor(self, _checked: bool = False) -> None:
        ident = self.layer2_inline_block_ident
        if ident:
            self._reset_layer2_block(ident)
        self._hide_layer2_inline_editor()

    def _hide_layer2_inline_editor(self, _checked: bool = False) -> None:
        self.layer2_inline_block_ident = ""
        self.layer2_inline_editor.hide()

    def _layer2_block_edited(self, ident: str, changes: dict[str, object]) -> None:
        layout = self._current_layer2_layout()
        if layout is None:
            return
        updated: list[LayoutBlock] = []
        changed_label = "Datenblock"
        for block in layout.blocks:
            if block.ident != ident:
                updated.append(block)
                continue
            changed_label = block.label
            editable_text = changes.get("editable_text")
            if isinstance(editable_text, str):
                block = block.with_edited_text(editable_text)
            safe_changes = {
                key: value for key, value in changes.items()
                if key in {"color", "size", "x", "y", "bold", "italic"}
            }
            if safe_changes:
                block = replace(block, **safe_changes).bounded(safe_right_x=self._safe_right_x())
            updated.append(block)
        self._store_current_layer2_layout(replace(layout, blocks=tuple(updated)))
        self._status(f"{changed_label} angepasst · Live-Wert und Bezeichnung bleiben ein gemeinsamer Block")

    def _reset_layer2_block(self, ident: str) -> None:
        design = self.current_hardware_design_path()
        layout = self._current_layer2_layout()
        if design is None or layout is None:
            return
        original = self.layer2_originals.get(self._layer2_key(design))
        if original is None:
            return
        default = next((block for block in original.blocks if block.ident == ident), None)
        if default is None:
            return
        blocks = tuple(default if block.ident == ident else block for block in layout.blocks)
        self._store_current_layer2_layout(replace(layout, blocks=blocks))
        self._status(f"{default.label} auf die Position und Darstellung des Original-Themes zurückgesetzt")

    def reset_layer2_layout(self) -> None:
        design = self.current_hardware_design_path()
        if design is None:
            return
        key = self._layer2_key(design)
        original = self.layer2_originals.get(key)
        if original is None:
            return
        self.layer2_overrides.pop(key, None)
        self._save_layer2_overrides()
        self._sync_layer2_controls()
        self.canvas.set_editable_layout(adjust_layout_intensity(
            original, self._current_layer2_intensity(),
        ))
        self._hide_layer2_inline_editor()
        self._status("Ebene 2 vollständig auf das unveränderte Original-Layout zurückgesetzt")

    def _hardware_design_changed(self, _index: int = -1) -> None:
        design = self.current_hardware_design_path()
        self.hardware_design_active = False
        self.gpu_clock_guard_state = ""
        if hasattr(self, "layer2_inline_editor"):
            self._hide_layer2_inline_editor()
        self.settings.setValue("thermalright/hardware_design", str(design or ""))
        self.custom_overlays_box.setEnabled(design is None)
        self.overlays_toggle.setEnabled(design is None)
        for path, button in self.hardware_card_buttons.items():
            button.setChecked(path == str(design or ""))
        self._sync_autostart_selection_if_enabled()
        self._sync_layer2_controls()
        self._sync_layer2_intensity_control()
        self.reload_selected_preview()
        if design is None:
            self._status("Ebene 2: eigene frei verschiebbare OHC-Hardwarewerte")
        else:
            error = self.layer2_load_errors.get(self._layer2_key(design))
            self._status(
                f"Ebene 2 konnte nicht editierbar geladen werden: {error}"
                if error else
                f"Zwei Ebenen aktiv · alle Datenblöcke aus {design.name} sind einzeln verschiebbar",
                error=bool(error),
            )

    def _entry_for_path(self, media: Path) -> MediaEntry | None:
        resolved = media.resolve()
        return next((entry for entry in self.media_entries if entry.path == resolved), None)

    def _queue_hover_preview(self, index: int) -> None:
        self.pending_hover_index = int(index)
        self.hover_preview_debounce.start()

    def _show_pending_hover_preview(self) -> None:
        self._show_media_preview_tile(self.pending_hover_index)

    def _show_selected_media_preview(self, index: int) -> None:
        if self.media_combo.view().isVisible():
            return
        self._show_media_preview_tile(index)

    def _show_hardware_design_preview(self, index: int) -> None:
        if not 0 <= int(index) < self.hardware_design_combo.count():
            return
        raw = self.hardware_design_combo.itemData(int(index))
        if not raw:
            return
        self._show_path_preview_tile(Path(str(raw)), "theme")

    def _show_media_preview_tile(self, index: int) -> None:
        if not 0 <= int(index) < self.media_combo.count():
            return
        raw = self.media_combo.itemData(int(index))
        if not raw:
            return
        media = Path(str(raw))
        entry = self._entry_for_path(media)
        self._show_path_preview_tile(media, entry.kind if entry else None)

    def _show_path_preview_tile(self, media: Path, known_kind: str | None = None) -> None:
        self.hover_preview_media = media.resolve()
        entry = self._entry_for_path(media)
        kind = known_kind or (entry.kind if entry else "video")
        self.hover_preview_frames = self._hover_preview_sources(media, kind)
        self.hover_preview_frame_index = 0
        self.hover_preview_timer.stop()
        if not self.hover_preview_frames:
            return
        self._render_hover_preview_frame()
        if len(self.hover_preview_frames) > 1:
            self.hover_preview_timer.start()

    def _fit_hover_preview_frames(self, frames: Iterable[QPixmap]) -> list[QPixmap]:
        """Scale selected-video frames once instead of on every 250 ms tick."""

        scale_mode = str(self.media_scale_mode.currentData() or MEDIA_SCALE_CONTAIN)
        fitted_frames: list[QPixmap] = []
        for frame in frames:
            if frame.isNull():
                continue
            fitted = self._fit_qpixmap(frame, scale_mode)
            if not fitted.isNull():
                fitted_frames.append(fitted)
        return fitted_frames

    def _hover_preview_sources(self, media: Path, kind: str) -> list[QPixmap]:
        if kind != "video" or media.suffix.casefold() == ".zt":
            source = self._preview_source(media)
            pixmap = QPixmap(str(source)) if source else QPixmap()
            return self._fit_hover_preview_frames((pixmap,))

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            return []
        fingerprint = hashlib.sha256(
            f"selected-preview-v2:{media}:{media.stat().st_mtime_ns}".encode("utf-8")
        ).hexdigest()[:20]
        targets = [
            self.cache_dir / f"hover-{fingerprint}-{number:02d}.jpg"
            for number in range(1, 17)
        ]
        frames = self._fit_hover_preview_frames(
            QPixmap(str(target)) for target in targets if target.is_file()
        )
        if frames:
            return frames
        pattern = self.cache_dir / f"hover-{fingerprint}-%02d.jpg"
        self._start_hover_preview_extract(media, ffmpeg, pattern, targets)
        return []

    def _start_hover_preview_extract(
        self,
        media: Path,
        ffmpeg: str,
        pattern: Path,
        targets: list[Path],
    ) -> None:
        resolved = media.resolve()
        if (
            self.hover_extract_process.state() != QProcess.ProcessState.NotRunning
            and self.hover_extract_media == resolved
        ):
            return
        if self.hover_extract_process.state() != QProcess.ProcessState.NotRunning:
            self.hover_extract_process.kill()
            self.hover_extract_process.waitForFinished(250)
        self.hover_extract_media = resolved
        self.hover_extract_targets = targets
        self.hover_extract_process.start(ffmpeg, [
            "-v", "error", "-ss", "0.2", "-i", str(resolved),
            "-vf", "fps=4,scale=800:-2", "-frames:v", "16", "-q:v", "4", "-y", str(pattern),
        ])
        self.hover_extract_timeout.start()

    def _cancel_hover_extract(self) -> None:
        if self.hover_extract_process.state() != QProcess.ProcessState.NotRunning:
            self.hover_extract_process.kill()

    def _on_hover_extract_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self.hover_extract_timeout.stop()
        media = self.hover_extract_media
        targets = list(self.hover_extract_targets)
        self.hover_extract_media = None
        self.hover_extract_targets = []
        if exit_code != 0 or media is None or media != self.hover_preview_media:
            return
        self.hover_preview_frames = self._fit_hover_preview_frames(
            QPixmap(str(target)) for target in targets if target.is_file()
        )
        self.hover_preview_frame_index = 0
        if not self.hover_preview_frames:
            return
        self._render_hover_preview_frame()
        if len(self.hover_preview_frames) > 1:
            self.hover_preview_timer.start()

    def _render_hover_preview_frame(self) -> None:
        if not self.hover_preview_frames:
            return
        frame = self.hover_preview_frames[
            self.hover_preview_frame_index % len(self.hover_preview_frames)
        ]
        if self.hover_card_button is not None and self.hover_card_entry is not None:
            card_frame = frame.scaled(
                176, 79, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            ).copy(0, 0, 176, 79)
            self.hover_card_button.setIcon(QIcon(card_frame))
        media = self.current_media_path()
        if media is None or media.resolve() != self.hover_preview_media:
            return
        self.canvas.set_background(frame)

    def _advance_hover_preview(self) -> None:
        if len(self.hover_preview_frames) < 2:
            self.hover_preview_timer.stop()
            return
        self.hover_preview_frame_index = (
            self.hover_preview_frame_index + 1
        ) % len(self.hover_preview_frames)
        self._render_hover_preview_frame()

    def _preview_source(self, media: Path) -> Path | None:
        if media.is_dir():
            for name in ("Theme.png", "00.png"):
                candidate = media / name
                if candidate.is_file():
                    return candidate
            return None
        if media.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES:
            return media
        return self._queue_video_thumbnail(media)

    @staticmethod
    def _fit_pixmap(source: Path, scale_mode: str) -> QPixmap:
        pixmap = QPixmap(str(source))
        return ThermalrightDisplayStudio._fit_qpixmap(pixmap, scale_mode)

    @staticmethod
    def _fit_transparent_layer_pixmap(source: Path) -> QPixmap:
        """Fit layer artwork without flattening its alpha channel onto black."""

        pixmap = QPixmap(str(source))
        if pixmap.isNull():
            return QPixmap()
        scaled = pixmap.scaled(
            LEVITA_WIDTH,
            LEVITA_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        canvas = QPixmap(LEVITA_WIDTH, LEVITA_HEIGHT)
        canvas.fill(QColor(0, 0, 0, 0))
        painter = QPainter(canvas)
        painter.drawPixmap(
            (LEVITA_WIDTH - scaled.width()) // 2,
            (LEVITA_HEIGHT - scaled.height()) // 2,
            scaled,
        )
        painter.end()
        return canvas

    @staticmethod
    def _fit_qpixmap(pixmap: QPixmap, scale_mode: str) -> QPixmap:
        if pixmap.isNull():
            return QPixmap()
        aspect_mode = (
            Qt.AspectRatioMode.KeepAspectRatio
            if scale_mode == MEDIA_SCALE_CONTAIN
            else Qt.AspectRatioMode.KeepAspectRatioByExpanding
        )
        scaled = pixmap.scaled(
            LEVITA_WIDTH, LEVITA_HEIGHT,
            aspect_mode,
            Qt.TransformationMode.SmoothTransformation,
        )
        if scale_mode == MEDIA_SCALE_COVER:
            x = max(0, (scaled.width() - LEVITA_WIDTH) // 2)
            y = max(0, (scaled.height() - LEVITA_HEIGHT) // 2)
            return scaled.copy(x, y, LEVITA_WIDTH, LEVITA_HEIGHT)
        canvas = QPixmap(LEVITA_WIDTH, LEVITA_HEIGHT)
        canvas.fill(QColor("#000000"))
        painter = QPainter(canvas)
        painter.drawPixmap(
            (LEVITA_WIDTH - scaled.width()) // 2,
            (LEVITA_HEIGHT - scaled.height()) // 2,
            scaled,
        )
        painter.end()
        return canvas

    def _immediate_background_pixmap(
        self, media: Path, hardware_design: Path | None,
    ) -> QPixmap:
        """Return a 1600×720 preview immediately, using a cached still if needed."""

        scale_mode = str(self.media_scale_mode.currentData() or MEDIA_SCALE_CONTAIN)
        source = self._preview_source(media)
        if hardware_design is not None and media.resolve() == hardware_design.resolve():
            original_background = hardware_design / "00.png"
            if original_background.is_file():
                source = original_background
        if source:
            pixmap = self._fit_pixmap(source, scale_mode)
            if not pixmap.isNull():
                return pixmap
        thumb = self._video_card_thumbnail(media)
        if thumb:
            pixmap = self._fit_pixmap(thumb, scale_mode)
            if not pixmap.isNull():
                return pixmap
        return QPixmap()

    def update_preview(self) -> None:
        media = self.current_media_path()
        if not media:
            self.canvas.set_background(QPixmap())
            self.canvas.set_hardware_layer(QPixmap())
            return
        hardware_design = self.current_hardware_design_path()
        layer2_intensity = self._current_layer2_intensity()
        self.canvas.set_layer_intensities(self.layer1_intensity_percent, layer2_intensity)
        pixmap = self._immediate_background_pixmap(media, hardware_design)
        editable_layout = self._load_layer2_layout(hardware_design) if hardware_design is not None else None
        if editable_layout is not None:
            editable_layout = adjust_layout_intensity(editable_layout, layer2_intensity)
        hardware_pixmap = QPixmap()
        if hardware_design is not None and editable_layout is not None:
            # The theme's 01.png is artwork only. Live/example values come
            # from draggable model blocks so the preview never double-draws
            # the fixed sample values baked into Theme.png.
            artwork = create_layered_mask(
                self.cache_dir / "intensity-preview",
                hardware_design=hardware_design,
                notch_width=self.notch_width.value(),
                notch_visible=False,
                layer_intensity=layer2_intensity,
            )
            if artwork is not None and artwork.is_file():
                hardware_pixmap = self._fit_transparent_layer_pixmap(artwork)
        elif hardware_design is not None:
            hardware_preview = create_hardware_design_preview(
                hardware_design, self.cache_dir / "hardware-layers",
            )
            hardware_pixmap = QPixmap(str(hardware_preview)) if hardware_preview else QPixmap()
        if hardware_design is not None and editable_layout is None and hardware_pixmap.isNull():
            full_theme_preview = hardware_design / "Theme.png"
            if full_theme_preview.is_file():
                hardware_pixmap = self._fit_pixmap(full_theme_preview, MEDIA_SCALE_CONTAIN)
        entry = self._entry_for_path(media)
        keep_previous_video_frame = bool(
            pixmap.isNull()
            and entry is not None
            and entry.kind == "video"
            and self.canvas.has_background()
        )
        if not keep_previous_video_frame:
            self.canvas.set_background(pixmap)
        self.canvas.set_hardware_layer(hardware_pixmap)
        self.canvas.set_editable_layout(editable_layout)
        self.canvas.set_specs(self.overlay_specs if hardware_design is None else ())
        self.canvas.set_split_mode(int(self.split_mode.currentData() or 0))
        if pixmap.isNull() and entry is not None and entry.kind == "video":
            self._status(
                "Videovorschau wird im Hintergrund vorbereitet · die Oberfläche bleibt bedienbar"
            )
        elif pixmap.isNull():
            self._status("Datei erkannt, aber Vorschau konnte nicht erzeugt werden", error=True)
        elif hardware_design is not None and editable_layout is None and hardware_pixmap.isNull():
            self._status(
                f"Hintergrund sichtbar · {hardware_design.name} wird auf dem Display als zweite Ebene geladen; "
                "für diese Datei ist keine getrennte Ebenenvorschau vorhanden",
                error=True,
            )
        elif hardware_design is not None and editable_layout is not None:
            self._status(
                f"Editierbare Zwei-Ebenen-Vorschau: {len(editable_layout.blocks)} Datenblöcke · "
                "ziehen oder per Rechtsklick anpassen"
            )
        elif hardware_design is not None:
            self._status(f"Zwei-Ebenen-Vorschau: {media.name} + {hardware_design.name}")
        else:
            self._status(f"Vorschau: {media.name}")

    def reload_selected_preview(self) -> None:
        """Reload both selected layers and restart the selected media preview."""

        self.update_preview()
        if self.media_combo.count():
            self._show_selected_media_preview(self.media_combo.currentIndex())

    def _split_mode_changed(self) -> None:
        mode = int(self.split_mode.currentData() or 0)
        self.settings.setValue("thermalright/split_mode", mode)
        self.canvas.set_split_mode(mode)

    def _media_scale_mode_changed(self) -> None:
        mode = str(self.media_scale_mode.currentData() or MEDIA_SCALE_CONTAIN)
        self.settings.setValue("thermalright/media_scale_mode", mode)
        self.update_preview()

    def apply_levita_display_settings(self) -> None:
        brightness = self.levita_brightness.value()
        orientation = int(self.levita_orientation.currentData() or 0)
        self.settings.setValue("thermalright/brightness", brightness)
        self.settings.setValue("thermalright/orientation", orientation)
        if self.test_mode.isChecked():
            self._status(
                f"Testmodus: Levita-Helligkeit {brightness} % und Ausrichtung {orientation}° gespeichert"
            )
            return
        if not self.cli.available:
            self._status("Levita-Displayeinstellungen benötigen das TRCC-Linux-Backend", error=True)
            return
        if self.command_process.state() != QProcess.ProcessState.NotRunning or self.command_step_timer.isActive():
            self._status("Eine Levita-Übertragung läuft bereits · bitte kurz warten", error=True)
            return
        commands = self.cli.reconnect_sequence() + [
            (self.cli.brightness_args(brightness), False),
            (self.cli.orientation_args(orientation), False),
        ]
        QTimer.singleShot(900, lambda: self._start_queue(
            commands, lambda ok, output: self._levita_display_settings_finished(
                ok, output, brightness, orientation,
            ),
        ))
        self._status("Levita-Livestream wird geordnet freigegeben · Einstellungen folgen …")

    def _levita_display_settings_finished(
        self, ok: bool, output: str, brightness: int, orientation: int,
    ) -> None:
        if ok:
            self._apply_finished(True, output)
        self._status(
            f"Levita-Helligkeit {brightness} % und Ausrichtung {orientation}° angewendet"
            if ok else f"Levita-Displayeinstellungen fehlgeschlagen: {output.strip()}",
            error=not ok,
        )

    def _safe_right_x(self) -> int:
        if not hasattr(self, "notch_width") or not hasattr(self, "notch_visible"):
            return notch_safe_right_x(DEFAULT_NOTCH_MASK_WIDTH, visible=True)
        return notch_safe_right_x(
            self.notch_width.value(), visible=self.notch_visible.isChecked(),
        )

    def _display_geometry_changed(self) -> None:
        self.settings.setValue("thermalright/background_x", self.background_x.value())
        self.settings.setValue("thermalright/background_y", self.background_y.value())
        self.settings.setValue("thermalright/notch_visible", self.notch_visible.isChecked())
        self.settings.setValue("thermalright/notch_width", self.notch_width.value())
        self.settings.setValue("thermalright/notch_radius_linked", self.notch_radius_linked.isChecked())
        self.settings.setValue("thermalright/notch_top_radius", self.notch_top_radius.value())
        self.settings.setValue("thermalright/notch_bottom_radius", self.notch_bottom_radius.value())
        self.canvas.set_background_offset(self.background_x.value(), self.background_y.value())
        self.canvas.set_notch_mask(
            self.notch_visible.isChecked(),
            self.notch_width.value(),
            self.notch_top_radius.value(),
            self.notch_bottom_radius.value(),
        )
        right = self._safe_right_x()
        self.overlay_specs = [
            clamp_overlay_outside_cutout(item, safe_right_x=right)
            for item in self.overlay_specs
        ]
        for spec in self.overlay_specs:
            controls = self.overlay_controls.get(spec.ident, {})
            x_spin = controls.get("x")
            if isinstance(x_spin, QSpinBox):
                x_spin.setMaximum(max(0, right - 1))
            self._sync_overlay_controls(spec.ident)
        self._save_overlays()
        self.canvas.set_specs(
            self.overlay_specs if self.current_hardware_design_path() is None else (),
        )

    def _notch_radius_link_changed(self, linked: bool) -> None:
        if linked:
            self.notch_bottom_radius.blockSignals(True)
            self.notch_bottom_radius.setValue(self.notch_top_radius.value())
            self.notch_bottom_radius.blockSignals(False)
        self._display_geometry_changed()

    def _notch_top_radius_changed(self, value: int) -> None:
        if self.notch_radius_linked.isChecked():
            self.notch_bottom_radius.blockSignals(True)
            self.notch_bottom_radius.setValue(bounded_inner_corner_radius(value))
            self.notch_bottom_radius.blockSignals(False)
        self._display_geometry_changed()

    def _notch_bottom_radius_changed(self, value: int) -> None:
        if self.notch_radius_linked.isChecked():
            self.notch_top_radius.blockSignals(True)
            self.notch_top_radius.setValue(bounded_inner_corner_radius(value))
            self.notch_top_radius.blockSignals(False)
        self._display_geometry_changed()

    def _notch_resized_in_preview(self, width: int) -> None:
        self.notch_width.setValue(bounded_notch_width(width))
        self._status(f"Schwarzer Balken in der Vorschau auf {self.notch_width.value()} px gezogen")

    def apply_wide_notch_preset(self) -> None:
        geometry_widgets = (
            self.background_x, self.background_y, self.notch_width, self.notch_visible,
            self.notch_top_radius, self.notch_bottom_radius, self.notch_radius_linked,
        )
        for widget in geometry_widgets:
            widget.blockSignals(True)
        self.background_x.setValue(DEFAULT_BACKGROUND_OFFSET_X)
        self.background_y.setValue(DEFAULT_BACKGROUND_OFFSET_Y)
        self.notch_width.setValue(DEFAULT_NOTCH_MASK_WIDTH)
        self.notch_visible.setChecked(True)
        self.notch_top_radius.setValue(DEFAULT_INNER_CORNER_RADIUS)
        self.notch_bottom_radius.setValue(DEFAULT_INNER_CORNER_RADIUS)
        self.notch_radius_linked.setChecked(True)
        for widget in geometry_widgets:
            widget.blockSignals(False)
        self._display_geometry_changed()
        self._status(
            f"Levita-Standard aktiv · 80 px Balken · rechter Bildradius {DEFAULT_INNER_CORNER_RADIUS} px"
        )

    def apply_overlay_layout(self, layout: str) -> None:
        right = self._safe_right_x()
        if layout == "two_rows":
            columns = (max(150, right // 6), max(430, right // 2), max(760, right * 5 // 6))
            positions = (
                (columns[0], 550), (columns[0], 630),
                (columns[1], 550), (columns[1], 630),
                (columns[2], 550), (columns[2], 630),
            )
            size = 38
            message = "Hardware-Infos in zwei sauberen Reihen angeordnet"
        elif layout == "vertical":
            x = max(180, right - 230)
            positions = tuple((x, 130 + index * 95) for index in range(len(self.overlay_specs)))
            size = 36
            message = "Hardware-Infos mit gleichmäßigem Abstand untereinander angeordnet"
        else:
            return
        self._remember_overlay_state()
        self.overlay_specs = [
            clamp_overlay_outside_cutout(
                replace(spec, x=positions[index][0], y=positions[index][1], size=size),
                safe_right_x=right,
            )
            for index, spec in enumerate(self.overlay_specs)
        ]
        for spec in self.overlay_specs:
            self._sync_overlay_controls(spec.ident)
        self._save_overlays()
        self.canvas.set_specs(
            self.overlay_specs if self.current_hardware_design_path() is None else (),
        )
        self._status(message)

    def _overlay_index(self, ident: str) -> int:
        return next(index for index, item in enumerate(self.overlay_specs) if item.ident == ident)

    def _overlay_control_changed(self, ident: str, **changes: object) -> None:
        index = self._overlay_index(ident)
        candidate = clamp_overlay_outside_cutout(
            replace(self.overlay_specs[index], **changes), safe_right_x=self._safe_right_x(),
        )
        if candidate == self.overlay_specs[index]:
            return
        self._remember_overlay_state()
        self.overlay_specs[index] = candidate
        self._sync_overlay_controls(ident)
        self._save_overlays()
        self.canvas.set_specs(
            self.overlay_specs if self.current_hardware_design_path() is None else (),
        )

    def _overlay_moved(self, ident: str, x: int, y: int) -> None:
        index = self._overlay_index(ident)
        updated = clamp_overlay_outside_cutout(
            replace(self.overlay_specs[index], x=x, y=y), safe_right_x=self._safe_right_x(),
        )
        if updated.x == self.overlay_specs[index].x and updated.y == self.overlay_specs[index].y:
            return
        self.overlay_specs[index] = updated
        self._sync_overlay_controls(ident)
        self._save_overlays()

    def _remember_overlay_state(self) -> None:
        state = tuple(self.overlay_specs)
        if self.overlay_undo_stack and self.overlay_undo_stack[-1] == state:
            return
        self.overlay_undo_stack.append(state)
        del self.overlay_undo_stack[:-20]
        if hasattr(self, "overlay_undo_button"):
            self.overlay_undo_button.setEnabled(True)

    def undo_overlay_change(self) -> None:
        if not self.overlay_undo_stack:
            self._status("Kein früherer Elementzustand vorhanden")
            return
        self.overlay_specs = list(self.overlay_undo_stack.pop())
        for spec in self.overlay_specs:
            self._sync_overlay_controls(spec.ident)
        self._save_overlays()
        self.canvas.set_specs(
            self.overlay_specs if self.current_hardware_design_path() is None else (),
        )
        self.overlay_undo_button.setEnabled(bool(self.overlay_undo_stack))
        self._status("Letzten Zustand der Hardware-Infos wiederhergestellt")

    def _sync_overlay_controls(self, ident: str) -> None:
        spec = self.overlay_specs[self._overlay_index(ident)]
        controls = self.overlay_controls.get(ident, {})
        for name, value in (("visible", spec.visible), ("x", spec.x), ("y", spec.y), ("size", spec.size)):
            widget = controls.get(name)
            if widget is None:
                continue
            widget.blockSignals(True)
            if isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value))
            widget.blockSignals(False)
        color_button = controls.get("color")
        if isinstance(color_button, QPushButton):
            color_button.setText(spec.color)
            color_button.setStyleSheet(f"color: {spec.color};")

    def _choose_overlay_color(self, ident: str) -> None:
        spec = self.overlay_specs[self._overlay_index(ident)]
        color = QColorDialog.getColor(QColor(spec.color), self, f"Farbe für {spec.label}")
        if color.isValid():
            self._overlay_control_changed(ident, color=color.name())

    def reset_overlays(self) -> None:
        self._remember_overlay_state()
        self.overlay_specs = [
            clamp_overlay_outside_cutout(item, safe_right_x=self._safe_right_x())
            for item in DEFAULT_OVERLAYS
        ]
        for spec in self.overlay_specs:
            self._sync_overlay_controls(spec.ident)
        self._save_overlays()
        self.canvas.set_specs(
            self.overlay_specs if self.current_hardware_design_path() is None else (),
        )
        self._status("Hardware-Infos auf sichere Standardpositionen zurückgesetzt")

    def detect_backend_and_device(self) -> None:
        self.refresh_backend_status()
        if not self.cli.available:
            self._status("TRCC Linux ist nicht installiert; die lokale Vorschau bleibt vollständig nutzbar", error=True)
            return
        self._start_queue([(self.cli.version_args(), False), (self.cli.detect_args(), False)], self._detect_finished)
        self._status("Backend und Thermalright-Gerät werden gelesen …")

    def _detect_finished(self, ok: bool, output: str) -> None:
        detected = ok and parse_detect_output(output)
        if detected:
            self.backend_status.setText("TRCC Linux bereit · Thermalright 87ad:70db erkannt")
            self._status("Thermalright-Display erkannt · Hardwaremodus kann verwendet werden")
        else:
            self.backend_status.setText("TRCC Linux gefunden · Thermalright 87ad:70db nicht erkannt")
            self._status("Backend vorhanden, aber das Display wurde nicht erkannt oder ist bereits belegt", error=True)

    def apply_design(self, _checked: bool = False, *, startup: bool = False) -> None:
        cooldown_remaining = self.next_hardware_apply_at - time.monotonic()
        if not startup and cooldown_remaining > 0:
            self.apply_cooldown_timer.start(max(1, round(cooldown_remaining * 1000)))
            self._status(
                "Levita-Designwechsel vorgemerkt · USB-Schutzpause läuft, "
                "danach wird die zuletzt gewählte Kombination übertragen"
            )
            return
        self.apply_cooldown_timer.stop()
        if self.command_process.state() != QProcess.ProcessState.NotRunning or self.command_step_timer.isActive():
            self.next_hardware_apply_at = max(
                self.next_hardware_apply_at,
                time.monotonic() + LEVITA_APPLY_COOLDOWN_SECONDS,
            )
            self.apply_cooldown_timer.start(round(LEVITA_APPLY_COOLDOWN_SECONDS * 1000))
            self._status(
                "Eine Levita-Übertragung läuft bereits · die zuletzt gewählte Kombination "
                "wird nach der USB-Schutzpause übertragen"
            )
            return
        if startup:
            self.startup_apply_active = True
        self.update_preview()
        media = self.current_media_path()
        if not media:
            detail = "kein gespeichertes Design verfügbar"
            if startup:
                self._schedule_startup_retry(detail)
            else:
                self._status("Zuerst einen Designordner importieren und ein Design auswählen", error=True)
            return
        if self.test_mode.isChecked():
            self._status("Testmodus: Design und Hardware-Infos nur in der Vorschau angewendet")
            self.startup_apply_active = False
            return
        self.refresh_backend_status()
        if not self.cli.available:
            detail = "TRCC-Linux-Backend fehlt"
            if startup:
                self._schedule_startup_retry(detail)
            else:
                self._status("Hardwaremodus benötigt das separat installierte TRCC-Linux-Backend", error=True)
            return
        try:
            hardware_design = self.current_hardware_design_path()
            prepared = prepare_shifted_media(
                media,
                self.cache_dir / "prepared-media",
                offset_x=self.background_x.value(),
                offset_y=self.background_y.value(),
                scale_mode=str(self.media_scale_mode.currentData() or MEDIA_SCALE_CONTAIN),
                intensity_percent=self.layer1_intensity_percent,
            )
            mask_path = create_layered_mask(
                self.cache_dir / "masks",
                hardware_design=hardware_design,
                notch_width=self.notch_width.value(),
                notch_visible=self.notch_visible.isChecked(),
                notch_top_radius=self.notch_top_radius.value(),
                notch_bottom_radius=self.notch_bottom_radius.value(),
                layer_intensity=self._current_layer2_intensity(),
            )
            apply_hardware_design = hardware_design
            apply_media = prepared.path
            apply_mask_path = mask_path
            replace_hardware_background: bool | None = None
            if hardware_design is not None:
                layout = self._load_layer2_layout(hardware_design)
                config = self.layer2_configs.get(self._layer2_key(hardware_design))
                if layout is None or config is None:
                    raise ThemeLayoutError(
                        self.layer2_load_errors.get(
                            self._layer2_key(hardware_design),
                            "Datenoberfläche konnte nicht editierbar geladen werden",
                        )
                    )
                layout = adjust_layout_intensity(layout, self._current_layer2_intensity())
                same_theme = media.resolve() == hardware_design.resolve()
                background_image: Path | None = None
                background_video: Path | None = None
                if not same_theme and prepared.path.is_file():
                    if prepared.path.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES:
                        background_image = prepared.path
                    else:
                        background_video = prepared.path
                elif not same_theme and prepared.path.is_dir():
                    candidate = prepared.path / "00.png"
                    if candidate.is_file():
                        background_image = candidate
                    else:
                        background_video = next((
                            prepared.path / name for name in (
                                "Theme.zt", "Theme.mp4", "Theme.mov", "Theme.webm",
                                "Theme.mkv", "Theme.avi",
                            ) if (prepared.path / name).is_file()
                        ), None)
                apply_hardware_design = stage_editable_theme(
                    hardware_design,
                    self.cache_dir / "editable-themes",
                    layout,
                    config,
                    background_image=background_image,
                    background_video=background_video,
                    mask_image=mask_path,
                    include_source_video=same_theme,
                    safe_right_x=self._safe_right_x(),
                )
                # Loading adopts the edited live blocks; explicit daemon-side
                # ApplyMask then makes the combined artwork/notch visible even
                # if an earlier design persisted mask_visible=False.
                apply_media = apply_hardware_design
                apply_mask_path = mask_path
                replace_hardware_background = False
            sequence = build_apply_sequence(
                self.cli, apply_media, self.overlay_specs,
                split_mode=int(self.split_mode.currentData() or 0),
                mask_path=apply_mask_path,
                safe_right_x=self._safe_right_x(),
                hardware_design=apply_hardware_design,
                replace_hardware_background=replace_hardware_background,
                brightness=self.levita_brightness.value(),
                orientation=int(self.levita_orientation.currentData() or 0),
            )
        except (OSError, RuntimeError, ValueError) as exc:
            if startup:
                self._schedule_startup_retry(str(exc))
            else:
                self._status(str(exc), error=True)
            return
        self.pending_apply_warning = prepared.warning
        self.pending_apply_sequence = list(sequence)
        self.pending_apply_animated = self._media_is_animated(prepared.path)
        self.hardware_design_active = False
        self._stop_stream_client()
        self.apply_retry_remaining = 1
        self.apply_start_timer.start()
        if hardware_design is not None and media.resolve() == hardware_design.resolve():
            self._status(
                "Editierbares TRCC-Standarddesign wird aus dem OHC-Cache geladen · Originaldateien bleiben unverändert …"
            )
        elif hardware_design is not None:
            self._status(
                "Zwei Ebenen werden als ein Cache-Theme übertragen · Video unten, "
                "komplettes Hardware-Design mit Live-Werten darüber …"
            )
        elif int(self.split_mode.currentData() or 0):
            self._status("Design und Hardware-Infos werden übertragen · Notch-Stil bleibt aus Kompatibilitätsgründen nur in der Vorschau …")
        else:
            self._status("Design und Hardware-Infos werden übertragen …")

    def _apply_finished(self, ok: bool, output: str) -> None:
        if not ok:
            detail = output.strip().splitlines()[-1] if output.strip() else "unbekannter Backendfehler"
            timeout = "timed out" in output.casefold() or "errno 110" in output.casefold()
            backend_crash = "trcc-prozess ist abgestürzt" in output.casefold()
            if timeout and self.apply_retry_remaining > 0 and self.pending_apply_sequence:
                self.apply_retry_remaining -= 1
                self._status(
                    "USB-Timeout beim Levita-Handshake · USB-Zugriff wird freigegeben und einmal kontrolliert wiederholt …",
                    error=True,
                )
                self.apply_start_timer.setInterval(5000)
                self.apply_start_timer.start()
                return
            self.pending_apply_sequence = []
            self.apply_retry_remaining = 0
            if backend_crash:
                self.next_hardware_apply_at = time.monotonic() + LEVITA_APPLY_COOLDOWN_SECONDS
                self.startup_apply_active = False
                self._status(
                    "TRCC ist beim Öffnen des Levita-USB-Geräts abgestürzt · automatische "
                    "Versuche wurden gestoppt; Display bitte vollständig stromlos machen",
                    error=True,
                )
            elif timeout:
                self.next_hardware_apply_at = time.monotonic() + LEVITA_APPLY_COOLDOWN_SECONDS
                self.startup_apply_active = False
                self._status(
                    "Levita antwortet nicht auf den USB-Handshake · weitere automatische Versuche "
                    "wurden gestoppt; Display bitte einmal vollständig stromlos machen",
                    error=True,
                )
            elif self.startup_apply_active:
                self._schedule_startup_retry(detail)
            else:
                self._status(f"Übertragung fehlgeschlagen: {detail}", error=True)
            return
        self._daemon_stream_started()

    def _daemon_stream_started(self) -> None:
        """Confirm the theme and start a daemon-safe video ticker if needed."""

        animated = self.pending_apply_animated
        self.hardware_design_active = self.current_hardware_design_path() is not None
        if animated:
            self._start_stream_client()

        if animated:
            self._status(
                "Levita-Design geladen · daemon-sicherer Video-Taktgeber startet …"
            )
        elif self.pending_apply_warning:
            self._status(
                "Levita-Design aktiv · schwarzer Balken angewendet · " + self.pending_apply_warning,
                error=True,
            )
        elif (
            self.current_hardware_design_path() is not None
            and self.current_media_path() == self.current_hardware_design_path()
        ):
            self._status(
                "TRCC-Standarddesign aktiv · bearbeitete Live-Blöcke laufen aus dem OHC-Cache"
            )
        elif self.current_hardware_design_path() is not None:
            self._status(
                "Levita-Zwei-Ebenen-Design aktiv · Hintergrundvideo läuft hinter dem Live-Hardware-Design"
            )
        else:
            self._status("Levita-Design aktiv · verschobener Hintergrund, schwarzer Balken und Hardwarewerte laufen")
        if self.startup_apply_active:
            self._log("LCD-START: gespeichertes Levita-Design ist aktiv")
        self.startup_apply_active = False
        self.startup_retry_count = 0
        self.pending_apply_warning = ""
        self.pending_apply_sequence = []
        self.pending_apply_animated = False
        self.apply_retry_remaining = 0
        self.next_hardware_apply_at = time.monotonic() + LEVITA_APPLY_COOLDOWN_SECONDS

    def _active_gpu_clock_block(self) -> LayoutBlock | None:
        layout = self._current_layer2_layout()
        if layout is None:
            return None
        return next(
            (block for block in layout.blocks if block.metric == "gpu:primary:clock"),
            None,
        )

    def _guard_gpu_clock(self) -> None:
        """Correct TRCC's low-Hz idle boundary through daemon IPC."""
        if (
            not self.hardware_design_active
            or self.test_mode.isChecked()
            or not self.cli.available
            or self.command_process.state() != QProcess.ProcessState.NotRunning
            or self.command_step_timer.isActive()
        ):
            return
        block = self._active_gpu_clock_block()
        if block is None:
            self.gpu_clock_guard_state = ""
            return
        reading = read_primary_amd_gpu_clock()
        boundary_issue = "TRCC-9.9.11-Grenzfall" in reading.issue
        if boundary_issue and reading.mhz is not None:
            if self.gpu_clock_guard_state == "boundary":
                return
            try:
                literal = block.format.format(value=reading.mhz)
                command = self.cli.overlay_update_format_args(
                    block.ident, literal, show_unit=True,
                )
            except (KeyError, ValueError, IndexError):
                return

            def corrected(ok: bool, _output: str) -> None:
                if not ok:
                    return
                self.gpu_clock_guard_state = "boundary"
                message = (
                    "GPU-Takt korrigiert · Quelle=freq1_input · "
                    f"Rohwert={reading.raw} Hz · normalisiert={reading.mhz:g} MHz · "
                    "Ursache=TRCC-9.9.11-Grenzwertfehler bei niedrigen Hz-Rohwerten bis 1000000"
                )
                self._status(message)
                if self.log_ready and self.log_callback:
                    self.log_callback("HARDWARE: " + message)

            self._start_queue([(command, False)], corrected)
            return
        if self.gpu_clock_guard_state != "boundary":
            return
        command = self.cli.overlay_update_format_args(
            block.ident, block.format, show_unit=True,
        )

        def restored(ok: bool, _output: str) -> None:
            if not ok:
                return
            self.gpu_clock_guard_state = ""
            message = "GPU-Taktquelle wieder plausibel · dynamische Live-Anzeige wiederhergestellt"
            self._status(message)
            if self.log_ready and self.log_callback:
                self.log_callback("HARDWARE: " + message)

        self._start_queue([(command, False)], restored)

    def _begin_pending_apply(self) -> None:
        self.apply_start_timer.setInterval(900)
        if not self.pending_apply_sequence:
            return
        if self.command_process.state() != QProcess.ProcessState.NotRunning or self.command_step_timer.isActive():
            self.apply_start_timer.start(500)
            return
        self._start_queue(self.pending_apply_sequence, self._apply_finished)

    def run_display_test(self) -> None:
        if self.test_mode.isChecked():
            self.test_color_index = 0
            self.test_timer.start()
            self._next_test_color()
            self._status("Testmodus: lokaler Farbtest läuft · keine USB-Daten gesendet")
            return
        self.refresh_backend_status()
        if not self.cli.available:
            self._status("Display-Test benötigt das TRCC-Linux-Backend", error=True)
            return
        commands = self.cli.reconnect_sequence()
        commands.append((self.cli.test_args(0.5), False))
        self._start_queue(commands, self._test_finished)
        self._status("Display wird sauber neu verbunden · danach läuft der Farbtest …")

    def _next_test_color(self) -> None:
        if self.test_color_index >= len(self.test_colors):
            self.test_timer.stop()
            self.update_preview()
            return
        pixmap = QPixmap(LEVITA_WIDTH, LEVITA_HEIGHT)
        pixmap.fill(self.test_colors[self.test_color_index])
        self.canvas.set_background(pixmap)
        self.test_color_index += 1

    def _test_finished(self, ok: bool, output: str) -> None:
        self._status("Display-Farbtest abgeschlossen" if ok else f"Display-Farbtest fehlgeschlagen: {output.strip()}", error=not ok)

    def stop_display(self) -> None:
        self.test_timer.stop()
        self.pending_apply_animated = False
        self.hardware_design_active = False
        self.gpu_clock_guard_state = ""
        self._stop_stream_client()
        if self.test_mode.isChecked() or not self.cli.available:
            self.update_preview()
            self._status("Test-/Vorschaumodus angehalten")
            return
        self._start_queue([(self.cli.stop_video_args(), True)], lambda _ok, _out: self._status("Thermalright-Übertragung angehalten"))

    @staticmethod
    def _media_is_animated(media: Path) -> bool:
        source = media.expanduser().resolve()
        if source.is_file():
            return source.suffix.casefold() in SUPPORTED_VIDEO_SUFFIXES
        return source.is_dir() and any(
            (source / name).is_file() for name in (
                "Theme.zt", "Theme.mp4", "Theme.mov", "Theme.webm",
                "Theme.mkv", "Theme.avi",
            )
        )

    def _start_stream_client(self) -> None:
        if self.stream_process.state() != QProcess.ProcessState.NotRunning:
            return
        self.stream_should_run = True
        self.stream_stop_requested = False
        args = self.cli.play_args(0.15)
        self.stream_process.start(args[0], list(args[1:]))

    def _stop_stream_client(self) -> None:
        self.stream_should_run = False
        if self.stream_process.state() == QProcess.ProcessState.NotRunning:
            return
        self.stream_stop_requested = True
        self.stream_process.terminate()
        if not self.stream_process.waitForFinished(750):
            self.stream_process.kill()
            self.stream_process.waitForFinished(500)

    def _on_stream_finished(self, exit_code: int, status: QProcess.ExitStatus) -> None:
        requested = self.stream_stop_requested
        self.stream_stop_requested = False
        if requested or not self.stream_should_run:
            return
        if status == QProcess.ExitStatus.CrashExit or exit_code != 0:
            self._status(
                "Levita-Video-Taktgeber wurde beendet · Design bleibt sichtbar, Video steht",
                error=True,
            )

    def _on_stream_started(self) -> None:
        if not self.stream_should_run:
            return
        if self.current_hardware_design_path() is not None:
            self._status(
                "Levita-Video läuft · Hintergrund, Ebene-2-Grafik und Notch-Maske sind aktiv"
            )
        else:
            self._status("Levita-Hintergrundvideo läuft über den TRCC-Daemon")

    def _on_stream_error(self, error: QProcess.ProcessError) -> None:
        if self.stream_should_run and error == QProcess.ProcessError.FailedToStart:
            self.stream_should_run = False
            self._status(
                "Levita-Video-Taktgeber konnte nicht gestartet werden · Design bleibt als Standbild sichtbar",
                error=True,
            )

    def _start_queue(
        self,
        commands: Iterable[tuple[tuple[str, ...], bool]],
        done: Callable[[bool, str], None],
    ) -> None:
        if self.command_process.state() != QProcess.ProcessState.NotRunning or self.command_step_timer.isActive():
            self._status("Levita-Befehl nicht gestartet · eine andere USB-Übertragung läuft noch", error=True)
            return
        self.command_queue = list(commands)
        self.command_outputs = []
        self.queue_done = done
        self._start_next_command()

    def _start_next_command(self) -> None:
        if not self.command_queue:
            done, self.queue_done = self.queue_done, None
            if done:
                done(True, "\n".join(self.command_outputs))
            return
        args, self.current_tolerates_failure = self.command_queue.pop(0)
        self.command_process.start(args[0], list(args[1:]))

    def _on_command_finished(self, exit_code: int, status: QProcess.ExitStatus) -> None:
        stdout = bytes(self.command_process.readAllStandardOutput()).decode("utf-8", errors="replace")
        stderr = bytes(self.command_process.readAllStandardError()).decode("utf-8", errors="replace")
        output = (stdout + "\n" + stderr).strip()
        if output:
            self.command_outputs.append(output)
        if status == QProcess.ExitStatus.CrashExit:
            self.command_outputs.append(
                "TRCC-Prozess ist abgestürzt (externer Backend-/libusb-Fehler)"
            )
        if exit_code != 0 and not self.current_tolerates_failure:
            self.command_queue.clear()
            done, self.queue_done = self.queue_done, None
            if done:
                done(False, "\n".join(self.command_outputs))
            return
        self.command_step_timer.start()

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.shutdown()
        super().closeEvent(event)

    def shutdown(self) -> None:
        """Stop workers and quickly return Levita to its active TRCC theme."""
        if self.shutdown_started:
            return
        self.shutdown_started = True
        self.test_timer.stop()
        self.gpu_clock_guard_timer.stop()
        self.apply_start_timer.stop()
        self.apply_cooldown_timer.stop()
        self.command_step_timer.stop()
        self.hover_preview_timer.stop()
        self.hover_preview_debounce.stop()
        self.hover_extract_timeout.stop()
        self.pending_apply_animated = False
        self._stop_stream_client()
        if self.hover_extract_process.state() != QProcess.ProcessState.NotRunning:
            self.hover_extract_process.terminate()
            if not self.hover_extract_process.waitForFinished(500):
                self.hover_extract_process.kill()
                self.hover_extract_process.waitForFinished(500)
        self.thumbnail_shutting_down = True
        self.thumbnail_queue.clear()
        self.thumbnail_queued.clear()
        for worker in self.thumbnail_workers:
            self.thumbnail_worker_timeouts[worker].stop()
            if worker.state() != QProcess.ProcessState.NotRunning:
                worker.kill()
                worker.waitForFinished(500)
        self.thumbnail_active.clear()
        self.command_queue.clear()
        self.queue_done = None
        if self.command_process.state() != QProcess.ProcessState.NotRunning:
            self.command_process.kill()
            self.command_process.waitForFinished(500)
        self.command_step_timer.stop()
        if not self.test_mode.isChecked() and self.cli.available:
            try:
                result = self.cli.stop_video_now(timeout=1.5)
            except (OSError, subprocess.SubprocessError) as exc:
                self._log(f"Programmende: Originaldesign konnte nicht bestätigt werden: {exc}")
            else:
                if result.ok:
                    self._log("Programmende: Übertragung angehalten · aktives TRCC-Originaldesign wiederhergestellt")
                else:
                    detail = result.message or f"Rückgabecode {result.returncode}"
                    self._log(f"Programmende: Übertragung anhalten fehlgeschlagen: {detail}")
