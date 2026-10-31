"""Crash context is private, bounded and replayed only after abnormal exits."""

from __future__ import annotations

import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPlainTextEdit
from log_view_support import LogViewActionsMixin
from modules.crash_recovery.v1_0 import append_crash_context, recover_crash_context


APP = QApplication.instance() or QApplication([])


def test_abnormal_exit_recovers_exactly_the_final_five_minutes(tmp_path: Path) -> None:
    current = tmp_path / "crash-context-current.jsonl"
    snapshot = tmp_path / "last-crash-context.log"
    assert append_crash_context(current, "too old", observed_at=699.9)
    assert append_crash_context(current, "at boundary", observed_at=700.0)
    assert append_crash_context(current, "most recent", observed_at=999.0)

    recovered = recover_crash_context(
        current, snapshot, unexpected_exit=True, observed_at=1000.0,
    )

    assert recovered == ["at boundary", "most recent"]
    assert "too old" not in snapshot.read_text(encoding="utf-8")
    assert "most recent" in snapshot.read_text(encoding="utf-8")
    assert current.read_text(encoding="utf-8") == ""
    assert current.stat().st_mode & 0o777 == 0o600
    assert snapshot.stat().st_mode & 0o777 == 0o600


def test_normal_exit_discards_ring_without_creating_crash_snapshot(tmp_path: Path) -> None:
    current = tmp_path / "crash-context-current.jsonl"
    snapshot = tmp_path / "last-crash-context.log"
    assert append_crash_context(current, "normal session", observed_at=100.0)

    assert recover_crash_context(
        current, snapshot, unexpected_exit=False, observed_at=101.0,
    ) == []
    assert current.read_text(encoding="utf-8") == ""
    assert not snapshot.exists()


def test_new_empty_crash_does_not_leave_an_older_snapshot_misleading(tmp_path: Path) -> None:
    current = tmp_path / "crash-context-current.jsonl"
    snapshot = tmp_path / "last-crash-context.log"
    current.write_text("", encoding="utf-8")
    snapshot.write_text("older crash line\n", encoding="utf-8")

    assert recover_crash_context(
        current, snapshot, unexpected_exit=True, observed_at=100.0,
    ) == []
    payload = snapshot.read_text(encoding="utf-8")
    assert "older crash line" not in payload
    assert "letzte fünf Minuten" in payload


def test_symlink_is_never_followed_for_active_or_snapshot_file(tmp_path: Path) -> None:
    victim = tmp_path / "victim"
    victim.write_text("keep", encoding="utf-8")
    current = tmp_path / "crash-context-current.jsonl"
    current.symlink_to(victim)
    assert not append_crash_context(current, "must not write", observed_at=1.0)
    assert recover_crash_context(
        current, tmp_path / "snapshot", unexpected_exit=True, observed_at=1.0,
    ) == []
    assert victim.read_text(encoding="utf-8") == "keep"


def test_context_file_is_bounded_on_append(tmp_path: Path) -> None:
    from modules.crash_recovery.v1_0 import context

    current = tmp_path / "crash-context-current.jsonl"
    current.write_bytes(b"old\n" + b"x" * (context.CRASH_CONTEXT_MAX_BYTES + 1))
    os.chmod(current, 0o600)
    assert append_crash_context(current, "new", observed_at=2.0)
    assert current.stat().st_size <= context.CRASH_CONTEXT_RETAIN_BYTES + 256


def test_native_faulthandler_archives_prior_signal_trace_privately(
    tmp_path: Path, monkeypatch,
) -> None:
    import privacy_logging

    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    state = tmp_path / "open-hardware-control"
    state.mkdir()
    current = state / "native-crash-current.log"
    current.write_text("Fatal Python error at /home/exampleuser/private.py\n", encoding="utf-8")
    calls = []
    monkeypatch.setattr(
        privacy_logging.faulthandler, "enable",
        lambda *, file, all_threads: calls.append((file, all_threads)),
    )

    assert privacy_logging._install_native_fault_logging() == current
    assert calls and calls[0][1] is True
    assert current.read_text(encoding="utf-8") == ""
    archived = (state / "last-native-crash.log").read_text(encoding="utf-8")
    assert "/home/[USER]/private.py" in archived
    assert "/home/exampleuser" not in archived
    privacy_logging._native_fault_stream.close()
    privacy_logging._native_fault_stream = None


def test_recovered_lines_are_replayed_into_visible_and_session_log(tmp_path: Path) -> None:
    class LogHost(LogViewActionsMixin):
        def __init__(self):
            self.log_view = QPlainTextEdit()
            self.session_log_path = tmp_path / "session.log"

    host = LogHost()
    host.restore_previous_crash_context(
        ["[12:34:56] letzte Aktion"], tmp_path / "last-crash-context.log",
    )
    visible = host.log_view.toPlainText()
    persisted = host.session_log_path.read_text(encoding="utf-8")
    assert "ABSTURZDIAGNOSE" in visible
    assert "VORHERIGER ABSTURZ · [12:34:56] letzte Aktion" in visible
    assert persisted == visible + "\n"
    host.log_view.deleteLater()
    APP.processEvents()
