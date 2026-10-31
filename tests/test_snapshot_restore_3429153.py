#!/usr/bin/env python3
"""Regression guards for the bounded Snapshot Manager 1.0 policy."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from modules.localization.v1_0.catalog import UI_TRANSLATIONS
from modules.snapshot_manager.v1_0.model import (
    ActivityGate, ActivitySample, manual_block_active, normalize_policy,
    normalize_process_names, parse_snapper_json, process_match,
)
from modules.snapshot_manager.v1_0.probe import read_os_release
from modules.snapshot_manager.v1_0.program_manager import (
    ProgramChoice, installed_programs, recent_running_programs, running_programs,
)
from modules.snapshot_manager.v1_0 import helper as snapshot_helper


def test_manual_snapshot_writes_use_a_separate_polkit_entrypoint() -> None:
    assert snapshot_helper.entrypoint_allows(
        "/usr/libexec/open-hardware-control-snapshot-admin-helper", "create",
    )
    assert snapshot_helper.entrypoint_allows(
        "/usr/libexec/open-hardware-control-snapshot-admin-helper", "delete",
    )
    assert not snapshot_helper.entrypoint_allows(
        "/usr/libexec/open-hardware-control-snapshot-helper", "create",
    )
    assert snapshot_helper.entrypoint_allows(
        "/usr/libexec/open-hardware-control-snapshot-helper", "list",
    )
    assert snapshot_helper.entrypoint_allows(
        "/usr/libexec/open-hardware-control-snapshot-helper", "game",
    )
    page = "\n".join((ROOT / "src/modules/snapshot_manager/v1_0" / name).read_text(encoding="utf-8") for name in ("page.py", "process_runtime.py", "views.py", "snapshot_actions.py"))
    assert 'ADMIN_ACTIONS = frozenset({"create", "delete", "setup-root"})' in page
    assert "helper = ADMIN_HELPER if action in ADMIN_ACTIONS else HELPER" in page
    assert "Polkit-Anfrage gestartet" in page
    assert "Polkit-Aktion fehlgeschlagen" in page
    assert "Polkit-Autorisierung nicht erteilt oder nicht verfügbar" in page
    assert "möglicherweise kein Authentifizierungsagent erreichbar" in page
    assert 'self._expire(process, "system-probe", 8)' in page
    activity_runtime = (
        ROOT / "src/modules/snapshot_manager/v1_0/activity_runtime.py"
    ).read_text(encoding="utf-8")
    assert "Aktivitätswächter nach 5 Sekunden" in activity_runtime
    assert 'self._expire(process, action, 90)' in page
    assert "lambda: self._expire(process))" not in page


def test_snapper_services_receive_real_cpu_and_io_bounds(
    tmp_path: Path, monkeypatch,
) -> None:
    observed: list[list[str]] = []
    monkeypatch.setattr(snapshot_helper, "SYSTEMD_UNIT_DIR", tmp_path)
    monkeypatch.setattr(snapshot_helper, "SYSTEMCTL", tmp_path / "systemctl")
    monkeypatch.setattr(snapshot_helper.os, "sched_getaffinity", lambda _pid: {0, 2, 4, 6})
    monkeypatch.setattr(
        snapshot_helper, "run",
        lambda command, **_kwargs: observed.append(command) or SimpleNamespace(returncode=0),
    )
    policy = snapshot_helper.policy_from_args([
        "50", "16384", "5", "2048", "2", "50",
    ])
    result = snapshot_helper.configure_service_resources(policy)
    assert result == {
        "allowed_cpus": [4, 6], "cpu_quota_percent": 100,
        "cpu_percent_per_core": 50,
    }
    assert observed == [[str(tmp_path / "systemctl"), "daemon-reload"]]
    for unit in snapshot_helper.RESOURCE_SERVICES:
        content = (tmp_path / f"{unit}.d" / snapshot_helper.RESOURCE_DROPIN).read_text()
        assert "CPUQuota=100%" in content
        assert "AllowedCPUs=4,6" in content
        assert "Nice=15" in content
        assert "CPUWeight=10" in content
        assert "IOWeight=10" in content


def test_activity_probe_is_persistent_low_priority_and_manual_block_stops_it() -> None:
    activity = (ROOT / "src/modules/snapshot_manager/v1_0/activity_probe.py").read_text(encoding="utf-8")
    page = "\n".join((ROOT / "src/modules/snapshot_manager/v1_0" / name).read_text(encoding="utf-8") for name in ("page.py", "process_runtime.py", "views.py", "snapshot_actions.py"))
    runtime = (ROOT / "src/modules/snapshot_manager/v1_0/activity_runtime.py").read_text(encoding="utf-8")
    assert "os.nice(15)" in activity
    assert "os.sched_setaffinity" in activity
    assert "def watch(" in activity
    assert 'names, busy_core_percent, "--watch", interval_seconds' in runtime
    assert 'or self.manual_mode != "desktop"' in page


def test_program_manager_discovers_desktop_and_running_programs(tmp_path: Path) -> None:
    applications = tmp_path / "applications"
    applications.mkdir()
    (applications / "game.desktop").write_text(
        "[Desktop Entry]\nName=Example Racer\nExec=/opt/racer/bin/racer %U\n",
        encoding="utf-8",
    )
    (applications / "hidden.desktop").write_text(
        "[Desktop Entry]\nName=Hidden\nNoDisplay=true\nExec=hidden\n",
        encoding="utf-8",
    )
    assert installed_programs((applications,)) == (ProgramChoice("Example Racer", "racer", "installed"),)
    proc = tmp_path / "proc"
    (proc / "123").mkdir(parents=True)
    (proc / "123" / "comm").write_text("racer\n", encoding="utf-8")
    (proc / "123" / "stat").write_text("123 (racer) S " + "0 " * 18 + "99 0\n", encoding="utf-8")
    assert running_programs(proc)[0].executable == "racer"
    assert recent_running_programs(proc)[0].source == "recent"


def test_manual_snapshot_creation_uses_only_the_fixed_snapper_command(
    tmp_path: Path, monkeypatch, capsys,
) -> None:
    snapper = tmp_path / "snapper"
    snapper.touch()
    observed: list[list[str]] = []
    monkeypatch.setattr(snapshot_helper, "SNAPPER", snapper)
    monkeypatch.setattr(
        snapshot_helper, "run",
        lambda command, **_kwargs: observed.append(command) or SimpleNamespace(
            returncode=0, stdout="42\n",
        ),
    )
    snapshot_helper.create_snapshot("root", "Vor Grafiktreiber-Test")
    assert observed == [[
        str(snapper), "-c", "root", "create", "--description",
        "[OHC] Vor Grafiktreiber-Test", "--print-number",
    ]]
    assert json.loads(capsys.readouterr().out)["created_snapshot"] == "42"
    with pytest.raises(SystemExit):
        snapshot_helper.create_snapshot("root", "unzulässig\nzweite Zeile")


def test_snapshot_list_reads_bounded_metadata_without_blocking_snapper(
    tmp_path: Path, monkeypatch, capsys,
) -> None:
    snapper = tmp_path / "snapper"
    snapper.touch()
    configs = tmp_path / "configs"
    configs.mkdir()
    subvolume = tmp_path / "subvolume"
    snapshots = subvolume / ".snapshots"
    snapshots.mkdir(parents=True)
    (configs / "1").write_text(f'SUBVOLUME="{subvolume}"\n', encoding="utf-8")
    for number, description, cleanup in (
        (365, "timeline", "timeline"),
        (366, "[OHC] Manueller Snapshot", "number"),
    ):
        directory = snapshots / str(number)
        directory.mkdir()
        (directory / "info.xml").write_text(
            "<snapshot>"
            f"<date>2026-10-03 21:{number - 325:02d}:00</date>"
            f"<description>{description}</description>"
            f"<cleanup>{cleanup}</cleanup>"
            "</snapshot>",
            encoding="utf-8",
        )

    monkeypatch.setattr(snapshot_helper, "SNAPPER", snapper)
    monkeypatch.setattr(snapshot_helper, "SNAPPER_CONFIG_DIR", configs)
    monkeypatch.setattr(
        snapshot_helper, "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("snapper list must not run")),
    )
    snapshot_helper.list_snapshots("1")
    response = json.loads(capsys.readouterr().out)
    assert response["ok"] is True
    assert response["list_backend"] == "metadata"
    assert [row["number"] for row in response["payload"]["snapshots"]] == [0, 366, 365]
    assert response["payload"]["snapshots"][1]["description"] == "[OHC] Manueller Snapshot"


def test_snapshot_source_is_visible_and_filterable() -> None:
    records = parse_snapper_json({"snapshots": [
        {"number": 1, "description": "[OHC] Vor Treibertest"},
        {"number": 2, "description": "timeline", "cleanup": "timeline"},
        {"number": 3, "description": "Manueller Snapshot aus Open Hardware Control"},
    ]})
    assert [(record.description, record.source) for record in records] == [
        ("Vor Treibertest", "ohc"), ("timeline", "system"),
        ("Manueller Snapshot aus Open Hardware Control", "ohc"),
    ]


def test_create_button_can_chain_fixed_root_setup() -> None:
    source = "\n".join((ROOT / "src/modules/snapshot_manager/v1_0" / name).read_text(encoding="utf-8") for name in ("page.py", "views.py", "snapshot_actions.py"))
    assert 'self.pending_snapshot_after_setup = description' in source
    assert 'self.run_helper("setup-root", [])' in source
    assert 'self.run_helper("create", ["root", description])' in source
    assert 'self.snapshot_filter.addItem(self.tr("Alle Snapshots"), "all")' in source


def test_root_setup_is_fixed_to_btrfs_root(tmp_path: Path, monkeypatch, capsys) -> None:
    snapper = tmp_path / "snapper"
    findmnt = tmp_path / "findmnt"
    configs = tmp_path / "configs"
    snapper.touch(); findmnt.touch(); configs.mkdir()
    observed: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        observed.append(command)
        if command[0] == str(findmnt):
            return SimpleNamespace(returncode=0, stdout="btrfs\n")
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(snapshot_helper, "SNAPPER", snapper)
    monkeypatch.setattr(snapshot_helper, "FINDMNT", findmnt)
    monkeypatch.setattr(snapshot_helper, "SNAPPER_CONFIG_DIR", configs)
    monkeypatch.setattr(snapshot_helper, "run", fake_run)
    snapshot_helper.setup_root_config()
    assert observed == [
        [str(findmnt), "-n", "-o", "FSTYPE", "/"],
        [str(snapper), "-c", "root", "create-config", "/"],
    ]
    assert json.loads(capsys.readouterr().out)["created_config"] is True


def test_successful_create_remains_visible_while_snapshot_list_refreshes(
    monkeypatch,
) -> None:
    """The automatic list read must never hide a completed snapshot write."""

    import importlib
    from PySide6.QtCore import QProcess
    from PySide6.QtWidgets import QApplication, QWidget

    snapshot_page = importlib.import_module("modules.snapshot_manager.v1_0.page")
    app = QApplication.instance() or QApplication([])

    class Settings:
        def value(self, _key: str, default=None):
            return default

        def setValue(self, _key: str, _value: object) -> None:
            return None

        def sync(self) -> None:
            return None

    class Host(QWidget):
        def __init__(self) -> None:
            super().__init__()
            self.settings = Settings()
            self.messages: list[str] = []

        def log_message(self, message: str) -> None:
            self.messages.append(message)

    class FinishedProcess:
        def __init__(self, payload: dict[str, object]) -> None:
            self.payload = payload

        def readAllStandardOutput(self) -> bytes:
            return json.dumps(self.payload).encode("utf-8")

        def readAllStandardError(self) -> bytes:
            return b""

        def deleteLater(self) -> None:
            return None

    monkeypatch.setenv("OHC_SNAPSHOT_MANAGER_DEMO", "1")
    host = Host()
    page = snapshot_page.SnapshotManagerPage(host, lambda text: text)
    scheduled: list[tuple[int, object]] = []
    monkeypatch.setattr(
        snapshot_page, "QTimer",
        SimpleNamespace(singleShot=lambda delay, *args: scheduled.append((delay, args[-1]))),
    )

    action_module = importlib.import_module("modules.snapshot_manager.v1_0.snapshot_actions")
    monkeypatch.setattr(action_module, "QTimer", snapshot_page.QTimer)

    created = FinishedProcess({"ok": True, "created_snapshot": "365"})
    page.helper_process = created
    page.pending_helper_action = "create"
    page._helper_finished(created, "create", 0, QProcess.ExitStatus.NormalExit)

    assert "Snapshot 365 wurde erstellt" in page.snapshot_action_status.text()
    assert "Administratorenfreigabe" not in page.snapshot_action_status.text()
    assert page.snapshot_create.isEnabled()

    calls: list[tuple[str, list[str]]] = []
    page.run_helper = lambda action, arguments: calls.append((action, arguments)) or True
    refresh = next(callback for delay, callback in scheduled if delay == 600)
    refresh()
    assert calls == [("list", ["1"])]
    assert page.snapshot_action_status.text() == (
        "Snapshot 365 wurde erstellt · Liste wird aktualisiert …"
    )

    listed = FinishedProcess({
        "ok": True,
        "payload": {"snapshots": [{"number": 365, "description": "[OHC] Test"}]},
    })
    page.helper_process = listed
    page.pending_helper_action = "list"
    page._helper_finished(listed, "list", 0, QProcess.ExitStatus.NormalExit)
    assert page.snapshot_action_status.text() == (
        "Snapshot 365 wurde erstellt · 1 Snapshots geladen."
    )
    assert page.pending_created_snapshot == ""

    newer = FinishedProcess({"ok": True, "payload": {"snapshots": []}})
    page.helper_process = newer
    page.pending_helper_action = "list"
    page._helper_finished(created, "create", 0, QProcess.ExitStatus.NormalExit)
    assert page.helper_process is newer
    assert page.pending_helper_action == "list"

    page.pending_created_snapshot = "366"
    failed_list = FinishedProcess({"ok": False, "error": "cannot read snapshots"})
    page.helper_process = failed_list
    page.pending_helper_action = "list"
    page._helper_finished(failed_list, "list", 2, QProcess.ExitStatus.NormalExit)
    assert page.snapshot_action_status.text() == (
        "Snapshot 366 wurde erstellt · Liste konnte nicht aktualisiert werden."
    )
    assert page.pending_created_snapshot == ""

    # A user-requested snapshot always wins over automatic/manual blocking.
    page.manual_mode = "forever"
    page.helper_process = object()
    page.pending_helper_action = "forever"
    page.create_snapshot_now()
    assert page.pending_manual_snapshot == (
        "1", "Manueller Snapshot aus Open Hardware Control",
    )
    assert "unabhängig von Automatikpausen" in page.snapshot_action_status.text()
    page.helper_process = None
    calls.clear()
    page._dispatch_pending_manual_snapshot()
    assert calls == [(
        "create", ["1", "Manueller Snapshot aus Open Hardware Control"],
    )]
    assert page.pending_manual_snapshot is None

    page.until_hour_slider.setValue(23)
    page.until_minute_slider.setValue(9)
    assert page.until_edit.time().toString("HH:mm") == "23:45"
    assert page.until_time_value.text() == "23:45"

    page.deleteLater()
    host.deleteLater()
    app.processEvents()
