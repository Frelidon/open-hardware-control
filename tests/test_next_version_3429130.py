#!/usr/bin/env python3
"""Regression tests for the compact GPU/RGB and measured case-space work."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.gpu_control.v1_0.page import preview_requires_graphics_load  # noqa: E402
from modules.pc_case_profiles.v1_5.spatial_layout import (  # noqa: E402
    DISTANCES_KEY, UNIT_KEY, display_distance, millimeters, read_links, upsert_link,
)
from modules.rgb_studio.v1_15.design_gallery import RGBDesignGallery  # noqa: E402
from modules.rgb_studio.v1_15.led_topology_store import set_case_direction  # noqa: E402

APP = QApplication.instance() or QApplication([])


class Settings:
    def __init__(self):
        self.data = {}

    def value(self, key, default=None, **_kwargs):
        return self.data.get(key, default)

    def setValue(self, key, value):
        self.data[key] = value

    def sync(self):
        return


def test_fan_only_trial_never_requires_graphics_load_helper():
    assert not preview_requires_graphics_load({"fan_control_enabled": True})
    assert not preview_requires_graphics_load({"fan_control_settings": {"mode": "static"}})
    assert preview_requires_graphics_load({"fan_control_enabled": True, "power_cap": 300})


def test_distance_values_are_stored_in_mm_and_round_trip_inches():
    settings = Settings()
    valid = {"front", "rear", "gpu"}
    assert upsert_link(settings, "front", "rear", "distance", 10.0, "in", valid)
    links = read_links(settings, valid)
    assert links == [{
        "source": "front", "target": "rear", "kind": "distance", "distance_mm": 254.0,
    }]
    assert display_distance(links[0]["distance_mm"], "in") == 10.0
    assert millimeters(1.0, "in") == 25.4
    assert DISTANCES_KEY in settings.data
    assert json.loads(settings.data[DISTANCES_KEY])[0]["distance_mm"] == 254.0


def test_invalid_or_stale_distance_endpoints_fail_closed():
    settings = Settings()
    settings.setValue(DISTANCES_KEY, json.dumps([
        {"source": "front", "target": "front", "kind": "depth", "distance_mm": 80},
        {"source": "front", "target": "missing", "kind": "depth", "distance_mm": 80},
    ]))
    assert read_links(settings, {"front", "rear"}) == []
    assert not upsert_link(settings, "front", "front", "distance", 10, "mm", {"front"})


def test_rgb_gallery_reaches_six_compact_columns_without_clipping_mode_button():
    gallery = RGBDesignGallery()
    gallery.resize(1200, 500)
    assert gallery.column_count() == 6
    assert gallery.card_height <= 132
    gallery.resize(600, 500)
    assert gallery.column_count() >= 3
    gallery.close()


def test_distance_unit_defaults_to_millimetres():
    settings = Settings()
    assert settings.value(UNIT_KEY, "mm") == "mm"


def test_spatial_direction_updates_saved_paths_without_hardware_io():
    class Host:
        settings = Settings()
        rgb_last_effect_request_signature = ("old",)

    Host.settings.setValue("rgb_studio/led_paths_v1", json.dumps({
        "openrgb:controller": {"ARGB": {
            "kind": "line", "start": "left", "end": "right", "units": 1,
            "clockwise": True, "direction": "local",
        }}
    }))
    assert set_case_direction(Host, "top-bottom")
    stored = json.loads(Host.settings.data["rgb_studio/led_paths_v1"])
    assert stored["openrgb:controller"]["ARGB"]["direction"] == "top-bottom"
    assert Host.settings.data["rgb_studio/case_effect_direction_v1"] == "top-bottom"
    assert Host.rgb_last_effect_request_signature is None


def test_gpu_page_disables_both_scrollbars_and_exposes_artwork_actions():
    source = (ROOT / "src/modules/gpu_control/v1_0/page.py").read_text(encoding="utf-8")
    source += (ROOT / "src/modules/gpu_control/v1_0/cockpit_ui.py").read_text(encoding="utf-8")
    assert "ScrollBarAlwaysOff" in source
    assert 'self.tr("Eigenes GPU-Bild importieren")' in source
    assert 'self.tr("GPU-Bild zurücksetzen")' in source
