#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure RGB device inventory and grouping helpers.

This module deliberately contains no hardware I/O.  It turns the device list
reported by the local OpenRGB engine into stable, user-facing devices and
removes a known class of duplicate ENE DRAM aliases without collapsing two
real memory modules into one.
"""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from openrgb_integration import MAX_OPENRGB_LEDS, OpenRGBDevice

try:
    import fcntl
except ImportError:  # pragma: no cover - Linux is the supported platform
    fcntl = None

MAX_RGB_GROUPS = 32
MAX_GROUP_NAME_LENGTH = 48
MAX_DEVICE_ALIAS_LENGTH = 64
MAX_RGB_ZONE_CONFIG_DEVICES = 128
MAX_RGB_ZONE_CONFIG_ZONES = 64
MAX_RGB_UNITS_PER_ZONE = 64
MAX_RGB_LEDS_PER_UNIT = 512
MAX_PLAUSIBLE_FAN_LEDS = 64
RGB_LAYOUT_POSITIONS = (
    "top", "front", "side", "bottom", "rear", "gpu", "gpu-support", "ram", "pump"
)
RGB_LAYOUT_AIRFLOWS = {"intake", "exhaust", "component"}
THERMALTAKE_LAYOUT_VERSION = 4


@dataclass(frozen=True)
class RGBFanModel:
    model_id: str
    title: str
    leds_per_fan: int
    airflow: str


RGB_FAN_MODELS = (
    RGBFanModel(
        "tzmrit-interstellar-v2-normal",
        "TZMRIT / Jungle Leopard Interstellar-V2 · Normal",
        24,
        "normal",
    ),
    RGBFanModel(
        "tzmrit-interstellar-v2-reverse",
        "TZMRIT / Jungle Leopard Interstellar-V2 · Reverse",
        24,
        "reverse",
    ),
)


def rgb_fan_model(model_id: object) -> RGBFanModel | None:
    clean = str(model_id or "")[:96]
    return next((model for model in RGB_FAN_MODELS if model.model_id == clean), None)


def fan_zone_plausibility_warning(units: int, leds_per_unit: int) -> str:
    """Return a non-blocking warning for unusually large fan declarations."""

    clean_units = max(0, int(units))
    clean_leds = max(0, int(leds_per_unit))
    if clean_units and clean_leds > MAX_PLAUSIBLE_FAN_LEDS:
        return (
            f"{clean_leds} LEDs je Lüfter sind ungewöhnlich hoch. "
            "Bitte Modellangabe und Verkabelung prüfen."
        )
    if clean_units > 12:
        return f"{clean_units} Lüfter an einer Zone sind ungewöhnlich viele."
    return ""

RGB_LAYOUT_DEFAULT_POINTS: dict[str, tuple[tuple[float, float], ...]] = {
    "top": ((0.50, 0.12), (0.37, 0.18)),
    "front": ((0.87, 0.40), (0.82, 0.56)),
    "side": ((0.69, 0.40), (0.57, 0.42), (0.75, 0.58)),
    "bottom": ((0.57, 0.84), (0.38, 0.84)),
    "rear": ((0.13, 0.31), (0.16, 0.54)),
    "gpu": ((0.46, 0.59),),
    "gpu-support": ((0.48, 0.70),),
    "ram": ((0.55, 0.31),),
    "pump": ((0.38, 0.36),),
}


def _plain(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", text))


def canonical_device_name(name: object) -> str:
    """Normalize a name and collapse adjacent duplicate words.

    OpenRGB can report the same ENE controller family as both ``ENE DRAM`` and
    ``ENE DRAM DRAM``.  Collapsing only adjacent duplicates avoids broad fuzzy
    matching across unrelated controllers.
    """

    result: list[str] = []
    for token in _plain(name).split():
        if not result or result[-1] != token:
            result.append(token)
    return " ".join(result) or "rgb device"


def _is_dram(device: OpenRGBDevice) -> bool:
    identity = f"{device.name} {device.description} {device.device_type}".casefold()
    return any(token in identity for token in ("dram", "memory", "dimm", "ram"))


def _merge_device(primary: OpenRGBDevice, aliases: Iterable[OpenRGBDevice]) -> OpenRGBDevice:
    candidates = (primary, *tuple(aliases))
    modes = tuple(dict.fromkeys(mode for item in candidates for mode in item.modes))
    zones = tuple(dict.fromkeys(zone for item in candidates for zone in item.zones))
    leds = max((item.leds for item in candidates), key=len, default=primary.leds)

    def first(field: str) -> str:
        return next((str(getattr(item, field)) for item in candidates if getattr(item, field)), "")

    return OpenRGBDevice(
        index=primary.index,
        name=primary.name,
        device_type=first("device_type") or "Unbekannt",
        description=first("description"),
        version=first("version"),
        location=first("location"),
        serial=first("serial"),
        modes=modes,
        zones=zones,
        leds=leds,
    )


def _strong_duplicate_key(device: OpenRGBDevice) -> str:
    """Return an identity only when OpenRGB supplied a hardware path.

    Fedora's rc2 server can enumerate the complete controller inventory twice.
    Matching names alone are insufficient because two real DIMMs or two hubs
    may legitimately share a product name.  A serial number or the full
    OpenRGB location is required before two entries can be folded together.
    """

    serial = _plain(device.serial)
    if serial and serial not in {"0", "none", "unknown", "n a"}:
        return f"serial:{canonical_device_name(device.name)}:{serial}"
    location = _plain(device.location)
    if location and location not in {"none", "unknown", "n a"}:
        return ":".join(
            (
                "location",
                canonical_device_name(device.name),
                canonical_device_name(device.device_type),
                location,
            )
        )
    return ""


def _enumeration_signature(device: OpenRGBDevice) -> tuple[object, ...]:
    return (
        canonical_device_name(device.name),
        canonical_device_name(device.device_type),
        _plain(device.description),
        device.led_count,
        tuple(mode.casefold() for mode in device.modes),
        tuple(zone.casefold() for zone in device.zones),
    )


def _collapse_mirrored_inventory(devices: list[OpenRGBDevice]) -> tuple[list[OpenRGBDevice], list[str]]:
    """Collapse a complete rc2 inventory that was registered twice.

    The reported Fedora list contained indices 0..6 followed by the exact same
    seven controller signatures at 7..13.  Requiring at least four contiguous
    pairs and an exact signature match avoids treating two same-model DIMMs as
    a mirror by themselves.
    """

    ordered = sorted(devices, key=lambda item: item.index)
    if len(ordered) < 8 or len(ordered) % 2:
        return devices, []
    half = len(ordered) // 2
    first, second = ordered[:half], ordered[half:]
    if half < 4:
        return devices, []
    offset = second[0].index - first[0].index
    if offset <= 0 or any(right.index - left.index != offset for left, right in zip(first, second)):
        return devices, []
    if any(_enumeration_signature(left) != _enumeration_signature(right) for left, right in zip(first, second)):
        return devices, []
    removed = [f"{device.index}: {device.name}" for device in second]
    return first, removed


@dataclass(frozen=True)
class PreparedRGBDevices:
    devices: tuple[OpenRGBDevice, ...]
    stable_ids: tuple[str, ...]
    duplicate_aliases_removed: tuple[str, ...] = ()

    def stable_id_for_index(self, device_index: int) -> str:
        for device, stable_id in zip(self.devices, self.stable_ids):
            if device.index == device_index:
                return stable_id
        return ""


def prepare_openrgb_devices(devices: Iterable[OpenRGBDevice]) -> PreparedRGBDevices:
    """Return stable devices while keeping every real DRAM module.

    For DRAM only, exact-name variants that reduce to the same canonical name
    are treated as alias buckets.  If equally sized buckets exist, the shortest
    spelling is kept and metadata is merged ordinal-by-ordinal.  Thus
    ``ENE DRAM`` x2 plus ``ENE DRAM DRAM`` x2 becomes two devices, never one.
    Repeated devices with the same exact name remain untouched.
    """

    raw_source, mirrored_removed = _collapse_mirrored_inventory(list(devices))
    source: list[OpenRGBDevice] = []
    removed: list[str] = list(mirrored_removed)
    strong_positions: dict[str, int] = {}
    for device in raw_source:
        strong_key = _strong_duplicate_key(device)
        if strong_key and strong_key in strong_positions:
            primary_position = strong_positions[strong_key]
            source[primary_position] = _merge_device(source[primary_position], (device,))
            removed.append(f"{device.index}: {device.name}")
            continue
        if strong_key:
            strong_positions[strong_key] = len(source)
        source.append(device)
    kept: list[OpenRGBDevice] = []
    consumed: set[int] = set()

    for position, device in enumerate(source):
        if position in consumed:
            continue
        if not _is_dram(device):
            kept.append(device)
            continue
        canonical = canonical_device_name(device.name)
        family_positions = [
            index
            for index, candidate in enumerate(source)
            if index not in consumed and _is_dram(candidate) and canonical_device_name(candidate.name) == canonical
        ]
        buckets: dict[str, list[int]] = {}
        for index in family_positions:
            buckets.setdefault(_plain(source[index].name), []).append(index)
        bucket_values = list(buckets.values())
        if len(bucket_values) < 2 or len({len(bucket) for bucket in bucket_values}) != 1:
            for index in family_positions:
                kept.append(source[index])
                consumed.add(index)
            continue
        primary_bucket = min(
            bucket_values,
            key=lambda bucket: (len(_plain(source[bucket[0]].name).split()), len(_plain(source[bucket[0]].name))),
        )
        alias_buckets = [bucket for bucket in bucket_values if bucket is not primary_bucket]
        for ordinal, primary_index in enumerate(primary_bucket):
            aliases = [source[bucket[ordinal]] for bucket in alias_buckets]
            kept.append(_merge_device(source[primary_index], aliases))
            consumed.add(primary_index)
            for alias, bucket in zip(aliases, alias_buckets):
                consumed.add(bucket[ordinal])
                removed.append(f"{alias.index}: {alias.name}")

    stable_ids: list[str] = []
    ordinal_by_base: dict[str, int] = {}
    for device in kept:
        if device.serial:
            base = f"serial:{_plain(device.serial)}"
        elif device.location:
            base = f"location:{_plain(device.location)}"
        else:
            base = ":".join(
                (canonical_device_name(device.name), canonical_device_name(device.device_type), str(device.led_count))
            )
        ordinal_by_base[base] = ordinal_by_base.get(base, 0) + 1
        digest = hashlib.sha256(f"{base}:{ordinal_by_base[base]}".encode("utf-8")).hexdigest()[:16]
        stable_ids.append(f"openrgb:{digest}")
    return PreparedRGBDevices(tuple(kept), tuple(stable_ids), tuple(removed))


@dataclass(frozen=True)
class RGBGroup:
    group_id: str
    name: str


@dataclass(frozen=True)
class RGBLayoutSlot:
    position: str
    name: str
    count: int
    group_id: str
    connection: str = ""
    device_ids: tuple[str, ...] = ()
    slot_id: str = ""
    x: float = 0.5
    y: float = 0.5
    airflow: str = "component"
    size_mm: int = 120


def normalize_device_aliases(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for raw_device_id, raw_name in list(raw.items())[:512]:
        device_id = str(raw_device_id)[:96]
        name = " ".join(str(raw_name or "").split())[:MAX_DEVICE_ALIAS_LENGTH]
        if device_id and name:
            result[device_id] = name
    return result


def normalize_zone_configurations(raw: object) -> dict[str, dict[str, dict[str, int]]]:
    """Validate persisted fan/unit and LED counts for OpenRGB zones."""

    if not isinstance(raw, dict):
        return {}
    result: dict[str, dict[str, dict[str, int]]] = {}
    for raw_device_id, raw_zones in list(raw.items())[:MAX_RGB_ZONE_CONFIG_DEVICES]:
        device_id = str(raw_device_id)[:96]
        if not device_id or not isinstance(raw_zones, dict):
            continue
        zones: dict[str, dict[str, int]] = {}
        for raw_zone_name, raw_values in list(raw_zones.items())[:MAX_RGB_ZONE_CONFIG_ZONES]:
            zone_name = " ".join(str(raw_zone_name or "").split())[:96]
            if not zone_name or not isinstance(raw_values, dict):
                continue
            try:
                units = max(0, min(MAX_RGB_UNITS_PER_ZONE, int(raw_values.get("units", 0))))
                leds_per_unit = max(
                    0,
                    min(MAX_RGB_LEDS_PER_UNIT, int(raw_values.get("leds_per_unit", 0))),
                )
            except (TypeError, ValueError):
                continue
            zones[zone_name] = {"units": units, "leds_per_unit": leds_per_unit}
        if zones:
            result[device_id] = zones
    return result


def configured_zone_sizes(
    zone_names: Iterable[str],
    configuration: object,
) -> tuple[int, ...] | None:
    """Return one bounded total per reported zone, or ``None`` if unset."""

    clean = normalize_zone_configurations({"device": configuration}).get("device", {})
    if not clean:
        return None
    by_name = {name.casefold(): values for name, values in clean.items()}
    sizes: list[int] = []
    configured = False
    for raw_name in zone_names:
        values = by_name.get(str(raw_name).casefold(), {})
        units = int(values.get("units", 0))
        leds_per_unit = int(values.get("leds_per_unit", 0))
        size = units * leds_per_unit
        if size > MAX_OPENRGB_LEDS:
            return None
        sizes.append(size)
        configured = configured or bool(units or leds_per_unit)
    return tuple(sizes) if configured and any(sizes) else None


def normalize_layout_slots(raw: object, groups: Iterable[RGBGroup]) -> list[RGBLayoutSlot]:
    if not isinstance(raw, list):
        return []
    valid_groups = {group.group_id for group in groups}
    result: list[RGBLayoutSlot] = []
    used_slot_ids: set[str] = set()
    for item in raw[:64]:
        if not isinstance(item, dict):
            continue
        position = str(item.get("position", "")).casefold()
        group_id = str(item.get("group_id", ""))[:48]
        slot_id = re.sub(r"[^a-z0-9_-]+", "-", str(item.get("slot_id", position)).casefold()).strip("-")[:48]
        if not slot_id:
            slot_id = position
        if position not in RGB_LAYOUT_POSITIONS or slot_id in used_slot_ids or group_id not in valid_groups:
            continue
        used_slot_ids.add(slot_id)
        name = sanitize_group_name(item.get("name"))
        connection = " ".join(str(item.get("connection", "")).split())[:96]
        try:
            count = max(0, min(12, int(item.get("count", 0))))
        except (TypeError, ValueError):
            count = 0
        raw_devices = item.get("device_ids", [])
        device_ids = tuple(
            dict.fromkeys(str(value)[:96] for value in raw_devices[:64] if str(value))
        ) if isinstance(raw_devices, list) else ()
        ordinal = sum(1 for existing in result if existing.position == position)
        default_points = RGB_LAYOUT_DEFAULT_POINTS.get(position, ((0.5, 0.5),))
        default_x, default_y = default_points[min(ordinal, len(default_points) - 1)]
        try:
            x = max(0.04, min(0.96, float(item.get("x", default_x))))
            y = max(0.04, min(0.96, float(item.get("y", default_y))))
        except (TypeError, ValueError):
            x, y = default_x, default_y
        airflow = str(item.get("airflow", "component")).casefold()
        if airflow not in RGB_LAYOUT_AIRFLOWS:
            airflow = "component"
        try:
            size_mm = max(0, min(240, int(item.get("size_mm", 120))))
        except (TypeError, ValueError):
            size_mm = 120
        result.append(
            RGBLayoutSlot(
                position, name, count, group_id, connection, device_ids,
                slot_id, x, y, airflow, size_mm,
            )
        )
    return result


def auto_arrange_layout_slots(slots: Iterable[RGBLayoutSlot]) -> list[RGBLayoutSlot]:
    """Place every block on a deterministic, non-stacked case overview."""

    ordinals: dict[str, int] = {}
    arranged: list[RGBLayoutSlot] = []
    for slot in slots:
        ordinal = ordinals.get(slot.position, 0)
        ordinals[slot.position] = ordinal + 1
        points = RGB_LAYOUT_DEFAULT_POINTS.get(slot.position, ((0.5, 0.5),))
        if ordinal < len(points):
            x, y = points[ordinal]
        else:
            base_x, base_y = points[-1]
            row, column = divmod(ordinal - len(points) + 1, 3)
            x = max(0.08, min(0.92, base_x - 0.11 * column))
            y = max(0.08, min(0.92, base_y + 0.10 * row))
        arranged.append(
            RGBLayoutSlot(
                slot.position, slot.name, slot.count, slot.group_id,
                slot.connection, slot.device_ids, slot.slot_id,
                x, y, slot.airflow, slot.size_mm,
            )
        )
    return arranged


def infer_layout_position(slot: RGBLayoutSlot, x: float, y: float) -> str:
    """Infer a case zone from a dragged slot while preserving components."""

    if slot.position in {"gpu", "gpu-support", "ram", "pump"}:
        return slot.position
    clean_x = max(0.0, min(1.0, float(x)))
    clean_y = max(0.0, min(1.0, float(y)))
    if clean_y <= 0.23:
        return "top"
    if clean_y >= 0.74:
        return "bottom"
    if clean_x <= 0.22:
        return "rear"
    if clean_x >= 0.80:
        return "front"
    return "side"


def reorder_layout_device_ids(
    device_ids: Iterable[str],
    source_index: int,
    target_index: int,
) -> tuple[str, ...]:
    """Move one physical device to another visual position in a layout block."""

    ordered = tuple(dict.fromkeys(str(device_id)[:96] for device_id in device_ids if str(device_id)))
    if not ordered:
        return ()
    source = max(0, min(len(ordered) - 1, int(source_index)))
    target = max(0, min(len(ordered) - 1, int(target_index)))
    if source == target:
        return ordered
    mutable = list(ordered)
    moved = mutable.pop(source)
    mutable.insert(target, moved)
    return tuple(mutable)


def flori_rgb_layout_profile() -> tuple[list[RGBGroup], list[RGBLayoutSlot]]:
    """Frelidon's Thermaltake 360 mm layout and recorded wiring."""

    groups = [
        RGBGroup("kraken-radiator", "Kraken-Radiator"),
        RGBGroup("front", "Frontlüfter"),
        RGBGroup("seite-intake", "Rückwand/Seite Intake"),
        RGBGroup("heck", "Hecklüfter"),
        RGBGroup("boden-intake", "Netzteilabdeckung vorne Intake"),
        RGBGroup("grafikkarte", "Grafikkarte"),
        RGBGroup("gpu-halterung", "Grafikkartenhalterung"),
        RGBGroup("arbeitsspeicher", "Arbeitsspeicher"),
        RGBGroup("pumpenkopf", "Kraken-Pumpenkopf"),
    ]
    slots = [
        # The diagram is drawn from case rear (left) to case front (right).
        # Frelidon's physical controller order is channel 2 rear, channel 3
        # centre and channel 1 front.
        RGBLayoutSlot(
            "top", "Kraken 360 · 3× 120 mm", 3, "kraken-radiator",
            "NZXT RGB led1–led3 · Radiator oben",
            ("nzxt:led2", "nzxt:led3", "nzxt:led1"),
            "radiator-top", 0.50, 0.12, "exhaust", 120,
        ),
        RGBLayoutSlot("front", "Front · 2× 120 mm normal", 2, "front", "RGB-Hub A1 · PWM SYS-FAN4", (), "fans-front", 0.87, 0.40, "intake", 120),
        RGBLayoutSlot("side", "Rückwand/Seite · 3× 120 mm Reverse", 3, "seite-intake", "PWM SYS-FAN2 · RGB-Anschluss prüfen", (), "fans-side", 0.69, 0.40, "intake", 120),
        RGBLayoutSlot("bottom", "Netzteilabdeckung vorne · 3× 120 mm Reverse", 3, "boden-intake", "RGB-Hub B7 · PWM SYS-FAN6", (), "fans-psu-shroud", 0.57, 0.84, "intake", 120),
        RGBLayoutSlot("rear", "Heck · 1× 120 mm Abluft", 1, "heck", "RGB-Hub A2 · PWM SYS-FAN1", (), "fan-rear", 0.13, 0.31, "exhaust", 120),
        RGBLayoutSlot("gpu", "Sapphire RX 9070 XT", 1, "grafikkarte", "Grafikkartenbeleuchtung", (), "gpu", 0.47, 0.59, "component", 0),
        RGBLayoutSlot("gpu-support", "Grafikkartenhalterung", 1, "gpu-halterung", "RGB-Hub B6", (), "gpu-support", 0.48, 0.70, "component", 0),
        RGBLayoutSlot("ram", "Arbeitsspeicher · 2 Riegel", 2, "arbeitsspeicher", "2× 16 GB · DDR5-6000", (), "ram", 0.56, 0.32, "component", 0),
        RGBLayoutSlot("pump", "NZXT Kraken Pumpenkopf", 1, "pumpenkopf", "Kraken 2023 · LCD separat", (), "pump", 0.38, 0.36, "component", 0),
    ]
    return groups, slots


