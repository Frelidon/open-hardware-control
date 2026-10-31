#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Narrow privileged snapshot/timer and Btrfs discard helper.

The helper accepts no arbitrary command, unit or filesystem path. It is
installed root-owned and invoked through its dedicated Polkit action.
"""

from __future__ import annotations

import json
import os
import pwd
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ElementTree
from pathlib import Path


ACTION_ID = "io.github.Frelidon.OpenHardwareControl.snapshot-control"
ADMIN_ACTION_ID = "io.github.Frelidon.OpenHardwareControl.snapshot-admin"
ADMIN_HELPER_NAME = "open-hardware-control-snapshot-admin-helper"
ADMIN_ACTIONS = frozenset({"create", "delete", "setup-root"})
CONTROL_ACTIONS = frozenset({
    "status", "list", "game", "forever", "until", "desktop", "resume", "limits",
    "grant", "revoke",
})
TIMERS = ("snapper-timeline.timer", "snapper-cleanup.timer")
RESOURCE_SERVICES = ("snapper-timeline.service", "snapper-cleanup.service")
SYSTEMCTL = Path("/usr/bin/systemctl")
SYSTEMD_RUN = Path("/usr/bin/systemd-run")
SNAPPER = Path("/usr/bin/snapper")
FINDMNT = Path("/usr/bin/findmnt")
SNAPPER_CONFIG_DIR = Path("/etc/snapper/configs")
SYSFS_BTRFS = Path("/sys/fs/btrfs")
STATE_DIR = Path("/var/lib/open-hardware-control")
MODE_STATE = STATE_DIR / "snapshot-manager-state.json"
POLICY_STATE = STATE_DIR / "snapshot-manager-policy.json"
TMPFILES_CONFIG = Path("/etc/tmpfiles.d/open-hardware-control-btrfs-discard.conf")
SYSTEMD_UNIT_DIR = Path("/etc/systemd/system")
RESOURCE_DROPIN = "50-open-hardware-control-resources.conf"
RULES_DIR = Path("/etc/polkit-1/rules.d")
GRANTS_DIR = STATE_DIR / "polkit-grants"
RULE_PREFIX = "49-open-hardware-control-snapshot"
RESUME_UNIT = "open-hardware-control-snapshot-resume"
CONFIG_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
DESCRIPTION_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
SUBVOLUME_LINE = re.compile(r'^\s*SUBVOLUME\s*=\s*"([^"\r\n]{1,4096})"\s*$')
MAX_SNAPSHOT_METADATA = 500
MAX_INFO_XML_BYTES = 64 * 1024


def emit(ok: bool, **values: object) -> None:
    print(json.dumps({"ok": bool(ok), **values}, ensure_ascii=False, sort_keys=True), flush=True)


def fail(message: str, code: int = 2) -> "NoReturn":
    emit(False, error=message)
    raise SystemExit(code)


def bounded(raw: object, low: int, high: int, label: str) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        fail(f"{label} must be an integer")
    if not low <= value <= high:
        fail(f"{label} outside allowed range {low}..{high}")
    return value


def run(command: list[str], *, timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"fixed system action failed: {type(exc).__name__}")


def atomic_json(path: Path, payload: dict[str, object], mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    temporary = path.parent / f".{path.name}.tmp-{os.getpid()}"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temporary, flags, mode)
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            json.dump(payload, stream, ensure_ascii=True, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        os.chmod(path, mode)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="ascii"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def timer_property(unit: str, property_name: str) -> bool:
    if unit not in TIMERS or property_name not in {"is-active", "is-enabled"}:
        return False
    completed = run([str(SYSTEMCTL), property_name, unit], timeout=5)
    return completed.returncode == 0


def capture_timers() -> dict[str, dict[str, bool]]:
    return {
        unit: {"active": timer_property(unit, "is-active"), "enabled": timer_property(unit, "is-enabled")}
        for unit in TIMERS
    }


def systemctl(action: str, unit: str) -> None:
    if action not in {"start", "stop", "enable", "disable"} or unit not in TIMERS:
        fail("unsupported timer action")
    completed = run([str(SYSTEMCTL), action, unit])
    if completed.returncode != 0:
        fail(f"cannot {action} {unit}")


def policy_from_args(values: list[str]) -> dict[str, int]:
    if len(values) != 6:
        fail("six bounded resource values required")
    return {
        "desktop_iops": bounded(values[0], 25, 1000, "desktop_iops"),
        "desktop_kbps": bounded(values[1], 8192, 262144, "desktop_kbps"),
        "game_iops": bounded(values[2], 1, 100, "game_iops"),
        "game_kbps": bounded(values[3], 1024, 65536, "game_kbps"),
        "cpu_core_limit": bounded(values[4], 1, 8, "cpu_core_limit"),
        "cpu_percent_per_core": bounded(values[5], 10, 100, "cpu_percent_per_core"),
    }


def allowed_cpu_ids(requested: int) -> tuple[int, ...]:
    """Choose a bounded tail of the helper's permitted logical CPUs."""

    try:
        available = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        available = list(range(max(1, os.cpu_count() or 1)))
    count = max(1, min(int(requested), len(available)))
    return tuple(available[-count:])


