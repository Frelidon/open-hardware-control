# SPDX-License-Identifier: GPL-3.0-or-later
"""Single source of truth for user-visible feature maturity and versions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeatureLifecycle:
    key: str
    version: str
    stage: str

    @property
    def label(self) -> str:
        return f"{self.stage} · v{self.version}"


_FEATURES = (
    FeatureLifecycle("overview", "0.9.0", "Beta"),
    FeatureLifecycle("gpu", "0.8.0", "Beta"),
    FeatureLifecycle("case", "0.9.0", "Beta"),
    FeatureLifecycle("hardware_checker", "0.6.0", "Alpha"),
    FeatureLifecycle("snapshot_manager", "0.5.0", "Alpha"),
    FeatureLifecycle("automations", "0.4.0", "Alpha"),
    FeatureLifecycle("programs", "0.5.0", "Alpha"),
    FeatureLifecycle("cooling", "0.9.0", "Beta"),
    FeatureLifecycle("rgb_studio", "0.9.0-rc1", "Release Candidate"),
    FeatureLifecycle("lcd", "0.9.0-rc1", "Release Candidate"),
    FeatureLifecycle("display_effects", "0.8.0", "Beta"),
    FeatureLifecycle("profiles", "0.9.0", "Beta"),
    FeatureLifecycle("openlinkhub", "0.4.0", "Alpha"),
    FeatureLifecycle("wallpaper_engine", "0.8.0", "Beta"),
    FeatureLifecycle("desktop_designs", "0.5.0", "Alpha"),
    FeatureLifecycle("settings", "1.0.0", "Stabil"),
    FeatureLifecycle("about", "1.0.0", "Stabil"),
    FeatureLifecycle("log", "0.9.0", "Beta"),
)
_BY_KEY = {feature.key: feature for feature in _FEATURES}
_ALIASES = {
    "rgb": "rgb_studio",
    "snapshots": "snapshot_manager",
    "automation": "automations",
    "wallpaper": "wallpaper_engine",
}


def feature_lifecycles() -> tuple[FeatureLifecycle, ...]:
    return _FEATURES


def feature_lifecycle(key: str) -> FeatureLifecycle | None:
    return _BY_KEY.get(_ALIASES.get(key, key))
