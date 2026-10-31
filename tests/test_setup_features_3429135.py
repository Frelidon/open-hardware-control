"""Platform-aware first-run and settings feature ownership tests."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.control_authority.v1_0 import (  # noqa: E402
    authority_choices,
    normalize_authority,
    ohc_may_write,
)
from modules.setup_features.v1_0 import feature_choices, normalize_selection  # noqa: E402


def test_feature_catalog_tracks_platform_and_legacy_default() -> None:
    linux = {item.key: item for item in feature_choices("linux")}
    windows = {item.key: item for item in feature_choices("win32")}
    assert linux["snapshots"].available and not windows["snapshots"].available
    assert linux["cooling"].available and not windows["cooling"].available
    assert windows["rgb"].available and windows["lcd"].available
    assert set(normalize_selection(None, platform="linux")) == {
        key for key, item in linux.items() if item.default_enabled
    }
    assert "snapshots" not in normalize_selection(["snapshots", "rgb"], platform="win32")


def test_navigation_shaped_152_selection_preserves_feature_choices() -> None:
    assert set(normalize_selection(
        ["cooling", "rgb_studio", "lcd", "display_effects", "snapshot_manager", "wallpaper_engine", "profiles", "settings"],
        platform="linux",
    )) == {"cooling", "rgb", "lcd", "snapshots", "wallpaper", "automation"}
    assert normalize_selection(["cooling"], platform="linux") == ("cooling",)
    assert normalize_selection([], platform="linux") == ()


def test_authority_is_fail_closed_and_windows_offers_external_owners() -> None:
    windows_rgb = {choice.key: choice for choice in authority_choices("rgb", "win32")}
    assert {"signalrgb", "icue", "dynamic_lighting"} <= windows_rgb.keys()
    assert not windows_rgb["signalrgb"].ohc_writes
    assert normalize_authority("rgb", "unknown-provider", "win32") == "monitor"
    assert ohc_may_write("rgb", "ohc_openrgb", "win32")
    assert not ohc_may_write("rgb", "signalrgb", "win32")
    assert not ohc_may_write("gpu", "ohc_lact", "win32")


def test_wizard_and_settings_share_cards_and_physical_release_paths() -> None:
    source = (ROOT / "src" / "kraken_control.py").read_text(encoding="utf-8")
    ownership = (ROOT / "src/modules/setup_features/v1_0/ownership.py").read_text(encoding="utf-8")
    panel = (
        ROOT / "src" / "modules" / "setup_features" / "v1_0" / "settings_panel.py"
    ).read_text(encoding="utf-8")
    assert "self.feature_cards" in source and "Funktionen auswählen" in source
    assert "build_feature_settings(self, layout)" in source
    assert "FeatureOwnershipMixin" in source
    assert "def release_feature_writers" in ownership
    assert "restore_firmware_display()" in ownership
    assert "stop_managed_rgb_engine" in ownership
    assert "Steuerungszuständigkeit" in panel
    assert "set_control_authority" in panel


def test_feature_hover_reserves_space_instead_of_reflowing_settings() -> None:
    widgets = (ROOT / "src/modules/setup_features/v1_0/widgets.py").read_text(encoding="utf-8")
    assert "self.details.setFixedHeight(58)" in widgets
    assert "QGraphicsOpacityEffect" in widgets
    assert 'b"maximumHeight"' not in widgets
