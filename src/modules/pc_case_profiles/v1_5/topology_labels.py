# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only configured ARGB lengths and reported fan connectors for callouts."""
import re
from rgb_devices import normalize_zone_configurations
from modules.rgb_studio.v1_15.argb_controls import slot_header_targets
from modules.rgb_studio.v1_15.led_topology_store import paths
from modules.rgb_studio.v1_15.gpu_motion import configured_count
from .channel_labels import channel_caption


def _header_in_note(zone, note):
    def clean(value):
        return re.sub(r"[_\s]", "", re.sub(r"_V2", "", str(value), flags=re.I)).casefold()
    name = clean(zone)
    aliases = {name, re.sub(r"^channel", "", name)}
    text = re.sub(r"_V2", "", str(note), flags=re.I).replace("_", "")
    return any(re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])",
                         text, re.I) for alias in aliases if alias)


def display_header_targets(host, slot):
    targets = slot_header_targets(host, slot)
    explicit = [target for target in targets if _header_in_note(target[1], slot.connection)]
    return explicit or targets


def slot_topology_label(host, slot):
    targets = display_header_targets(host, slot)
    counts, seen = [], set()
    configurations = normalize_zone_configurations(host.rgb_zone_configurations)
    for source, zone, _gpu in targets:
        source_id = host.openrgb_stable_ids.get(source.index, "")
        key = source_id, zone.casefold()
        if key in seen:
            continue
        seen.add(key)
        config = next((v for name, v in configurations.get(source_id, {}).items()
                       if name.casefold() == zone.casefold()), None)
        count = str(config["units"] * config["leds_per_unit"]) if config else "—"
        counts.append((zone, count))
    values = " / ".join(count for _zone, count in counts) or "—"
    # Multiple lengths refer to controller zones, never a guessed block total.
    led_line = f"LEDs{'/ARGB' if len(counts) > 1 else ''}: {values}"
    channel_by_id = {c.stable_id: c for c in host.chassis_mainboard_channels()}
    connectors = [channel_caption(host, channel_by_id[key]) for key, value in host.mainboard_layout_assignments.items()
                  if value == (slot.slot_id or slot.position) and key in channel_by_id]
    pwm_line = "PWM: " + (" / ".join(connectors) or "—")
    details = "\n".join(f"{zone}: {count} LEDs" for zone, count in counts)
    return led_line, pwm_line, details


def slot_led_path(host, slot):
    """Show only one saved physical path; never guess a shared header's order."""
    targets = display_header_targets(host, slot)
    if len(targets) != 1:
        return None
    source, zone, _gpu = targets[0]
    stable_id = host.openrgb_stable_ids.get(source.index, "")
    count = configured_count(host, stable_id, zone)
    path = paths(host).get(stable_id, {}).get(zone)
    if path is None or type(count) is not int or not 1 <= count <= 512:
        return None
    return path, count
