from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def test_bundled_ohc_layouts_keep_literal_units_visible_on_device() -> None:
    for name in ("ohc-nebula-drift", "ohc-orbital-command"):
        payload = json.loads((ROOT / "src/assets" / "levita-designs" / name / "trcc.json").read_text(encoding="utf-8"))
        metrics = [item for item in payload["elements"] if item.get("type") == "metric"]
        assert metrics
        assert all(item.get("show_unit") is True for item in metrics)

from modules.lcd_levita.v1_4.layout_model import (
    EditableLayout,
    LayoutBlock,
    deserialize_layout_overrides,
    layout_from_config,
    serialize_layout_overrides,
)
from modules.lcd_levita.v1_4.runtime_policy import safe_split_mode
from modules.lcd_levita.v1_4.theme_adapter import (
    load_editable_layout,
    stage_editable_theme,
)


def sample_theme(tmp_path: Path) -> Path:
    theme = tmp_path / "Theme1"
    theme.mkdir()
    (theme / "00.png").write_bytes(b"background")
    (theme / "01.png").write_bytes(b"mask")
    (theme / "Theme.png").write_bytes(b"preview")
    (theme / "config1.dc").write_bytes(b"original-must-stay-unchanged")
    (theme / "trcc.json").write_text(json.dumps({
        "name": "Theme1",
        "overlay_enabled": True,
        "elements": [
            {
                "type": "metric", "metric": "cpu:usage",
                "format": "CPU {value:.0f}%", "x": 120, "y": 220,
                "size": 36, "color": "#32c5ff", "bold": True,
            },
            {
                "type": "clock", "source": "time", "x": 800, "y": 80,
                "size": 44, "color": "#ffffff",
            },
        ],
    }), encoding="utf-8")
    return theme


def test_metric_label_and_live_value_are_one_indivisible_block(tmp_path: Path) -> None:
    layout, _config = load_editable_layout(sample_theme(tmp_path))
    cpu = layout.blocks[0]
    assert cpu.preview_text == "CPU 30%"

    renamed = cpu.with_edited_text("Prozessor")
    assert renamed.format == "Prozessor {value:.0f}%"
    assert renamed.preview_text == "Prozessor 30%"


def test_separate_trcc_cpu_gpu_labels_merge_with_usage_blocks(tmp_path: Path) -> None:
    layout = layout_from_config(tmp_path, {"elements": [
        {"type": "text", "text": "CPU", "x": 100, "y": 600, "size": 36},
        {
            "type": "metric", "metric": "cpu:usage", "format": "{value:.0f}%",
            "x": 500, "y": 600, "size": 36,
        },
        {"type": "text", "text": "GPU", "x": 100, "y": 100, "size": 36},
        {
            "type": "metric", "metric": "gpu:primary:usage", "format": "{value:.0f}%",
            "x": 500, "y": 100, "size": 36,
        },
    ]})
    assert len(layout.blocks) == 2
    assert [block.preview_text for block in layout.blocks] == ["CPU 30%", "GPU 42%"]
    assert [block.x for block in layout.blocks] == [100, 100]


def test_offsets_and_dragged_positions_are_bounded_away_from_cutout(tmp_path: Path) -> None:
    layout, _config = load_editable_layout(sample_theme(tmp_path))
    moved = EditableLayout(
        layout.source,
        (layout.blocks[0].bounded(), layout.blocks[1]),
        offset_x=2000,
        offset_y=-900,
    )
    elements = moved.to_trcc_elements(safe_right_x=1520)
    assert all(0 <= int(element["x"]) < 1520 for element in elements)
    assert all(0 <= int(element["y"]) < 720 for element in elements)


def test_overrides_round_trip_per_theme() -> None:
    block = LayoutBlock(
        "ohc-layer2-00", "metric", 123, 234,
        metric="gpu:primary:usage", format="GPU {value:.0f}%",
        color="#44d7b6", size=41,
    )
    layout = EditableLayout("/designs/Theme1", (block,), 12, -8)
    encoded = serialize_layout_overrides({layout.source: layout})
    decoded = deserialize_layout_overrides(encoded)
    assert decoded[layout.source] == layout


def test_staging_uses_json_and_symlinks_without_touching_original_dc(tmp_path: Path) -> None:
    theme = sample_theme(tmp_path)
    original_dc = (theme / "config1.dc").read_bytes()
    layout, config = load_editable_layout(theme)
    edited = layout.replace_block(
        layout.blocks[0].ident, x=333, color="#ff5500", size=52,
    )

    staged = stage_editable_theme(theme, tmp_path / "cache", edited, config)
    payload = json.loads((staged / "trcc.json").read_text(encoding="utf-8"))

    assert payload["elements"][0]["x"] == 333
    assert payload["elements"][0]["color"] == "#ff5500"
    assert payload["elements"][0]["size"] == 52
    assert (staged / "00.png").is_symlink()
    assert not (staged / "config1.dc").exists()
    assert (theme / "config1.dc").read_bytes() == original_dc


def test_staging_embeds_selected_video_and_generated_mask_for_one_theme_load(tmp_path: Path) -> None:
    theme = sample_theme(tmp_path)
    layout, config = load_editable_layout(theme)
    config.update({
        "mask": "/old/theme/mask.png",
        "mask_position": [1, 2],
        "mask_visible": False,
    })
    video = tmp_path / "selected-background.mp4"
    video.write_bytes(b"video")
    mask = tmp_path / "generated-panel-mask.png"
    mask.write_bytes(b"mask")

    staged = stage_editable_theme(
        theme, tmp_path / "cache", layout, config,
        background_video=video, mask_image=mask,
    )
    payload = json.loads((staged / "trcc.json").read_text(encoding="utf-8"))

    assert (staged / "Theme.mp4").is_symlink()
    assert (staged / "Theme.mp4").resolve() == video.resolve()
    assert (staged / "01.png").is_symlink()
    assert (staged / "01.png").resolve() == mask.resolve()
    assert payload["mask_position"] == [800, 360]
    assert payload["mask_visible"] is True
    assert "mask" not in payload


def test_layout_from_config_rejects_unknown_elements_and_bounds_values(tmp_path: Path) -> None:
    layout = layout_from_config(tmp_path, {"elements": [
        {"type": "unknown", "x": 5, "y": 5},
        {"type": "text", "text": "A" * 500, "x": -10, "y": 5000, "size": 999},
    ]})
    assert len(layout.blocks) == 1
    assert layout.blocks[0].x == 0
    assert layout.blocks[0].y == 719
    assert layout.blocks[0].size == 160
    assert len(layout.blocks[0].text) == 160


def test_malformed_element_does_not_drop_following_valid_blocks(tmp_path: Path) -> None:
    layout = layout_from_config(tmp_path, {"elements": [
        {"type": "text", "text": "first", "x": 10, "y": 20},
        "broken-record",
        {"type": "text", "text": "second", "x": 30, "y": 40},
    ]})

    assert [block.text for block in layout.blocks] == ["first", "second"]


def test_split_mode_policy_defaults_corrupt_values_to_safe_off() -> None:
    assert safe_split_mode(None) == 0
    assert safe_split_mode("broken") == 0
    assert safe_split_mode(-9) == 0
    assert safe_split_mode(9) == 3
    assert safe_split_mode("2") == 2
