#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Auditable bundled-media catalog for Levita display effects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ASSET_ROOT = Path(__file__).resolve().parents[3] / "assets" / "display-effects"

CATEGORY_LABELS: tuple[tuple[str, str], ...] = (
    ("all", "Alle Kategorien"),
    ("ohc_original", "OHC Originale"),
)


@dataclass(frozen=True)
class EffectVariant:
    ident: str
    label: str
    filename: str

    @property
    def video_path(self) -> Path:
        return ASSET_ROOT / self.filename

    @property
    def preview_path(self) -> Path:
        return self.video_path.with_suffix(".jpg")


@dataclass(frozen=True)
class EffectDesign:
    ident: str
    category: str
    title: str
    description: str
    creator: str
    creator_url: str
    source_url: str
    license_name: str
    license_url: str
    variants: tuple[EffectVariant, ...]


def _single_variant(stem: str) -> tuple[EffectVariant, ...]:
    return (EffectVariant("original", "Original", f"{stem}-original.mp4"),)


DESIGNS: tuple[EffectDesign, ...] = (
    EffectDesign(
        "ohc-light-bands", "ohc_original", "OHC Lichtbänder",
        "Eigene nahtlose Lichtstäbe mit einer warmen wandernden Helligkeitswelle.",
        "Frelidon / Open Hardware Control",
        "https://github.com/Frelidon/open-hardware-control",
        "https://github.com/Frelidon/open-hardware-control",
        "GPL-3.0-or-later", "https://www.gnu.org/licenses/gpl-3.0.html",
        tuple(
            EffectVariant(direction, label, f"ohc-light-bands-{direction}.mp4")
            for direction, label in (
                ("right", "Nach rechts"), ("left", "Nach links"),
                ("down", "Nach unten"), ("up", "Nach oben"),
                ("down-right", "Links oben → rechts unten"),
                ("up-left", "Rechts unten → links oben"),
                ("down-left", "Rechts oben → links unten"),
                ("up-right", "Links unten → rechts oben"),
            )
        ),
    ),
    EffectDesign(
        "ohc-prism-drift", "ohc_original", "Prism Drift",
        "Eigenständige, langsam driftende Prismengitter mit viel ruhiger Fläche für Sensordaten.",
        "Frelidon / Open Hardware Control", "https://github.com/Frelidon/open-hardware-control",
        "https://github.com/Frelidon/open-hardware-control", "GPL-3.0-or-later",
        "https://www.gnu.org/licenses/gpl-3.0.html", _single_variant("ohc-prism-drift"),
    ),
    EffectDesign(
        "ohc-twin-wyrm", "ohc_original", "Twin Wyrm Orbit",
        "Zwei abstrakte Lichtwesen kreisen gegenläufig um einen freien Datenkern – ohne Markenmotiv.",
        "Frelidon / Open Hardware Control", "https://github.com/Frelidon/open-hardware-control",
        "https://github.com/Frelidon/open-hardware-control", "GPL-3.0-or-later",
        "https://www.gnu.org/licenses/gpl-3.0.html", _single_variant("ohc-twin-wyrm"),
    ),
    EffectDesign(
        "ohc-neon-garden", "ohc_original", "Neon Particle Garden",
        "Organische Neonpartikel wachsen, schweben und verlöschen in einem nahtlosen Zyklus.",
        "Frelidon / Open Hardware Control", "https://github.com/Frelidon/open-hardware-control",
        "https://github.com/Frelidon/open-hardware-control", "GPL-3.0-or-later",
        "https://www.gnu.org/licenses/gpl-3.0.html", _single_variant("ohc-neon-garden"),
    ),
    EffectDesign(
        "ohc-circuit-chase", "ohc_original", "Circuit Chase",
        "Ein eigener Energie-Kurier jagt durch ein verzweigtes Leiterbahn-Labyrinth; keine Figur oder Grafik eines Spiels wird verwendet.",
        "Frelidon / Open Hardware Control", "https://github.com/Frelidon/open-hardware-control",
        "https://github.com/Frelidon/open-hardware-control", "GPL-3.0-or-later",
        "https://www.gnu.org/licenses/gpl-3.0.html", _single_variant("ohc-circuit-chase"),
    ),
    EffectDesign(
        "ohc-code-rain", "ohc_original", "Matrix Code Rain",
        "Grüner Code-Regen mit sanften Lichtspuren und Platz für die vorhandene Datenebene.",
        "Frelidon / Open Hardware Control", "https://github.com/Frelidon/open-hardware-control",
        "https://github.com/Frelidon/open-hardware-control", "GPL-3.0-or-later",
        "https://www.gnu.org/licenses/gpl-3.0.html", (
            EffectVariant("large-30", "Zeichen +30 % · Standard", "ohc-code-rain-large-30.mp4"),
            EffectVariant("large-50", "Zeichen +50 %", "ohc-code-rain-large-50.mp4"),
            EffectVariant("large-100", "Zeichen +100 %", "ohc-code-rain-large-100.mp4"),
            EffectVariant("original", "Original", "ohc-code-rain-original.mp4"),
        ),
    ),
)


def designs_for_category(category: str) -> tuple[EffectDesign, ...]:
    """Return the stable catalog subset for one UI category."""

    key = str(category or "all")
    return DESIGNS if key == "all" else tuple(design for design in DESIGNS if design.category == key)


def validated_asset(variant: EffectVariant, *, preview: bool = False) -> Path:
    """Return a regular bundled asset while rejecting path/symlink surprises."""

    root = ASSET_ROOT.resolve()
    candidate = variant.preview_path if preview else variant.video_path
    resolved = candidate.resolve()
    resolved.relative_to(root)
    expected_suffix = ".jpg" if preview else ".mp4"
    if candidate.is_symlink() or not resolved.is_file() or resolved.suffix.casefold() != expected_suffix:
        raise ValueError(f"invalid bundled display-effect asset: {candidate.name}")
    return resolved
