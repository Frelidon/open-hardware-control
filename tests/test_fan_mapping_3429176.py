"""Run production calibration methods on synthetic hwmon, never real hardware."""
import ast
import math
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace, MethodType
from unittest.mock import Mock
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from PySide6.QtWidgets import QApplication, QMessageBox
import mainboard_fan_control as fan
from modules.fan_mapping.v1_0 import runtime, lighting

APP=QApplication.instance() or QApplication([])


@pytest.fixture
def host(tmp_path):
    channels=[]
    for i in (3,4):
        pwm=tmp_path/f'pwm{i}'; enable=tmp_path/f'pwm{i}_enable';rpm=tmp_path/f'fan{i}_input'
        pwm.write_text('170\n');enable.write_text('1\n');rpm.write_text('900\n')
        label=tmp_path/f'fan{i}_label';label.write_text(f'SYS_FAN{i}')
        channels.append(fan.FanChannel(i,tmp_path,'nct6687',pwm,enable,rpm,label_path=label))
    (tmp_path/'fan_control_watchdog').write_text('0\n')
    saved={c.stable_id:{'name':c.display_name,'enabled':False,'calibrated':False,'curve':[[30,25],[80,100]]} for c in channels}
    label=SimpleNamespace(setText=Mock())
    h=SimpleNamespace(mainboard_channels={c.stable_id:c for c in channels},mainboard_hwmon_controller=fan.HwmonController(tmp_path,'nct6687',channels),
        mainboard_fan_profiles=saved,mainboard_control_active=False,mainboard_calibration_channel_id='',
        mainboard_assistant_contrast_requested=True,mainboard_selected_channel_id=channels[0].stable_id,
        mainboard_calibration_timer=SimpleNamespace(start=Mock(),stop=Mock()),
        mainboard_calibration_sample_timer=SimpleNamespace(start=Mock(),stop=Mock()),
        mainboard_runtime_status=label,footer_status=label,cooling_owner_status=SimpleNamespace(coolercontrol_active=False),
        current_cpu_temp=45,current_gpu_temp=50,fan_backend_write_ready=lambda:True,
        refresh_cooling_ownership_status=Mock(),is_thermalright_cooling=lambda:False,
        save_selected_mainboard_fan_profile=Mock(),save_mainboard_fan_settings=Mock(),
        refresh_mainboard_fan_table=Mock(),update_thermalright_cooling_ui=Mock(),log_message=Mock(),show_error=Mock(),
        tr_static=lambda text:text,mainboard_layout_assignments={},refresh_chassis_assistant_summary=Mock(),assistant_continue_with_next_fan=Mock())
    h.selected_mainboard_channel=lambda:h.mainboard_channels[h.mainboard_selected_channel_id]
    h.chassis_mainboard_channels=lambda:channels
    h.mainboard_profile_for=lambda c:saved[c.stable_id]
    names=['start_mainboard_fan_calibration','sample_mainboard_fan_calibration','finish_mainboard_fan_calibration']
    tree=ast.parse((ROOT/'src/kraken_control.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='KrakenControl')
    nodes=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in names]
    ns=dict(os=os,math=math,time=time,MainboardFanWriteError=fan.FanWriteError,
        mainboard_channel_is_chassis_fan=fan.channel_is_chassis_fan,mainboard_channel_can_control=fan.channel_can_control,
        mainboard_channel_control_method=fan.channel_control_method,snapshot_mainboard_channel=fan.snapshot_channel,
        set_mainboard_fan_watchdog=fan.set_fan_control_watchdog,set_mainboard_channel_percent=fan.set_channel_percent,
        restore_mainboard_snapshot=fan.restore_snapshot,disarm_mainboard_fan_watchdog=fan.disarm_fan_control_watchdog,
        QMessageBox=SimpleNamespace(StandardButton=QMessageBox.StandardButton,warning=lambda *a:QMessageBox.StandardButton.Yes,
                                    question=lambda *a:QMessageBox.StandardButton.Yes))
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<production-calibration>','exec'),ns)
    for name in names:setattr(h,name,MethodType(ns[name],h))
    h._globals=ns;h._channels=channels
    return h


def test_two_minute_stop_has_short_lease_and_cancel_restores_all_contrast_channels(host):
    before=[fan.snapshot_channel(c) for c in host._channels]
    host.start_mainboard_fan_calibration(stop_test=True)
    assert host.mainboard_calibration_timer.start.call_args.args==(120000,)
    assert (host.mainboard_hwmon_controller.path/'fan_control_watchdog').read_text().strip()=='10'
    assert int(host._channels[0].pwm_path.read_text())==0
    assert int(host._channels[1].pwm_path.read_text())==fan.percent_to_pwm(45)
    runtime.cancel_test(host)
    assert [fan.snapshot_channel(c) for c in host._channels]==before
    assert not host.mainboard_calibration_channel_id
    host.mainboard_calibration_timer.stop.assert_called_once()
    assert not any(p['calibrated'] for p in host.mainboard_fan_profiles.values())


def test_regular_speed_test_keeps_its_ten_second_duration(host):
    host.start_mainboard_fan_calibration()
    assert host.mainboard_calibration_timer.start.call_args.args==(10000,)
    runtime.cancel_test(host)


def test_no_watchdog_refuses_long_stop_before_any_pwm_write(host):
    (host.mainboard_hwmon_controller.path/'fan_control_watchdog').unlink()
    before=[fan.snapshot_channel(c) for c in host._channels]
    host.start_mainboard_fan_calibration(stop_test=True)
    assert [fan.snapshot_channel(c) for c in host._channels]==before
    assert not host.mainboard_calibration_channel_id
    host.show_error.assert_called_once()


@pytest.mark.parametrize('temperature',[None,float('nan'),90,110])
def test_missing_or_critical_cpu_refuses_long_stop(host,temperature):
    host.current_cpu_temp=temperature
    before=[fan.snapshot_channel(c) for c in host._channels]
    host.start_mainboard_fan_calibration(stop_test=True)
    assert [fan.snapshot_channel(c) for c in host._channels]==before
    host.show_error.assert_called_once()


def test_partial_target_write_failure_rolls_back_every_changed_channel(host):
    real=host._globals['set_mainboard_channel_percent'];before=[fan.snapshot_channel(c) for c in host._channels]
    def fail_after_write(c,percent):
        real(c,percent)
        if percent==0:raise fan.FanWriteError('injected target failure')
    host._globals['set_mainboard_channel_percent']=fail_after_write
    host.start_mainboard_fan_calibration(stop_test=True)
    assert [fan.snapshot_channel(c) for c in host._channels]==before
    assert not host.mainboard_calibration_channel_id


def test_lease_refresh_failure_restores_before_any_later_rpm_sample(host,monkeypatch):
    before=[fan.snapshot_channel(c) for c in host._channels]
    host.start_mainboard_fan_calibration(stop_test=True)
    host.fan_stop_lease_refreshed=0
    monkeypatch.setattr(runtime,'set_fan_control_watchdog',lambda *a:False)
    host.sample_mainboard_fan_calibration()
    assert [fan.snapshot_channel(c) for c in host._channels]==before
    assert not host.mainboard_calibration_channel_id


def test_explicit_disconnected_choice_retains_curve_and_removes_active_assignment(host):
    channel=host._channels[0];profile=host.mainboard_profile_for(channel);curve=list(profile['curve'])
    assert not runtime.disconnected(host,channel)  # Zero alone is never a classification.
    channel.rpm=0;assert not runtime.disconnected(host,channel)
    host.mainboard_layout_assignments[channel.stable_id]='front'
    runtime.mark_disconnected(host)
    assert profile['connection']=='disconnected' and profile['enabled'] is False and profile['calibrated'] is False
    assert profile['curve']==curve and channel.stable_id not in host.mainboard_layout_assignments
    host.assistant_continue_with_next_fan.assert_called_once()


def test_wizard_cancel_and_page_change_restore_running_stop(host):
    before=[fan.snapshot_channel(c) for c in host._channels]
    host.start_mainboard_fan_calibration(stop_test=True)
    runtime.wizard_page_changed(host,2)
    assert [fan.snapshot_channel(c) for c in host._channels]==before
    assert host.mainboard_profile_for(host._channels[0])['calibrated']
    host.restore_rgb_after_chassis_assistant=Mock()
    runtime.wizard_finished(host)
    host.restore_rgb_after_chassis_assistant.assert_called_once()


def test_automatic_white_requires_confirmed_native_stop():
    h=SimpleNamespace(openrgb_write_enabled=True,hardware_io_disabled=False,openrgb_native_plugin_active=True,
        build_chassis_white_rgb_commands=lambda:[['fixture-command']],native_openrgb_plugin=SimpleNamespace(stop=lambda:SimpleNamespace(ok=False)),
        tr_static=lambda text:text,assistant_rgb_status=SimpleNamespace(setText=Mock()),run_rgb_command_sequence=Mock(),stop_openrgb_effect=Mock())
    lighting.begin(h)
    h.run_rgb_command_sequence.assert_not_called();h.stop_openrgb_effect.assert_not_called()
    assert h.openrgb_native_plugin_active


def test_white_scope_restores_original_design_only_after_pending_command_finishes():
    callbacks=[]
    h=SimpleNamespace(openrgb_write_enabled=True,hardware_io_disabled=False,openrgb_native_plugin_active=True,
        build_chassis_white_rgb_commands=lambda:[['fixture-command']],native_openrgb_plugin=SimpleNamespace(stop=lambda:SimpleNamespace(ok=True)),
        current_rgb_design_snapshot=lambda:{'design':'original'},rgb_selected_devices={'fan'},
        tr_static=lambda text:text,assistant_rgb_status=SimpleNamespace(setText=Mock()),
        run_rgb_command_sequence=lambda commands,description,finished:callbacks.append(finished),stop_openrgb_effect=Mock(),
        backend=SimpleNamespace(_shutting_down=False),openrgb_server_reachable=True,openrgb_external_server_detected=False,
        current_rgb_studio_config=lambda:SimpleNamespace(effect_id='static'),apply_openrgb_static=Mock(),log_message=Mock())
    lighting.begin(h)
    assert h.rgb_header_preview_depth==1 and not h.openrgb_native_plugin_active
    h.stop_openrgb_effect.assert_called_once()
    lighting.finish(h)
    assert h.rgb_header_preview_depth==0
    h.apply_openrgb_static.assert_not_called()
    callbacks[0](True)
    h.apply_openrgb_static.assert_called_once()


def test_shutdown_cleanup_restores_all_channels_without_launching_ui_refresh(host):
    before=[fan.snapshot_channel(c) for c in host._channels]
    host.start_mainboard_fan_calibration(stop_test=True)
    host.finish_mainboard_fan_calibration(confirm=False,refresh=False)
    assert [fan.snapshot_channel(c) for c in host._channels]==before
    host.refresh_mainboard_fan_table.assert_not_called()
    host.update_thermalright_cooling_ui.assert_not_called()


def test_disappeared_target_does_not_skip_restoring_other_contrast_channels(host):
    before=fan.snapshot_channel(host._channels[1])
    host.start_mainboard_fan_calibration(stop_test=True)
    del host.mainboard_channels[host._channels[0].stable_id]
    host.finish_mainboard_fan_calibration(confirm=False)
    assert fan.snapshot_channel(host._channels[1])==before
    assert (host.mainboard_hwmon_controller.path/'fan_control_watchdog').read_text().strip()=='10'


def test_explicit_unused_choice_returns_previously_enabled_header_to_firmware(host):
    channel=host._channels[0];host.mainboard_profile_for(channel)['enabled']=True
    runtime.mark_disconnected(host)
    assert channel.enable_path.read_text().strip()=='2'
    assert host.mainboard_profile_for(channel)['connection']=='disconnected'


def test_stop_identification_never_touches_cpu_or_pump_header(host):
    host._channels[0].label_path.write_text('PUMP_FAN1')
    before=[fan.snapshot_channel(c) for c in host._channels]
    host.start_mainboard_fan_calibration(stop_test=True)
    assert [fan.snapshot_channel(c) for c in host._channels]==before
    host.show_error.assert_called_once()


@pytest.mark.parametrize('language',['de','en','es','fr'])
def test_long_stop_prompt_uses_active_language_and_exact_bounded_values(host,language):
    from localization_catalog import UI_TRANSLATIONS
    host.tr_static=lambda text:UI_TRANSLATIONS[language].get(text,text)
    text=runtime.confirmation_text(host,host._channels[0],120,0,True,45,'polkit',True)
    assert '120' in text and '45' in text and host._channels[0].stable_id in text
    assert text.endswith(UI_TRANSLATIONS[language]['Test starten?'])
    if language!='de':assert 'wird höchstens' not in text and 'Andere angeschlossene' not in text
