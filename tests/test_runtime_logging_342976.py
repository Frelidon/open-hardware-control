from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.levita_daemon_health.v1_1 import (
    DAEMON_RSS_LIMIT_BYTES,
    DaemonMemorySample,
    daemon_memory_exceeded,
    find_trcc_daemon_memory,
    is_probable_daemon_failure,
    is_trcc_daemon_command,
    signal_trcc_daemon,
)
from modules.runtime_logging.v1_0 import RollingLogBuffer, is_error_log_message
from log_view_support import is_rgb_fan_log_message


def test_rolling_log_keeps_one_hour_and_enforces_hard_bounds() -> None:
    history = RollingLogBuffer(window_seconds=3600, max_characters=40, max_entries=3)
    history.append("old", now=0)
    history.append("recent-one", now=3599)
    history.append("recent-two", now=3600)
    history.prune(3601)
    assert history.text() == "recent-one\nrecent-two"

    history.append("recent-three", now=3601)
    history.append("recent-four", now=3602)
    assert history.line_count == 3
    assert "recent-one" not in history.text()
    assert history.character_count == len(history.text())


def test_error_classifier_captures_failures_without_normal_status_noise() -> None:
    assert is_error_log_message("THERMALRIGHT-FEHLER: Verbindung fehlgeschlagen")
    assert is_error_log_message("Levita-Taktgeber unerwartet beendet")
    assert not is_error_log_message("Levita-Video läuft")


def test_rgb_fan_log_classifier_keeps_mapping_and_control_events_together() -> None:
    for message in (
        "ARGB-DIAG: op=led-path-save · layout=Reihe · fan_count=3",
        "RGB-STUDIO: OpenRGB #2 erkannt",
        "MAINBOARD-FAN: nct6687:pwm8 · 45 %",
        "GPU-LACT: fan curve applied",
        "VORHERIGER ABSTURZ · [12:00:00] RGB-ENGINE: unerwartet beendet",
    ):
        assert is_rgb_fan_log_message(message)
    assert not is_rgb_fan_log_message("LCD: Standbild übertragen")


def test_trcc_daemon_detection_is_exact_and_reads_own_rss(tmp_path: Path) -> None:
    own = tmp_path / "123"
    own.mkdir()
    (own / "cmdline").write_bytes(b"/usr/bin/python3\0/usr/bin/trcc\0daemon\0")
    (own / "status").write_text("Uid:\t1000 1000 1000 1000\nVmRSS:\t2048 kB\n", encoding="utf-8")
    other = tmp_path / "456"
    other.mkdir()
    (other / "cmdline").write_bytes(b"/usr/bin/trcc\0display\0play\0")
    (other / "status").write_text("Uid:\t1000 1000 1000 1000\nVmRSS:\t999999 kB\n", encoding="utf-8")

    assert is_trcc_daemon_command(("python3", "-m", "trcc", "daemon"))
    assert not is_trcc_daemon_command(("trcc", "display", "play"))
    assert find_trcc_daemon_memory(proc_root=tmp_path, uid=1000) == DaemonMemorySample(
        123, 2048 * 1024,
    )


def test_daemon_limit_and_disconnect_markers_trigger_recovery() -> None:
    assert daemon_memory_exceeded(DaemonMemorySample(1, DAEMON_RSS_LIMIT_BYTES))
    assert not daemon_memory_exceeded(DaemonMemorySample(1, DAEMON_RSS_LIMIT_BYTES - 1))
    assert is_probable_daemon_failure("ConnectionError: peer closed without sending data")
    assert is_probable_daemon_failure("interface is in use by another process")
    assert not is_probable_daemon_failure("render completed")


def test_hard_recovery_signals_only_the_exact_user_daemon(tmp_path: Path) -> None:
    daemon = tmp_path / "42"
    daemon.mkdir()
    (daemon / "cmdline").write_bytes(b"/usr/bin/trcc\0daemon\0")
    (daemon / "status").write_text(
        "Name:\ttrcc\nUid:\t1000\t1000\t1000\t1000\n", encoding="utf-8",
    )
    signals: list[tuple[int, int]] = []
    assert signal_trcc_daemon(
        42, proc_root=tmp_path, uid=1000,
        kill_fn=lambda pid, requested: signals.append((pid, requested)),
    )
    assert signals and signals[0][0] == 42

    (daemon / "cmdline").write_bytes(b"/usr/bin/sleep\0100\0")
    assert not signal_trcc_daemon(
        42, proc_root=tmp_path, uid=1000,
        kill_fn=lambda pid, requested: signals.append((pid, requested)),
    )
    assert len(signals) == 1
