"""No live system mutations: restored snapshot boundaries use local fixtures."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["OHC_DISABLE_HARDWARE_IO"] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QEvent, QObject, QProcess, QSettings, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402
from modules.snapshot_manager.v1_0 import helper  # noqa: E402
from modules.snapshot_manager.v1_0.activity_runtime import ActivityProbeRuntime  # noqa: E402
from modules.snapshot_manager.v1_0.model import normalize_policy  # noqa: E402
from modules.snapshot_manager.v1_0.page import SnapshotManagerPage  # noqa: E402


def test_bounded_metadata_never_follows_a_snapshot_directory_or_info_symlink(tmp_path: Path, monkeypatch) -> None:
    volume = tmp_path / "volume"
    snapshots = volume / ".snapshots"
    snapshots.mkdir(parents=True)
    configs = tmp_path / "configs"
    configs.mkdir()
    (configs / "root").write_text(f'SUBVOLUME="{volume}"\n', encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "info.xml").write_text("<snapshot><description>must not read</description></snapshot>")
    (snapshots / "123").symlink_to(outside, target_is_directory=True)
    (snapshots / "124").mkdir()
    (snapshots / "124" / "info.xml").symlink_to(outside / "info.xml")
    (snapshots / "125").mkdir()
    (snapshots / "125" / "info.xml").write_bytes(b"x" * (helper.MAX_INFO_XML_BYTES + 1))
    monkeypatch.setattr(helper, "SNAPPER_CONFIG_DIR", configs)
    assert helper._snapshot_metadata_payload("root")["snapshots"] == [{
        "number": 0, "date": "", "description": "Aktueller Systemzustand", "cleanup": "",
    }]


def test_resource_dropins_do_not_reload_unchanged_configuration(tmp_path: Path, monkeypatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(helper, "SYSTEMD_UNIT_DIR", tmp_path)
    monkeypatch.setattr(helper.os, "sched_getaffinity", lambda _pid: {1, 3, 5})
    monkeypatch.setattr(helper, "run", lambda cmd, **_kwargs: calls.append(cmd) or SimpleNamespace(returncode=0))
    policy = helper.policy_from_args(["50", "16384", "5", "2048", "2", "50"])
    helper.configure_service_resources(policy)
    helper.configure_service_resources(policy)
    assert calls == [[str(helper.SYSTEMCTL), "daemon-reload"]]
    assert not list(tmp_path.rglob("*.tmp-*"))


def test_activity_runtime_reuses_one_worker_and_bounds_partial_json(monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    parent = QObject()
    samples: list[object] = []
    logs: list[str] = []
    runtime = ActivityProbeRuntime(parent, Path("/fixture/activity_probe.py"), samples.append, logs.append)
    starts: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(QProcess, "start", lambda _self, program, arguments: starts.append((program, arguments)))
    runtime.start("game.exe", 65, 20)
    first = runtime.process
    runtime.start("game.exe", 65, 20)
    assert first is runtime.process and len(starts) == 1
    assert starts[0][1][-2:] == ["--watch", "20"]
    chunks = iter((b'{"schema": 1', b'}\ninvalid\n', b'x' * 65_537))
    monkeypatch.setattr(first, "readAllStandardOutput", lambda: next(chunks))
    runtime._ready(first)
    assert not samples
    runtime._ready(first)
    assert samples == [{"schema": 1}]
    runtime._ready(first)
    assert runtime.buffer == bytearray() and len(logs) == 1
    runtime.stop()
    assert not runtime.enabled and runtime.process is None
    parent.deleteLater()
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_page_shutdown_cancels_helper_and_queued_callback_and_retains_user_thresholds(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    monkeypatch.setenv("OHC_SNAPSHOT_MANAGER_DEMO", "1")
    host = QWidget()
    host.settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    page = SnapshotManagerPage(host, lambda text: text)
    page.policy = normalize_policy({"busy_core_percent": 90, "high_samples": 5, "release_samples": 7})
    page.save_policy()
    assert (page.policy.busy_core_percent, page.policy.high_samples, page.policy.release_samples) == (90, 5, 7)
    assert page.snapshot_create.isEnabled() and page.snapshot_filter.count() == 3
    assert page.until_hour_slider.maximum() == 23 and page.until_minute_slider.maximum() == 11
    called: list[bool] = []
    QTimer.singleShot(0, page, lambda: called.append(True))
    page.stop_processes()
    assert not page.run_helper("create", ["root", "fixture"])
    host.deleteLater()
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    assert not called


def test_persistent_automation_grant_never_names_the_manual_admin_action(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(helper, "RULES_DIR", tmp_path / "rules")
    monkeypatch.setattr(helper, "GRANTS_DIR", tmp_path / "grants")
    monkeypatch.setattr(helper, "invoking_user", lambda: (1234, "fixtureuser"))
    helper.set_grant(True)
    rule = (tmp_path / "rules" / f"{helper.RULE_PREFIX}-1234.rules").read_text()
    assert helper.ACTION_ID in rule and helper.ADMIN_ACTION_ID not in rule
    assert json.loads(capsys.readouterr().out)["persistent_authorization"] is True
    for action in ("create", "delete", "setup-root"):
        assert not helper.entrypoint_allows("open-hardware-control-snapshot-helper", action)
        assert helper.entrypoint_allows("open-hardware-control-snapshot-admin-helper", action)
