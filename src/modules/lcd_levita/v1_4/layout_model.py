#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure editable model for the Levita data surface (LCD layer 2).

The model deliberately has no Qt dependency and performs no device I/O.  It
validates imported TRCC JSON, stores OHC-owned overrides and renders preview
labels.  The original ``config1.dc`` remains read-only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from thermalright_display import adjust_rgb_intensity, bounded_layer_intensity


LAYOUT_SCHEMA_VERSION = 1
MODULE_VERSION = "1.4"
MAX_LAYOUT_BLOCKS = 100
MAX_SAVED_LAYOUTS = 500
MAX_TEXT_LENGTH = 160
MIN_FONT_SIZE = 12
MAX_FONT_SIZE = 160

_VALUE_TOKEN = re.compile(r"\{value(?::[^}]*)?\}")
_VALID_COLOR = re.compile(r"#[0-9a-fA-F]{6}")
_VALID_KIND = frozenset({"text", "metric", "clock"})

_METRIC_SAMPLES: dict[str, float] = {
    "cpu:temp": 51,
    "cpu:usage": 30,
    "cpu:freq": 4850,
    "cpu:power": 92,
    "gpu:primary:temp": 47,
    "gpu:primary:usage": 42,
    "gpu:primary:clock": 2715,
    "gpu:primary:power": 188,
    "memory:percent": 41,
    "memory:clock": 6000,
    "memory:available": 16384,
    "memory:temp": 38,
    "disk:read": 420,
    "disk:write": 180,
    "disk:activity": 35,
    "disk:temp": 36,
    "net:down": 850,
    "net:up": 120,
    "fan:cpu": 1450,
    "fan:gpu": 1180,
    "fan:ssd": 900,
    "fan:sys2": 1100,
}

_METRIC_LABELS: dict[str, str] = {
    "cpu:temp": "CPU-Temperatur",
    "cpu:usage": "CPU-Auslastung",
    "cpu:freq": "CPU-Takt",
    "cpu:power": "CPU-Leistung",
    "gpu:primary:temp": "GPU-Temperatur",
    "gpu:primary:usage": "GPU-Auslastung",
    "gpu:primary:clock": "GPU-Takt",
    "gpu:primary:power": "GPU-Leistung",
    "memory:percent": "Arbeitsspeicher",
    "memory:clock": "Speichertakt",
    "memory:available": "Freier Arbeitsspeicher",
    "memory:temp": "Speichertemperatur",
}

_USAGE_LABEL_METRICS: dict[str, tuple[str, ...]] = {
    "cpu": ("cpu:usage",),
    "gpu": ("gpu:primary:usage", "gpu:usage"),
    "ram": ("memory:percent",),
    "memory": ("memory:percent",),
    "speicher": ("memory:percent",),
}


def _bounded_int(value: object, minimum: int, maximum: int, fallback: int) -> int:
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        parsed = fallback
    return max(minimum, min(maximum, parsed))


def _bounded_text(value: object, fallback: str = "") -> str:
    text = str(value if value is not None else fallback).strip()
    return text[:MAX_TEXT_LENGTH]


def _color(value: object) -> str:
    text = str(value or "#ffffff").strip().lower()
    return text if _VALID_COLOR.fullmatch(text) else "#ffffff"


def _safe_format(value: object) -> str:
    text = _bounded_text(value, "{value}") or "{value}"
    if not _VALUE_TOKEN.search(text):
        text = "{value}"
    try:
        text.format(value=42)
    except (KeyError, ValueError, IndexError):
        return "{value}"
    return text


