# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded personal fan declarations, separate from design/PWM state."""
import json

KEY = "rgb_studio/fan_profiles_v1"
FAN_POSITIONS = {"top", "front", "side", "bottom", "rear"}
PERSONAL_SLOTS = {"fans-front", "fans-side", "fans-psu-shroud", "fan-rear"}


def normalize_profiles(raw):
    if not isinstance(raw, dict):
        return {}
    result = {}
    for key, values in list(raw.items())[:128]:
        if not isinstance(key, str) or not 1 <= len(key) <= 96 or not isinstance(values, dict):
            continue
        brand, model, color = (values.get(name, "") for name in ("brand", "model", "color"))
        leds = values.get("leds_per_fan", 0)
        if (not all(isinstance(v, str) and len(v) <= 64 for v in (brand, model))
                or any(ord(c) < 32 for c in key + brand + model)
                or color not in {"black", "white"} or type(leds) is not int or not 0 <= leds <= 512):
            continue
        result[key] = dict(brand=brand.strip(), model=model.strip(), color=color, leds_per_fan=leds)
    return result


def profiles(host):
    try:
        return normalize_profiles(json.loads(str(host.settings.value(KEY, "{}"))))
    except (ValueError, TypeError):
        return {}


def profile_for_slot(host, slot):
    key = slot.slot_id or slot.position
    saved = profiles(host).get(key)
    if saved is not None:
        return saved
    if str(host.settings.value("rgb_studio/layout_profile", "")) == "flori" and key in PERSONAL_SLOTS:
        # ASIN B0CN39T7QN; eight addressable LEDs are owner-observed, not a
        # verified general manufacturer count. Never migrate unrelated headers.
        return dict(brand="TZMRIT", model="Interstellar-V2", color="black", leds_per_fan=8)
    if (str(host.settings.value("rgb_studio/layout_profile", "")) == "flori"
            and key == "radiator-top" and "thermalright" in slot.name.casefold()):
        return dict(brand="Thermalright", model="Levita Vision 360 · Radiator", color="black", leds_per_fan=10)
    return dict(brand="", model="", color="black", leds_per_fan=0)


def remember_profile(host, key, values):
    current = profiles(host)
    clean = normalize_profiles({key: values})
    if not clean or (key not in current and len(current) >= 128):
        return False
    current.update(clean)
    host.settings.setValue(KEY, json.dumps(current, ensure_ascii=False))
    host.settings.sync()
    return True


def declared_total(profile, count):
    leds = profile.get("leds_per_fan", 0)
    if type(count) is not int or not 1 <= count <= 12 or type(leds) is not int or not 1 <= leds <= 512:
        return None
    return count * leds
