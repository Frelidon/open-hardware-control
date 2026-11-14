"""Local setup contracts, correlated terminal results and translated Qt UI."""
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton
from shiboken6 import delete

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from modules.hardware_fix.v1_0 import page, runner, profile, status
from modules.hardware_fix.v1_0.workflow import install_local
from modules.localization.v1_0 import UI_TRANSLATIONS


def sample(**changes):
    values = dict(os_family='ubuntu', resources_valid=True, monitor_connectors=('card1-DP-2',),
                  monitor_original=False, corrected_edid_loaded=True, firmware_present=True,
                  firmware_valid=True, boot_parameter_running=True, boot_configuration_present=True,
                  automation_installed=True, automation_active=True, selected_provider='local',
                  actual_provider='local', reboot_required=False, detail='')
    values.update(changes)
    return status.HardwareFixStatus(**values)


@pytest.mark.parametrize('family,desktop,expected', [
    ('ubuntu', 'ubuntu:GNOME', ['desktop', 'automation-install']),
    ('ubuntu', 'KDE', []), ('fedora', 'GNOME', []), ('fedora', 'KDE', []),
])
def test_healthy_setup_keeps_distribution_and_desktop_paths(family, desktop, expected):
    calls = []
    assert install_local(family, desktop, sample, lambda action: calls.append(action) or 0) == (0, False)
    assert calls == expected


@pytest.mark.parametrize('family', ['ubuntu', 'fedora'])
def test_new_boot_install_waits_for_reboot_before_desktop_changes(family):
    calls = []
    states = iter([sample(firmware_valid=False, boot_configuration_present=False, corrected_edid_loaded=False),
                   sample(reboot_required=True, corrected_edid_loaded=False)])
    assert install_local(family, 'GNOME', lambda: next(states), lambda key: calls.append(key) or 0) == (0, True)
    assert calls == ['install']


def test_failed_desktop_setup_never_starts_automation():
    calls = []
    assert install_local('ubuntu', 'GNOME', sample, lambda key: calls.append(key) or 9) == (9, False)
    assert calls == ['desktop']


def test_failed_boot_install_stops_all_later_steps():
    calls = []
    assert install_local('ubuntu', 'GNOME', lambda: sample(firmware_valid=False), lambda key: calls.append(key) or 7) == (7, False)
    assert calls == ['install']


def test_job_argument_is_fixed_hex_only():
    assert profile.runner_argv('install-local', 'a' * 32)[-1] == 'a' * 32
    assert profile.runner_argv('install-local', '../bad') is None
    assert runner.main(['install-local', '../bad']) == 2


@pytest.mark.parametrize('family', ['ubuntu', 'fedora'])
def test_runner_writes_local_provider_before_final_status(tmp_path, monkeypatch, family):
    monkeypatch.setattr(runner, 'STATE_ROOT', tmp_path)
    monkeypatch.setattr(runner, 'os_family', lambda: family)
    monkeypatch.setattr(runner, 'inspect_status', sample)
    monkeypatch.setenv('XDG_CURRENT_DESKTOP', 'GNOME')
    def command(step, lane):
        assert lane == family
        assert family == 'ubuntu' and step in {'desktop', 'automation-install'}
        return [sys.executable, '-c', 'print("FERTIG: Ubuntu-Automatik installiert")']
    monkeypatch.setattr(runner, '_command', command)
    def inspect_after():
        assert json.loads((tmp_path / 'provider.json').read_text()) == {'selected': 'local', 'actual': 'local'}
        return '{}'
    monkeypatch.setattr(runner, 'status_json', inspect_after)
    job = 'b' * 32
    assert runner.main(['install-local', job]) == 0
    result = json.loads((tmp_path / 'last-result.json').read_text())
    assert result['job_id'] == job and result['success'] and result['finished']


def test_runner_records_spawn_failure_as_finished(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'STATE_ROOT', tmp_path)
    monkeypatch.setattr(runner, 'os_family', lambda: 'ubuntu')
    monkeypatch.setattr(runner, '_command', lambda *args: ['/definitely-not-an-ohc-executable'])
    assert runner.main(['status', 'c' * 32]) == 1
    result = json.loads((tmp_path / 'last-result.json').read_text())
    assert result['finished'] and result['success'] is False


