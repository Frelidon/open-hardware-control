#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure normalization and assessment for the read-only hardware checker."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class Assessment:
    state: str
    value: str
    detail: str


@dataclass(frozen=True, slots=True)
class DmiInventory:
    memory: tuple[dict[str, object], ...]
    socket: str
    socket_source: str


def parse_link_speed(value: object) -> float | None:
    """Return GT/s from Linux PCIe link text such as ``16.0 GT/s PCIe``."""
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*GT/s", str(value), re.I)
    if not match:
        return None
    try:
        speed = float(match.group(1))
    except ValueError:
        return None
    return speed if 0.1 <= speed <= 128.0 else None


def pcie_generation(value: object) -> int | None:
    speed = parse_link_speed(value)
    if speed is None:
        return None
    standards = ((2.5, 1), (5.0, 2), (8.0, 3), (16.0, 4), (32.0, 5), (64.0, 6))
    return min(standards, key=lambda item: abs(item[0] - speed))[1]


def link_label(speed: object, width: object) -> str:
    generation = pcie_generation(speed)
    try:
        lanes = int(width)
    except (TypeError, ValueError):
        lanes = 0
    if generation and lanes > 0:
        return f"PCIe {generation}.0 ×{lanes}"
    return "Nicht prüfbar"


def assess_pcie_link(component: dict[str, object], *, under_load: bool = False) -> Assessment:
    current_speed = parse_link_speed(component.get("current_speed"))
    maximum_speed = parse_link_speed(component.get("max_speed"))
    try:
        current_width = int(component.get("current_width") or 0)
        maximum_width = int(component.get("max_width") or 0)
    except (TypeError, ValueError):
        current_width = maximum_width = 0
    current = link_label(component.get("current_speed"), current_width)
    maximum = link_label(component.get("max_speed"), maximum_width)
    if not current_speed or not maximum_speed or current_width <= 0 or maximum_width <= 0:
        return Assessment("unknown", current, "Der Kernel meldet keinen vollständigen PCIe-Link-Sollwert.")
    reduced = current_speed + 0.05 < maximum_speed or current_width < maximum_width
    if not reduced:
        return Assessment("pass", current, f"Aktueller Link entspricht dem gemeldeten Maximum {maximum}.")
    if under_load:
        return Assessment("fail", current, f"Unter Last unter dem gemeldeten Maximum {maximum}.")
    return Assessment("warning", current, f"Leerlaufwert; Maximum {maximum}. Für eine belastbare Bewertung Lasttest starten.")


def assess_nvme_link(component: dict[str, object]) -> Assessment:
    """Assess an NVMe link without issuing a storage write benchmark."""
    base = assess_pcie_link(component)
    try:
        current_width = int(component.get("current_width") or 0)
        maximum_width = int(component.get("max_width") or 0)
    except (TypeError, ValueError):
        return base
    maximum = link_label(component.get("max_speed"), maximum_width)
    if current_width > 0 and maximum_width > 0 and current_width < maximum_width:
        return Assessment("fail", base.value, f"Weniger Lanes als das gemeldete Maximum {maximum}.")
    return base


def parse_dmidecode_memory(text: str) -> tuple[dict[str, object], ...]:
    """Parse bounded, non-serial Type-17 fields from dmidecode output."""
    modules: list[dict[str, object]] = []
    blocks = re.split(r"\n\s*Memory Device\s*\n", str(text))
    for block in blocks[1:257]:
        fields: dict[str, str] = {}
        for raw in block.splitlines()[:96]:
            match = re.match(r"\s*([^:]{1,48}):\s*(.{0,240})\s*$", raw)
            if match:
                fields[match.group(1).strip()] = match.group(2).strip()
        size = fields.get("Size", "")
        if not size or size.casefold() in {"no module installed", "not installed", "unknown"}:
            continue
        modules.append({
            "locator": fields.get("Locator", ""),
            "size": size,
            "type": fields.get("Type", ""),
            "manufacturer": fields.get("Manufacturer", ""),
            "part": fields.get("Part Number", ""),
            "speed_mts": _memory_speed(fields.get("Speed", "")),
            "configured_mts": _memory_speed(
                fields.get("Configured Memory Speed", fields.get("Configured Clock Speed", ""))
            ),
        })
    return tuple(modules)


