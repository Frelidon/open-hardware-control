"""Complete portable configuration and declared LED paths, no real hardware."""
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

import pytest
from PySide6.QtCore import QByteArray, QPoint, QRect, QSettings, QSize
from PySide6.QtWidgets import QSpinBox
from test_slot_argb_routes_342985 import APP, Host, HUB
from localization_catalog import UI_TRANSLATIONS
from rgb_effects import EFFECTS, RGBEffectConfig, render_hex_frame
from modules.profile_bundle.v1_0 import archive
from modules.profile_bundle.v1_0.restore import PENDING_KEY, lcd_store_root, restore_pending, safety_settings
from modules.profile_bundle.v1_0.values import decode, encode
from modules.rgb_studio.v1_15.gpu_routing import render_zone_frame
from modules.rgb_studio.v1_15.led_topology import normalize_path, path_points, projected_coordinate, render_physical_frame
from modules.rgb_studio.v1_15.led_topology_editor import LedTopologyEditor, MOVEMENT_LABELS, POINT_LABELS, UNIT_ORDER_LABELS
from modules.rgb_studio.v1_15.led_topology_store import KEY, DIRECTION_KEY, paths, direction

PATH = dict(kind="line", start="top", end="bottom", units=1, clockwise=True)


def package_snapshot(tmp_path):
    media = tmp_path / "media"
    media.mkdir()
    (media / "image.png").write_bytes(b"synthetic image content")
    (media / "video.mp4").write_bytes(b"synthetic video content")
    theme = media / "theme"
    theme.mkdir()
    (theme / "config1.dc").write_bytes(b"unchanged original layout")
    (theme / "trcc.json").write_text(json.dumps({"video": str(media / "video.mp4")}), encoding="utf-8")
    lcd = tmp_path / "lcd-profiles"
    lcd.mkdir()
    (lcd / "profiles.json").write_text(json.dumps({"profiles": [{"media": str(media / "image.png")}]}))
    values = {
        "rgb_studio/zone_configurations": json.dumps({"openrgb:hub": {"Channel B7": {"units": 3, "leds_per_unit": 8}}}),
        "rgb_studio/fan_library_v1": json.dumps([dict(brand="Own", model="Fan", color="black", leds_per_fan=8)]),
        "rgb_studio/layout_slots": json.dumps([dict(slot_id="bottom", x=.2, y=.8, scale=.7)]),
        "mainboard_fans/layout_assignments": json.dumps({"nct6687:pwm8": "bottom"}),
        "mainboard_fans/profiles": json.dumps({"nct6687:pwm8": dict(calibrated=True, enabled=True, curve=[[30, 25], [90, 100]])}),
        "mainboard_fans/master_enabled": True, "profiles/startup": "saved", "thermalright/test_mode": False,
        KEY: json.dumps({"openrgb:hub": {"Channel B7": {**PATH, "kind": "ring", "units": 3, "reverse_units": True}}}), DIRECTION_KEY: "top-bottom",
        "rgb_studio/gpu_support_sync_v1": False,
        "thermalright/media_directory": str(media),
        "thermalright/overrides": json.dumps({str(theme): {"media": str(media / "video.mp4")}}),
        "window/geometry": QByteArray(b"qt geometry\x00"), "display/size": QSize(1280, 720),
    }
    profile = dict(id="user-saved", name="Saved", payload={"lcd": {"file": str(media / "image.png")}})
    return dict(settings={k: encode(v) for k, v in values.items()}, profiles=[profile], lcd_store=str(lcd)), media, lcd


def test_supported_settings_types_are_lossless_and_reject_unsafe_values():
    values = [None, True, 13, 1.25, "utf8 ä", [1, "a"], (1, 2), {"t": "bytes", "v": "literal"},
              b"data\x00", QByteArray(b"qt\x00"), QPoint(5, 6), QSize(1280, 720), QRect(1, 2, 3, 4)]
    for value in values:
        assert decode(json.loads(json.dumps(encode(value)))) == value
    for value in (float("nan"), float("inf"), object()):
        with pytest.raises(ValueError): encode(value)
    with pytest.raises(ValueError): decode({"t": "arbitrary-command", "v": "bad"})
    with pytest.raises(ValueError): decode({"t": "QSize", "v": [2 ** 40, 1]})


