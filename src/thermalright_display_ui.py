#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""PySide6 editor for Thermalright Levita media and metric overlays."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from typing import Callable, Iterable
import weakref

from PySide6.QtCore import QPoint, QProcess, QProcessEnvironment, QRect, QSize, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFontDatabase, QIcon, QPainter, QPen, QPixmap, QResizeEvent
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
from shiboken6 import isValid

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
    THERMALRIGHT_DEVICE_KEY,
    ThermalrightCli,
    bounded_layer_intensity,
    bounded_notch_width,
    build_apply_sequence,
    clamp_overlay_outside_cutout,
    collapse_catalog_previews,
    create_hardware_design_preview,
    deduplicate_media_entries,
    default_trcc_design_directory,
    default_trcc_media_directories,
    create_layered_mask,
    media_category_key,
    media_catalog_sort_key,
    notch_safe_right_x,
    parse_detect_output,
    prepare_shifted_media,
    scan_media_directory,
    stage_custom_overlay_theme,
    trcc_theme_is_supported,
)
from window_diagnostics import track_qprocess
from privacy_logging import redact_private_text
from modules.ui_performance.v1_1 import (
    cache_budget_mb, cached_catalog_records, preview_cache_path, save_catalog_records,
)
from modules.lcd_levita_shutdown.v1_0 import (
    LevitaFirmwareGuard,
    restore_firmware_logo,
    stop_owned_daemon,
)
from modules.lcd_levita.v1_7.layout_canvas import ThermalrightCanvas
from modules.lcd_levita.v1_7.panel_geometry import (
    DEFAULT_INNER_CORNER_RADIUS,
    MAX_INNER_CORNER_RADIUS,
    bounded_inner_corner_radius,
)
from modules.lcd_levita.v1_7.layout_model import (
    EditableLayout,
    LayoutBlock,
    MAX_FONT_SIZE,
    MIN_FONT_SIZE,
    adjust_layout_intensity,
    deserialize_layout_overrides,
    serialize_layout_overrides,
    restore_explicit_format_units,
)
from hardware_diagnostics import advance_gpu_clock_recovery_streak, read_primary_amd_gpu_clock
from modules.lcd_levita.v1_7.runtime_policy import safe_split_mode
from modules.lcd_levita.v1_7.stream_recovery import StreamRestartPolicy
from modules.lcd_runtime.v1_1.progress import daemon_owns_playback
from modules.backend_updates.v1_0.executables import is_ubuntu_runtime
from modules.levita_daemon_health.v1_1.model import backend_failure_detail, is_usb_owner_conflict
from modules.levita_daemon_health.v1_1 import (
    DAEMON_RECOVERY_COOLDOWN_SECONDS,
    PLAYBACK_HEALTH_INTERVAL_MS,
    PLAYBACK_RECOVERY_COOLDOWN_SECONDS,
    PlaybackHealth,
    PlaybackRecoveryPolicy,
    find_trcc_daemon_memory,
    is_probable_daemon_failure,
    is_owned_trcc_daemon_pid,
    parse_playback_status,
    parse_video_playback_status,
    recent_trcc_cause,
    replacement_owned_trcc_pid,
    signal_trcc_daemon,
)
from modules.lcd_levita.v1_7.motion_renderer import render_layer2_motion_frame
from modules.lcd_levita.v1_7.motion_compositor import compose_motion_video
from modules.lcd_levita.v1_7.theme_adapter import (
    ThemeLayoutError,
    load_editable_layout,
    stage_editable_theme,
)
from modules.display_effects.v1_11.handoff import validate_effect_handoff
from modules.lcd_media_manager.v1_0 import (
    DesignLibraryDialog,
    friendly_media_name,
    load_library_state,
    save_library_state,
)
from modules.responsive_gallery.v1_0 import ViewportResizeRelay, responsive_column_count
from modules.snapshot_manager.v1_0.program_manager import ProgramManagerPanel
from modules.levita_performance.v1_1 import (
    GAME_ACTIVITY_POLL_MS,
    SAFE_LCD_FPS,
    GameSignals,
    fallback_lcd_fps,
    normalize_lcd_fps,
    normalize_process_names,
    parse_gamemode_status,
    process_game_signal,
    resolve_game_activity,
)


LEVITA_APPLY_COOLDOWN_SECONDS = 10.0
READABLE_CONTROL_HEIGHT = 36
READABLE_SPIN_WIDTH = 148
READABLE_COMBO_WIDTH = 320
DESIGN_CARD_WIDTH = 180
DESIGN_CARD_GAP = 8
MEDIA_GALLERY_COLUMNS = (1, 12)
HARDWARE_GALLERY_COLUMNS = (1, 12)
MAX_CUSTOM_TEXT_OVERLAYS = 12
BUILTIN_LEVITA_THEMES = (
    ("ohc-nebula-drift", "Nebelberg · System"),
    ("ohc-nebula-drift-minimal", "Nebelberg · Minimal"),
    ("ohc-nebula-drift-performance", "Nebelberg · Leistung"),
    ("ohc-orbital-command", "Orbitalzentrale"),
    ("kenney-space-console", "Weltraumkonsole"),
    ("kenney-orbital-reticle", "Orbital-Fadenkreuz"),
    ("kenney-navigator-grid", "Navigationsraster"),
    ("kenney-ambient-glow", "Atmosphärenleuchten"),
    ("kenney-clean-telemetry", "Klare Telemetrie"),
    ("ohc-orbit", "OHC Umlaufbahn"),
    ("ohc-aqua-pulse", "OHC Wasserpuls"),
    ("ohc-horizon-glass", "OHC Horizontglas"),
    ("ohc-split-core", "OHC Geteilter Kern"),
    ("ohc-spectrum-ring", "OHC Spektrumring"),
    ("ohc-neon-double-arc", "OHC Neon-Doppelbogen"),
    ("ohc-prism-segments", "OHC Prismensegmente"),
    ("ohc-aurora-radar", "OHC Polarlicht-Radar"),
)
BUILTIN_LEVITA_THEME_NAMES = frozenset(directory for directory, _title in BUILTIN_LEVITA_THEMES)
ANIMATED_LAYER2_THEMES = frozenset({
    "ohc-spectrum-ring", "ohc-neon-double-arc", "ohc-prism-segments", "ohc-aurora-radar",
})