def _atomic_text(path: Path, content: str) -> bool:
    """Replace a fixed root-owned configuration only when its content changed."""

    try:
        if path.read_text(encoding="ascii") == content:
            return False
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    temporary = path.parent / f".{path.name}.tmp-{os.getpid()}"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temporary, flags, 0o644)
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o644)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def configure_service_resources(policy: dict[str, int]) -> dict[str, object]:
    """Install fixed systemd cgroup bounds for both known Snapper services."""

    cpus = allowed_cpu_ids(policy["cpu_core_limit"])
    quota = len(cpus) * policy["cpu_percent_per_core"]
    content = (
        "# Managed by Open Hardware Control Snapshot Manager.\n"
        "[Service]\n"
        "Nice=15\n"
        "CPUWeight=10\n"
        "IOWeight=10\n"
        f"CPUQuota={quota}%\n"
        f"AllowedCPUs={','.join(map(str, cpus))}\n"
        "IOSchedulingClass=idle\n"
        "CPUSchedulingPolicy=idle\n"
    )
    changed = False
    for unit in RESOURCE_SERVICES:
        target = SYSTEMD_UNIT_DIR / f"{unit}.d" / RESOURCE_DROPIN
        changed = _atomic_text(target, content) or changed
    if changed:
        completed = run([str(SYSTEMCTL), "daemon-reload"], timeout=15)
        if completed.returncode != 0:
            fail("cannot reload fixed Snapper resource limits")
    return {
        "allowed_cpus": list(cpus),
        "cpu_quota_percent": quota,
        "cpu_percent_per_core": policy["cpu_percent_per_core"],
    }


def discard_targets() -> list[Path]:
    try:
        entries = sorted(SYSFS_BTRFS.iterdir())
    except OSError:
        return []
    result: list[Path] = []
    for entry in entries[:64]:
        if re.fullmatch(r"[0-9a-fA-F-]{36}", entry.name) and (entry / "discard/iops_limit").is_file():
            result.append(entry / "discard")
    return result


def write_sysfs(path: Path, value: int) -> None:
    try:
        path.write_text(f"{int(value)}\n", encoding="ascii")
    except OSError as exc:
        fail(f"cannot write {path.name}: {exc}")


def apply_limits(policy: dict[str, int], mode: str) -> None:
    prefix = "game" if mode in {"game", "until", "forever"} else "desktop"
    iops = policy[f"{prefix}_iops"]
    kbps = policy[f"{prefix}_kbps"]
    max_size = 1_048_576 if prefix == "game" else 8_388_608
    for target in discard_targets():
        write_sysfs(target / "iops_limit", iops)
        write_sysfs(target / "kbps_limit", kbps)
        write_sysfs(target / "max_discard_size", max_size)


