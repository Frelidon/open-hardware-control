from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_import_ui_and_safety_text_wired() -> None:
    source = (ROOT / "src" / "kraken_control.py").read_text(encoding="utf-8")
    for text in (
        "NZXT-ESC-Profil importieren",
        "Als neues Profil importieren",
        "Importierten Originalzustand wiederherstellen",
        "OHC-Standardprofil als neue Kopie anlegen",
        "Backup erstellen",
        "Backup wiederherstellen",
        "Passende Beschriftung automatisch ändern",
    ):
        assert text in source or text in (ROOT / "src" / "nzxt_esc_profiles.py").read_text(encoding="utf-8")
    assert "NZXT_ESC_URL" in source
    assert "stop_imported_lcd_mode" in source


def test_runtime_package_includes_importer() -> None:
    build = (ROOT / "scripts/build_release.py").read_text(encoding="utf-8")
    assert '"nzxt_esc_profiles.py"' in build