def gallery_column_count(
    width: int,
    *,
    minimum: int,
    maximum: int,
    card_width: int = DESIGN_CARD_WIDTH,
    gap: int = DESIGN_CARD_GAP,
) -> int:
    """Fit as many Levita cards as the gallery width allows, within bounds."""

    return responsive_column_count(
        width, card_width=card_width, gap=gap, minimum=minimum, maximum=maximum,
    )


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

    library_ready = Signal()

    def __init__(
        self,
        settings,
        cache_dir: Path,
        *,
        log_callback: Callable[[str], None] | None = None,
        device_present: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Thermalright Levita Vision · Display-Studio", parent)
        self.settings = settings
        self.cache_dir = cache_dir / "thermalright-preview"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_callback = log_callback
        self.device_present = bool(device_present)
        # The LCD page is built before the main Log page. Restoring a saved
        # media directory renders its first preview synchronously, so logging
        # must stay muted until this widget has finished constructing.
        self.log_ready = False
        self.hardware_io_disabled = os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1"
        self.ubuntu_runtime = is_ubuntu_runtime()
        self.cli = ThermalrightCli()
        self.firmware_guard = LevitaFirmwareGuard(self.cli.executable)
        existing_daemon = find_trcc_daemon_memory()
        self.preexisting_trcc_daemon_pid = existing_daemon.pid if existing_daemon else None
        self.owned_trcc_daemon_pid: int | None = None
        self.awaiting_owned_trcc_replacement = False
        self.media_entries: list[MediaEntry] = []
        self.library_loaded = False
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
        try:
            saved_motion = json.loads(str(
                self.settings.value("thermalright/layer2_motion_overrides", "{}") or "{}"
            ))
        except (json.JSONDecodeError, TypeError):
            saved_motion = {}
        self.layer2_motion_overrides = {
            str(key): bool(value) for key, value in saved_motion.items() if isinstance(key, str)
        } if isinstance(saved_motion, dict) else {}
        self.experimental_60_fps = self.settings.value(
            "thermalright/experimental_60_fps", False, type=bool,
        )
        self.desktop_lcd_fps = normalize_lcd_fps(
            self.settings.value("thermalright/desktop_fps", 15),
            experimental_60=self.experimental_60_fps,
        )
        self.game_lcd_fps = normalize_lcd_fps(
            self.settings.value("thermalright/game_fps", 15),
            experimental_60=self.experimental_60_fps,
        )
        self.preview_fps = 60 if int(self.settings.value("thermalright/preview_fps", 60)) >= 60 else 30
        self.game_auto_detection = self.settings.value(
            "thermalright/game_auto_detection", True, type=bool,
        )
        self.game_manual = False
        self.game_active = False
        self.game_reason = "Desktop"
        self.game_process_names = normalize_process_names(
            self.settings.value("thermalright/game_process_names", "")
        )
        self.game_fullscreen_detection = self.settings.value(
            "thermalright/game_fullscreen_detection", True, type=bool,
        )
        self.game_borderless_detection = self.settings.value(
            "thermalright/game_borderless_detection", True, type=bool,
        )
        self.gamemode_active = False
        self.active_lcd_fps = self.desktop_lcd_fps
        self.session_fps_limit: int | None = None
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
        from modules.lcd_runtime.v1_1.design_state import DesignState
        from modules.lcd_runtime.v1_1.memory_guard import MemoryGuard
        self.design_state = DesignState(self.settings)
        self.daemon_memory_guard = MemoryGuard()
        self.playback_recovery_policy = PlaybackRecoveryPolicy()
        self.playback_health_probe_active = False
        self.playback_last_confirmed_at = 0.0
        self.last_playback_reapply_at = float("-inf")
        self.startup_apply_active = False
        self.startup_retry_count = 0
        self.startup_apply_requested = False
        self.restoring_startup_selection = False
        self.remember_design_after_apply = False
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
        self.design_library_state = load_library_state(
            self.settings.value("thermalright/design_library_v1", ""),
            self.custom_media_directory,
        )
        self.custom_media_directory = (
            self.design_library_state.folders[0]
            if self.design_library_state.folders else None
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
        self.command_process.setObjectName('ohcLCDCommand')
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
        self.stream_process.setObjectName('ohcLCDTicker')
        self.stream_process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.stream_process.setProcessEnvironment(command_environment)
        self.stream_process.readyReadStandardOutput.connect(self._capture_stream_output)
        self.stream_process.readyReadStandardError.connect(self._capture_stream_output)
        self.stream_process.started.connect(self._on_stream_started)
        self.stream_process.errorOccurred.connect(self._on_stream_error)
        self.stream_process.finished.connect(self._on_stream_finished)
        self.gamemode_process = track_qprocess(QProcess(self))
        self.gamemode_process.setObjectName('ohcGameProbe')
        self.gamemode_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.gamemode_process.finished.connect(self._gamemode_status_finished)
        from modules.lcd_runtime.v1_1.controller import LCDRuntime
        self.lcd_runtime = LCDRuntime(self)
        from modules.lcd_runtime.v1_1.game_activity import GameActivity
        self.game_activity = GameActivity(self)
        self.stream_stop_requested = False
        self.stream_should_run = False
        self.stream_delegated = False
        self._fps_restart_pending = False
        self.stream_started_at = 0.0
        self.stream_output_tail = ""
        self.stream_restart_policy = StreamRestartPolicy()
        self.stream_restart_timer = QTimer(self)
        self.stream_restart_timer.setSingleShot(True)
        self.stream_restart_timer.timeout.connect(self._restart_stream_client)
        self.daemon_restart_in_progress = False
        self.last_daemon_recovery_at = float("-inf")
        self.daemon_restart_timer = QTimer(self)
        self.daemon_restart_timer.setSingleShot(True)
        self.daemon_restart_timer.timeout.connect(self._perform_daemon_restart)
        self.daemon_health_timer = QTimer(self)
        self.daemon_health_timer.setInterval(PLAYBACK_HEALTH_INTERVAL_MS)
        self.daemon_health_timer.timeout.connect(self._poll_trcc_daemon_health)
        self.firmware_guard_timer = QTimer(self)
        self.firmware_guard_timer.setInterval(5_000)
        self.firmware_guard_timer.timeout.connect(self._poll_firmware_guard_health)
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
        self.thumbnail_paused_workers: set[QProcess] = set()
        self.thumbnail_workers: list[QProcess] = []
        self.thumbnail_worker_timeouts: dict[QProcess, QTimer] = {}
        self.thumbnail_total = 0
        self.thumbnail_finished = 0
        self.thumbnail_generated = 0
        self.thumbnail_failed = 0
        self.thumbnail_shutting_down = False
        self._media_cards_materialized = False
        self._hardware_cards_materialized = False
        self._gallery_materialize_pending = False
        self.shutdown_started = False
        from modules.ui_performance.v1_1.gallery_preparation import GalleryPreparation
        self.gallery_preparation = GalleryPreparation(self)
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
        self.gpu_clock_plausible_streak = 0
        self.gpu_clock_guard_timer = QTimer(self)
        self.gpu_clock_guard_timer.setInterval(5000)
        self.gpu_clock_guard_timer.timeout.connect(self._guard_gpu_clock)
        self.game_detection_timer = QTimer(self)
        self.game_detection_timer.setInterval(GAME_ACTIVITY_POLL_MS)
        self.game_detection_timer.timeout.connect(self._poll_game_activity)
        self.layer2_motion_started = time.monotonic()
        self.layer2_motion_timer = QTimer(self)
        self.layer2_motion_timer.timeout.connect(self._advance_layer2_motion_preview)

        self._build_ui()
        for area in (self.media_cards_scroll, self.hardware_cards_scroll):
            area.verticalScrollBar().valueChanged.connect(lambda _value: self._start_thumbnail_workers())
            area.horizontalScrollBar().valueChanged.connect(lambda _value: self._start_thumbnail_workers())
        self.refresh_backend_status()
        self.log_ready = True
        self.gpu_clock_guard_timer.start()
        self.game_detection_timer.start()
        self.daemon_health_timer.start()
        self.firmware_guard_timer.start()
        self._preview_fps_changed()
        QTimer.singleShot(0, self, self._poll_game_activity)
        if os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1":
            self.load_initial_library()
        else:
            # Let the main window paint and accept input before scanning local
            # TRCC/custom media and constructing all preview cards.
            QTimer.singleShot(80, self, self.load_initial_library)

    def load_initial_library(self) -> None:
        if self.library_loaded:
            return
        if self.design_library_state.has_sources and self.custom_media_enabled.isChecked():
            self._reload_managed_library()
        else:
            self.load_default_trcc_designs(quiet=True)

    def install_backend(self) -> None:
        host = self.window()
        installer = getattr(host, "install_optional_backend", None)
        if callable(installer):
            installer("trcc")
            return
        self._status(
            "TRCC Linux für diese Distribution anhand der offiziellen Anleitung installieren.",
            error=True,
        )

    def reload_backend_availability(self) -> None:
        """Refresh CLI availability and local catalogs after installation."""

        self.refresh_backend_status()
        self.firmware_guard = LevitaFirmwareGuard(self.cli.executable)
        self.library_loaded = False
        self.load_initial_library()

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

        display_recovery_row = QHBoxLayout()
        self.restore_firmware_button = QPushButton("Thermalright-Originalanzeige wiederherstellen")
        self.restore_firmware_button.setObjectName("primaryAction")
        self.restore_firmware_button.setMinimumHeight(44)
        self.restore_firmware_button.setToolTip(
            "Beendet die OHC-Übertragung und gibt das Display an die eingebaute Thermalright-Firmware zurück"
        )
        self.restore_firmware_button.clicked.connect(self.restore_firmware_display)
        display_recovery_row.addWidget(self.restore_firmware_button, 1)
        self.force_recovery_button = QPushButton("Display freigeben")
        self.force_recovery_button.setMinimumHeight(44)
        self.force_recovery_button.clicked.connect(self.force_recover_display)
        display_recovery_row.addWidget(self.force_recovery_button, 1)
        outer.addLayout(display_recovery_row)

        status_row = QHBoxLayout()
        self.test_mode = QCheckBox("Testmodus · nur Vorschau, keine USB-Schreibzugriffe")
        # A present Levita with an installed backend should work immediately.
        # Missing device/backend remains fail-closed in preview-only mode.
        default_test_mode = not (self.device_present and self.cli.available)
        self.test_mode.setChecked(
            self.settings.value("thermalright/test_mode", default_test_mode, type=bool)
        )
        self.test_mode.toggled.connect(self._on_test_mode_changed)
        self.backend_status = QLabel()
        self.backend_status.setWordWrap(True)
        self.backend_status.setObjectName("muted")
        detect_button = QPushButton("Backend & Gerät prüfen")
        detect_button.clicked.connect(self.detect_backend_and_device)
        status_row.addWidget(self.test_mode)
        status_row.addWidget(self.backend_status, 1)
        self.install_backend_button = QPushButton("TRCC Linux für Thermalright-LCD installieren")
        self.install_backend_button.clicked.connect(self.install_backend)
        status_row.addWidget(self.install_backend_button)
        status_row.addWidget(detect_button)
        outer.addLayout(status_row)

        self.playback_health_status = QLabel("Wiedergabe noch nicht geprüft")
        self.playback_health_status.setWordWrap(True)
        self.playback_health_status.setObjectName("muted")
        self.playback_health_status.setToolTip(
            "Open Hardware Control prüft regelmäßig, ob TRCC das ausgewählte Design noch wirklich wiedergibt."
        )
        outer.addWidget(self.playback_health_status)


        library_toolbar = QHBoxLayout()
        standard_button = QPushButton("TRCC-Standarddesigns")
        standard_button.setToolTip(
            "Lädt automatisch die für Levita 1600×720 installierten TRCC-Layouts. "
            "config1.dc übernimmt Positionen, Farben und Live-Sensorwerte direkt."
        )
        standard_button.clicked.connect(self.load_default_trcc_designs)
        import_button = QPushButton("LCD-Manager")
        import_button.setToolTip(
            "Liest Bilder, Videos und vollständige Layoutordner ein. Über das Kartenmenü legst du Ebene 1 oder 2 fest."
        )
        import_button.clicked.connect(self.choose_media_directory)
        self.remembered_media_button = QPushButton("Gemerkten Ordner anzeigen")
        self.remembered_media_button.clicked.connect(self.show_remembered_media_directory)
        self.remembered_media_button.setEnabled(self.design_library_state.has_sources)
        self.custom_media_enabled = QCheckBox("Eigenen Designordner einbeziehen")
        self.custom_media_enabled.setChecked(
            self.design_library_state.has_sources
            and self.settings.value("thermalright/custom_media_enabled", True, type=bool)
        )
        self.custom_media_enabled.setEnabled(self.design_library_state.has_sources)
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
        self.media_category.setProperty("i18nTranslateItems", False)
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
        self._media_resize_relay = ViewportResizeRelay(self._relayout_design_galleries, self)
        self.media_cards_scroll.viewport().installEventFilter(self._media_resize_relay)
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
        self.layer2_motion_checkbox = QCheckBox("Dekor-Animation")
        self.layer2_motion_checkbox.setChecked(True)
        self.layer2_motion_checkbox.setToolTip(
            "Animiert Ring, Bögen, Segmente oder Aurora lokal unter den weiterhin editierbaren Live-Daten"
        )
        self.layer2_motion_checkbox.toggled.connect(self._layer2_motion_changed)
        hardware_layout.addWidget(self.layer2_motion_checkbox)
        self.hardware_cards_widget = QWidget()
        self.hardware_cards_grid = QGridLayout(self.hardware_cards_widget)
        self.hardware_cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.hardware_cards_grid.setSpacing(DESIGN_CARD_GAP)
        self.hardware_cards_scroll = QScrollArea()
        self.hardware_cards_scroll.setWidgetResizable(True)
        self.hardware_cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.hardware_cards_scroll.setMinimumHeight(310)
        self.hardware_cards_scroll.setWidget(self.hardware_cards_widget)
        self._hardware_resize_relay = ViewportResizeRelay(self._relayout_design_galleries, self)
        self.hardware_cards_scroll.viewport().installEventFilter(self._hardware_resize_relay)
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
        preview_header = QHBoxLayout()
        preview_title = QLabel("Live-Vorschau · Levita 1600 × 720 · Hintergrund + Ebene 2")
        preview_title.setObjectName("muted")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        preview_header.addWidget(preview_title, 1)
        preview_header.addWidget(QLabel("Vorschau-FPS"))
        self.preview_fps_combo = QComboBox()
        self.preview_fps_combo.addItem("30 FPS", 30)
        self.preview_fps_combo.addItem("60 FPS", 60)
        self.preview_fps_combo.setCurrentIndex(max(0, self.preview_fps_combo.findData(self.preview_fps)))
        self.preview_fps_combo.currentIndexChanged.connect(self._preview_fps_changed)
        preview_header.addWidget(self.preview_fps_combo)
        preview_header.addWidget(QLabel("LCD-FPS"))
        self.lcd_fps_combo = QComboBox()
        self._populate_lcd_fps_combo()
        self.lcd_fps_combo.currentIndexChanged.connect(self._desktop_fps_changed)
        preview_header.addWidget(self.lcd_fps_combo)
        preview_stage_layout.addLayout(preview_header)
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
        performance_box = QGroupBox("Leistungsmodus und Spielerkennung")
        performance_layout = QGridLayout(performance_box)
        self.game_auto_checkbox = QCheckBox("Spielmodus automatisch erkennen")
        self.game_auto_checkbox.setChecked(self.game_auto_detection)
        self.game_auto_checkbox.toggled.connect(self._game_policy_changed)
        self.game_manual_checkbox = QCheckBox("Spielmodus manuell")
        self.game_manual_checkbox.toggled.connect(self._game_policy_changed)
        self.game_fullscreen_checkbox = QCheckBox("Vollbildanwendungen erkennen")
        self.game_fullscreen_checkbox.setChecked(self.game_fullscreen_detection)
        self.game_fullscreen_checkbox.toggled.connect(self._game_policy_changed)
        self.game_borderless_checkbox = QCheckBox("Rahmenlose Vollbildfenster erkennen")
        self.game_borderless_checkbox.setChecked(self.game_borderless_detection)
        self.game_borderless_checkbox.toggled.connect(self._game_policy_changed)
        self.game_fps_combo = QComboBox()
        self._populate_game_fps_combo()
        self.game_fps_combo.currentIndexChanged.connect(self._game_fps_changed)
        self.game_process_input = QLineEdit(", ".join(self.game_process_names))
        self.game_process_input.setReadOnly(True)
        self.game_process_input.setPlaceholderText("Keine zusätzlichen Spiele ausgewählt")
        self.game_program_manager_button = QPushButton("Spiele-Programmliste verwalten …")
        self.game_program_manager_button.clicked.connect(self._toggle_game_program_manager)
        self.game_status_label = QLabel("Desktop · LCD-Sollwert 15 FPS")
        self.game_status_label.setObjectName("muted")
        performance_layout.addWidget(self.game_auto_checkbox, 0, 0)
        performance_layout.addWidget(self.game_manual_checkbox, 0, 1)
        performance_layout.addWidget(QLabel("LCD-FPS im Spiel"), 0, 2)
        performance_layout.addWidget(self.game_fps_combo, 0, 3)
        performance_layout.addWidget(self.game_fullscreen_checkbox, 1, 0, 1, 2)
        performance_layout.addWidget(self.game_borderless_checkbox, 1, 2, 1, 2)
        performance_layout.addWidget(QLabel("Spiele-Programmliste"), 2, 0)
        performance_layout.addWidget(self.game_process_input, 2, 1, 1, 2)
        performance_layout.addWidget(self.game_program_manager_button, 2, 3)
        self.game_program_manager = ProgramManagerPanel(
            lambda text: text,
            self.game_process_input.text(),
            self.settings.value("thermalright/game_process_paths", ""),
            self._game_program_selection_changed,
            performance_box,
        )
        self.game_program_manager.close_button.clicked.connect(self._toggle_game_program_manager)
        self.game_program_manager.hide()
        performance_layout.addWidget(self.game_program_manager, 3, 0, 1, 4)
        performance_layout.addWidget(self.game_status_label, 4, 0, 1, 4)
        performance_note = QLabel(
            "Erkennung: Feral GameMode, Gamescope, ausdrücklich eingetragene Programme oder – wenn aktiviert – "
            "das aktive KDE-Vollbild beziehungsweise rahmenlose Vollbildfenster. Keine CPU-/GPU-Lastschätzung."
        )
        performance_note.setWordWrap(True)
        performance_note.setObjectName("muted")
        performance_layout.addWidget(performance_note, 5, 0, 1, 4)
        preview_stage_layout.addWidget(performance_box)
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
        overlay_box_layout = QVBoxLayout(self.custom_overlays_box)
        overlay_note = QLabel(
            "Hardwarewerte und mehrere eigene Texte lassen sich frei positionieren. "
            "Die Schriftenliste stammt ausschließlich aus den lokal installierten Qt-Schriften."
        )
        overlay_note.setWordWrap(True)
        overlay_note.setObjectName("muted")
        overlay_box_layout.addWidget(overlay_note)
        self.overlay_table_widget = QWidget()
        self.overlay_grid = QGridLayout(self.overlay_table_widget)
        self.overlay_grid.setContentsMargins(0, 0, 0, 0)
        self.overlay_grid.setColumnStretch(1, 1)
        self.overlay_grid.setColumnStretch(2, 1)
        overlay_box_layout.addWidget(self.overlay_table_widget)
        overlay_actions = QHBoxLayout()
        add_text_button = QPushButton("+ Eigenen Text hinzufügen")
        add_text_button.clicked.connect(self.add_custom_text_overlay)
        overlay_actions.addWidget(add_text_button)
        reset_button = QPushButton("Hardware-Infos zurücksetzen")
        reset_button.clicked.connect(self.reset_overlays)
        overlay_actions.addWidget(reset_button)
        undo_button = QPushButton("Letzten Zustand wiederherstellen")
        undo_button.clicked.connect(self.undo_overlay_change)
        self.overlay_undo_button = undo_button
        self.overlay_undo_button.setEnabled(False)
        overlay_actions.addWidget(undo_button)
        two_rows_button = QPushButton("Zwei saubere Reihen")
        two_rows_button.clicked.connect(lambda: self.apply_overlay_layout("two_rows"))
        overlay_actions.addWidget(two_rows_button)
        vertical_button = QPushButton("Untereinander")
        vertical_button.clicked.connect(lambda: self.apply_overlay_layout("vertical"))
        overlay_actions.addWidget(vertical_button)
        overlay_actions.addStretch(1)
        overlay_box_layout.addLayout(overlay_actions)
        self._rebuild_overlay_controls()
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

        from modules.lcd_levita.v1_7.media_preview import MediaPreview
        self.media_preview = MediaPreview(self)

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
        custom_texts: list[OverlaySpec] = []
        if isinstance(values, list):
            for value in values:
                if not isinstance(value, dict):
                    continue
                ident = str(value.get("ident") or "")
                try:
                    if ident in defaults:
                        base = defaults[ident]
                        loaded.append(replace(
                            base,
                            x=int(value.get("x", base.x)), y=int(value.get("y", base.y)),
                            size=int(value.get("size", base.size)), color=str(value.get("color", base.color)),
                            visible=bool(value.get("visible", base.visible)),
                            font=str(value.get("font", base.font)),
                            italic=bool(value.get("italic", base.italic)),
                        ).bounded())
                    elif (
                        ident.startswith("ohc-text-")
                        and str(value.get("kind") or "") == "text"
                        and len(custom_texts) < MAX_CUSTOM_TEXT_OVERLAYS
                    ):
                        custom_texts.append(OverlaySpec(
                            ident=ident,
                            label=str(value.get("label") or f"Eigener Text {len(custom_texts) + 1}"),
                            kind="text",
                            text=str(value.get("text") or "Eigener Text"),
                            sample=str(value.get("text") or "Eigener Text"),
                            x=int(value.get("x", 760)),
                            y=int(value.get("y", 180 + len(custom_texts) * 70)),
                            size=int(value.get("size", 42)),
                            color=str(value.get("color") or "#ffffff"),
                            visible=bool(value.get("visible", True)),
                            font=str(value.get("font") or ""),
                            bold=bool(value.get("bold", True)),
                            italic=bool(value.get("italic", False)),
                        ).bounded())
                except (TypeError, ValueError):
                    continue
        by_id = {item.ident: item for item in loaded}
        return [by_id.get(item.ident, item) for item in DEFAULT_OVERLAYS] + custom_texts

    def _save_overlays(self) -> None:
        self.settings.setValue("thermalright/overlays", json.dumps([asdict(item) for item in self.overlay_specs]))

    def _rebuild_overlay_controls(self) -> None:
        """Recreate the bounded editor rows after adding/removing text."""

        while self.overlay_grid.count():
            item = self.overlay_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.overlay_controls.clear()
        for column, title in enumerate(("Ein", "Element / Text", "Lokale Schrift", "X", "Y", "Größe", "Farbe", "")):
            self.overlay_grid.addWidget(QLabel(title), 0, column)
        font_families = tuple(QFontDatabase.families())
        for row, spec in enumerate(self.overlay_specs, start=1):
            visible = QCheckBox()
            visible.setChecked(spec.visible)
            if spec.kind == "text":
                label: QWidget = QLineEdit(spec.text)
                label.setToolTip("Text, der auf dem Display erscheinen soll")
                label.setMaxLength(160)
            else:
                label = QLabel(spec.label)
            font_combo = QComboBox()
            font_combo.setProperty("i18nTranslateItems", False)
            font_combo.addItem("Systemstandard", "")
            for family in font_families:
                font_combo.addItem(family, family)
            font_combo.setCurrentIndex(max(0, font_combo.findData(spec.font)))
            font_combo.setMinimumWidth(170)
            font_combo.setMaxVisibleItems(18)
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
            remove_button = QPushButton("Entfernen" if spec.kind == "text" else "—")
            remove_button.setEnabled(spec.kind == "text")
            controls: dict[str, QWidget] = {
                "visible": visible, "label": label, "font": font_combo,
                "x": x_spin, "y": y_spin, "size": size_spin,
                "color": color_button, "remove": remove_button,
            }
            self.overlay_controls[spec.ident] = controls
            visible.toggled.connect(lambda checked, ident=spec.ident: self._overlay_control_changed(ident, visible=checked))
            if isinstance(label, QLineEdit):
                label.editingFinished.connect(
                    lambda ident=spec.ident, editor=label: self._overlay_control_changed(
                        ident, text=editor.text(), sample=editor.text(),
                    )
                )
            font_combo.currentIndexChanged.connect(
                lambda _index, ident=spec.ident, combo=font_combo: self._overlay_control_changed(
                    ident, font=str(combo.currentData() or ""),
                )
            )
            x_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, x=value))
            y_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, y=value))
            size_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, size=value))
            color_button.clicked.connect(lambda _checked=False, ident=spec.ident: self._choose_overlay_color(ident))
            remove_button.clicked.connect(lambda _checked=False, ident=spec.ident: self.remove_custom_text_overlay(ident))
            for column, widget in enumerate((visible, label, font_combo, x_spin, y_spin, size_spin, color_button, remove_button)):
                self.overlay_grid.addWidget(widget, row, column)

    def add_custom_text_overlay(self) -> None:
        existing = {item.ident for item in self.overlay_specs}
        custom_count = sum(item.kind == "text" for item in self.overlay_specs)
        if custom_count >= MAX_CUSTOM_TEXT_OVERLAYS:
            self._status(f"Maximal {MAX_CUSTOM_TEXT_OVERLAYS} eigene Texte sind möglich", error=True)
            return
        number = next(index for index in range(1, MAX_CUSTOM_TEXT_OVERLAYS + 1) if f"ohc-text-{index:02d}" not in existing)
        self._remember_overlay_state()
        text = f"Eigener Text {number}"
        self.overlay_specs.append(OverlaySpec(
            ident=f"ohc-text-{number:02d}", label=text, kind="text",
            text=text, sample=text, x=760, y=min(650, 150 + custom_count * 70),
            size=42, color="#ffffff", bold=True,
        ).bounded(safe_right_x=self._safe_right_x()))
        self._rebuild_overlay_controls()
        self._save_overlays()
        self.canvas.set_specs(self.overlay_specs if self.current_hardware_design_path() is None else ())
        self._status(f"{text} hinzugefügt · Text, Schrift, Größe und Position sind jetzt bearbeitbar")

    def remove_custom_text_overlay(self, ident: str) -> None:
        index = self._overlay_index(ident)
        if self.overlay_specs[index].kind != "text":
            return
        self._remember_overlay_state()
        removed = self.overlay_specs.pop(index)
        self._rebuild_overlay_controls()
        self._save_overlays()
        self.canvas.set_specs(self.overlay_specs if self.current_hardware_design_path() is None else ())
        self._status(f"{removed.label} entfernt")

    def _log(self, message: str) -> None:
        if self.log_ready and self.log_callback:
            self.log_callback(f"THERMALRIGHT: {message}")

    def _status(self, message: str, *, error: bool = False) -> None:
        self.preview_status.setText(message)
        self.preview_status.setObjectName("warningText" if error else "muted")
        self.preview_status.style().unpolish(self.preview_status)
        self.preview_status.style().polish(self.preview_status)
        if error:
            self._log(f"FEHLER: {message}")
        else:
            self._log(message)

    def refresh_backend_status(self) -> None:
        self.cli = ThermalrightCli()
        if hasattr(self, "install_backend_button"):
            self.install_backend_button.setVisible(self.device_present and not self.cli.available)
        if self.cli.available:
            self.backend_status.setText("TRCC-Linux-Backend gefunden · Gerät noch nicht geprüft")
        else:
            self.backend_status.setText("TRCC-Linux-Backend fehlt · Testmodus und Designimport funktionieren trotzdem")

    def _on_test_mode_changed(self, checked: bool) -> None:
        self.settings.setValue("thermalright/test_mode", checked)
        self._status("Testmodus aktiv · keine USB-Schreibzugriffe" if checked else "Hardwaremodus freigegeben · Aktionen benötigen TRCC Linux")

    def _lcd_write_allowed(self) -> bool:
        raw = self.settings.value("features/enabled", None)
        if raw not in (None, ""):
            try:
                values = json.loads(raw) if isinstance(raw, str) else raw
            except (TypeError, ValueError, json.JSONDecodeError):
                values = ()
            if isinstance(values, (list, tuple, set)) and "lcd" not in values:
                return False
        owner = str(self.settings.value("control_authority/lcd", "auto") or "auto")
        return owner in {"auto", "ohc_trcc"}


    def _autostart_toggled(self, checked: bool) -> None:
        self.settings.setValue("thermalright/autostart_enabled", checked)
        if checked and not self.design_state.has_standard():
            self.remember_startup_design()
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
        self._remember_startup_media(media)

    def _remember_startup_media(self, media: Path, *, enable: bool = True) -> bool:
        """Persist one canonical Levita start design from any trusted UI page."""

        if not media.exists():
            return False
        self.design_state.invalidate_startup()
        self.startup_apply_requested = True
        self.startup_apply_active = False
        hardware = self.current_hardware_design_path()
        self.settings.setValue("thermalright/start_media", str(media.resolve()))
        self.settings.setValue(
            "thermalright/start_hardware_design", str(hardware.resolve()) if hardware else "",
        )
        self.settings.setValue("thermalright/start_layer2_motion", self._layer2_motion_enabled(hardware))
        self.settings.setValue("thermalright/start_desktop_fps", self.desktop_lcd_fps)
        self.settings.setValue("thermalright/start_game_fps", self.game_lcd_fps)
        if enable:
            self.autostart_enabled.setChecked(True)
        self.stage_profile_startup_design()
        self.settings.sync()
        self._refresh_startup_status()
        self._status(
            "Aktuelle Ebenen als Levita-Startdesign gespeichert · globale Kraken-LCD-Aktionen bleiben getrennt"
        )
        return True

    def remember_effect_startup_design(self, path: Path, *, bundled: bool) -> bool:
        """Save a validated Display Effects selection as the shared Levita standard."""

        root = (
            Path(__file__).resolve().parent / "assets" / "display-effects"
            if bundled else self.generated_effect_directory()
        )
        candidate = validate_effect_handoff(path, root)
        return self._remember_startup_media(candidate)

    def stage_profile_startup_design(self) -> bool:
        """Remember the current Levita layers for the next profile save only."""

        media = self.current_media_path()
        if media is None or not media.exists():
            return False
        return self._store_pending_profile_startup(media)

    def stage_profile_effect_media(self, path: Path, *, bundled: bool) -> bool:
        """Stage validated effect media without selecting or applying it to hardware."""

        root = (
            Path(__file__).resolve().parent / "assets" / "display-effects"
            if bundled else self.generated_effect_directory()
        )
        candidate = validate_effect_handoff(path, root)
        return self._store_pending_profile_startup(candidate)

    def _store_pending_profile_startup(self, media: Path) -> bool:
        hardware = self.current_hardware_design_path()
        self.settings.setValue("thermalright/profile_pending_media", str(media.resolve()))
        self.settings.setValue(
            "thermalright/profile_pending_hardware_design",
            str(hardware.resolve()) if hardware and hardware.exists() else "",
        )
        self.settings.setValue(
            "thermalright/profile_pending_layer2_motion", self._layer2_motion_enabled(hardware),
        )
        self.settings.setValue("thermalright/profile_pending_desktop_fps", self.desktop_lcd_fps)
        self.settings.setValue("thermalright/profile_pending_game_fps", self.game_lcd_fps)
        self.settings.sync()
        return True

    def profile_startup_payload(self) -> dict[str, object] | None:
        """Return a staged Levita startup choice for an LCD or full profile."""

        media_value = str(self.settings.value("thermalright/profile_pending_media", "") or "")
        if not media_value or not Path(media_value).exists():
            return None
        hardware_value = str(
            self.settings.value("thermalright/profile_pending_hardware_design", "") or ""
        )
        if hardware_value and not Path(hardware_value).exists():
            hardware_value = ""
        return {
            "media": str(Path(media_value).resolve()),
            "hardware_design": str(Path(hardware_value).resolve()) if hardware_value else "",
            "enabled": True,
            "layer2_motion": self.settings.value(
                "thermalright/profile_pending_layer2_motion", True, type=bool,
            ),
            "desktop_fps": normalize_lcd_fps(
                self.settings.value("thermalright/profile_pending_desktop_fps", 15),
                experimental_60=self.experimental_60_fps,
            ),
            "game_fps": normalize_lcd_fps(
                self.settings.value("thermalright/profile_pending_game_fps", 15),
                experimental_60=self.experimental_60_fps,
            ),
        }

    def restore_profile_startup_payload(self, payload: dict[str, object], *, startup: bool = False) -> bool:
        """An explicit profile load may replace the one shared Levita standard."""

        if startup and self.design_state.has_standard():
            self._log("LCD-START: gespeicherter Levita-Standard hat Vorrang vor dem automatischen Profil")
            return False

        media_value = str(payload.get("media", "") or "")
        if not bool(payload.get("enabled", True)) or not media_value:
            return False
        media = Path(media_value)
        if not media.exists():
            self._log("LCD-START: Levita-Medium aus dem Profil ist nicht mehr vorhanden")
            return False
        hardware_value = str(payload.get("hardware_design", "") or "")
        hardware = Path(hardware_value) if hardware_value else None
        if hardware is not None and not hardware.exists():
            hardware_value = ""
        self.settings.setValue("thermalright/start_media", str(media.resolve()))
        self.settings.setValue(
            "thermalright/start_hardware_design",
            str(Path(hardware_value).resolve()) if hardware_value else "",
        )
        self.settings.setValue("thermalright/profile_pending_media", str(media.resolve()))
        self.settings.setValue(
            "thermalright/profile_pending_hardware_design",
            str(Path(hardware_value).resolve()) if hardware_value else "",
        )
        motion_enabled = bool(payload.get("layer2_motion", True))
        if hardware_value:
            key = self._layer2_key(Path(hardware_value))
            self.layer2_motion_overrides[key] = motion_enabled
            self.settings.setValue(
                "thermalright/layer2_motion_overrides",
                json.dumps(self.layer2_motion_overrides, ensure_ascii=False, sort_keys=True),
            )
        self.desktop_lcd_fps = normalize_lcd_fps(
            payload.get("desktop_fps", 15), experimental_60=self.experimental_60_fps,
        )
        self.game_lcd_fps = normalize_lcd_fps(
            payload.get("game_fps", 15), experimental_60=self.experimental_60_fps,
        )
        self.settings.setValue("thermalright/desktop_fps", self.desktop_lcd_fps)
        self.settings.setValue("thermalright/game_fps", self.game_lcd_fps)
        self._populate_lcd_fps_combo()
        self._populate_game_fps_combo()
        self.design_state.invalidate_startup()
        self.settings.setValue("thermalright/start_layer2_motion", motion_enabled)
        self.settings.setValue("thermalright/start_desktop_fps", self.desktop_lcd_fps)
        self.settings.setValue("thermalright/start_game_fps", self.game_lcd_fps)
        self.settings.setValue("thermalright/profile_pending_layer2_motion", motion_enabled)
        self.settings.setValue("thermalright/profile_pending_desktop_fps", self.desktop_lcd_fps)
        self.settings.setValue("thermalright/profile_pending_game_fps", self.game_lcd_fps)
        self.settings.setValue("thermalright/autostart_enabled", True)
        self.settings.sync()
        self.autostart_enabled.blockSignals(True)
        self.autostart_enabled.setChecked(True)
        self.autostart_enabled.blockSignals(False)
        self._refresh_startup_status()
        self._log("LCD-START: Levita-Startdesign aus dem ausgewählten Profil vorgemerkt")
        return True

    def _sync_autostart_selection_if_enabled(self) -> None:
        # Preview edits never rewrite the explicitly saved startup standard.
        if getattr(self, "startup_apply_active", False) and not self.restoring_startup_selection:
            self.design_state.invalidate_startup()
            self.startup_apply_active = False
        self._refresh_startup_status()

    def _restore_startup_selection(self) -> bool:
        media_value = str(self.settings.value("thermalright/start_media", "") or "")
        hardware_value = str(self.settings.value("thermalright/start_hardware_design", "") or "")
        if not media_value or not Path(media_value).exists():
            self._status("Gespeichertes Levita-Startdesign ist nicht mehr vorhanden", error=True)
            return False
        self.desktop_lcd_fps = normalize_lcd_fps(
            self.settings.value("thermalright/start_desktop_fps", self.desktop_lcd_fps),
            experimental_60=self.experimental_60_fps,
        )
        self.game_lcd_fps = normalize_lcd_fps(
            self.settings.value("thermalright/start_game_fps", self.game_lcd_fps),
            experimental_60=self.experimental_60_fps,
        )
        self._populate_lcd_fps_combo()
        self._populate_game_fps_combo()
        self._register_saved_effect_media(Path(media_value))
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
            if hardware_value:
                self.layer2_motion_overrides[self._layer2_key(Path(hardware_value))] = self.settings.value(
                    "thermalright/start_layer2_motion", True, type=bool,
                )
                self._sync_layer2_motion_control()
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

    def _register_saved_effect_media(self, path: Path) -> None:
        """Re-enrol one validated effect that is not part of the LCD gallery scan."""

        try:
            resolved = path.resolve()
        except OSError:
            return
        if any(entry.path == resolved for entry in self.media_entries):
            return
        bundled_root = Path(__file__).resolve().parent / "assets" / "display-effects"
        for root in (self.generated_effect_directory(), bundled_root):
            try:
                candidate = validate_effect_handoff(resolved, root)
            except (OSError, ValueError):
                continue
            self.media_entries.append(
                MediaEntry(candidate, f"Display-Effekte / {candidate.stem}", "video")
            )
            return

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

    def activate_staged_profile_design(self) -> None:
        """Apply a profile-staged Levita design through the guarded startup pipeline."""

        self.startup_apply_requested = False
        self.apply_startup_design_if_enabled(competing_lcd_action=False)


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
        generation = self.design_state.generation
        QTimer.singleShot(3000, self, lambda: self.apply_design(startup=True)
                          if generation == self.design_state.generation
                          and self.startup_apply_active and not self.shutdown_started else None)

    def choose_media_directory(self) -> None:
        translator = getattr(self.window(), "tr_static", None)
        dialog = DesignLibraryDialog(
            self.design_library_state,
            translator if callable(translator) else None,
            self,
        )
        if not dialog.exec():
            return
        self.design_library_state = dialog.state()
        self.settings.setValue(
            "thermalright/design_library_v1", save_library_state(self.design_library_state),
        )
        self.custom_media_directory = (
            self.design_library_state.folders[0]
            if self.design_library_state.folders else None
        )
        if self.custom_media_directory is not None:
            self.settings.setValue("thermalright/custom_media_directory", str(self.custom_media_directory))
            self.settings.setValue("thermalright/media_directory", str(self.custom_media_directory))
        else:
            self.settings.remove("thermalright/custom_media_directory")
            self.settings.remove("thermalright/media_directory")
        enabled = self.design_library_state.has_sources
        self.custom_media_enabled.setEnabled(enabled)
        self.custom_media_enabled.blockSignals(True)
        self.custom_media_enabled.setChecked(enabled)
        self.custom_media_enabled.blockSignals(False)
        self.settings.setValue("thermalright/custom_media_enabled", enabled)
        self.remembered_media_button.setEnabled(enabled)
        self._reload_managed_library()

    def _reload_managed_library(self) -> None:
        standard = default_trcc_design_directory()
        source = self.custom_media_directory or standard
        if source is None and self.design_library_state.files:
            source = self.design_library_state.files[0].parent
        if source is None:
            self.media_entries = []
            self._populate_media_categories()
            self._populate_hardware_design_combo()
            self._apply_media_filter()
            return
        self.load_media_directory(source, quiet=True, remember_custom=False, force_catalog=False)

    def show_remembered_media_directory(self) -> None:
        if not self.design_library_state.has_sources:
            self._status("Der gemerkte Designordner ist nicht mehr vorhanden", error=True)
            return
        self.custom_media_enabled.blockSignals(True)
        self.custom_media_enabled.setChecked(True)
        self.custom_media_enabled.blockSignals(False)
        self.settings.setValue("thermalright/custom_media_enabled", True)
        self._reload_managed_library()
        source = self.custom_media_directory or self.design_library_state.files[0]
        self._select_library_source(source, prefer_saved_custom=True)

    def _toggle_custom_media_directory(self, checked: bool) -> None:
        self.settings.setValue("thermalright/custom_media_enabled", checked)
        standard = default_trcc_design_directory()
        self._reload_managed_library()
        if checked and self.design_library_state.has_sources:
            source = self.custom_media_directory or self.design_library_state.files[0]
            self._select_library_source(source, prefer_saved_custom=True)
            self._status("Eigener Designordner wieder eingeblendet · gespeicherte Auswahl wiederhergestellt")
        else:
            self._select_library_source(standard, prefer_theme=True)
            self._status("Eigener Designordner aus OHC ausgeblendet · Dateien auf der Festplatte bleiben erhalten")

    def load_default_trcc_designs(self, _checked: bool = False, *, quiet: bool = False) -> None:
        directory = default_trcc_design_directory()
        if directory is None:
            directory = Path(__file__).resolve().parent / "assets" / "levita-designs"
            if not directory.is_dir():
                if not quiet:
                    self._status(
                        "Keine installierten TRCC-Standarddesigns für Levita 1600×720 gefunden",
                        error=True,
                    )
                return
        self.load_media_directory(
            directory, quiet=True, remember_custom=False, force_catalog=not quiet,
        )
        self._select_library_source(directory, prefer_theme=True)
        if not quiet:
            self._status(
                "TRCC-Standarddesigns angezeigt · eigener Designordner bleibt gespeichert"
            )

    def load_media_directory(
        self, directory: Path, *, quiet: bool = False, remember_custom: bool = True,
        force_catalog: bool = True,
    ) -> None:
        try:
            requested = directory.expanduser().resolve()
            roots: list[tuple[str, Path]] = []
            standard = default_trcc_design_directory()
            if standard is not None:
                roots.append(("TRCC-Standard", standard))
            for media_root in default_trcc_media_directories():
                label = "TRCC-Katalog" if ".trcc/data" in str(media_root) else "Eigene TRCC-Dateien"
                roots.append((label, media_root))
            if remember_custom:
                folders = list(self.design_library_state.folders)
                if requested not in folders:
                    folders.append(requested)
                self.design_library_state = replace(
                    self.design_library_state, folders=tuple(folders[:32]),
                )
                self.settings.setValue(
                    "thermalright/design_library_v1", save_library_state(self.design_library_state),
                )
                self.custom_media_directory = self.design_library_state.folders[0]
                self.settings.setValue("thermalright/custom_media_directory", str(requested))
                self.settings.setValue("thermalright/media_directory", str(requested))
                self.settings.setValue("thermalright/custom_media_enabled", True)
                self.custom_media_enabled.blockSignals(True)
                self.custom_media_enabled.setChecked(True)
                self.custom_media_enabled.blockSignals(False)
                self.custom_media_enabled.setEnabled(True)
                self.remembered_media_button.setEnabled(True)
            if self.custom_media_enabled.isChecked():
                for number, custom in enumerate(self.design_library_state.folders, 1):
                    if custom != standard:
                        roots.append((f"Eigener Ordner {number}", custom))
            if not roots and requested.is_dir() and not self.design_library_state.files:
                roots.append(("Ausgewählter Ordner", requested))
            entries: list[MediaEntry] = []
            seen: set[Path] = set()
            builtin_dir = Path(__file__).resolve().parent / "assets" / "levita-designs"
            builtin_names = (
                ("ohc-carbon-blue.png", "Kohlefaserblau"),
                ("ohc-titanium-blue.png", "Titanblau"),
                ("ohc-plasma-circuit.png", "Plasmaschaltkreis"),
                ("ohc-ai-neon-corridor.png", "Neon-Korridor"),
                ("ohc-ai-orbital-observatory.png", "Orbital-Observatorium"),
                ("ohc-ai-neon-city.png", "Neonstadt"),
                ("ohc-ai-azure-reactor.png", "Azur-Reaktor"),
                ("ohc-ai-deep-space-command.png", "Tiefenraum-Zentrale"),
                ("ohc-ai-quantum-portal.png", "Quantenportal"),
                ("ohc-ai-crystal-core.png", "Kristallkern"),
                ("ohc-ai-command-deck.png", "Kommando-Deck"),
            )
            for filename, title in builtin_names:
                path = (builtin_dir / filename).resolve()
                if path.is_file():
                    entries.append(MediaEntry(path, f"OHC-Designs / {title}", "image"))
                    seen.add(path)
            for filename, title in (
                ("ohc-ai-quantum-voyage-30s.mp4", "Cyberreise · 30 s"),
                ("ohc-3d-orbital-ring-10s.mp4", "Orbitalring · 3D · 10 s"),
                ("ohc-3d-neon-apex-10s.mp4", "Neonspitze · 3D · 10 s"),
                ("ohc-3d-quantum-core-10s.mp4", "Quantenkern · 3D · 10 s"),
            ):
                path = (builtin_dir / filename).resolve()
                if path.is_file():
                    entries.append(MediaEntry(path, f"OHC-Designs / {title}", "video"))
                    seen.add(path)
            effects_dir = self.generated_effect_directory()
            for path in sorted(effects_dir.glob("*.mp4")) if effects_dir.is_dir() else ():
                resolved = path.resolve()
                if path.is_symlink() or not resolved.is_file() or resolved in seen:
                    continue
                entries.append(MediaEntry(resolved, f"Display-Effekte / {path.stem}", "video"))
                seen.add(resolved)
            for dirname, title in BUILTIN_LEVITA_THEMES:
                path = (builtin_dir / dirname).resolve()
                if trcc_theme_is_supported(path):
                    entries.append(MediaEntry(path, f"OHC-Designs / {title} · TRCC-Layout", "theme"))
                    seen.add(path)
            for label, root in roots:
                root_entries = self._scan_media_root(root, force=force_catalog)
                if label == "TRCC-Katalog":
                    root_entries = collapse_catalog_previews(root_entries)
                for entry in root_entries:
                    if entry.path in seen or entry.path in self.design_library_state.excluded:
                        continue
                    seen.add(entry.path)
                    title = friendly_media_name(
                        entry.path,
                        self.design_library_state.aliases.get(str(entry.path), ""),
                    )
                    entries.append(MediaEntry(
                        path=entry.path,
                        relative_name=f"{label} / {title}",
                        kind=entry.kind,
                    ))
            if self.custom_media_enabled.isChecked():
                for path in self.design_library_state.files:
                    if path in seen or path in self.design_library_state.excluded:
                        continue
                    seen.add(path)
                    title = friendly_media_name(
                        path, self.design_library_state.aliases.get(str(path), ""),
                    )
                    kind = "image" if path.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES else "video"
                    entries.append(MediaEntry(path, f"Eigene Datei / {title}", kind))
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
        source_count = len(self.design_library_state.folders) + len(self.design_library_state.files)
        custom_text = (
            f"{source_count} eigene Quellen eingeblendet"
            if self.custom_media_enabled.isChecked() and source_count
            else f"{source_count} eigene Quellen ausgeblendet"
            if source_count else "keine eigenen Quellen gespeichert"
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
        self.library_loaded = True
        self.library_ready.emit()

    def _scan_media_root(self, root: Path, *, force: bool) -> list[MediaEntry]:
        budget = cache_budget_mb(self.settings)
        namespace = "levita-" + hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:16]
        records = cached_catalog_records(namespace, (root,), budget, force=force)
        if records is not None:
            result: list[MediaEntry] = []
            for record in records:
                try:
                    raw_path = Path(str(record["path"]))
                    if raw_path.is_symlink():
                        continue
                    path = raw_path.resolve()
                    path.relative_to(root.resolve())
                    kind = str(record["kind"])
                    valid_path = path.is_dir() if kind == "theme" else path.is_file()
                    if kind not in {"image", "video", "theme"} or not valid_path:
                        continue
                    result.append(MediaEntry(path, str(record["name"])[:500], kind))
                except (KeyError, OSError, ValueError):
                    continue
            return result
        result = scan_media_directory(root)
        save_catalog_records(namespace, (root,), [
            {"path": str(entry.path), "name": entry.relative_name, "kind": entry.kind}
            for entry in result
        ], budget)
        return result

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
            button.setObjectName("lcdCategoryButton")
            button.setText(self.media_category.itemText(index))
            button.setCheckable(True)
            button.setChecked(key == current)
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
        from modules.ui_performance.v1_1.thumbnails import card_source
        pixmap = card_source(source, self.settings) if source else QPixmap()
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
        catalog_preview = media.with_suffix(".png")
        if (
            not catalog_preview.is_symlink()
            and catalog_preview.is_file()
            and catalog_preview.parent == media.parent
        ):
            return catalog_preview
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
        target = preview_cache_path("levita-video", media, cache_budget_mb(self.settings))
        target = target or self.cache_dir / f"card-{fingerprint}.jpg"
        return fingerprint, target, target.with_suffix(".failed")

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
        if not self.thumbnail_ffmpeg or self.thumbnail_shutting_down or not self.isVisible():
            return
        for worker in self.thumbnail_workers:
            if worker in self.thumbnail_active or not self.thumbnail_queue:
                continue
            visible_index = next(
                (index for index, item in enumerate(self.thumbnail_queue) if self._thumbnail_job_visible(item[0])),
                -1,
            )
            if visible_index < 0:
                return
            item = self.thumbnail_queue.pop(visible_index)
            _key, media, target, _failure = item
            self.thumbnail_active[worker] = item
            worker.start(self.thumbnail_ffmpeg, [
                "-v", "error", "-nostdin", "-ss", "0.15", "-i", str(media),
                "-frames:v", "1", "-q:v", "5", "-y", str(target),
            ])
            self.thumbnail_worker_timeouts[worker].start()

    def _thumbnail_job_visible(self, key: str) -> bool:
        # A Python weak reference can still return its PySide wrapper after
        # Qt has already destroyed the underlying C++ card.  This happens
        # when the user switches large design categories while thumbnail
        # extraction is still queued.  Never call QWidget methods until the
        # wrapper has passed shiboken's lifetime check.
        waiters = []
        for button_ref in self.thumbnail_waiters.get(key, ()):
            button = button_ref()
            if button is not None and isValid(button):
                waiters.append(button_ref)
        if waiters:
            self.thumbnail_waiters[key] = waiters
        else:
            self.thumbnail_waiters.pop(key, None)
        if not waiters:
            return self.isVisible()
        for button_ref in waiters:
            button = button_ref()
            if button is None or not isValid(button):
                continue
            try:
                if not button.isVisibleTo(self):
                    continue
                for area in (self.media_cards_scroll, self.hardware_cards_scroll):
                    if area.isAncestorOf(button):
                        position = button.mapTo(area.viewport(), QPoint(0, 0))
                        if QRect(position, button.size()).intersects(area.viewport().rect()):
                            return True
            except RuntimeError:
                # A nested Qt event may invalidate the wrapper between the
                # explicit isValid check and the visibility query.
                continue
        return False

    def _pause_thumbnail_workers(self) -> None:
        for worker in tuple(self.thumbnail_active):
            self.thumbnail_paused_workers.add(worker)
            self.thumbnail_worker_timeouts[worker].stop()
            if worker.state() != QProcess.ProcessState.NotRunning:
                worker.kill()

    def _cancel_thumbnail_worker(self, worker: QProcess) -> None:
        if worker in self.thumbnail_active and worker.state() != QProcess.ProcessState.NotRunning:
            worker.kill()

    def _on_thumbnail_finished(
        self, worker: QProcess, exit_code: int, _status: QProcess.ExitStatus,
    ) -> None:
        if self.thumbnail_shutting_down or not isValid(self) or not isValid(worker):
            return
        self.thumbnail_worker_timeouts[worker].stop()
        item = self.thumbnail_active.pop(worker, None)
        if item is None:
            return
        if worker in self.thumbnail_paused_workers:
            self.thumbnail_paused_workers.discard(worker)
            self.thumbnail_queue.insert(0, item)
            self._start_thumbnail_workers()
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
                if button is None or not isValid(button):
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
        QTimer.singleShot(4_000, self, self._hide_thumbnail_progress_if_idle)

    def _hide_thumbnail_progress_if_idle(self) -> None:
        if not self.thumbnail_queue and not self.thumbnail_active:
            self.thumbnail_progress_panel.hide()

    def _design_card(self, entry: MediaEntry | None, *, hardware: bool = False) -> QToolButton:
        translate = getattr(self.window(), "tr_static", lambda text: text)
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
        button.setObjectName("lcdDesignCard")
        button.setCheckable(True)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setIcon(QIcon(self._card_thumbnail(entry)))
        button.setIconSize(QSize(DESIGN_CARD_WIDTH - 16, 79))
        favorite_key = "ohc://overlays" if entry is None else str(entry.path)
        favorite = favorite_key in self.design_favorites
        button.setText(translate(f"{'★ ' if favorite else ''}{title[:23]}\n{subtitle}"))
        button.setFixedSize(DESIGN_CARD_WIDTH, 126)
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
        button.setToolTip(translate("Linksklick: auswählen · Rechtsklick: Favorit und Ebenenzuordnung"))
        from modules.ui_performance.v1_1.dynamic_text import remember
        remember(self.window(), button, text=f"{'★ ' if favorite else ''}{title[:23]}\n{subtitle}",
                 tooltip="Linksklick: auswählen · Rechtsklick: Favorit und Ebenenzuordnung")
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

    def _rebuild_media_cards(self, entries: Iterable[MediaEntry], *, reuse: bool = False) -> None:
        self._visible_media_entries = list(entries)[:300]
        self._media_gallery_columns = self._gallery_columns(
            self.media_cards_scroll, *MEDIA_GALLERY_COLUMNS,
        )
        columns = self._media_gallery_columns
        for column in range(MEDIA_GALLERY_COLUMNS[1]):
            self.media_cards_grid.setColumnStretch(column, 1 if column < columns else 0)
        self.gallery_preparation.request(self._visible_media_entries, reuse=reuse)

    def _rebuild_hardware_cards(self, themes: Iterable[MediaEntry], *, reuse: bool = False) -> None:
        self._visible_hardware_themes = list(themes)
        self._hardware_gallery_columns = self._gallery_columns(
            self.hardware_cards_scroll, *HARDWARE_GALLERY_COLUMNS,
        )
        entries: list[MediaEntry | None] = [*self._visible_hardware_themes]
        if not self.favorites_only.isChecked() or "ohc://overlays" in self.design_favorites:
            entries.insert(0, None)
        columns = self._hardware_gallery_columns
        for column in range(HARDWARE_GALLERY_COLUMNS[1]):
            self.hardware_cards_grid.setColumnStretch(column, 1 if column < columns else 0)
        self.gallery_preparation.request(entries, hardware=True, reuse=reuse)

    def _materialize_visible_galleries(self) -> None:
        self._gallery_materialize_pending = False
        if self.shutdown_started or not self.isVisible():
            return
        if not self._media_cards_materialized:
            if "media" not in self.gallery_preparation.jobs:
                self._rebuild_media_cards(getattr(self, "_visible_media_entries", ()), reuse=True)
        if not self._hardware_cards_materialized:
            if "hardware" not in self.gallery_preparation.jobs:
                self._rebuild_hardware_cards(getattr(self, "_visible_hardware_themes", ()), reuse=True)
        self.gallery_preparation.wake()
        self._start_thumbnail_workers()

    def _gallery_columns(self, area: QScrollArea, minimum: int, maximum: int) -> int:
        return gallery_column_count(area.viewport().width(), minimum=minimum, maximum=maximum)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        if hasattr(self, "media_cards_scroll"):
            self._relayout_design_galleries()

    def showEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        super().showEvent(event)
        if self.shutdown_started:
            return
        if hasattr(self, 'media_preview'):
            self.media_preview.observer.timer.start(40)
        if len(self.hover_preview_frames) > 1 and not self.hover_preview_timer.isActive():
            self.hover_preview_timer.start()
        if not self._gallery_materialize_pending:
            self._gallery_materialize_pending = True
            # Paint the page shell first; constructing many local design cards
            # then happens in the next event-loop turn.
            QTimer.singleShot(0, self, self._materialize_visible_galleries)

    def hideEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        self.layer2_motion_timer.stop()
        self.hover_preview_timer.stop()
        self.hover_preview_debounce.stop()
        self._cancel_hover_extract()
        self._pause_thumbnail_workers()
        if hasattr(self, 'media_preview'):
            self.media_preview.refresh()
        super().hideEvent(event)

    def _relayout_design_galleries(self) -> None:
        media_columns = self._gallery_columns(self.media_cards_scroll, *MEDIA_GALLERY_COLUMNS)
        hardware_columns = self._gallery_columns(self.hardware_cards_scroll, *HARDWARE_GALLERY_COLUMNS)
        if media_columns != self._media_gallery_columns:
            self._rebuild_media_cards(self._visible_media_entries, reuse=True)
        if hardware_columns != self._hardware_gallery_columns:
            self._rebuild_hardware_cards(self._visible_hardware_themes, reuse=True)

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
        if path:
            resolved = Path(path).resolve()
            if resolved in self.design_library_state.files or any(
                resolved.is_relative_to(root) for root in self.design_library_state.folders
            ):
                self.settings.setValue("thermalright/custom_selected_media", path)
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

    def generated_effect_directory(self) -> Path:
        """Return the private cache root accepted for generated effect media."""

        return self.cache_dir / "display-effects"

    def select_generated_effect_media(self, path: Path, title: str = "Rauch") -> None:
        """Select a generated Layer-1 video without changing the active Layer 2."""

        candidate = validate_effect_handoff(path, self.generated_effect_directory())
        self._select_effect_media(candidate, title)

    def select_bundled_effect_media(self, path: Path, title: str) -> None:
        """Select one packaged offline library video through an explicit root."""

        bundled_root = Path(__file__).resolve().parent / "assets" / "display-effects"
        candidate = validate_effect_handoff(path, bundled_root)
        self._select_effect_media(candidate, title)

    def _select_effect_media(self, candidate: Path, title: str) -> None:
        known = any(entry.path == candidate for entry in self.media_entries)
        if not known:
            self.media_entries.append(MediaEntry(candidate, f"Display-Effekte / {title}", "video"))
        self.settings.setValue("thermalright/selected_media", str(candidate))
        self.settings.setValue("thermalright/custom_selected_media", str(candidate))
        index = self.media_combo.findData(str(candidate))
        if index < 0:
            self.media_filter.clear()
            all_index = self.media_category.findData("all")
            if all_index >= 0:
                self.media_category.setCurrentIndex(all_index)
            self._apply_media_filter()
            index = self.media_combo.findData(str(candidate))
        if index < 0:
            raise ValueError("Display-Effekt konnte nicht in den lokalen Katalog aufgenommen werden")
        self.media_combo.setCurrentIndex(index)
        self.update_preview()

    def layer2_preview_choices(self) -> list[tuple[str, str, QPixmap]]:
        """Expose the LCD Studio Layer-2 cards to sibling preview pages."""

        entries = {str(entry.path): entry for entry in self.media_entries}
        choices: list[tuple[str, str, QPixmap]] = []
        for index in range(self.hardware_design_combo.count()):
            path = str(self.hardware_design_combo.itemData(index) or "")
            choices.append((
                self.hardware_design_combo.itemText(index),
                path,
                self._card_thumbnail(entries.get(path) if path else None),
            ))
        return choices

    def sync_effect_preview(self, target: ThermalrightCanvas, background: QPixmap) -> None:
        """Copy the current Layer-2 state into an external effect preview canvas."""

        source = self.canvas
        target.set_layer_intensities(source._layer1_intensity, source._layer2_intensity)
        target.set_hardware_layer(source._hardware_layer)
        target.set_editable_layout(source._layout)
        target.set_specs(source._specs)
        target.set_background_offset(source._background_x, source._background_y)
        target.set_notch_mask(
            source._notch_visible,
            source._notch_width,
            source._notch_top_radius,
            source._notch_bottom_radius,
        )
        target.set_split_mode(source._split_mode)
        target.set_background(background)
        target.set_motion_layer(self._current_motion_pixmap())

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

    def _layer2_motion_enabled(self, design: Path | None = None) -> bool:
        selected = design if design is not None else self.current_hardware_design_path()
        if selected is None or selected.name not in ANIMATED_LAYER2_THEMES:
            return False
        return self.layer2_motion_overrides.get(self._layer2_key(selected), True)

    def _sync_layer2_motion_control(self) -> None:
        design = self.current_hardware_design_path()
        supported = design is not None and design.name in ANIMATED_LAYER2_THEMES
        self.layer2_motion_checkbox.blockSignals(True)
        self.layer2_motion_checkbox.setEnabled(supported)
        self.layer2_motion_checkbox.setChecked(self._layer2_motion_enabled(design))
        self.layer2_motion_checkbox.blockSignals(False)

    def _layer2_motion_changed(self, enabled: bool) -> None:
        design = self.current_hardware_design_path()
        if design is None or design.name not in ANIMATED_LAYER2_THEMES:
            return
        self.layer2_motion_overrides[self._layer2_key(design)] = bool(enabled)
        self.settings.setValue(
            "thermalright/layer2_motion_overrides",
            json.dumps(self.layer2_motion_overrides, ensure_ascii=False, sort_keys=True),
        )
        self._sync_autostart_selection_if_enabled()
        self.update_preview()
        state = "aktiv" if enabled else "aus"
        self._status(f"Dekor-Animation für {design.name}: {state}")

    def _populate_lcd_fps_combo(self) -> None:
        current = self.desktop_lcd_fps
        self.lcd_fps_combo.blockSignals(True)
        self.lcd_fps_combo.clear()
        for fps in SAFE_LCD_FPS:
            self.lcd_fps_combo.addItem(f"{fps} FPS", fps)
        if self.experimental_60_fps:
            self.lcd_fps_combo.addItem("60 FPS · Experimentell", 60)
        self.lcd_fps_combo.setCurrentIndex(max(0, self.lcd_fps_combo.findData(current)))
        self.lcd_fps_combo.blockSignals(False)

    def _populate_game_fps_combo(self) -> None:
        current = self.game_lcd_fps
        self.game_fps_combo.blockSignals(True)
        self.game_fps_combo.clear()
        for fps in SAFE_LCD_FPS:
            self.game_fps_combo.addItem(f"{fps} FPS", fps)
        if self.experimental_60_fps:
            self.game_fps_combo.addItem("60 FPS · Experimentell", 60)
        self.game_fps_combo.setCurrentIndex(max(0, self.game_fps_combo.findData(current)))
        self.game_fps_combo.blockSignals(False)

    def configure_experimental_60(self, enabled: bool) -> None:
        """Expose 60 FPS only after the separate Settings opt-in."""
        self.experimental_60_fps = bool(enabled)
        self.settings.setValue("thermalright/experimental_60_fps", self.experimental_60_fps)
        self.desktop_lcd_fps = normalize_lcd_fps(
            self.desktop_lcd_fps, experimental_60=self.experimental_60_fps,
        )
        self.game_lcd_fps = normalize_lcd_fps(
            self.game_lcd_fps, experimental_60=self.experimental_60_fps,
        )
        self._populate_lcd_fps_combo()
        self._populate_game_fps_combo()
        self._apply_fps_policy("Experimentelle Freigabe geändert")

    def _preview_fps_changed(self, _index: int = -1) -> None:
        self.preview_fps = 60 if int(self.preview_fps_combo.currentData() or 30) >= 60 else 30
        self.settings.setValue("thermalright/preview_fps", self.preview_fps)
        self.layer2_motion_timer.setInterval(max(16, round(1000 / self.preview_fps)))

    def _desktop_fps_changed(self, _index: int = -1) -> None:
        self.desktop_lcd_fps = normalize_lcd_fps(
            self.lcd_fps_combo.currentData(), experimental_60=self.experimental_60_fps,
        )
        self.settings.setValue("thermalright/desktop_fps", self.desktop_lcd_fps)
        self.session_fps_limit = None
        self._apply_fps_policy("Desktop-Bildrate geändert")

    def _game_fps_changed(self, _index: int = -1) -> None:
        self.game_lcd_fps = normalize_lcd_fps(
            self.game_fps_combo.currentData(), experimental_60=self.experimental_60_fps,
        )
        self.settings.setValue("thermalright/game_fps", self.game_lcd_fps)
        self.session_fps_limit = None
        self._apply_fps_policy("Spiel-Bildrate geändert")

    def _game_process_list_changed(self) -> None:
        self.game_process_names = normalize_process_names(self.game_process_input.text())
        normalized = ", ".join(self.game_process_names)
        self.game_process_input.setText(normalized)
        self.settings.setValue("thermalright/game_process_names", normalized)
        self._poll_game_activity()

    def _toggle_game_program_manager(self) -> None:
        visible = self.game_program_manager.isHidden()
        if visible:
            self.game_program_manager.ensure_loaded()
        self.game_program_manager.setVisible(visible)
        self.game_program_manager_button.setText(
            "Manager schließen" if visible else "Spiele-Programmliste verwalten …"
        )


    def _game_program_selection_changed(self, names: tuple[str, ...]) -> None:
        self.game_process_input.setText(", ".join(names))
        self._game_process_list_changed()
        self.settings.setValue(
            "thermalright/game_process_paths", "\n".join(self.game_program_manager.paths())
        )


    def _game_policy_changed(self, _checked: bool = False) -> None:
        self.game_auto_detection = self.game_auto_checkbox.isChecked()
        self.game_manual = self.game_manual_checkbox.isChecked()
        self.game_fullscreen_detection = self.game_fullscreen_checkbox.isChecked()
        self.game_borderless_detection = self.game_borderless_checkbox.isChecked()
        self.settings.setValue("thermalright/game_auto_detection", self.game_auto_detection)
        self.settings.setValue("thermalright/game_fullscreen_detection", self.game_fullscreen_detection)
        self.settings.setValue("thermalright/game_borderless_detection", self.game_borderless_detection)
        self._poll_game_activity()

    def _poll_game_activity(self) -> None:
        self.game_activity.poll()

    def _gamemode_status_finished(self, exit_code: int, status: QProcess.ExitStatus) -> None:
        self.game_activity.finished(exit_code, status)

    def _update_game_activity(self, process_signal: bool, process_reason: str) -> None:
        active, reason = resolve_game_activity(GameSignals(
            manual=self.game_manual,
            gamemode=self.game_auto_detection and self.gamemode_active,
            gamescope_or_process=self.game_auto_detection and process_signal,
            process_reason=process_reason,
        ))
        changed = active != self.game_active or reason != self.game_reason
        self.game_active, self.game_reason = active, reason
        if changed:
            self.session_fps_limit = None
        self._apply_fps_policy(f"Spielstatus: {reason}")

    def _wanted_lcd_fps(self) -> int:
        wanted = self.game_lcd_fps if self.game_active else self.desktop_lcd_fps
        return min(wanted, self.session_fps_limit) if self.session_fps_limit else wanted

    def _apply_fps_policy(self, reason: str) -> None:
        wanted = self._wanted_lcd_fps()
        if getattr(self, "stream_delegated", False):
            self.active_lcd_fps = wanted
            self.game_status_label.setText(
                f"{self.game_reason} · LCD-Takt durch TRCC-Daemon · Vorschau {self.preview_fps} FPS"
            )
            return
        self.game_status_label.setText(
            f"{self.game_reason} · LCD-Sollwert {wanted} FPS · Vorschau {self.preview_fps} FPS"
        )
        if wanted == self.active_lcd_fps:
            return
        self.active_lcd_fps = wanted
        if self.stream_process.state() == QProcess.ProcessState.NotRunning or not self.stream_should_run:
            return
        self.stream_stop_requested = True
        self._fps_restart_pending = True
        self.lcd_runtime.stop_started = time.monotonic()
        self.stream_process.terminate()
        self._log(f"LCD-FPS: {reason} · Taktgeber wird ohne Theme-Neuübertragung auf {wanted} FPS gewechselt")

    def _current_motion_pixmap(self) -> QPixmap:
        design = self.current_hardware_design_path()
        if not self._layer2_motion_enabled(design):
            return QPixmap()
        phase = ((time.monotonic() - self.layer2_motion_started) / 6.0) % 1.0
        return QPixmap.fromImage(render_layer2_motion_frame(design.name, phase))

    def _advance_layer2_motion_preview(self) -> None:
        from modules.lcd_media_manager.v1_0.preview_visibility import exposed
        if exposed(self.canvas):
            self.canvas.set_motion_layer(self._current_motion_pixmap())

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
                if design.name in BUILTIN_LEVITA_THEME_NAMES:
                    original = restore_explicit_format_units(original)
                self.layer2_originals[key] = original
                self.layer2_configs[key] = dict(config)
        if key in self.layer2_load_errors:
            return None
        selected = self.layer2_overrides.get(key, self.layer2_originals.get(key))
        if selected is not None and design.name in BUILTIN_LEVITA_THEME_NAMES:
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
        self._sync_layer2_motion_control()

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
        self.gpu_clock_plausible_streak = 0
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
        self.canvas.set_motion_layer(self._current_motion_pixmap())
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
        if hasattr(self, 'media_preview'):
            self.media_preview.refresh()

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
        seed = preview_cache_path("levita-hover", media, cache_budget_mb(self.settings))
        directory = seed.parent if seed is not None else self.cache_dir
        targets = [
            directory / f"hover-{fingerprint}-{number:02d}.jpg"
            for number in range(1, 17)
        ]
        frames = self._fit_hover_preview_frames(
            QPixmap(str(target)) for target in targets if target.is_file()
        )
        if frames:
            return frames
        pattern = directory / f"hover-{fingerprint}-%02d.jpg"
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
        # Hover affects the card only. The main canvas belongs to the selected
        # video's independent visibility-bound decoder.

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
        QTimer.singleShot(900, self, lambda: self._start_queue(
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
            row_count = max(1, (len(self.overlay_specs) + len(columns) - 1) // len(columns))
            spacing = min(90, max(54, 540 // row_count))
            start_y = max(72, 630 - (row_count - 1) * spacing)
            positions = tuple(
                (columns[index % len(columns)], start_y + (index // len(columns)) * spacing)
                for index in range(len(self.overlay_specs))
            )
            size = 38
            message = "Hardware-Infos in zwei sauberen Reihen angeordnet"
        elif layout == "vertical":
            x = max(180, right - 230)
            spacing = min(95, max(42, 600 // max(1, len(self.overlay_specs) - 1)))
            positions = tuple((x, 60 + index * spacing) for index in range(len(self.overlay_specs)))
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
        self._rebuild_overlay_controls()
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
        label = controls.get("label")
        if isinstance(label, QLineEdit) and label.text() != spec.text:
            label.blockSignals(True)
            label.setText(spec.text)
            label.blockSignals(False)
        font_combo = controls.get("font")
        if isinstance(font_combo, QComboBox):
            font_combo.blockSignals(True)
            font_combo.setCurrentIndex(max(0, font_combo.findData(spec.font)))
            font_combo.blockSignals(False)

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
        self._rebuild_overlay_controls()
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
        if self.shutdown_started:
            return
        if hasattr(self, "_lcd_write_allowed") and not self._lcd_write_allowed():
            self._status("LCD-Zuständigkeit liegt nicht bei OHC · keine Übertragung gestartet", error=True)
            return
        if not startup:
            self.design_state.invalidate_startup()
            self.startup_apply_requested = True
            self.startup_apply_active = False
            autostart_control = getattr(self, "autostart_enabled", None)
            self.remember_design_after_apply = bool(
                autostart_control is not None and autostart_control.isChecked()
            )
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
            layer1_source = prepared.path
            motion_warning = ""
            if hardware_design is not None and self._layer2_motion_enabled(hardware_design):
                composed = compose_motion_video(
                    layer1_source,
                    hardware_design / "motion.mp4",
                    self.cache_dir / "layer2-motion",
                    fps=self._wanted_lcd_fps(),
                )
                layer1_source = composed.path
                motion_warning = composed.warning
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
            apply_media = layer1_source
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
                same_theme = layer1_source.resolve() == hardware_design.resolve()
                background_image: Path | None = None
                background_video: Path | None = None
                if not same_theme and layer1_source.is_file():
                    if layer1_source.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES:
                        background_image = layer1_source
                    else:
                        background_video = layer1_source
                elif not same_theme and layer1_source.is_dir():
                    candidate = layer1_source / "00.png"
                    if candidate.is_file():
                        background_image = candidate
                    else:
                        background_video = next((
                            layer1_source / name for name in (
                                "Theme.zt", "Theme.mp4", "Theme.mov", "Theme.webm",
                                "Theme.mkv", "Theme.avi",
                            ) if (layer1_source / name).is_file()
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
            elif any(
                item.visible and (item.kind == "text" or bool(item.font))
                for item in self.overlay_specs
            ):
                # A native cache theme is the only public TRCC path that
                # currently carries per-element font families.  It also keeps
                # all custom text and live metrics in one atomic composition.
                apply_hardware_design = stage_custom_overlay_theme(
                    prepared.path,
                    self.cache_dir / "custom-overlay-themes",
                    self.overlay_specs,
                    mask_path=mask_path,
                    safe_right_x=self._safe_right_x(),
                )
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
        self.pending_apply_warning = " · ".join(
            warning for warning in (prepared.warning, motion_warning) if warning
        )
        self.pending_apply_sequence = list(sequence)
        self.pending_apply_animated = self._media_is_animated(apply_hardware_design or apply_media)
        self.design_state.capture(sequence, self.pending_apply_animated,
                                  hardware=hardware_design is not None,
                                  layout=self._current_layer2_layout())
        if hasattr(self, 'media_preview'): self.media_preview.capture()
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
            if getattr(self, "ubuntu_runtime", False) and self._stop_for_usb_owner_conflict(output):
                return
            self.remember_design_after_apply = False
            detail = (
                backend_failure_detail(output) if getattr(self, "ubuntu_runtime", False)
                else output.strip().splitlines()[-1] if output.strip() else ""
            ) or "unbekannter Backendfehler"
            timeout = "timed out" in output.casefold() or "errno 110" in output.casefold()
            backend_crash = "trcc-prozess ist abgestürzt" in output.casefold()
            if is_probable_daemon_failure(output) and self._request_daemon_restart(
                "Levita-USB-Schnittstelle oder TRCC-Daemon ist festgefahren"
            ):
                self.pending_apply_sequence = []
                self.apply_retry_remaining = 0
                return
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

    def _stop_for_usb_owner_conflict(self, output: str) -> bool:
        """Stop only OHC retries when another program holds the USB interface.

        Keep the saved startup selection and immutable request. Once that
        owner has been released, an explicit Apply uses the existing queue;
        no polling, process signalling or new USB path is introduced here.
        """

        if not getattr(self, "ubuntu_runtime", False) or not is_usb_owner_conflict(output):
            return False
        self.remember_design_after_apply = False
        self.pending_apply_sequence = []
        self.apply_retry_remaining = 0
        self.apply_start_timer.stop()
        self.apply_cooldown_timer.stop()
        self._stop_stream_client()
        # A freshly spawned TRCC daemon can claim the USB interface before
        # the next short-lived CLI process has completed its IPC hand-off.
        # The backend then reports the same "another process" text used for a
        # genuinely foreign owner.  Recover automatically only when the
        # currently observed process is the exact daemon registered by this
        # OHC session.  PID, command and UID are revalidated immediately; an
        # untracked/preexisting daemon remains strictly untouched.
        sample = find_trcc_daemon_memory()
        owned_pid = getattr(self, "owned_trcc_daemon_pid", None)
        owns_conflict = bool(
            getattr(self, "preexisting_trcc_daemon_pid", None) is None
            and owned_pid is not None
            and sample is not None
            and sample.pid == owned_pid
            and is_owned_trcc_daemon_pid(owned_pid) is True
        )
        if owns_conflict:
            reason = (
                "Eigener TRCC-Daemon hat die Levita-Schnittstelle beim Start "
                "nicht sauber an den IPC-Betrieb übergeben"
            )
            if self._request_daemon_restart(
                reason,
                cooldown_seconds=PLAYBACK_RECOVERY_COOLDOWN_SECONDS,
            ):
                self._log(
                    f"Levita-USB-Konflikt gehört zum registrierten OHC-Daemon PID {owned_pid} · "
                    "ein kontrollierter Neustart wird einmal automatisch ausgeführt"
                )
                return True
            self.startup_apply_active = False
            translate = getattr(self.window(), "tr_static", lambda text: text)
            message = translate(
                "Eigener Levita-Daemon ist erneut blockiert · automatische Reparatur ist bereits ausgeschöpft; "
                "Display freigeben manuell ausführen"
            )
            if hasattr(self, "playback_health_status"):
                self.playback_health_status.setText(message)
            self._status(message, error=True)
            return True

        self.startup_apply_active = False
        translate = getattr(self.window(), "tr_static", lambda text: text)
        message = translate(
            "Levita-Display ist durch ein anderes Programm belegt · keine automatische Freigabe; "
            "das andere Programm schließen und das Design erneut anwenden"
        )
        if hasattr(self, "playback_health_status"):
            self.playback_health_status.setText(message)
        self._status(message, error=True)
        return True

    def _daemon_stream_started(self) -> None:
        """Confirm the theme and start a daemon-safe video ticker if needed."""

        if hasattr(self, 'media_preview'):
            self.media_preview.confirm()

        if getattr(self, "remember_design_after_apply", False):
            media = self.current_media_path()
            if media is not None:
                self._remember_startup_media(media, enable=False)
        self.remember_design_after_apply = False
        if hasattr(self, "playback_recovery_policy"):
            self.playback_recovery_policy.consecutive_failures = 0
        if hasattr(self, "playback_health_status"):
            self.playback_health_status.setText("Design übertragen · Wiedergabeprüfung folgt automatisch")

        animated = self.pending_apply_animated
        request = getattr(getattr(self, "design_state", None), "desired", None)
        self.hardware_design_active = request.hardware if request else self.current_hardware_design_path() is not None
        if not getattr(self, "hardware_io_disabled", False) and not self.firmware_guard.arm(self.cli.executable):
            self._log(
                "Levita-Absturzwächter konnte nicht gestartet werden · "
                "kontrolliertes Programmende bleibt geschützt"
            )
        self.stream_animated = animated
        if (
            not getattr(self, "hardware_io_disabled", False)
            and not self.test_mode.isChecked()
            and not self.shutdown_started
        ):
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
        request = getattr(getattr(self, "design_state", None), "desired", None)
        if self.hardware_design_active and request is not None:
            return request.gpu_clock_block
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
            self.gpu_clock_plausible_streak = 0
            return
        reading = read_primary_amd_gpu_clock()
        boundary_issue = "TRCC-9.9.11-Grenzfall" in reading.issue
        if boundary_issue and reading.mhz is not None:
            self.gpu_clock_plausible_streak = 0
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
        # The AMD graphics engine can cross the exact 1 MHz idle boundary for
        # only one or two 5-second samples.  Keep the corrected value stable
        # until three consecutive, genuinely plausible samples prove that the
        # dynamic TRCC source is safe again.  Missing/malformed readings never
        # count as recovery evidence.
        self.gpu_clock_plausible_streak, recovered = advance_gpu_clock_recovery_streak(
            self.gpu_clock_plausible_streak, reading,
        )
        if not recovered:
            return
        command = self.cli.overlay_update_format_args(
            block.ident, block.format, show_unit=True,
        )

        def restored(ok: bool, _output: str) -> None:
            if not ok:
                return
            self.gpu_clock_guard_state = ""
            self.gpu_clock_plausible_streak = 0
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
        if not self._lcd_write_allowed():
            self._status("LCD-Zuständigkeit liegt nicht bei OHC · kein Display-Test gestartet", error=True)
            return
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
        if ok and not getattr(self, "hardware_io_disabled", False):
            self.firmware_guard.arm(self.cli.executable)
        self._status("Display-Farbtest abgeschlossen" if ok else f"Display-Farbtest fehlgeschlagen: {output.strip()}", error=not ok)

    def stop_display(self) -> None:
        self.test_timer.stop()
        self.pending_apply_animated = False
        self.hardware_design_active = False
        self.gpu_clock_guard_state = ""
        self.gpu_clock_plausible_streak = 0
        self._stop_stream_client()
        if self.test_mode.isChecked() or not self.cli.available:
            self.update_preview()
            self._status("Test-/Vorschaumodus angehalten")
            return
        self._start_queue([(self.cli.stop_video_args(), True)], lambda _ok, _out: self._status("Thermalright-Übertragung angehalten"))

    def restore_firmware_display(self, _checked: bool = False) -> None:
        """Release the sole TRCC owner so the cooler firmware redraws its original screen."""
        self.test_timer.stop()
        self.apply_start_timer.stop()
        self.apply_cooldown_timer.stop()
        self.pending_apply_sequence = []
        self.pending_apply_animated = False
        self.hardware_design_active = False
        self._stop_stream_client()
        if self.test_mode.isChecked():
            self.update_preview()
            self._status("Testmodus: Originalanzeige nicht gesendet · keine USB-Daten übertragen")
            return
        self.refresh_backend_status()
        if not self.cli.available:
            self._status("Thermalright-Originalanzeige benötigt das TRCC-Linux-Backend", error=True)
            return
        if self.command_process.state() != QProcess.ProcessState.NotRunning or self.command_step_timer.isActive():
            self._status("Originalanzeige wartet · eine andere Levita-Übertragung läuft noch", error=True)
            return
        self.restore_firmware_button.setEnabled(False)

        def restored(ok: bool, output: str) -> None:
            self.restore_firmware_button.setEnabled(True)
            if ok or "not attached" in output.casefold():
                self.media_preview.release()
                self.firmware_guard.finish(restored=True)
                self._status(
                    "Levita an die Thermalright-Firmware zurückgegeben · Originalanzeige erscheint nach dem Firmware-Zeitlimit"
                )
            else:
                detail = output.strip().splitlines()[-1] if output.strip() else "unbekannter TRCC-Fehler"
                self._status(f"Thermalright-Originalanzeige konnte nicht wiederhergestellt werden: {detail}", error=True)

        self._start_queue([(self.cli.disconnect_args(), False)], restored)
        self._status("OHC-Übertragung wird beendet · Thermalright-Originalanzeige wird wiederhergestellt …")

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
        self.stream_restart_timer.stop()
        self.stream_restart_policy.reset()
        self.stream_should_run = True
        self.stream_delegated = False
        self.stream_stop_requested = False
        self.active_lcd_fps = self._wanted_lcd_fps()
        self._launch_stream_client()

    def _launch_stream_client(self) -> None:
        if (
            getattr(self, "hardware_io_disabled", False)
            or self.shutdown_started
            or self.test_mode.isChecked()
            or not self.stream_should_run
        ):
            return
        if self.stream_process.state() != QProcess.ProcessState.NotRunning:
            return
        self.stream_output_tail = ""
        self.stream_started_at = 0.0
        self.lcd_runtime.stream_launch()
        args = self.cli.play_args(1.0 / max(1, self.active_lcd_fps))
        self.stream_process.start(args[0], list(args[1:]))

    def _restart_stream_client(self) -> None:
        if not self.stream_should_run or self.shutdown_started:
            return
        self._launch_stream_client()

    def _stop_stream_client(self) -> None:
        self.stream_should_run = False
        self.stream_delegated = False
        self._fps_restart_pending = False
        self.stream_restart_timer.stop()
        self.stream_restart_policy.reset()
        if self.stream_process.state() == QProcess.ProcessState.NotRunning:
            return
        self.stream_stop_requested = True
        self.stream_process.terminate()
        if not self.stream_process.waitForFinished(750):
            self.stream_process.kill()
            self.stream_process.waitForFinished(500)

    def _on_stream_finished(self, exit_code: int, status: QProcess.ExitStatus) -> None:
        self._capture_stream_output()
        requested = self.stream_stop_requested
        delegated = bool(
            not requested
            and exit_code == 0
            and status == QProcess.ExitStatus.NormalExit
            and daemon_owns_playback(self.stream_output_tail)
        )
        self.lcd_runtime.stream_done(exit_code, status, requested, delegated)
        self.stream_stop_requested = False
        if requested and getattr(self, "_fps_restart_pending", False) and self.stream_should_run:
            self._fps_restart_pending = False
            QTimer.singleShot(100, self, self._launch_stream_client)
            return
        if requested or not self.stream_should_run:
            return
        if delegated:
            self.stream_delegated = True
            self._fps_restart_pending = False
            self.stream_restart_timer.stop()
            self.stream_restart_policy.reset()
            self._status(
                "Levita-Dauerbetrieb aktiv · TRCC-Daemon übernimmt Video- und Sensor-Takt"
            )
            self.game_status_label.setText(
                f"{self.game_reason} · LCD-Takt durch TRCC-Daemon · Vorschau {self.preview_fps} FPS"
            )
            return
        if getattr(self, "ubuntu_runtime", False) and self._stop_for_usb_owner_conflict(self.stream_output_tail):
            return
        if self.stream_restart_timer.isActive():
            return
        runtime = time.monotonic() - self.stream_started_at if self.stream_started_at else 0.0
        if (self.lcd_runtime.stream_reason or is_probable_daemon_failure(self.stream_output_tail)) and self._request_daemon_restart(
            self.lcd_runtime.stream_reason or "Levita-Taktgeber hat die Verbindung zum TRCC-Daemon verloren"
        ):
            return
        reduced = fallback_lcd_fps(self.active_lcd_fps)
        if reduced < self.active_lcd_fps:
            failed = self.active_lcd_fps
            self.session_fps_limit = reduced
            self.active_lcd_fps = reduced
            self._status(
                f"Levita-Taktgeber bei {failed} FPS beendet · automatische Rückstufung auf {reduced} FPS",
                error=True,
            )
            self.game_status_label.setText(
                f"{self.game_reason} · LCD-Sollwert {reduced} FPS · automatisch von {failed} FPS zurückgestuft"
            )
            from modules.process_runtime.v1_1.diagnostics import record
            record("lcd-ticker", "retry", reason="fps-fallback", retry_ms=1000, fps=reduced)
            self.stream_restart_timer.start(1000)
            return
        confirmed_runtime = max(0.0, self.lcd_runtime.progress.last_sent - self.lcd_runtime.progress.started) if self.lcd_runtime.progress.frames else 0.0
        delay_ms = self.stream_restart_policy.next_delay_ms(confirmed_runtime)
        detail = f" · Backend: {self.stream_output_tail}" if self.stream_output_tail else ""
        if delay_ms is None:
            from modules.process_runtime.v1_1.diagnostics import record
            record("lcd-ticker", "exhausted", reason="three automatic ticker restarts exhausted")
            self.stream_should_run = False
            self._status(
                "Levita-Video-Taktgeber wiederholt beendet · automatische Wiederanläufe "
                f"ausgeschöpft · Design bleibt als Standbild sichtbar{detail}",
                error=True,
            )
            return
        self._status(
            "Levita-Video-Taktgeber unerwartet beendet "
            f"(Code {exit_code}) · Wiederanlauf "
            f"{self.stream_restart_policy.attempts}/{self.stream_restart_policy.max_attempts} "
            f"in {delay_ms / 1000:g} s{detail}",
            error=True,
        )
        from modules.process_runtime.v1_1.diagnostics import record
        record("lcd-ticker", "retry", retry_ms=delay_ms, attempt=self.stream_restart_policy.attempts)
        self.stream_restart_timer.start(delay_ms)









    def _poll_firmware_guard_health(self) -> None:
        """Recover quickly if the independent crash guard ever disappears."""

        if (
            getattr(self, "hardware_io_disabled", False)
            or self.shutdown_started
            or self.daemon_restart_in_progress
            or not self.stream_should_run
            or self.test_mode.isChecked()
            or self.firmware_guard.armed
        ):
            return
        reason = (
            "Levita-Absturzwächter wurde unerwartet beendet; eine ungewollte "
            "Display-Freigabe wird vorsorglich repariert"
        )
        self._log(f"Levita-Wiedergabeprüfung: {reason}")
        from modules.process_runtime.v1_1.diagnostics import record
        record("lcd-firmware-guard", "unexpected-exit", reason=reason)
        if not self.firmware_guard.arm(self.cli.executable):
            self._status(
                "Levita-Absturzwächter konnte nicht neu gestartet werden · "
                "Display bitte erneut anwenden",
                error=True,
            )
            return
        self.last_daemon_recovery_at = float("-inf")
        self._request_daemon_restart(reason)


    def _playback_health_finished(self, ok: bool, output: str) -> None:
        """Confirm actual daemon playback and recover only after two failures."""

        self.playback_health_probe_active = False
        if not ok and getattr(self, "ubuntu_runtime", False) and self._stop_for_usb_owner_conflict(output):
            return
        if ok and self.stream_animated:
            health = parse_video_playback_status(output, THERMALRIGHT_DEVICE_KEY)
        else:
            health = parse_playback_status(output, THERMALRIGHT_DEVICE_KEY) if ok else None
        if health is not None and health.healthy:
            self.playback_recovery_policy.observe(health)
            self.playback_last_confirmed_at = time.time()
            checked = time.strftime("%H:%M:%S", time.localtime(self.playback_last_confirmed_at))
            self.playback_health_status.setText(
                f"Wiedergabe aktiv · zuletzt geprüft {checked} · automatische Wiederherstellungen "
                f"{self.playback_recovery_policy.recovery_attempts}/"
                f"{self.playback_recovery_policy.max_recovery_attempts}"
            )
            return

        reason = health.reason if health is not None else (
            output.strip().splitlines()[-1] if output.strip() else "TRCC-Statusabfrage fehlgeschlagen"
        )
        sample = find_trcc_daemon_memory()
        daemon_detail = (
            f"PID={sample.pid} · RSS={sample.rss_bytes // (1024 * 1024)} MiB"
            if sample is not None else "kein TRCC-Daemon in /proc gefunden"
        )
        confirmed_detail = (
            f"letzte Bestätigung vor {max(0, round(time.time() - self.playback_last_confirmed_at))} s"
            if self.playback_last_confirmed_at > 0 else "in dieser Sitzung noch nicht bestätigt"
        )
        trcc_cause = recent_trcc_cause(
            Path.home() / ".trcc" / "trcc.log",
            since_epoch=self.playback_last_confirmed_at,
        )
        from modules.process_runtime.v1_1.diagnostics import record
        record(
            "lcd-playback",
            "unhealthy",
            reason=reason,
            consecutive_failures=self.playback_recovery_policy.consecutive_failures + 1,
        )
        self._log(
            f"Levita-Wiedergabeprüfung: {reason} · {daemon_detail} · {confirmed_detail} · "
            f"TRCC-Ursachenspur={trcc_cause}"
        )
        unhealthy = health or PlaybackHealth(False, reason)
        should_recover = self.playback_recovery_policy.observe(unhealthy)
        if should_recover:
            attempt = self.playback_recovery_policy.recovery_attempts
            started = self._request_playback_reapply(
                f"Levita-Wiedergabe wurde nicht mehr bestätigt: {reason}"
            )
            if started:
                self.playback_health_status.setText(
                    f"Wiedergabe unterbrochen · automatische Wiederherstellung {attempt}/"
                    f"{self.playback_recovery_policy.max_recovery_attempts} läuft"
                )
                return
            self.playback_recovery_policy.defer_recovery()
            self.playback_health_status.setText(
                "Wiedergabe unterbrochen · Wiederherstellung kurz zurückgestellt · "
                "erneute Prüfung folgt in 5 Sekunden"
            )
            QTimer.singleShot(5000, self, self._poll_trcc_daemon_health)
            return
        if self.playback_recovery_policy.recovery_attempts >= self.playback_recovery_policy.max_recovery_attempts:
            self.playback_health_status.setText(
                "Wiedergabe nicht bestätigt · automatische Wiederherstellungen ausgeschöpft · "
                "über ‚Display freigeben‘ kann ein neuer Versuch gestartet werden"
            )
            return
        self.playback_health_status.setText(
            "Wiedergabe nicht bestätigt · zweite Prüfung folgt in 5 Sekunden"
        )
        QTimer.singleShot(5000, self, self._poll_trcc_daemon_health)


    def _request_playback_reapply(self, reason: str) -> bool:
        """Restore the accepted design without discarding a healthy daemon.

        A missing TRCC playback object is not proof that the daemon itself is
        dead.  Killing it on every video loss throws away the most useful
        diagnostic state and lengthens the black-screen interval.  The saved
        immutable design sequence already starts with a bounded reconnect, so
        replaying that sequence is the narrow repair.  Its existing failure
        path escalates to the full daemon restart when IPC or USB is genuinely
        wedged.
        """

        now = time.monotonic()
        if self.shutdown_started or self.daemon_restart_in_progress:
            return False
        remaining = max(
            0.0,
            PLAYBACK_RECOVERY_COOLDOWN_SECONDS - (now - self.last_playback_reapply_at),
        )
        if remaining > 0:
            self._log(
                f"Levita-Wiedergabe-Neuübertragung zurückgestellt · Schutzzeit noch "
                f"{remaining:.1f} s · Grund={reason}"
            )
            return False
        self.last_playback_reapply_at = now
        self._stop_stream_client()
        self.next_hardware_apply_at = 0.0
        from modules.process_runtime.v1_1.diagnostics import record
        sample = find_trcc_daemon_memory()
        record(
            "lcd-playback",
            "reapply",
            reason=reason,
            pid=sample.pid if sample is not None else None,
            rss_bytes=sample.rss_bytes if sample is not None else None,
            retry_ms=0,
        )
        self._status(
            f"{reason} · aktives Design wird gezielt neu übertragen; "
            "der TRCC-Daemon bleibt für die Diagnose erhalten …",
            error=True,
        )
        if self.design_state.recover(self):
            return True
        # This is only possible before the first accepted design.  Keep the
        # old hard recovery as the bounded fallback for that exceptional path.
        return self._request_daemon_restart(
            reason,
            cooldown_seconds=PLAYBACK_RECOVERY_COOLDOWN_SECONDS,
        )


    def _poll_trcc_daemon_health(self) -> None:
        if (
            self.shutdown_started
            or self.daemon_restart_in_progress
            or not self.stream_should_run
            or self.test_mode.isChecked()
            or self.pending_apply_sequence
            or self.command_process.state() != QProcess.ProcessState.NotRunning
            or self.command_step_timer.isActive()
            or self.playback_health_probe_active
        ):
            return
        from modules.lcd_runtime.v1_1.memory_guard import available_memory
        sample = find_trcc_daemon_memory()
        memory_reason = self.daemon_memory_guard.reason(sample, available_memory())
        if memory_reason:
            from modules.process_runtime.v1_1.diagnostics import record
            record("lcd-daemon", "memory-limit", pid=sample.pid, rss_bytes=sample.rss_bytes,
                   baseline_bytes=self.daemon_memory_guard.baseline, reason=memory_reason)
            used_mib = sample.rss_bytes // (1024 * 1024) if sample is not None else 0
            self._request_daemon_restart(
                f"TRCC-Daemon belegt {used_mib} MiB Arbeitsspeicher und erreicht die Sicherheitsgrenze"
            )
            return
        if not self.cli.available:
            return
        self.playback_health_probe_active = True
        health_args = (
            self.cli.video_status_args()
            if self.stream_animated
            else self.cli.status_args()
        )
        self._start_queue(
            [(health_args, False)],
            self._playback_health_finished,
        )







    def _request_daemon_restart(
        self,
        reason: str,
        *,
        cooldown_seconds: float = DAEMON_RECOVERY_COOLDOWN_SECONDS,
    ) -> bool:
        now = time.monotonic()
        if self.shutdown_started:
            self._log(f"Levita-Wiederherstellung verworfen · Programm wird beendet · Grund={reason}")
            return False
        if self.daemon_restart_in_progress:
            self._log(f"Levita-Wiederherstellung zurückgestellt · Neustart läuft bereits · Grund={reason}")
            return False
        remaining = max(0.0, float(cooldown_seconds) - (now - self.last_daemon_recovery_at))
        if remaining > 0:
            self._log(
                f"Levita-Wiederherstellung zurückgestellt · Schutzzeit noch {remaining:.1f} s · "
                f"Grund={reason}"
            )
            return False
        self.last_daemon_recovery_at = now
        self.daemon_restart_in_progress = True
        self.awaiting_owned_trcc_replacement = bool(
            self.preexisting_trcc_daemon_pid is None
            and self.owned_trcc_daemon_pid is not None
        )
        self._stop_stream_client()
        self._status(
            f"{reason} · kontrollierter Neustart und erneute Designübertragung laufen …",
            error=True,
        )
        from modules.process_runtime.v1_1.diagnostics import record
        record("lcd-daemon", "retry", reason=reason, retry_ms=0)
        self.daemon_restart_timer.start(0)
        return True

    def force_recover_display(self, _checked: bool = False) -> None:
        """Hard-release only OHC workers and an exact same-user TRCC daemon."""

        if getattr(self, "hardware_io_disabled", False) or self.shutdown_started:
            return
        self.force_recovery_button.setEnabled(False)
        self.playback_recovery_policy = PlaybackRecoveryPolicy()
        self.last_daemon_recovery_at = float("-inf")
        self.daemon_restart_in_progress = True
        self.awaiting_owned_trcc_replacement = bool(
            self.preexisting_trcc_daemon_pid is None
            and self.owned_trcc_daemon_pid is not None
        )
        self.pending_apply_sequence = []
        self.apply_retry_remaining = 0
        self.apply_start_timer.stop()
        self.apply_cooldown_timer.stop()
        self.command_step_timer.stop()
        self.command_queue.clear()
        self.queue_done = None
        self._stop_stream_client()
        if self.command_process.state() != QProcess.ProcessState.NotRunning:
            self.command_process.kill()
            self.command_process.waitForFinished(500)
        sample = find_trcc_daemon_memory()
        if sample is not None and signal_trcc_daemon(sample.pid, signal.SIGTERM):
            self._status(
                "Eigener TRCC-Daemon wird freigegeben · falls nötig folgt ein begrenztes hartes Beenden …",
                error=True,
            )
            QTimer.singleShot(1200, self, lambda pid=sample.pid: self._finish_hard_daemon_recovery(pid))
            return
        self._status("Kein eigener festgefahrener TRCC-Daemon gefunden · Design wird neu verbunden")
        QTimer.singleShot(500, self, self._resume_after_daemon_restart)

    def _finish_hard_daemon_recovery(self, pid: int) -> None:
        if getattr(self, "hardware_io_disabled", False):
            return
        sample = find_trcc_daemon_memory()
        if sample is not None and sample.pid == int(pid):
            signal_trcc_daemon(sample.pid, signal.SIGKILL)
        QTimer.singleShot(500, self, self._resume_after_daemon_restart)

    def _perform_daemon_restart(self) -> None:
        if self.shutdown_started or not self.daemon_restart_in_progress:
            return
        if self.command_process.state() != QProcess.ProcessState.NotRunning or self.command_step_timer.isActive():
            self.daemon_restart_timer.start(1000)
            return
        self.refresh_backend_status()
        if not self.cli.available:
            self.daemon_restart_in_progress = False
            self._status(
                "TRCC-Daemon konnte nicht neu gestartet werden · Backend ist nicht verfügbar",
                error=True,
            )
            return
        # ``trcc kill`` closes the daemon through its IPC endpoint. The
        # following apply starts a fresh daemon and reconstructs the selected
        # design, without a second process touching the USB endpoints.
        self._start_queue([(self.cli.daemon_kill_args(), False)], self._daemon_restart_finished)

    def _daemon_restart_finished(self, ok: bool, _output: str) -> None:
        if self.shutdown_started:
            self.daemon_restart_in_progress = False
            return
        if not ok:
            sample = find_trcc_daemon_memory()
            if sample is not None and signal_trcc_daemon(sample.pid, signal.SIGTERM):
                self._status(
                    "TRCC-IPC reagiert nicht · eigener Daemon wird kontrolliert freigegeben …",
                    error=True,
                )
                QTimer.singleShot(1200, self, lambda pid=sample.pid: self._finish_hard_daemon_recovery(pid))
                return
        QTimer.singleShot(1200, self, self._resume_after_daemon_restart)

    def _resume_after_daemon_restart(self) -> None:
        if self.shutdown_started:
            self.daemon_restart_in_progress = False
            return
        self.daemon_restart_in_progress = False
        if hasattr(self, "force_recovery_button"):
            self.force_recovery_button.setEnabled(True)
        self.next_hardware_apply_at = 0.0
        self._status("TRCC-Daemon wurde freigegeben · ausgewähltes Levita-Design wird wiederhergestellt")
        if not self.design_state.recover(self) and self.design_state.desired is None:
            # Only explicit force-recovery can precede the first accepted design.
            self.apply_design()

    def _on_stream_started(self) -> None:
        if not self.stream_should_run:
            return
        self.stream_started_at = time.monotonic()
        self.lcd_runtime.stream_did_start()
        self.game_status_label.setText(
            f"{self.game_reason} · LCD-Taktgeber {self.active_lcd_fps} FPS · Vorschau {self.preview_fps} FPS"
        )

    def _on_stream_progress(self) -> None:
        if not getattr(self, "stream_animated", True):
            self._status("Levita-Dauerbetrieb aktiv · statisches Design wird regelmäßig übertragen")
        elif self.current_hardware_design_path() is not None:
            self._status(
                "Levita-Video läuft · Hintergrund, Ebene-2-Grafik und Notch-Maske sind aktiv"
            )
        else:
            self._status("Levita-Hintergrundvideo läuft über den TRCC-Daemon")

    def _on_stream_error(self, error: QProcess.ProcessError) -> None:
        if self.stream_should_run and error == QProcess.ProcessError.FailedToStart:
            if not self.stream_restart_timer.isActive():
                self._on_stream_finished(-1, QProcess.ExitStatus.CrashExit)

    def _capture_stream_output(self) -> None:
        stdout = bytes(self.stream_process.readAllStandardOutput()).decode("utf-8", "replace")
        stderr = bytes(self.stream_process.readAllStandardError()).decode("utf-8", "replace")
        first = self.lcd_runtime.progress.frames == 0
        if self.lcd_runtime.progress.feed(stdout, time.monotonic()) and first and self.stream_should_run:
            self._on_stream_progress()
        # Keep warnings/startup/errors, never continuous successful-frame chatter.
        from modules.lcd_runtime.v1_1.progress import SENT
        lines = [line for line in stdout.splitlines() if not SENT.match(line)]
        text = " ".join(lines) + " " + stderr
        if text.strip():
            combined = f"{self.stream_output_tail} {redact_private_text(text)}".strip()
            self.stream_output_tail = " ".join(combined.split())[-1200:]

    def _start_queue(
        self,
        commands: Iterable[tuple[tuple[str, ...], bool]],
        done: Callable[[bool, str], None],
    ) -> None:
        if getattr(self, "hardware_io_disabled", False):
            done(False, "Hardware-I/O ist für diesen Prüf- oder Vorschaulauf deaktiviert")
            return
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
        self.lcd_runtime.command_launch(args)
        self.command_process.start(args[0], list(args[1:]))

    def _on_command_finished(self, exit_code: int, status: QProcess.ExitStatus) -> None:
        stdout = bytes(self.command_process.readAllStandardOutput()).decode("utf-8", errors="replace")
        stderr = bytes(self.command_process.readAllStandardError()).decode("utf-8", errors="replace")
        output = (stdout + "\n" + stderr).strip()
        failed = self.lcd_runtime.command_done(exit_code, status, output)
        if self.shutdown_started:
            return
        if self.preexisting_trcc_daemon_pid is None:
            observed_daemon = find_trcc_daemon_memory()
            event = ""
            previous_pid = self.owned_trcc_daemon_pid
            if previous_pid is None and observed_daemon is not None:
                self.owned_trcc_daemon_pid = observed_daemon.pid
                event = "owned-trcc-start"
            elif self.awaiting_owned_trcc_replacement:
                replacement = replacement_owned_trcc_pid(previous_pid, observed_daemon)
                if replacement is not None:
                    self.owned_trcc_daemon_pid = replacement
                    self.awaiting_owned_trcc_replacement = False
                    event = "owned-trcc-replaced"
                    self._log(
                        f"TRCC-Daemon-Neustart übernommen · PID {previous_pid} → {replacement}"
                    )
            if event and self.owned_trcc_daemon_pid is not None:
                from modules.application_shutdown.v1_1.journal import record
                from modules.application_shutdown.v1_1.watcher import identity
                current = identity(self.owned_trcc_daemon_pid)
                if current is not None:
                    record(
                        event,
                        child_pid=self.owned_trcc_daemon_pid,
                        previous_child_pid=previous_pid,
                        starttime=current[0],
                    )
        if self.lcd_runtime.command_reason:
            output += "\n" + self.lcd_runtime.command_reason
        if output:
            self.command_outputs.append(output)
        if status == QProcess.ExitStatus.CrashExit:
            self.command_outputs.append(
                "TRCC-Prozess ist abgestürzt (externer Backend-/libusb-Fehler)"
            )
        if failed and (self.lcd_runtime.command_reason or status == QProcess.ExitStatus.CrashExit or not self.current_tolerates_failure):
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
        """Stop workers and release Levita to its built-in firmware logo."""
        if self.shutdown_started:
            return
        self.shutdown_started = True
        self.shutdown_errors = []
        self.media_preview.shutdown()
        self.lcd_runtime.shutdown()
        self.game_activity.shutdown()
        self.gallery_preparation.shutdown()
        self.test_timer.stop()
        self.gpu_clock_guard_timer.stop()
        self.game_detection_timer.stop()
        self.daemon_health_timer.stop()
        self.firmware_guard_timer.stop()
        self.daemon_restart_timer.stop()
        self.layer2_motion_timer.stop()
        self.apply_start_timer.stop()
        self.apply_cooldown_timer.stop()
        self.command_step_timer.stop()
        self.hover_preview_timer.stop()
        self.hover_preview_debounce.stop()
        self.hover_extract_timeout.stop()
        self.pending_apply_animated = False
        self._stop_stream_client()
        if self.gamemode_process.state() != QProcess.ProcessState.NotRunning:
            self.gamemode_process.kill()
            self.gamemode_process.waitForFinished(300)
        if self.hover_extract_process.state() != QProcess.ProcessState.NotRunning:
            self.hover_extract_process.terminate()
            if not self.hover_extract_process.waitForFinished(500):
                self.hover_extract_process.kill()
                self.hover_extract_process.waitForFinished(500)
        self.thumbnail_shutting_down = True
        self.thumbnail_queue.clear()
        self.thumbnail_queued.clear()
        self.thumbnail_paused_workers.clear()
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
        restored = not self.firmware_guard.armed and self.test_mode.isChecked()
        if (
            not getattr(self, "hardware_io_disabled", False)
            and self.cli.available
            and (self.firmware_guard.armed or not self.test_mode.isChecked())
        ):
            result = restore_firmware_logo(self.cli.executable or "", timeout=2.0)
            restored = result.ok
            if result.ok:
                self._log(
                    "Programmende: Levita aus TRCC freigegeben · "
                    "Thermalright-Standardbild kehrt nach dem Firmware-Zeitlimit zurück"
                )
            else:
                detail = result.message or "unbekannter TRCC-Fehler"
                self._log(f"Programmende: Levita-Firmware-Rückgabe fehlgeschlagen: {detail}")
                self.shutdown_errors.append("firmware restore: " + detail)
        self.firmware_guard.finish(restored=restored)
        if not getattr(self, "hardware_io_disabled", False) and self.owned_trcc_daemon_pid is not None:
            stopped = stop_owned_daemon(self.cli.executable or "", self.owned_trcc_daemon_pid)
            if stopped.ok:
                if "replacement left untouched" in stopped.message:
                    self._log("Programmende: ursprünglicher OHC-TRCC-Daemon bereits beendet · andere TRCC-Instanz unangetastet")
                else:
                    self._log("Programmende: von OHC gestarteter TRCC-Daemon beendet")
                from modules.application_shutdown.v1_1.journal import record
                record("owned-trcc-stopped", child_pid=self.owned_trcc_daemon_pid)
            else:
                self._log(f"Programmende: TRCC-Daemon konnte nicht beendet werden: {stopped.message}")
                self.shutdown_errors.append("TRCC daemon: " + stopped.message)

    def verify_shutdown_result(self) -> None:
        failures = getattr(self, "shutdown_errors", ())
        if failures:
            raise RuntimeError("; ".join(failures))
