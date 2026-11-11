"""Original matrix loops, side-effect-free preview and existing-owner delegation."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from rgb_effects import BUILTIN_DESIGNS, render_effect
from modules.design_hub.v1_0.catalog import PAIRS, normalize_order
from modules.design_hub.v1_0.controller import apply_pair, resolve_pair
from modules.design_hub.v1_0.page import DesignHubPage
from modules.design_hub.v1_0.games import GAMES
from modules.design_automation.v1_0.model import AutomationRule, process_matches


def test_pairs_keep_existing_rgb_indices_and_lcd_asset_contract():
    assert [resolve_pair(pair)[0] for pair in PAIRS] == [34, 30, 31, 32, 33]
    for pair in PAIRS:
        _index, video = resolve_pair(pair)
        assert video.is_file() and video.with_suffix('.jpg').is_file()
    assert BUILTIN_DESIGNS[-1][1].effect_id == "code_rain"


@pytest.mark.parametrize("count", (1, 6, 8, 10, 30, 114, 512))
def test_matrix_periodicity_direction_brightness_and_real_motion(count):
    original = BUILTIN_DESIGNS[-1][1]
    for speed in (10, 100, 200):
        for direction in (-1, 1):
            config = replace(original, speed=speed, direction=direction)
            period = 12 * 100 / speed
            assert render_effect(config, count, .321) == render_effect(config, count, .321 + period)
            assert render_effect(config, count, 0) != render_effect(config, count, period * .31)
            before, after = [render_effect(config, count, period + delta) for delta in (-1e-6, 1e-6)]
            assert max(abs(a-b) for l,r in zip(before,after) for a,b in zip(l,r)) <= 1
    assert set(render_effect(replace(original, brightness=0), count, 1)) == {(0,0,0)}


def test_personal_order_migration_moves_only_the_new_section():
    old = ["settings", "lcd", "rgb_studio", "profiles", "automations"]
    new = normalize_order(old)
    assert [key for key in new if key != "design_hub"] == old
    assert new.index("design_hub") == new.index("rgb_studio") + 1
    assert normalize_order(new) == new


class FakeStudio:
    def __init__(self, calls):
        self.calls = calls
        self.layer2 = {"blocks": [{"metric": "cpu_temp", "x": 180}], "user_text": "own"}

    def select_bundled_effect_media(self, path, title): self.calls.append(("select-lcd", path, title))
    def stage_profile_startup_design(self): self.calls.append(("stage-lcd",))
    def apply_design(self): self.calls.append(("apply-lcd",))


def fake_host():
    calls = []
    return SimpleNamespace(
        calls=calls, thermalright_display_studio=FakeStudio(calls),
        feature_enabled=lambda key: True, is_thermalright_cooling=lambda: True,
        activate_rgb_design_tile=lambda index: calls.append(("rgb", index)),
    )


def test_pair_apply_delegates_once_and_preserves_the_sensor_layer():
    host = fake_host()
    layer2 = host.thermalright_display_studio.layer2.copy()
    status = apply_pair(host, PAIRS[0], "both")
    assert [call[0] for call in host.calls] == ["select-lcd", "rgb", "stage-lcd", "apply-lcd"]
    assert host.calls[1] == ("rgb", 34)
    assert host.thermalright_display_studio.layer2 == layer2
    assert "angefordert" in status


@pytest.mark.parametrize("target, expected", (("rgb", ["rgb"]), ("lcd", ["select-lcd", "stage-lcd", "apply-lcd"])))
def test_targets_can_be_applied_independently(target, expected):
    host = fake_host(); apply_pair(host, PAIRS[0], target)
    assert [call[0] for call in host.calls] == expected


def test_preflight_does_not_apply_half_a_pair_or_enable_features():
    host = fake_host(); host.is_thermalright_cooling = lambda: False
    assert "benötigt" in apply_pair(host, PAIRS[0], "both")
    assert not host.calls
    host = fake_host(); host.feature_enabled = lambda key: key != "lcd"
    assert "aktivieren" in apply_pair(host, PAIRS[0], "both")
    assert not host.calls


def test_game_basenames_match_proton_names_without_launcher_false_positives():
    for game in GAMES:
        rule = AutomationRule.from_mapping(dict(rule_id=game.ident, trigger="game", trigger_value=game.process))
        assert process_matches(rule, (game.process.casefold(),))
        assert not process_matches(rule, ("UbisoftConnect.exe", "REDprelauncher.exe", "steam"))


def test_qt_selection_is_hardware_free_and_hidden_preview_releases_decoder():
    app = QApplication.instance() or QApplication([])
    host = fake_host()
    host.tr_static = str
    host.make_module_hero = lambda _icon, title, _description: QLabel(title)
    page = DesignHubPage(host)
    page.resize(1100, 780)
    for pair in PAIRS:
        page.select(pair)
    assert not host.calls
    page.show(); QTest.qWait(120)
    assert page.preview.timer.isActive()
    page.hide(); app.processEvents()
    assert not page.preview.timer.isActive()
    assert not page.preview.video._source_loaded
    assert page.preview.video.player.source().isEmpty()
    assert not host.calls
    page.shutdown(); page.deleteLater(); app.processEvents()
