"""Reclassify OHC presets without changing saved indices or native choices."""

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from PySide6.QtWidgets import QApplication
from modules.localization.v1_0 import UI_TRANSLATIONS
from modules.rgb_studio.v1_15.design_gallery import RGBDesignGallery, build_category_selector
from rgb_effects import BUILTIN_DESIGNS, BUILTIN_DESIGN_CATEGORIES


def test_rgb_categories_retain_every_design_and_four_language_native_entry():
    app = QApplication.instance() or QApplication([])
    expected = {"Prism Drift": "Räumlich", "Twin Wyrm Orbit": "Räumlich",
                "Neon Particle Garden": "Energie", "Circuit Chase": "Bewegung"}
    for language in ("de", "en", "es", "fr"):
        changes = []
        tr = lambda source: UI_TRANSLATIONS[language][source]
        selector, buttons = build_category_selector(tr, changes.append)
        assert "OHC Originale" not in buttons
        assert "Räumlich" in buttons and "OpenRGB Originale" in buttons
        buttons["OpenRGB Originale"].click()
        assert changes == ["OpenRGB Originale"]
        assert all(button.text() == tr(key) for key, button in buttons.items())
        gallery = RGBDesignGallery(translator=tr)
        gallery.set_view_mode("all")
        seen = []
        for category in buttons:
            if category in {"Alle", "OpenRGB Originale"}:
                continue
            gallery.set_category(category)
            seen.extend(gallery.visible_indices())
        assert len(BUILTIN_DESIGNS) == 45
        assert sorted(seen) == list(range(len(BUILTIN_DESIGNS)))
        for index in range(30, 34):
            title, _cfg = BUILTIN_DESIGNS[index]
            assert BUILTIN_DESIGN_CATEGORIES[index] == expected[title]
        assert len(gallery.suggestion_indices) == 12
        gallery.set_category("OHC Originale")  # stale callers safely recover
        assert gallery.category == "Alle"
        selector.deleteLater()
        gallery.deleteLater()
        app.processEvents()
