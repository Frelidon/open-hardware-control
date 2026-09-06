from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thermalright_display import (
    DEFAULT_NOTCH_CORNER_RADIUS,
    DEFAULT_NOTCH_MASK_WIDTH,
    DEFAULT_OVERLAYS,
    LEVITA_CUTOUT_HEIGHT,
    LEVITA_CUTOUT_WIDTH,
    LEVITA_CUTOUT_X,
    LEVITA_HEIGHT,
    LEVITA_WIDTH,
    MEDIA_SCALE_CONTAIN,
    MEDIA_CATEGORY_LABELS,
    TRCC_CLOUD_CATEGORIES,
    MediaEntry,
    OverlaySpec,
    ThermalrightCli,
    adjust_rgb_intensity,
    bounded_layer_intensity,
    build_apply_sequence,
    clamp_overlay_outside_cutout,
    create_hardware_design_preview,
    create_layered_mask,
    create_black_notch_mask,
    deduplicate_media_entries,
    default_trcc_design_directory,
    media_category_key,
    media_catalog_sort_key,
    notch_safe_right_x,
    parse_detect_output,
    prepare_shifted_media,
    scan_media_directory,
    trcc_theme_is_supported,
)


def test_layer_intensity_is_bounded_and_changes_rgb() -> None:
    assert bounded_layer_intensity(5) == 25
    assert bounded_layer_intensity(190) == 150
    assert adjust_rgb_intensity("#204080", 50) == "#102040"
    assert adjust_rgb_intensity("#204080", 130) != "#204080"


def test_overlay_update_uses_daemon_safe_bounded_command() -> None:
    cli = ThermalrightCli("/usr/bin/trcc")
    args = cli.overlay_update_format_args("ohc-layer2-07", "GPU 1 MHz", show_unit=True)
    assert args[1:5] == ("display", "overlay-update", "87ad:70db", "ohc-layer2-07")
    assert args[-1] == "--show-unit"


def test_levita_geometry_keeps_exact_right_cutout() -> None:
    assert (LEVITA_WIDTH, LEVITA_HEIGHT) == (1600, 720)
    assert (LEVITA_CUTOUT_X, LEVITA_CUTOUT_WIDTH, LEVITA_CUTOUT_HEIGHT) == (1520, 80, 720)


def test_scan_imports_local_media_and_trcc_layouts_without_copying(tmp_path: Path) -> None:
    from PIL import Image

    video = tmp_path / "a001.mp4"
    video.write_bytes(b"local-test")
    theme = tmp_path / "Theme1"
    theme.mkdir()
    (theme / "config1.dc").write_bytes(b"\xdd")
    Image.new("RGB", (1600, 720)).save(theme / "Theme.png")
    (tmp_path / "download-report.csv").write_text("external,url\n", encoding="utf-8")

    entries = scan_media_directory(tmp_path)

    assert [(entry.relative_name, entry.kind) for entry in entries] == [
        ("Theme1 · TRCC-Layout", "theme"),
        ("a001.mp4", "video"),
    ]
    assert entries[1].path == video.resolve()


def test_broad_import_rejects_square_live_layout_but_keeps_levita_layout(tmp_path: Path) -> None:
    from PIL import Image

    square = tmp_path / "theme480480" / "a001"
    square.mkdir(parents=True)
    (square / "config1.dc").write_bytes(b"square")
    Image.new("RGB", (480, 480)).save(square / "Theme.png")
    levita = tmp_path / "theme1600720l" / "a002"
    levita.mkdir(parents=True)
    (levita / "config1.dc").write_bytes(b"landscape")
    Image.new("RGB", (1600, 720)).save(levita / "Theme.png")

    themes = [entry.path for entry in scan_media_directory(tmp_path) if entry.kind == "theme"]

    assert themes == [levita.resolve()]


