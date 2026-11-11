"""Profile read-only browsing, local media validation and decoder lifecycle."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import os
import sys
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget
from modules.profiles_workspace.v1_0.model import matches, summaries
from modules.profiles_workspace.v1_0.cards import ProfileCard
from modules.app_backgrounds.v1_0.catalog import VIDEO_THEMES, profile_source
from modules.app_backgrounds.v1_0.media import MediaBackground
from modules.app_backgrounds.v1_0.profile import mark_applied, sync
from modules.display_effects.v1_11.catalog import DESIGNS


@pytest.mark.parametrize('kind, expected', [('all',True),('user',False),('builtin',True)])
def test_filter_preserves_input_and_uses_stable_ids(kind,expected):
    profile={'id':'quiet','name':'Leise','category':'Kühlung','builtin':True}
    before=deepcopy(profile)
    assert matches(profile,' KÜHLUNG ',kind) is expected
    assert not matches(profile,'missing',kind)
    assert profile==before


@pytest.mark.parametrize('payload',[None,[],{}, {'cooling':None}, {'lcd':'bad','rgb':False}])
def test_malformed_and_empty_payloads_have_no_fake_summaries(payload):
    assert summaries(payload,str)==[]


def test_summary_uses_saved_values_without_mutating_or_inventing_gpu_metrics():
    payload={'gpu':{'name':'Saved GPU','config':{'power':120}},'cooling':{'pump':70,'fan':50},'rgb':{'studio_effect':'code_rain','studio_brightness':85},'future':{'x':1}}
    before=deepcopy(payload); items=summaries(payload,str)
    assert [item[0] for item in items]==['cooling','gpu','rgb']
    assert items[0][-1]==['Pumpe · 70 %','Lüfter · 50 %','2 Einstellungen']
    assert items[1][-1]==['Saved GPU','2 Einstellungen']
    assert payload==before


def test_local_profile_media_precedence_and_rejected_remote_paths(tmp_path):
    matrix=DESIGNS[-1].variants[0].video_path
    assert matrix.is_file()
    assert profile_source({'levita_display':{'media':str(matrix)},'rgb':{'studio_effect':'code_rain'}})==(matrix.resolve(),None)
    for value in ('https://example.org/clip.mp4','file:///tmp/clip.mp4','relative.mp4','/tmp/nul\x00.mp4',str(tmp_path),str(tmp_path/'missing.mp4')):
        assert profile_source({'lcd':{'file':value}})==(None,None)
    bad=tmp_path/'bad.txt';bad.write_text('not media')
    assert profile_source({'lcd':{'file':str(bad)}})==(None,None)
    sparse=tmp_path/'large.mp4'
    with sparse.open('wb') as stream:stream.truncate(256*1024*1024+1)
    assert profile_source({'lcd':{'file':str(sparse)}})==(None,None)


def test_rgb_preview_normalizes_bounds_and_bad_imports():
    _path,config=profile_source({'rgb':{'studio_effect':'code_rain','studio_brightness':200,'studio_speed':-5}})
    assert config.effect_id=='code_rain' and config.brightness==100 and config.speed==10
    assert profile_source({'rgb':{'studio_speed':{}}})==(None,None)


def test_matrix_default_and_old_small_variant_remain_distinct():
    design=next(item for item in DESIGNS if item.ident=='ohc-code-rain')
    assert [item.ident for item in design.variants]==['large-30','large-50','large-100','original']
    assert len({item.filename for item in design.variants})==4
    assert all(item.video_path.is_file() and item.preview_path.is_file() for item in design.variants)


def test_original_video_catalog_is_complete_and_local():
    assert len(VIDEO_THEMES)==6
    for path in VIDEO_THEMES.values():
        assert path.is_file() and path.with_suffix('.jpg').is_file()
        assert path.resolve().is_relative_to(ROOT/'src/assets')


def test_card_keyboard_selects_id_without_applying_hardware():
    app=QApplication.instance() or QApplication([])
    card=ProfileCard({'id':'literal-id','name':'My profile'},str)
    selected=[];card.selected.connect(selected.append)
    card.show();card.setFocus();QTest.keyClick(card,Qt.Key.Key_Return)
    assert selected==['literal-id']
    card.deleteLater();app.processEvents()


def test_profile_override_returns_to_global_theme_and_unloads_hidden_decoder():
    app=QApplication.instance() or QApplication([])
    window=QWidget();window.resize(500,300)
    background=QWidget(window);background.resize(500,300)
    background._theme='Ocean Caustics · Video';background._enabled=True
    background._window_active=True;background._pause_inactive=False;background._intensity=40
    background._frame_dirty=False;background._phase=0;background._timer=QTimer(background)
    background.media_background=MediaBackground(background)
    pages=QStackedWidget(window);profiles=QWidget();other=QWidget()
    pages.addWidget(other);pages.addWidget(profiles)
    host=SimpleNamespace(background_widget=background,tabs=pages,profile_workspace=profiles)
    background.media_background.configure();window.show();background.show()
    background.media_background.sync();app.processEvents()
    assert background.media_background.video.source_path==VIDEO_THEMES[background._theme].resolve()
    assert background.media_background.video._source_loaded
    payload={'lcd':{'file':str(DESIGNS[-1].variants[0].video_path)}}
    pages.setCurrentWidget(profiles);mark_applied(host,payload)
    payload['lcd']['file']='changed-after-apply'
    assert background.media_background.path==DESIGNS[-1].variants[0].video_path.resolve()
    pages.setCurrentWidget(other);sync(host)
    assert background.media_background.path==VIDEO_THEMES[background._theme]
    background._enabled=False;background.media_background.sync()
    assert not background.media_background.video._source_loaded
    assert background.media_background.video.player.source().isEmpty()
    background._enabled=True;background.media_background.sync()
    window.hide();background.media_background.sync()
    assert not background.media_background.video._source_loaded
    background.media_background.shutdown();window.deleteLater();app.processEvents()
