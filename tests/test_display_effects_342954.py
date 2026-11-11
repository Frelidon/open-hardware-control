#!/usr/bin/env python3
"""Regression tests for procedural display effects and Levita integration."""

from pathlib import Path
import hashlib
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEventLoop, QSettings, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QToolButton


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from modules.display_effects.v1_11 import DisplayEffectsPage  # noqa: E402
from modules.display_effects.v1_11.catalog import DESIGNS, designs_for_category, validated_asset  # noqa: E402
from modules.display_effects.v1_11.handoff import validate_effect_handoff  # noqa: E402
from modules.display_effects.v1_11.model import SmokeSettings  # noqa: E402
from modules.display_effects.v1_11.light_bands_renderer import render_light_bands_frame  # noqa: E402
from modules.display_effects.v1_11.library import StockEffectsLibrary  # noqa: E402
from modules.display_effects.v1_11.smoke_renderer import render_smoke_frame  # noqa: E402
from modules.lcd_levita.v1_7.motion_renderer import render_layer2_motion_frame  # noqa: E402
from modules.display_effects.v1_11.video_preview import BundledVideoPreview  # noqa: E402


def test_smoke_settings_are_bounded_serializable_and_stable():
    settings = SmokeSettings.from_mapping({
        "primary_color": "bad", "secondary_color": "#12abef",
        "sharpness": 3, "density": 500, "speed": "70", "turbulence": -4,
        "glow": 101, "direction": "diagonal",
    })
    assert settings.primary_color == "#FF6A00"
    assert settings.secondary_color == "#12ABEF"
    assert (settings.sharpness, settings.density, settings.speed) == (50, 100, 70)
    assert (settings.turbulence, settings.glow, settings.direction) == (0, 100, "right")
    assert SmokeSettings.from_mapping(settings.as_dict()).cache_key() == settings.cache_key()


def test_smoke_frame_is_deterministic_dark_and_has_sharp_highlights():
    settings = SmokeSettings()
    first = render_smoke_frame(settings, 0.25, width=400, height=180)
    second = render_smoke_frame(settings, 0.25, width=400, height=180)
    assert first.size() == second.size()
    assert hashlib.sha256(bytes(first.bits())).digest() == hashlib.sha256(bytes(second.bits())).digest()
    samples = [first.pixelColor(x, y).lightness() for y in range(0, 180, 6) for x in range(0, 400, 6)]
    assert min(samples) < 12
    assert max(samples) > 150
    assert first.pixelColor(0, 0) != QColor("#FFFFFF")


def test_worker_and_studio_keep_generation_in_the_safe_existing_pipeline():
    worker = (SRC / "modules/display_effects/v1_11/worker.py").read_text(encoding="utf-8")
    studio = (SRC / "thermalright_display_ui.py").read_text(encoding="utf-8")
    page = (SRC / "modules/display_effects/v1_11/base_page.py").read_text(encoding="utf-8")
    assert "shell=True" not in worker
    assert "relative_to(root.resolve())" in worker
    assert 'target.suffix.casefold() != ".mp4"' in worker
    assert "select_generated_effect_media" in studio
    assert "select_bundled_effect_media" in studio
    assert "self.studio.select_bundled_effect_media(output, title)" in page
    assert "self.studio.stage_profile_startup_design()" in page
    assert "self.studio.apply_design()" in page
    assert "ThermalrightCli" not in page


def test_effect_page_explains_and_exposes_canonical_startup_saving():
    page = (SRC / "modules/display_effects/v1_11/base_page.py").read_text(encoding="utf-8")
    assert 'QPushButton("Als Startdesign vormerken")' in page
    assert "beim nächsten Programmstart automatisch verwendet" in page
    assert "def remember_for_profile_start" in page
    assert "def _library_selection_changed" in page
    assert "self.studio.remember_effect_startup_design(" in page
    assert "self.studio.stage_profile_startup_design()" in page


