#!/usr/bin/env python3
"""Regression tests for safe Levita FPS and game-mode policy."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.levita_performance.v1_1 import (  # noqa: E402
    GAME_ACTIVITY_POLL_MS,
    GameSignals,
    fallback_lcd_fps,
    normalize_lcd_fps,
    normalize_process_names,
    parse_gamemode_status,
    process_game_signal,
    resolve_game_activity,
)


def test_15_fps_is_safe_default_and_60_requires_explicit_unlock() -> None:
    assert normalize_lcd_fps(None) == 15
    assert normalize_lcd_fps(60) == 15
    assert normalize_lcd_fps(60, experimental_60=True) == 60
    assert normalize_lcd_fps(30) == 30
    assert [fallback_lcd_fps(value) for value in (60, 30, 24, 20, 15)] == [30, 20, 20, 15, 15]


def test_game_signals_do_not_use_load_heuristics() -> None:
    assert GAME_ACTIVITY_POLL_MS == 10_000
    assert parse_gamemode_status("gamemode is active", 0)
    assert not parse_gamemode_status("gamemode is inactive", 0)
    assert not parse_gamemode_status("gamemode is active", 1)
    configured = normalize_process_names("/games/MyGame, wine64-preloader; bad name")
    assert configured == ("mygame", "wine64-preloader")
    assert process_game_signal(("plasmashell", "gamescope"), configured) == (True, "Gamescope")
    active, reason = process_game_signal(("mygame",), configured)
    assert active and "mygame" in reason
    assert resolve_game_activity(GameSignals(manual=True)) == (True, "Manuell")
    assert resolve_game_activity(GameSignals(gamemode=True)) == (True, "Feral GameMode")
    assert resolve_game_activity(GameSignals()) == (False, "Desktop")


def test_motion_assets_are_layer2_only_and_reproducibly_present() -> None:
    designs = ROOT / "src/assets/levita-designs"
    for name in (
        "ohc-spectrum-ring", "ohc-neon-double-arc", "ohc-prism-segments", "ohc-aurora-radar",
    ):
        video = designs / name / "motion.mp4"
        assert video.is_file() and video.stat().st_size > 100_000
    catalog = (ROOT / "src/modules/display_effects/v1_11/catalog.py").read_text(encoding="utf-8")
    assert '"ohc-spectrum-motion", "abstract"' not in catalog
