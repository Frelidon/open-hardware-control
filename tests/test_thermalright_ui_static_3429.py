from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
UI = (ROOT / "src/thermalright_display_ui.py").read_text(encoding="utf-8")
LAYOUT_CANVAS = (ROOT / "src/modules" / "lcd_levita" / "v1_4" / "layout_canvas.py").read_text(encoding="utf-8")
LAYOUT_MODEL = (ROOT / "src/modules" / "lcd_levita" / "v1_4" / "layout_model.py").read_text(encoding="utf-8")
THEME_ADAPTER = (ROOT / "src/modules" / "lcd_levita" / "v1_4" / "theme_adapter.py").read_text(encoding="utf-8")
BUILD = (ROOT / "scripts" / "build_release.py").read_text(encoding="utf-8")
DESKTOP = (ROOT / "packaging/kraken-control.desktop.in").read_text(encoding="utf-8")


def test_thermalright_studio_is_a_full_width_lcd_tile() -> None:
    assert "from thermalright_display_ui import ThermalrightDisplayStudio" in MAIN
    assert '("thermalright", self.thermalright_display_studio, 3)' in MAIN


def test_test_mode_defaults_to_no_usb_writes() -> None:
    assert 'self.settings.value("thermalright/test_mode", True, type=bool)' in UI
    assert "if self.test_mode.isChecked():" in UI
    assert "nur Vorschau, keine USB-Schreibzugriffe" in UI


def test_cutout_and_drag_editor_are_visible() -> None:
    assert "from modules.lcd_levita.v1_4.layout_canvas import ThermalrightCanvas" in UI
    assert "ItemIsMovable" in LAYOUT_CANVAS
    assert 'cutout_label = self._scene.addSimpleText(f"NOTCH · {cutout_width} px")' in LAYOUT_CANVAS


def test_broken_trcc_split_modes_are_clearly_preview_only() -> None:
    assert "Stil A · derzeit nur Vorschau" in UI
    assert "TRCC Linux 9.9.11 bricht sie" in UI
    assert 'self.settings.value("thermalright/split_mode", 0)' in UI
    assert "safe_split_mode(saved_split_value)" in UI


def test_real_notch_mask_and_background_movement_are_user_adjustable() -> None:
    assert "Schwarzen Balken wirklich auf das Display legen" in UI
    assert "Maximale Bildfläche · minimaler 80-px-Notch" in UI
    assert "prepare_shifted_media(" in UI
    assert "create_layered_mask(" in UI
    assert "_MovableNotchItem" in LAYOUT_CANVAS
    assert "Einpassen · vollständig und unverzerrt" in UI
    assert "Radius oben rechts" in UI
    assert "Radius unten rechts" in UI
    assert "Oben und unten gemeinsam einstellen" in UI
    assert "self.notch_radius_linked.isChecked()" in UI
    assert "path.moveTo(-top, 0.0)" in LAYOUT_CANVAS
    assert "path.quadTo(0.0, 0.0, 0.0, top)" in LAYOUT_CANVAS
    assert "path.quadTo(0.0, height, -bottom, height)" in LAYOUT_CANVAS
    assert "outer_right_corner_wedges()" in LAYOUT_CANVAS
    assert "def fill_outside_levita_panel" in (
        ROOT / "src/modules" / "lcd_levita" / "v1_4" / "panel_geometry.py"
    ).read_text(encoding="utf-8")
    assert "READABLE_CONTROL_HEIGHT = 36" in UI
    assert "def _readable_value_widget" in UI
    assert "def _readable_combo" in UI
    assert 'self.geometry_box.setObjectName("levitaGeometryBox")' in UI
    assert "geometry_grid.addWidget(self.notch_visible, 1, 0, 1, 4)" in UI
    assert "_readable_combo(self.media_scale_mode)" in UI
    assert "_readable_combo(self.split_mode)" in UI
    assert 'self.geometry_scroll.setObjectName("levitaGeometryScroll")' in UI
    assert "self.geometry_scroll.setMinimumWidth(400)" in UI
    assert "self.geometry_scroll.setMaximumWidth(460)" not in UI
    assert "self.geometry_toggle.toggled.connect(self.geometry_scroll.setVisible)" in UI


