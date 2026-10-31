#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure localization coverage policy and bounded dynamic caption handling."""

from __future__ import annotations

import re

_TECHNICAL_UI_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"^[#][0-9a-f]{6}$", r"^[0-9]+(?:[.,][0-9]+)?\s*(?:%|fps|hz|°|px)$",
    r"^AMD Ryzen ", r"^(?:CPU|Pump|System) Fan .*(?:pwm|rpm)", r"\bpwm[0-9]+\b",
    r"^(?:AMD|NVIDIA) · (?:Radeon|GeForce) [A-Z0-9 ]+ · (?:Radeon|GeForce) [A-Z0-9 ]+$",
    r"\brpm\b", r"^(?:led[0-9]+|sync)$", r"^v?[0-9]+(?:\.[0-9]+){2,}",
))

UNCHANGED_UI_NAMES = frozenset({
    "#RRGGBB", "Abyssal Bloom", "Firefly Grove", "Magma Heart", "Nebula Vanguard", "Neon Rain",
    "Polar Aurora", "Ringworld Runner", "Singularity Dive", "Open Hardware Control",
    "Open Hardware Control by Frelidon", "OpenLinkHub", "OpenRGB", "Wallpaper Engine", "KDE Plasma",
    "NZXT Kraken über liquidctl", "Thermalright Levita Vision 360 ARGB Black", "OHC Metro 8",
    "OHC Metro Cursor", "OHC Orchard", "OHC Orchard Cursor", "OHC Windowed 11", "OHC Windowed Cursor",
    "CPU", "GPU", "RGB", "LCD", "Python", "PySide6", "Qt", "Pillow", "Web", "Live", "Normal",
    "Position", "X", "Y",
})


def interactive_text_needs_translation(source: str) -> bool:
    """Return whether an interactive caption must exist in every catalog."""
    text = str(source).strip()
    if not text or text in UNCHANGED_UI_NAMES or not any(character.isalpha() for character in text):
        return False
    if re.fullmatch(r"(?:Alle Hintergründe|Eigene Dateien|OHC-Designs) · [0-9]+", text):
        return False
    if re.fullmatch(r"(?:Galerie|Technik|HUD|Licht|Natur|Ästhetik|Gallery|Tech|Light|Nature|Aesthetic) · [0-9]+", text):
        return False
    if re.fullmatch(r"(?:★ )?.+\n(?:Bild|Video|Live-Layout)", text):
        return False
    return not any(pattern.search(text) for pattern in _TECHNICAL_UI_PATTERNS)


def translated_control_text(source: str, translations: dict[str, str]) -> str:
    """Translate exact captions plus bounded dynamic card/count/colour variants."""
    text = str(source)
    if text in translations:
        return translations[text]
    # Navigation entries keep their symbolic icon (and, while the navigation
    # editor is open, the drag handle) outside the canonical message.  Resolve
    # the ordinary caption and then put that decoration back unchanged.
    decorated = re.fullmatch(r"([^\w]*)(.+)", text, re.DOTALL)
    if decorated and decorated.group(2) in translations:
        return f"{decorated.group(1)}{translations[decorated.group(2)]}"
    # QLabel stores links and small two-line statistic cards as rich text.
    # Translate only the human-readable label while preserving the validated
    # URL, markup and measured value verbatim.
    link = re.fullmatch(r'(<a href="[^"]+">)([^<>]+)(</a>)', text)
    if link and link.group(2) in translations:
        return f"{link.group(1)}{translations[link.group(2)]}{link.group(3)}"
    bold = re.fullmatch(r"(<b>)([^<>]+)(</b>)", text)
    if bold and bold.group(2) in translations:
        return f"{bold.group(1)}{translations[bold.group(2)]}{bold.group(3)}"
    statistic = re.fullmatch(
        r"(<b>.*?</b><br><span style='color:#[0-9a-fA-F]{6}'>)([^<>]+)(</span>)",
        text,
        re.DOTALL,
    )
    if statistic and statistic.group(2) in translations:
        return f"{statistic.group(1)}{translations[statistic.group(2)]}{statistic.group(3)}"
    card = re.fullmatch(r"((?:★ )?.+)\n(Bild|Video|Live-Layout)", text)
    if card:
        return f"{card.group(1)}\n{translations.get(card.group(2), card.group(2))}"
    count = re.fullmatch(r"(Alle Hintergründe|Eigene Dateien|OHC-Designs) · ([0-9]+)", text)
    if count:
        return f"{translations.get(count.group(1), count.group(1))} · {count.group(2)}"
    colour = re.fullmatch(r"(🎨 )?(Hauptfarbe ändern|Zweitfarbe ändern|Testfarbe) · (#[0-9a-fA-F]{6})", text)
    if colour:
        return f"{colour.group(1) or ''}{translations.get(colour.group(2), colour.group(2))} · {colour.group(3)}"
    return text
