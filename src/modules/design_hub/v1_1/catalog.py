# SPDX-License-Identifier: GPL-3.0-or-later
"""Stable visual pairs and backward-compatible section placement."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DesignPair:
    ident: str
    title: str
    rgb_title: str
    lcd_id: str
    description: str
    media_file: str = ""
    poster_file: str = ""


PAIRS = (
    DesignPair("matrix", "Matrix Code Rain", "Matrix Code Rain", "ohc-code-rain",
               "Grüne Datenspuren auf den Lüftern und fließender Code-Regen auf dem Display."),
    DesignPair("prism", "Prism Drift", "Prism Drift", "ohc-prism-drift",
               "Violette und türkise Lichtbewegung mit einem ruhigen Prismenhintergrund."),
    DesignPair("wyrm", "Twin Wyrm Orbit", "Twin Wyrm Orbit", "ohc-twin-wyrm",
               "Warme und kühle Lichtkörper für Lüfter und Display."),
    DesignPair("garden", "Neon Particle Garden", "Neon Particle Garden", "ohc-neon-garden",
               "Sanfte Neonpartikel und funkelnde Akzente im Gehäuse."),
    DesignPair("circuit", "Circuit Chase", "Circuit Chase", "ohc-circuit-chase",
               "Türkise und pinke Energiespuren auf LEDs und Leiterbahnen."),
    DesignPair("bands", "Amber Light Bands", "Amber Light Bands", "ohc-light-bands",
               "Warme Lichtbänder und weiche bernsteinfarbene Wellen im Gehäuse."),
    DesignPair("aurora", "Aurora Silk", "Aurora Silk", "",
               "Seidige Polarlichtwellen in Grün und Violett für Lüfter und Display.",
               "app-backgrounds/aurora-silk.mp4", "app-backgrounds/aurora-silk.jpg"),
    DesignPair("nebula", "Nebula Depth", "Nebula Depth", "",
               "Violetter Sternennebel und langsam pulsierendes Licht im Gehäuse.",
               "app-backgrounds/nebula-depth.mp4", "app-backgrounds/nebula-depth.jpg"),
    DesignPair("liquid", "Liquid Prism", "Liquid Prism", "",
               "Fließende Prismenreflexe und kühle silberblaue Lichtwellen.",
               "app-backgrounds/liquid-prism.mp4", "app-backgrounds/liquid-prism.jpg"),
    DesignPair("ocean", "Ocean Caustics", "Ocean Caustics", "",
               "Türkise Wasserreflexe und ruhige blaue Wellen für das ganze Gehäuse.",
               "app-backgrounds/ocean-caustics.mp4", "app-backgrounds/ocean-caustics.jpg"),
    DesignPair("solar", "Solar Orbit", "Solar Orbit", "",
               "Ein warmer Sonnenorbit mit goldenen Lichtspuren auf den Lüftern.",
               "app-backgrounds/solar-orbit.mp4", "app-backgrounds/solar-orbit.jpg"),
    DesignPair("orbital", "Orbital Halo", "Orbital Halo", "",
               "Ein räumlicher Lichtring und umlaufende türkise Akzente im Gehäuse.",
               "levita-designs/ohc-3d-orbital-ring-10s.mp4", "design-hub/orbital.jpg"),
    DesignPair("apex", "Neon Apex", "Neon Apex", "",
               "Violette Neonflächen und gegenläufige türkise Lichtbahnen.",
               "levita-designs/ohc-3d-neon-apex-10s.mp4", "design-hub/apex.jpg"),
    DesignPair("quantum", "Quantum Core", "Quantum Core", "",
               "Ein leuchtender Quantenkern mit zusammenlaufenden blauen Lichtimpulsen.",
               "levita-designs/ohc-3d-quantum-core-10s.mp4", "design-hub/quantum.jpg"),
    DesignPair("voyage", "Quantum Voyage", "Quantum Voyage", "",
               "Eine violette Cyberreise mit wandernden Lichtkometen auf den Lüftern.",
               "levita-designs/ohc-ai-quantum-voyage-30s.mp4", "design-hub/voyage.jpg"),
)

ASSET_ROOT = Path(__file__).resolve().parents[3] / "assets"
MATRIX_SIZES = ((100, "original"), (130, "large-30"), (150, "large-50"), (200, "large-100"))


def pair_variant(pair, variant_id=None):
    from modules.display_effects.v1_11.catalog import DESIGNS
    if not pair.lcd_id:
        if variant_id: raise ValueError("design has no alternate media")
        return None
    design = next(design for design in DESIGNS if design.ident == pair.lcd_id)
    ident = variant_id or design.variants[0].ident
    return next(variant for variant in design.variants if variant.ident == ident)


def pair_media(pair, variant_id=None):
    """Only fixed, original bundled media may enter the paired-design path."""
    if pair not in PAIRS: raise ValueError("unknown paired design")
    variant = pair_variant(pair, variant_id)
    if variant is not None:
        from modules.display_effects.v1_11.catalog import validated_asset
        return validated_asset(variant)
    if variant_id: raise ValueError("design has no alternate media")
    candidate = ASSET_ROOT / pair.media_file
    return _fixed_asset(candidate, ".mp4")


def pair_poster(pair, variant_id=None):
    if pair not in PAIRS: raise ValueError("unknown paired design")
    variant = pair_variant(pair, variant_id)
    if variant is not None:
        from modules.display_effects.v1_11.catalog import validated_asset
        return validated_asset(variant, preview=True)
    return _fixed_asset(ASSET_ROOT / pair.poster_file, ".jpg")


def _fixed_asset(candidate, suffix):
    resolved = candidate.resolve()
    resolved.relative_to(ASSET_ROOT.resolve())
    if candidate.is_symlink() or not resolved.is_file() or resolved.suffix.lower() != suffix:
        raise ValueError("invalid bundled paired-design asset")
    return resolved


def validate_pair_media(path):
    """Exact catalog membership, not permission for an entire asset folder."""
    candidate = Path(path)
    if candidate.is_symlink(): raise ValueError("symlink design media")
    resolved = candidate.resolve()
    for pair in PAIRS:
        if pair.lcd_id:
            from modules.display_effects.v1_11.catalog import DESIGNS
            design = next(design for design in DESIGNS if design.ident == pair.lcd_id)
            variants = [variant.ident for variant in design.variants]
        else:
            variants = [None]
        if any(resolved == pair_media(pair, variant) for variant in variants): return resolved
    raise ValueError("media is not a paired-design catalog asset")


def normalize_order(order):
    """Insert the new section beside RGB without replacing personal ordering."""
    result = list(dict.fromkeys(order))
    if "design_hub" not in result:
        result.insert(result.index("rgb_studio") + 1 if "rgb_studio" in result else len(result),
                      "design_hub")
    return result
