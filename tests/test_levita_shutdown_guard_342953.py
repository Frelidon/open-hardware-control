from __future__ import annotations

import io
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.lcd_levita_shutdown.v1_0 import guard  # noqa: E402
from modules.levita_daemon_health.v1_1 import (  # noqa: E402
    DaemonMemorySample, is_owned_trcc_daemon_pid, replacement_owned_trcc_pid,
)


UI = (ROOT / "src/thermalright_display_ui.py").read_text(encoding="utf-8")
MAIN = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")


def _fake_trcc(tmp_path: Path) -> Path:
    executable = tmp_path / "trcc"
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def test_firmware_restore_is_a_bounded_daemon_disconnect(tmp_path: Path) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, "Disconnected\n", "")

    executable = _fake_trcc(tmp_path)
    result = guard.restore_firmware_logo(
        str(executable), runner=runner,
        finder=lambda: guard.DaemonMemorySample(123, 4096), timeout=99,
    )

    assert result.ok
    assert calls[0][0] == [
        str(executable.resolve()), "device", "disconnect", "87ad:70db",
    ]
    assert calls[0][1]["timeout"] == 3.0
    assert calls[0][1]["env"]["TRCC_DAEMON"] == "1"
    assert calls[0][1]["env"]["QT_QPA_PLATFORM"] == "offscreen"
    assert "shell" not in calls[0][1]


def test_firmware_restore_rejects_an_untrusted_program_path() -> None:
    result = guard.restore_firmware_logo("/tmp/not-trcc")
    assert not result.ok
    assert "TRCC" in result.message


def test_already_detached_device_is_an_idempotent_success(tmp_path: Path) -> None:
    executable = _fake_trcc(tmp_path)

    def runner(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 1, "", "Not attached: 87ad:70db")

    result = guard.restore_firmware_logo(
        str(executable), runner=runner,
        finder=lambda: guard.DaemonMemorySample(123, 4096),
    )
    assert result.ok


def test_shutdown_does_not_spawn_a_daemon_when_none_is_running(tmp_path: Path) -> None:
    executable = _fake_trcc(tmp_path)
    result = guard.restore_firmware_logo(
        str(executable),
        runner=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected TRCC start")),
        finder=lambda: None,
    )
    assert result.ok


def test_owned_daemon_stops_after_display_release_without_touching_a_replacement(tmp_path: Path) -> None:
    executable = _fake_trcc(tmp_path)
    calls: list[tuple[list[str], dict[str, object]]] = []
    samples = iter((guard.DaemonMemorySample(123, 4096), None))

    def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, "Daemon stopped.\n", "")

    result = guard.stop_owned_daemon(
        str(executable), 123, runner=runner, finder=lambda: next(samples),
    )
    assert result.ok
    assert calls[0][0] == [str(executable.resolve()), "kill"]
    assert calls[0][1]["timeout"] == 8.0
    assert "TRCC_DAEMON" not in calls[0][1]["env"]

    untouched = guard.stop_owned_daemon(
        str(executable), 123,
        runner=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unrelated daemon")),
        finder=lambda: guard.DaemonMemorySample(456, 4096),
        owned_pid_exists=lambda _pid: True,
    )
    assert not untouched.ok

    vanished = guard.stop_owned_daemon(
        str(executable), 123,
        runner=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("replacement must remain")),
        finder=lambda: guard.DaemonMemorySample(456, 4096),
        owned_pid_exists=lambda _pid: False,
    )
    assert vanished.ok
    assert "replacement left untouched" in vanished.message


def test_exact_trcc_pid_probe_distinguishes_exited_and_unreadable_process(tmp_path: Path) -> None:
    process = tmp_path / "123"
    process.mkdir()
    (process / "cmdline").write_bytes(b"/usr/bin/trcc\0daemon\0")
    status = process / "status"
    status.write_text("Name:\ttrcc\nUid:\t1000\t1000\t1000\t1000\n")
    assert is_owned_trcc_daemon_pid(123, proc_root=tmp_path, uid=1000) is True
    status.write_text("Name:\ttrcc\nUid:\t2000\t2000\t2000\t2000\n")
    assert is_owned_trcc_daemon_pid(123, proc_root=tmp_path, uid=1000) is False
    status.unlink()
    assert is_owned_trcc_daemon_pid(123, proc_root=tmp_path, uid=1000) is None
    (process / "cmdline").unlink()
    process.rmdir()
    assert is_owned_trcc_daemon_pid(123, proc_root=tmp_path, uid=1000) is False


