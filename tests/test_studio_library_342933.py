#!/usr/bin/env python3
"""Regression coverage for the compact 3.4.29.33 RGB/LCD libraries."""

import json
import hashlib
import sys
from pathlib import Path

from PIL import Image

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
    expected = {
        "ohc-nebula-drift", "ohc-nebula-drift-minimal",
        "ohc-nebula-drift-performance", "ohc-orbital-command", "ohc-orbit", "ohc-aqua-pulse",
        "ohc-horizon-glass", "ohc-split-core", "ohc-spectrum-ring",
        "ohc-neon-double-arc", "ohc-prism-segments", "ohc-aurora-radar",
    }
    assert expected <= themes.keys()
    for name in expected:
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


def test_nebula_variants_keep_translucent_art_and_use_different_metrics() -> None:
    designs = ROOT / "src/assets" / "levita-designs"
    nebula = designs / "ohc-nebula-drift"
    with Image.open(nebula / "source-overlay.png") as source_image:
        source = source_image.convert("RGBA")
    assert source.size == (LEVITA_WIDTH, LEVITA_HEIGHT)
    assert source.getchannel("A").getextrema() == (0, 255)

    metric_sets = set()
    variants = (
        "ohc-nebula-drift", "ohc-nebula-drift-minimal",
        "ohc-nebula-drift-performance",
    )
    for name in variants:
        target = designs / name
        with Image.open(target / "01.png") as styled_image:
            styled = styled_image.convert("RGBA")
        alpha = styled.getchannel("A")
        assert styled.size == source.size
        assert alpha.getextrema()[0] == 0
        assert sum(alpha.histogram()[:255]) > styled.width * styled.height * 0.70
        config = json.loads((target / "trcc.json").read_text(encoding="utf-8"))
        metric_sets.add(tuple(
            item.get("metric") for item in config["elements"] if item.get("type") == "metric"
        ))
    assert len(metric_sets) == 3


def test_nebula_value_pills_include_the_measured_trcc_font_reserve() -> None:
    renderer = (ROOT / "tools" / "render_levita_overlays.py").read_text(encoding="utf-8")
    assert "TRCC_TEXT_WIDTH_FACTOR = 1.22" in renderer
    assert "TRCC_TEXT_HEIGHT_FACTOR = 1.12" in renderer
    assert "math.ceil(preview_width * TRCC_TEXT_WIDTH_FACTOR)" in renderer
    assert "math.ceil(preview_height * TRCC_TEXT_HEIGHT_FACTOR)" in renderer


def test_project_owned_overlay_styles_are_distinct() -> None:
    designs = ROOT / "src/assets" / "levita-designs"

    style_names = (
        "ohc-orbit", "ohc-aqua-pulse", "ohc-horizon-glass", "ohc-split-core",
        "ohc-spectrum-ring", "ohc-neon-double-arc", "ohc-prism-segments",
        "ohc-aurora-radar",
    )
    digests = {
        hashlib.sha256((designs / name / "01.png").read_bytes()).hexdigest()
        for name in style_names
    }
    assert len(digests) == len(style_names)


def test_lcd_library_exposes_import_assignment_and_favorites() -> None:
    assert 'QPushButton("LCD-Manager")' in LEVITA_UI
    assert "DesignLibraryPanel" in LEVITA_UI
    assert "self.library_manager_panel.saved.connect" in LEVITA_UI
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