def parse_dmidecode_inventory(text: str) -> DmiInventory:
    """Read memory plus a firmware-reported CPU socket without serial fields."""
    memory = parse_dmidecode_memory(text)
    candidates: list[tuple[str, str]] = []
    for block in re.split(r"\n\s*Processor Information\s*\n", str(text))[1:65]:
        fields: dict[str, str] = {}
        for raw in block.splitlines()[:128]:
            match = re.match(r"\s*([^:]{1,48}):\s*(.{0,240})\s*$", raw)
            if match:
                fields[match.group(1).strip()] = match.group(2).strip()
        for field in ("Socket Designation", "Upgrade"):
            value = fields.get(field, "").strip()
            normalized = normalize_socket(value)
            if normalized:
                candidates.append((normalized, field))
                break
    unique = {value for value, _source in candidates}
    if len(unique) != 1:
        return DmiInventory(memory, "Nicht gemeldet", "")
    value = candidates[0][0]
    source = next(source for candidate, source in candidates if candidate == value)
    return DmiInventory(memory, value, source)


def normalize_socket(value: object) -> str:
    text = str(value or "").strip()
    if not text or text.casefold() in {
        "unknown", "not specified", "other", "to be filled by o.e.m.", "cpu 1",
    }:
        return ""
    match = re.search(r"\b(AM[2-9]|FM[1-9]|LGA\s*\d{3,5}|BGA\s*\d{3,5}|SP[3-9]|sTRX\w*)\b", text, re.I)
    if match:
        return re.sub(r"\s+", "", match.group(1)).upper()
    return text[:80] if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._+/-]{1,79}", text) else ""


def normalize_board(vendor: object, model: object, identifier: object = "") -> dict[str, str]:
    raw_vendor = str(vendor or "").strip()
    raw_model = str(model or "").strip()
    raw_identifier = str(identifier or "").strip()
    lowered = raw_vendor.casefold()
    friendly_vendor = "MSI" if "micro-star" in lowered or lowered == "msi" else raw_vendor
    if friendly_vendor and raw_model.casefold().startswith(friendly_vendor.casefold() + " "):
        raw_model = raw_model[len(friendly_vendor):].strip()
    if raw_identifier and raw_identifier.casefold() in raw_model.casefold():
        raw_identifier = ""
    display = " · ".join(part for part in (friendly_vendor, raw_model) if part) or "Unbekannt"
    if raw_identifier:
        display += f" ({raw_identifier})"
    return {
        "vendor": friendly_vendor or "Unbekannt",
        "vendor_raw": raw_vendor or "Unbekannt",
        "model": raw_model or "Unbekannt",
        "identifier": raw_identifier,
        "display": display,
    }


def _memory_speed(value: str) -> int | None:
    match = re.search(r"(\d{3,6})\s*(?:MT/s|MHz)", value, re.I)
    if not match:
        return None
    speed = int(match.group(1))
    return speed if 100 <= speed <= 20_000 else None


def assess_memory(
    modules: tuple[dict[str, object], ...], *, expected_mts: int = 0,
) -> Assessment:
    configured = [int(item["configured_mts"]) for item in modules if item.get("configured_mts")]
    if not configured:
        return Assessment("unknown", "Nicht prüfbar", "Keine konfigurierte Speichertaktrate gemeldet.")
    actual = min(configured)
    if expected_mts > 0:
        state = "pass" if actual >= expected_mts else "fail"
        detail = (
            "Konfigurierte Taktrate erreicht den eingetragenen Sollwert."
            if state == "pass" else f"Eingetragener Sollwert: {expected_mts} MT/s."
        )
        return Assessment(state, f"{actual} MT/s", detail)
    declared = [int(item["speed_mts"]) for item in modules if item.get("speed_mts")]
    if declared and actual < min(declared):
        return Assessment("warning", f"{actual} MT/s", f"DMI-Modulangabe: mindestens {min(declared)} MT/s; bitte Sollwert prüfen.")
    return Assessment("pass", f"{actual} MT/s", "Alle bestückten Module melden dieselbe konfigurierte Taktrate.")