def test_controlled_restart_adopts_only_a_verified_replacement() -> None:
    observed = DaemonMemorySample(456, 8192)
    assert replacement_owned_trcc_pid(
        123, observed, previous_pid_exists=lambda _pid: False,
    ) == 456
    assert replacement_owned_trcc_pid(
        123, observed, previous_pid_exists=lambda _pid: True,
    ) is None
    assert replacement_owned_trcc_pid(
        123, observed, previous_pid_exists=lambda _pid: None,
    ) is None
    assert replacement_owned_trcc_pid(
        456, observed, previous_pid_exists=lambda _pid: False,
    ) is None
    assert replacement_owned_trcc_pid(
        None, observed, previous_pid_exists=lambda _pid: False,
    ) is None


def test_clean_guard_finish_suppresses_the_crash_fallback(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OHC_DISABLE_HARDWARE_IO", raising=False)
    class FakeProcess:
        def __init__(self) -> None:
            self.stdin = FakeInput()
            self.waited = False

        def poll(self) -> None:
            return None

        def wait(self, *, timeout: float) -> int:
            assert timeout == 1.0
            self.waited = True
            return 0

    class FakeInput(io.StringIO):
        def close(self) -> None:
            self.was_closed = True

    process = FakeProcess()
    calls: list[tuple[list[str], dict[str, object]]] = []

    def factory(args: list[str], **kwargs: object) -> FakeProcess:
        calls.append((args, kwargs))
        return process

    executable = _fake_trcc(tmp_path)
    watcher = guard.LevitaFirmwareGuard(str(executable), process_factory=factory)
    assert watcher.arm()
    watcher.finish(restored=True)

    assert calls[0][0][-4:-2] == ["--watch", str(executable.resolve())]
    assert calls[0][0][-2] == str(os.getpid())
    assert calls[0][0][-1].isdigit()
    assert calls[0][1]["start_new_session"] is True
    assert process.waited
    assert process.stdin.getvalue() == "clean\n"


def test_guard_script_finds_installed_modules_without_parent_pythonpath(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [sys.executable, str(Path(guard.__file__).resolve())],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert completed.returncode == 2
    assert "ModuleNotFoundError" not in completed.stderr


def test_ui_arms_after_real_write_and_releases_even_if_test_mode_changed() -> None:
    assert "self.firmware_guard.arm(self.cli.executable)" in UI
    assert "self.firmware_guard.armed or not self.test_mode.isChecked()" in UI
    assert "restore_firmware_logo(self.cli.executable" in UI
    assert "self.firmware_guard.finish(restored=restored)" in UI
    assert "stop_owned_daemon(self.cli.executable" in UI


def test_parent_pipe_eof_runs_firmware_fallback(monkeypatch) -> None:
    calls: list[str] = []

    def restore(executable: str) -> guard.FirmwareRestoreResult:
        calls.append(executable)
        return guard.FirmwareRestoreResult(True, "Disconnected")

    monkeypatch.setattr(guard.sys, "stdin", io.StringIO(""))
    monkeypatch.setattr(guard, "restore_firmware_logo", restore)
    monkeypatch.setattr("modules.application_shutdown.v1_1.journal.record", lambda *_args, **_kwargs: None)
    assert guard._watch_parent_pipe("/usr/bin/trcc", 123, "456", parent_probe=lambda *_args: False) == 0
    assert calls == ["/usr/bin/trcc"]


def test_clean_parent_pipe_token_does_not_touch_hardware(monkeypatch) -> None:
    monkeypatch.setattr(guard.sys, "stdin", io.StringIO("clean\n"))
    monkeypatch.setattr(
        guard,
        "restore_firmware_logo",
        lambda _executable: (_ for _ in ()).throw(AssertionError("unexpected fallback")),
    )
    assert guard._watch_parent_pipe("/usr/bin/trcc", 123, "456") == 0


def test_guard_parent_identity_rejects_pid_reuse_and_zombies(tmp_path: Path) -> None:
    process = tmp_path / "123"
    process.mkdir()
    stat = process / "stat"
    fields = ["S", *("0" for _ in range(18)), "456", "0"]
    stat.write_text("123 (Open Hardware Control) " + " ".join(fields), encoding="utf-8")
    assert guard._parent_identity_matches(123, "456", proc_root=tmp_path) is True
    assert guard._parent_identity_matches(123, "999", proc_root=tmp_path) is False
    fields[0] = "Z"
    stat.write_text("123 (Open Hardware Control) " + " ".join(fields), encoding="utf-8")
    assert guard._parent_identity_matches(123, "456", proc_root=tmp_path) is False
    stat.unlink()
    assert guard._parent_identity_matches(123, "456", proc_root=tmp_path) is None
    process.rmdir()
    assert guard._parent_identity_matches(123, "456", proc_root=tmp_path) is False


def test_pipe_eof_waits_for_confirmed_exact_parent_exit(monkeypatch) -> None:
    states = iter((True, None, False))
    delays: list[float] = []
    calls: list[str] = []
    monkeypatch.setattr(guard.sys, "stdin", io.StringIO(""))
    monkeypatch.setattr("modules.application_shutdown.v1_1.journal.record", lambda *_args, **_kwargs: None)

    def restore(executable: str) -> guard.FirmwareRestoreResult:
        assert delays == [1.0, 1.0]
        calls.append(executable)
        return guard.FirmwareRestoreResult(True)

    monkeypatch.setattr(guard, "restore_firmware_logo", restore)
    assert guard._watch_parent_pipe(
        "/usr/bin/trcc", 123, "456", parent_probe=lambda *_args: next(states), sleeper=delays.append,
    ) == 0
    assert calls == ["/usr/bin/trcc"]


def test_hardware_io_disabled_never_arms_a_live_firmware_guard(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OHC_DISABLE_HARDWARE_IO", "1")
    watcher = guard.LevitaFirmwareGuard(
        str(_fake_trcc(tmp_path)),
        process_factory=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected guard start")),
    )
    assert not watcher.arm()


def test_kraken_orderly_and_next_start_crash_fallback_remain_wired() -> None:
    assert 'Backend.kraken_args() + ["set", "lcd", "screen", "liquid"]' in MAIN
    assert 'exit_run.run("hardware", lambda: self.perform_orderly_hardware_exit(reason))' in MAIN
    assert 'self.perform_orderly_hardware_exit("System-Shutdown/Logout")' in MAIN
    assert "self.previous_experimental_lcd_session" in MAIN
    assert 'self.settings.setValue("lcd/recovery_required", True)' in MAIN


def test_tray_and_both_levita_pages_share_the_firmware_restore_path() -> None:
    effects = (ROOT / "src/modules/display_effects/v1_11/base_page.py").read_text(encoding="utf-8")
    assert 'QAction("Originalanzeige des Kühlers wiederherstellen", self)' in MAIN
    assert "if self.is_thermalright_cooling():" in MAIN
    assert "studio.restore_firmware_display()" in MAIN
    assert 'self.restore_firmware_button = QPushButton("Thermalright-Originalanzeige wiederherstellen")' in UI
    assert "self.cli.disconnect_args(), False" in UI
    assert "self.firmware_guard.finish(restored=True)" in UI
    assert 'self.restore_original_button = QPushButton("Thermalright-Originalanzeige wiederherstellen")' in effects
    assert 'getattr(self.studio, "restore_firmware_display", None)' in effects


def test_minimize_and_close_are_unambiguous_and_tray_quit_remains_explicit() -> None:
    assert "self.explicit_quit_requested = True" in MAIN
    assert "self.tray_quit_action.setEnabled(False)" in MAIN
    assert "self.tray.hide()" in MAIN
    minimize = MAIN[MAIN.index("    def minimize_to_tray"):MAIN.index("    def closeEvent")]
    close = MAIN[MAIN.index("    def closeEvent"):MAIN.index("    def show_from_tray")]
    assert "self.hide()" in minimize and "self.showMinimized()" in minimize
    assert "event.ignore()" in close
    assert "self.minimize_to_tray(force_tray=True)" in close
    assert "self.perform_orderly_hardware_exit" not in close
