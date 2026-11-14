"""Exercise the packaged EDID through the watcher and read-only diagnostics."""
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from modules.hardware_fix.v1_0.profile import ASSET_ROOT, CORRECTED_EDID_SHA256
from modules.hardware_fix.v1_0 import runner


@pytest.fixture
def helpers(monkeypatch):
    monkeypatch.syspath_prepend(str(ASSET_ROOT / 'lib'))
    names = ('vrr_hardware', 'x11_games', 'auto_vrr', 'status')
    for name in names:
        monkeypatch.delitem(sys.modules, name, raising=False)
    loaded = SimpleNamespace(**{name: importlib.import_module(name) for name in names})
    yield loaded
    for name in names:
        sys.modules.pop(name, None)


@pytest.fixture
def connector(tmp_path):
    drm = tmp_path / 'drm'
    target = drm / 'card1-DP-2'
    target.mkdir(parents=True)
    (target / 'status').write_text('connected\n')
    (target / 'edid').write_bytes((ASSET_ROOT / 'EDID/vrr-korrigiert.bin').read_bytes())
    (target / 'connector_id').write_text('123\n')
    return drm, target


def test_all_readers_accept_the_actual_packaged_edid(helpers):
    assert helpers.vrr_hardware.PATCH == CORRECTED_EDID_SHA256
    assert helpers.x11_games.PATCH == CORRECTED_EDID_SHA256
    assert helpers.status.PATCH == CORRECTED_EDID_SHA256


def test_packaged_edid_maps_borderless_game_on_offset_monitor(helpers, connector, monkeypatch):
    drm, _ = connector
    module = helpers.x11_games
    monkeypatch.setattr(module, 'Path', lambda _: drm)
    calls = []
    def monitors(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(stdout='Monitors: 2\n 0: +*DP-2 2560/600x1440/330+1920+0  DP-2\n 1: +HDMI-2 1920/530x1080/300+0+360  HDMI-2\n')
    monkeypatch.setattr(module.subprocess, 'run', monitors)
    detector = module.GameWindows.__new__(module.GameWindows)
    detector._rects_at = -10.0
    detector._rects = []
    rects = detector.msi_rects()
    assert rects == [(1920, 0, 2560, 1440)]
    assert module.window_coverage([1920, 0, 2560, 1440], rects) == (True, True)
    assert module.window_coverage([0, 360, 1920, 1080], rects) == (False, False)
    assert module.window_coverage([1920, 0, 2560, 1440], rects, decorated=True) == (True, False)
    game = dict(window=7, pid=8, appid='3035570', geometry=[1920, 0, 2560, 1440], fullscreen=False, on_msi=True, covers_msi=True)
    pending = {}
    assert helpers.auto_vrr.ready_games([game], 7, pending, set(), 100) == []
    assert helpers.auto_vrr.ready_games([game], 7, pending, set(), 105) == [game]
    assert helpers.auto_vrr.ready_games([game], 9, pending, set(), 106) == []
    assert calls == [['xrandr', '--listmonitors']]


@pytest.mark.parametrize('value', [0, 1, None])
def test_actual_edid_reaches_crtc_read_and_preserves_unknown(helpers, connector, monkeypatch, value):
    drm, _ = connector
    module = helpers.vrr_hardware
    monkeypatch.setattr(module, 'Path', lambda _: drm)
    opened, closed, requested = [], [], []
    monkeypatch.setattr(module.os, 'open', lambda path, flags: opened.append((path, flags)) or 42)
    monkeypatch.setattr(module.os, 'close', closed.append)
    hardware = module.MSIVRR.__new__(module.MSIVRR)
    hardware.lib = SimpleNamespace(drmSetClientCap=lambda *args: 0)
    def properties(fd, obj, kind):
        requested.append((fd, obj, kind))
        return {'CRTC_ID': 437} if obj == 123 else ({} if value is None else {'VRR_ENABLED': value})
    hardware.props = properties
    assert hardware.value() == value
    assert opened == [('/dev/dri/card1', module.os.O_RDONLY)]
    assert closed == [42]
    assert requested == [(42, 123, 0xc0c0c0c0), (42, 437, 0xcccccccc)]


def test_unrecognized_edid_never_opens_drm(helpers, connector, monkeypatch):
    drm, target = connector
    (target / 'edid').write_bytes((ASSET_ROOT / 'EDID/original.bin').read_bytes())
    module = helpers.vrr_hardware
    monkeypatch.setattr(module, 'Path', lambda _: drm)
    def unexpected(*args):
        pytest.fail('Unrecognized EDID must not be used as a VRR target')
    monkeypatch.setattr(module.os, 'open', unexpected)
    hardware = module.MSIVRR.__new__(module.MSIVRR)
    assert hardware.value() is None


@pytest.mark.parametrize('family,script', [('ubuntu', '01-Installieren-Ubuntu.sh'), ('fedora', '01-Installieren-Fedora.sh')])
def test_distribution_install_paths_remain_separate(family, script):
    assert Path(runner._command('install', family)[1]).name == script
    assert runner._command('preflight', family)[-1] == '--check'


def test_fedora_still_rejects_ubuntu_automation(monkeypatch):
    monkeypatch.setattr(runner, 'os_family', lambda: 'fedora')
    monkeypatch.setattr(runner, 'validate_profile_assets', lambda: pytest.fail('Must reject before any job'))
    assert runner.main(['automation-install']) == 2
