#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Strict local-only OpenRGB CLI/SDK adapter.

Open Hardware Control never performs direct RGB hardware discovery here.  It
only talks to an already running OpenRGB SDK server on a loopback address.  The
explicit ``--client`` argument and a reachability check prevent the OpenRGB CLI
from silently falling back to standalone hardware access.
"""

from __future__ import annotations

import ipaddress
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

OPENRGB_DEFAULT_PORT = 6742
MAX_OPENRGB_DEVICE_ID = 4096
MAX_OPENRGB_LEDS = 4096
MAX_OPENRGB_BATCH_DEVICES = 64
SAFE_MODE_RE = re.compile(r"^[\w .+()'/-]{1,80}$", re.UNICODE)
HEX_COLOR_RE = re.compile(r"^[0-9a-fA-F]{6}$")
DEVICE_HEADER_RE = re.compile(r"^\s*(\d+)\s*:\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^\s*(Type|Description|Version|Location|Serial|Modes|Zones|LEDs)\s*:\s*(.*?)\s*$", re.IGNORECASE)
class OpenRGBError(RuntimeError):
    pass


def openrgb_subprocess_environment(
    source: dict[str, str] | None = None,
) -> dict[str, str]:
    """Return an environment that cannot map an OpenRGB helper window.

    OpenRGB is a Qt GUI binary even for ``--version`` and SDK-client commands.
    Every subprocess path therefore needs the same explicit offscreen boundary
    as the long-lived managed server.
    """

    environment = dict(os.environ if source is None else source)
    environment["QT_QPA_PLATFORM"] = "offscreen"
    return environment


def running_named_process_ids(
    names: Iterable[str], proc_root: str | Path = "/proc"
) -> tuple[int, ...]:
    """Return exact process-name matches without invoking another process."""

    accepted = {str(name).casefold() for name in names if str(name).strip()}
    if not accepted:
        return ()
    root = Path(proc_root)
    found: list[int] = []
    try:
        entries = tuple(root.iterdir())
    except OSError:
        return ()
    for entry in entries:
        if not entry.name.isdecimal():
            continue
        try:
            command_name = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()
            if not command_name:
                command_line = (entry / "cmdline").read_bytes().split(b"\0", 1)[0]
                command_name = Path(command_line.decode("utf-8", "replace")).name
        except OSError:
            continue
        if command_name.casefold() in accepted:
            found.append(int(entry.name))
    return tuple(sorted(set(found)))


def running_openrgb_process_ids(proc_root: str | Path = "/proc") -> tuple[int, ...]:
    """Return OpenRGB process IDs without invoking another process.

    A separately opened OpenRGB GUI can own RGB hardware even when its SDK
    server is disabled.  A port-only collision check therefore misses exactly
    the situation that can make otherwise valid writes appear ineffective.
    ``/proc`` is read directly so this check neither changes nor terminates any
    user process.  Unreadable or already-finished entries are ignored.
    """

    return running_named_process_ids(("openrgb",), proc_root)


def running_ckb_next_process_ids(proc_root: str | Path = "/proc") -> tuple[int, ...]:
    """Return ckb-next GUI/daemon PIDs for read-only ownership diagnostics."""

    return running_named_process_ids(("ckb-next", "ckb-next-daemon", "ckb-next-anim"), proc_root)


def is_suspicious_inventory_drop(
    previous_count: int,
    expected_count: int,
    candidate_count: int,
) -> bool:
    """Return whether a discovery result is probably an incomplete warm-up scan.

    OpenRGB can briefly answer while only its early DRAM controllers have
    finished probing.  A typical affected machine therefore changes from a
    known seven-device inventory to only two entries.  Small hot-plug changes
    remain valid; only a loss of at least half of a previously healthy
    inventory is treated as suspicious and rechecked.
    """

    previous = max(0, int(previous_count))
    expected = max(0, int(expected_count))
    candidate = max(0, int(candidate_count))
    reference = max(previous, expected)
    if reference < 4 or candidate >= reference:
        return False
    missing = reference - candidate
    return candidate <= max(2, reference // 2) and missing >= max(2, reference // 2)


def is_confirmed_small_inventory_shrink(
    expected_count: int,
    current_count: int,
    stable_for_seconds: float,
) -> bool:
    """Accept a stable one/two-device removal without weakening cold-start protection."""

    expected = max(0, int(expected_count))
    current = max(0, int(current_count))
    missing = expected - current
    return (
        expected >= 4
        and current >= 3
        and 1 <= missing <= 2
        and float(stable_for_seconds) >= 2.5
    )


def is_openrgb_configuration_error(output: str) -> bool:
    """Recognize safe configuration/state errors that must not quarantine hardware."""

    detail = str(output or "").casefold()
    return any(
        marker in detail
        for marker in (
            "konfiguration_erforderlich",
            "plausibilitaet_pruefen",
            "zonenkonfiguration unvollständig",
            "zonengrössen nicht bestätigt",
            "keine gültige zahl steuerbarer farben",
            "meldet 0 angelegte leds",
        )
    )


def is_openrgb_apply_options_crash(returncode: int, output: str) -> bool:
    """Recognize the Fedora OpenRGB rc2 ApplyOptions assertion.

    Depending on how QProcess receives SIGABRT, the exit code can be reported
    as 6, 134 or a negative signal value.  The assertion text is therefore the
    authoritative discriminator; ordinary OpenRGB errors must not quarantine a
    device after their first occurrence.
    """

    if int(returncode) == 0:
        return False
    detail = str(output or "").casefold()
    vector_assertion = (
        "stl_vector.h" in detail
        and ("std::vector" in detail or "assertion" in detail)
    )
    bounds_assertion = "assertion '__n < this->size()' failed" in detail
    apply_options_abort = (
        "applyoptions" in detail
        and any(marker in detail for marker in ("assert", "sigabrt", "aborted"))
    )
    return vector_assertion or bounds_assertion or apply_options_abort


@dataclass(frozen=True)
class OpenRGBDevice:
    index: int
    name: str
    device_type: str = "Unbekannt"
    description: str = ""
    version: str = ""
    location: str = ""
    serial: str = ""
    modes: tuple[str, ...] = ()
    zones: tuple[str, ...] = ()
    leds: tuple[str, ...] = ()

    @property
    def led_count(self) -> int:
        return max(1, min(MAX_OPENRGB_LEDS, len(self.leds) or 1))

    @property
    def reported_led_count(self) -> int:
        """Return only LEDs actually listed by OpenRGB, without a UI fallback."""

        return min(MAX_OPENRGB_LEDS, len(self.leds))

    @property
    def supports_direct(self) -> bool:
        return any(mode.casefold() == "direct" for mode in self.modes)


def _parse_named_values(value: str) -> tuple[str, ...]:
    clean = value.replace("[", " ").replace("]", " ").strip()
    if not clean:
        return ()
    try:
        values = shlex.split(clean)
    except ValueError:
        values = clean.split()
    return tuple(item.strip() for item in values if item.strip())


def parse_device_listing(output: str) -> list[OpenRGBDevice]:
    devices: list[OpenRGBDevice] = []
    current: dict[str, object] | None = None

    def finish() -> None:
        nonlocal current
        if current is None:
            return
        devices.append(
            OpenRGBDevice(
                index=int(current["index"]),
                name=str(current["name"]),
                device_type=str(current.get("type") or "Unbekannt"),
                description=str(current.get("description") or ""),
                version=str(current.get("version") or ""),
                location=str(current.get("location") or ""),
                serial=str(current.get("serial") or ""),
                modes=tuple(current.get("modes") or ()),
                zones=tuple(current.get("zones") or ()),
                leds=tuple(current.get("leds") or ()),
            )
        )
        current = None

    active_list_field = ""
    for raw_line in output.replace("\r", "").splitlines():
        line = raw_line.rstrip()
        header = DEVICE_HEADER_RE.match(line)
        if header and 0 <= int(header.group(1)) <= MAX_OPENRGB_DEVICE_ID:
            finish()
            current = {"index": int(header.group(1)), "name": header.group(2).strip()}
            active_list_field = ""
            continue
        if current is None:
            continue
        field = FIELD_RE.match(line)
        if field:
            key = field.group(1).casefold()
            value = field.group(2).strip()
            if key in {"modes", "zones", "leds"}:
                current[key] = _parse_named_values(value)
                active_list_field = key
            else:
                current[key] = value
                active_list_field = ""
            continue
        # Very long mode/zone/LED lists may be wrapped by the CLI.  Continuation
        # lines are accepted only while a known list field is active.
        if active_list_field and line.startswith((" ", "\t")):
            previous = tuple(current.get(active_list_field) or ())
            current[active_list_field] = previous + _parse_named_values(line.strip())
    finish()
    return devices


class OpenRGBClient:
    def __init__(self, executable: str | None = None, address: str = "127.0.0.1", port: int = OPENRGB_DEFAULT_PORT):
        parsed_address = ipaddress.ip_address(address)
        if not parsed_address.is_loopback:
            raise ValueError("OpenRGB darf nur über eine lokale Loopback-Adresse angesprochen werden.")
        if not 1024 <= int(port) <= 65535:
            raise ValueError("Der OpenRGB-Port muss zwischen 1024 und 65535 liegen.")
        resolved = executable or shutil.which("openrgb") or shutil.which("OpenRGB")
        self.executable = str(Path(resolved).resolve()) if resolved else ""
        self.sdk_helper = str(Path(__file__).with_name("openrgb_sdk.py").resolve())
        self.address = str(parsed_address)
        self.port = int(port)

    @property
    def endpoint(self) -> str:
        address = f"[{self.address}]" if ":" in self.address else self.address
        return f"{address}:{self.port}"

    @property
    def installed(self) -> bool:
        return bool(self.executable and Path(self.executable).is_file())

    def server_reachable(self, timeout: float = 0.25) -> bool:
        try:
            with socket.create_connection((self.address, self.port), timeout=max(0.05, min(2.0, timeout))):
                return True
        except OSError:
            return False

    def _require_client(self) -> None:
        if not self.installed:
            raise OpenRGBError("OpenRGB ist nicht installiert.")
        if not self.server_reachable():
            raise OpenRGBError(
                f"Der lokale OpenRGB-SDK-Server ist unter {self.endpoint} nicht erreichbar."
            )

    def client_command(self, *arguments: str) -> list[str]:
        self._require_client()
        return [self.executable, "--client", self.endpoint, *arguments]

    def managed_server_command(self, config_directory: str | Path) -> list[str]:
        """Build the private server command owned by Open Hardware Control.

        ``--noautoconnect`` is important: the managed server must discover the
        hardware itself and must never become a client of an unrelated server.
        A private absolute configuration directory avoids changing a user's
        normal OpenRGB GUI configuration.
        """

        if not self.installed:
            raise OpenRGBError("OpenRGB ist nicht installiert.")
        config = Path(config_directory).expanduser().resolve()
        if not config.is_absolute():
            raise ValueError("Das Verzeichnis der RGB-Engine muss absolut sein.")
        return [
            self.executable,
            "--server",
            "--server-port", str(self.port),
            "--noautoconnect",
            "--loglevel", "error",
            "--config", str(config),
        ]

    def list_command(self) -> list[str]:
        return self.client_command("--list-devices")

    @staticmethod
    def _device_id(device_id: int) -> str:
        value = int(device_id)
        if not 0 <= value <= MAX_OPENRGB_DEVICE_ID:
            raise ValueError("Ungültige OpenRGB-Gerätenummer.")
        return str(value)

    @staticmethod
    def _colors(colors: Iterable[str]) -> str:
        clean = [str(color).strip().lstrip("#").lower() for color in colors]
        if not clean or len(clean) > MAX_OPENRGB_LEDS or any(not HEX_COLOR_RE.fullmatch(color) for color in clean):
            raise ValueError("Ungültige oder zu große OpenRGB-Farbliste.")
        return ",".join(clean)

    def color_command(self, device_id: int, colors: Iterable[str], *, direct: bool = False) -> list[str]:
        arguments = ["--device", self._device_id(device_id)]
        if direct:
            arguments += ["--mode", "direct"]
        arguments += ["--color", self._colors(colors)]
        return self.client_command(*arguments)

    def sdk_color_command(
        self,
        device_id: int,
        colors: Iterable[str],
        led_count: int,
        *,
        direct: bool = True,
        zone_sizes: Iterable[int] | None = None,
    ) -> list[str]:
        """Build a bounded local SDK helper command for a Direct-capable device.

        This path bypasses the OpenRGB CLI's ``ApplyOptions`` implementation.
        The helper still talks only to the already validated loopback server;
        it does not contain or execute controller-specific hardware code.
        """

        self._require_client()
        if not Path(self.sdk_helper).is_file():
            raise OpenRGBError("Der interne OpenRGB-SDK-Schreibhelfer fehlt.")
        count = int(led_count)
        if not 1 <= count <= MAX_OPENRGB_LEDS:
            raise ValueError("Ungültige OpenRGB-LED-Anzahl.")
        command = [
            sys.executable,
            self.sdk_helper,
            "--address", self.address,
            "--port", str(self.port),
            "--device", self._device_id(device_id),
            "--led-count", str(count),
            "--colors", self._colors(colors),
        ]
        if not direct:
            command.append("--no-custom-mode")
        if zone_sizes is not None:
            sizes = tuple(int(value) for value in zone_sizes)
            if not sizes or len(sizes) > MAX_OPENRGB_LEDS or any(
                value < 0 or value > MAX_OPENRGB_LEDS for value in sizes
            ):
                raise ValueError("Ungültige OpenRGB-Zonengrößen.")
            command += ["--zone-sizes", ",".join(str(value) for value in sizes)]
        return command

    def sdk_inspect_command(self, device_id: int) -> list[str]:
        """Build a read-only controller/zone inspection command."""

        self._require_client()
        if not Path(self.sdk_helper).is_file():
            raise OpenRGBError("Der interne OpenRGB-SDK-Schreibhelfer fehlt.")
        return [
            sys.executable,
            self.sdk_helper,
            "--address", self.address,
            "--port", str(self.port),
            "--device", self._device_id(device_id),
            "--inspect",
        ]

    def sdk_color_commands(
        self,
        device_frames: Iterable[tuple[int, Iterable[str], int]],
        *,
        direct: bool = True,
    ) -> list[list[str]]:
        frames = list(device_frames)
        if not frames or len(frames) > MAX_OPENRGB_BATCH_DEVICES:
            raise ValueError("Ungültige Anzahl von OpenRGB-Geräten im SDK-Auftrag.")
        commands: list[list[str]] = []
        seen: set[int] = set()
        for raw_device_id, colors, led_count in frames:
            device_id = int(raw_device_id)
            if device_id in seen:
                raise ValueError("Ein OpenRGB-Gerät darf pro Auftrag nur einmal angesprochen werden.")
            seen.add(device_id)
            commands.append(self.sdk_color_command(device_id, colors, led_count, direct=direct))
        return commands

    def multi_color_command(
        self,
        device_frames: Iterable[tuple[int, Iterable[str]]],
        *,
        direct: bool = False,
    ) -> list[str]:
        """Build a command for exactly one device.

        OpenRGB 1.0~rc2 on Fedora can crash in ``ApplyOptions`` when its CLI
        receives several repeated ``--device`` blocks.  Keeping this legacy
        method intentionally single-device makes that failure mode impossible
        for callers that have not migrated to :meth:`color_commands` yet.
        """

        frames = list(device_frames)
        if len(frames) != 1:
            raise ValueError(
                "OpenRGB-Mehrgerätebefehle sind deaktiviert; Geräte müssen einzeln und seriell geschrieben werden."
            )
        device_id, colors = frames[0]
        return self.color_command(device_id, colors, direct=direct)

    def color_commands(
        self,
        device_frames: Iterable[tuple[int, Iterable[str]]],
        *,
        direct: bool = False,
    ) -> list[list[str]]:
        """Return one validated client command per device.

        The GUI executes the returned commands serially.  Apart from avoiding
        the OpenRGB rc2 CLI crash this also guarantees that a failed controller
        cannot corrupt the option vector for another selected device.
        """

        frames = list(device_frames)
        if not frames or len(frames) > MAX_OPENRGB_BATCH_DEVICES:
            raise ValueError("Ungültige Anzahl von OpenRGB-Geräten im Geräteauftrag.")
        commands: list[list[str]] = []
        seen: set[int] = set()
        for raw_device_id, colors in frames:
            device_id = int(raw_device_id)
            if device_id in seen:
                raise ValueError("Ein OpenRGB-Gerät darf pro Auftrag nur einmal angesprochen werden.")
            seen.add(device_id)
            commands.append(self.color_command(device_id, colors, direct=direct))
        return commands

    def native_mode_command(
        self,
        device_id: int,
        mode: str,
        colors: Iterable[str],
        brightness: int = 100,
    ) -> list[str]:
        clean_mode = str(mode).strip()
        if not SAFE_MODE_RE.fullmatch(clean_mode):
            raise ValueError("Ungültiger OpenRGB-Gerätemodus.")
        clean_brightness = max(0, min(100, int(brightness)))
        return self.client_command(
            "--device", self._device_id(device_id),
            "--mode", clean_mode,
            "--color", self._colors(colors),
            "--brightness", str(clean_brightness),
        )

    def read_devices(self, timeout: float = 25.0) -> list[OpenRGBDevice]:
        completed = subprocess.run(
            self.list_command(),
            capture_output=True,
            text=True,
            timeout=max(1.0, min(60.0, timeout)),
            check=False,
            env=openrgb_subprocess_environment(),
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()
            raise OpenRGBError(detail or "OpenRGB konnte die Geräteliste nicht lesen.")
        return parse_device_listing(completed.stdout)


def preferred_reset_mode(device: OpenRGBDevice) -> str:
    """Pick a device-reported hardware/default mode, never invent one."""

    priorities = (
        "default", "hardware", "hardware mode", "rainbow", "rainbow wave",
        "spectrum cycle", "spectrum", "color cycle", "static",
    )
    by_name = {mode.casefold(): mode for mode in device.modes if mode.casefold() != "direct"}
    for candidate in priorities:
        if candidate in by_name:
            return by_name[candidate]
    return ""


def best_native_mode_for_effect(
    device: OpenRGBDevice,
    effect_id: str,
    preferred_mode: str = "",
) -> str:
    """Choose an actually reported native mode for a non-Direct device."""

    available = {mode.casefold(): mode for mode in device.modes if mode.casefold() != "direct"}
    preferred = str(preferred_mode).strip().casefold()
    if preferred and preferred in available:
        return available[preferred]
    candidates = {
        "static": ("static", "fixed"),
        "breathing": ("breathing", "breathe", "pulse"),
        "rainbow": ("rainbow wave", "rainbow", "spectrum cycle", "color cycle"),
        "lightning": ("random flicker", "flicker", "flashing", "flash"),
        "spinner": ("visor", "chase", "marquee", "rainbow wave", "color cycle"),
        "comet": ("visor", "chase", "marquee"),
        "wave": ("rainbow wave", "wave", "spectrum cycle", "color cycle"),
        "pulse": ("pulse", "breathing", "breathe"),
        "alternating": ("alternating", "color cycle", "static"),
        "sparkle": ("random flicker", "flicker", "starry night", "static"),
    }.get(str(effect_id).casefold(), ("static",))
    for candidate in candidates:
        if candidate in available:
            return available[candidate]
    return preferred_reset_mode(device)
