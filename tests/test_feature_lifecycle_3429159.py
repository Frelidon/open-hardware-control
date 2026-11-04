"""Feature maturity and versions stay complete, visible and hardware-inert."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.feature_lifecycle.v1_0 import feature_lifecycle, feature_lifecycles  # noqa: E402
from modules.localization.v1_0 import UI_TRANSLATIONS  # noqa: E402


def test_lifecycle_catalog_has_unique_semantic_versions_and_expected_stages() -> None:
    catalog = {item.key: item for item in feature_lifecycles()}
    assert len(catalog) == len(feature_lifecycles()) == 18
    assert catalog["openlinkhub"].stage == "Alpha"
    assert catalog["gpu"].stage == catalog["case"].stage == "Beta"
    assert catalog["hardware_checker"].stage == "Alpha"
    assert catalog["automations"].stage == catalog["programs"].stage == "Alpha"
    assert catalog["rgb_studio"].stage == catalog["lcd"].stage == "Release Candidate"
    assert catalog["wallpaper_engine"].stage == "Beta"
    assert catalog["snapshot_manager"].stage == "Alpha"
    assert catalog["profiles"].stage == catalog["overview"].stage == "Beta"
    assert all(item.version and item.version[0].isdigit() for item in catalog.values())


def test_setup_aliases_resolve_to_the_same_read_only_metadata() -> None:
    assert feature_lifecycle("rgb") is feature_lifecycle("rgb_studio")
    assert feature_lifecycle("snapshots") is feature_lifecycle("snapshot_manager")
    assert feature_lifecycle("automation") is feature_lifecycle("automations")
    assert feature_lifecycle("wallpaper") is feature_lifecycle("wallpaper_engine")
    assert feature_lifecycle("unknown") is None


def test_lifecycle_stages_are_translated_in_all_languages() -> None:
    for language in ("de", "en", "es", "fr"):
        translations = UI_TRANSLATIONS[language]
        for stage in ("Alpha", "Beta", "Release Candidate", "Stabil"):
            assert translations.get(stage)


def test_lifecycle_catalog_has_no_hardware_or_settings_dependency() -> None:
    source = (ROOT / "src/modules/feature_lifecycle/v1_0/catalog.py").read_text(encoding="utf-8")
    for forbidden in ("QSettings", "subprocess", "openrgb", "liquidctl", "write("):
        assert forbidden not in source
