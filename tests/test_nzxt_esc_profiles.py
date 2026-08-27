from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nzxt_esc_profiles import (
    LcdProfileStore,
    canonical_metric,
    clone_profile,
    import_nzxt_esc_file,
    import_nzxt_esc_payload,
    ohc_default_profile,
    render_profile,
    restore_import_original,
    update_metric,
)


def sample_payload() -> dict:
    return {
        "schemaVersion": 3,
        "exportedAt": "2026-08-24T17:00:00Z",
        "appVersion": "test",
        "presetName": "ALL TESTS",
        "background": {
            "url": "https://example.invalid/background.mp4",
            "settings": {
                "resolution": "640x640",
                "backgroundColor": "#101820",
                "scale": 1,
                "x": 0,
                "y": 0,
                "fit": "cover",
                "align": "center",
            },
        },
        "overlay": {
            "mode": "custom",
            "elements": [
                {"id": "metric", "type": "metric", "x": -100, "y": -50, "data": {"metric": "cpuTemp", "numberColor": "#ffffff", "numberSize": 120, "textColor": "#00aaff", "textSize": 30}},
                {"id": "label", "type": "text", "x": -100, "y": 70, "data": {"text": "CPU", "textColor": "#ffffff", "textSize": 30}},
                {"id": "divider", "type": "divider", "x": 0, "y": 0, "angle": 10, "data": {"width": 4, "height": 180, "color": "#556677"}},
                {"id": "clock", "type": "clock", "x": 100, "y": -60, "data": {"format": "HH:mm", "mode": "24h", "fontSize": 55, "color": "#ffffff", "font": "digital"}},
                {"id": "date", "type": "date", "x": 100, "y": 70, "data": {"format": "DD.MM.YYYY", "fontSize": 28, "color": "#aaaaaa"}},
                {"id": "future", "type": "audioVisualizer", "x": 0, "y": 0, "data": {}},
            ],
            "zOrder": ["divider", "metric", "label", "clock", "date", "future"],
        },
    }


def test_schema3_import_and_mandatory_report(tmp_path: Path) -> None:
    path = tmp_path / "ALL-IN-ONE.nzxt-esc-preset.json"
    path.write_text(json.dumps(sample_payload()), encoding="utf-8")
    result = import_nzxt_esc_file(path)
    assert result.profile["source"]["schemaVersion"] == 3
    assert result.profile["source"]["sha256"]
    assert [layer["id"] for layer in result.profile["layers"]] == ["divider", "metric", "label", "clock", "date", "future"]
    assert result.counts["blocked"] == 1  # remote background
    assert result.counts["unsupported"] == 1  # future/audio visualizer
    assert result.counts["approximate"] >= 2  # background transform + digital font/date
    assert result.profile["layers"][-1]["visible"] is False


def test_alias_metrics_and_user_sensor_change_auto_label() -> None:
    payload = sample_payload()
    payload["overlay"]["elements"][0]["data"] = {
        "sourceMetric": "cpu_temp",
        "numberColor": "#fff",
        "numberSize": 100,
        "textColor": "#fff",
        "textSize": 30,
    }
    result = import_nzxt_esc_payload(payload)
    assert result.profile["layers"][1]["data"]["metric"] == "cpuTemp"  # z-order puts divider first
    assert canonical_metric("gpu_temp") == "gpuTemp"
    assert update_metric(result.profile, "metric", "gpuTemp", auto_label=True)
    metric_layer = next(layer for layer in result.profile["layers"] if layer["id"] == "metric")
    label_layer = next(layer for layer in result.profile["layers"] if layer["id"] == "label")
    assert metric_layer["data"]["metric"] == "gpuTemp"
    assert label_layer["data"]["text"] == "GPU"


def test_clone_and_restore_original_are_independent() -> None:
    profile = import_nzxt_esc_payload(sample_payload()).profile
    copied = clone_profile(profile)
    assert copied["id"] != profile["id"]
    assert copied["name"].endswith("Kopie")
    next(layer for layer in copied["layers"] if layer["id"] == "label")["data"]["text"] = "EDITED"
    restored = restore_import_original(copied)
    assert next(layer for layer in restored["layers"] if layer["id"] == "label")["data"]["text"] == "CPU"


def test_renderer_creates_240_square_without_network(tmp_path: Path) -> None:
    profile = import_nzxt_esc_payload(sample_payload()).profile
    image = render_profile(
        profile,
        {"cpuTemp": 55, "gpuTemp": 61, "liquidTemp": 32, "cpuLoad": 45, "gpuLoad": 77},
    )
    assert image.size == (240, 240)
    target = tmp_path / "preview.png"
    image.save(target)
    assert target.stat().st_size > 500


def test_profile_store_export_backup_restore(tmp_path: Path) -> None:
    store = LcdProfileStore(tmp_path / "profiles")
    profile = ohc_default_profile()
    store.save([profile])
    assert len(store.load()) == 1

    exported = store.export_profile(profile, tmp_path / "one.ohc-lcd-profile.json")
    imported = store.import_ohc_profile(exported)
    assert imported["id"] != profile["id"]

    preview = store.write_preview(profile, {"cpuTemp": 50, "gpuTemp": 60, "liquidTemp": 30})
    assert preview.is_file()
    backup = store.backup([profile], tmp_path / "backup.ohc-lcd-backup.zip")
    restored, stats = store.restore_backup(backup)
    assert len(restored) == 1
    assert restored[0]["id"] != profile["id"]
    assert stats["profiles"] == 1