def test_media_library_uses_cards_and_animates_the_main_preview() -> None:
    assert "self.media_cards_grid" in UI
    assert "self.hardware_cards_grid" in UI
    assert "def _design_card" in UI
    assert "def _show_media_preview_tile" in UI
    assert "def _hover_preview_sources" in UI
    assert "self.hover_extract_process = track_qprocess(QProcess(self))" in UI
    assert '"-vf", "fps=4,scale=800:-2"' in UI
    assert '"-frames:v", "16"' in UI
    assert "def _fit_hover_preview_frames" in UI
    assert "self.canvas.set_background(frame)" in UI
    assert "def _fit_transparent_layer_pixmap" in UI
    assert "canvas.fill(QColor(0, 0, 0, 0))" in UI
    assert "TRCC-Prozess ist abgestürzt (externer Backend-/libusb-Fehler)" in UI
    assert "def _immediate_background_pixmap" in UI
    assert "self._prioritize_video_thumbnail(media)" in UI
    assert "self.media_combo.hide()" in UI
    assert "def _video_card_thumbnail" in UI
    assert "self.hover_card_button.setIcon" in UI
    assert "Videos beim Darüberfahren in der Karte animieren" in UI


def test_video_card_thumbnails_use_a_bounded_persistent_background_queue() -> None:
    assert "self.thumbnail_workers: list[QProcess] = []" in UI
    assert "for _worker_number in range(2):" in UI
    assert "self.thumbnail_progress = QProgressBar()" in UI
    assert "Cache bleibt für nächste Programmstarts erhalten" in UI
    assert "def _queue_video_thumbnail" in UI
    assert "def _start_thumbnail_workers" in UI
    assert "return self._queue_video_thumbnail(media)" in UI
    assert "subprocess.run" not in UI
    assert "thumbnail extraction failed" in UI


def test_lcd_studio_has_separate_background_and_hardware_design_layers() -> None:
    assert "Ebene 1 · Hintergrund" in UI
    assert "Ebene 2 · Datenoberfläche" in UI
    assert "self.hardware_design_combo" in UI
    assert "create_hardware_design_preview(" in UI
    assert "hardware_design=hardware_design" in UI
    assert "Hintergrundvideo läuft hinter dem Live-Hardware-Design" in UI
    assert "TRCC-Standarddesigns" in UI
    assert "default_trcc_design_directory()" in UI
    assert "config1.dc übernimmt Positionen, Farben und Live-Sensorwerte direkt" in UI
    assert 'entry.kind != "theme" or str(entry.path) in self.background_theme_overrides' in UI
    assert "Auswahl → Ebene 2" in UI
    assert "Auswahl → Ebene 1" in UI
    assert "TRCC-Standarddesign aktiv" in UI
    assert "Live-Vorschau · Levita 1600 × 720 · Hintergrund + Ebene 2" in UI
    assert 'full_theme_preview = hardware_design / "Theme.png"' in UI


def test_levita_preview_is_centered_at_the_real_display_aspect_ratio() -> None:
    assert "self.setMaximumSize(960, 432)" in LAYOUT_CANVAS
    assert "def heightForWidth" in LAYOUT_CANVAS
    assert "LEVITA_HEIGHT / LEVITA_WIDTH" in LAYOUT_CANVAS
    assert 'preview_stage.setObjectName("levitaPreviewStage")' in UI
    assert "self.preview_canvas_row.addWidget(self.canvas, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)" in UI
    assert "self.preview_canvas_row.insertWidget(1, self.geometry_scroll, 1)" in UI
    assert "galleries = QHBoxLayout()" in UI
    assert "MEDIA_GALLERY_COLUMNS = (4, 8)" in UI
    assert "HARDWARE_GALLERY_COLUMNS = (4, 8)" in UI
    assert "DESIGN_CARD_WIDTH = 180" in UI
    assert "def gallery_column_count" in UI
    assert "def _relayout_design_galleries" in UI


def test_custom_folder_can_be_hidden_without_forgetting_or_deleting_it() -> None:
    assert 'thermalright/custom_media_directory' in UI
    assert 'thermalright/custom_media_enabled' in UI
    assert "Eigenen Designordner einbeziehen" in UI
    assert "Dateien auf der Festplatte bleiben erhalten" in UI
    assert "def show_remembered_media_directory" in UI
    assert "def _toggle_custom_media_directory" in UI
    assert "deduplicate_media_entries(entries)" in UI
    assert "gleiche Dateinamen nur einmal angezeigt" in UI
    assert "keine Dateien kopiert oder gelöscht" in UI