def test_bundled_effect_catalog_is_complete_attributed_and_bounded():
    assert len(DESIGNS) == 6
    assert len(next(design for design in DESIGNS if design.ident == "ohc-light-bands").variants) == 8
    assert all(len(design.variants) == 1 for design in DESIGNS if design.ident != "ohc-light-bands")
    assert len(designs_for_category("ohc_original")) == 6
    assert all(design.ident.startswith("ohc-") for design in DESIGNS)
    assert all(design.creator == "Frelidon / Open Hardware Control" for design in DESIGNS)
    rejected = " ".join(f"{design.ident} {design.title} {design.description}" for design in DESIGNS).casefold()
    assert "saturn" not in rejected
    assert "grand canyon" not in rejected
    assert "fly-through" not in rejected
    assert "ohc-spectrum-motion" not in {design.ident for design in DESIGNS}
    assert {variant.ident for variant in DESIGNS[0].variants} == {
        "right", "left", "down", "up", "down-right", "up-left", "down-left", "up-right",
    }
    for design in DESIGNS:
        assert design.creator and design.creator_url.startswith("https://")
        assert design.source_url.startswith("https://")
        assert design.license_name and design.license_url.startswith("https://")
        for variant in design.variants:
            video = validated_asset(variant)
            preview = validated_asset(variant, preview=True)
            assert video.stat().st_size > 100_000
            assert preview.stat().st_size > 1_000


def test_library_uses_graphical_cards_and_keeps_attribution_links():
    app = QApplication.instance() or QApplication([])
    library = StockEffectsLibrary(lambda source: source)
    cards = [
        button for button in library.findChildren(QToolButton)
        if button.objectName() == "effectDesignCard"
    ]
    assert library.design_combo.isHidden()
    assert len(cards) == len(DESIGNS)
    assert sum(button.isChecked() for button in cards) == 0
    library._select_design_card(DESIGNS[0].ident)
    assert sum(button.isChecked() for button in cards) == 1
    assert all(not button.icon().isNull() for button in cards)
    assert "Originalquelle" in library.credit_label.text()
    assert library.credit_label.text().count("<a href=") == 3
    library.category_combo.setCurrentIndex(library.category_combo.findData("ohc_original"))
    assert len(library._design_cards) == 6
    app.processEvents()


def test_effect_preview_waits_for_page_paint_and_reuses_loaded_cards():
    page = (SRC / "modules/display_effects/v1_11/page.py").read_text(encoding="utf-8")
    base = (SRC / "modules/display_effects/v1_11/base_page.py").read_text(encoding="utf-8")
    library = (SRC / "modules/display_effects/v1_11/library.py").read_text(encoding="utf-8")
    assert "QTimer.singleShot(40" in page
    assert "self._preview_ready_after_show = True" in page
    assert "self.preview_timer.setInterval(50)" in base
    assert "if not force and signature == self._layer2_signature" in base
    relayout = library.split("def _relayout_cards", 1)[1].split("def _select_design_card", 1)[0]
    assert "reflow_grid" in relayout
    assert "_rebuild_design_cards" not in relayout


class _FakeStudio:
    def __init__(self, media: Path, generated_root: Path) -> None:
        self._media = media
        self._generated_root = generated_root
        self.hardware_design_combo = QComboBox()
        self.hardware_design_combo.addItem("OHC data", "")
        self.media_combo = QComboBox()
        self.media_combo.addItem(media.name, str(media))
        self.staged: list[Path] = []

    def current_media_path(self) -> Path:
        return self._media

    def generated_effect_directory(self) -> Path:
        return self._generated_root

    def layer2_preview_choices(self):  # type: ignore[no-untyped-def]
        return []

    def sync_effect_preview(self, _target, _background) -> None:  # type: ignore[no-untyped-def]
        pass

    def stage_profile_effect_media(self, path: Path, *, bundled: bool) -> bool:
        self.staged.append(path)
        return bundled


