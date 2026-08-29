from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from thermalright_display import (
    DEFAULT_OVERLAYS,
    LEVITA_CUTOUT_HEIGHT,
    LEVITA_CUTOUT_WIDTH,
    LEVITA_CUTOUT_X,
    LEVITA_HEIGHT,
    LEVITA_WIDTH,
    OverlaySpec,
    ThermalrightCli,
    build_apply_sequence,
    clamp_overlay_outside_cutout,
    parse_detect_output,
    scan_media_directory,
)


def test_levita_geometry_keeps_exact_right_cutout() -> None:
    assert (LEVITA_WIDTH, LEVITA_HEIGHT) == (1600, 720)
    assert (LEVITA_CUTOUT_X, LEVITA_CUTOUT_WIDTH, LEVITA_CUTOUT_HEIGHT) == (1520, 80, 720)


def test_scan_imports_local_media_and_trcc_layouts_without_copying(tmp_path: Path) -> None:
    video = tmp_path / "a001.mp4"
    video.write_bytes(b"local-test")
    theme = tmp_path / "Theme1"
    theme.mkdir()
    (theme / "config1.dc").write_bytes(b"\xdd")
    (theme / "Theme.png").write_bytes(b"png")
    (tmp_path / "download-report.csv").write_text("external,url\n", encoding="utf-8")

    entries = scan_media_directory(tmp_path)

    assert [(entry.relative_name, entry.kind) for entry in entries] == [
        ("Theme1 · TRCC-Layout", "theme"),
        ("a001.mp4", "video"),
    ]
    assert entries[1].path == video.resolve()


def test_scan_rejects_symlinked_media(tmp_path: Path) -> None:
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"media")
    linked = tmp_path / "linked.mp4"
    linked.symlink_to(outside)
    assert [entry.relative_name for entry in scan_media_directory(tmp_path)] == ["outside.mp4"]


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


def test_cli_builds_bounded_shell_free_commands(tmp_path: Path) -> None:
    media = tmp_path / "design name.mp4"
    media.write_bytes(b"video")
    cli = ThermalrightCli("/usr/bin/trcc")
    sequence = build_apply_sequence(cli, media, DEFAULT_OVERLAYS, split_mode=9)

    assert sequence[0][0] == (
        "/usr/bin/trcc", "display", "split-mode", "87ad:70db", "0",
    )
    assert sequence[1][0] == (
        "/usr/bin/trcc", "display", "load-video", "87ad:70db", str(media.resolve()),
    )
    assert not any(
        command[-1] != "0"
        for command, _tolerated in sequence
        if "split-mode" in command
    )
    assert all(isinstance(command, tuple) for command, _tolerated in sequence)
    assert not any("sh" == part for command, _tolerated in sequence for part in command)
    gpu = next(command for command, _tolerated in sequence if "ohc-gpu-temp" in command and "overlay-add" in command)
    assert "gpu:primary:temp" in gpu
    assert "GPU {value:.0f}°C" in gpu


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


def test_unknown_overlay_identifier_is_rejected() -> None:
    cli = ThermalrightCli("/usr/bin/trcc")
    with pytest.raises(ValueError):
        cli.overlay_delete_args("../../foreign")
