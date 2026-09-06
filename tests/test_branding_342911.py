from pathlib import Path

from PIL import Image

from PySide6.QtWidgets import QApplication


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
BRANDING = (ROOT / "src/branding.py").read_text(encoding="utf-8")
INSTALLER = (ROOT / "packaging/install.sh").read_text(encoding="utf-8")
BUILDER = (ROOT / "scripts/build_release.py").read_text(encoding="utf-8")

import sys

sys.path.insert(0, str(ROOT / "src"))
from branding import system_tray_icon  # noqa: E402


def test_full_logo_and_compact_transparent_icon_are_packaged() -> None:
    logo = ROOT / "src/assets/branding/open-hardware-control-logo.png"
    icon = ROOT / "src/assets/branding/open-hardware-control-icon.png"
    assert logo.is_file()
    assert icon.is_file()
    with Image.open(logo) as image:
        assert image.size == (768, 768)
    with Image.open(icon) as image:
        assert image.size == (512, 512)
        assert image.mode == "RGBA"
        assert image.getextrema()[3][0] == 0
    for size in (22, 32, 48, 64, 128, 256):
        path = ROOT / f"src/assets/branding/icons/open-hardware-control-{size}.png"
        with Image.open(path) as image:
            assert image.size == (size, size)


def test_logo_is_inlaid_in_sidebar_and_icon_reaches_window_tray_and_packages() -> None:
    assert 'create_sidebar_branding(Path(__file__).resolve().parent)' in MAIN
    assert '"open-hardware-control-logo.png"' in BRANDING
    assert '"open-hardware-control-icon.png"' in BRANDING
    assert 'logo.setObjectName("brandLogo")' in BRANDING
    assert 'open-hardware-control-icon.png" not in autostart_text' in MAIN
    assert '$APP_DIR/assets/branding/open-hardware-control-icon.png' in INSTALLER
    assert 'open-hardware-control-icon.png' in BUILDER
    assert 'usr/share/icons/hicolor/{size}x{size}/apps' in BUILDER
    assert 'system_tray_icon(Path(__file__).resolve().parent)' in MAIN
    assert 'QIcon.fromTheme("preferences-system-cooling")' not in MAIN
    assert 'for size in (22, 32, 48, 64)' in BRANDING


def test_system_tray_icon_contains_plasma_native_size() -> None:
    QApplication.instance() or QApplication(["ohc-branding-test", "-platform", "offscreen"])
    icon = system_tray_icon(ROOT / "src")
    assert not icon.isNull()
    assert any(size.width() == 22 and size.height() == 22 for size in icon.availableSizes())


def test_zip_installer_contains_new_runtime_modules() -> None:
    for module in (
        "branding.py",
        "thermalright_cooling.py",
        "thermalright_display.py",
        "thermalright_display_ui.py",
        "window_diagnostics.py",
    ):
        assert f'$SRC_DIR/{module}' in INSTALLER