def test_default_trcc_designs_use_only_verified_levita_landscape_geometry(tmp_path: Path) -> None:
    wrong = tmp_path / ".trcc" / "data" / "theme480480" / "Theme1"
    wrong.mkdir(parents=True)
    (wrong / "config1.dc").write_bytes(b"wrong geometry")
    (wrong / "Theme.png").write_bytes(b"png")
    assert default_trcc_design_directory(tmp_path) is None

    expected = tmp_path / ".trcc" / "data" / "theme1600720l"
    theme = expected / "Theme1"
    theme.mkdir(parents=True)
    (theme / "config1.dc").write_bytes(b"verified geometry")
    (theme / "00.png").write_bytes(b"png")
    assert default_trcc_design_directory(tmp_path) == expected.resolve()


def test_theme_discovery_rejects_symlinked_config_and_artwork(tmp_path: Path) -> None:
    from PIL import Image

    external_config = tmp_path / "external.dc"
    external_config.write_text("external", encoding="utf-8")
    external_artwork = tmp_path / "external.png"
    Image.new("RGB", (1600, 720)).save(external_artwork)

    import_root = tmp_path / "import"
    config_link_theme = import_root / "theme1600720l" / "config-link"
    config_link_theme.mkdir(parents=True)
    (config_link_theme / "config1.dc").symlink_to(external_config)
    Image.new("RGB", (1600, 720)).save(config_link_theme / "Theme.png")
    artwork_link_theme = import_root / "theme1600720l" / "artwork-link"
    artwork_link_theme.mkdir(parents=True)
    (artwork_link_theme / "config1.dc").write_text("local", encoding="utf-8")
    (artwork_link_theme / "Theme.png").symlink_to(external_artwork)

    assert not [entry for entry in scan_media_directory(import_root) if entry.kind == "theme"]

    installed = tmp_path / ".trcc" / "data" / "theme1600720l" / "linked"
    installed.mkdir(parents=True)
    (installed / "config1.dc").symlink_to(external_config)
    (installed / "Theme.png").symlink_to(external_artwork)
    assert default_trcc_design_directory(tmp_path) is None


def test_private_editable_theme_cache_accepts_linked_validated_artwork(tmp_path: Path) -> None:
    from PIL import Image

    source = tmp_path / "validated-source.png"
    Image.new("RGB", (1600, 720)).save(source)
    staged = tmp_path / "private-cache" / "editable-theme"
    staged.mkdir(parents=True)
    (staged / "00.png").symlink_to(source)
    (staged / "Theme.png").symlink_to(source)
    (staged / "trcc.json").write_text(
        json.dumps({"width": 1600, "height": 720, "elements": []}),
        encoding="utf-8",
    )

    assert trcc_theme_is_supported(staged)
    sequence = build_apply_sequence(
        ThermalrightCli("/usr/bin/trcc"),
        staged,
        DEFAULT_OVERLAYS,
        split_mode=0,
        hardware_design=staged,
    )
    assert any("load-theme" in command for command, _tolerated in sequence)
    assert not [entry for entry in scan_media_directory(tmp_path) if entry.kind == "theme"]


def test_scan_rejects_symlinked_media(tmp_path: Path) -> None:
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"media")
    linked = tmp_path / "linked.mp4"
    linked.symlink_to(outside)
    assert [entry.relative_name for entry in scan_media_directory(tmp_path)] == ["outside.mp4"]


def test_catalog_keeps_one_file_per_complete_case_insensitive_name(tmp_path: Path) -> None:
    normal = tmp_path / "TRCC-Themes" / "bj1600720l" / "d002.mp4"
    backup = tmp_path / "Display sicherung" / "alt" / "bj1600720l" / "D002.MP4"
    renamed = tmp_path / "Display sicherung" / "bj1600720l" / "d002-copy.mp4"
    still = tmp_path / "web" / "d002.png"
    for path in (normal, backup, renamed, still):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"media")
    entries = [
        MediaEntry(backup.resolve(), "Display sicherung/alt/bj1600720l/D002.MP4", "video"),
        MediaEntry(normal.resolve(), "TRCC-Themes/bj1600720l/d002.mp4", "video"),
        MediaEntry(renamed.resolve(), "Display sicherung/bj1600720l/d002-copy.mp4", "video"),
        MediaEntry(still.resolve(), "web/d002.png", "image"),
    ]

    retained, replacements = deduplicate_media_entries(entries)

    assert [entry.path.name for entry in retained] == ["d002.mp4", "d002-copy.mp4", "d002.png"]
    assert replacements == {backup.resolve(): normal.resolve()}


