# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded QSettings persistence for exact, device-bound GPU profiles."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any

from .catalog import model_by_id


PROFILE_KEY = "gpu_control/profiles/v1"
SELECTED_KEY = "gpu_control/selected_profile/v1"
MAX_PROFILES = 32
MAX_CONFIG_BYTES = 64 * 1024
PRESENTATION_MAXIMIZED = "maximized"
PRESENTATIONS = {PRESENTATION_MAXIMIZED, "minimized", "fullscreen"}
SIZES = {"3840x2160", "7680x4320"}
DURATIONS = {15, 30, 60, 120}
ORIENTATIONS = {"horizontal", "vertical"}


def normalize_presentation(value: object) -> str:
    return str(value) if str(value) in PRESENTATIONS else PRESENTATION_MAXIMIZED


def _bounded_json_dict(value: object) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        decoded = json.loads(encoded)
    except (TypeError, ValueError):
        return None
    return decoded if isinstance(decoded, dict) and len(encoded.encode("utf-8")) <= MAX_CONFIG_BYTES else None


def config_digest(config: object) -> str:
    clean = _bounded_json_dict(config)
    if clean is None:
        return ""
    payload = json.dumps(clean, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def zero_rpm_state(config: object) -> bool | None:
    if not isinstance(config, dict):
        return None
    pmfw = config.get("pmfw_options")
    if isinstance(pmfw, dict) and isinstance(pmfw.get("zero_rpm"), bool):
        return pmfw["zero_rpm"]
    fan = config.get("fan_control_settings")
    if isinstance(fan, dict) and isinstance(fan.get("zero_rpm"), bool):
        return fan["zero_rpm"]
    return None


def normalize_profile(value: object) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    profile_id = str(value.get("id", ""))[:96]
    name = str(value.get("name", "")).strip()[:80]
    gpu_id = str(value.get("gpu_id", ""))[:160]
    config = _bounded_json_dict(value.get("config"))
    if not profile_id or not name or not gpu_id or config is None:
        return None
    digest = config_digest(config)
    claimed_digest = str(value.get("config_digest", ""))
    if claimed_digest and claimed_digest != digest:
        return None
    model_id = str(value.get("model_id", ""))[:96]
    if model_id and model_by_id(model_id) is None:
        model_id = ""
    try:
        duration = int(value.get("stress_duration", 30))
    except (TypeError, ValueError):
        duration = 30
    size = str(value.get("stress_size", "3840x2160"))
    orientation = str(value.get("orientation", "horizontal"))
    artwork = str(value.get("artwork", ""))[:1024]
    return {
        "id": profile_id,
        "name": name,
        "gpu_id": gpu_id,
        "model_id": model_id,
        "orientation": orientation if orientation in ORIENTATIONS else "horizontal",
        "artwork": artwork,
        "config": config,
        "config_digest": digest,
        "verified": bool(value.get("verified", False)),
        "activate_at_start": bool(value.get("activate_at_start", False)),
        "stress_duration": duration if duration in DURATIONS else 30,
        "stress_size": size if size in SIZES else "3840x2160",
        "stress_presentation": normalize_presentation(value.get("stress_presentation")),
        "zero_rpm": zero_rpm_state(config),
    }


def load_profiles(settings: Any) -> list[dict[str, Any]]:
    try:
        raw = json.loads(str(settings.value(PROFILE_KEY, "[]")))
    except (TypeError, ValueError):
        return []
    if not isinstance(raw, list):
        return []
    result: list[dict[str, Any]] = []
    for row in raw[:MAX_PROFILES]:
        clean = normalize_profile(row)
        if clean is not None and not any(item["id"] == clean["id"] for item in result):
            result.append(clean)
    return result


def save_profiles(settings: Any, profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clean: list[dict[str, Any]] = []
    for row in profiles[:MAX_PROFILES]:
        profile = normalize_profile(row)
        if profile is not None and not any(item["id"] == profile["id"] for item in clean):
            clean.append(profile)
    settings.setValue(PROFILE_KEY, json.dumps(clean, sort_keys=True, separators=(",", ":")))
    settings.sync()
    return clean


def append_or_replace_profile(settings: Any, profile: dict[str, Any]) -> list[dict[str, Any]]:
    clean = normalize_profile(profile)
    if clean is None:
        raise ValueError("Invalid GPU profile")
    profiles = [row for row in load_profiles(settings) if row["id"] != clean["id"]]
    if clean["activate_at_start"]:
        for row in profiles:
            if row["gpu_id"] == clean["gpu_id"]:
                row["activate_at_start"] = False
    profiles.append(deepcopy(clean))
    settings.setValue(SELECTED_KEY, clean["id"])
    return save_profiles(settings, profiles)


def remove_profile(settings: Any, profile_id: object) -> list[dict[str, Any]]:
    key = str(profile_id)
    profiles = save_profiles(settings, [row for row in load_profiles(settings) if row["id"] != key])
    if str(settings.value(SELECTED_KEY, "")) == key:
        settings.setValue(SELECTED_KEY, "")
        settings.sync()
    return profiles
