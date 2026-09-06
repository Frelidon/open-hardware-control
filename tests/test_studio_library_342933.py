#!/usr/bin/env python3
"""Regression coverage for the compact 3.4.29.33 RGB/LCD libraries."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thermalright_display import LEVITA_HEIGHT, LEVITA_WIDTH, scan_media_directory


RGB_UI = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
LEVITA_UI = (ROOT / "src/thermalright_display_ui.py").read_text(encoding="utf-8")


def test_bundled_space_layouts_are_valid_native_levita_themes() -> None:
    themes = {
        entry.path.name: entry
        for entry in scan_media_directory(ROOT / "src/assets" / "levita-designs")
        if entry.kind == "theme"
    }
    assert {"ohc-nebula-drift", "ohc-orbital-command"} <= themes.keys()
    for name in ("ohc-nebula-drift", "ohc-orbital-command"):
        config = json.loads((themes[name].path / "trcc.json").read_text(encoding="utf-8"))
        assert (config["width"], config["height"]) == (LEVITA_WIDTH, LEVITA_HEIGHT)
        assert config["elements"]


def test_orbital_command_contains_requested_cpu_gpu_and_vram_values() -> None:
    config = json.loads(
        (ROOT / "src/assets" / "levita-designs" / "ohc-orbital-command" / "trcc.json").read_text(
            encoding="utf-8"
        )
    )
    metrics = {item.get("metric") for item in config["elements"]}
    assert {
        "cpu:usage", "cpu:temp", "cpu:freq", "gpu:primary:usage",
        "gpu:primary:temp", "gpu:primary:clock", "gpu:primary:vram_used",
    } <= metrics


def test_lcd_library_exposes_import_assignment_and_favorites() -> None:
    assert "Eigene Designs importieren · Ordner" in LEVITA_UI
    assert "★ Nur Favoriten" in LEVITA_UI
    assert "Als Ebene 1 · Hintergrund verwenden" in LEVITA_UI
    assert "Als Ebene 2 · Datenoberfläche verwenden" in LEVITA_UI
    assert '"thermalright/design_favorites", json.dumps(sorted(self.design_favorites))' in LEVITA_UI
    assert "galleries = QHBoxLayout()" in LEVITA_UI
    assert '"migration/v342933_minimal_levita_notch"' in LEVITA_UI
    assert "notch_width_setting = LEVITA_CUTOUT_WIDTH" in LEVITA_UI


def test_rgb_selection_and_per_design_colors_are_persisted() -> None:
    assert 'settings.setValue("rgb_studio/selected_design_index"' in RGB_UI
    assert '"rgb_studio/design_color_overrides"' in RGB_UI
    assert "set_design_overrides" in RGB_UI
    assert "🎨 Hauptfarbe ändern" in RGB_UI
    assert "🎨 Zweitfarbe ändern" in RGB_UI