@dataclass(frozen=True, slots=True)
class LayoutBlock:
    """One indivisible live text block on the 1600x720 data surface."""

    ident: str
    kind: str
    x: int
    y: int
    color: str = "#ffffff"
    size: int = 36
    bold: bool = False
    italic: bool = False
    font: str = ""
    text: str = ""
    metric: str = ""
    format: str = "{value}"
    show_unit: bool = True
    source: str = "time"

    def bounded(self, *, width: int = 1600, height: int = 720, safe_right_x: int = 1520) -> "LayoutBlock":
        right = max(1, min(int(width), int(safe_right_x)))
        return replace(
            self,
            ident=_bounded_text(self.ident, "ohc-layer2") or "ohc-layer2",
            kind=self.kind if self.kind in _VALID_KIND else "text",
            x=_bounded_int(self.x, 0, right - 1, 0),
            y=_bounded_int(self.y, 0, max(0, int(height) - 1), 0),
            color=_color(self.color),
            size=_bounded_int(self.size, MIN_FONT_SIZE, MAX_FONT_SIZE, 36),
            font=_bounded_text(self.font),
            text=_bounded_text(self.text),
            metric=_bounded_text(self.metric),
            format=_safe_format(self.format) if self.kind == "metric" else _bounded_text(self.format),
            source=self.source if self.source in {"time", "date", "weekday"} else "time",
        )

    @property
    def label(self) -> str:
        if self.kind == "metric":
            return _METRIC_LABELS.get(self.metric, self.metric or "Hardwarewert")
        if self.kind == "clock":
            return {"time": "Uhrzeit", "date": "Datum", "weekday": "Wochentag"}.get(self.source, "Uhr")
        return self.text or "Text"

    @property
    def preview_text(self) -> str:
        if self.kind == "text":
            return self.text or "Text"
        if self.kind == "clock":
            return {"time": "13:38", "date": "09/26", "weekday": "Montag"}.get(self.source, "13:38")
        sample = _METRIC_SAMPLES.get(self.metric, 42)
        try:
            return self.format.format(value=sample)
        except (KeyError, ValueError, IndexError):
            return f"{sample:g}"

    @property
    def editable_text(self) -> str:
        return self.format if self.kind == "metric" else self.text

    def with_edited_text(self, value: str) -> "LayoutBlock":
        """Change visible text while retaining a metric's live-value token."""
        text = _bounded_text(value)
        if self.kind == "text":
            return replace(self, text=text or self.text)
        if self.kind != "metric" or not text:
            return self
        if _VALUE_TOKEN.search(text):
            return replace(self, format=_safe_format(text))
        match = _VALUE_TOKEN.search(self.format)
        token = match.group(0) if match else "{value}"
        suffix = self.format[match.end():] if match else ""
        return replace(self, format=_safe_format(f"{text} {token}{suffix}".strip()))

    def to_trcc(self, *, offset_x: int = 0, offset_y: int = 0, safe_right_x: int = 1520) -> dict[str, object]:
        moved = replace(self, x=self.x + int(offset_x), y=self.y + int(offset_y)).bounded(
            safe_right_x=safe_right_x,
        )
        data: dict[str, object] = {
            "id": moved.ident,
            "type": moved.kind,
            "x": moved.x,
            "y": moved.y,
            "color": moved.color,
            "size": moved.size,
            "bold": moved.bold,
            "italic": moved.italic,
        }
        if moved.font:
            data["name"] = moved.font
        if moved.kind == "text":
            data["text"] = moved.text
        elif moved.kind == "metric":
            data.update(metric=moved.metric, format=moved.format, show_unit=moved.show_unit)
        else:
            data.update(source=moved.source, format=moved.format)
        return data


@dataclass(frozen=True, slots=True)
class EditableLayout:
    source: str
    blocks: tuple[LayoutBlock, ...]
    offset_x: int = 0
    offset_y: int = 0

    def bounded(self, *, safe_right_x: int = 1520) -> "EditableLayout":
        return replace(
            self,
            blocks=tuple(block.bounded(safe_right_x=safe_right_x) for block in self.blocks[:MAX_LAYOUT_BLOCKS]),
            offset_x=_bounded_int(self.offset_x, -1600, 1600, 0),
            offset_y=_bounded_int(self.offset_y, -720, 720, 0),
        )

    def replace_block(self, ident: str, **changes: object) -> "EditableLayout":
        updated = tuple(replace(block, **changes) if block.ident == ident else block for block in self.blocks)
        return replace(self, blocks=updated)

    def to_trcc_elements(self, *, safe_right_x: int = 1520) -> list[dict[str, object]]:
        layout = self.bounded(safe_right_x=safe_right_x)
        return [
            block.to_trcc(
                offset_x=layout.offset_x,
                offset_y=layout.offset_y,
                safe_right_x=safe_right_x,
            )
            for block in layout.blocks
        ]


def adjust_layout_intensity(layout: EditableLayout, percent: int) -> EditableLayout:
    """Create the transmission/preview copy for a chosen layer-2 emphasis."""
    level = bounded_layer_intensity(percent)
    if level == 100:
        return layout
    return replace(layout, blocks=tuple(
        replace(block, color=adjust_rgb_intensity(block.color, level))
        for block in layout.blocks
    ))


def restore_explicit_format_units(layout: EditableLayout) -> EditableLayout:
    """Keep literal units in OHC formats visible in TRCC's physical renderer."""
    tokens = ("%", "°C", "MHz", "MB", "GB", " W")
    return replace(layout, blocks=tuple(
        replace(block, show_unit=True)
        if block.kind == "metric" and any(token in block.format for token in tokens)
        else block
        for block in layout.blocks
    ))