def current_v3_payload() -> dict:
    # Minimal reproduction of the current NZXT-ESC v6 schema-v3 layout used by
    # real exports: data live under preset/, transforms are normalized and the
    # exporter embeds a rendered previewImage at root.
    import base64
    import io
    from PIL import Image as PILImage

    preview = PILImage.new("RGB", (128, 128), (18, 44, 90))
    buffer = io.BytesIO()
    preview.save(buffer, format="PNG")
    preview_uri = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    return {
        "schemaVersion": 3,
        "exportedAt": "2026-08-24T17:35:13.926Z",
        "app": {"name": "NZXT-ESC-DEV", "version": "v6.08.20"},
        "preset": {
            "id": "preset-current",
            "name": "Current Reactor",
            "background": {
                "base": {"sourceType": "color", "color": "#000000"},
                "mediaOverlay": {
                    "kind": "media-overlay",
                    "source": "url",
                    "media": {"type": "url", "url": "https://example.invalid/reactor.mp4"},
                    "transform": {"scale": 0.92, "offsetX": 0, "offsetY": 0},
                },
            },
            "overlay": {
                "enabled": True,
                "elements": [
                    {"id": "shape", "elementType": "shape", "transform": {"x": 0, "y": 0, "rotateDeg": 0}, "config": {"width": 200, "height": 200, "radius": 100, "fillColor": "rgba(2,2,2,0.72)", "borderColor": "#ffffff", "borderWidth": 1}, "visibility": "always"},
                    {"id": "metric", "elementType": "metric", "transform": {"x": 0.4, "y": -0.5, "rotateDeg": 0}, "config": {"metricType": "cpu_temp", "color": "#ffffff", "fontSize": 70}, "visibility": "always"},
                    {"id": "label", "elementType": "text", "transform": {"x": -0.4, "y": -0.6, "rotateDeg": 0}, "config": {"content": "CPU", "color": "#ffffff", "fontSize": 33}, "visibility": "always"},
                    {"id": "arc", "elementType": "radial_graphic", "transform": {"x": 0, "y": 0, "rotateDeg": 0}, "config": {"sourceMetric": "cpu_load", "strokeWidth": 10, "totalAngle": 180, "size": 500, "strokeColor": "#00e5ff", "trackEnabled": True}, "visibility": "always"},
                    {"id": "audio", "elementType": "audio_visualizer", "transform": {"x": 0, "y": 0.8, "rotateDeg": 0}, "config": {}, "visibility": "musicOnly"},
                ],
            },
            "previewImageId": "preview_current",
        },
        "previewImage": preview_uri,
    }


def test_current_v3_nested_layout_is_not_imported_as_black_empty_profile() -> None:
    result = import_nzxt_esc_payload(current_v3_payload())
    assert result.profile["name"] == "Current Reactor"
    assert result.profile["source"]["currentV3Layout"] is True
    assert result.profile["source"]["appVersion"] == "v6.08.20"
    layers = {layer["id"]: layer for layer in result.profile["layers"]}
    assert layers["metric"]["data"]["metric"] == "cpuTemp"
    assert layers["metric"]["x"] == 128.0  # 0.4 * 640 / 2
    assert layers["metric"]["y"] == -160.0
    assert layers["shape"]["type"] == "shape"
    assert layers["arc"]["type"] == "radial_graphic"
    assert layers["audio"]["visible"] is False
    assert result.profile["canvas"]["background"]["previewData"].startswith("data:image/png;base64,")
    assert result.counts["blocked"] >= 1  # remote media is never fetched
    assert canonical_metric("ram_usage") == "ramLoad"
    # Browser-style fractional rgba colours from current exports stay intact
    # instead of silently becoming the old fallback colour.
    assert layers["shape"]["data"]["fillColor"] == "#020202b8"


def test_current_v3_renderer_and_embedded_preview_are_visible() -> None:
    from nzxt_esc_profiles import render_import_preview

    result = import_nzxt_esc_payload(current_v3_payload())
    preview = render_import_preview(result.profile, {"cpuTemp": 55, "cpuLoad": 66})
    assert preview.size == (240, 240)
    assert preview.getbbox() is not None
    rendered = render_profile(result.profile, {"cpuTemp": 55, "cpuLoad": 66})
    assert rendered.size == (240, 240)
    # The current-schema element conversion must produce visible non-black data.
    extrema = rendered.convert("L").getextrema()
    assert extrema[1] > 0


def test_renderer_supports_dynamic_target_resolution_and_global_scale() -> None:
    profile = import_nzxt_esc_payload(current_v3_payload()).profile
    profile["renderScalePercent"] = 135
    image = render_profile(profile, {"cpuTemp": 55, "cpuLoad": 66}, target_resolution=(640, 640))
    assert image.size == (640, 640)
    assert image.convert("L").getextrema()[1] > 0


def test_remote_media_uses_embedded_preview_as_live_background() -> None:
    profile = import_nzxt_esc_payload(current_v3_payload()).profile
    image = render_profile(profile, {"cpuTemp": 55, "cpuLoad": 66})
    # Embedded preview is blue-ish; if it were ignored the flat black base would dominate.
    center = image.getpixel((120, 120))
    assert max(center) > 20