def sanitize_group_name(value: object) -> str:
    name = " ".join(str(value or "").split())[:MAX_GROUP_NAME_LENGTH]
    return name or "Neue Gruppe"


def normalize_rgb_groups(raw: object) -> list[RGBGroup]:
    groups: list[RGBGroup] = []
    used: set[str] = set()
    if not isinstance(raw, list):
        return groups
    for item in raw[:MAX_RGB_GROUPS]:
        if not isinstance(item, dict):
            continue
        group_id = re.sub(r"[^a-z0-9_-]+", "-", str(item.get("id", "")).casefold()).strip("-")[:48]
        if not group_id or group_id in used or group_id == "ungrouped":
            continue
        used.add(group_id)
        groups.append(RGBGroup(group_id, sanitize_group_name(item.get("name"))))
    return groups


def normalize_group_assignments(raw: object, groups: Iterable[RGBGroup]) -> dict[str, str]:
    valid_groups = {group.group_id for group in groups}
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for raw_device, raw_group in list(raw.items())[:512]:
        device_id = str(raw_device)[:96]
        group_id = str(raw_group)[:48]
        if device_id and group_id in valid_groups:
            result[device_id] = group_id
    return result


class ProcessFileLock:
    """Kernel-backed Linux process lock held by an inheritable-safe file descriptor."""

    def __init__(self, path: str | os.PathLike[str]):
        self.path = os.fspath(path)
        self._handle = None
        self.owner_pid: int | None = None
        self.last_error = ""

    @property
    def acquired(self) -> bool:
        return self._handle is not None

    def acquire(self) -> bool:
        if self.acquired:
            return True
        self.owner_pid = None
        self.last_error = ""
        if fcntl is None:
            self.last_error = "fcntl ist auf diesem System nicht verfügbar"
            return False
        directory = os.path.dirname(self.path) or "."
        descriptor: int | None = None
        try:
            os.makedirs(directory, mode=0o700, exist_ok=True)
            flags = os.O_RDWR | os.O_CREAT
            flags |= getattr(os, "O_CLOEXEC", 0)
            flags |= getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(self.path, flags, 0o600)
            os.set_inheritable(descriptor, False)
            os.fchmod(descriptor, 0o600)
            handle = os.fdopen(descriptor, "r+", encoding="ascii")
        except OSError as exc:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            self.last_error = str(exc)
            return False
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            try:
                handle.seek(0)
                value = handle.read(32).strip()
                self.owner_pid = int(value) if value.isdigit() else None
            except (OSError, ValueError):
                self.owner_pid = None
            self.last_error = "busy"
            handle.close()
            return False
        except OSError as exc:
            self.last_error = str(exc)
            handle.close()
            return False
        try:
            handle.seek(0)
            handle.truncate()
            handle.write(str(os.getpid()))
            handle.flush()
            os.fsync(handle.fileno())
        except OSError as exc:
            self.last_error = str(exc)
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            finally:
                handle.close()
            return False
        self._handle = handle
        self.owner_pid = os.getpid()
        return True

    def release(self) -> None:
        handle = self._handle
        self._handle = None
        if handle is None:
            return
        try:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Eine andere Open-Hardware-Control-Instanz besitzt bereits die RGB-Steuerung.")
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        self.release()


class RGBSessionLock(ProcessFileLock):
    """Prevent two RGB writers from sharing the OHC-managed backend."""


class ApplicationInstanceLock(ProcessFileLock):
    """Prevent a second Open Hardware Control application instance."""
