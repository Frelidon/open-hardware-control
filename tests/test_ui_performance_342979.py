#!/usr/bin/env python3
"""Regression coverage for lightweight transitions and the bounded SSD cache."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.rgb_studio.v1_15.ene_start_recovery import EneDramStartRecoveryMixin  # noqa: E402
from modules.ui_performance.v1_1.cache import (  # noqa: E402
    cache_budget_mb,
    cached_catalog_records,
    preview_cache_path,
    save_catalog_records,
)
from modules.ui_performance.v1_1.maintenance import trim_cache  # noqa: E402
from modules.ui_performance.v1_1.memory import release_idle_memory  # noqa: E402


class Settings:
    def __init__(self, value: object) -> None:
        self.raw = value

    def value(self, _key: str, default: object) -> object:
        return self.raw if self.raw is not None else default


class Timer:
    def __init__(self) -> None:
        self.started: list[int] = []

    def start(self, delay: int) -> None:
        self.started.append(delay)

    def stop(self) -> None:
        return


class Device:
    index = 1


class Recovery(EneDramStartRecoveryMixin):
    openrgb_write_enabled = True
    openrgb_server_reachable = True
    openrgb_external_server_detected = False
    rgb_reset_in_progress = False
    ene_dram_cli_prime_in_progress = False
    ene_dram_post_start_retry_index = 0
    rgb_active_design_title = "Prisma"
    openrgb_stable_ids = {1: "ene:1"}
    ene_dram_cli_prime_done = {"ene:1"}

    def __init__(self) -> None:
        self.ene_dram_post_start_retry_timer = Timer()
        self.last_ui_navigation_at = 99.0
        self.prime_calls = 0
        self.logs: list[str] = []

    def selected_openrgb_devices(self) -> list[Device]:
        return [Device()]

    @staticmethod
    def is_ene_dram_device(_device: Device) -> bool:
        return True

    def log_message(self, message: str) -> None:
        self.logs.append(message)

    def prime_ene_dram_cold_start(self, callback: object) -> None:
        self.prime_calls += 1


def test_cache_budget_accepts_only_supported_presets() -> None:
    assert cache_budget_mb(Settings(0)) == 0
    assert cache_budget_mb(Settings(4096)) == 4096
    assert cache_budget_mb(Settings(3333)) == 2048
    assert cache_budget_mb(Settings("broken")) == 2048


def test_catalog_and_previews_are_regenerable_and_invalidated(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    source_root = tmp_path / "media"
    source_root.mkdir()
    source = source_root / "frame.png"
    source.write_bytes(b"first")
    with patch.dict(os.environ, {"XDG_CACHE_HOME": str(cache)}):
        records = [{"path": str(source), "name": "frame", "kind": "image"}]
        save_catalog_records("test-media", (source_root,), records, 512)
        assert cached_catalog_records("test-media", (source_root,), 512) == records
        first_preview = preview_cache_path("test-preview", source, 512)
        assert first_preview is not None
        source.write_bytes(b"second-version")
        os.utime(source, None)
        assert cached_catalog_records("test-media", (source_root,), 512) is None
        assert preview_cache_path("test-preview", source, 512) != first_preview
        assert preview_cache_path("test-preview", source, 0) is None


def test_cache_trim_removes_oldest_files_inside_owned_root(tmp_path: Path) -> None:
    root = tmp_path / "performance-cache-v1"
    root.mkdir()
    old = root / "old.bin"
    new = root / "new.bin"
    old.write_bytes(b"o" * 60)
    new.write_bytes(b"n" * 60)
    os.utime(old, ns=(1, 1))
    os.utime(new, ns=(2, 2))
    total, removed = trim_cache(root, 100)
    assert (total, removed) == (60, 1)
    assert not old.exists() and new.exists()


def test_ene_recovery_waits_until_page_switching_is_idle() -> None:
    recovery = Recovery()
    with patch("modules.rgb_studio.v1_15.ene_start_recovery.time.monotonic", return_value=100.0):
        recovery._retry_ene_dram_profile_start()
    assert recovery.ene_dram_post_start_retry_timer.started == [3500]
    assert recovery.prime_calls == 0


def test_transition_implementation_never_captures_or_rerenders_pages() -> None:
    source = (ROOT / "src/modules/ui_performance/v1_1/controller.py").read_text(encoding="utf-8")
    assert "QVariantAnimation" in source and "TransitionOverlay" in source
    assert ".grab(" not in source
    assert "QGraphicsOpacityEffect" not in source
    assert "QPixmap" not in source
    assert "QEvent.Type.Hide" in source and "animation.stop()" in source


def test_idle_memory_reclaim_collects_cycles_and_uses_optional_glibc_trim() -> None:
    class Trim:
        argtypes = None
        restype = None

        def __call__(self, padding: int) -> int:
            assert padding == 0
            return 1

    process = type("Process", (), {"malloc_trim": Trim()})()
    with patch("modules.ui_performance.v1_1.memory.gc.collect", return_value=7), patch(
        "modules.ui_performance.v1_1.memory.ctypes.CDLL", return_value=process,
    ):
        assert release_idle_memory() == (7, True)


def test_hidden_video_preview_releases_decoder_source_and_frame_buffer() -> None:
    source = (ROOT / "src/modules/lcd_media_manager/v1_1/video_preview.py").read_text(
        encoding="utf-8"
    )
    assert "def _release_player_source" in source
    assert "self.player.setSource(QUrl())" in source
    assert "self.latest_image = QImage()" in source
    assert "self._release_player_source()" in source[source.index("    def set_active"):]