def test_levita_has_real_independent_display_settings_and_usb_timeout_guard() -> None:
    assert "Levita-Displayeinstellungen · unabhängig von der NZXT Kraken" in UI
    assert "Levita-Helligkeit und Ausrichtung anwenden" in UI
    assert "self.cli.brightness_args" in UI
    assert "self.cli.orientation_args" in UI
    assert "USB-Timeout beim Levita-Handshake" in UI
    assert "self.apply_retry_remaining = 1" in UI
    assert 'command_environment.insert("TRCC_DAEMON", "1")' in UI
    assert 'command_environment.insert("QT_QPA_PLATFORM", "offscreen")' in UI
    assert "self._daemon_stream_started()" in UI
    assert "self.stream_process = track_qprocess(QProcess(self))" in UI
    assert "self.stream_process.started.connect(self._on_stream_started)" in UI
    assert "args = self.cli.play_args(0.15)" in UI
    assert "self._stop_stream_client()" in UI
    assert "self.command_step_timer.setInterval(350)" in UI
    assert "self.command_step_timer.start()" in UI
    assert "die zuletzt gewählte Kombination" in UI
    assert "LEVITA_APPLY_COOLDOWN_SECONDS = 10.0" in UI
    assert "Levita-Designwechsel vorgemerkt" in UI
    assert "Display bitte einmal vollständig stromlos machen" in UI
    assert "self.cli.stop_video_now(timeout=1.5)" in UI
    assert "aktives TRCC-Originaldesign wiederhergestellt" in UI
    assert "commands = self.cli.reconnect_sequence()" in UI
    assert "Display wird sauber neu verbunden" in UI


def test_editable_theme_stages_assets_then_explicitly_enables_combined_mask() -> None:
    assert "background_video=background_video" in UI
    assert "mask_image=mask_path" in UI
    assert "apply_media = apply_hardware_design" in UI
    assert "apply_mask_path = mask_path" in UI
    assert 'target / f"Theme{video.suffix.casefold()}"' in THEME_ADAPTER
    assert 'name == "01.png" and mask is not None' in THEME_ADAPTER


def test_levita_start_design_is_explicit_and_retried_once() -> None:
    assert "Ausgewähltes Levita-Design bei OHC-Start automatisch laden" in UI
    assert "Aktuelle Auswahl als Startdesign speichern" in UI
    assert "def apply_startup_design_if_enabled" in UI
    assert "self.startup_retry_count >= 1" in UI
    assert "thermalright_studio.apply_startup_design_if_enabled" in MAIN


def test_running_window_has_kde_desktop_identity_and_icon() -> None:
    assert 'app.setDesktopFileName("open-hardware-control")' in MAIN
    assert "app.setWindowIcon(application_icon(" in MAIN
    assert "StartupWMClass=open-hardware-control" in DESKTOP


def test_project_owned_levita_media_are_packaged_from_an_explicit_allowlist() -> None:
    from PIL import Image

    designs = ROOT / "src/assets" / "levita-designs"
    expected_images = {
        "ohc-carbon-blue.png",
        "ohc-titanium-blue.png",
        "ohc-plasma-circuit.png",
        "ohc-ai-neon-corridor.png",
        "ohc-ai-orbital-observatory.png",
        "ohc-ai-neon-city.png",
        "ohc-ai-azure-reactor.png",
        "ohc-ai-deep-space-command.png",
        "ohc-ai-quantum-portal.png",
        "ohc-ai-crystal-core.png",
        "ohc-ai-command-deck.png",
    }
    expected_video = "ohc-ai-quantum-voyage-30s.mp4"
    expected_top_level = expected_images | {expected_video, "README.md"}
    assert {path.name for path in designs.iterdir() if path.is_file()} == expected_top_level
    assert {path.name for path in designs.iterdir() if path.is_dir()} == {
        "ohc-nebula-drift",
        "ohc-orbital-command",
    }
    for filename in expected_images:
        with Image.open(designs / filename) as image:
            assert image.size == (1600, 720)
    assert (designs / expected_video).stat().st_size > 1_000_000
    for filename in expected_images | {expected_video}:
        assert filename in UI
    assert '"ohc": "OHC-Designs"' in (ROOT / "src/thermalright_display.py").read_text(encoding="utf-8")


