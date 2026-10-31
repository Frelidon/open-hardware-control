"""Ubuntu USB ownership reports must never trigger a foreign-owner restart."""
import ast
from pathlib import Path
import sys
from types import MethodType, SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from modules.levita_daemon_health.v1_1.model import (
    DaemonMemorySample,
    backend_failure_detail,
    is_probable_daemon_failure,
    is_usb_owner_conflict,
)
from modules.lcd_runtime.v1_1.design_state import DesignState
from modules.localization.v1_0 import UI_TRANSLATIONS

BUSY = "USB device abcd:1234 interface is in use by another process. Close any other TRCC instances and try again."
HINT = "  hint: udev rules not installed — device access may require root."
OUTPUT = "Not attached: abcd:1234\n" + BUSY + "\n" + HINT


def method(name, **extra):
    tree = ast.parse((ROOT / "src/thermalright_display_ui.py").read_text())
    node = next(item for item in ast.walk(tree) if isinstance(item, ast.FunctionDef) and item.name == name)
    env = dict(backend_failure_detail=backend_failure_detail,
               is_usb_owner_conflict=is_usb_owner_conflict,
               is_probable_daemon_failure=is_probable_daemon_failure,
               find_trcc_daemon_memory=lambda: None,
               is_owned_trcc_daemon_pid=lambda _pid: False,
               PLAYBACK_RECOVERY_COOLDOWN_SECONDS=30,
               time=SimpleNamespace(monotonic=lambda: 100), LEVITA_APPLY_COOLDOWN_SECONDS=10,
               QProcess=SimpleNamespace(ExitStatus=SimpleNamespace(NormalExit="normal", CrashExit="crash")))
    env.update(extra)
    exec(compile(ast.Module([node], type_ignores=[]), "actual_lcd_method", "exec"), env)
    return env[name]


def host(*, ubuntu=True):
    events = []
    settings = SimpleNamespace(values={"thermalright/autostart_enabled": True,
                                       "thermalright/start_media": "saved-design.mp4"})
    state = DesignState(settings)
    state.capture([(("trcc", "load", "prepared-design"), False)], True)
    result = SimpleNamespace(
        ubuntu_runtime=ubuntu, events=events, settings=settings, design_state=state,
        window=lambda: SimpleNamespace(tr_static=lambda text: text),
        remember_design_after_apply=True, startup_apply_active=True, startup_retry_count=0,
        preexisting_trcc_daemon_pid=None, owned_trcc_daemon_pid=None,
        pending_apply_sequence=list(state.desired.sequence), apply_retry_remaining=1,
        stream_should_run=True, shutdown_started=False,
        test_mode=SimpleNamespace(isChecked=lambda: False),
        apply_start_timer=SimpleNamespace(stop=lambda: events.append("apply-stop"),
            start=lambda: events.append("apply-start"), setInterval=lambda delay: events.append(("interval", delay))),
        apply_cooldown_timer=SimpleNamespace(stop=lambda: events.append("cooldown-stop")),
        _status=lambda text, **kwargs: events.append((text, kwargs)),
        _request_daemon_restart=lambda reason: events.append(("daemon-restart", reason)) or True,
        _schedule_startup_retry=lambda detail: events.append(("startup-retry", detail)),
        _daemon_stream_started=lambda: events.append("confirmed"),
    )
    def stop_stream():
        result.stream_should_run = False
        events.append("stream-stop")
    result._stop_stream_client = stop_stream
    result._stop_for_usb_owner_conflict = MethodType(method("_stop_for_usb_owner_conflict"), result)
    return result


def test_busy_is_explicit_and_hint_is_not_a_primary_failure():
    assert is_usb_owner_conflict(OUTPUT.upper())
    assert not is_usb_owner_conflict(HINT)
    assert not is_usb_owner_conflict("USB read failed: [Errno 110] Operation timed out")
    assert backend_failure_detail(OUTPUT) == BUSY
    assert backend_failure_detail("Connection refused\n" + HINT) == "Connection refused"
    assert backend_failure_detail(HINT) == ""
    assert backend_failure_detail("") == ""
    # Retain the established legacy classifier; only Ubuntu's UI intercepts busy.
    assert is_probable_daemon_failure(BUSY)
    assert is_probable_daemon_failure("peer closed without sending data")


def test_ubuntu_apply_busy_stops_only_own_pending_work_and_preserves_saved_intent():
    page = host()
    saved = dict(page.settings.values)
    request = page.design_state.desired
    method("_apply_finished")(page, False, OUTPUT)
    assert not page.startup_apply_active and not page.stream_should_run
    assert page.pending_apply_sequence == [] and page.apply_retry_remaining == 0
    assert not page.remember_design_after_apply
    assert page.settings.values == saved and page.design_state.desired is request
    assert "apply-stop" in page.events and "cooldown-stop" in page.events
    assert not any(isinstance(event, tuple) and event[0] in {"daemon-restart", "startup-retry"}
                   for event in page.events)
    assert "anderes Programm belegt" in page.events[-1][0]
    assert "udev" not in page.events[-1][0]
    # The same prepared request remains available after explicit owner release;
    # it reuses the existing serialized queue and changes no saved setting.
    assert page.design_state.recover(page)
    assert page.pending_apply_sequence == list(request.sequence)
    assert page.events[-1] == "apply-start" and page.settings.values == saved


