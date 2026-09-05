"""Native Open Hardware Control surface for Wallpaper Engine for KDE."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QProcess, QSettings, QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .library import (
    WallpaperEntry,
    is_unsafe_video_folder,
    previous_workshop_entry,
    scan_video_folder,
    scan_workshop_library,
)
from .onboarding import WallpaperEngineOnboarding
from .plasma import (
    DEFAULT_DISPLAY_MODE,
    DISPLAY_MODES,
    OPTIMIZED_PROFILE,
    STOCK_PROFILE,
    build_display_mode_script,
    build_profile_script,
    build_select_script,
    build_video_folder_script,
    original_settings_command,
    normalize_display_mode,
    playback_command,
    plasma_config_path,
    plasma_script_command,
    plugin_installed,
    preferred_steam_library,
    read_plasma_wallpaper_states,
)


KIND_LABELS = {
    "scene": "Szene",
    "video": "Video",
    "web": "Web",
    "application": "Anwendung",
    "preset": "Voreinstellung",
}
GALLERY_ICON_SIZE = QSize(192, 108)
GALLERY_GRID_SIZE = QSize(224, 154)


class WallpaperEnginePage(QWidget):
    """Local library browser and safe Plasma bridge."""

    def __init__(
        self,
        *,
        hero_factory: Callable[[str, str, str, str], QFrame],
        logger: Callable[[str], None] | None = None,
        process_tracker: Callable[..., object] | None = None,
        settings: QSettings | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.logger = logger or (lambda _message: None)
        self.process_tracker = process_tracker
        self.settings = settings or QSettings()
        self.states = []
        self.steam_library = Path.home() / ".local/share/Steam"
        self.workshop_entries: list[WallpaperEntry] = []
        self.video_entries: list[WallpaperEntry] = []
        self._thumb_queue: list[tuple[QListWidgetItem, Path]] = []
        self._pending_success = ""
        self._pending_refresh = False
        self._intro_scheduled = False

        self.command_process = QProcess(self)
        self.command_process.finished.connect(self._command_finished)
        self.settings_process = QProcess(self)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setMinimumWidth(760)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 14, 22, 22)
        layout.setSpacing(14)
        layout.addWidget(
            hero_factory(
                "▧",
                "Wallpaper Engine",
                "Steam-Workshop-Wallpaper, eigene Videos und das CaptSilver-Plasma-Plugin direkt verwalten.",
                "KDE Plasma",
            )
        )

        self.status_box = QGroupBox("Plugin und aktuelle Einrichtung")
        status_layout = QVBoxLayout(self.status_box)
        self.status_label = QLabel("Wallpaper-Engine-Status wird gelesen …")
        self.status_label.setWordWrap(True)
        status_actions = QHBoxLayout()
        refresh = QPushButton("↻  Bibliotheken neu laden")
        refresh.clicked.connect(self.refresh_library)
        original = QPushButton("Originale Plasma-Oberfläche öffnen")
        original.clicked.connect(self.open_original_settings)
        guide = QPushButton("Einrichtungsassistent öffnen")
        guide.clicked.connect(lambda: self.show_setup_guide(force=True))
        status_actions.addWidget(refresh)
        status_actions.addWidget(original)
        status_actions.addWidget(guide)
        status_actions.addStretch()
        status_layout.addWidget(self.status_label)
        status_layout.addLayout(status_actions)
        layout.addWidget(self.status_box)

        control = QGroupBox("Wiedergabe")
        control_layout = QVBoxLayout(control)
        playback_layout = QHBoxLayout()
        for label, method in (
            ("◀  Zurück", "Previous"),
            ("Pause", "Pause"),
            ("Fortsetzen", "Resume"),
            ("Weiter  ▶", "Next"),
            ("Ton umschalten", "ToggleMute"),
        ):
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, name=method: self.run_playback(name))
            playback_layout.addWidget(button)
        playback_layout.addStretch()
        control_layout.addLayout(playback_layout)
        scaling_layout = QHBoxLayout()
        scaling_layout.addWidget(QLabel("Skalierung:"))
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.setAccessibleName("Wallpaper-Skalierungsmodus")
        for value, label in DISPLAY_MODES:
            self.display_mode_combo.addItem(label, value)
        scaling_layout.addWidget(self.display_mode_combo)
        apply_scaling = QPushButton("Skalierung anwenden")
        apply_scaling.clicked.connect(self.apply_display_mode)
        scaling_layout.addWidget(apply_scaling)
        scaling_layout.addStretch()
        control_layout.addLayout(scaling_layout)
        layout.addWidget(control)

        self.sections = QTabWidget()
        self.sections.setMinimumHeight(620)
        self.sections.addTab(self._make_workshop_tab(), "Wallpapers")
        self.sections.addTab(self._make_video_tab(), "Videos")
        self.sections.addTab(self._make_setup_tab(), "Einrichtung & Optimierung")
        layout.addWidget(self.sections)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.thumbnail_timer = QTimer(self)
        self.thumbnail_timer.setInterval(12)
        self.thumbnail_timer.timeout.connect(self._load_thumbnail_batch)
        QTimer.singleShot(0, self.refresh_library)

    def _make_workshop_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel(
            "Hier erscheinen ausschließlich die abonnierten Wallpaper aus der Steam-Bibliothek. "
            "Doppelklick oder „Ausgewähltes Wallpaper anwenden“ setzt das Motiv über Plasmas offizielle Skript-Schnittstelle."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        filters = QHBoxLayout()
        self.workshop_search = QLineEdit()
        self.workshop_search.setPlaceholderText("Wallpaper suchen …")
        self.workshop_search.textChanged.connect(self._filter_workshop)
        self.workshop_kind = QComboBox()
        for title, kind in (("Alle Typen", ""), ("Szenen", "scene"), ("Videos", "video"), ("Web", "web")):
            self.workshop_kind.addItem(title, kind)
        self.workshop_kind.currentIndexChanged.connect(self._filter_workshop)
        self.target_screen = QComboBox()
        self.target_screen.currentIndexChanged.connect(self._sync_display_mode)
        filters.addWidget(self.workshop_search, 2)
        filters.addWidget(self.workshop_kind)
        filters.addWidget(QLabel("Ziel:"))
        filters.addWidget(self.target_screen)
        layout.addLayout(filters)

        self.workshop_list = self._make_gallery()
        self.workshop_list.itemSelectionChanged.connect(self._update_workshop_detail)
        self.workshop_list.itemDoubleClicked.connect(lambda _item: self.apply_selected_workshop())
        layout.addWidget(self.workshop_list, 1)
        self.workshop_detail = QLabel("Noch kein Wallpaper ausgewählt.")
        self.workshop_detail.setWordWrap(True)
        self.workshop_detail.setObjectName("muted")
        apply_button = QPushButton("Ausgewähltes Wallpaper anwenden")
        apply_button.clicked.connect(self.apply_selected_workshop)
        layout.addWidget(self.workshop_detail)
        layout.addWidget(apply_button)
        return page

    def _make_video_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        notice = QLabel(
            "„Videos“ ist nur für einen kleinen, separaten Ordner mit eigenen MP4/WebM-Dateien. "
            "Die Steam-Bibliothek gehört nicht hier hinein; OHC blockiert diesen Fehlerfall ausdrücklich."
        )
        notice.setWordWrap(True)
        notice.setObjectName("warningText")
        layout.addWidget(notice)
        folder_actions = QHBoxLayout()
        self.video_folder_label = QLabel("Zusätzlicher Video-Ordner: leer (empfohlen)")
        choose = QPushButton("Video-Ordner wählen")
        choose.clicked.connect(self.choose_video_folder)
        clear = QPushButton("Video-Ordner leeren")
        clear.clicked.connect(self.clear_video_folder)
        folder_actions.addWidget(self.video_folder_label, 1)
        folder_actions.addWidget(choose)
        folder_actions.addWidget(clear)
        layout.addLayout(folder_actions)
        self.video_list = self._make_gallery()
        self.video_list.itemSelectionChanged.connect(self._update_video_detail)
        self.video_list.itemDoubleClicked.connect(lambda _item: self.apply_selected_video())
        layout.addWidget(self.video_list, 1)
        self.video_detail = QLabel("Kein zusätzlicher Video-Ordner eingerichtet.")
        self.video_detail.setWordWrap(True)
        apply_button = QPushButton("Ausgewähltes Video anwenden")
        apply_button.clicked.connect(self.apply_selected_video)
        layout.addWidget(self.video_detail)
        layout.addWidget(apply_button)
        return page

    def _make_setup_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        standard = QGroupBox("Originalzustand · Standard")
        standard_layout = QVBoxLayout(standard)
        standard_text = QLabel(
            "CaptSilver-v1.4-Standard: animierte Vorschau an, 30 FPS, Pause-Modus Nie, "
            "300 ms Wiederaufnahme und Present Mode Auto. Wallpaper-Auswahl, Steam-Pfad, Videos und Playlists bleiben erhalten."
        )
        standard_text.setWordWrap(True)
        standard_button = QPushButton("Originale Plugin-Werte anwenden")
        standard_button.clicked.connect(lambda: self.apply_profile(STOCK_PROFILE, "Originalzustand"))
        standard_layout.addWidget(standard_text)
        standard_layout.addWidget(standard_button)
        layout.addWidget(standard)

        optimized = QGroupBox("Optionale Leistungsoptimierung")
        optimized_layout = QVBoxLayout(optimized)
        optimized_text = QLabel(
            "25 FPS, Pause bei Vollbild, 1000 ms Wiederaufnahme, Present Mode Auto und statische Bibliotheksvorschauen. "
            "Es werden keine Plugin-Dateien gepatcht, keine Cache-Builder installiert und keine Watcher gestartet."
        )
        optimized_text.setWordWrap(True)
        optimized_button = QPushButton("Optionale Optimierung anwenden")
        optimized_button.clicked.connect(lambda: self.apply_profile(OPTIMIZED_PROFILE, "Optimierung"))
        optimized_layout.addWidget(optimized_text)
        optimized_layout.addWidget(optimized_button)
        layout.addWidget(optimized)
        self.onboarding = WallpaperEngineOnboarding(
            settings=self.settings,
            logger=self.logger,
            process_tracker=self.process_tracker,
            install_changed=self.refresh_library,
        )
        layout.addWidget(self.onboarding)
        xwayland_note = QLabel(
            "Der separate XWaylandVideoBridge-Fix und Plasma-Sicherungen werden von diesem Modul weder verändert noch entfernt."
        )
        xwayland_note.setWordWrap(True)
        layout.addWidget(xwayland_note)
        layout.addStretch()
        return page

    @staticmethod
    def _make_gallery() -> QListWidget:
        gallery = QListWidget()
        gallery.setViewMode(QListView.ViewMode.IconMode)
        gallery.setResizeMode(QListView.ResizeMode.Adjust)
        gallery.setMovement(QListView.Movement.Static)
        gallery.setIconSize(GALLERY_ICON_SIZE)
        gallery.setGridSize(GALLERY_GRID_SIZE)
        gallery.setWordWrap(True)
        gallery.setUniformItemSizes(True)
        return gallery

    def refresh_library(self) -> None:
        self.thumbnail_timer.stop()
        self._thumb_queue.clear()
        self.states = read_plasma_wallpaper_states(plasma_config_path())
        self.steam_library = preferred_steam_library(self.states)
        self.workshop_entries = scan_workshop_library(self.steam_library)
        video_folder = next((state.video_folder for state in self.states if state.video_folder), None)
        self.video_entries = scan_video_folder(video_folder) if video_folder else []
        self._populate_screens()
        self._sync_display_mode()
        self._populate_gallery(self.workshop_list, self.workshop_entries, workshop=True)
        self._populate_gallery(self.video_list, self.video_entries, workshop=False)
        self._update_status(video_folder)
        self.onboarding.update_runtime_state(
            plugin=plugin_installed(),
            steam_library=self.steam_library,
            wallpaper_count=len(self.workshop_entries),
            active_surfaces=len(self.states),
        )
        self.video_folder_label.setText(
            f"Zusätzlicher Video-Ordner: {video_folder}" if video_folder else "Zusätzlicher Video-Ordner: leer (empfohlen)"
        )
        self.video_detail.setText(
            f"{len(self.video_entries)} eigene Videos gefunden." if video_folder else "Kein zusätzlicher Video-Ordner eingerichtet."
        )
        if self._thumb_queue:
            self.thumbnail_timer.start()
        self._schedule_gallery_layout()

    def _populate_screens(self) -> None:
        previous = self.target_screen.currentData()
        self.target_screen.clear()
        self.target_screen.addItem("Alle Bildschirme", None)
        seen: set[int] = set()
        for state in self.states:
            if state.screen not in seen:
                seen.add(state.screen)
                self.target_screen.addItem(f"Bildschirm {state.screen + 1}", state.screen)
        index = self.target_screen.findData(previous)
        self.target_screen.setCurrentIndex(max(0, index))

    def _populate_gallery(self, gallery: QListWidget, entries: list[WallpaperEntry], *, workshop: bool) -> None:
        gallery.clear()
        active_ids = {state.workshop_id for state in self.states}
        for index, entry in enumerate(entries):
            marker = "● " if entry.ident in active_ids else ""
            label = f"{marker}{entry.title}\n{KIND_LABELS.get(entry.kind, entry.kind.title())}"
            item = QListWidgetItem(label)
            item.setSizeHint(GALLERY_GRID_SIZE)
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip(f"{entry.title}\n{entry.source_path}")
            gallery.addItem(item)
            if workshop and entry.preview_path is not None:
                self._thumb_queue.append((item, entry.preview_path))
        if gallery.count():
            gallery.setCurrentRow(0)

    def _load_thumbnail_batch(self) -> None:
        for _ in range(min(6, len(self._thumb_queue))):
            item, path = self._thumb_queue.pop(0)
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                item.setIcon(QIcon(pixmap.scaled(192, 108, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
        if not self._thumb_queue:
            self.thumbnail_timer.stop()
            self._schedule_gallery_layout()

    def _schedule_gallery_layout(self) -> None:
        """Reapply stable card metrics after an in-place library refresh."""

        for delay in (0, 80):
            QTimer.singleShot(delay, self._stabilize_gallery_layout)

    def _stabilize_gallery_layout(self) -> None:
        for gallery in (self.workshop_list, self.video_list):
            gallery.setIconSize(GALLERY_ICON_SIZE)
            gallery.setGridSize(GALLERY_GRID_SIZE)
            gallery.scheduleDelayedItemsLayout()
            gallery.doItemsLayout()
            gallery.viewport().updateGeometry()
            gallery.viewport().update()

    def _filter_workshop(self) -> None:
        needle = self.workshop_search.text().strip().casefold()
        kind = str(self.workshop_kind.currentData() or "")
        for row in range(self.workshop_list.count()):
            item = self.workshop_list.item(row)
            entry = self.workshop_entries[int(item.data(Qt.ItemDataRole.UserRole))]
            visible = (not needle or needle in entry.title.casefold() or needle in " ".join(entry.tags).casefold()) and (not kind or entry.kind == kind)
            item.setHidden(not visible)

    def _selected_entry(self, gallery: QListWidget, entries: list[WallpaperEntry]) -> WallpaperEntry | None:
        item = gallery.currentItem()
        if item is None:
            return None
        index = int(item.data(Qt.ItemDataRole.UserRole))
        return entries[index] if 0 <= index < len(entries) else None

    def _update_workshop_detail(self) -> None:
        entry = self._selected_entry(self.workshop_list, self.workshop_entries)
        self.workshop_detail.setText(
            "Noch kein Wallpaper ausgewählt." if entry is None else f"{entry.title} · {KIND_LABELS.get(entry.kind, entry.kind)} · Workshop-ID {entry.ident}"
        )

    def _update_video_detail(self) -> None:
        entry = self._selected_entry(self.video_list, self.video_entries)
        self.video_detail.setText("Kein Video ausgewählt." if entry is None else f"{entry.title} · {entry.source_path}")

    def _target_screen(self) -> int | None:
        value = self.target_screen.currentData()
        return value if isinstance(value, int) else None

    def _sync_display_mode(self) -> None:
        target = self._target_screen()
        state = next((item for item in self.states if target is not None and item.screen == target), None)
        if state is None and self.states:
            state = self.states[0]
        mode = normalize_display_mode(
            DEFAULT_DISPLAY_MODE if state is None else state.settings.get("DisplayMode", DEFAULT_DISPLAY_MODE)
        )
        index = self.display_mode_combo.findData(mode)
        self.display_mode_combo.setCurrentIndex(max(0, index))

    def apply_display_mode(self) -> None:
        mode = self.display_mode_combo.currentData()
        script = build_display_mode_script(mode, self._target_screen())
        self._run(plasma_script_command(script), "Die Wallpaper-Skalierung wurde angewendet.", refresh=True)

    def apply_selected_workshop(self) -> None:
        entry = self._selected_entry(self.workshop_list, self.workshop_entries)
        if entry is None:
            self.status_label.setText("Bitte zuerst ein Wallpaper auswählen.")
            return
        script = build_select_script(
            workshop_id=entry.ident,
            packed_source=entry.packed_source,
            steam_library=self.steam_library,
            target_screen=self._target_screen(),
        )
        self._run(plasma_script_command(script), f"„{entry.title}“ wurde an Plasma übergeben.", refresh=True)

    def apply_selected_video(self) -> None:
        entry = self._selected_entry(self.video_list, self.video_entries)
        if entry is None:
            self.status_label.setText("Bitte zuerst ein eigenes Video auswählen.")
            return
        script = build_select_script(
            workshop_id=entry.ident,
            packed_source=entry.packed_source,
            steam_library=self.steam_library,
            target_screen=self._target_screen(),
        )
        self._run(plasma_script_command(script), f"„{entry.title}“ wurde an Plasma übergeben.", refresh=True)

    def choose_video_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Separaten Video-Ordner wählen", str(Path.home() / "Videos"))
        if not selected:
            return
        folder = Path(selected)
        if is_unsafe_video_folder(folder, self.steam_library):
            QMessageBox.warning(
                self,
                "Steam-Bibliothek nicht als Video-Ordner verwenden",
                "Dieser Ordner ist die Steam-Bibliothek oder enthält steamapps. Nutze für eigene Videos einen separaten kleinen Ordner.",
            )
            return
        script = build_video_folder_script(folder, self._target_screen())
        self._run(plasma_script_command(script), "Der separate Video-Ordner wurde gespeichert.", refresh=True)

    def clear_video_folder(self) -> None:
        script = build_video_folder_script(None, self._target_screen())
        self._run(plasma_script_command(script), "Der zusätzliche Video-Ordner ist wieder leer.", refresh=True)

    def apply_profile(self, profile: dict[str, object], name: str) -> None:
        answer = QMessageBox.question(
            self,
            f"{name} anwenden",
            f"Soll das Profil „{name}“ auf das gewählte Ziel angewendet werden? Aktive Wallpaper und Bibliotheken bleiben erhalten.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        script = build_profile_script(profile, self._target_screen())
        self._run(plasma_script_command(script), f"{name} wurde angewendet.", refresh=True)

    def run_playback(self, method: str) -> None:
        if method == "Previous":
            self.apply_previous_workshop()
            return
        self._run(playback_command(method), f"Wiedergabebefehl {method} wurde ausgeführt.")

    def apply_previous_workshop(self) -> None:
        target = self._target_screen()
        state = next((item for item in self.states if target is not None and item.screen == target), None)
        if state is None and self.states:
            state = self.states[0]
        current_id = "" if state is None else state.workshop_id
        entry = previous_workshop_entry(self.workshop_entries, current_id)
        if entry is None:
            self.status_label.setText("Für Zurück wurde noch kein Workshop-Wallpaper gefunden.")
            return
        script = build_select_script(
            workshop_id=entry.ident,
            packed_source=entry.packed_source,
            steam_library=self.steam_library,
            target_screen=target,
        )
        self._run(plasma_script_command(script), f"Zurück zu „{entry.title}“.", refresh=True)

    def open_original_settings(self) -> None:
        command = original_settings_command()
        if command is None:
            self.status_label.setText("Die KDE-Hintergrundbild-Einstellungen wurden nicht gefunden.")
            return
        program, arguments = command
        self.settings_process.setProgram(program)
        self.settings_process.setArguments(arguments)
        self._track(self.settings_process, "wallpaper-settings")
        self.settings_process.start()
        self.logger("WALLPAPER ENGINE: Originale Plasma-Hintergrundbildoberfläche geöffnet")

    def show_setup_guide(self, *, force: bool = False) -> None:
        self.sections.setCurrentIndex(2)
        self.onboarding.show_first_start_dialog(force=force)
        if not self.onboarding.intro_complete():
            self._intro_scheduled = False

    def showEvent(self, event) -> None:  # noqa: N802 - Qt API
        super().showEvent(event)
        if self._intro_scheduled or self.onboarding.intro_complete():
            return
        self._intro_scheduled = True
        QTimer.singleShot(0, self.show_setup_guide)

    def _run(self, command: list[str], success: str, *, refresh: bool = False) -> None:
        if not command:
            self.status_label.setText("qdbus6 fehlt; Plasma kann momentan nicht gesteuert werden.")
            return
        if self.command_process.state() != QProcess.ProcessState.NotRunning:
            self.status_label.setText("Ein Wallpaper-Befehl läuft bereits. Bitte kurz warten.")
            return
        self._pending_success = success
        self._pending_refresh = refresh
        self.command_process.setProgram(command[0])
        self.command_process.setArguments(command[1:])
        self._track(self.command_process, "wallpaper-command")
        self.command_process.start()
        self.status_label.setText("Änderung wird sicher an Plasma übergeben …")

    def _track(self, process: QProcess, label: str) -> None:
        if self.process_tracker is None:
            return
        try:
            self.process_tracker(process, label)
        except TypeError:
            self.process_tracker(process)

    def _command_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        stderr = bytes(self.command_process.readAllStandardError()).decode("utf-8", "replace").strip()
        if exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0:
            message = self._pending_success or "Wallpaper-Befehl abgeschlossen."
            self.status_label.setText(message)
            self.logger(f"WALLPAPER ENGINE: {message}")
            if self._pending_refresh:
                QTimer.singleShot(250, self.refresh_library)
        else:
            detail = stderr.splitlines()[-1][:300] if stderr else f"Exit-Code {exit_code}"
            self.status_label.setText(f"Plasma hat den Wallpaper-Befehl nicht übernommen: {detail}")
            self.logger(f"WALLPAPER ENGINE FEHLER: {detail}")
        self._pending_success = ""
        self._pending_refresh = False

    def _update_status(self, video_folder: Path | None) -> None:
        installed = plugin_installed()
        active = len(self.states)
        counts: dict[str, int] = {}
        for entry in self.workshop_entries:
            counts[entry.kind] = counts.get(entry.kind, 0) + 1
        type_summary = " · ".join(f"{KIND_LABELS.get(kind, kind)} {count}" for kind, count in sorted(counts.items()))
        profile_names = []
        for state in self.states:
            merged = {key: state.settings.get(key, fallback) for key, fallback in STOCK_PROFILE.items()}
            profile_names.append("optimiert" if merged == OPTIMIZED_PROFILE else "Original/individuell")
        profile_summary = ", ".join(profile_names) if profile_names else "nicht aktiv"
        safe_video = "Video-Ordner leer" if video_folder is None else f"separater Video-Ordner: {video_folder}"
        self.status_label.setText(
            f"Plugin: {'installiert' if installed else 'nicht gefunden'} · aktive Plasma-Flächen: {active} · "
            f"Steam: {self.steam_library} · {len(self.workshop_entries)} Workshop-Wallpaper"
            + (f" ({type_summary})" if type_summary else "")
            + f" · {safe_video} · Profil: {profile_summary}"
        )
