#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent NZXT-ESC preset compatibility layer for Open Hardware Control.

This module intentionally contains no NZXT-ESC source code or bundled presets.
It only reads the documented/exported JSON data structure and converts user-
selected files into an OHC-owned local profile representation.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import io
import json
import math
import re
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image, ImageColor, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - handled by caller/UI
    Image = None
    ImageColor = None
    ImageDraw = None
    ImageFont = None

OHC_LCD_PROFILE_SCHEMA = 1
MAX_PRESET_BYTES = 8 * 1024 * 1024
MAX_LAYERS = 256
MAX_TEXT_LENGTH = 240
DEFAULT_SOURCE_RESOLUTION = (640, 640)
LCD_RESOLUTION = (240, 240)

# The current public NZXT-ESC format uses these keys. Additional aliases are
# accepted because users may import older exports; the aliases are OHC logic,
# not copied implementation code.
METRIC_DEFINITIONS: dict[str, dict[str, str]] = {
    "cpuTemp": {"label": "CPU-Temperatur", "short": "CPU", "unit": "°C", "kind": "temp"},
    "cpuLoad": {"label": "CPU-Auslastung", "short": "CPU", "unit": "%", "kind": "percent"},
    "cpuClock": {"label": "CPU-Takt", "short": "CPU", "unit": "MHz", "kind": "clock"},
    "cpuPower": {"label": "CPU-Leistung", "short": "CPU", "unit": "W", "kind": "power"},
    "liquidTemp": {"label": "Kühlmitteltemperatur", "short": "Liquid", "unit": "°C", "kind": "temp"},
    "gpuTemp": {"label": "GPU-Temperatur", "short": "GPU", "unit": "°C", "kind": "temp"},
    "gpuLoad": {"label": "GPU-Auslastung", "short": "GPU", "unit": "%", "kind": "percent"},
    "gpuClock": {"label": "GPU-Takt", "short": "GPU", "unit": "MHz", "kind": "clock"},
    "gpuPower": {"label": "GPU-Leistung", "short": "GPU", "unit": "W", "kind": "power"},
    "ramLoad": {"label": "RAM-Auslastung", "short": "RAM", "unit": "%", "kind": "percent"},
    "ramUsed": {"label": "RAM verwendet", "short": "RAM", "unit": "GB", "kind": "memory"},
    "ramTotal": {"label": "RAM gesamt", "short": "RAM", "unit": "GB", "kind": "memory"},
    "fanRpm": {"label": "Lüfterdrehzahl", "short": "FAN", "unit": "RPM", "kind": "rpm"},
    "pumpRpm": {"label": "Pumpendrehzahl", "short": "PUMP", "unit": "RPM", "kind": "rpm"},
}

_METRIC_ALIASES = {
    "cpu_temp": "cpuTemp", "cputemp": "cpuTemp", "cpu-temperature": "cpuTemp",
    "cpu_load": "cpuLoad", "cpuload": "cpuLoad", "cpu_usage": "cpuLoad", "cpuusage": "cpuLoad",
    "cpu_clock": "cpuClock", "cpuclock": "cpuClock", "cpu_frequency": "cpuClock",
    "cpu_power": "cpuPower", "cpupower": "cpuPower",
    "liquid_temp": "liquidTemp", "liquidtemp": "liquidTemp", "coolant_temp": "liquidTemp", "watertemp": "liquidTemp",
    "gpu_temp": "gpuTemp", "gputemp": "gpuTemp", "gpu-temperature": "gpuTemp",
    "gpu_load": "gpuLoad", "gpuload": "gpuLoad", "gpu_usage": "gpuLoad", "gpuusage": "gpuLoad",
    "gpu_clock": "gpuClock", "gpuclock": "gpuClock", "gpu_frequency": "gpuClock",
    "gpu_power": "gpuPower", "gpupower": "gpuPower",
    "ram_load": "ramLoad", "ram_usage": "ramLoad", "memory_load": "ramLoad", "memory_usage": "ramLoad", "ramusage": "ramLoad",
    "ram_used": "ramUsed", "memory_used": "ramUsed",
    "ram_total": "ramTotal", "memory_total": "ramTotal",
    "fan_rpm": "fanRpm", "fanrpm": "fanRpm",
    "pump_rpm": "pumpRpm", "pumprpm": "pumpRpm",
}
for _key in tuple(METRIC_DEFINITIONS):
    _METRIC_ALIASES[_key.casefold()] = _key


@dataclass(frozen=True)
class ImportIssue:
    status: str  # direct | approximate | unsupported | blocked | warning
    item: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"status": self.status, "item": self.item, "detail": self.detail}


@dataclass
class ImportResult:
    profile: dict[str, Any]
    issues: list[ImportIssue]

    @property
    def counts(self) -> dict[str, int]:
        result = {"direct": 0, "approximate": 0, "unsupported": 0, "blocked": 0, "warning": 0}
        for issue in self.issues:
            result[issue.status] = result.get(issue.status, 0) + 1
        return result


def canonical_metric(value: object) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw in METRIC_DEFINITIONS:
        return raw
    normalized = re.sub(r"\s+", "_", raw).casefold()
    return _METRIC_ALIASES.get(normalized) or _METRIC_ALIASES.get(raw.casefold())


def metric_choices() -> list[tuple[str, str]]:
    return [(key, spec["label"]) for key, spec in METRIC_DEFINITIONS.items()]


