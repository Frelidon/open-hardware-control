# SPDX-License-Identifier: GPL-3.0-or-later
"""Real Qt flow drafts survive refresh; saved profile directions remain visible."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from modules.localization.v1_0 import UI_TRANSLATIONS
from modules.pc_case_profiles.v1_5.spatial_layout import CaseSpatialPanel
from modules.rgb_studio.v1_15.led_topology_store import DIRECTION_KEY, KEY, paths

APP = QApplication.instance() or QApplication([])
NO_PATH = ("Räumlicher Ablauf gespeichert. Bitte zuerst den LED-Verlauf am Anschluss festlegen; "
           "ohne ihn bleibt die Beleuchtung lokal.")


class Settings:
    def __init__(self):
        self.data = {"rgb_studio/speed": 66, DIRECTION_KEY: "local"}

    def value(self, key, default=None):
        return self.data.get(key, default)

    def setValue(self, key, value):
        self.data[key] = value

    def sync(self):
        pass


def build(language, distro, monkeypatch):
    calls = []
    host = SimpleNamespace(settings=Settings(), rgb_layout_slots=[],
                           ubuntu_runtime=distro == "ubuntu", rgb_last_effect_request_signature=("old",),
                           openrgb_write_enabled=False, rgb_selected_devices={"openrgb:synthetic"},
                           tr_static=lambda text: UI_TRANSLATIONS[language].get(text, text),
                           log_message=calls.append,
                           request_rgb_direct_apply=lambda **kwargs: calls.append(("apply", kwargs)))
    monkeypatch.setattr(CaseSpatialPanel, "_refresh_diagrams", lambda panel: panel.refresh())
    return host, CaseSpatialPanel(host), calls


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
@pytest.mark.parametrize("distro", ["ubuntu", "fedora"])
def test_refresh_keeps_unfinished_draft_but_reflects_changed_saved_profile(language, distro, monkeypatch):
    host, panel, _ = build(language, distro, monkeypatch)
    panel.flow_direction.setCurrentIndex(panel.flow_direction.findData("left-right"))
    panel.flow_speed.setValue(80)
    panel.refresh()
    assert panel.flow_direction.currentData() == "left-right" and panel.flow_speed.value() == 80
    # A loaded profile changes persisted intent; stale widgets must not overwrite it.
    host.settings.setValue(DIRECTION_KEY, "top-bottom")
    host.settings.setValue("rgb_studio/speed", 90)
    panel.refresh()
    assert panel.flow_direction.currentData() == "top-bottom" and panel.flow_speed.value() == 90
    panel.flow_direction.setCurrentIndex(panel.flow_direction.findData("bottom-top"))
    panel.refresh()
    assert panel.flow_direction.currentData() == "bottom-top"
    panel.close()


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
@pytest.mark.parametrize("distro", ["ubuntu", "fedora"])
def test_direction_without_declared_paths_is_saved_with_actionable_translated_status(language, distro, monkeypatch):
    host, panel, calls = build(language, distro, monkeypatch)
    panel.flow_direction.setCurrentIndex(panel.flow_direction.findData("left-right"))
    panel.save_flow()
    assert host.settings.value(DIRECTION_KEY) == "left-right" and paths(host) == {}
    assert panel.status.text() == UI_TRANSLATIONS[language][NO_PATH]
    assert "declared_paths=0" in calls[-1] and "settings-only" in calls[-1]
    assert not any(isinstance(item, tuple) for item in calls)  # Ownership gate remains closed.
    panel.close()


@pytest.mark.parametrize("distro", ["ubuntu", "fedora"])
def test_save_updates_only_declared_path_direction_and_preserves_topology(distro, monkeypatch):
    host, panel, calls = build("de", distro, monkeypatch)
    path = dict(kind="ring", start="top-left", end="bottom-right", units=3,
                clockwise=False, reverse_units=True, reverse_effect=True, direction="local")
    host.settings.setValue(KEY, json.dumps({"openrgb:synthetic": {"ARGB 1": path}}))
    panel.flow_direction.setCurrentIndex(panel.flow_direction.findData("right-left"))
    panel.flow_speed.setValue(75)
    panel.save_flow()
    assert paths(host) == {"openrgb:synthetic": {"ARGB 1": {**path, "direction": "right-left"}}}
    assert panel.status.text() == "Räumlicher Ablauf gespeichert."
    assert host.settings.value("rgb_studio/speed") == 75
    assert "declared_paths=1" in calls[-1]
    assert host.rgb_last_effect_request_signature is None
    panel.close()
    # Reconstruction reads persisted intent, with no write permission gained.
    rebuilt = CaseSpatialPanel(host)
    assert rebuilt.flow_direction.currentData() == "right-left" and rebuilt.flow_speed.value() == 75
    assert not host.openrgb_write_enabled
    rebuilt.close()


@pytest.mark.parametrize("invalid", ["bad", None, -1, 500])
def test_malformed_or_unbounded_speed_is_safe_in_ui_without_mutating_settings(invalid, monkeypatch):
    host, panel, _ = build("de", "ubuntu", monkeypatch)
    host.settings.setValue("rgb_studio/speed", invalid)
    panel.refresh()
    assert 10 <= panel.flow_speed.value() <= 200
    assert host.settings.value("rgb_studio/speed") == invalid
    panel.close()
