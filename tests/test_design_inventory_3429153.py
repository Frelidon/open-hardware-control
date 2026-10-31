#!/usr/bin/env python3
"""Keep the .148 project-owned LCD media and their gallery choices available."""

from pathlib import Path
import hashlib
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from PySide6.QtWidgets import QApplication  # noqa: E402
from localization_catalog import UI_TRANSLATIONS  # noqa: E402
from modules.display_effects.v1_11.catalog import designs_for_category, validated_asset  # noqa: E402
from modules.display_effects.v1_11.library import StockEffectsLibrary  # noqa: E402


# Hashes from the verified .148 source release. Intentional rerendering
# must update this preservation baseline explicitly, never silently drop it.
ORIGINAL_MEDIA_SHA256 = {
    "ohc-prism-drift-original.jpg": "6850e7f016515f4834ac82dd06cce21978f34a73a36c592b0a6c43fb37e3e027",
    "ohc-prism-drift-original.mp4": "a3e4bb9ef5b0af68e158ba1cde67716c34157b22138b150003eda148775f6212",
    "ohc-twin-wyrm-original.jpg": "e6d58c1c52d7ef0b063077104f065a43c48c019a203517b825ffa287c66577b9",
    "ohc-twin-wyrm-original.mp4": "ca49cd04cec9e2bc9ce712edc4e1e49764af4873931e952a8db7abe2f735d8db",
    "ohc-neon-garden-original.jpg": "b9b378e8129e1a8200a1d50c38d252d64b6c1678b0da10b6f5837393ebb140bc",
    "ohc-neon-garden-original.mp4": "a60a3bb35a612890a54e32533b23724fd98733269ff531a094983abb8ba24dc2",
    "ohc-circuit-chase-original.jpg": "c9d232f61f2e1f3dd9a0b2bec377ae03ab27d042cad0da0f19c0982ac612bde7",
    "ohc-circuit-chase-original.mp4": "87e5b8fd06e9e80b19bdf0cd41a6deaa80be8613fed9cfdedeefb33be24de12d",
}
ORIGINAL_IDS = {
    "ohc-prism-drift", "ohc-twin-wyrm", "ohc-neon-garden", "ohc-circuit-chase",
}


def test_original_media_are_unchanged_and_registered_with_their_stable_ids():
    originals = designs_for_category("ohc_original")
    assert {design.ident for design in originals} == ORIGINAL_IDS
    registered = set()
    for design in originals:
        assert design.creator == "Frelidon / Open Hardware Control"
        assert design.license_name == "GPL-3.0-or-later"
        assert len(design.variants) == 1
        variant = design.variants[0]
        assert variant.ident == "original"
        for preview in (False, True):
            asset = validated_asset(variant, preview=preview)
            registered.add(asset.name)
            assert hashlib.sha256(asset.read_bytes()).hexdigest() == ORIGINAL_MEDIA_SHA256[asset.name]
    assert registered == set(ORIGINAL_MEDIA_SHA256)


def test_original_gallery_category_and_descriptions_have_four_language_data():
    sources = {"OHC Originale"} | {
        design.description for design in designs_for_category("ohc_original")
    }
    for code in ("de", "en", "es", "fr"):
        assert sources <= UI_TRANSLATIONS[code].keys()
        for design in designs_for_category("ohc_original"):
            assert UI_TRANSLATIONS[code][design.title] == design.title
        if code != "de":
            assert all(UI_TRANSLATIONS[code][source] != source for source in sources)


def test_original_gallery_cards_are_visible_and_exact_saved_videos_are_selectable():
    app = QApplication.instance() or QApplication([])
    library = StockEffectsLibrary(lambda source: source)
    category = library.category_combo.findData("ohc_original")
    assert category >= 0
    library.category_combo.setCurrentIndex(category)
    assert set(library._design_cards) == ORIGINAL_IDS
    assert all(not card.icon().isNull() for card in library._design_cards.values())
    for design in designs_for_category("ohc_original"):
        assert library.select_video(validated_asset(design.variants[0]))
        assert library.current_design().ident == design.ident
        assert library.current_variant().ident == "original"
    library.deleteLater()
    app.processEvents()
