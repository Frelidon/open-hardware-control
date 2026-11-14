"""Real paired-design sizes, immutable source selection and stale-job safety."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import os
import shutil
import subprocess
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

import pytest
from PySide6.QtCore import QSettings, QProcess
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel
from rgb_effects import BUILTIN_DESIGNS
from modules.design_hub.v1_1.catalog import PAIRS, MATRIX_SIZES, pair_media, pair_poster, validate_pair_media
from modules.design_hub.v1_1.controller import apply_pair, resolve_pair
from modules.design_hub.v1_1.page import DesignHubPage
from modules.design_hub.v1_1.preparation import ZoomPreparation
from modules.design_hub.v1_1.scaling import encoder_arguments, valid_zoom, validate_prepared, zoom_filter, zoom_plan


def application():
    return QApplication.instance() or QApplication([])


def host(tmp_path):
    calls = []
    studio = SimpleNamespace(
        generated_effect_directory=lambda: tmp_path / 'generated',
        select_owned_design_media=lambda path, title: calls.append(('select', path, title)),
        select_generated_effect_media=lambda path, title: calls.append(('generated', path, title)),
        stage_profile_startup_design=lambda: calls.append(('stage',)),
        apply_design=lambda: calls.append(('apply',)),
    )
    return SimpleNamespace(
        settings=QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat),
        tr_static=str, calls=calls, thermalright_display_studio=studio,
        make_module_hero=lambda _icon, title, _description: QLabel(title),
        activate_rgb_design_tile=lambda index: calls.append(('rgb', index)),
        feature_enabled=lambda _key: True, is_thermalright_cooling=lambda: True,
    )


def test_fifteen_pairs_keep_old_ids_indices_and_use_unique_original_sources():
    assert [pair.ident for pair in PAIRS[:5]] == ['matrix', 'prism', 'wyrm', 'garden', 'circuit']
    assert [resolve_pair(pair)[0] for pair in PAIRS[:5]] == [34, 30, 31, 32, 33]
    assert len(PAIRS) == len({pair.ident for pair in PAIRS}) == 15
    assert len({pair_media(pair) for pair in PAIRS}) == 15
    assert len(BUILTIN_DESIGNS) == 45
    for pair in PAIRS:
        assert pair_poster(pair).is_file()
        assert validate_pair_media(pair_media(pair)) == pair_media(pair)


def test_fixed_media_whitelist_rejects_other_existing_media_and_symlinks(tmp_path):
    candidate = ROOT / 'src/assets/display-effects/ohc-spectrum-motion-original.mp4'
    assert candidate.is_file()
    with pytest.raises(ValueError): validate_pair_media(candidate)
    link = tmp_path / 'alias.mp4'; link.symlink_to(pair_media(PAIRS[0]))
    with pytest.raises(ValueError): validate_pair_media(link)
    with pytest.raises(ValueError): pair_media(replace(PAIRS[0], media_file='arbitrary.mp4'))


@pytest.mark.parametrize('zoom', (None, True, '100', float('nan'), 49, 201, 103))
def test_zoom_never_accepts_unbounded_or_fractional_values(zoom):
    with pytest.raises(ValueError): valid_zoom(zoom)


def test_size_controls_remember_each_design_without_applying_and_keep_matrix_variants(tmp_path):
    app = application(); fake = host(tmp_path); page = DesignHubPage(fake)
    try:
        assert page.sizes.glyph.value() == 1
        assert page.sizes.variant_id() == 'large-30'
        for index, (percent, ident) in enumerate(MATRIX_SIZES):
            page.sizes.glyph.setValue(index)
            assert page.sizes.variant_id() == ident
            assert f'{percent} %' == page.sizes.glyph_value.text()
            assert page.preview.video.source_path == pair_media(PAIRS[0], ident)
        page.sizes.zoom.setValue(145)
        page.select(PAIRS[1]); page.sizes.zoom.setValue(75)
        page.select(PAIRS[0])
        assert page.sizes.zoom.value() == 145
        assert page.preview.zoom == 145
        assert page.sizes.variant_id() == 'large-100'
        page.select(PAIRS[1])
        assert page.sizes.zoom.value() == 75
        assert not fake.calls
    finally:
        page.shutdown(); page.deleteLater(); app.processEvents()


def test_apply_uses_exact_requested_glyph_variant_and_keeps_sensor_layer_owner(tmp_path):
    fake = host(tmp_path)
    apply_pair(fake, PAIRS[0], 'both', variant_id='large-100')
    assert fake.calls == [('select', pair_media(PAIRS[0], 'large-100'), PAIRS[0].title),
                          ('rgb', 34), ('stage',), ('apply',)]


def test_unprepared_zoom_rejected_before_either_hardware_target(tmp_path):
    fake = host(tmp_path)
    with pytest.raises(ValueError): apply_pair(fake, PAIRS[0], 'both', zoom=150)
    assert not fake.calls
    source = pair_media(PAIRS[0]); plan = zoom_plan(source, tmp_path / 'elsewhere', 150)
    with pytest.raises(ValueError):
        validate_prepared(plan, source, tmp_path / 'generated/paired-zoom', 150)


def test_plan_has_matching_aspect_correct_filter_and_atomic_destination(tmp_path):
    source = pair_media(PAIRS[0]); plan = zoom_plan(source, tmp_path, 150)
    same = zoom_plan(source, tmp_path, 150)
    assert plan == same and source != plan.target
    assert plan.target != zoom_plan(source, tmp_path, 50).target
    assert 'scale=2400:1080' in zoom_filter(150)
    assert 'force_original_aspect_ratio=decrease' in zoom_filter(50)
    args = encoder_arguments(plan, tmp_path / '.work.mp4')
    assert args[args.index('-vf') + 1] == zoom_filter(150)
    assert '-an' in args and args[-1].endswith('.work.mp4')


def test_stale_preparation_cannot_apply_after_selection_or_size_change(tmp_path):
    app = application(); fake = host(tmp_path); page = DesignHubPage(fake)
    try:
        source = pair_media(PAIRS[0]); plan = zoom_plan(source, tmp_path / 'generated/paired-zoom', 150)
        page.pending_request = (PAIRS[0], None, 150, 'both')
        page.select(PAIRS[1]); page.prepared(plan)
        assert not fake.calls
        page.pending_request = (PAIRS[1], None, 150, 'both')
        page.sizes.zoom.setValue(125); page.prepared(plan)
        assert not fake.calls
    finally:
        page.shutdown(); page.deleteLater(); app.processEvents()


def test_missing_encoder_reports_failure_in_existing_private_error_bridge(tmp_path, monkeypatch):
    app = application(); preparation = ZoomPreparation(); logged = []; failed = []
    import privacy_logging
    monkeypatch.setattr(privacy_logging, 'append_error_event', logged.append)
    monkeypatch.setattr('modules.design_hub.v1_1.preparation.shutil.which', lambda _name: None)
    preparation.failed.connect(lambda: failed.append(True))
    preparation.start(pair_media(PAIRS[0]), tmp_path, 150)
    assert failed == [True]
    assert len(logged) == 1 and 'ffmpeg unavailable' in logged[0]
    assert preparation.process.state() == QProcess.ProcessState.NotRunning
    preparation.shutdown(); app.processEvents()


def test_newer_lcd_intent_discards_prepared_pair_before_rgb_or_lcd_apply(tmp_path, monkeypatch):
    app = application(); fake = host(tmp_path)
    fake.thermalright_display_studio.design_state = SimpleNamespace(generation=7)
    page = DesignHubPage(fake)
    monkeypatch.setattr(page.preparation, 'start', lambda *_args: None)
    monkeypatch.setattr('modules.design_hub.v1_1.page.apply_pair',
                        lambda *_args, **_kwargs: fake.calls.append(('unexpected-apply',)) or '')
    try:
        page.sizes.zoom.setValue(150); page.apply('both')
        assert page.pending_request is not None and page.pending_lcd_generation == 7
        source = pair_media(PAIRS[0], page.sizes.variant_id())
        plan = zoom_plan(source, tmp_path / 'generated/paired-zoom', 150)
        fake.thermalright_display_studio.design_state.generation += 1
        page.prepared(plan)
        assert not fake.calls
        assert page.pending_request is None and not page.message
        # An unchanged explicit intent still completes normally.
        page.apply('both'); page.prepared(plan)
        assert fake.calls == [('unexpected-apply',)]
    finally:
        page.shutdown(); page.deleteLater(); app.processEvents()


def test_leaving_design_hub_cancels_preparation_and_clears_waiting_status(tmp_path, monkeypatch):
    app = application(); fake = host(tmp_path)
    fake.thermalright_display_studio.design_state = SimpleNamespace(generation=1)
    page = DesignHubPage(fake)
    monkeypatch.setattr(page.preparation, 'start', lambda *_args: None)
    monkeypatch.setattr('modules.design_hub.v1_1.page.apply_pair',
                        lambda *_args, **_kwargs: fake.calls.append(('unexpected-apply',)) or '')
    try:
        page.show(); app.processEvents()
        page.sizes.zoom.setValue(150); page.apply('both')
        source = pair_media(PAIRS[0], page.sizes.variant_id())
        plan = zoom_plan(source, tmp_path / 'generated/paired-zoom', 150)
        assert page.pending_request is not None and page.message
        page.hide(); app.processEvents(); page.prepared(plan)
        assert page.pending_request is None and page.pending_lcd_generation is None
        assert page.preparation.cancelled and not page.message and not fake.calls
        assert page.preparation.process.state() == QProcess.ProcessState.NotRunning
    finally:
        page.shutdown(); page.deleteLater(); app.processEvents()


def test_failed_preparation_clears_request_and_generation_without_applying(tmp_path, monkeypatch):
    app = application(); fake = host(tmp_path)
    fake.thermalright_display_studio.design_state = SimpleNamespace(generation=3)
    page = DesignHubPage(fake)
    monkeypatch.setattr(page.preparation, 'start', lambda *_args: None)
    try:
        page.sizes.zoom.setValue(150); page.apply('both')
        assert page.pending_request is not None and page.pending_lcd_generation == 3
        page.preparation_failed()
        assert page.pending_request is None and page.pending_lcd_generation is None
        assert page.message == 'Die LCD-Größe konnte nicht vorbereitet werden. Bitte ffmpeg und freien Speicher prüfen.'
        assert not fake.calls
    finally:
        page.shutdown(); page.deleteLater(); app.processEvents()


@pytest.mark.skipif(not shutil.which('ffmpeg') or not shutil.which('ffprobe'), reason='local encoder tools unavailable')
def test_real_encoder_output_is_1600x720_and_cancel_has_no_ready_result(tmp_path):
    app = application(); preparation = ZoomPreparation(); ready = []; failed = []
    preparation.ready.connect(ready.append); preparation.failed.connect(lambda: failed.append(True))
    source = pair_media(PAIRS[0])
    cache = tmp_path / 'generated/paired-zoom'
    preparation.start(source, cache, 50)
    for _index in range(300):
        app.processEvents(); QTest.qWait(50)
        if ready or failed: break
    try:
        assert not failed and len(ready) == 1
        plan = ready[0]
        assert validate_prepared(plan, source, cache, 50) == plan.target
        metadata = subprocess.run([shutil.which('ffprobe'), '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(plan.target)],
            capture_output=True, text=True, timeout=10, check=True)
        assert metadata.stdout.strip() == '1600,720'
        fake = host(tmp_path)
        apply_pair(fake, PAIRS[0], 'both', zoom=50, prepared_media=plan)
        assert fake.calls == [('generated', plan.target, PAIRS[0].title), ('rgb', 34), ('stage',), ('apply',)]
        ready.clear()
        preparation.start(source, cache, 150); preparation.cancel()
        preparation.process.waitForFinished(5000); app.processEvents()
        assert not ready
        assert not list(cache.glob('.paired-zoom-*.mp4'))
        assert preparation.process.state() == QProcess.ProcessState.NotRunning
    finally:
        preparation.shutdown(); preparation.process.waitForFinished(5000)
