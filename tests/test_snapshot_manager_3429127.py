#!/usr/bin/env python3
"""Regression guards for the bounded Snapshot Manager 1.0 policy."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.localization.v1_0.catalog import UI_TRANSLATIONS
from modules.snapshot_manager.v1_0.model import (
    ActivityGate, ActivitySample, manual_block_active, normalize_policy,
    normalize_process_names, parse_snapper_json, process_match,
)
from modules.snapshot_manager.v1_0.probe import read_os_release


def test_policy_bounds_and_boolean_settings() -> None:
    policy = normalize_policy({
        "automatic_game_pause": "false", "fullscreen_signal": "1",
        "cpu_threshold": 999, "gpu_threshold": -4,
        "desktop_kbps": 999_999, "game_kbps": 0,
    })
    assert not policy.automatic_game_pause
    assert policy.fullscreen_signal
    assert policy.cpu_threshold == 100
    assert policy.gpu_threshold == 30
    assert policy.desktop_kbps == 262_144
    assert policy.game_kbps == 1_024


def test_game_signals_and_hysteresis() -> None:
    policy = normalize_policy({"high_samples": 3, "release_samples": 3})
    gate = ActivityGate()
    trusted = gate.update(ActivitySample(gamemode=True), policy)
    assert trusted.blocked and trusted.reason == "Feral GameMode"
    assert gate.update(ActivitySample(), policy).blocked
    assert gate.update(ActivitySample(), policy).blocked
    assert not gate.update(ActivitySample(), policy).blocked

    high = ActivitySample(
        cpu_percent=88, busy_cores=6, logical_cores=12, gpu_percent=91,
    )
    assert not gate.update(high, policy).blocked
    assert not gate.update(high, policy).blocked
    assert gate.update(high, policy).blocked


def test_process_names_and_manual_deadline_are_bounded() -> None:
    assert normalize_process_names("/tmp/Game.exe, gamescope; bad name!") == ("game.exe", "gamescope")
    assert process_match(("steam", "GAME.EXE"), ("game.exe",)) == (True, "game.exe")
    assert manual_block_active("until", 1_100, now=1_000)
    assert not manual_block_active("until", 900, now=1_000)
    assert manual_block_active("forever", 0, now=1_000)


def test_snapper_and_os_parsers_reject_unbounded_shapes(tmp_path: Path) -> None:
    records = parse_snapper_json({"snapshots": [
        {"number": 12, "date": "2026-10-01", "description": "safe", "cleanup": "timeline"},
        {"description": "missing number"},
    ]})
    assert len(records) == 1 and records[0].number == "12"
    os_release = tmp_path / "os-release"
    os_release.write_text('NAME="Test Linux"\nID=test\n# ignored\n', encoding="utf-8")
    assert read_os_release(os_release) == {"NAME": "Test Linux", "ID": "test"}


def test_helper_surface_has_no_arbitrary_command_or_path() -> None:
    helper = (ROOT / "src/modules/snapshot_manager/v1_0/helper.py").read_text(encoding="utf-8")
    assert 'TIMERS = ("snapper-timeline.timer", "snapper-cleanup.timer")' in helper
    assert 'CONFIG_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")' in helper
    assert "shell=True" not in helper
    assert "os.system" not in helper
    assert 'action in {"game", "forever"}' in helper
    assert 'elif action == "delete" and len(argv) == 4:' in helper
    assert '[str(SNAPPER), "-c", config, "delete", str(number)]' in helper
    policy = (ROOT / "packaging/io.github.Frelidon.OpenHardwareControl.snapshot.policy").read_text(encoding="utf-8")
    assert "/usr/libexec/open-hardware-control-snapshot-helper" in policy
    build = (ROOT / "scripts/build_release.py").read_text(encoding="utf-8")
    assert "open-hardware-control-snapshot-helper" in build


def test_page_navigation_and_localization_are_complete() -> None:
    main = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    assert '"snapshot_manager": ("◫   Snapshot-Manager", 16)' in main
    assert "build_snapshot_manager_page" in main
    sources = (
        "Snapshot-Manager",
        "Snapshot-Arbeit bei Spielen automatisch pausieren",
        "Dauerhaft blockieren",
        "Snapshots erkennen, Aufräumlast begrenzen und Spiele schützen.",
    )
    for language in ("de", "en", "es", "fr"):
        assert all(source in UI_TRANSLATIONS[language] for source in sources)


def test_example_activity_payload_stays_plain_json() -> None:
    sample = {"schema": 1, "cpu_percent": 40.0, "gpu_percent": 55.0}
    assert json.loads(json.dumps(sample)) == sample


def test_expired_deleted_qprocess_is_ignored() -> None:
    from PySide6.QtCore import QCoreApplication, QEvent, QProcess
    from PySide6.QtWidgets import QApplication
    from shiboken6 import isValid
    from modules.snapshot_manager.v1_0.page import SnapshotManagerPage

    QApplication.instance() or QApplication([])
    process = QProcess()
    process.deleteLater()
    QCoreApplication.sendPostedEvents(process, QEvent.Type.DeferredDelete)
    assert not isValid(process)
    SnapshotManagerPage._expire(None, process, "test-probe", 1)
