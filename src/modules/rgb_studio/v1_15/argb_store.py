#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit manual topology is physical setup, not an RGB design setting."""

import json
from .argb_diagnostics import log_argb_zones

KEY = "rgb_studio/manual_zone_counts"


def manual_headers(host):
    if not hasattr(host, "settings"):
        return {}
    try:
        raw = json.loads(str(host.settings.value(KEY, "{}")))
        if not isinstance(raw, dict):
            return {}
        return {key: [n for n in names[:64] if isinstance(n, str) and len(n) <= 96]
                for key, names in list(raw.items())[:512]
                if isinstance(key, str) and len(key) <= 96 and isinstance(names, list)}
    except (TypeError, ValueError):
        return {}


def remember_headers(host, stable_id, names):
    if not hasattr(host, "settings"):
        return
    pins = manual_headers(host)
    pins[stable_id] = list(dict.fromkeys([*pins.get(stable_id, []), *names]))[:64]
    host.settings.setValue(KEY, json.dumps(pins, ensure_ascii=False))


def retain_manual_headers(host, restored):
    for controller, names in manual_headers(host).items():
        saved = host.rgb_zone_configurations.get(controller, {})
        retained = {n: dict(v) for n, v in saved.items()
                    if n.casefold() in {name.casefold() for name in names}}
        if retained:
            restored[controller] = {**saved, **restored.get(controller, {}), **retained}
    return restored


def save_controller_diagnostics(host, source, zones, operation, configuration):
    remember_headers(host, host.openrgb_stable_ids[source.index], configuration)
    log_argb_zones(host, source, zones, operation, configuration)
