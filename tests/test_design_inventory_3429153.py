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
    "ohc-light-bands-down-left.jpg": "0a43a18e97929629c59b82759636ccf45509cae05749a98b503d2dd269590001",
    "ohc-light-bands-down-left.mp4": "846e6fef49259016f7437a9109f5adaf782658ef08f66af94ba72fd0c6c0b017",
    "ohc-light-bands-down-right.jpg": "bc697006e22a4e09670381cd82613408ba191f14bb982f28e8784247083cc782",
    "ohc-light-bands-down-right.mp4": "a9fb0481e54920321e2e3b80b1d5d2062cd777deb9bff6cee1d685fcc70127b8",
    "ohc-light-bands-down.jpg": "09af9f4e6c7d66ecb1f195931a2ebfab84f9f4be110d5954b680176b6d85514d",
    "ohc-light-bands-down.mp4": "e0dcbb9554adf41fb8c96bb65a1735ff6ef3b23ba62d4755006e1d16fd0f7946",
    "ohc-light-bands-left.jpg": "9544e46f756bf2ae07162af5dca2cd9a8bd50375c6b51d5855ef7779ec30a27a",
    "ohc-light-bands-left.mp4": "196ec57c1ea10243b6367115762d74efdd2d9777bf496712bb0c69ae1aec63fb",
    "ohc-light-bands-right.jpg": "cbdbed569e49a45c54377fe5dc5c84a3649e57d01b40f41a0f7238b062b3ecba",
    "ohc-light-bands-right.mp4": "1c233f19ea7e5b5f48e30cf19cbed61abba36aa2c34ee40ae2de8fda6e498100",
    "ohc-light-bands-up-left.jpg": "468d26bb8dbf6e7b52ad8ff6c4e1585674c0f4963d2fb7b737ee01067cb38518",
    "ohc-light-bands-up-left.mp4": "5469d81cc777d89c901893db79a4659b096b81870a687caf20adb2955d373c46",
    "ohc-light-bands-up-right.jpg": "011c8ead2fe4d3245b25526abb593369f909b5ba093f8586327ebb1f304b817a",
    "ohc-light-bands-up-right.mp4": "0324a795ee200e809db68f189f7acc090fbdf992c534abb5ca1e73100c22eda9",
    "ohc-light-bands-up.jpg": "931a051f3f2b05703db9a3010a06c8bae13d094cc10445aadf7322e16578327b",
    "ohc-light-bands-up.mp4": "9cee81380bae9fff05deb217484019b852ac95c006ca146515c1048a92137c78",
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
    "ohc-light-bands", "ohc-prism-drift", "ohc-twin-wyrm", "ohc-neon-garden", "ohc-circuit-chase",
}


def test_original_media_are_unchanged_and_registered_with_their_stable_ids():
    originals = designs_for_category("ohc_original")
    assert {design.ident for design in originals} == ORIGINAL_IDS
    registered = set()
    for design in originals:
        assert design.creator == "Frelidon / Open Hardware Control"
        assert design.license_name == "GPL-3.0-or-later"
        assert design.variants
        for variant in design.variants:
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
            assert UI_TRANSLATIONS[code][design.title]
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
        for variant in design.variants:
            assert library.select_video(validated_asset(variant))
            assert library.current_design().ident == design.ident
            assert library.current_variant().ident == variant.ident
    library.deleteLater()
    app.processEvents()