def test_detect_parser_is_exact_and_case_insensitive() -> None:
    assert parse_detect_output("[1] 87AD:70DB Thermalright LCD")
    assert parse_detect_output("device=87ad : 70db")
    assert not parse_detect_output("87ad:70dc")


def test_overlay_is_clamped_outside_physical_cutout() -> None:
    unsafe = OverlaySpec(
        "ohc-test", "Test", "metric", "cpu:temp",
        sample="CPU 99 °C", x=1599, y=900, size=60,
    )
    safe = clamp_overlay_outside_cutout(unsafe, estimated_width=300)
    assert safe.x + 150 < LEVITA_CUTOUT_X
    assert safe.y == LEVITA_HEIGHT - 1


def test_default_notch_mask_matches_the_rounded_80_px_levita_edge(tmp_path: Path) -> None:
    from PIL import Image
    from modules.lcd_levita.v1_4.panel_geometry import DEFAULT_INNER_CORNER_RADIUS

    mask = create_black_notch_mask(tmp_path, DEFAULT_NOTCH_MASK_WIDTH)
    with Image.open(mask) as image:
        assert image.size == (LEVITA_WIDTH, LEVITA_HEIGHT)
        assert image.getpixel((0, 0)) == (0, 0, 0, 0)
        assert image.getpixel((LEVITA_WIDTH - 1, 0)) == (0, 0, 0, 0)
        assert image.getpixel((LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH, 0)) == (0, 0, 0, 255)
        assert image.getpixel((LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH - DEFAULT_INNER_CORNER_RADIUS, 0)) == (0, 0, 0, 255)
        assert image.getpixel((LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH - DEFAULT_INNER_CORNER_RADIUS - 1, 0)) == (0, 0, 0, 0)
        assert image.getpixel((LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH - 1, LEVITA_HEIGHT // 2)) == (0, 0, 0, 0)
        assert image.getpixel((LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH, DEFAULT_NOTCH_CORNER_RADIUS)) == (0, 0, 0, 255)
        assert image.getpixel((LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH, LEVITA_HEIGHT - 1)) == (0, 0, 0, 255)
        assert image.getpixel((LEVITA_WIDTH - 1 - DEFAULT_NOTCH_CORNER_RADIUS, 0)) == (0, 0, 0, 255)
        assert image.getpixel((LEVITA_WIDTH - 1, LEVITA_HEIGHT // 2)) == (0, 0, 0, 255)
        assert image.getpixel((LEVITA_WIDTH - 1, LEVITA_HEIGHT - 1)) == (0, 0, 0, 0)
    assert notch_safe_right_x(DEFAULT_NOTCH_MASK_WIDTH) == 1520


def test_right_image_corner_radii_can_be_independent(tmp_path: Path) -> None:
    from PIL import Image

    mask = create_black_notch_mask(
        tmp_path,
        DEFAULT_NOTCH_MASK_WIDTH,
        top_radius=72,
        bottom_radius=24,
    )
    boundary = LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH
    with Image.open(mask) as image:
        assert image.getpixel((boundary - 72, 0)) == (0, 0, 0, 255)
        assert image.getpixel((boundary - 73, 0)) == (0, 0, 0, 0)
        assert image.getpixel((boundary - 24, LEVITA_HEIGHT - 1)) == (0, 0, 0, 255)
        assert image.getpixel((boundary - 25, LEVITA_HEIGHT - 1)) == (0, 0, 0, 0)
        assert image.getpixel((boundary - 1, LEVITA_HEIGHT // 2)) == (0, 0, 0, 0)


def test_prepared_image_keeps_a_straight_inner_notch_and_rounded_outer_corners(tmp_path: Path) -> None:
    from PIL import Image

    from modules.lcd_levita.v1_4.panel_geometry import pixel_is_outside_levita_panel

    source = tmp_path / "panel.png"
    Image.new("RGB", (1600, 720), (12, 80, 160)).save(source)
    prepared = prepare_shifted_media(source, tmp_path / "cache")
    with Image.open(prepared.path) as image:
        assert image.getpixel((LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH, 0)) == (12, 80, 160)
        assert image.getpixel((LEVITA_WIDTH - 1, LEVITA_HEIGHT // 2)) == (12, 80, 160)
        assert image.getpixel((LEVITA_WIDTH - 1, 0)) == (0, 0, 0)
        assert image.getpixel((LEVITA_WIDTH - 1, LEVITA_HEIGHT - 1)) == (0, 0, 0)
        assert pixel_is_outside_levita_panel(LEVITA_WIDTH - 1, 0)
        assert not pixel_is_outside_levita_panel(LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH, 0)


def test_shifted_image_is_a_cached_copy_and_keeps_original(tmp_path: Path) -> None:
    from PIL import Image

    source = tmp_path / "source.png"
    Image.new("RGB", (1600, 720), (255, 0, 0)).save(source)
    prepared = prepare_shifted_media(source, tmp_path / "cache", offset_x=-160)
    assert prepared.transformed
    assert prepared.path != source
    with Image.open(prepared.path) as image:
        assert image.getpixel((0, 100)) == (255, 0, 0)
        assert image.getpixel((1599, 100)) == (0, 0, 0)
    with Image.open(source) as original:
        assert original.getpixel((1599, 100)) == (255, 0, 0)


def test_media_is_always_scaled_to_levita_without_distortion(tmp_path: Path) -> None:
    from PIL import Image

    source = tmp_path / "square.png"
    Image.new("RGB", (100, 100), (255, 20, 30)).save(source)
    prepared = prepare_shifted_media(
        source, tmp_path / "cache", scale_mode=MEDIA_SCALE_CONTAIN,
    )
    assert prepared.transformed
    with Image.open(prepared.path) as image:
        assert image.size == (1600, 720)
        assert image.getpixel((800, 360)) == (255, 20, 30)
        assert image.getpixel((10, 360)) == (0, 0, 0)


@pytest.mark.parametrize(
    ("name", "category"),
    [
        ("A001.mp4", "a"),
        ("d019.zt", "d"),
        ("Y010-extra.mp4", "y"),
        ("a083.mp4", "own"),
        ("d-019.zt", "own"),
        ("my-video.mp4", "own"),
    ],
)
def test_local_theme_prefixes_are_grouped(name: str, category: str, tmp_path: Path) -> None:
    assert media_category_key(MediaEntry(tmp_path / name, name, "video")) == category


def test_trcc_categories_match_the_upstream_catalog_exactly(tmp_path: Path) -> None:
    assert TRCC_CLOUD_CATEGORIES == (
        ("a", "Gallery", 82),
        ("b", "Tech", 25),
        ("c", "HUD", 72),
        ("d", "Light", 55),
        ("e", "Nature", 54),
        ("y", "Aesthetic", 10),
    )
    assert [MEDIA_CATEGORY_LABELS[key] for key in "abcdey"] == [
        "Gallery", "Tech", "HUD", "Light", "Nature", "Aesthetic",
    ]
    entries = [
        MediaEntry(tmp_path / "b010.mp4", "b010.mp4", "video"),
        MediaEntry(tmp_path / "a082.mp4", "a082.mp4", "video"),
        MediaEntry(tmp_path / "a002.mp4", "a002.mp4", "video"),
    ]
    assert [entry.relative_name for entry in sorted(entries, key=media_catalog_sort_key)] == [
        "a002.mp4", "a082.mp4", "b010.mp4",
    ]


def test_cli_builds_bounded_shell_free_commands(tmp_path: Path) -> None:
    media = tmp_path / "design name.mp4"
    media.write_bytes(b"video")
    cli = ThermalrightCli("/usr/bin/trcc")
    sequence = build_apply_sequence(cli, media, DEFAULT_OVERLAYS, split_mode=9)

    assert sequence[0] == ((
        "/usr/bin/trcc", "device", "disconnect", "87ad:70db",
    ), True)
    assert sequence[1] == ((
        "/usr/bin/trcc", "device", "connect", "87ad:70db",
    ), False)
    assert sequence[2][0] == (
        "/usr/bin/trcc", "display", "split-mode", "87ad:70db", "0",
    )
    assert sequence[3][0] == (
        "/usr/bin/trcc", "display", "load-video", "87ad:70db", str(media.resolve()),
    )
    assert not any(
        command[-1] != "0"
        for command, _tolerated in sequence
        if "split-mode" in command
    )
    assert any("--show-unit" in command for command, _tolerated in sequence)
    assert not any("--hide-unit" in command for command, _tolerated in sequence)
    assert all(isinstance(command, tuple) for command, _tolerated in sequence)
    assert not any("sh" == part for command, _tolerated in sequence for part in command)
    gpu = next(command for command, _tolerated in sequence if "ohc-gpu-temp" in command and "overlay-add" in command)
    assert "gpu:primary:temp" in gpu
    assert "GPU {value:.0f}°C" in gpu


def test_levita_brightness_and_orientation_are_bounded_real_trcc_commands(tmp_path: Path) -> None:
    media = tmp_path / "design.png"
    media.write_bytes(b"image")
    cli = ThermalrightCli("/usr/bin/trcc")
    sequence = build_apply_sequence(
        cli, media, DEFAULT_OVERLAYS, split_mode=0,
        brightness=140, orientation=270,
    )
    commands = [command for command, _tolerated in sequence]
    assert commands[3] == (
        "/usr/bin/trcc", "display", "set-brightness", "87ad:70db", "100",
    )
    assert commands[4] == (
        "/usr/bin/trcc", "display", "set-orientation", "87ad:70db", "270",
    )
    with pytest.raises(ValueError, match="Ausrichtung"):
        cli.orientation_args(45)


def test_apply_sequence_loads_real_mask_before_metrics(tmp_path: Path) -> None:
    media = tmp_path / "design.png"
    media.write_bytes(b"image")
    mask = tmp_path / "mask.png"
    mask.write_bytes(b"mask")
    cli = ThermalrightCli("/usr/bin/trcc")
    sequence = build_apply_sequence(
        cli, media, DEFAULT_OVERLAYS, split_mode=0,
        mask_path=mask, safe_right_x=1280,
    )
    commands = [command for command, _tolerated in sequence]
    assert commands[:7] == [
        ("/usr/bin/trcc", "device", "disconnect", "87ad:70db"),
        ("/usr/bin/trcc", "device", "connect", "87ad:70db"),
        ("/usr/bin/trcc", "display", "split-mode", "87ad:70db", "0"),
        ("/usr/bin/trcc", "display", "load-image", "87ad:70db", str(media.resolve())),
        ("/usr/bin/trcc", "display", "apply-mask", "87ad:70db", str(mask.resolve())),
        ("/usr/bin/trcc", "display", "mask-position", "87ad:70db", "0", "0"),
        ("/usr/bin/trcc", "display", "mask-visible", "87ad:70db", "on"),
    ]
    metric_commands = [command for command in commands if "overlay-add" in command]
    assert metric_commands
    assert all(int(command[command.index("--x") + 1]) < 1280 for command in metric_commands)


def test_two_layer_sequence_keeps_theme_layout_and_replaces_only_video_background(tmp_path: Path) -> None:
    video = tmp_path / "background.mp4"
    video.write_bytes(b"video")
    design = tmp_path / "HardwareDesign"
    design.mkdir()
    (design / "config1.dc").write_bytes(b"\xdd")
    (design / "Theme.png").write_bytes(b"preview")
    cli = ThermalrightCli("/usr/bin/trcc")

    sequence = build_apply_sequence(
        cli,
        video,
        DEFAULT_OVERLAYS,
        split_mode=0,
        hardware_design=design,
    )
    commands = [command for command, _tolerated in sequence]

    assert commands[:5] == [
        ("/usr/bin/trcc", "device", "disconnect", "87ad:70db"),
        ("/usr/bin/trcc", "device", "connect", "87ad:70db"),
        ("/usr/bin/trcc", "display", "split-mode", "87ad:70db", "0"),
        ("/usr/bin/trcc", "display", "load-theme", "87ad:70db", str(design.resolve())),
        ("/usr/bin/trcc", "display", "play-video", "87ad:70db", str(video.resolve())),
    ]
    assert not any("overlay-add" in command for command in commands)
    assert commands[-1] == (
        "/usr/bin/trcc", "display", "overlay", "87ad:70db", "on",
    )


def test_complete_standard_design_can_be_loaded_directly_with_its_saved_values(tmp_path: Path) -> None:
    design = tmp_path / "Theme1"
    design.mkdir()
    (design / "config1.dc").write_bytes(b"saved live values")
    (design / "Theme.png").write_bytes(b"preview")
    sequence = build_apply_sequence(
        ThermalrightCli("/usr/bin/trcc"),
        design,
        DEFAULT_OVERLAYS,
        split_mode=0,
        hardware_design=design,
    )
    commands = [command for command, _tolerated in sequence]
    assert commands[:4] == [
        ("/usr/bin/trcc", "device", "disconnect", "87ad:70db"),
        ("/usr/bin/trcc", "device", "connect", "87ad:70db"),
        ("/usr/bin/trcc", "display", "split-mode", "87ad:70db", "0"),
        ("/usr/bin/trcc", "display", "load-theme", "87ad:70db", str(design.resolve())),
    ]
    assert not any("play-video" in command for command in commands)
    assert not any("overlay-add" in command for command in commands)
    assert commands[-1] == (
        "/usr/bin/trcc", "display", "overlay", "87ad:70db", "on",
    )


def test_editable_native_json_cache_is_a_complete_hardware_design(tmp_path: Path) -> None:
    design = tmp_path / "editable-themes" / "theme-3d6236e94bad47b2aaff04f8"
    design.mkdir(parents=True)
    (design / "01.png").write_bytes(b"artwork")
    (design / "trcc.json").write_text(
        json.dumps({
            "name": "OHC editable",
            "width": 1600,
            "height": 720,
            "elements": [{
                "type": "metric", "metric": "cpu:usage",
                "format": "CPU {value:.0f}%", "x": 120, "y": 220,
            }],
        }),
        encoding="utf-8",
    )

    sequence = build_apply_sequence(
        ThermalrightCli("/usr/bin/trcc"),
        design,
        DEFAULT_OVERLAYS,
        split_mode=0,
        hardware_design=design,
        replace_hardware_background=False,
    )
    commands = [command for command, _tolerated in sequence]
    assert commands[3] == (
        "/usr/bin/trcc", "display", "load-theme", "87ad:70db", str(design.resolve()),
    )
    assert sum("load-theme" in command for command in commands) == 1
    assert not any("play-video" in command for command in commands)
    assert not any("apply-mask" in command for command in commands)
    assert not (design / "config1.dc").exists()


def test_native_json_theme_rejects_invalid_or_wrong_geometry(tmp_path: Path) -> None:
    design = tmp_path / "editable-theme"
    design.mkdir()
    (design / "01.png").write_bytes(b"artwork")
    (design / "trcc.json").write_text('{"width":480,"height":480,"elements":[]}', encoding="utf-8")
    with pytest.raises(ValueError, match="Hardwaredesign"):
        build_apply_sequence(
            ThermalrightCli("/usr/bin/trcc"), design, DEFAULT_OVERLAYS,
            split_mode=0, hardware_design=design,
        )


def test_two_layer_mode_rejects_non_video_background(tmp_path: Path) -> None:
    image = tmp_path / "background.png"
    image.write_bytes(b"image")
    design = tmp_path / "HardwareDesign"
    design.mkdir()
    (design / "config1.dc").write_bytes(b"\xdd")
    (design / "Theme.png").write_bytes(b"preview")
    with pytest.raises(ValueError, match="Hintergrundvideo"):
        build_apply_sequence(
            ThermalrightCli("/usr/bin/trcc"), image, DEFAULT_OVERLAYS,
            split_mode=0, hardware_design=design,
        )


def test_layered_mask_preserves_theme_art_and_rounded_levita_bar(tmp_path: Path) -> None:
    from PIL import Image

    design = tmp_path / "HardwareDesign"
    design.mkdir()
    theme_mask = Image.new("RGBA", (LEVITA_WIDTH, LEVITA_HEIGHT), (0, 0, 0, 0))
    theme_mask.putpixel((120, 650), (20, 40, 60, 210))
    theme_mask.save(design / "01.png")

    combined_path = create_layered_mask(
        tmp_path / "cache",
        hardware_design=design,
        notch_width=DEFAULT_NOTCH_MASK_WIDTH,
        notch_visible=True,
    )
    assert combined_path is not None
    with Image.open(combined_path) as combined:
        assert combined.getpixel((120, 650)) == (20, 40, 60, 210)
        assert combined.getpixel((LEVITA_WIDTH - 1, LEVITA_HEIGHT // 2)) == (0, 0, 0, 255)
        assert combined.getpixel((LEVITA_WIDTH - 1, 0))[3] == 0
        assert combined.getpixel((LEVITA_WIDTH - DEFAULT_NOTCH_MASK_WIDTH, 0))[3] == 255


def test_hardware_design_preview_extracts_upper_layer_from_theme_composite(tmp_path: Path) -> None:
    from PIL import Image

    design = tmp_path / "HardwareDesign"
    design.mkdir()
    Image.new("RGBA", (40, 20), (10, 20, 30, 255)).save(design / "00.png")
    preview = Image.new("RGBA", (40, 20), (10, 20, 30, 255))
    preview.putpixel((8, 9), (255, 255, 255, 255))
    preview.save(design / "Theme.png")

    extracted = create_hardware_design_preview(design, tmp_path / "cache")
    assert extracted is not None
    with Image.open(extracted) as layer:
        assert layer.getpixel((0, 0))[3] == 0
        assert layer.getpixel((8, 9))[3] > 0


def test_cli_runner_never_uses_shell() -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, "trcc 9.9.4\n", "")

    result = ThermalrightCli("/usr/bin/trcc", runner=runner).run("--version")
    assert result.ok
    assert calls[0][0] == ["/usr/bin/trcc", "--version"]
    assert "shell" not in calls[0][1]
    assert calls[0][1]["check"] is False


def test_shutdown_stop_video_uses_bounded_offscreen_daemon_request() -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, "video stopped\n", "")

    result = ThermalrightCli("/usr/bin/trcc", runner=runner).stop_video_now(timeout=99)

    assert result.ok
    assert calls[0][0] == [
        "/usr/bin/trcc", "display", "stop-video", "87ad:70db",
    ]
    assert calls[0][1]["timeout"] == 3.0
    assert calls[0][1]["env"]["TRCC_DAEMON"] == "1"
    assert calls[0][1]["env"]["QT_QPA_PLATFORM"] == "offscreen"
    assert "shell" not in calls[0][1]


def test_unknown_overlay_identifier_is_rejected() -> None:
    cli = ThermalrightCli("/usr/bin/trcc")
    with pytest.raises(ValueError):
        cli.overlay_delete_args("../../foreign")
