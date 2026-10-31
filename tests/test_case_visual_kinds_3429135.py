"""Regression checks for explicit fan/ring/strip case visualization."""

import os
from dataclasses import asdict
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication  # noqa: E402
from rgb_devices import (  # noqa: E402
    RGBGroup,
    RGBLayoutSlot,
    layout_visual_kind,
    normalize_layout_slots,
    auto_arrange_layout_slots,
)
from modules.pc_case_profiles.v1_5 import PCLayoutDiagram  # noqa: E402
from modules.gpu_profiles.v1_0.visual_catalog import detect_gpu_visual, resolve_gpu_visual  # noqa: E402


APP = QApplication.instance() or QApplication([])


def test_visual_kind_migrates_and_defaults_from_role() -> None:
    groups = (RGBGroup("g", "Group"),)
    restored = normalize_layout_slots([
        {"position": "gpu", "name": "GPU", "count": 3, "group_id": "g", "visual_kind": "fans"},
        {"position": "gpu-support", "name": "Holder", "count": 1, "group_id": "g"},
        {"position": "front", "name": "Front", "count": 3, "group_id": "g", "visual_kind": "invalid"},
    ], groups)
    assert restored[0].visual_kind == "fans" and layout_visual_kind(restored[0]) == "fans"
    assert layout_visual_kind(restored[1]) == "strip"
    assert restored[2].visual_kind == "auto" and layout_visual_kind(restored[2]) == "fans"


def test_gpu_visual_profile_detects_only_specific_board_family() -> None:
    nitro = detect_gpu_visual("Sapphire NITRO+ Radeon RX 9070 XT")
    assert nitro is not None and nitro.lighting == "edge-strip" and nitro.fan_count == 3
    aorus = detect_gpu_visual("GIGABYTE AORUS GeForce RTX 5090 MASTER")
    assert aorus is not None and aorus.lighting == "fan-rings"
    assert detect_gpu_visual("AMD Radeon RX 9070 XT") is None
    assert resolve_gpu_visual("generic-triple-hubs", "unknown").lighting == "fan-hubs"


def test_every_visual_shape_renders_without_touching_hardware() -> None:
    diagram = PCLayoutDiagram()
    diagram.resize(960, 700)
    diagram.set_slots([
        RGBLayoutSlot("gpu", "GPU fans", 3, "g", slot_id="gpu", x=.5, y=.5, visual_kind="fans"),
        RGBLayoutSlot("gpu-support", "Strip", 1, "g", slot_id="strip", x=.5, y=.7, visual_kind="strip"),
        RGBLayoutSlot("pump", "Ring", 1, "g", slot_id="ring", x=.35, y=.35, visual_kind="ring"),
    ])
    image = diagram.grab().toImage()
    assert not image.isNull()
    source = (ROOT / "src/modules/pc_case_profiles/v1_5/diagram.py").read_text(encoding="utf-8")
    assert "draw_strip_visual" in source and "draw_ring_visual" in source
    assert "_animation_color" in source
    assert "draw_gpu_edge_lighting" in source
    assert 'spec.get("gpu_lighting") in {"edge-strip", "mixed", "indirect"}' in source
    assert 'if visual_kind == "component" and slot.position != "gpu":' in source
    assert "draw_gpu_component" in source
    diagram.close()


def test_visual_choices_survive_move_profile_serialization_and_rearrange():
    from kraken_control import KrakenControl
    from modules.pc_case_profiles.v1_5.controller import PcCaseProfilesMixin
    from types import SimpleNamespace
    slot = RGBLayoutSlot("gpu", "Custom GPU", 3, "g", slot_id="gpu", scale=1.25,
                         visual_kind="fans", gpu_visual="generic-triple-rings")
    moved = KrakenControl.copy_rgb_layout_slot(slot, x=.7, y=.8)
    assert moved.visual_kind == "fans" and moved.gpu_visual == "generic-triple-rings"
    arranged = auto_arrange_layout_slots([moved])[0]
    assert arranged.visual_kind == "fans" and arranged.gpu_visual == "generic-triple-rings"
    serialized = PcCaseProfilesMixin.rgb_layout_slots_payload(SimpleNamespace(rgb_layout_slots=[arranged]))
    assert serialized[0]["visual_kind"] == "fans"
    assert serialized[0]["gpu_visual"] == "generic-triple-rings"
    restored = normalize_layout_slots(serialized, (RGBGroup("g", "Group"),))
    assert restored == [arranged]
    assert asdict(restored[0])["scale"] == 1.25