def persist_desktop_limits(policy: dict[str, int]) -> None:
    lines = [
        "# Managed by Open Hardware Control Snapshot Manager.\n",
        "# Type Path Mode User Group Age Argument\n",
    ]
    for target in discard_targets():
        relative = target.relative_to(Path("/sys"))
        base = f"/sys/{relative.as_posix()}"
        lines.extend((
            f"w {base}/iops_limit - - - - {policy['desktop_iops']}\n",
            f"w {base}/kbps_limit - - - - {policy['desktop_kbps']}\n",
            f"w {base}/max_discard_size - - - - 8388608\n",
        ))
    temporary = TMPFILES_CONFIG.parent / f".{TMPFILES_CONFIG.name}.tmp-{os.getpid()}"
    temporary.write_text("".join(lines), encoding="ascii")
    os.chmod(temporary, 0o644)
    os.replace(temporary, TMPFILES_CONFIG)


def stop_resume_job() -> None:
    run([str(SYSTEMCTL), "stop", f"{RESUME_UNIT}.timer"], timeout=5)
    run([str(SYSTEMCTL), "reset-failed", f"{RESUME_UNIT}.service"], timeout=5)


def schedule_resume(epoch: int) -> None:
    delay = max(60, epoch - int(time.time()))
    helper = Path("/usr/libexec/open-hardware-control-snapshot-helper")
    if not SYSTEMD_RUN.is_file() or not helper.is_file():
        fail("systemd resume scheduler unavailable")
    stop_resume_job()
    completed = run([
        str(SYSTEMD_RUN), f"--unit={RESUME_UNIT}", f"--on-active={delay}s",
        "--property=Type=oneshot", str(helper), "resume",
    ])
    if completed.returncode != 0:
        fail("cannot schedule snapshot resume")


def pause(mode: str, policy: dict[str, int], until: int = 0) -> None:
    if mode not in {"game", "until", "forever"}:
        fail("unsupported pause mode")
    resources = configure_service_resources(policy)
    existing = read_json(MODE_STATE)
    timers = existing.get("timers") if isinstance(existing.get("timers"), dict) else capture_timers()
    for unit in TIMERS:
        systemctl("stop", unit)
        if mode in {"until", "forever"} and timer_property(unit, "is-enabled"):
            systemctl("disable", unit)
    atomic_json(MODE_STATE, {"schema": 1, "mode": mode, "until": until, "timers": timers})
    atomic_json(POLICY_STATE, {"schema": 2, **policy})
    persist_desktop_limits(policy)
    apply_limits(policy, mode)
    if mode == "until":
        schedule_resume(until)
    emit(True, mode=mode, until=until, timers=timers, resources=resources)


def resume(policy: dict[str, int] | None = None) -> None:
    state = read_json(MODE_STATE)
    stored = read_json(POLICY_STATE)
    active_policy = policy or policy_from_args([
        str(stored.get("desktop_iops", 50)), str(stored.get("desktop_kbps", 16384)),
        str(stored.get("game_iops", 5)), str(stored.get("game_kbps", 2048)),
        str(stored.get("cpu_core_limit", 2)), str(stored.get("cpu_percent_per_core", 50)),
    ])
    resources = configure_service_resources(active_policy)
    timers = state.get("timers") if isinstance(state.get("timers"), dict) else {}
    for unit in TIMERS:
        details = timers.get(unit) if isinstance(timers.get(unit), dict) else {}
        if details.get("enabled"):
            systemctl("enable", unit)
        if details.get("active"):
            systemctl("start", unit)
    apply_limits(active_policy, "desktop")
    persist_desktop_limits(active_policy)
    MODE_STATE.unlink(missing_ok=True)
    stop_resume_job()
    emit(True, mode="desktop", timers=timers, resources=resources)


def apply_resource_policy(policy: dict[str, int]) -> None:
    """Apply the bounded desktop policy without starting or stopping timers."""

    resources = configure_service_resources(policy)
    atomic_json(POLICY_STATE, {"schema": 2, **policy})
    persist_desktop_limits(policy)
    apply_limits(policy, "desktop")
    emit(True, mode="desktop", resources=resources)