def test_ubuntu_busy_from_exact_session_owned_daemon_recovers_once_automatically():
    page = host()
    page.owned_trcc_daemon_pid = 7185
    page._request_daemon_restart = lambda reason, **kwargs: page.events.append(
        ("daemon-restart", reason, kwargs)
    ) or True
    page._log = lambda message: page.events.append(("log", message))
    page._stop_for_usb_owner_conflict = MethodType(method(
        "_stop_for_usb_owner_conflict",
        find_trcc_daemon_memory=lambda: DaemonMemorySample(7185, 4096),
        is_owned_trcc_daemon_pid=lambda pid: pid == 7185,
    ), page)

    method("_apply_finished")(page, False, OUTPUT)

    recovery = next(event for event in page.events if event[0] == "daemon-restart")
    assert "Eigener TRCC-Daemon" in recovery[1]
    assert recovery[2]["cooldown_seconds"] == 30
    assert page.startup_apply_active
    assert page.pending_apply_sequence == []
    assert any(event[0] == "log" and "PID 7185" in event[1] for event in page.events)


def test_untracked_or_pid_mismatched_daemon_is_never_restarted():
    for observed_pid, trusted in ((7185, False), (9999, True)):
        page = host()
        page.owned_trcc_daemon_pid = 7185
        page._stop_for_usb_owner_conflict = MethodType(method(
            "_stop_for_usb_owner_conflict",
            find_trcc_daemon_memory=lambda pid=observed_pid: DaemonMemorySample(pid, 4096),
            is_owned_trcc_daemon_pid=lambda _pid, value=trusted: value,
        ), page)
        method("_apply_finished")(page, False, OUTPUT)
        assert not any(
            isinstance(event, tuple) and event[0] == "daemon-restart"
            for event in page.events
        )


def test_fedora_apply_keeps_established_recovery_without_new_conflict_branch():
    page = host(ubuntu=False)
    method("_apply_finished")(page, False, OUTPUT)
    assert page.startup_apply_active and page.stream_should_run
    assert any(isinstance(event, tuple) and event[0] == "daemon-restart" for event in page.events)
    assert "apply-stop" not in page.events
    assert not page._stop_for_usb_owner_conflict(OUTPUT)


def test_ubuntu_real_ipc_failure_and_one_timeout_retry_are_preserved():
    page = host()
    method("_apply_finished")(page, False, "peer closed without sending data")
    assert any(isinstance(event, tuple) and event[0] == "daemon-restart" for event in page.events)
    page = host()
    apply = method("_apply_finished")
    apply(page, False, "USB read failed: [Errno 110] Operation timed out")
    assert page.apply_retry_remaining == 0 and ("interval", 5000) in page.events
    assert page.pending_apply_sequence and page.startup_apply_active
    apply(page, False, "USB read failed: [Errno 110] Operation timed out")
    assert not page.startup_apply_active and not page.pending_apply_sequence
    assert "weitere automatische Versuche" in page.events[-1][0]


def test_success_and_non_busy_errors_do_not_cancel_accepted_playback():
    page = host()
    method("_apply_finished")(page, True, "sent frame")
    assert page.events == ["confirmed"]
    assert not page._stop_for_usb_owner_conflict("Connection refused")


@pytest.mark.parametrize("ubuntu", [True, False])
def test_stream_busy_is_not_misdiagnosed_as_fps_failure_on_ubuntu(ubuntu):
    page = host(ubuntu=ubuntu)
    page._capture_stream_output = lambda: None
    page.stream_output_tail = OUTPUT
    page.stream_stop_requested = False
    page.stream_restart_timer = SimpleNamespace(isActive=lambda: False)
    page.lcd_runtime = SimpleNamespace(stream_done=lambda *args: None, stream_reason="")
    page.stream_started_at = 90
    finish = method("_on_stream_finished", daemon_owns_playback=lambda text: False,
                    fallback_lcd_fps=lambda value: pytest.fail("busy is not an FPS failure"))
    finish(page, 1, "normal")
    restarts = [event for event in page.events if isinstance(event, tuple) and event[0] == "daemon-restart"]
    assert bool(restarts) is not ubuntu
    assert page.stream_should_run is not ubuntu


def test_busy_health_reply_cannot_start_another_recovery():
    page = host()
    page.playback_health_probe_active = True
    method("_playback_health_finished")(page, False, OUTPUT)
    assert not page.playback_health_probe_active and not page.stream_should_run
    assert "anderes Programm belegt" in page.events[-1][0]


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
@pytest.mark.parametrize("state", ["apply", "stream", "health"])
def test_each_conflict_state_uses_current_language_for_both_status_labels(language, state):
    page = host()
    current_language = ["de"]
    source = (
        "Levita-Display ist durch ein anderes Programm belegt · keine automatische Freigabe; "
        "das andere Programm schließen und das Design erneut anwenden"
    )
    page.window = lambda: SimpleNamespace(
        tr_static=lambda text: UI_TRANSLATIONS[current_language[0]].get(text, text))
    labels = []
    page.playback_health_status = SimpleNamespace(setText=labels.append)
    # A new runtime state must also honor a language changed since construction.
    page._stop_for_usb_owner_conflict(OUTPUT)
    assert labels[-1] == UI_TRANSLATIONS["de"][source]
    current_language[0] = language
    if state == "apply":
        method("_apply_finished")(page, False, OUTPUT)
    elif state == "stream":
        page.stream_should_run = True
        page.stream_stop_requested = False
        page._capture_stream_output = lambda: None
        page.stream_output_tail = OUTPUT
        page.lcd_runtime = SimpleNamespace(stream_done=lambda *args: None)
        method("_on_stream_finished")(page, 1, "normal")
    else:
        page.playback_health_probe_active = True
        method("_playback_health_finished")(page, False, OUTPUT)
    expected = UI_TRANSLATIONS[language][source]
    assert labels[-1] == expected and page.events[-1] == (expected, {"error": True})
    assert language == "de" or expected != source
