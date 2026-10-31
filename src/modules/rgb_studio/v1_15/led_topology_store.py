# SPDX-License-Identifier: GPL-3.0-or-later
"""Physical path settings are independent of effect/profile snapshots."""
import json
from .led_topology import DIRECTIONS, normalize_path

KEY = "rgb_studio/led_paths_v1"
DIRECTION_KEY = "rgb_studio/case_effect_direction_v1"


def paths(host):
    try: raw = json.loads(str(host.settings.value(KEY, "{}")))
    except (TypeError, ValueError): return {}
    if not isinstance(raw, dict): return {}
    result = {}
    for source, zones in list(raw.items())[:512]:
        if not isinstance(source, str) or not source.startswith("openrgb:") or len(source) > 96 or not isinstance(zones, dict): continue
        clean = {name: normalize_path(path) for name, path in list(zones.items())[:64]
                 if isinstance(name, str) and name and len(name) <= 96 and not any(ord(c) < 32 for c in source + name)}
        result[source] = {name: path for name, path in clean.items() if path is not None}
    return result


def direction(host):
    raw = str(host.settings.value(DIRECTION_KEY, "local"))
    return raw if raw in DIRECTIONS else "local"


def set_case_direction(host, movement):
    """Set the visible case-space travel direction without touching hardware routing."""
    if movement not in {"local", *DIRECTIONS}:
        return False
    raw = paths(host)
    for zones in raw.values():
        for path in zones.values():
            path["direction"] = movement
    host.settings.setValue(KEY, json.dumps(raw, ensure_ascii=False))
    host.settings.setValue(DIRECTION_KEY, movement)
    host.settings.sync()
    host.rgb_last_effect_request_signature = None
    return True


def remember_path(host, source, name, value, movement, count):
    if (type(count) is not int or not 1 <= count <= 4096 or not isinstance(source, str)
            or not source.startswith("openrgb:") or len(source) > 96 or not isinstance(name, str)
            or not name or len(name) > 96 or any(ord(c) < 32 for c in source + name)):
        return False
    clean = normalize_path(value)
    device = next((d for d in host.openrgb_devices if host.openrgb_stable_ids.get(d.index) == source
                   and d.supports_direct and name in d.zones), None)
    if device is None or clean is None or movement not in {"local", *DIRECTIONS}: return False
    if clean["kind"] == "ring" and (count % clean["units"] or clean["units"] > count): return False
    # The case-space travel direction belongs to this physical header.  The
    # former global setting made a horizontal fan bank overwrite vertical
    # banks and also coupled the GPU strip to its support bracket.
    clean["direction"] = movement
    raw = paths(host)
    if source not in raw and len(raw) >= 512: return False
    zones = raw.setdefault(source, {})
    if name not in zones and len(zones) >= 64: return False
    zones[name] = clean
    host.settings.setValue(KEY, json.dumps(raw, ensure_ascii=False))
    host.settings.sync()
    host.rgb_last_effect_request_signature = None
    if hasattr(host, "log_message"):
        leds_per_fan = count // clean["units"] if count % clean["units"] == 0 else "ungeteilt"
        layout = "Reihe" if clean["kind"] == "line" else "Ring"
        host.log_message(f"ARGB-DIAG: op=led-path-save · controller={source} · zone={name} · layout={layout} · "
                         f"total_leds={count} · fan_count={clean['units']} · leds_per_fan={leds_per_fan} · "
                         f"led1={clean['start']} · last={clean['end']} · clockwise={clean['clockwise']} · "
                         f"reverse_units={clean.get('reverse_units', False)} · "
                         f"reverse_effect={clean.get('reverse_effect', False)} · "
                         f"case_direction={clean['direction']} · settings-only · physical_readback=unavailable")
    return True


def case_rectangles(host, source):
    """Reuse actual component layout; ambiguous shared headers stay local."""
    from PySide6.QtCore import QRectF
    from modules.pc_case_profiles.v1_5.case_geometry import fitted_slot_rect
    from .argb_controls import slot_header_targets
    found, duplicate = {}, set()
    for slot in host.rgb_layout_slots:
        targets = slot_header_targets(host, slot)
        if len(targets) != 1: continue
        d, name, _gpu = targets[0]
        if host.openrgb_stable_ids.get(d.index) != source: continue
        if name in found: duplicate.add(name); continue
        # Preview resizing is presentation-only: physical projection uses 100%.
        r = fitted_slot_rect(slot, QRectF(0, 0, 760, 540), scale=1.)
        found[name] = ((r.x() / 760, r.y() / 540, r.width() / 760, r.height() / 540),
                       slot.position not in {"front", "side", "rear"})
    return {name: data for name, data in found.items() if name not in duplicate}