def test_complete_package_roundtrip_files_paths_geometry_models_and_safe_startup_restore(tmp_path):
    snapshot, media, lcd = package_snapshot(tmp_path)
    original = copy.deepcopy(snapshot)
    output = tmp_path / "complete.zip"
    result = archive.export_bundle(output, snapshot, [lcd])
    assert result["files"] == 5 and not result["missing"]
    assert snapshot == original
    config = tmp_path / "config"
    base = config / "profile-imports"
    base.mkdir(parents=True)
    stage = base / "package-test"
    imported = archive.import_bundle(output, stage)
    ready = json.loads((stage / "ready.json").read_text())
    values = {k: decode(v) for k, v in ready["settings"].items()}
    assert values["rgb_studio/layout_slots"] == decode(original["settings"]["rgb_studio/layout_slots"])
    assert values[KEY] == decode(original["settings"][KEY])
    assert values["rgb_studio/fan_library_v1"] == decode(original["settings"]["rgb_studio/fan_library_v1"])
    new_media = Path(values["thermalright/media_directory"])
    assert new_media.is_relative_to(stage) and (new_media / "video.mp4").read_bytes() == b"synthetic video content"
    override = json.loads(values["thermalright/overrides"])
    assert str(new_media / "theme") in override
    assert json.loads((new_media / "theme/trcc.json").read_text())["video"] == str(new_media / "video.mp4")
    assert (new_media / "theme/config1.dc").read_bytes() == b"unchanged original layout"
    settings = QSettings(str(config / "settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("previous", 42)
    (config / "profiles.json").write_text('{"schema":1,"profiles":[]}')
    settings.setValue(PENDING_KEY, json.dumps(imported))
    assert restore_pending(settings, config) == "restored"
    assert not settings.contains("previous")
    assert settings.value("window/geometry") == QByteArray(b"qt geometry\x00")
    assert settings.value("mainboard_fans/master_enabled", type=bool) is False
    fan = json.loads(settings.value("mainboard_fans/profiles"))["nct6687:pwm8"]
    assert fan["curve"] == [[30, 25], [90, 100]] and not fan["enabled"] and not fan["calibrated"]
    assert settings.value("profiles/startup") == "none"
    assert settings.value("cooling/pump_mode") == "unbekannt"
    assert settings.value("safety/auto_max", type=bool) is False
    assert settings.value("thermalright/test_mode", type=bool)
    assert settings.value(DIRECTION_KEY) == "top-bottom"
    assert settings.value("rgb_studio/gpu_support_sync_v1", type=bool) is False
    assert json.loads(settings.value(KEY))["openrgb:hub"]["Channel B7"]["reverse_units"] is True
    assert json.loads((config / "profiles.json").read_text())["profiles"][0]["id"] == "user-saved"
    rollback = Path(settings.value("profile_bundle/rollback_v1"))
    assert decode(json.loads((rollback / "settings.json").read_text())["previous"]) == 42
    assert (rollback / "profiles.json").read_text() == '{"schema":1,"profiles":[]}'
    assert lcd_store_root(settings, config) == Path(ready["lcd_store"])
    assert restore_pending(settings, config) is None


def test_atomic_export_limits_empty_roots_missing_media_and_local_cache_links(tmp_path, monkeypatch):
    snap, media, lcd = package_snapshot(tmp_path)
    cached = media / "cached.png"
    cached.symlink_to(media / "image.png")
    empty = tmp_path / "empty"
    empty.mkdir()
    snap["settings"]["empty"] = str(empty)
    snap["settings"]["missing"] = str(media / "missing.png")
    out = tmp_path / "package.zip"
    result = archive.export_bundle(out, snap, [lcd])
    assert result["missing"] == [str(media / "missing.png")]
    stage = tmp_path / "stage"
    archive.import_bundle(out, stage)
    ready = json.loads((stage / "ready.json").read_text())
    assert Path(ready["settings"]["empty"]).is_dir()
    imported_media = Path(ready["settings"]["thermalright/media_directory"])
    assert not (imported_media / "cached.png").is_symlink()
    assert (imported_media / "cached.png").read_bytes() == (media / "image.png").read_bytes()
    previous = out.read_bytes()
    monkeypatch.setattr(archive, "MAX_FILE", 4)
    with pytest.raises(ValueError): archive.export_bundle(out, snap)
    assert out.read_bytes() == previous


@pytest.mark.parametrize("case", ["traversal", "absolute", "backslash", "unlisted", "symlink", "checksum", "duplicate", "bad-setting"])
def test_untrusted_packages_fail_closed_without_live_changes(tmp_path, case):
    snap, media, lcd = package_snapshot(tmp_path)
    valid = tmp_path / "valid.zip"
    archive.export_bundle(valid, snap, [lcd])
    with zipfile.ZipFile(valid) as inp:
        members = [(i, inp.read(i)) for i in inp.infolist()]
    first = members[0][0].filename
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as out:
        for info, data in members:
            if info.filename == first and case == "checksum": data = b"changed" + data[7:]
            if info.filename == first and case == "symlink": info.external_attr = (stat.S_IFLNK | 0o777) << 16
            if info.filename == "manifest.json" and case == "bad-setting":
                manifest = json.loads(data); manifest["snapshot"]["settings"]["evil"] = {"t": "command", "v": "bad"}
                data = json.dumps(manifest).encode()
            out.writestr(info, data)
        if case in {"traversal", "absolute", "backslash", "unlisted", "duplicate"}:
            name = {"traversal": "../escape.json", "absolute": "/escape.json", "backslash": "assets\\escape.json",
                    "unlisted": "extra.py", "duplicate": first}[case]
            out.writestr(name, b"bad")
    before = copy.deepcopy(snap)
    with pytest.raises((ValueError, KeyError)): archive.import_bundle(bad, tmp_path / "unsafe-stage")
    assert not (tmp_path / "unsafe-stage").exists() and snap == before
    assert not (tmp_path / "escape.json").exists()


def test_tampered_ready_snapshot_retains_settings_and_untrusted_lcd_override(tmp_path):
    config = tmp_path / "config"; base = config / "profile-imports"; stage = base / "package-test"
    stage.mkdir(parents=True)
    (stage / "ready.json").write_text("{}")
    settings = QSettings(str(config / "settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("previous", 42)
    settings.setValue(PENDING_KEY, json.dumps(dict(stage=str(stage), sha256="0" * 64)))
    assert restore_pending(settings, config) == "failed" and settings.value("previous") == 42
    settings.setValue("profile_bundle/lcd_store_v1", str(tmp_path))
    assert lcd_store_root(settings, config) == config / "lcd-profiles"


def test_led_coordinates_reverse_ring_numbering_diagonal_projection_and_bad_values():
    points = path_points(PATH, 30)
    assert points[0] == (.5, 0) and points[-1] == (.5, 1) and len(points) == 30
    reverse = {**PATH, "start": "bottom", "end": "top"}
    for actual, expected in zip(path_points(reverse, 30), reversed(points), strict=True):
        assert actual == pytest.approx(expected)
    ring = {**PATH, "kind": "ring", "units": 3}
    cw, ccw = path_points(ring, 24), path_points({**ring, "clockwise": False}, 24)
    assert len(cw) == 24 and cw[0] == pytest.approx(ccw[0]) and cw[1][0] > cw[0][0] > ccw[1][0]
    for i in range(24): assert 0 <= cw[i][0] <= 1 and 0 <= cw[i][1] <= 1
    assert projected_coordinate((0, 0), "top-left-bottom-right") == 0
    assert projected_coordinate((1, 1), "top-left-bottom-right") == 1
    assert projected_coordinate((1, 0), "top-right-bottom-left") == 0
    for bad in (None, [], {**PATH, "start": []}, {**PATH, "units": True}, {**PATH, "clockwise": 1}, {**PATH, "end": "top"}):
        assert normalize_path(bad) is None
    with pytest.raises(ValueError): path_points(ring, 25)


@pytest.mark.parametrize("effect", [e.effect_id for e in EFFECTS])
def test_all_effects_keep_exact_counts_legacy_frames_and_physical_direction(effect):
    config = RGBEffectConfig(effect_id=effect)
    for count in (1, 8, 12, 16, 24, 30, 80, 512):
        legacy = render_hex_frame(config, count, .37)
        assert render_physical_frame(config, count, .37, PATH) == legacy
        down = render_physical_frame(config, count, .37, PATH, "top-bottom")
        up = render_physical_frame(config, count, .37, {**PATH, "start": "bottom", "end": "top"}, "top-bottom")
        assert len(down) == count and up == down[::-1]
    result = render_zone_frame(config, 38, [30, 8], ["GPU", "Fan"], {}, .37, paths={"GPU": PATH}, direction="top-bottom")
    assert result[30:] == render_hex_frame(config, 8, .37)


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
def test_led_editor_localized_save_cancel_and_invalid_counts_without_hardware(language):
    host = Host(language=language)
    count, index = QSpinBox(host), QSpinBox(host)
    count.setRange(1, 512); count.setValue(24); index.setValue(1)
    editor = LedTopologyEditor(host, HUB, "Channel A1", count, index, 3)
    assert editor.group.title() == UI_TRANSLATIONS[language]["LED-Verlauf"]
    assert not editor.group.isChecked() and paths(host) == {} and host.calls == []
    for combo, captions in ((editor.start, POINT_LABELS), (editor.movement, MOVEMENT_LABELS), (editor.unit_order, UNIT_ORDER_LABELS)):
        for i in range(combo.count()): assert combo.itemText(i) == UI_TRANSLATIONS[language][captions[combo.itemData(i)]]
    editor.group.setChecked(True)
    editor.start.setCurrentIndex(editor.start.findData("top")); editor.end.setCurrentIndex(editor.end.findData("bottom"))
    editor.movement.setCurrentIndex(editor.movement.findData("top-bottom"))
    before = copy.deepcopy(host.rgb_zone_configurations)
    assert editor.commit() and paths(host)["openrgb:hub"]["Channel A1"]["start"] == "top"
    assert paths(host)["openrgb:hub"]["Channel A1"]["direction"] == "top-bottom"
    assert direction(host) == "local" and host.rgb_zone_configurations == before and host.calls == []
    editor.kind.setCurrentIndex(editor.kind.findData("ring")); count.setValue(25)
    saved = copy.deepcopy(host.settings.data)
    assert not editor.commit() and host.settings.data == saved
    count.setValue(24)
    editor.unit_order.setCurrentIndex(editor.unit_order.findData(True))
    editor.reverse_effect.setChecked(True)
    assert editor.commit() and paths(host)["openrgb:hub"]["Channel A1"]["reverse_units"] is True
    assert paths(host)["openrgb:hub"]["Channel A1"]["reverse_effect"] is True
    reopened = LedTopologyEditor(host, HUB, "Channel A1", count, index, 3)
    assert reopened.unit_order.currentData() is True
    assert reopened.reverse_effect.isChecked()
    if os.environ.get("OHC_UI_RENDER_DIR"):
        editor.resize(600, 520); editor.show(); APP.processEvents()
        assert editor.grab().save(str(Path(os.environ["OHC_UI_RENDER_DIR"]) / f"led-path-{language}.png"))
    host.close()


def test_each_fan_gpu_and_support_header_keeps_its_own_case_direction():
    host = Host()
    host.settings.setValue(DIRECTION_KEY, "local")
    count, index = QSpinBox(host), QSpinBox(host)
    count.setRange(1, 512); count.setValue(24); index.setValue(1)

    vertical = LedTopologyEditor(host, HUB, "Channel A1", count, index, 3)
    vertical.group.setChecked(True)
    vertical.kind.setCurrentIndex(vertical.kind.findData("ring"))
    vertical.movement.setCurrentIndex(vertical.movement.findData("top-bottom"))
    assert vertical.commit()

    horizontal = LedTopologyEditor(host, HUB, "Channel B6", count, index, 3)
    horizontal.group.setChecked(True)
    horizontal.kind.setCurrentIndex(horizontal.kind.findData("ring"))
    horizontal.movement.setCurrentIndex(horizontal.movement.findData("left-right"))
    assert horizontal.commit()

    saved = paths(host)["openrgb:hub"]
    assert saved["Channel A1"]["direction"] == "top-bottom"
    assert saved["Channel B6"]["direction"] == "left-right"
    assert direction(host) == "local"  # The legacy fallback was not overwritten.
    reopened = LedTopologyEditor(host, HUB, "Channel A1", count, index, 3)
    assert reopened.movement.currentData() == "top-bottom"

    # These two native popup controls used to repaint while their selection
    # was transitional. Exercise both repeatedly on a visible offscreen UI.
    reopened.show(); APP.processEvents()
    for clockwise, reverse_units in ((False, True), (True, False), (False, False), (True, True)):
        reopened.clockwise.setCurrentIndex(reopened.clockwise.findData(clockwise))
        reopened.unit_order.setCurrentIndex(reopened.unit_order.findData(reverse_units))
        APP.processEvents()
    assert reopened.preview.grab().size().width() > 0
    host.close()


def test_case_fan_count_preserves_layout_choice_and_defaults_new_paths_to_row():
    host = Host()
    host.log_message = host.calls.append
    host.settings.setValue(KEY, json.dumps({"openrgb:hub": {
        "Channel A1": {**PATH, "start": "left", "end": "right"},
    }}))
    count, index = QSpinBox(host), QSpinBox(host)
    count.setRange(1, 512); count.setValue(24); index.setValue(1)
    editor = LedTopologyEditor(host, HUB, "Channel A1", count, index, 3, fan_units=3)
    assert editor.kind.currentData() == "line"
    assert editor.units.value() == 3
    assert editor.commit()
    saved = paths(host)["openrgb:hub"]["Channel A1"]
    assert saved["kind"] == "line" and saved["units"] == 3
    assert any("layout=Reihe" in line and "fan_count=3" in line and "leds_per_fan=8" in line
               for line in host.calls)

    editor.kind.setCurrentIndex(editor.kind.findData("ring"))
    assert editor.commit()
    reopened = LedTopologyEditor(host, HUB, "Channel A1", count, index, 3, fan_units=3)
    assert reopened.kind.currentData() == "ring"
    assert reopened.units.value() == 3
    assert "layout=Ring" in host.calls[-1] and "total_leds=24" in host.calls[-1]

    fresh = LedTopologyEditor(host, HUB, "Channel B6", count, index, 3, fan_units=3)
    assert fresh.kind.currentData() == "line"
    assert fresh.units.value() == 3
    host.close()


@pytest.mark.parametrize("horizontal", [True, False])
@pytest.mark.parametrize("count", [24, 30])
def test_reversed_fan_chain_preserves_each_ring_and_physical_numbering(horizontal, count):
    ring = {**PATH, "kind": "ring", "units": 3}
    old = path_points(ring, count, horizontal)
    reversed_path = {**ring, "reverse_units": True}
    new = path_points(reversed_path, count, horizontal)
    per_ring = count // 3
    assert new == old[2 * per_ring:] + old[per_ring:2 * per_ring] + old[:per_ring]
    axis = 0 if horizontal else 1
    assert new[0][axis] > new[-1][axis]
    assert normalize_path({**ring, "reverse_units": False}) == ring
    for invalid in (None, 1, "true", []):
        assert normalize_path({**ring, "reverse_units": invalid}) is None
        assert normalize_path({**ring, "reverse_effect": invalid}) is None
    for effect in EFFECTS:
        config = RGBEffectConfig(effect_id=effect.effect_id)
        direction = "left-right" if horizontal else "top-bottom"
        old_frame = render_physical_frame(config, count, .37, ring, direction, horizontal=horizontal)
        new_frame = render_physical_frame(config, count, .37, reversed_path, direction, horizontal=horizontal)
        assert new_frame == old_frame[2 * per_ring:] + old_frame[per_ring:2 * per_ring] + old_frame[:per_ring]


def test_per_component_animation_reverse_keeps_physical_led_numbering():
    config = RGBEffectConfig(effect_id="comet", primary="002244", secondary="ffffff")
    path = dict(kind="line", start="top", end="bottom", units=1, clockwise=True)
    points = path_points(path, 24, horizontal=False)
    forward = render_physical_frame(config, 24, .8, path, "top-bottom", horizontal=False)
    reverse = render_physical_frame(
        config, 24, .8, {**path, "reverse_effect": True}, "top-bottom", horizontal=False,
    )
    assert path_points({**path, "reverse_effect": True}, 24, horizontal=False) == points
    assert reverse == forward[::-1]


@pytest.mark.parametrize("case", ["unsupported", "file-directory", "file-parent", "duplicate-directory"])
def test_manifest_asset_types_and_path_conflicts_are_rejected_before_staging(tmp_path, case):
    data = b"synthetic content"
    name = "assets/theme/data.py" if case == "unsupported" else "assets/theme/data.json"
    record = dict(path=name, size=len(data), sha256=hashlib.sha256(data).hexdigest())
    directories = {"unsupported": [], "file-directory": [name], "file-parent": [name + "/child"],
                   "duplicate-directory": ["assets/theme", "assets/theme"]}[case]
    manifest = dict(format=archive.FORMAT, schema=1, snapshot=dict(settings={}, profiles=[]),
                    files=[record], directories=directories, references={})
    source = tmp_path / "invalid.zip"
    with zipfile.ZipFile(source, "w") as output:
        output.writestr(name, data)
        output.writestr("manifest.json", json.dumps(manifest))
    with pytest.raises(ValueError): archive.import_bundle(source, tmp_path / "stage")
    assert not (tmp_path / "stage").exists()


def test_owned_file_worker_cli_roundtrip_and_rejects_other_actions(tmp_path):
    state, _, lcd = package_snapshot(tmp_path)
    worker = Path(archive.__file__).with_name("worker.py")
    spec = tmp_path / "job.json"
    out, stage = tmp_path / "complete.zip", tmp_path / "stage"
    jobs = [dict(action="export", path=str(out), snapshot=state, extra_roots=[str(lcd)]),
            dict(action="import", path=str(out), stage=str(stage)), dict(action="arbitrary-command")]
    for i, job in enumerate(jobs):
        spec.write_bytes(archive.json_bytes(job))
        completed = subprocess.run([sys.executable, str(worker), str(spec)], capture_output=True,
                                   text=True, timeout=15, env={**os.environ, "OHC_DISABLE_HARDWARE_IO": "1"})
        answer = json.loads(completed.stdout)
        assert completed.returncode == (1 if i == 2 else 0)
        assert answer["ok"] is (i != 2)
    assert (stage / "ready.json").is_file()


def test_imported_settings_do_not_inherit_package_coordinator_or_hardware_authority():
    incoming = {PENDING_KEY: "foreign", "profile_bundle/lcd_store_v1": "/tmp/foreign",
                "profile_bundle/rollback_v1": "/tmp/foreign", "cooling/pump_mode": "CPU-Temperaturkurve",
                "safety/auto_max": True, "rgb_studio/auto_reclaim": True, "thermalright/autostart_enabled": True,
                "cooling/pump_curve": "keep curve", KEY: "keep physical path"}
    before = dict(incoming)
    safe = safety_settings(incoming)
    assert incoming == before and not any(k.startswith("profile_bundle/") for k in safe)
    assert safe["cooling/pump_mode"] == "unbekannt" and safe["cooling/pump_curve"] == "keep curve"
    assert not safe["safety/auto_max"] and not safe["rgb_studio/auto_reclaim"] and not safe["thermalright/autostart_enabled"]
    assert safe[KEY] == "keep physical path"


def test_path_settings_reject_invalid_counts_without_mutation():
    from modules.rgb_studio.v1_15.led_topology_store import remember_path
    host = Host()
    for count in (True, 0, -1, 4097, "30"):
        assert not remember_path(host, "openrgb:hub", "Channel A1", PATH, "top-bottom", count)
    assert paths(host) == {} and host.calls == []
    host.close()