def test_overlay_spacing_presets_remain_individually_editable() -> None:
    assert "Zwei saubere Reihen" in UI
    assert "Untereinander" in UI
    assert 'self.apply_overlay_layout("two_rows")' in UI
    assert "Letzten Zustand wiederherstellen" in UI


def test_runtime_package_contains_all_thermalright_modules() -> None:
    assert '"thermalright_cooling.py"' in BUILD
    assert '"thermalright_display.py"' in BUILD
    assert '"thermalright_display_ui.py"' in BUILD
    assert '"modules"' in BUILD


def test_release_profiles_keep_runtime_lean_and_developer_package_complete() -> None:
    assert "def validate_package_profiles" in BUILD
    assert 'runtime / "tests"' in BUILD
    assert "packaged_development_files" in BUILD
    assert 'development_roots = ("tests", "scripts", ".github", ".cursor", "tools")' in BUILD
    assert '"scripts/check_release.sh"' in BUILD
    assert '".github/workflows/ci.yml"' in BUILD
    assert '"tools/analyze_usbpcap.py"' in BUILD
    assert "def build_local_ai_git_bundle(developer: Path, temp: Path)" in BUILD
    assert 'shutil.copytree(developer, snapshot, dirs_exist_ok=True)' in BUILD
    assert '"commit", "-m", f"Open Hardware Control {VERSION} {CHANNEL} source snapshot"' in BUILD


def test_layer2_complete_themes_are_individually_editable_without_rewriting_dc() -> None:
    assert "layout_moved=self._layer2_block_moved" in UI
    assert "layout_edit_requested=self._open_layer2_inline_editor" in UI
    assert "Gesamt X" in UI and "Gesamt Y" in UI
    assert "Rechtsklick ändert Text, Farbe und Schriftgröße" in UI
    assert "def _open_layer2_inline_editor" in UI
    assert 'self.layer2_inline_editor.setObjectName("layer2InlineEditor")' in UI
    assert "QInputDialog" not in LAYOUT_CANVAS
    assert "QColorDialog" not in LAYOUT_CANVAS
    assert "QMenu" not in LAYOUT_CANVAS
    assert "Live-Wert und Bezeichnung bleiben ein gemeinsamer Block" in UI
    assert "def with_edited_text" in LAYOUT_MODEL
    assert "stage_editable_theme(" in UI
    assert "config1.dc" in THEME_ADAPTER
    assert ".write_bytes(" not in THEME_ADAPTER


def test_layer_switch_does_not_rebuild_background_catalog_or_double_preview() -> None:
    hardware_change = UI.split("def _hardware_design_changed", 1)[1].split("def _entry_for_path", 1)[0]
    assert "_apply_media_filter" not in hardware_change
    populate = UI.split("def _populate_media_combo", 1)[1].split("def _populate_hardware_design_combo", 1)[0]
    selected = populate.index("self.media_combo.setCurrentIndex")
    unblocked = populate.index("self.media_combo.blockSignals(False)")
    refreshed = populate.index("self.update_preview()")
    assert selected < unblocked < refreshed


def test_lcd_tiles_follow_detected_display_shape_and_collapse_kraken_importer() -> None:
    assert "def update_lcd_hardware_layout" in MAIN
    assert 'area.set_key_visible("preview", has_kraken)' in MAIN
    assert 'area.set_key_visible("thermalright", thermalright_present)' in MAIN
    assert 'key not in {"thermalright", "display"}' in MAIN
    assert "def set_kraken_importer_expanded" in MAIN
    assert "eingeklappt · zum Aktivieren anklicken" in MAIN


def test_openrgb_crash_is_quarantined_and_ui_tests_disable_hardware_io() -> None:
    assert 'os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1"' in MAIN
    assert "self.openrgb_engine_crash_quarantined = True" in MAIN
    assert "automatischer Neustart gesperrt" in MAIN
    assert "env=openrgb_subprocess_environment()" in MAIN


def test_gallery_column_count_fills_the_available_width() -> None:
    from thermalright_display_ui import gallery_column_count

    assert gallery_column_count(400, minimum=4, maximum=8) == 4
    assert gallery_column_count(1600, minimum=4, maximum=8) == 8
    assert gallery_column_count(1400, minimum=4, maximum=8) >= 6
    assert gallery_column_count(900, minimum=4, maximum=8) >= 4
    assert gallery_column_count(900, minimum=4, maximum=8) <= 8