@pytest.fixture
def panel(monkeypatch, tmp_path):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(page, 'STATE_ROOT', tmp_path)
    monkeypatch.setattr(page, 'inspect_status', sample)
    host = QWidget()
    widget = page.HardwareFixPanel(host, lambda text: text)
    widget.refresh_status()
    warnings = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args: warnings.append(args[-1]))
    yield widget, tmp_path, warnings
    delete(host)
    app.processEvents()


def test_finished_first_poll_is_accepted_and_stale_results_are_ignored(panel):
    widget, root, warnings = panel
    widget._job_id, widget._busy = 'd' * 32, True
    widget._started_at = page.time.monotonic()
    result = root / 'last-result.json'
    result.write_text(json.dumps(dict(job_id='e' * 32, finished=True, success=False)))
    widget._poll_result()
    assert widget._busy and warnings == []
    result.write_text(json.dumps(dict(job_id='d' * 32, finished=True, success=True)))
    widget._poll_result()
    assert not widget._busy and widget.activate_button.isEnabled() and warnings == []


def test_missing_or_malformed_job_has_bounded_wait(panel):
    widget, root, warnings = panel
    widget._job_id, widget._busy = 'd' * 32, True
    widget._started_at = page.time.monotonic() - 31
    (root / 'last-result.json').write_text('[]')
    widget._poll_result()
    assert not widget._busy and warnings


def test_second_click_cannot_start_another_terminal(panel, monkeypatch):
    widget, _, _ = panel
    widget._busy = True
    monkeypatch.setattr(page, 'terminal_spec', lambda *args: pytest.fail('No duplicate terminal'))
    widget._start_action('install-local')


def test_no_provider_picker_and_two_primary_actions_in_four_languages(panel):
    widget, _, _ = panel
    assert not hasattr(widget, 'provider_combo')
    assert not widget.technical.button.isChecked()
    for code in ('de', 'en', 'es', 'fr'):
        widget.translate = lambda source, lane=code: UI_TRANSLATIONS[lane].get(source, source)
        widget.refresh_language()
        for obj, source in widget._texts:
            if source:
                assert source in UI_TRANSLATIONS[code], (code, source)
                assert obj.text() == UI_TRANSLATIONS[code][source]
        assert widget.activate_button.text() == UI_TRANSLATIONS[code]['Installieren']
        assert widget.uninstall_button.text() == UI_TRANSLATIONS[code]['Deinstallieren']
        assert 'Ubuntu' in widget.details.text()


def test_parameter_matching_is_exact_and_provider_metadata_is_bounded(tmp_path, monkeypatch):
    p = tmp_path / 'cmdline'
    p.write_text('x=' + profile.KERNEL_PARAMETER + '-other')
    assert not status._contains_parameter(p)
    p.write_text('GRUB_CMDLINE_LINUX_DEFAULT="quiet ' + profile.KERNEL_PARAMETER + '"')
    assert status._contains_parameter(p)
    monkeypatch.setattr(status, 'STATE_ROOT', tmp_path)
    (tmp_path / 'provider.json').write_text('[]')
    assert status._provider_metadata() == ('local', 'local')


def test_saved_active_gnome_vrr_does_not_apply_display_configuration(monkeypatch, tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('ohc_desktop_fix', profile.ASSET_ROOT / 'lib/desktop.py')
    desktop = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(desktop)
    monkeypatch.setattr(desktop.os, 'geteuid', lambda: 1000)
    monkeypatch.setattr(desktop, 'persisted_vrr', lambda path: True)
    monkeypatch.setattr(desktop.time, 'sleep', lambda _: pytest.fail('No 35-second display reset'))
    state = (1, [(('DP-2', 'MSI', 'MAG 274 X30MV', ''),
                 [('2560x1440@300+vrr', 2560, 1440, 300., 1., [1.], {'is-current': True, 'refresh-rate-mode': 'variable'})], {})], [], {})
    calls = []
    def call(*args):
        calls.append(args[3])
        assert args[3] == 'GetCurrentState'
        return SimpleNamespace(unpack=lambda: state)
    gi = SimpleNamespace(Gio=SimpleNamespace(bus_get_sync=lambda *a: SimpleNamespace(call_sync=call),
                                           BusType=SimpleNamespace(SESSION=0), CallFlags=SimpleNamespace(NONE=0),
                                           DBusCallFlags=SimpleNamespace(NONE=0)), GLib=SimpleNamespace(Error=RuntimeError))
    monkeypatch.setitem(sys.modules, 'gi.repository', gi)
    desktop.main()
    assert calls == ['GetCurrentState']
