#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Minimal privileged NCT6687 hwmon helper for Open Hardware Control.

This program is intentionally tiny and accepts no arbitrary filesystem paths.
It resolves the first Linux hwmon controller whose name starts with nct6687 and
only permits bounded writes to pwmN, pwmN_enable and fan_control_watchdog. It
may also install/remove one fixed per-caller Polkit rule for this helper action.
It is designed to be invoked through pkexec/polkit while the GUI stays
unprivileged.
"""
from __future__ import annotations

import json
import os
import pwd
import sys
from pathlib import Path

HWMON_ROOT = Path("/sys/class/hwmon")
MAX_CHANNEL = 8
POLKIT_ACTION_ID = "io.github.Frelidon.OpenHardwareControl.fan-control"
PERSISTENT_RULES_DIR = Path("/etc/polkit-1/rules.d")
PERSISTENT_RULE_PREFIX = "49-open-hardware-control-fan"


def fail(message: str, code: int = 2) -> "NoReturn":
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False), flush=True)
    raise SystemExit(code)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="ascii", errors="strict").strip()
    except OSError as exc:
        fail(f"cannot read {path.name}: {exc}")


def read_int(path: Path) -> int | None:
    try:
        return int(read_text(path))
    except (TypeError, ValueError):
        return None


def write_value(path: Path, value: int) -> None:
    try:
        path.write_text(f"{int(value)}\n", encoding="ascii")
    except OSError as exc:
        fail(f"cannot write {path.name}: {exc}")


def invoking_desktop_user() -> tuple[int, str]:
    """Resolve the original pkexec caller; never trust an arbitrary username."""

    raw_uid = os.environ.get("PKEXEC_UID", "")
    try:
        uid = int(raw_uid, 10)
    except ValueError:
        fail("persistent authorization must be changed through pkexec")
    if uid <= 0:
        fail("persistent authorization is available only for a desktop user")
    try:
        account = pwd.getpwuid(uid)
    except KeyError:
        fail("pkexec caller account does not exist")
    if not account.pw_name or account.pw_uid != uid:
        fail("pkexec caller account is invalid")
    return uid, account.pw_name


def persistent_rule_path(uid: int) -> Path:
    return PERSISTENT_RULES_DIR / f"{PERSISTENT_RULE_PREFIX}-{int(uid)}.rules"


def set_persistent_authorization(enabled: bool) -> None:
    """Install/remove one exact-user rule for this helper's fixed action."""

    uid, username = invoking_desktop_user()
    rule_path = persistent_rule_path(uid)
    if enabled:
        # JSON string escaping is valid JavaScript string escaping too.  This
        # keeps even unusual account names from changing the rule program.
        user_literal = json.dumps(username, ensure_ascii=True)
        action_literal = json.dumps(POLKIT_ACTION_ID, ensure_ascii=True)
        content = (
            "// Managed by Open Hardware Control; remove from the app or delete this file as root.\n"
            "polkit.addRule(function(action, subject) {\n"
            f"    if (action.id == {action_literal} && subject.user == {user_literal}) {{\n"
            "        return polkit.Result.YES;\n"
            "    }\n"
            "});\n"
        )
        try:
            PERSISTENT_RULES_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)
            temporary = PERSISTENT_RULES_DIR / f".{rule_path.name}.tmp-{os.getpid()}"
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(temporary, flags, 0o644)
            try:
                with os.fdopen(descriptor, "w", encoding="ascii") as handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, rule_path)
                os.chmod(rule_path, 0o644)
            finally:
                try:
                    temporary.unlink()
                except FileNotFoundError:
                    pass
        except OSError as exc:
            fail(f"cannot install persistent authorization: {exc}")
    else:
        try:
            rule_path.unlink(missing_ok=True)
        except OSError as exc:
            fail(f"cannot remove persistent authorization: {exc}")
    print(
        json.dumps(
            {"ok": True, "persistent_authorization": bool(enabled), "uid": uid},
            ensure_ascii=False,
            sort_keys=True,
        ),
        flush=True,
    )


def controller() -> Path:
    try:
        entries = sorted(HWMON_ROOT.glob("hwmon*"))
    except OSError as exc:
        fail(f"cannot enumerate hwmon: {exc}")
    for entry in entries:
        name_path = entry / "name"
        try:
            name = name_path.read_text(encoding="ascii", errors="replace").strip().casefold()
        except OSError:
            continue
        if name.startswith("nct6687"):
            return entry
    fail("no nct6687 hwmon controller found")


