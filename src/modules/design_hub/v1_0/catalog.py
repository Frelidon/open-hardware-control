# SPDX-License-Identifier: GPL-3.0-or-later
"""Stable visual pairs and backward-compatible section placement."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DesignPair:
    ident: str
    title: str
    rgb_title: str
    lcd_id: str
    description: str


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
)


def normalize_order(order):
    """Insert the new section beside RGB without replacing personal ordering."""
    result = list(dict.fromkeys(order))
    if "design_hub" not in result:
        result.insert(result.index("rgb_studio") + 1 if "rgb_studio" in result else len(result),
                      "design_hub")
    return result