def layout_from_config(source: Path, config: Mapping[str, Any]) -> EditableLayout:
    blocks: list[LayoutBlock] = []
    elements = config.get("elements", ())
    if not isinstance(elements, Iterable) or isinstance(elements, (str, bytes, Mapping)):
        elements = ()
    for index, raw in enumerate(elements):
        if index >= MAX_LAYOUT_BLOCKS:
            break
        # Imported TRCC/user JSON is external input. One malformed record must
        # not discard every valid, bounded record that follows it.
        if not isinstance(raw, Mapping):
            continue
        kind = str(raw.get("type", "text"))
        if kind not in _VALID_KIND:
            continue
        block = LayoutBlock(
            ident=f"ohc-layer2-{index:02d}",
            kind=kind,
            x=_bounded_int(raw.get("x"), 0, 1599, 0),
            y=_bounded_int(raw.get("y"), 0, 719, 0),
            color=_color(raw.get("color")),
            size=_bounded_int(raw.get("size"), MIN_FONT_SIZE, MAX_FONT_SIZE, 36),
            bold=bool(raw.get("bold", False)),
            italic=bool(raw.get("italic", False)),
            font=_bounded_text(raw.get("name") or raw.get("font")),
            text=_bounded_text(raw.get("text")),
            metric=_bounded_text(raw.get("metric")),
            format=_safe_format(raw.get("format")) if kind == "metric" else _bounded_text(raw.get("format")),
            show_unit=bool(raw.get("show_unit", True)),
            source=_bounded_text(raw.get("source"), "time") or "time",
        ).bounded()
        blocks.append(block)
    return EditableLayout(str(source.expanduser().resolve()), _merge_usage_labels(tuple(blocks)))


def _merge_usage_labels(blocks: tuple[LayoutBlock, ...]) -> tuple[LayoutBlock, ...]:
    """Coalesce separate CPU/GPU/RAM captions with their usage value.

    TRCC's stock layouts often encode ``CPU`` and ``{value:.0f}%`` as two
    elements even though users perceive them as one value block.  Keeping the
    source pair separate would let a drag tear the caption away from its live
    value.  The editable OHC view therefore represents that pair as one metric
    format while leaving temperatures, clocks and unrelated text untouched.
    """
    by_metric = {
        block.metric: block for block in blocks
        if block.kind == "metric" and block.metric
    }
    replacements: dict[str, LayoutBlock] = {}
    consumed_text: set[str] = set()
    for label in blocks:
        if label.kind != "text":
            continue
        metrics = _USAGE_LABEL_METRICS.get(label.text.strip().casefold())
        if not metrics:
            continue
        metric = next((by_metric.get(name) for name in metrics if by_metric.get(name) is not None), None)
        if metric is None or abs(metric.y - label.y) > max(80, metric.size * 2):
            continue
        visible_label = label.text.strip()
        combined_format = metric.format
        if visible_label.casefold() not in combined_format.casefold():
            combined_format = f"{visible_label} {combined_format}".strip()
        replacements[metric.ident] = replace(
            metric,
            x=min(label.x, metric.x),
            y=label.y,
            format=_safe_format(combined_format),
        )
        consumed_text.add(label.ident)
    return tuple(
        replacements.get(block.ident, block)
        for block in blocks
        if block.ident not in consumed_text
    )


def layout_fingerprint(layout: EditableLayout) -> str:
    payload = json.dumps(
        {
            "schema": LAYOUT_SCHEMA_VERSION,
            "source": layout.source,
            "blocks": [asdict(block) for block in layout.blocks],
            "offset_x": layout.offset_x,
            "offset_y": layout.offset_y,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def serialize_layout_overrides(layouts: Mapping[str, EditableLayout]) -> str:
    retained = list(layouts.items())[-MAX_SAVED_LAYOUTS:]
    payload = {
        "schema": LAYOUT_SCHEMA_VERSION,
        "layouts": {
            key: {
                "source": layout.source,
                "offset_x": layout.offset_x,
                "offset_y": layout.offset_y,
                "blocks": [asdict(block) for block in layout.blocks],
            }
            for key, layout in retained
        },
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def deserialize_layout_overrides(raw: str) -> dict[str, EditableLayout]:
    try:
        payload = json.loads(raw or "{}")
    except (TypeError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict) or payload.get("schema") != LAYOUT_SCHEMA_VERSION:
        return {}
    values = payload.get("layouts")
    if not isinstance(values, dict):
        return {}
    result: dict[str, EditableLayout] = {}
    for key, value in list(values.items())[-MAX_SAVED_LAYOUTS:]:
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        blocks_raw = value.get("blocks", ())
        if not isinstance(blocks_raw, list):
            continue
        # Saved blocks use model field names; rebuild them directly so ids and
        # edited formats remain stable across application starts.
        blocks: list[LayoutBlock] = []
        for block_raw in blocks_raw[:MAX_LAYOUT_BLOCKS]:
            if not isinstance(block_raw, dict):
                continue
            try:
                blocks.append(LayoutBlock(**block_raw).bounded())
            except (TypeError, ValueError):
                continue
        result[key] = EditableLayout(
            source=str(value.get("source") or key)[:4096],
            blocks=tuple(blocks),
            offset_x=_bounded_int(value.get("offset_x"), -1600, 1600, 0),
            offset_y=_bounded_int(value.get("offset_y"), -720, 720, 0),
        ).bounded()
    return result