def test_effect_page_mirrors_active_library_design_without_restaging(tmp_path: Path):
    app = QApplication.instance() or QApplication([])
    design = next(item for item in DESIGNS if item.ident == "ohc-prism-drift")
    media = validated_asset(design.variants[0])
    studio = _FakeStudio(media, tmp_path / "generated")
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    page = DisplayEffectsPage(
        settings,
        studio,
        hero_factory=lambda *_args: QFrame(),
    )
    assert page.effect_combo.currentData() == "library"
    assert page.stock_library.current_design().ident == "ohc-prism-drift"
    assert page.stock_library.current_variant().ident == "original"
    assert page.stock_library.category_combo.currentData() == "ohc_original"
    assert studio.staged == []
    page.shutdown()
    app.processEvents()


def test_ohc_prism_preview_starts_on_visible_motion_and_pauses_decoder():
    app = QApplication.instance() or QApplication([])
    design = next(item for item in DESIGNS if item.ident == "ohc-prism-drift")
    preview = BundledVideoPreview()
    frames = []
    preview.frame_ready.connect(frames.append)
    preview.load(validated_asset(design.variants[0]), preview_start_ms=0)
    preview.set_active(True)
    loop = QEventLoop()
    QTimer.singleShot(1400, loop.quit)
    loop.exec()
    assert frames
    image = preview.latest_image.copy()
    samples = [
        image.pixelColor(x, y).lightness()
        for y in range(0, image.height(), 60)
        for x in range(0, image.width(), 80)
    ]
    assert max(samples) > 80
    preview.set_active(False)
    assert not preview._active
    assert not preview._source_loaded
    assert preview.latest_image.isNull()
    preview.shutdown()
    app.processEvents()


def test_original_light_bands_support_eight_directions_and_seamless_phase():
    assert len({variant.ident for variant in next(
        design for design in DESIGNS if design.ident == "ohc-light-bands"
    ).variants}) == 8
    first = render_light_bands_frame("up-right", 0.0, width=400, height=180)
    loop = render_light_bands_frame("up-right", 1.0, width=400, height=180)
    assert hashlib.sha256(bytes(first.bits())).digest() == hashlib.sha256(bytes(loop.bits())).digest()


def test_light_bands_release_renderer_uses_native_supersampling_and_high_quality_encoding():
    tool = (ROOT / "tools/render_light_bands.py").read_text(encoding="utf-8")
    assert "width=4800, height=2160" in tool
    assert '1600, 720, Qt.AspectRatioMode.IgnoreAspectRatio' in tool
    assert '"-preset", "slow", "-tune", "animation", "-crf", "10"' in tool


def test_original_layer2_spectrum_ring_is_seamless_and_transparent():
    first = render_layer2_motion_frame("ohc-spectrum-ring", 0.0, width=400, height=180)
    loop = render_layer2_motion_frame("ohc-spectrum-ring", 1.0, width=400, height=180)
    assert hashlib.sha256(bytes(first.bits())).digest() == hashlib.sha256(bytes(loop.bits())).digest()
    assert first.pixelColor(399, 90).alpha() == 0


def test_effect_handoff_accepts_only_regular_mp4_below_selected_root(tmp_path: Path):
    root = tmp_path / "allowed"
    root.mkdir()
    video = root / "effect.mp4"
    video.write_bytes(b"video")
    assert validate_effect_handoff(video, root) == video.resolve()

    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"video")
    try:
        validate_effect_handoff(outside, root)
    except ValueError as exc:
        assert "außerhalb" in str(exc)
    else:
        raise AssertionError("outside media was accepted")

    link = root / "linked.mp4"
    link.symlink_to(outside)
    try:
        validate_effect_handoff(link, root)
    except ValueError:
        pass
    else:
        raise AssertionError("symlinked media was accepted")