def _number(value: object, default: float = 0.0, low: float = -10000.0, high: float = 10000.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(parsed):
        return default
    return max(low, min(high, parsed))


def _int(value: object, default: int, low: int, high: int) -> int:
    return int(round(_number(value, float(default), float(low), float(high))))


def _bool(value: object, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _text(value: object, default: str = "", limit: int = MAX_TEXT_LENGTH) -> str:
    value = str(value if value is not None else default).replace("\x00", "")
    return value[:limit]


def normalize_color(value: object, default: str = "#ffffff") -> str:
    raw = _text(value, default, 80).strip()
    if not raw or raw.casefold() == "transparent":
        return "transparent" if raw.casefold() == "transparent" else default

    # Current NZXT-ESC exports use browser/CSS colours such as
    # ``rgba(2, 2, 2, 0.72)``. Pillow's ImageColor parser is stricter than a
    # browser and rejects fractional alpha on some versions, which previously
    # turned those layers into fallback colours (often making an imported
    # design look black). Normalize CSS rgb()/rgba() ourselves first.
    match = re.fullmatch(
        r"rgba?\(\s*([+-]?[0-9]*\.?[0-9]+)\s*,\s*([+-]?[0-9]*\.?[0-9]+)\s*,\s*([+-]?[0-9]*\.?[0-9]+)(?:\s*,\s*([+-]?[0-9]*\.?[0-9]+%?))?\s*\)",
        raw,
        re.I,
    )
    if match:
        channels = [max(0, min(255, int(round(float(match.group(i)))))) for i in (1, 2, 3)]
        alpha_raw = match.group(4)
        alpha = 255
        if alpha_raw is not None:
            try:
                if alpha_raw.endswith("%"):
                    alpha = int(round(max(0.0, min(100.0, float(alpha_raw[:-1]))) * 2.55))
                else:
                    value_float = float(alpha_raw)
                    alpha = int(round(max(0.0, min(1.0, value_float)) * 255.0)) if value_float <= 1.0 else int(round(max(0.0, min(255.0, value_float))))
            except ValueError:
                alpha = 255
        if alpha >= 255:
            return "#{:02x}{:02x}{:02x}".format(*channels)
        return "#{:02x}{:02x}{:02x}{:02x}".format(*channels, alpha)

    if ImageColor is None:
        return raw
    try:
        ImageColor.getcolor(raw, "RGBA")
        return raw
    except (ValueError, TypeError):
        return default


def _parse_resolution(value: object) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d{2,4})\s*[x×]\s*(\d{2,4})\s*", str(value or ""), re.I)
    if not match:
        return DEFAULT_SOURCE_RESOLUTION
    width, height = int(match.group(1)), int(match.group(2))
    if not (100 <= width <= 4096 and 100 <= height <= 4096):
        return DEFAULT_SOURCE_RESOLUTION
    return width, height


def _is_remote_url(value: str) -> bool:
    lowered = value.strip().casefold()
    return lowered.startswith(("http://", "https://", "ftp://", "file://", "data:"))


def _safe_layer_id(value: object, index: int) -> str:
    raw = re.sub(r"[^A-Za-z0-9_.:-]", "_", _text(value, "", 96)).strip("._")
    return raw or f"layer-{index + 1}"


def _metric_from_data(data: dict[str, Any]) -> str | None:
    for field in ("metric", "metricType", "sourceMetric", "source", "sensor"):
        if field in data:
            result = canonical_metric(data.get(field))
            if result:
                return result
    return None


def _safe_data_image_uri(value: object) -> str:
    """Return a bounded embedded preview image URI or an empty string.

    Current NZXT-ESC schema-v3 exports can contain a rendered previewImage.
    OHC never fetches remote media during import, but this self-contained
    preview is safe to decode after validating type and size.
    """
    raw = _text(value, "", MAX_PRESET_BYTES * 2).strip()
    match = re.fullmatch(r"data:image/(png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=\r\n]+)", raw, re.I)
    if not match:
        return ""
    encoded = re.sub(r"\s+", "", match.group(2))
    # Base64 expands by roughly 4/3; keep the decoded media bounded to the
    # same maximum order as the preset itself.
    if len(encoded) > MAX_PRESET_BYTES * 4 // 3 + 16:
        return ""
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except Exception:
        return ""
    if not decoded or len(decoded) > MAX_PRESET_BYTES:
        return ""
    return f"data:image/{match.group(1).lower()};base64,{encoded}"


def _image_from_data_uri(value: object, target_resolution: tuple[int, int] = LCD_RESOLUTION):
    if Image is None:
        return None
    uri = _safe_data_image_uri(value)
    if not uri:
        return None
    try:
        encoded = uri.split(",", 1)[1]
        raw = base64.b64decode(encoded, validate=True)
        with Image.open(io.BytesIO(raw)) as source:
            if source.width * source.height > 50_000_000:
                return None
            image = source.convert("RGB")
            side = min(image.size)
            left = (image.width - side) // 2
            top = (image.height - side) // 2
            return image.crop((left, top, left + side, top + side)).resize(target_resolution, Image.Resampling.LANCZOS)
    except Exception:
        return None


def _current_position(value: object, dimension: int) -> float:
    number = _number(value, 0.0)
    # Current exports use -1..+1 center-relative coordinates. Older internal
    # exports used source pixels, so only normalized-looking values are scaled.
    if -2.0 <= number <= 2.0:
        return number * (dimension / 2.0)
    return number


def import_nzxt_esc_payload(payload: dict[str, Any], *, source_name: str = "preset.nzxt-esc-preset.json") -> ImportResult:
    if not isinstance(payload, dict):
        raise ValueError("Die Profildatei enthält kein JSON-Objekt.")
    schema = _int(payload.get("schemaVersion"), 0, 0, 999)
    if schema <= 0:
        raise ValueError("Keine gültige NZXT-ESC-schemaVersion gefunden.")
    issues: list[ImportIssue] = []
    if schema == 3:
        issues.append(ImportIssue("direct", "Dateiformat", "NZXT-ESC Schema 3 erkannt."))
    elif schema in {1, 2}:
        issues.append(ImportIssue("approximate", "Dateiformat", f"Älteres Schema {schema}; OHC verwendet eine tolerante Feldzuordnung."))
    else:
        issues.append(ImportIssue("warning", "Dateiformat", f"Unbekanntes Schema {schema}; bekannte Felder werden bestmöglich gelesen."))

    # NZXT-ESC v6 schema-v3 exports wrap the actual preset below `preset`.
    # Older exports seen by OHC placed background/overlay directly at root.
    preset = payload.get("preset") if isinstance(payload.get("preset"), dict) else None
    current_v3 = bool(preset and isinstance(preset.get("overlay"), dict))
    app_info = payload.get("app") if isinstance(payload.get("app"), dict) else {}
    preview_data = _safe_data_image_uri(payload.get("previewImage"))
    if current_v3:
        issues.append(ImportIssue("direct", "Aktuelles Schema-v3-Layout", "preset/background/overlay-Struktur erkannt und in das OHC-LCD-Modell übersetzt."))
        if preview_data:
            issues.append(ImportIssue("direct", "Eingebettete Vorschau", "Die im Export enthaltene Vorschaugrafik wird als sicherer Darstellungs-Fallback übernommen."))

    if current_v3:
        assert preset is not None
        background = preset.get("background") if isinstance(preset.get("background"), dict) else {}
        base = background.get("base") if isinstance(background.get("base"), dict) else {}
        source_w, source_h = DEFAULT_SOURCE_RESOLUTION
        bg_color = normalize_color(base.get("color"), "#000000")
        media_overlay = background.get("mediaOverlay") if isinstance(background.get("mediaOverlay"), dict) else {}
        media = media_overlay.get("media") if isinstance(media_overlay.get("media"), dict) else {}
        transform = media_overlay.get("transform") if isinstance(media_overlay.get("transform"), dict) else {}
        bg_url = _text(media.get("url"), "", 4096).strip()
        background_info: dict[str, Any] = {
            "color": bg_color,
            "url": "",
            "original_url": bg_url,
            "fit": "cover",
            "align": "center",
            "scale": _number(transform.get("scale"), 1.0, 0.01, 20.0),
            "x": _number(transform.get("offsetX"), 0.0, -10000, 10000),
            "y": _number(transform.get("offsetY"), 0.0, -10000, 10000),
            "previewData": preview_data,
        }
        if bg_url:
            issues.append(ImportIssue("blocked", "Hintergrundmedium", "URL-/Video-Hintergründe werden aus Sicherheitsgründen nicht automatisch aus dem Internet geladen; die eingebettete Vorschau bleibt als statischer Fallback verfügbar." if preview_data else "URL-/Video-Hintergründe werden aus Sicherheitsgründen nicht automatisch aus dem Internet geladen."))
        source_type = _text(base.get("sourceType"), "color", 30).casefold()
        if source_type not in {"color", "none", "local", "image"}:
            issues.append(ImportIssue("approximate", "Hintergrundquelle", f"Hintergrundtyp '{source_type}' wird auf die lokale OHC-Darstellung angenähert."))
        raw_overlay = preset.get("overlay") if isinstance(preset.get("overlay"), dict) else {}
        raw_elements_all = raw_overlay.get("elements") if isinstance(raw_overlay.get("elements"), list) else []
    else:
        background = payload.get("background") if isinstance(payload.get("background"), dict) else {}
        settings = background.get("settings") if isinstance(background.get("settings"), dict) else {}
        source_w, source_h = _parse_resolution(settings.get("resolution", "640x640"))
        bg_url = _text(background.get("url"), "", 4096).strip()
        bg_color = normalize_color(settings.get("backgroundColor"), "#000000")
        bg_source = background.get("source") if isinstance(background.get("source"), dict) else {}
        background_info = {
            "color": bg_color,
            "url": "",
            "original_url": bg_url,
            "fit": _text(settings.get("fit"), "cover", 16),
            "align": _text(settings.get("align"), "center", 16),
            "scale": _number(settings.get("scale"), 1.0, 0.01, 20.0),
            "x": _number(settings.get("x"), 0.0, -10000, 10000),
            "y": _number(settings.get("y"), 0.0, -10000, 10000),
            "previewData": preview_data,
        }
        if bg_url:
            if _is_remote_url(bg_url):
                issues.append(ImportIssue("blocked", "Hintergrundmedium", "Externe/URL-basierte Medien werden beim Import nicht automatisch geladen."))
            else:
                issues.append(ImportIssue("approximate", "Hintergrundmedium", "Lokaler Medienverweis erkannt. Datei muss in OHC bei Bedarf neu zugeordnet werden."))
        source_type = _text(bg_source.get("type"), "", 30).casefold()
        if source_type and source_type not in {"local", "none"} and not bg_url:
            issues.append(ImportIssue("blocked", "Hintergrundquelle", f"Externe Quelle '{source_type}' wird nicht automatisch geladen."))
        if any(key in settings for key in ("scale", "x", "y", "fit", "align")):
            issues.append(ImportIssue("approximate", "Hintergrund-Transformation", "Skalierung/Ausrichtung wird in OHC auf die 240×240-LCD-Fläche angenähert."))
        raw_overlay = payload.get("overlay") if isinstance(payload.get("overlay"), dict) else {}
        raw_elements_all = raw_overlay.get("elements") if isinstance(raw_overlay.get("elements"), list) else []

    raw_elements = raw_elements_all[:MAX_LAYERS]
    if len(raw_elements_all) > MAX_LAYERS:
        issues.append(ImportIssue("warning", "Ebenenlimit", f"Nur die ersten {MAX_LAYERS} Ebenen werden übernommen."))

    normalized_layers: list[dict[str, Any]] = []
    ids_seen: set[str] = set()
    for index, raw_layer in enumerate(raw_elements):
        if not isinstance(raw_layer, dict):
            issues.append(ImportIssue("unsupported", f"Ebene {index + 1}", "Ungültige Ebenenstruktur wurde ausgelassen."))
            continue
        if current_v3:
            layer_type = _text(raw_layer.get("elementType"), "", 32).casefold()
            transform = raw_layer.get("transform") if isinstance(raw_layer.get("transform"), dict) else {}
            data = raw_layer.get("config") if isinstance(raw_layer.get("config"), dict) else {}
            raw_x = _current_position(transform.get("x"), source_w)
            raw_y = _current_position(transform.get("y"), source_h)
            raw_angle = transform.get("rotateDeg")
            visibility = _text(raw_layer.get("visibility"), "always", 24).casefold()
            raw_visible = visibility not in {"hidden", "never", "off"}
            raw_locked = _bool(raw_layer.get("isLocked"), False)
        else:
            layer_type = _text(raw_layer.get("type"), "", 32).casefold()
            data = raw_layer.get("data") if isinstance(raw_layer.get("data"), dict) else {}
            raw_x = _number(raw_layer.get("x"), 0.0)
            raw_y = _number(raw_layer.get("y"), 0.0)
            raw_angle = raw_layer.get("angle")
            raw_visible = _bool(raw_layer.get("visible"), True) if "visible" in raw_layer else True
            raw_locked = _bool(raw_layer.get("locked"), False)

        aliases = {"audioVisualizer": "audio_visualizer"}
        layer_type = aliases.get(layer_type, layer_type)
        layer_id = _safe_layer_id(raw_layer.get("id"), index)
        base_id = layer_id
        duplicate = 2
        while layer_id in ids_seen:
            layer_id = f"{base_id}-{duplicate}"
            duplicate += 1
        ids_seen.add(layer_id)
        layer: dict[str, Any] = {
            "id": layer_id,
            "type": layer_type or "unknown",
            "x": raw_x,
            "y": raw_y,
            "angle": _number(raw_angle, 0.0, -3600, 3600) % 360.0,
            "visible": raw_visible,
            "locked": raw_locked,
            "status": "direct",
            "displayName": _text(raw_layer.get("displayName"), "", 120),
            "data": {},
        }
        if layer_type == "metric":
            metric = _metric_from_data(data)
            if metric is None:
                layer["status"] = "unsupported"
                layer["visible"] = False
                layer["data"] = {"metric": _text(data.get("metric") or data.get("metricType") or data.get("sourceMetric"), "unknown", 64)}
                issues.append(ImportIssue("unsupported", f"Messwert · {layer_id}", "Unbekannte Sensorquelle; Ebene bleibt deaktiviert erhalten."))
            else:
                if current_v3:
                    color = normalize_color(data.get("color"), "#ffffff")
                    size = _int(data.get("fontSize"), 70, 6, 640)
                    layer["data"] = {
                        "metric": metric, "numberColor": color, "numberSize": size,
                        "textColor": color, "textSize": 0, "showLabel": False,
                        "outlineColor": normalize_color(data.get("outlineColor"), "transparent"),
                        "outlineThickness": _number(data.get("outlineWidth"), 0.0, 0.0, 40.0),
                    }
                else:
                    layer["data"] = {
                        "metric": metric,
                        "numberColor": normalize_color(data.get("numberColor"), "#ffffff"),
                        "numberSize": _int(data.get("numberSize"), 100, 6, 640),
                        "textColor": normalize_color(data.get("textColor"), "#ffffff"),
                        "textSize": _int(data.get("textSize"), 32, 0, 320),
                        "showLabel": _bool(data.get("showLabel"), True) if "showLabel" in data else True,
                        "outlineColor": normalize_color(data.get("outlineColor"), "transparent"),
                        "outlineThickness": _number(data.get("outlineThickness"), 0.0, 0.0, 40.0),
                    }
                issues.append(ImportIssue("direct", f"Messwert · {layer_id}", f"{METRIC_DEFINITIONS[metric]['label']} wird mit OHC-Livedaten verbunden."))
        elif layer_type == "text":
            layer["data"] = {
                "text": _text(data.get("content") if current_v3 else data.get("text"), "", MAX_TEXT_LENGTH),
                "textColor": normalize_color(data.get("color") if current_v3 else data.get("textColor"), "#ffffff"),
                "textSize": _int(data.get("fontSize") if current_v3 else data.get("textSize"), 32, 6, 320),
                "outlineColor": normalize_color(data.get("outlineColor"), "transparent"),
                "outlineThickness": _number(data.get("outlineWidth") if current_v3 else data.get("outlineThickness"), 0.0, 0.0, 40.0),
            }
            issues.append(ImportIssue("direct", f"Text · {layer_id}", "Text, Farbe, Größe, Position und Drehung werden übernommen."))
        elif layer_type == "shape":
            layer["data"] = {
                "width": _number(data.get("width"), 100.0, 1.0, 2000.0),
                "height": _number(data.get("height"), 100.0, 1.0, 2000.0),
                "radius": _number(data.get("radius"), 0.0, 0.0, 1000.0),
                "fillColor": normalize_color(data.get("fillColor"), "transparent"),
                "borderColor": normalize_color(data.get("borderColor"), "transparent"),
                "borderWidth": _number(data.get("borderWidth"), 0.0, 0.0, 80.0),
            }
            layer["status"] = "approximate"
            issues.append(ImportIssue("approximate", f"Form · {layer_id}", "Form, Füllung und Rand werden auf die runde OHC-LCD-Fläche angenähert."))
        elif layer_type == "divider":
            layer["data"] = {
                "width": _number(data.get("width"), 2.0, 1.0, 2000.0),
                "height": _number(data.get("height"), 100.0, 1.0, 2000.0),
                "color": normalize_color(data.get("color"), "#ffffff"),
                "outlineColor": normalize_color(data.get("outlineColor"), "transparent"),
                "outlineThickness": _number(data.get("outlineThickness"), 0.0, 0.0, 40.0),
            }
            issues.append(ImportIssue("direct", f"Trenner · {layer_id}", "Rechteck/Trennlinie wird übernommen."))
        elif layer_type == "clock":
            font = _text(data.get("fontFamily") if current_v3 else data.get("font"), "default", 80).casefold()
            layer["data"] = {
                "format": _text(data.get("timeFormat") if current_v3 else data.get("format"), "HH:mm", 20),
                "mode": "12h" if str(data.get("timeSystem", "24")) == "12" else _text(data.get("mode"), "24h", 10),
                "fontSize": _int(data.get("fontSize"), 64, 6, 320),
                "color": normalize_color(data.get("color"), "#ffffff"),
                "font": "system",
                "outlineColor": normalize_color(data.get("outlineColor"), "transparent"),
                "outlineThickness": _number(data.get("outlineWidth") if current_v3 else data.get("outlineThickness"), 0.0, 0.0, 40.0),
            }
            if font not in {"", "default", "system", "default-extrabold"}:
                layer["status"] = "approximate"
                issues.append(ImportIssue("approximate", f"Uhr · {layer_id}", "Spezielle Schrift wird durch eine lokale Systemschrift ersetzt."))
            else:
                issues.append(ImportIssue("direct", f"Uhr · {layer_id}", "Uhrformat, Farbe, Größe und Position werden übernommen."))
        elif layer_type == "analog_clock":
            layer["data"] = {
                "size": _number(data.get("size"), 160.0, 30.0, 1200.0),
                "faceColor": normalize_color(data.get("faceColor"), "#000000"),
                "borderColor": normalize_color(data.get("borderColor"), "#ffffff"),
                "borderWidth": _number(data.get("borderWidth"), 2.0, 0.0, 30.0),
                "hourHandColor": normalize_color(data.get("hourHandColor"), "#ffffff"),
                "minuteHandColor": normalize_color(data.get("minuteHandColor"), "#ffffff"),
                "secondHandColor": normalize_color(data.get("secondHandColor"), "#ff0000"),
                "tickColor": normalize_color(data.get("tickColor"), "#ffffff"),
                "showSecondHand": _bool(data.get("showSecondHand"), True),
            }
            layer["status"] = "approximate"
            issues.append(ImportIssue("approximate", f"Analoguhr · {layer_id}", "Analoguhr wird mit lokalen OHC-Zeigern und Ticks angenähert."))
        elif layer_type == "radial_graphic":
            metric = _metric_from_data(data)
            layer["data"] = {
                "metric": metric or "",
                "size": _number(data.get("size"), 200.0, 20.0, 1200.0),
                "strokeWidth": _number(data.get("strokeWidth"), 8.0, 1.0, 100.0),
                "totalAngle": _number(data.get("totalAngle"), 270.0, 5.0, 360.0),
                "strokeColor": normalize_color(data.get("strokeColor"), "#00aaff"),
                "trackEnabled": _bool(data.get("trackEnabled"), True),
                "trackColor": normalize_color(data.get("trackColor"), "rgba(255,255,255,0.18)"),
                "trackWidth": _number(data.get("trackWidth"), data.get("strokeWidth", 8.0), 1.0, 100.0),
                "reverse": _bool(data.get("reverse"), False),
            }
            layer["status"] = "approximate"
            if metric:
                issues.append(ImportIssue("approximate", f"Radialgrafik · {layer_id}", f"{METRIC_DEFINITIONS[metric]['label']} wird als OHC-Livebogen angenähert."))
            else:
                layer["visible"] = False
                issues.append(ImportIssue("unsupported", f"Radialgrafik · {layer_id}", "Unbekannte Sensorquelle; Radialgrafik bleibt deaktiviert."))
        elif layer_type == "sensor_chart":
            metric = _metric_from_data(data)
            layer["data"] = {
                "metric": metric or "", "width": _number(data.get("width"), 180.0, 10.0, 1000.0),
                "height": _number(data.get("height"), 70.0, 10.0, 1000.0),
                "chartColor": normalize_color(data.get("chartColor"), "#00aaff"),
            }
            layer["status"] = "approximate"
            if metric:
                issues.append(ImportIssue("approximate", f"Sensordiagramm · {layer_id}", "Der Verlauf wird derzeit als lokale Momentaufnahme/Sparkline angenähert."))
            else:
                layer["visible"] = False
                issues.append(ImportIssue("unsupported", f"Sensordiagramm · {layer_id}", "Unbekannte Sensorquelle; Diagramm bleibt deaktiviert."))
        elif layer_type == "date":
            layer["data"] = {
                "format": _text(data.get("format"), "DD.MM.YYYY", 80),
                "fontSize": _int(data.get("fontSize"), 36, 6, 320),
                "color": normalize_color(data.get("color"), "#ffffff"),
                "outlineColor": normalize_color(data.get("outlineColor"), "transparent"),
                "outlineThickness": _number(data.get("outlineThickness"), 0.0, 0.0, 40.0),
            }
            layer["status"] = "approximate"
            issues.append(ImportIssue("approximate", f"Datum · {layer_id}", "Gängige Datums-Platzhalter werden in ein lokales OHC-Datumsformat übersetzt."))
        else:
            layer["status"] = "unsupported"
            layer["visible"] = False
            layer["data"] = {"rawType": layer_type or "unknown"}
            issues.append(ImportIssue("unsupported", f"Ebene · {layer_id}", f"Elementtyp '{layer_type or 'unbekannt'}' wird noch nicht gerendert und bleibt deaktiviert erhalten."))
        normalized_layers.append(layer)

    # Legacy schema can define a canonical z-order. Current v3 array order is
    # already the export order and is preserved as-is.
    z_order = raw_overlay.get("zOrder") if isinstance(raw_overlay.get("zOrder"), list) else None
    if z_order:
        order = [str(item) for item in z_order]
        position = {layer_id: idx for idx, layer_id in enumerate(order)}
        fallback_order = {str(layer.get("id", "")): idx for idx, layer in enumerate(normalized_layers)}
        normalized_layers.sort(key=lambda layer: position.get(str(layer.get("id", "")), len(position) + fallback_order.get(str(layer.get("id", "")), 0)))
        unknown_ids = [item for item in order if item not in ids_seen]
        if unknown_ids:
            issues.append(ImportIssue("warning", "Ebenenreihenfolge", f"{len(unknown_ids)} unbekannte zOrder-ID(s) wurden ignoriert."))
        issues.append(ImportIssue("direct", "Ebenenreihenfolge", "Schema-v3-zOrder wurde als OHC-Ebenenreihenfolge übernommen."))

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    normalized_original = {
        "canvas": {"sourceWidth": source_w, "sourceHeight": source_h, "background": background_info},
        "layers": copy.deepcopy(normalized_layers),
    }
    preset_name = _text(preset.get("name") if current_v3 and preset else payload.get("presetName"), Path(source_name).stem.replace(".nzxt-esc-preset", ""), 120) or "Importiertes LCD-Profil"
    app_version = _text(app_info.get("version") if current_v3 else payload.get("appVersion"), "unbekannt", 80)
    profile = {
        "ohcLcdProfileSchema": OHC_LCD_PROFILE_SCHEMA,
        "id": str(uuid.uuid4()), "name": preset_name, "createdAt": now, "modifiedAt": now,
        "source": {
            "kind": "nzxt-esc", "fileName": Path(source_name).name, "schemaVersion": schema,
            "appVersion": app_version, "exportedAt": _text(payload.get("exportedAt"), "", 80),
            "importedAt": now, "currentV3Layout": current_v3,
        },
        "canvas": copy.deepcopy(normalized_original["canvas"]),
        "layers": copy.deepcopy(normalized_original["layers"]),
        "original": normalized_original,
        "autoUpdateMatchingLabels": True,
        "importReport": [issue.as_dict() for issue in issues],
    }
    return ImportResult(profile=profile, issues=issues)

def import_nzxt_esc_file(path: Path) -> ImportResult:
    path = Path(path)
    if not path.is_file():
        raise ValueError("Die ausgewählte Profildatei existiert nicht.")
    size = path.stat().st_size
    if size <= 0 or size > MAX_PRESET_BYTES:
        raise ValueError(f"Die Profildatei muss zwischen 1 Byte und {MAX_PRESET_BYTES // (1024 * 1024)} MiB groß sein.")
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Ungültige JSON-Profildatei: {exc}") from exc
    result = import_nzxt_esc_payload(payload, source_name=path.name)
    result.profile["source"]["sha256"] = hashlib.sha256(raw).hexdigest()
    return result


def clone_profile(profile: dict[str, Any], *, name: str | None = None) -> dict[str, Any]:
    cloned = copy.deepcopy(profile)
    cloned["id"] = str(uuid.uuid4())
    cloned["name"] = _text(name, f"{profile.get('name', 'Profil')} – Kopie", 120)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    cloned["createdAt"] = now
    cloned["modifiedAt"] = now
    return cloned


def restore_import_original(profile: dict[str, Any]) -> dict[str, Any]:
    restored = copy.deepcopy(profile)
    original = profile.get("original") if isinstance(profile.get("original"), dict) else None
    if not original:
        raise ValueError("Für dieses Profil ist kein importierter Originalzustand gespeichert.")
    restored["canvas"] = copy.deepcopy(original.get("canvas", {}))
    restored["layers"] = copy.deepcopy(original.get("layers", []))
    restored["modifiedAt"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return restored


def ohc_default_profile() -> dict[str, Any]:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    base = {
        "canvas": {"sourceWidth": 640, "sourceHeight": 640, "background": {"color": "#10141c", "url": "", "original_url": "", "fit": "cover", "align": "center", "scale": 1.0, "x": 0.0, "y": 0.0}},
        "layers": [
            {"id": "ohc-cpu", "type": "metric", "x": -112, "y": -18, "angle": 0.0, "visible": True, "locked": False, "status": "direct", "data": {"metric": "cpuTemp", "numberColor": "#ffffff", "numberSize": 112, "textColor": "#8fdcff", "textSize": 28, "showLabel": True, "outlineColor": "transparent", "outlineThickness": 0.0}},
            {"id": "ohc-gpu", "type": "metric", "x": 112, "y": -18, "angle": 0.0, "visible": True, "locked": False, "status": "direct", "data": {"metric": "gpuTemp", "numberColor": "#ffffff", "numberSize": 112, "textColor": "#8fdcff", "textSize": 28, "showLabel": True, "outlineColor": "transparent", "outlineThickness": 0.0}},
            {"id": "ohc-liquid", "type": "metric", "x": 0, "y": 168, "angle": 0.0, "visible": True, "locked": False, "status": "direct", "data": {"metric": "liquidTemp", "numberColor": "#ffffff", "numberSize": 80, "textColor": "#8fdcff", "textSize": 22, "showLabel": True, "outlineColor": "transparent", "outlineThickness": 0.0}},
        ],
    }
    return {
        "ohcLcdProfileSchema": OHC_LCD_PROFILE_SCHEMA,
        "id": str(uuid.uuid4()),
        "name": "OHC-Standardprofil",
        "createdAt": now,
        "modifiedAt": now,
        "source": {"kind": "ohc", "importedAt": now},
        "canvas": copy.deepcopy(base["canvas"]),
        "layers": copy.deepcopy(base["layers"]),
        "original": copy.deepcopy(base),
        "autoUpdateMatchingLabels": True,
        "importReport": [],
    }


def update_metric(profile: dict[str, Any], layer_id: str, metric: str, *, auto_label: bool = True) -> bool:
    metric = canonical_metric(metric) or ""
    if not metric:
        return False
    layers = profile.get("layers") if isinstance(profile.get("layers"), list) else []
    target_index = -1
    old_metric = ""
    for index, layer in enumerate(layers):
        if isinstance(layer, dict) and layer.get("id") == layer_id and layer.get("type") == "metric":
            target_index = index
            data = layer.setdefault("data", {})
            old_metric = canonical_metric(data.get("metric")) or ""
            data["metric"] = metric
            break
    if target_index < 0:
        return False
    if auto_label and old_metric and old_metric in METRIC_DEFINITIONS:
        old_short = METRIC_DEFINITIONS[old_metric]["short"].casefold()
        new_short = METRIC_DEFINITIONS[metric]["short"]
        # Only touch the closest unambiguous text layer that is exactly the old label.
        candidates: list[tuple[int, dict[str, Any]]] = []
        for idx, layer in enumerate(layers):
            if not isinstance(layer, dict) or layer.get("type") != "text":
                continue
            text = str((layer.get("data") or {}).get("text", "")).strip().casefold()
            if text == old_short:
                candidates.append((abs(idx - target_index), layer))
        if candidates:
            candidates.sort(key=lambda item: item[0])
            if len(candidates) == 1 or candidates[0][0] < candidates[1][0]:
                candidates[0][1].setdefault("data", {})["text"] = new_short
    profile["modifiedAt"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return True


def _font(size: int, *, bold: bool = True):
    if ImageFont is None:
        return None
    candidates = [
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            if Path(candidate).exists():
                return ImageFont.truetype(candidate, max(6, size))
        except OSError:
            continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def _rgba(color: object, default: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    if ImageColor is None:
        return default
    normalized = normalize_color(color, "transparent")
    if normalized == "transparent":
        return (0, 0, 0, 0)
    try:
        return ImageColor.getcolor(normalized, "RGBA")
    except (ValueError, TypeError):
        return default


def _date_format(fmt: str) -> str:
    replacements = [
        ("YYYY", "%Y"), ("yyyy", "%Y"), ("YY", "%y"),
        ("DD", "%d"), ("dd", "%d"), ("MM", "%m"),
        ("MMM", "%b"), ("MMMM", "%B"),
    ]
    output = fmt
    # Long month tokens before short numeric month token.
    output = output.replace("MMMM", "%B").replace("MMM", "%b")
    for source, target in replacements:
        if source not in {"MMMM", "MMM"}:
            output = output.replace(source, target)
    return output


def format_metric(metric: str, value: object, temperature_unit: str = "c") -> tuple[str, str, str]:
    spec = METRIC_DEFINITIONS.get(metric, {"short": metric.upper(), "unit": "", "kind": "none"})
    try:
        number = float(value)
        valid = math.isfinite(number)
    except (TypeError, ValueError):
        valid = False
        number = 0.0
    if not valid:
        return "—", spec["unit"], spec["short"]
    unit = spec["unit"]
    kind = spec["kind"]
    if kind == "temp":
        if str(temperature_unit).casefold().startswith("f"):
            number = number * 9.0 / 5.0 + 32.0
            unit = "°F"
        return str(int(round(number))), unit, spec["short"]
    if kind == "memory":
        return f"{number:.1f}", unit, spec["short"]
    return str(int(round(number))), unit, spec["short"]


def _draw_centered_text(canvas, center: tuple[float, float], text: str, font, fill, *, stroke_width: int = 0, stroke_fill=None) -> tuple[int, int, int, int]:
    draw = ImageDraw.Draw(canvas)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = center[0] - width / 2 - bbox[0]
    y = center[1] - height / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
    return int(x), int(y), int(x + width), int(y + height)


def render_profile(
    profile: dict[str, Any],
    metrics: dict[str, object] | None = None,
    *,
    temperature_unit: str = "c",
    now: datetime | None = None,
    target_resolution: tuple[int, int] = LCD_RESOLUTION,
):
    if Image is None or ImageDraw is None:
        raise RuntimeError("Pillow ist für LCD-Profilvorschauen erforderlich.")
    metrics = metrics or {}
    width = max(32, min(4096, int(target_resolution[0])))
    height = max(32, min(4096, int(target_resolution[1])))
    target_resolution = (width, height)
    canvas_info = profile.get("canvas") if isinstance(profile.get("canvas"), dict) else {}
    source_w = max(1, _int(canvas_info.get("sourceWidth"), 640, 100, 4096))
    source_h = max(1, _int(canvas_info.get("sourceHeight"), 640, 100, 4096))
    background = canvas_info.get("background") if isinstance(canvas_info.get("background"), dict) else {}
    # A current ESC export can reference a remote MP4/image. OHC deliberately
    # never fetches that URL implicitly. If the exporter embedded a preview,
    # use it as the visual base instead of reducing the design to a flat colour.
    # Dynamic OHC-owned overlays are then redrawn on top.
    preview_base = None
    if str(background.get("original_url") or background.get("url") or "").strip():
        preview_base = _image_from_data_uri(background.get("previewData"), target_resolution)
    if preview_base is not None:
        image = preview_base.convert("RGBA")
        preview_as_background = True
    else:
        image = Image.new("RGBA", target_resolution, _rgba(background.get("color"), (0, 0, 0, 255)))
        preview_as_background = False
    draw = ImageDraw.Draw(image)
    global_scale = max(0.60, min(1.60, _number(profile.get("renderScalePercent"), 100.0, 60.0, 160.0) / 100.0))
    scale_x = (target_resolution[0] / source_w) * global_scale
    scale_y = (target_resolution[1] / source_h) * global_scale
    scale = min(scale_x, scale_y)
    cx, cy = target_resolution[0] / 2, target_resolution[1] / 2
    now = now or datetime.now()

    layers = profile.get("layers") if isinstance(profile.get("layers"), list) else []
    drawn_layers = 0
    for layer in layers[:MAX_LAYERS]:
        if not isinstance(layer, dict) or not layer.get("visible", True):
            continue
        layer_type = str(layer.get("type", ""))
        # The embedded exporter preview already contains static text/shapes.
        # Repaint only live/dynamic OHC layers on such a preview to avoid
        # duplicated labels while still making clocks/sensors move.
        if preview_as_background and layer_type not in {"metric", "clock", "radial_graphic", "sensor_chart", "analog_clock", "date"}:
            continue
        data = layer.get("data") if isinstance(layer.get("data"), dict) else {}
        x = cx + _number(layer.get("x"), 0.0) * scale_x
        y = cy + _number(layer.get("y"), 0.0) * scale_y
        angle = _number(layer.get("angle"), 0.0) % 360.0
        # Draw each element into a transparent full-size layer so rotation is
        # centered on the element without trusting arbitrary source dimensions.
        element = Image.new("RGBA", target_resolution, (0, 0, 0, 0))
        edraw = ImageDraw.Draw(element)
        outline_color = _rgba(data.get("outlineColor"), (0, 0, 0, 0))
        stroke = max(0, int(round(_number(data.get("outlineThickness"), 0.0) * scale)))
        if layer_type == "metric":
            metric = canonical_metric(data.get("metric")) or str(data.get("metric", ""))
            value, unit, label = format_metric(metric, metrics.get(metric), temperature_unit)
            number_size = max(6, int(round(_int(data.get("numberSize"), 100, 6, 640) * scale)))
            label_size = max(6, int(round(_int(data.get("textSize"), 28, 0, 320) * scale)))
            number_font = _font(number_size)
            label_font = _font(label_size)
            number_color = _rgba(data.get("numberColor"), (255, 255, 255, 255))
            label_color = _rgba(data.get("textColor"), (220, 220, 220, 255))
            main = f"{value}{unit}" if unit in {"%", "°C", "°F"} else value
            bbox = edraw.textbbox((0, 0), main, font=number_font, stroke_width=stroke)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            label_h = 0
            show_label = bool(data.get("showLabel", True)) and _int(data.get("textSize"), 28, 0, 320) > 0
            if show_label:
                lb = edraw.textbbox((0, 0), (unit if unit not in {"%", "°C", "°F"} and unit else label), font=label_font, stroke_width=stroke)
                label_h = lb[3] - lb[1] + max(1, int(5 * scale))
            start_y = y - (th + label_h) / 2
            edraw.text((x - tw / 2 - bbox[0], start_y - bbox[1]), main, font=number_font, fill=number_color, stroke_width=stroke, stroke_fill=outline_color)
            if show_label:
                label_text = unit if unit not in {"%", "°C", "°F"} and unit else label
                lb = edraw.textbbox((0, 0), label_text, font=label_font, stroke_width=stroke)
                lw = lb[2] - lb[0]
                edraw.text((x - lw / 2 - lb[0], start_y + th + max(1, int(5 * scale)) - lb[1]), label_text, font=label_font, fill=label_color, stroke_width=stroke, stroke_fill=outline_color)
        elif layer_type == "text":
            font = _font(max(6, int(round(_int(data.get("textSize"), 32, 6, 320) * scale))))
            _draw_centered_text(element, (x, y), _text(data.get("text"), "", MAX_TEXT_LENGTH), font, _rgba(data.get("textColor"), (255, 255, 255, 255)), stroke_width=stroke, stroke_fill=outline_color)
        elif layer_type == "divider":
            w = max(1, int(round(_number(data.get("width"), 2.0, 1.0, 2000.0) * scale_x)))
            h = max(1, int(round(_number(data.get("height"), 100.0, 1.0, 2000.0) * scale_y)))
            edraw.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=_rgba(data.get("color"), (255, 255, 255, 255)), outline=outline_color if stroke else None, width=stroke or 1)
        elif layer_type == "clock":
            mode = str(data.get("mode", "24h"))
            fmt = str(data.get("format", "HH:mm"))
            if mode == "12h":
                text = now.strftime("%I:%M:%S %p" if "ss" in fmt else "%I:%M %p").lstrip("0")
            else:
                text = now.strftime("%H:%M:%S" if "ss" in fmt else "%H:%M")
            font = _font(max(6, int(round(_int(data.get("fontSize"), 64, 6, 320) * scale))))
            _draw_centered_text(element, (x, y), text, font, _rgba(data.get("color"), (255, 255, 255, 255)), stroke_width=stroke, stroke_fill=outline_color)
        elif layer_type == "shape":
            w = max(1, int(round(_number(data.get("width"), 100.0, 1.0, 2000.0) * scale_x)))
            h = max(1, int(round(_number(data.get("height"), 100.0, 1.0, 2000.0) * scale_y)))
            radius = max(0, int(round(_number(data.get("radius"), 0.0, 0.0, 1000.0) * scale)))
            border_w = max(0, int(round(_number(data.get("borderWidth"), 0.0, 0.0, 80.0) * scale)))
            box = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            edraw.rounded_rectangle(
                box, radius=min(radius, w // 2, h // 2),
                fill=_rgba(data.get("fillColor"), (0, 0, 0, 0)),
                outline=_rgba(data.get("borderColor"), (0, 0, 0, 0)) if border_w else None,
                width=border_w or 1,
            )
        elif layer_type == "radial_graphic":
            metric = canonical_metric(data.get("metric")) or str(data.get("metric", ""))
            raw_value = metrics.get(metric)
            try:
                value = float(raw_value) if raw_value is not None else 0.0
            except (TypeError, ValueError):
                value = 0.0
            if metric in {"cpuTemp", "gpuTemp", "liquidTemp"}:
                fraction = max(0.0, min(1.0, value / 100.0))
            elif metric in {"cpuLoad", "gpuLoad", "ramLoad"}:
                fraction = max(0.0, min(1.0, value / 100.0))
            else:
                fraction = max(0.0, min(1.0, value / 5000.0))
            size = max(8, int(round(_number(data.get("size"), 200.0, 20.0, 1200.0) * scale)))
            stroke_w = max(1, int(round(_number(data.get("strokeWidth"), 8.0, 1.0, 100.0) * scale)))
            track_w = max(1, int(round(_number(data.get("trackWidth"), stroke_w, 1.0, 100.0) * scale)))
            total = _number(data.get("totalAngle"), 270.0, 5.0, 360.0)
            start = -90.0 - total / 2.0
            if bool(data.get("reverse", False)):
                end = start - total * fraction
            else:
                end = start + total * fraction
            box = (x - size / 2, y - size / 2, x + size / 2, y + size / 2)
            if bool(data.get("trackEnabled", True)):
                edraw.arc(box, start=start, end=start + total, fill=_rgba(data.get("trackColor"), (255, 255, 255, 45)), width=track_w)
            edraw.arc(box, start=min(start, end), end=max(start, end), fill=_rgba(data.get("strokeColor"), (0, 170, 255, 255)), width=stroke_w)
        elif layer_type == "sensor_chart":
            w = max(12, int(round(_number(data.get("width"), 180.0, 10.0, 1000.0) * scale_x)))
            h = max(12, int(round(_number(data.get("height"), 70.0, 10.0, 1000.0) * scale_y)))
            color = _rgba(data.get("chartColor"), (0, 170, 255, 255))
            # OHC currently has only the instantaneous value at import-render
            # time, so draw a deterministic sparkline around that point rather
            # than pretending historical samples exist.
            metric = canonical_metric(data.get("metric")) or str(data.get("metric", ""))
            try:
                value = float(metrics.get(metric) or 0.0)
            except (TypeError, ValueError):
                value = 0.0
            fraction = max(0.05, min(0.95, value / 100.0))
            left, top = x - w / 2, y - h / 2
            points = []
            for idx in range(18):
                px = left + (w * idx / 17)
                wobble = math.sin(idx * 0.85 + now.timestamp() * 1.8) * h * 0.08
                py = top + h * (1.0 - fraction) + wobble
                points.append((px, py))
            edraw.rectangle((left, top, left + w, top + h), outline=(255, 255, 255, 45), width=1)
            edraw.line(points, fill=color, width=max(1, int(scale * 3)))
        elif layer_type == "analog_clock":
            size = max(24, int(round(_number(data.get("size"), 160.0, 30.0, 1200.0) * scale)))
            radius = size / 2
            face = _rgba(data.get("faceColor"), (0, 0, 0, 210))
            border = _rgba(data.get("borderColor"), (255, 255, 255, 180))
            border_w = max(1, int(round(_number(data.get("borderWidth"), 2.0, 0.0, 30.0) * scale)))
            edraw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=face, outline=border, width=border_w)
            tick_color = _rgba(data.get("tickColor"), (255, 255, 255, 130))
            for tick in range(12):
                a = math.radians(tick * 30 - 90)
                r1, r2 = radius * 0.76, radius * 0.90
                edraw.line((x + math.cos(a)*r1, y + math.sin(a)*r1, x + math.cos(a)*r2, y + math.sin(a)*r2), fill=tick_color, width=max(1, int(scale*2)))
            hour = now.hour % 12 + now.minute / 60.0
            minute = now.minute + now.second / 60.0
            second = now.second + now.microsecond / 1_000_000.0
            for angle_value, length, color_value, width_value in (
                (hour * 30 - 90, .48, data.get("hourHandColor"), 4),
                (minute * 6 - 90, .68, data.get("minuteHandColor"), 3),
            ):
                a = math.radians(angle_value)
                edraw.line((x, y, x + math.cos(a)*radius*length, y + math.sin(a)*radius*length), fill=_rgba(color_value, (255,255,255,255)), width=max(1, int(width_value*scale)))
            if bool(data.get("showSecondHand", True)):
                a = math.radians(second * 6 - 90)
                edraw.line((x, y, x + math.cos(a)*radius*.76, y + math.sin(a)*radius*.76), fill=_rgba(data.get("secondHandColor"), (255,0,0,255)), width=max(1, int(scale*2)))
            edraw.ellipse((x-2*scale, y-2*scale, x+2*scale, y+2*scale), fill=(255,255,255,255))
        elif layer_type == "date":
            fmt = _date_format(str(data.get("format", "DD.MM.YYYY")))
            try:
                text = now.strftime(fmt)
            except ValueError:
                text = now.strftime("%d.%m.%Y")
            font = _font(max(6, int(round(_int(data.get("fontSize"), 36, 6, 320) * scale))))
            _draw_centered_text(element, (x, y), text, font, _rgba(data.get("color"), (255, 255, 255, 255)), stroke_width=stroke, stroke_fill=outline_color)
        else:
            continue
        if angle:
            # Rotate the complete element canvas around its center. Source x/y
            # coordinates are center-relative in NZXT-ESC, matching OHC's model.
            element = element.rotate(-angle, resample=Image.Resampling.BICUBIC, center=(x, y))
        image.alpha_composite(element)
        drawn_layers += 1
    if drawn_layers == 0:
        fallback = _image_from_data_uri(background.get("previewData"), target_resolution)
        if fallback is not None:
            return fallback
    return image.convert("RGB")


def render_import_preview(
    profile: dict[str, Any], metrics: dict[str, object] | None = None, *,
    temperature_unit: str = "c", target_resolution: tuple[int, int] = LCD_RESOLUTION,
):
    """Prefer the exporter-provided embedded preview for the import gate.

    It represents exactly what the user selected on the source website. OHC's
    own renderer is then used for live activation and safe approximations.
    """
    canvas = profile.get("canvas") if isinstance(profile.get("canvas"), dict) else {}
    background = canvas.get("background") if isinstance(canvas.get("background"), dict) else {}
    fallback = _image_from_data_uri(background.get("previewData"), target_resolution)
    if fallback is not None:
        return fallback
    return render_profile(profile, metrics, temperature_unit=temperature_unit, target_resolution=target_resolution)


class LcdProfileStore:
    """Persistent local OHC LCD profile library with non-destructive imports."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.previews_dir = self.root / "previews"
        self.media_dir = self.root / "media"
        self.fonts_dir = self.root / "fonts"
        for folder in (self.previews_dir, self.media_dir, self.fonts_dir):
            folder.mkdir(parents=True, exist_ok=True)
        self.index_file = self.root / "profiles.json"

    def load(self) -> list[dict[str, Any]]:
        if not self.index_file.is_file():
            return []
        try:
            payload = json.loads(self.index_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        profiles = payload.get("profiles") if isinstance(payload, dict) else []
        if not isinstance(profiles, list):
            return []
        result: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in profiles[:512]:
            if not isinstance(item, dict):
                continue
            profile_id = str(item.get("id", ""))
            if not profile_id or profile_id in seen:
                item = copy.deepcopy(item)
                item["id"] = str(uuid.uuid4())
            seen.add(str(item["id"]))
            result.append(item)
        return result

    def save(self, profiles: Iterable[dict[str, Any]]) -> None:
        payload = {"schema": OHC_LCD_PROFILE_SCHEMA, "profiles": list(profiles)}
        temporary = self.index_file.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.index_file)

    def write_preview(self, profile: dict[str, Any], metrics: dict[str, object] | None = None, *, temperature_unit: str = "c") -> Path:
        path = self.previews_dir / f"{profile.get('id', uuid.uuid4())}.png"
        render_profile(profile, metrics, temperature_unit=temperature_unit).save(path, format="PNG", optimize=True)
        return path

    def export_profile(self, profile: dict[str, Any], target: Path) -> Path:
        target = Path(target)
        payload = {"format": "open-hardware-control-lcd-profile", "schema": OHC_LCD_PROFILE_SCHEMA, "profile": profile}
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return target

    def import_ohc_profile(self, path: Path) -> dict[str, Any]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("format") != "open-hardware-control-lcd-profile" or not isinstance(payload.get("profile"), dict):
            raise ValueError("Keine gültige OHC-LCD-Profildatei.")
        return clone_profile(payload["profile"], name=str(payload["profile"].get("name", "Importiertes OHC-Profil")))

    def backup(
        self,
        profiles: Iterable[dict[str, Any]],
        target: Path,
        *,
        settings: dict[str, Any] | None = None,
    ) -> Path:
        target = Path(target)
        manifest = {
            "format": "open-hardware-control-lcd-profile-backup",
            "schema": OHC_LCD_PROFILE_SCHEMA,
            "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "profiles": list(profiles),
            "settings": copy.deepcopy(settings or {}),
        }
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
            for folder_name, folder in (("previews", self.previews_dir), ("media", self.media_dir), ("fonts", self.fonts_dir)):
                if folder.is_dir():
                    for path in sorted(folder.iterdir()):
                        if path.is_file() and path.stat().st_size <= 32 * 1024 * 1024:
                            archive.write(path, arcname=f"{folder_name}/{path.name}")
        return target

    def restore_backup(self, path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        path = Path(path)
        with zipfile.ZipFile(path, "r") as archive:
            names = archive.namelist()
            if "manifest.json" not in names:
                raise ValueError("Backup enthält keine manifest.json.")
            if any(name.startswith("/") or ".." in Path(name).parts for name in names):
                raise ValueError("Unsicherer Pfad im Backup erkannt.")
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            if not isinstance(manifest, dict) or manifest.get("format") != "open-hardware-control-lcd-profile-backup":
                raise ValueError("Unbekanntes LCD-Backupformat.")
            raw_profiles = manifest.get("profiles") if isinstance(manifest.get("profiles"), list) else []
            profiles = [clone_profile(item, name=str(item.get("name", "Wiederhergestelltes Profil"))) for item in raw_profiles if isinstance(item, dict)][:512]
            copied = 0
            for name in names:
                parts = Path(name).parts
                if len(parts) != 2 or parts[0] not in {"previews", "media", "fonts"} or not parts[1]:
                    continue
                data = archive.read(name)
                if len(data) > 32 * 1024 * 1024:
                    continue
                destination = {"previews": self.previews_dir, "media": self.media_dir, "fonts": self.fonts_dir}[parts[0]] / Path(parts[1]).name
                if destination.exists():
                    destination = destination.with_name(f"{destination.stem}-{uuid.uuid4().hex[:8]}{destination.suffix}")
                destination.write_bytes(data)
                copied += 1
        return profiles, {
            "profiles": len(profiles),
            "files": copied,
            "settings": manifest.get("settings") if isinstance(manifest.get("settings"), dict) else {},
        }

# Optional Qt dialogs live here so the core importer stays usable in tests and
# command-line validation without depending on a running QApplication.
try:  # pragma: no cover - exercised by GUI/static tests
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSpinBox,
        QTableWidget,
        QTableWidgetItem,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    QDialog = object  # type: ignore[misc,assignment]


_STATUS_LABELS = {
    "direct": "Unterstützt",
    "approximate": "Angenähert",
    "unsupported": "Nicht unterstützt",
    "blocked": "Blockiert",
    "warning": "Hinweis",
}


def layer_summary(layer: dict[str, Any]) -> str:
    data = layer.get("data") if isinstance(layer.get("data"), dict) else {}
    layer_type = str(layer.get("type", ""))
    if layer_type == "metric":
        metric = canonical_metric(data.get("metric")) or str(data.get("metric", "?"))
        return METRIC_DEFINITIONS.get(metric, {}).get("label", metric)
    if layer_type == "text":
        return str(data.get("text", ""))[:80]
    if layer_type == "clock":
        return f"Uhr · {data.get('format', 'HH:mm')}"
    if layer_type == "date":
        return f"Datum · {data.get('format', 'DD.MM.YYYY')}"
    if layer_type == "divider":
        return "Trennlinie"
    return str(data.get("rawType", layer_type or "Unbekannt"))


class NzxtEscImportPreviewDialog(QDialog):
    """Mandatory preview/report gate before an imported profile is stored."""

    def __init__(self, result: ImportResult, preview_path: Path, parent=None):
        super().__init__(parent)
        self.result = result
        self.setWindowTitle("NZXT-ESC-Profil importieren · Vorschau")
        self.resize(920, 620)
        layout = QVBoxLayout(self)
        intro = QLabel(
            "Das Profil wird noch nicht aktiviert. Prüfe zuerst die Vorschau und die Liste der "
            "unterstützten, angenäherten, fehlenden oder blockierten Bestandteile."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        body = QHBoxLayout()
        preview_column = QVBoxLayout()
        preview_label = QLabel()
        preview_label.setFixedSize(320, 320)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(str(preview_path))
        if not pixmap.isNull():
            preview_label.setPixmap(
                pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        preview_column.addWidget(preview_label, alignment=Qt.AlignmentFlag.AlignTop)
        source = result.profile.get("source", {})
        source_label = QLabel(
            f"<b>{result.profile.get('name', 'Importiertes Profil')}</b><br>"
            f"Schema: {source.get('schemaVersion', '?')} · Quelle: {source.get('fileName', '—')}"
        )
        source_label.setWordWrap(True)
        preview_column.addWidget(source_label)
        preview_column.addStretch()
        body.addLayout(preview_column)

        table = QTableWidget(len(result.issues), 3)
        table.setHorizontalHeaderLabels(["Status", "Element", "Details"])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setWordWrap(True)
        for row, issue in enumerate(result.issues):
            table.setItem(row, 0, QTableWidgetItem(_STATUS_LABELS.get(issue.status, issue.status)))
            table.setItem(row, 1, QTableWidgetItem(issue.item))
            table.setItem(row, 2, QTableWidgetItem(issue.detail))
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)
        body.addWidget(table, 1)
        layout.addLayout(body, 1)

        counts = result.counts
        summary = QLabel(
            f"Unterstützt: {counts.get('direct', 0)} · Angenähert: {counts.get('approximate', 0)} · "
            f"Nicht unterstützt: {counts.get('unsupported', 0)} · Blockiert: {counts.get('blocked', 0)} · "
            f"Hinweise: {counts.get('warning', 0)}"
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)

        buttons = QDialogButtonBox()
        import_button = buttons.addButton("Als neues Profil importieren", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = buttons.addButton("Abbrechen", QDialogButtonBox.ButtonRole.RejectRole)
        import_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(buttons)


class LcdProfileEditorDialog(QDialog):
    """Reduced editor for safe post-import changes to an OHC-local profile."""

    def __init__(self, profile: dict[str, Any], parent=None):
        super().__init__(parent)
        self.working = copy.deepcopy(profile)
        self._loading = False
        self._current_layer_id = ""
        self.setWindowTitle(f"LCD-Profil bearbeiten · {profile.get('name', '')}")
        self.resize(1050, 700)
        root = QVBoxLayout(self)

        note = QLabel(
            "Bearbeitet wird ausschließlich die lokale OHC-Kopie. Die ursprüngliche Importfassung bleibt für "
            "„Importierten Originalzustand wiederherstellen“ erhalten. Ebenen können per Drag-and-drop sortiert werden."
        )
        note.setWordWrap(True)
        root.addWidget(note)

        body = QHBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Ebene", "Typ", "Inhalt / Sensor", "Status"])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setColumnWidth(0, 75)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 250)
        self._populate_tree()
        self.tree.itemSelectionChanged.connect(self._selection_changed)
        body.addWidget(self.tree, 5)

        editor = QGroupBox("Ausgewählte Ebene")
        form = QFormLayout(editor)
        self.visible_checkbox = QCheckBox("Ebene sichtbar")
        self.locked_checkbox = QCheckBox("Ebene sperren")
        self.metric_combo = QComboBox()
        for metric, label in metric_choices():
            self.metric_combo.addItem(label, metric)
        self.auto_label_checkbox = QCheckBox("Passende Beschriftung automatisch ändern")
        self.auto_label_checkbox.setChecked(bool(self.working.get("autoUpdateMatchingLabels", True)))
        self.text_input = QLineEdit()
        self.primary_color = QLineEdit()
        self.secondary_color = QLineEdit()
        self.number_size = QSpinBox(); self.number_size.setRange(0, 640)
        self.text_size = QSpinBox(); self.text_size.setRange(0, 320)
        self.x_spin = QSpinBox(); self.x_spin.setRange(-4096, 4096)
        self.y_spin = QSpinBox(); self.y_spin.setRange(-4096, 4096)
        self.angle_spin = QSpinBox(); self.angle_spin.setRange(0, 359)
        form.addRow(self.visible_checkbox)
        form.addRow(self.locked_checkbox)
        form.addRow("Sensorquelle", self.metric_combo)
        form.addRow(self.auto_label_checkbox)
        form.addRow("Text", self.text_input)
        form.addRow("Hauptfarbe / Hex", self.primary_color)
        form.addRow("Zweitfarbe / Hex", self.secondary_color)
        form.addRow("Wert-/Schriftgröße", self.number_size)
        form.addRow("Labelgröße", self.text_size)
        form.addRow("Position X", self.x_spin)
        form.addRow("Position Y", self.y_spin)
        form.addRow("Drehung", self.angle_spin)
        apply_layer = QPushButton("Änderungen an Ebene übernehmen")
        apply_layer.clicked.connect(self._commit_current)
        form.addRow(apply_layer)
        body.addWidget(editor, 3)
        root.addLayout(body, 1)

        buttons = QDialogButtonBox()
        save_button = buttons.addButton("Änderungen speichern", QDialogButtonBox.ButtonRole.AcceptRole)
        discard_button = buttons.addButton("Ungespeicherte Änderungen verwerfen", QDialogButtonBox.ButtonRole.RejectRole)
        save_button.clicked.connect(self._accept_changes)
        discard_button.clicked.connect(self.reject)
        root.addWidget(buttons)
        if self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def _populate_tree(self) -> None:
        self.tree.clear()
        for index, layer in enumerate(self.working.get("layers", []), start=1):
            if not isinstance(layer, dict):
                continue
            item = QTreeWidgetItem([
                str(index),
                str(layer.get("type", "")),
                layer_summary(layer),
                _STATUS_LABELS.get(str(layer.get("status", "direct")), str(layer.get("status", ""))),
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, str(layer.get("id", "")))
            self.tree.addTopLevelItem(item)

    def _layer(self, layer_id: str) -> dict[str, Any] | None:
        for layer in self.working.get("layers", []):
            if isinstance(layer, dict) and str(layer.get("id", "")) == layer_id:
                return layer
        return None

    def _selection_changed(self) -> None:
        if self._loading:
            return
        self._commit_current()
        item = self.tree.currentItem()
        if item is None:
            self._current_layer_id = ""
            return
        layer_id = str(item.data(0, Qt.ItemDataRole.UserRole) or "")
        layer = self._layer(layer_id)
        if layer is None:
            return
        self._current_layer_id = layer_id
        self._loading = True
        try:
            data = layer.get("data") if isinstance(layer.get("data"), dict) else {}
            layer_type = str(layer.get("type", ""))
            self.visible_checkbox.setChecked(bool(layer.get("visible", True)))
            self.locked_checkbox.setChecked(bool(layer.get("locked", False)))
            metric = canonical_metric(data.get("metric")) or "cpuTemp"
            idx = self.metric_combo.findData(metric)
            self.metric_combo.setCurrentIndex(max(0, idx))
            self.metric_combo.setEnabled(layer_type == "metric")
            self.auto_label_checkbox.setEnabled(layer_type == "metric")
            self.text_input.setText(str(data.get("text", "")))
            self.text_input.setEnabled(layer_type == "text")
            if layer_type == "metric":
                self.primary_color.setText(str(data.get("numberColor", "#ffffff")))
                self.secondary_color.setText(str(data.get("textColor", "#ffffff")))
                self.number_size.setValue(_int(data.get("numberSize"), 100, 0, 640))
                self.text_size.setValue(_int(data.get("textSize"), 28, 0, 320))
            elif layer_type == "text":
                self.primary_color.setText(str(data.get("textColor", "#ffffff")))
                self.secondary_color.setText("")
                self.number_size.setValue(_int(data.get("textSize"), 32, 0, 640))
                self.text_size.setValue(0)
            elif layer_type in {"clock", "date"}:
                self.primary_color.setText(str(data.get("color", "#ffffff")))
                self.secondary_color.setText("")
                self.number_size.setValue(_int(data.get("fontSize"), 48, 0, 640))
                self.text_size.setValue(0)
            elif layer_type == "divider":
                self.primary_color.setText(str(data.get("color", "#ffffff")))
                self.secondary_color.setText("")
                self.number_size.setValue(_int(data.get("width"), 2, 0, 640))
                self.text_size.setValue(_int(data.get("height"), 100, 0, 320))
            else:
                self.primary_color.setText("")
                self.secondary_color.setText("")
                self.number_size.setValue(0)
                self.text_size.setValue(0)
            self.x_spin.setValue(_int(layer.get("x"), 0, -4096, 4096))
            self.y_spin.setValue(_int(layer.get("y"), 0, -4096, 4096))
            self.angle_spin.setValue(_int(layer.get("angle"), 0, 0, 359))
        finally:
            self._loading = False

    def _commit_current(self) -> None:
        if self._loading or not self._current_layer_id:
            return
        layer = self._layer(self._current_layer_id)
        if layer is None:
            return
        data = layer.setdefault("data", {})
        layer["visible"] = self.visible_checkbox.isChecked()
        layer["locked"] = self.locked_checkbox.isChecked()
        layer["x"] = self.x_spin.value()
        layer["y"] = self.y_spin.value()
        layer["angle"] = self.angle_spin.value()
        layer_type = str(layer.get("type", ""))
        if layer_type == "metric":
            new_metric = str(self.metric_combo.currentData() or "cpuTemp")
            update_metric(self.working, self._current_layer_id, new_metric, auto_label=self.auto_label_checkbox.isChecked())
            data = layer.setdefault("data", {})
            data["numberColor"] = normalize_color(self.primary_color.text(), str(data.get("numberColor", "#ffffff")))
            data["textColor"] = normalize_color(self.secondary_color.text(), str(data.get("textColor", "#ffffff")))
            data["numberSize"] = self.number_size.value()
            data["textSize"] = self.text_size.value()
        elif layer_type == "text":
            data["text"] = _text(self.text_input.text(), "", MAX_TEXT_LENGTH)
            data["textColor"] = normalize_color(self.primary_color.text(), str(data.get("textColor", "#ffffff")))
            data["textSize"] = self.number_size.value()
        elif layer_type in {"clock", "date"}:
            data["color"] = normalize_color(self.primary_color.text(), str(data.get("color", "#ffffff")))
            data["fontSize"] = self.number_size.value()
        elif layer_type == "divider":
            data["color"] = normalize_color(self.primary_color.text(), str(data.get("color", "#ffffff")))
            data["width"] = self.number_size.value()
            data["height"] = self.text_size.value()
        self.working["autoUpdateMatchingLabels"] = self.auto_label_checkbox.isChecked()
        self.working["modifiedAt"] = datetime.now().astimezone().isoformat(timespec="seconds")
        # Refresh visible row text without rebuilding the tree (which would lose drag order).
        for row in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(row)
            if str(item.data(0, Qt.ItemDataRole.UserRole) or "") == self._current_layer_id:
                item.setText(2, layer_summary(layer))
                break

    def _accept_changes(self) -> None:
        self._commit_current()
        ordered_ids = [
            str(self.tree.topLevelItem(row).data(0, Qt.ItemDataRole.UserRole) or "")
            for row in range(self.tree.topLevelItemCount())
        ]
        by_id = {str(layer.get("id", "")): layer for layer in self.working.get("layers", []) if isinstance(layer, dict)}
        self.working["layers"] = [by_id[layer_id] for layer_id in ordered_ids if layer_id in by_id]
        for row in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(row).setText(0, str(row + 1))
        self.accept()

    def profile(self) -> dict[str, Any]:
        return copy.deepcopy(self.working)
