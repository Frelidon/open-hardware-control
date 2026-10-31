#!/usr/bin/env python3
"""Regression coverage for modular UI themes in 3.4.29.71."""

from pathlib import Path
import ast
import sys

from PySide6.QtGui import QColor, QPalette

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.ui_themes.v1_0 import THEME_IDS, resolve_theme  # noqa: E402


def test_light_and_dark_are_independent_registered_theme_modules():
    light_path = ROOT / "src/modules/ui_themes/v1_0/light.py"
    dark_path = ROOT / "src/modules/ui_themes/v1_0/dark.py"
    assert light_path.is_file() and dark_path.is_file()
    assert THEME_IDS == ("system", "light", "dark", "studio-light", "studio-dark")
    system = QPalette()
    accent = QColor("#2f80ed")
    light = resolve_theme("light", system, accent)
    dark = resolve_theme("dark", system, accent)
    assert set(light.styles) == set(dark.styles)
    assert light.palette_colors[QPalette.ColorRole.Window] == "#f3f6fa"
    assert dark.palette_colors[QPalette.ColorRole.Window] == "#11161d"
    assert light.styles["panel"] == "rgba(255, 255, 255, 248)"
    assert light.styles["design_title"] == "#17212b"
    assert dark.styles["design_title"] == "#eaf7ff"
    studio_light = resolve_theme("studio-light", system, accent)
    studio_dark = resolve_theme("studio-dark", system, accent)
    assert studio_light.animated_background_allowed is False
    assert studio_dark.animated_background_allowed is False
    assert studio_light.styles["studio_shell"] == "true"
    assert studio_dark.styles["studio_shell"] == "true"
    assert light.animated_background_allowed is True
    assert dark.animated_background_allowed is True
    assert light.styles["content"].startswith("rgba(")
    assert studio_light.styles["content"].startswith("#")
    assert light.styles["lcd_card"] != studio_light.styles["lcd_card"]


def test_lcd_gallery_uses_theme_owned_surface_styles():
    ui = (ROOT / "src/thermalright_display_ui.py").read_text(encoding="utf-8")
    controller = (ROOT / "src/modules/ui_themes/v1_0/controller.py").read_text(encoding="utf-8")
    controller += "".join((ROOT / "src/modules/ui_themes/v1_0" / name).read_text(encoding="utf-8")
                          for name in ("style_base.py", "style_controls.py"))
    assert 'setObjectName("lcdDesignCard")' in ui
    assert 'setObjectName("lcdCategoryButton")' in ui
    assert "rgba(7,20,32,170)" not in ui
    assert "QToolButton#lcdDesignCard" in controller
    assert "QToolButton#lcdCategoryButton" in controller


def test_theme_controller_is_outside_the_main_window_and_future_extensible():
    main = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    registry = (ROOT / "src/modules/ui_themes/v1_0/registry.py").read_text(encoding="utf-8")
    controller = (ROOT / "src/modules/ui_themes/v1_0/controller.py").read_text(encoding="utf-8")
    window = next(node for node in ast.parse(main).body if isinstance(node, ast.ClassDef) and node.name == "KrakenControl")
    assert any(isinstance(base, ast.Name) and base.id == "UiThemeMixin" for base in window.bases)
    assert "def apply_theme" not in main
    assert 'THEME_FACTORIES: dict[str, ThemeFactory]' in registry
    assert "resolve_theme(self.theme_mode" in controller
