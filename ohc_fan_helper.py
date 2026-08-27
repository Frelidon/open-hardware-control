#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Minimal privileged NCT6687 hwmon helper for Open Hardware Control.

This program is intentionally tiny and accepts no arbitrary filesystem paths.
It resolves the first Linux hwmon controller whose name starts with nct6687 and
only permits bounded writes to pwmN, pwmN_enable and fan_control_watchdog.
It is designed to be invoked through pkexec/polkit while the GUI stays
unprivileged.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HWMON_ROOT = Path("/sys/class/hwmon")
MAX_CHANNEL = 8


def fail(message: str, code: int = 2) -> "NoReturn":
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
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
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def main(argv: list[str]) -> int:
    if os.geteuid() != 0:
        fail("helper must run as root through pkexec", 77)
    if len(argv) < 2:
        fail("missing operation")
    op = argv[1]
    root = controller()

    if op == "probe" and len(argv) == 2:
        emit(root)
        return 0

    if op == "set-percent" and len(argv) == 4:
        channel = parse_channel(argv[2])
        percent = bounded_int(argv[3], 0, 100, "percent")
        pwm, enable, _rpm = paths_for_channel(root, channel)
        target = int(round(percent * 255 / 100))
        # The current nct6687d driver saves the original firmware curve on the
        # first manual request and restores it when pwmN_enable=2 is written.
        write_value(enable, 1)
        write_value(pwm, target)
        emit(root, channel, target_pwm=target)
        return 0

    if op == "restore-firmware" and len(argv) == 3:
        channel = parse_channel(argv[2])
        _pwm, enable, _rpm = paths_for_channel(root, channel)
        write_value(enable, 2)
        emit(root, channel)
        return 0

    if op == "restore-snapshot" and len(argv) == 5:
        channel = parse_channel(argv[2])
        old_pwm = bounded_int(argv[3], 0, 255, "pwm")
        old_enable = bounded_int(argv[4], 1, 99, "enable")
        pwm, enable, _rpm = paths_for_channel(root, channel)
        if old_enable in (2, 99):
            # Let the driver restore the original saved MSI curve itself.
            write_value(enable, 2)
        elif old_enable == 1:
            write_value(enable, 1)
            write_value(pwm, old_pwm)
        else:
            fail("unsupported snapshot enable mode")
        emit(root, channel)
        return 0

    if op == "watchdog" and len(argv) == 3:
        timeout = bounded_int(argv[2], 0, 300, "watchdog timeout")
        path = root / "fan_control_watchdog"
        if not path.is_file():
            fail("fan_control_watchdog is not exposed")
        write_value(path, timeout)
        print(json.dumps({"ok": True, "controller": read_text(root / "name"), "watchdog": read_int(path)}))
        return 0

    fail("unsupported operation or arguments")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
