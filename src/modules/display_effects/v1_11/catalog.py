#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Auditable bundled-media catalog for Levita display effects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ASSET_ROOT = Path(__file__).resolve().parents[3] / "assets" / "display-effects"

CATEGORY_LABELS: tuple[tuple[str, str], ...] = (
    ("all", "Alle Kategorien"),
    ("abstract", "Abstrakt"),
    ("space", "Weltall & Erde"),
    ("landscape", "Landschaft & Himmel"),
    ("water", "Wasser & Unterwasser"),
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


def _variants(stem: str) -> tuple[EffectVariant, ...]:
    return (
        EffectVariant("original", "Original", f"{stem}-original.mp4"),
        EffectVariant("ice", "Eisblau · Designvariante", f"{stem}-ice.mp4"),
        EffectVariant("plasma", "Plasma-Violett", f"{stem}-plasma.mp4"),
        EffectVariant("ember", "Glut-Orange", f"{stem}-ember.mp4"),
    )


def _single_variant(stem: str) -> tuple[EffectVariant, ...]:
    return (EffectVariant("original", "Original", f"{stem}-original.mp4"),)


DESIGNS: tuple[EffectDesign, ...] = (
    EffectDesign(
        "smoke-seamless", "abstract", "Lichtnebel",
        "Heller, weich fließender Rauch auf tiefschwarzem Hintergrund.",
        "Norberto Navarro Valiente (doktorkleinmusic)",
        "https://pixabay.com/users/doktorkleinmusic-5871510/",
        "https://pixabay.com/videos/smoke-abstract-black-background-337943/",
        "Pixabay Content License", "https://pixabay.com/service/license-summary/",
        _variants("smoke-seamless"),
    ),
    EffectDesign(
        "dark-smoke", "abstract", "Tiefenrauch",
        "Organischer dunkler Rauch mit viel freier Fläche für Sensordaten.",
        "TH-DARK Media", "https://www.pexels.com/video/smoke-16488810/",
        "https://www.pexels.com/video/smoke-16488810/",
        "Pexels License", "https://www.pexels.com/license/",
        _variants("dark-smoke"),
    ),
    EffectDesign(
        "dark-fog", "abstract", "Partikelnebel",
        "Dunkler Nebel mit feiner Körnung und zurückhaltenden Lichtpartikeln.",
        "ForYouMuchMoreSpecial",
        "https://pixabay.com/users/foryoumuchmorespecial-15308418/",
        "https://pixabay.com/videos/abstract-smoke-fog-gray-dark-250440/",
        "Pixabay Content License", "https://pixabay.com/service/license-summary/",
        _variants("dark-fog"),
    ),
    EffectDesign(
        "fluid-waves", "abstract", "Flüssiges Licht",
        "Fließende abstrakte Wellen mit warmen und kühlen Lichtakzenten.",
        "Colin Jones",
        "https://www.pexels.com/video/abstract-smoke-animation-on-a-black-background-27607570/",
        "https://www.pexels.com/video/abstract-smoke-animation-on-a-black-background-27607570/",
        "Pexels License", "https://www.pexels.com/license/",
        _variants("fluid-waves"),
    ),
    EffectDesign(
        "digital-wave", "abstract", "Digitale Partikelwelle",
        "Futuristische Partikelwelle für einen klaren technischen Display-Look.",
        "WhiteHatDesigner",
        "https://pixabay.com/users/whitehatdesigner-25779762/",
        "https://pixabay.com/videos/digital-wave-abstract-particles-309178/",
        "Pixabay Content License", "https://pixabay.com/service/license-summary/",
        _variants("digital-wave"),
    ),
    EffectDesign(
        "ohc-light-bands", "abstract", "OHC Lichtbänder",
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
        "earth-360", "space", "Erde · 360°",
        "Langsame Erdrotation mit klarer Tag-Nacht-Grenze.",
        "Wikideas1", "https://commons.wikimedia.org/wiki/User:Wikideas1",
        "https://commons.wikimedia.org/wiki/File:Earth_360_animation.webm",
        "CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/",
        _single_variant("space-earth-360"),
    ),
    EffectDesign(
        "orion-nebula", "space", "Orionnebel",
        "Ruhige Kamerafahrt durch eine detailreiche Aufnahme des Orionnebels.",
        "ESO · Musik der stummen Quelle: Johan B. Monell", "https://www.eso.org/",
        "https://commons.wikimedia.org/wiki/File:Panning_across_the_Orion_Nebula.webm",
        "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/",
        _single_variant("space-orion-nebula"),
    ),
    EffectDesign(
        "galaxy-megamerger", "space", "Uralte Galaxien",
        "Leuchtende ferne Galaxien vor einem tiefschwarzen Weltraumhintergrund.",
        "ESO/M. Kornmesser", "https://www.eso.org/",
        "https://commons.wikimedia.org/wiki/File:Artist%E2%80%99s_impression_of_ancient_galaxy_megamerger_(video).webm",
        "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/",
        _single_variant("space-galaxy-megamerger"),
    ),
    EffectDesign(
        "ngc300", "space", "NGC 300",
        "Sanfte Aufnahmefahrt über die südliche Spiralgalaxie NGC 300.",
        "ESO/Digitized Sky Survey 2", "https://www.eso.org/",
        "https://commons.wikimedia.org/wiki/File:Panning_across_the_southern_spiral_NGC_300_(ESO_1037a).webm",
        "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/",
        _single_variant("space-ngc300-pan"),
    ),
    EffectDesign(
        "milky-way-observatory", "space", "Milchstraßennacht",
        "Sternenhimmel und Milchstraße über der menschenleeren Berglandschaft.",
        "Astrobond", "https://commons.wikimedia.org/wiki/User:Astrobond",
        "https://commons.wikimedia.org/wiki/File:A_timelapse_of_the_Milky_Way%27s_movement_against_the_backdrop_of_the_Assy-Turgen_Observatory_at_an_altitude_of_2,750_m._Kazakhstan.webm",
        "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
        _single_variant("space-milkyway-observatory"),
    ),
    EffectDesign(
        "clouds", "landscape", "Wolkenmeer",
        "Weiche Wolkenbewegung in einem weiten blauen Himmel.",
        "John Fowler", "https://www.flickr.com/photos/snowpeak/",
        "https://commons.wikimedia.org/wiki/File:Cloud_timelapse.webm",
        "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/",
        _single_variant("landscape-clouds"),
    ),
    EffectDesign(
        "aurora", "landscape", "Nordlicht",
        "Grüne Nordlichter über einer dunklen, menschenleeren Winterlandschaft.",
        "Harriniva Hotels & Safaris", "https://commons.wikimedia.org/wiki/File:Aurora_borealis_timelapse.webm",
        "https://commons.wikimedia.org/wiki/File:Aurora_borealis_timelapse.webm",
        "CC BY 3.0", "https://creativecommons.org/licenses/by/3.0/",
        _single_variant("landscape-aurora"),
    ),
    EffectDesign(
        "steens-mountain", "landscape", "Steens Mountain · Wolkenflug",
        "Schnell ziehende Wolken über einer weiten Berglandschaft.",
        "BLM Oregon & Washington", "https://www.flickr.com/people/blmoregon/",
        "https://commons.wikimedia.org/wiki/File:Time_Lapse_Clouds_above_Steens_Mountain_(36203941112).webm",
        "Public Domain", "https://creativecommons.org/publicdomain/mark/1.0/",
        _single_variant("landscape-steens-mountain"),
    ),
    EffectDesign(
        "tokyo-sunset", "landscape", "Tokio · Sonnenuntergang",
        "Warmer Sonnenuntergang über der Silhouette der Stadt.",
        "Nesnad", "https://commons.wikimedia.org/wiki/User:Nesnad",
        "https://commons.wikimedia.org/wiki/File:Sunset_tokyoarea-timelapse-2019-03-17.webm",
        "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
        _single_variant("landscape-tokyo-sunset"),
    ),
    EffectDesign(
        "lake-garda", "landscape", "Gardasee · Abendglühen",
        "Goldene Wolken und Bergsilhouetten am Gardasee ohne Texteinblendung.",
        "93galas", "https://www.youtube.com/user/93galas",
        "https://commons.wikimedia.org/wiki/File:Time_Lapse_Sunset_4K_4096x2304.webm",
        "CC BY 3.0", "https://creativecommons.org/licenses/by/3.0/",
        _single_variant("landscape-lake-garda-sunset"),
    ),
    EffectDesign(
        "ocean-waves", "water", "Atlantikwellen",
        "Ruhige Atlantikwellen an der Küste von Saint-Malo.",
        "Matti Schneider", "https://commons.wikimedia.org/wiki/User:Matti_Schneider",
        "https://commons.wikimedia.org/wiki/File:Ocean_waves.webm",
        "CC BY-SA 3.0", "https://creativecommons.org/licenses/by-sa/3.0/",
        _single_variant("water-ocean-waves"),
    ),
    EffectDesign(
        "waterfall", "water", "Waldwasserfall",
        "Kleiner Wasserfall zwischen Felsen und sattem Grün.",
        "Editor", "https://www.youtube.com/user/Editor",
        "https://commons.wikimedia.org/wiki/File:Small_waterfall.webm",
        "CC BY 3.0", "https://creativecommons.org/licenses/by/3.0/",
        _single_variant("water-waterfall"),
    ),
    EffectDesign(
        "jellyfish", "water", "Blaue Qualle",
        "Schwebende Qualle in tiefblauem Wasser.",
        "FASTILY", "https://commons.wikimedia.org/wiki/User:Fastily",
        "https://commons.wikimedia.org/wiki/File:Jellyfish_at_Monterey_Bay_Aquarium_2_2017-11-21.webm",
        "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
        _single_variant("water-jellyfish"),
    ),
    EffectDesign(
        "san-juan-waves", "water", "San-Juan-Brandung",
        "Brechende Wellen zwischen dunklen Felsen und Treibholz.",
        "BLM Oregon & Washington", "https://www.flickr.com/people/blmoregon/",
        "https://commons.wikimedia.org/wiki/File:Crashing_waves_in_the_San_Juan_Islands_(40007700135).webm",
        "Public Domain", "https://creativecommons.org/publicdomain/mark/1.0/",
        _single_variant("water-san-juan-waves"),
    ),
    EffectDesign(
        "red-sea-reef", "water", "Rotes Meer · Korallenriff",
        "Fische ziehen durch ein farbiges Korallenriff im Roten Meer.",
        "Kora27", "https://commons.wikimedia.org/wiki/User:Kora27",
        "https://commons.wikimedia.org/wiki/File:Unterwasserwelt,_Korallenriff_im_Roten_Meer_DSCF1654.webm",
        "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
        _single_variant("water-red-sea-reef"),
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
