#!/usr/bin/env python3
"""Regression coverage for 3.4.29.71 compact UI and case profiles."""

from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QPointF, Qt  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402

from modules.pc_case_profiles.v1_5 import (  # noqa: E402
    CASE_TEMPLATES, DEFAULT_CASE_ID, case_template, decode_profiles, encode_profiles,
)
from modules.pc_case_profiles.v1_5.profiles import normalize_hardware_snapshot  # noqa: E402
from modules.window_chrome.v1_2 import FramelessResizeController, edge_at_position  # noqa: E402
from rgb_effects import BUILTIN_DESIGN_CATEGORIES, BUILTIN_DESIGNS  # noqa: E402


def test_case_catalog_has_30_unique_original_templates_and_exact_retro_default() -> None:
    assert len(CASE_TEMPLATES) == 30
    assert len({item.case_id for item in CASE_TEMPLATES}) == 30
    assert all(item.source_url.startswith("https://") for item in CASE_TEMPLATES)
    retro = case_template(DEFAULT_CASE_ID)
    assert retro.exact
    assert retro.title == "Thermaltake · Retro 360 TG"
    assert retro.radiator_mm == 360
    assert dict(retro.fan_layout) == {"front": 2, "side": 3, "top": 3, "rear": 1, "bottom": 3}
    assert {item.visual_style for item in CASE_TEMPLATES} == {"retro", "slatted", "panorama", "dual", "compact", "classic"}


def test_pc_profile_decoder_is_bounded_and_rejects_untrusted_shapes() -> None:
    profiles = [{
        "id": "user-main-1", "name": "Main PC", "case_id": DEFAULT_CASE_ID,
        "cooling_visual": "aio",
        "groups": [{"id": "fans", "name": "Fans"}], "slots": [{"position": "top"}],
    }]
    assert decode_profiles(encode_profiles(profiles)) == profiles
    assert decode_profiles("not json") == []
    assert decode_profiles('[{"id":"builtin","name":"No","slots":[]}]') == []


def test_pc_profile_roundtrips_complete_settings_only_rgb_topology() -> None:
    hardware = {
        "slot_routes": {
            "fans-front": {"controller": "openrgb:hub", "zone": "Channel A1"},
            "fans-side": {"controller": "openrgb:hub", "zone": "Channel A2"},
        },
        "fan_profiles": {
            "fans-front": {"brand": "TZMRIT", "model": "Interstellar-V2", "color": "black", "leds_per_fan": 8},
        },
        "zone_configurations": {
            "openrgb:hub": {
                "Channel A1": {"units": 2, "leds_per_unit": 8},
                "Channel A2": {"units": 3, "leds_per_unit": 8},
            },
        },
        "led_paths": {"openrgb:hub": {"Channel A1": {
            "kind": "line", "start": "top", "end": "bottom", "units": 2,
            "clockwise": True, "direction": "top-bottom",
        }}},
        "manual_headers": {"openrgb:hub": ["Channel A1", "Channel A2"]},
        "group_assignments": {"openrgb:ram-1": "ram"},
        "device_aliases": {"openrgb:ram-1": "RAM-Riegel 1"},
        "selected_devices": ["openrgb:hub", "openrgb:ram-1"],
        "pwm_assignments": {"hw:pwm4": "fans-front"},
        "aio_channels": {"pump": "hw:pwm2", "radiator": "hw:pwm1"},
        "case_direction": "top-bottom",
    }
    profile = {
        "id": "user-main-1", "name": "Main PC", "case_id": DEFAULT_CASE_ID,
        "cooling_visual": "aio", "groups": [{"id": "ram", "name": "RAM"}],
        "slots": [{"position": "ram"}], "hardware": hardware,
    }
    restored = decode_profiles(encode_profiles([profile]))[0]
    assert restored["hardware"] == normalize_hardware_snapshot(hardware)
    assert restored["hardware"]["aio_channels"] == {"pump": "hw:pwm2", "radiator": "hw:pwm1"}
    assert restored["hardware"]["zone_configurations"]["openrgb:hub"]["Channel A2"] == {
        "units": 3, "leds_per_unit": 8,
    }
    bad = normalize_hardware_snapshot({
        "slot_routes": {"fans": {"controller": "not-openrgb", "zone": "A1"}},
        "selected_devices": ["good", "bad\n", "x" * 97],
        "pwm_assignments": {"bad\n": "fans"},
        "aio_channels": {"pump": "bad\n", "radiator": "", "unknown": "hw:pwm1"},
    })
    assert bad["slot_routes"] == {}
    assert bad["selected_devices"] == ["good"]
    assert bad["pwm_assignments"] == {}
    assert bad["aio_channels"] == {"pump": "", "radiator": ""}
    assert normalize_hardware_snapshot({"aio_channels": {"pump": "same", "radiator": "same"}})["aio_channels"] == {
        "pump": "same", "radiator": "",
    }


def test_frameless_resize_edges_cover_corners_and_center() -> None:
    assert edge_at_position(QPointF(1, 1), 1000, 700) == Qt.Edge.TopEdge | Qt.Edge.LeftEdge
    assert edge_at_position(QPointF(999, 699), 1000, 700) == Qt.Edge.BottomEdge | Qt.Edge.RightEdge
    assert edge_at_position(QPointF(500, 350), 1000, 700) == Qt.Edge(0)


def test_frameless_resize_cursor_is_explicitly_released() -> None:
    QApplication.instance() or QApplication([])
    window = QWidget()
    child = QWidget(window)
    controller = FramelessResizeController(window)
    controller._set_resize_cursor(child, Qt.Edge.LeftEdge)
    assert child.cursor().shape() == Qt.CursorShape.SizeHorCursor
    controller.clear_resize_cursor()
    assert child.cursor().shape() == Qt.CursorShape.ArrowCursor
    controller.detach()
    window.deleteLater()


def test_rgb_library_adds_spatial_designs_without_breaking_category_alignment() -> None:
    assert len(BUILTIN_DESIGNS) == 45
    assert len(BUILTIN_DESIGN_CATEGORIES) == len(BUILTIN_DESIGNS)
    assert [title for title, _config in BUILTIN_DESIGNS[20:30]] == [
        "Nebula Pulse", "Liquid Metal", "Ember Flow", "Arctic Halo",
        "Center Fusion", "Crimson Convergence", "Orbital Crossflow",
        "Dual Vector", "Deep Space Sweep", "Vertical Reactor",
    ]
    assert [title for title, _config in BUILTIN_DESIGNS[30:34]] == [
        "Prism Drift", "Twin Wyrm Orbit", "Neon Particle Garden", "Circuit Chase",
    ]


def test_personal_amazon_link_is_not_part_of_case_ui() -> None:
    controller = (ROOT / "src/modules/pc_case_profiles/v1_5/controller.py").read_text(encoding="utf-8")
    main = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    assert "Amazon" not in controller
    assert "RETRO_360_AMAZON_URL" not in controller
    assert "def open_rgb_layout_slot_device_editor" in controller
    assert "self.configure_openrgb_zones(openrgb_device)" in controller
    assert "if not openrgb_device.supports_direct:" in controller
    assert "keine zusätzlichen einzeln animierten LEDs erfinden" in controller
    workspace = (ROOT / "src/modules/pc_case_profiles/v1_5/workspace.py").read_text()
    assert "slot_selected.connect(self.open_rgb_layout_slot_device_editor)" in workspace
    assert "build_case_workspace(self)" in main
    inline = (ROOT / "src/modules/pc_case_profiles/v1_5/inline_editor.py").read_text()
    assert "MouseButtonPress" not in inline
