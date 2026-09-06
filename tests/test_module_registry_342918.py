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
    assert "modules/lcd_levita/v1_4/" in REGISTRY
    version_dirs = sorted(
        path.name for path in (ROOT / "src/modules" / "lcd_levita").iterdir()
        if path.is_dir() and path.name.startswith("v")
    )
    assert version_dirs == ["v1_4"]
    assert (ROOT / "src/modules" / "lcd_levita" / "v1_4" / "README.md").is_file()


def test_registry_points_to_only_current_versioned_rgb_module() -> None:
    assert "modules/rgb_studio/v1_1/" in REGISTRY
    version_dirs = sorted(
        path.name for path in (ROOT / "src/modules" / "rgb_studio").iterdir()
        if path.is_dir() and path.name.startswith("v")
    )
    assert version_dirs == ["v1_1"]
    assert (ROOT / "src/modules" / "rgb_studio" / "v1_1" / "README.md").is_file()


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
