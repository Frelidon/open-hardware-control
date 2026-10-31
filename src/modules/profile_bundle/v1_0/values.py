# SPDX-License-Identifier: GPL-3.0-or-later
"""Lossless supported settings values; portable JSON/path reference rewriting."""
import base64
import json
import math


def encode(value, depth=0):
    if depth > 32:
        raise ValueError("BUNDLE_VALUE_DEPTH")
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, (list, tuple)):
        return {"t": "tuple" if isinstance(value, tuple) else "list",
                "v": [encode(v, depth + 1) for v in value]}
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        return {"t": "map", "v": [[k, encode(v, depth + 1)] for k, v in value.items()]}
    if isinstance(value, bytes):
        return {"t": "bytes", "v": base64.b64encode(value).decode("ascii")}
    from PySide6.QtCore import QByteArray, QPoint, QRect, QSize
    if isinstance(value, QByteArray):
        return {"t": "QByteArray", "v": base64.b64encode(bytes(value)).decode("ascii")}
    if isinstance(value, QRect):
        return {"t": "QRect", "v": [value.x(), value.y(), value.width(), value.height()]}
    if isinstance(value, (QPoint, QSize)):
        return {"t": type(value).__name__, "v": list(value.toTuple())}
    raise ValueError("BUNDLE_UNSUPPORTED_VALUE:" + type(value).__name__)


def decode(value, depth=0):
    if depth > 32:
        raise ValueError("BUNDLE_VALUE_DEPTH")
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if not isinstance(value, dict) or set(value) != {"t", "v"}:
        raise ValueError("BUNDLE_VALUE_TYPE")
    kind, raw = value["t"], value["v"]
    if kind in {"list", "tuple", "map"} and isinstance(raw, list) and len(raw) <= 8192:
        if kind == "map":
            if not all(isinstance(p, list) and len(p) == 2 and isinstance(p[0], str) for p in raw):
                raise ValueError("BUNDLE_MAP")
            return {k: decode(v, depth + 1) for k, v in raw}
        result = [decode(v, depth + 1) for v in raw]
        return tuple(result) if kind == "tuple" else result
    if kind in {"bytes", "QByteArray"} and isinstance(raw, str):
        result = base64.b64decode(raw, validate=True)
        if kind == "bytes": return result
        from PySide6.QtCore import QByteArray
        return QByteArray(result)
    if kind in {"QPoint", "QSize", "QRect"} and isinstance(raw, list):
        from PySide6.QtCore import QPoint, QRect, QSize
        if len(raw) != (4 if kind == "QRect" else 2) or not all(type(v) is int and -(2 ** 31) <= v < 2 ** 31 for v in raw):
            raise ValueError("BUNDLE_GEOMETRY")
        return {"QPoint": QPoint, "QSize": QSize, "QRect": QRect}[kind](*raw)
    raise ValueError("BUNDLE_VALUE_TYPE")


def strings(value, depth=0):
    if depth > 32: raise ValueError("BUNDLE_VALUE_DEPTH")
    if isinstance(value, str):
        yield value
        if value[:1] in {"{", "["}:
            try: yield from strings(json.loads(value), depth + 1)
            except json.JSONDecodeError: pass
    elif isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from strings(v, depth + 1)
    elif isinstance(value, list):
        for v in value: yield from strings(v, depth + 1)


def relocate(value, mapping, depth=0):
    if depth > 32: raise ValueError("BUNDLE_VALUE_DEPTH")
    if isinstance(value, str):
        if value in mapping: return mapping[value]
        if value[:1] in {"{", "["}:
            try:
                raw = json.loads(value)
                updated = relocate(raw, mapping, depth + 1)
                if updated != raw: return json.dumps(updated, ensure_ascii=False)
            except json.JSONDecodeError: pass
        return value
    if isinstance(value, list): return [relocate(v, mapping, depth + 1) for v in value]
    if isinstance(value, dict):
        return {mapping.get(k, k): relocate(v, mapping, depth + 1) for k, v in value.items()}
    return value