def parse_channel(raw: str) -> int:
    try:
        value = int(raw, 10)
    except ValueError:
        fail("channel must be an integer")
    if not 1 <= value <= MAX_CHANNEL:
        fail("channel outside allowed range 1..8")
    return value


def bounded_int(raw: str, low: int, high: int, label: str) -> int:
    try:
        value = int(raw, 10)
    except ValueError:
        fail(f"{label} must be an integer")
    if not low <= value <= high:
        fail(f"{label} outside allowed range {low}..{high}")
    return value


def paths_for_channel(root: Path, channel: int) -> tuple[Path, Path, Path]:
    pwm = root / f"pwm{channel}"
    enable = root / f"pwm{channel}_enable"
    rpm = root / f"fan{channel}_input"
    if not pwm.is_file():
        fail(f"pwm{channel} is not exposed")
    if not enable.is_file():
        fail(f"pwm{channel}_enable is not exposed")
    return pwm, enable, rpm


def emit(root: Path, channel: int | None = None, *, target_pwm: int | None = None) -> None:
    payload: dict[str, object] = {
        "ok": True,
        "controller": read_text(root / "name"),
    }
    if channel is not None:
        pwm, enable, rpm = paths_for_channel(root, channel)
        payload.update(
            {
                "channel": channel,
                "pwm": read_int(pwm),
                "enable": read_int(enable),
                "rpm": read_int(rpm) if rpm.is_file() else None,
            }
        )
    if target_pwm is not None:
        payload["target_pwm"] = target_pwm
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)


def dispatch(root: Path, args: list[str]) -> None:
    """Execute one already authenticated, strictly bounded helper operation."""

    if not args:
        fail("missing operation")
    op = args[0]

    if op == "probe" and len(args) == 1:
        emit(root)
        return

    if op == "set-percent" and len(args) == 3:
        channel = parse_channel(args[1])
        percent = bounded_int(args[2], 0, 100, "percent")
        pwm, enable, _rpm = paths_for_channel(root, channel)
        target = int(round(percent * 255 / 100))
        # The current nct6687d driver saves the original firmware curve on the
        # first manual request and restores it when pwmN_enable=2 is written.
        write_value(enable, 1)
        write_value(pwm, target)
        emit(root, channel, target_pwm=target)
        return

    if op == "restore-firmware" and len(args) == 2:
        channel = parse_channel(args[1])
        _pwm, enable, _rpm = paths_for_channel(root, channel)
        write_value(enable, 2)
        emit(root, channel)
        return

    if op == "restore-snapshot" and len(args) == 4:
        channel = parse_channel(args[1])
        old_pwm = bounded_int(args[2], 0, 255, "pwm")
        old_enable = bounded_int(args[3], 1, 99, "enable")
        pwm, enable, _rpm = paths_for_channel(root, channel)
        if old_enable in (2, 99):
            write_value(enable, 2)
        elif old_enable == 1:
            write_value(enable, 1)
            write_value(pwm, old_pwm)
        else:
            fail("unsupported snapshot enable mode")
        emit(root, channel)
        return

    if op == "watchdog" and len(args) == 2:
        timeout = bounded_int(args[1], 0, 300, "watchdog timeout")
        path = root / "fan_control_watchdog"
        if not path.is_file():
            fail("fan_control_watchdog is not exposed")
        write_value(path, timeout)
        print(
            json.dumps({"ok": True, "controller": read_text(root / "name"), "watchdog": read_int(path)}),
            flush=True,
        )
        return

    fail("unsupported operation or arguments")


def main(argv: list[str]) -> int:
    if os.geteuid() != 0:
        fail("helper must run as root through pkexec", 77)
    if len(argv) < 2:
        fail("missing operation")
    op = argv[1]
    if op in {"grant-persistent", "revoke-persistent"} and len(argv) == 2:
        set_persistent_authorization(op == "grant-persistent")
        return 0
    root = controller()

    if op == "session" and len(argv) == 2:
        print(json.dumps({"ok": True, "session": "ready"}), flush=True)
        for raw_line in sys.stdin:
            if len(raw_line) > 512:
                fail("session request too long")
            try:
                request = json.loads(raw_line)
            except (TypeError, ValueError, json.JSONDecodeError):
                fail("invalid session request")
            if not isinstance(request, list) or not all(isinstance(item, str) for item in request):
                fail("session request must be a string list")
            # Re-discover the controller for every request so a driver reload
            # or resume-time hwmon renumbering cannot leave the privileged
            # session writing through an obsolete sysfs directory.
            dispatch(controller(), request)
        return 0

    dispatch(root, argv[1:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