def _snapper_subvolume(config: str) -> Path:
    """Resolve only the fixed SUBVOLUME from a root-owned Snapper config."""

    if not CONFIG_NAME.fullmatch(config):
        fail("invalid Snapper configuration")
    source = SNAPPER_CONFIG_DIR / config
    try:
        if source.is_symlink() or not source.is_file() or source.stat().st_size > 128 * 1024:
            fail("invalid Snapper configuration")
        lines = source.read_text(encoding="utf-8", errors="strict").splitlines()
    except (OSError, UnicodeError):
        fail("cannot read Snapper configuration")
    value = next((match.group(1) for line in lines if (match := SUBVOLUME_LINE.fullmatch(line))), "")
    target = Path(value)
    if not value or not target.is_absolute() or DESCRIPTION_CONTROL.search(value):
        fail("invalid Snapper subvolume")
    try:
        return target.resolve(strict=True)
    except OSError:
        fail("Snapper subvolume is unavailable")


def _snapshot_metadata_payload(config: str) -> dict[str, object]:
    """Read Snapper's bounded metadata without its potentially blocking DBus list."""

    snapshot_root = _snapper_subvolume(config) / ".snapshots"
    try:
        if snapshot_root.is_symlink() or not snapshot_root.is_dir():
            fail("Snapper metadata directory is unavailable")
        directories = sorted(
            (entry for entry in snapshot_root.iterdir()
             if entry.name.isdigit() and not entry.is_symlink() and entry.is_dir()),
            key=lambda entry: int(entry.name), reverse=True,
        )[:MAX_SNAPSHOT_METADATA]
    except OSError:
        fail("cannot enumerate Snapper metadata")

    snapshots: list[dict[str, object]] = [{
        "number": 0,
        "date": "",
        "description": "Aktueller Systemzustand",
        "cleanup": "",
    }]
    for directory in directories:
        metadata = directory / "info.xml"
        try:
            if metadata.is_symlink() or not metadata.is_file():
                continue
            if metadata.stat().st_size > MAX_INFO_XML_BYTES:
                continue
            root = ElementTree.fromstring(metadata.read_bytes())
        except (OSError, ElementTree.ParseError):
            continue

        def field(name: str, limit: int) -> str:
            value = root.findtext(name, default="")
            return str(value or "").replace("\x00", "")[:limit]

        snapshots.append({
            "number": int(directory.name),
            "date": field("date", 64),
            "description": field("description", 240),
            "cleanup": field("cleanup", 64),
        })
    return {"snapshots": snapshots}


def list_snapshots(config: str) -> None:
    if not SNAPPER.is_file():
        fail("Snapper is unavailable")
    # ``snapper --jsonout list`` can wait indefinitely for snapperd or for a
    # used-space calculation. The list shown by OHC only needs the immutable
    # per-snapshot info.xml metadata, so read that bounded root-owned catalog
    # directly and never hold the GUI behind Snapper's DBus transaction.
    emit(True, config=config, payload=_snapshot_metadata_payload(config), list_backend="metadata")


def delete_snapshot(config: str, raw_number: str) -> None:
    if not CONFIG_NAME.fullmatch(config) or not SNAPPER.is_file():
        fail("invalid or unavailable Snapper configuration")
    number = bounded(raw_number, 1, 2_147_483_647, "snapshot")
    completed = run([str(SNAPPER), "-c", config, "delete", str(number)], timeout=60)
    if completed.returncode != 0:
        fail("cannot delete Snapper snapshot")
    emit(True, config=config, deleted_snapshot=number)


def create_snapshot(config: str, description: str) -> None:
    if not CONFIG_NAME.fullmatch(config) or not SNAPPER.is_file():
        fail("invalid or unavailable Snapper configuration")
    description = description.strip()
    if not description or len(description) > 160 or DESCRIPTION_CONTROL.search(description):
        fail("invalid snapshot description")
    tagged_description = f"[OHC] {description}"
    completed = run([
        str(SNAPPER), "-c", config, "create", "--description", tagged_description, "--print-number",
    ], timeout=60)
    if completed.returncode != 0:
        fail("cannot create Snapper snapshot")
    number = completed.stdout.strip()
    emit(True, config=config, created_snapshot=number if number.isdigit() else "")


