# SPDX-License-Identifier: GPL-3.0-or-later
"""Reusable bounded fan declarations; choosing/saving never writes hardware."""
import json
import hashlib
from .fan_profiles import normalize_profiles

KEY = "rgb_studio/fan_library_v1"
BUILTINS = (
    dict(brand="TZMRIT", model="Interstellar-V2", color="black", leds_per_fan=8),
    # Ten addressable LEDs are owner-observed on the Levita reference only.
    dict(brand="Thermalright", model="Levita Vision 360 · Radiator", color="black", leds_per_fan=10),
)
BRANDS = ("TZMRIT", "Jungle Leopard", "ARCTIC", "Corsair", "Lian Li", "Thermalright")


def identity(value):
    return value["brand"].casefold(), value["model"].casefold(), value["color"]


def normalize_library(raw):
    if not isinstance(raw, list):
        return []
    result = {}
    for value in raw[:128]:
        clean = normalize_profiles({"fan": value}).get("fan")
        if clean and clean["brand"] and clean["model"] and clean["leds_per_fan"]:
            result[identity(clean)] = clean
    return list(result.values())


def stored_library(host):
    try:
        return normalize_library(json.loads(str(host.settings.value(KEY, "[]"))))
    except (TypeError, ValueError):
        return []


def available_models(host):
    result = {identity(v): dict(v) for v in BUILTINS}
    result.update({identity(v): v for v in stored_library(host)})
    return list(result.values())


def available_brands(host):
    result = {v.casefold(): v for v in BRANDS}
    result.update({v["brand"].casefold(): v["brand"] for v in available_models(host)})
    return sorted(result.values(), key=str.casefold)


def remember_model(host, value):
    clean = normalize_library([value])
    if not clean:
        return False
    result = {identity(v): v for v in stored_library(host)}
    key = identity(clean[0])
    if key not in result and len(result) >= 128:
        return False
    result[key] = clean[0]
    host.settings.setValue(KEY, json.dumps(list(result.values()), ensure_ascii=False))
    host.settings.sync()
    return True


def zone_models(host):
    """Keep legacy model IDs; expose user models in the existing zone editor."""
    from rgb_devices import RGB_FAN_MODELS, RGBFanModel
    result = list(RGB_FAN_MODELS)
    for value in stored_library(host):
        token = hashlib.sha256(json.dumps(identity(value), ensure_ascii=False).encode()).hexdigest()[:24]
        color = host.tr_static("Schwarz" if value["color"] == "black" else "Weiß")
        result.append(RGBFanModel("custom-fan-" + token,
                                 f'{value["brand"]} {value["model"]} · {color}', value["leds_per_fan"], "normal"))
    return tuple(result)
