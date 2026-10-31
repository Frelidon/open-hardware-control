# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure platform-aware catalog for first-run feature selection."""

from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Iterable


@dataclass(frozen=True, slots=True)
class FeatureChoice:
    key: str
    title: str
    description: str
    icon: str
    available: bool
    default_enabled: bool
    availability: str
    navigation_keys: tuple[str, ...]


def feature_choices(platform: str | None = None) -> tuple[FeatureChoice, ...]:
    target = (platform or sys.platform).casefold()
    windows = target.startswith("win")
    linux = target.startswith("linux")

    def item(key: str, title: str, description: str, icon: str,
             available: bool, navigation: tuple[str, ...], *, default: bool = True,
             note: str = "Verfügbar") -> FeatureChoice:
        return FeatureChoice(
            key, title, description, icon, available, bool(default and available),
            note if available else "Auf diesem System nicht verfügbar", navigation,
        )

    return (
        item("cooling", "Kühlung & Lüfter", "Überwacht Temperaturen und steuert nur geprüfte Kühlgeräte und bestätigte Lüfterkanäle.", "❄", linux, ("cooling",), note="Unter Linux verfügbar"),
        item("rgb", "RGB-Steuerung", "Steuert Lüfter, LED-Streifen, RAM und weitere erkannte Beleuchtung über einen eindeutig gewählten Besitzer.", "◉", linux or windows, ("rgb_studio",)),
        item("lcd", "LCD & Displayeffekte", "Verwaltet Bilder, Videos, Live-Werte und zeitgesteuerte Designs für unterstützte Hardware-Displays.", "▣", linux or windows, ("lcd", "display_effects")),
        item("gpu", "Grafikkarte", "Zeigt GPU-Messwerte; sichere Lüfter- und Leistungsfunktionen erscheinen nur mit geprüftem Backend.", "◆", linux or windows, ("gpu",)),
        item("case", "Gehäuseansicht", "Ordnet Lüfter, LED-Ringe, Streifen und Komponenten räumlich an und zeigt den Effektverlauf.", "▥", linux or windows, ("case",)),
        item("hardware_checker", "Hardware-Checker", "Stellt CPU, Mainboard, Sockel, GPU, NVMe und RAM in einer lesbaren Übersicht zusammen.", "✓", linux or windows, ("hardware_checker",)),
        item("snapshots", "Snapshot-Manager", "Verwaltet unter Linux Snapper/Btrfs-Snapshots mit enger Polkit-Freigabe und Spielschutz.", "◫", linux, ("snapshot_manager",), note="Linux · Snapper/Btrfs"),
        item("automation", "Automationen & Profile", "Wechselt Gesamtprofile nach Zeit oder beim Start eines Spiels beziehungsweise Programms.", "⌁", linux or windows, ("automations", "profiles")),
        item("wallpaper", "Wallpaper Engine", "Steuert vorhandene Wallpaper-Engine-Inhalte über den passenden KDE- oder Windows-Adapter.", "▧", linux or windows, ("wallpaper_engine",)),
    )


def normalize_selection(values: Iterable[object] | None, *, platform: str | None = None) -> tuple[str, ...]:
    catalog = feature_choices(platform)
    available = {item.key for item in catalog if item.available}
    if values is None:
        return tuple(item.key for item in catalog if item.default_enabled)
    chosen = {str(value) for value in values}
    # Builds .149-.152 wrote sidebar IDs into this setting. Accept those IDs
    # without re-enabling a genuinely disabled canonical feature selection.
    navigation_aliases = {
        nav_key: item.key for item in catalog for nav_key in item.navigation_keys
        if nav_key != item.key
    }
    if chosen.intersection(navigation_aliases):
        chosen = {navigation_aliases.get(key, key) for key in chosen}
    return tuple(item.key for item in catalog if item.key in chosen and item.key in available)