def setup_root_config() -> None:
    """Create only the fixed Snapper root configuration on a Btrfs root."""

    if not SNAPPER.is_file() or not FINDMNT.is_file():
        fail("Snapper or findmnt is unavailable")
    if (SNAPPER_CONFIG_DIR / "root").is_file():
        emit(True, config="root", already_configured=True)
        return
    filesystem = run([str(FINDMNT), "-n", "-o", "FSTYPE", "/"], timeout=5)
    if filesystem.returncode != 0 or filesystem.stdout.strip().casefold() != "btrfs":
        fail("root filesystem is not Btrfs")
    completed = run([str(SNAPPER), "-c", "root", "create-config", "/"], timeout=60)
    if completed.returncode != 0:
        fail("cannot create fixed Snapper root configuration")
    emit(True, config="root", created_config=True)


def invoking_user() -> tuple[int, str]:
    try:
        uid = int(os.environ.get("PKEXEC_UID", ""), 10)
    except ValueError:
        fail("authorization changes require pkexec")
    if uid <= 0:
        fail("desktop user required")
    try:
        account = pwd.getpwuid(uid)
    except KeyError:
        fail("desktop user unavailable")
    return uid, account.pw_name


def set_grant(enabled: bool) -> None:
    uid, username = invoking_user()
    rule = RULES_DIR / f"{RULE_PREFIX}-{uid}.rules"
    marker = GRANTS_DIR / f"snapshot-{uid}"
    if enabled:
        user_literal = json.dumps(username, ensure_ascii=True)
        action_literal = json.dumps(ACTION_ID, ensure_ascii=True)
        content = (
            "// Managed by Open Hardware Control Snapshot Manager.\n"
            "polkit.addRule(function(action, subject) {\n"
            f"    if (action.id == {action_literal} && subject.user == {user_literal}) {{\n"
            "        return polkit.Result.YES;\n    }\n});\n"
        )
        RULES_DIR.mkdir(parents=True, exist_ok=True)
        temporary = RULES_DIR / f".{rule.name}.tmp-{os.getpid()}"
        temporary.write_text(content, encoding="ascii")
        os.chmod(temporary, 0o644)
        os.replace(temporary, rule)
        atomic_json(marker, {"action": ACTION_ID, "uid": uid, "user": username})
    else:
        rule.unlink(missing_ok=True)
        marker.unlink(missing_ok=True)
    emit(True, persistent_authorization=enabled, uid=uid)


def status() -> None:
    emit(True, state=read_json(MODE_STATE), policy=read_json(POLICY_STATE), timers=capture_timers())


def entrypoint_allows(program: str, action: str) -> bool:
    """Keep persistent automation authority away from manual write actions."""

    name = Path(program).name
    if name == ADMIN_HELPER_NAME:
        return action in ADMIN_ACTIONS
    if name == "open-hardware-control-snapshot-helper":
        return action in CONTROL_ACTIONS
    # Source-tree execution is retained only for non-privileged unit tests.
    return name == "helper.py" and action in ADMIN_ACTIONS | CONTROL_ACTIONS


def main(argv: list[str]) -> int:
    if os.geteuid() != 0:
        fail("helper must run through Polkit")
    action = argv[1] if len(argv) > 1 else ""
    if not entrypoint_allows(argv[0], action):
        fail("helper entry point does not permit this action")
    if action == "status" and len(argv) == 2:
        status()
    elif action == "list" and len(argv) == 3:
        list_snapshots(argv[2])
    elif action == "delete" and len(argv) == 4:
        delete_snapshot(argv[2], argv[3])
    elif action == "create" and len(argv) == 4:
        create_snapshot(argv[2], argv[3])
    elif action == "setup-root" and len(argv) == 2:
        setup_root_config()
    elif action in {"game", "forever"} and len(argv) == 8:
        policy = policy_from_args(argv[2:])
        pause(action, policy)
    elif action == "until" and len(argv) == 9:
        deadline = bounded(argv[2], int(time.time()) + 60, int(time.time()) + 366 * 86400, "until")
        policy = policy_from_args(argv[3:])
        pause("until", policy, deadline)
    elif action == "desktop" and len(argv) == 8:
        resume(policy_from_args(argv[2:]))
    elif action == "limits" and len(argv) == 8:
        apply_resource_policy(policy_from_args(argv[2:]))
    elif action == "resume" and len(argv) == 2:
        resume()
    elif action == "grant" and len(argv) == 2:
        set_grant(True)
    elif action == "revoke" and len(argv) == 2:
        set_grant(False)
    else:
        fail("unsupported helper request")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
