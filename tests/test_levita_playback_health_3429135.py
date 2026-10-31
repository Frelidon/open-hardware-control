"""Pure playback supervision tests; no USB access."""

from datetime import datetime
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.levita_daemon_health.v1_1 import (  # noqa: E402
    PLAYBACK_HEALTH_INTERVAL_MS,
    PLAYBACK_RECOVERY_COOLDOWN_SECONDS,
    PlaybackHealth,
    PlaybackRecoveryPolicy,
    parse_playback_status,
    parse_video_playback_status,
    recent_trcc_cause,
)


def test_status_parser_requires_exact_attached_device_and_active_theme() -> None:
    good = parse_playback_status(
        'warning before JSON\n{"lcd_devices":[{"key":"87ad:70db","current_theme":"ohc-orbit"}]}\n',
        "87ad:70db",
    )
    assert good.healthy and good.theme == "ohc-orbit"
    assert not parse_playback_status('{"lcd_devices":[]}', "87ad:70db").healthy
    assert not parse_playback_status(
        '{"lcd_devices":[{"key":"87ad:70db","current_theme":null}]}',
        "87ad:70db",
    ).healthy
    assert not parse_playback_status("not json", "87ad:70db").healthy


def test_recovery_needs_two_failures_is_bounded_and_success_clears_streak() -> None:
    policy = PlaybackRecoveryPolicy()
    bad = PlaybackHealth(False, "not attached")
    good = PlaybackHealth(True, "ok", "theme")
    assert not policy.observe(bad)
    assert not policy.observe(good)
    assert not policy.observe(bad)
    assert policy.observe(bad)
    assert policy.recovery_attempts == 1
    for expected_attempt in (2, 3):
        assert not policy.observe(bad)
        assert policy.observe(bad)
        assert policy.recovery_attempts == expected_attempt
    assert not policy.observe(bad)
    assert not policy.observe(bad)
    assert policy.recovery_attempts == 3


def test_deferred_retry_is_not_consumed_and_stable_playback_renews_budget() -> None:
    policy = PlaybackRecoveryPolicy()
    bad = PlaybackHealth(False, "stopped")
    good = PlaybackHealth(True, "playing", "theme")
    assert not policy.observe(bad)
    assert policy.observe(bad)
    policy.defer_recovery()
    assert policy.recovery_attempts == 0
    assert policy.consecutive_failures == 1
    assert policy.observe(bad)
    assert policy.recovery_attempts == 1
    for _index in range(policy.successes_to_reset_attempts):
        assert not policy.observe(good)
    assert policy.recovery_attempts == 0
    assert PLAYBACK_RECOVERY_COOLDOWN_SECONDS == 30


def test_video_status_parser_requires_actual_unpaused_daemon_playback() -> None:
    assert parse_video_playback_status(
        "playing frame 17/240 @ 30 fps", "87ad:70db",
    ).healthy
    assert not parse_video_playback_status(
        "playing frame 17/240 @ 30 fps (paused)", "87ad:70db",
    ).healthy
    stopped = parse_video_playback_status("no playback loaded", "87ad:70db")
    assert not stopped.healthy
    assert stopped.failure_kind == "missing-playback"
    assert "verloren" in stopped.reason


def test_recent_trcc_tail_is_bounded_and_reports_categories_not_private_lines(tmp_path: Path) -> None:
    log = tmp_path / "trcc.log"
    log.write_text(
        "private /srv/private-user/video.mp4\n"
        "DeviceDetached 87ad:70db\n"
        "unload: dropped 192-frame playback for 87ad:70db\n",
        encoding="utf-8",
    )
    cause = recent_trcc_cause(log)
    assert "USB-Geräteabmeldung" in cause
    assert "Wiedergabeobjekt" in cause
    assert "/srv/private-user" not in cause
    assert recent_trcc_cause(tmp_path / "missing.log") == "TRCC-Log nicht lesbar"

    log.write_text(
        "2026-10-03T17:00:00 INFO DisconnectDevice: key=87ad:70db\n"
        "2026-10-03T17:05:00 INFO unload: dropped 192-frame playback for 87ad:70db\n",
        encoding="utf-8",
    )
    since = datetime(2026, 10, 3, 17, 4, 0).timestamp()
    filtered = recent_trcc_cause(log, since_epoch=since)
    assert "Wiedergabeobjekt" in filtered
    assert "expliziter TRCC-Disconnect" not in filtered


def test_ui_exposes_health_status_and_queries_trcc_json() -> None:
    ui = (ROOT / "src" / "thermalright_display_ui.py").read_text(encoding="utf-8")
    cli = (ROOT / "src" / "thermalright_display.py").read_text(encoding="utf-8")
    assert "playback_health_status" in ui
    assert "_playback_health_finished" in ui
    assert "self.cli.status_args()" in ui
    assert "self.cli.video_status_args()" in ui
    assert 'self._command("status", "--json")' in cli
    assert 'self._command("display", "video-status", THERMALRIGHT_DEVICE_KEY)' in cli
    assert "_request_playback_reapply" in ui
    assert "aktives Design wird gezielt neu übertragen" in ui
    assert "Wiedergabe-Neuübertragung zurückgestellt" in ui
    assert PLAYBACK_HEALTH_INTERVAL_MS == 15_000
