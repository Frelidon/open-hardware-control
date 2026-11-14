from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (ROOT / "docs/project/MODULE_REGISTRY.md").read_text(encoding="utf-8")
AGENTS = (ROOT / "docs/ai/AGENTS.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "docs/ai/AI_DEVELOPMENT_GUIDE.md").read_text(encoding="utf-8")
REGISTRY_CHECK = (ROOT / "scripts" / "check_module_registry.py").read_text(encoding="utf-8")


def test_registry_is_mandatory_and_uses_date_without_time() -> None:
    assert "Read `docs/project/MODULE_REGISTRY.md`" in AGENTS
    assert "01.09.26" in REGISTRY
    assert "TT.MM.JJ" in REGISTRY
    assert "Keine Uhrzeit" in REGISTRY
    assert not re.search(r"\b\d{2}:\d{2}(?::\d{2})?\b", REGISTRY)


def test_registry_points_to_only_current_versioned_levita_module() -> None:
    assert "modules/lcd_levita/v1_7/" in REGISTRY
    version_dirs = sorted(
        path.name for path in (ROOT / "src/modules" / "lcd_levita").iterdir()
        if path.is_dir() and path.name.startswith("v")
    )
    assert version_dirs == ["v1_7"]
    assert (ROOT / "src/modules" / "lcd_levita" / "v1_7" / "README.md").is_file()


def test_registry_points_to_only_current_versioned_rgb_module() -> None:
    assert "modules/rgb_studio/v1_15/" in REGISTRY
    version_dirs = sorted(
        path.name for path in (ROOT / "src/modules" / "rgb_studio").iterdir()
        if path.is_dir() and path.name.startswith("v")
    )
    assert version_dirs == ["v1_15"]
    assert (ROOT / "src/modules" / "rgb_studio" / "v1_15" / "README.md").is_file()


def test_registry_points_to_only_current_display_effects_module() -> None:
    assert "modules/display_effects/v1_11/" in REGISTRY
    version_dirs = sorted(
        path.name for path in (ROOT / "src/modules" / "display_effects").iterdir()
        if path.is_dir() and path.name.startswith("v")
    )
    assert version_dirs == ["v1_11"]
    assert (ROOT / "src/modules" / "display_effects" / "v1_11" / "README.md").is_file()


def test_registry_points_to_current_levita_performance_and_window_modules() -> None:
    expected = {
        "levita_daemon_health": "v1_1",
        "levita_performance": "v1_1",
        "window_chrome": "v1_2",
        "window_placement": "v1_5",
        "ui_performance": "v1_1",
        "mainboard_driver_setup": "v1_1",
        "wallpaper_engine": "v1_3",
        "responsive_gallery": "v1_0",
        "lcd_media_manager": "v1_1",
        "temperature_history": "v1_2",
        "pc_case_profiles": "v1_5",
        "cooling_state": "v1_0",
        "navigation_settings": "v1_0",
        "programs": "v1_0",
        "lcd_runtime": "v1_1",
    }
    for module, version in expected.items():
        module_root = ROOT / "src/modules" / module
        version_dirs = sorted(
            path.name for path in module_root.iterdir()
            if path.is_dir() and path.name.startswith("v")
        )
        assert version_dirs == [version]
        assert f"modules/{module}/{version}/" in REGISTRY
        assert (module_root / version / "README.md").is_file()


def test_local_ai_size_budgets_are_explicit() -> None:
    assert "600 Zeilen" in REGISTRY
    assert "32.000 Zeichen" in REGISTRY
    assert "800 Zeilen" in REGISTRY
    assert "1.200 Zeilen" in REGISTRY
    assert "Git-Historie" in REGISTRY


def test_ai_guide_covers_small_ui_sensor_and_lcd_modules() -> None:
    assert "## UI-Komponente erweitern" in GUIDE
    assert "## Sensor-Komponente erweitern" in GUIDE
    assert "## LCD-Komponente erweitern" in GUIDE
    assert "16 GB VRAM" in GUIDE
    assert "MODULE_REGISTRY.md" in GUIDE
    assert "docs/project/MODULE_REGISTRY.md" in AGENTS


def test_registry_validator_passes() -> None:
    import subprocess
    import sys

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_module_registry.py")],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_registry_validator_accepts_the_declared_release_channel() -> None:
    assert 'ROOT / "packaging/BUILD_CHANNEL"' in REGISTRY_CHECK
    assert '{version} {channel}' in REGISTRY_CHECK
    assert '{version} INTERN' not in REGISTRY_CHECK
