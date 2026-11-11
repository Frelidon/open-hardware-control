#!/usr/bin/env python3
"""Regression guards for the one-file-per-language localization module."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from localization_catalog import HELP_TOPICS, SETUP_TRANSLATIONS, UI_TRANSLATIONS  # noqa: E402
from modules.localization.v1_0 import de, en, es, fr  # noqa: E402


def test_each_supported_language_has_one_complete_data_file():
    module_dir = SRC / "modules/localization/v1_0"
    language_modules = (de, en, es, fr)
    assert tuple(module.LANGUAGE_CODE for module in language_modules) == ("de", "en", "es", "fr")
    assert {path.name for path in module_dir.glob("??.py")} == {"de.py", "en.py", "es.py", "fr.py"}
    assert all(set(module.UI_MESSAGES) == set(de.UI_MESSAGES) for module in language_modules)
    assert len(de.UI_MESSAGES) == 2444
    assert len(set(de.UI_MESSAGES.values())) == len(de.UI_MESSAGES)


def test_all_language_surfaces_are_assembled_without_data_loss():
    assert tuple(UI_TRANSLATIONS) == ("de", "en", "es", "fr")
    assert tuple(SETUP_TRANSLATIONS) == ("de", "en", "es", "fr")
    assert tuple(HELP_TOPICS) == ("de", "en", "es", "fr")
    for language in UI_TRANSLATIONS:
        assert len(UI_TRANSLATIONS[language]) == 2444
        assert len(SETUP_TRANSLATIONS[language]) == 37
        assert len(HELP_TOPICS[language]) == 11
    assert UI_TRANSLATIONS["de"]["Ausbalanciert"] == "Ausbalanciert"
    assert UI_TRANSLATIONS["en"]["Ausbalanciert"] == "Balanced"
    assert UI_TRANSLATIONS["es"]["Ausbalanciert"] == "Equilibrado"
    assert UI_TRANSLATIONS["fr"]["Ausbalanciert"] == "Équilibré"
    assert UI_TRANSLATIONS["en"]["3 · Hilfspakete installieren"] == "3 · Install helper packages"
    assert UI_TRANSLATIONS["es"]["4 · Plugin installieren"] == "4 · Instalar complemento"
    assert UI_TRANSLATIONS["fr"]["Leistung und SSD-Cache"] == "Performances et cache SSD"
    assert UI_TRANSLATIONS["en"]["3 · MOK-Import im Terminal starten"] == "3 · Start MOK import in terminal"
    assert UI_TRANSLATIONS["es"]["MOK-Schlüssel"] == "Clave MOK"
    assert UI_TRANSLATIONS["fr"]["Modulsignatur"] == "Signature du module"
    assert UI_TRANSLATIONS["en"]["Alle Lüfterzuordnungen zurücksetzen"] == "Reset all fan assignments"
    assert UI_TRANSLATIONS["es"]["Nächsten Lüfter zuordnen"] == "Asignar el siguiente ventilador"


def test_compatibility_facade_is_small_and_old_split_files_are_gone():
    facade = (SRC / "localization_catalog.py").read_text(encoding="utf-8")
    assert len(facade.splitlines()) < 40
    assert "from modules.localization.v1_0 import" in facade
    for obsolete in (
        "localization_controls.py", "localization_cards.py",
        "localization_labels.py", "localization_policy.py",
    ):
        assert not (SRC / obsolete).exists()


def test_language_files_are_data_only_and_below_the_registered_hard_limit():
    module_dir = SRC / "modules/localization/v1_0"
    for language in ("de", "en", "es", "fr"):
        source = (module_dir / f"{language}.py").read_text(encoding="utf-8")
        assert "UI_MESSAGES" in source
        assert "SETUP_TRANSLATIONS" in source
        assert "HELP_TOPICS" in source
        assert len(source.splitlines()) <= 620
        assert len(source) < 78_000
