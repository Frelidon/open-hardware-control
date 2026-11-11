"""Content sizing, safe backend replacement and persisted mouse startup DPI."""
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from modules.openlinkhub_update.v1_0 import apply_user_space, mouse_profiles, stage_integrity
from modules.ui_performance.v1_1.adaptive_views import install_content_heights
from PySide6.QtWidgets import QApplication, QListWidget, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout


def test_daemon_reload_does_not_receive_a_service_argument():
    calls=[]
    def run(args,**kwargs):
        calls.append(args)
        valid=args in [["systemctl","--user","daemon-reload"],["systemctl","--user","start","OpenLinkHub.service"]]
        return subprocess.CompletedProcess(args,0 if valid else 1,"","Too many arguments.")
    with patch.object(apply_user_space.subprocess,"run",side_effect=run):
        apply_user_space._run_systemctl("daemon-reload")
        apply_user_space._run_systemctl("start")
    assert len(calls)==2


@pytest.mark.parametrize("family",["ubuntu","fedora"])
def test_failed_backend_health_restores_previous_tree_before_restart(tmp_path,monkeypatch,family):
    install=tmp_path/family/"OpenLinkHub";install.mkdir(parents=True)
    (install/"OpenLinkHub").write_bytes(b"old")
    (install/"config.json").write_text('{"custom":true}')
    cache=tmp_path/family/"cache";stage=cache/"stage";(stage/"web").mkdir(parents=True)
    (stage/"OpenLinkHub").write_bytes(b"new")
    stage_integrity.seal(stage,"a"*64)
    monkeypatch.setattr(apply_user_space,"_installation_directory",lambda:install)
    events=[]
    def service(action):
        binary=(install/"OpenLinkHub").read_bytes() if install.exists() else None
        events.append((action,binary))
    monkeypatch.setattr(apply_user_space,"_run_systemctl",service)
    monkeypatch.setattr(apply_user_space,"wait_ready",lambda _path:(_ for _ in ()).throw(RuntimeError("fixture startup failure")))
    with pytest.raises(RuntimeError,match="fixture startup failure"):
        apply_user_space.apply_update(stage,cache)
    assert (install/"OpenLinkHub").read_bytes()==b"old"
    assert json.loads((install/"config.json").read_text())=={"custom":True}
    assert events[-3:]==[("stop",b"new"),("daemon-reload",b"old"),("start",b"old")]


@pytest.mark.parametrize("mutation",["change","remove","add","symlink"])
def test_prepared_payload_damage_is_detected(tmp_path,mutation):
    (tmp_path/"OpenLinkHub").write_bytes(b"verified")
    stage_integrity.seal(tmp_path,"a"*64);stage_integrity.verify(tmp_path,"a"*64)
    if mutation=="change":(tmp_path/"OpenLinkHub").write_bytes(b"changed")
    elif mutation=="remove":(tmp_path/"OpenLinkHub").unlink()
    elif mutation=="add":(tmp_path/"unverified").write_text("extra")
    else:(tmp_path/"link").symlink_to(tmp_path/"OpenLinkHub")
    with pytest.raises(ValueError):stage_integrity.verify(tmp_path,"a"*64)


def test_mouse_metadata_keeps_reported_sixth_stage_and_never_exports_paths():
    metadata=mouse_profiles.mouse_metadata({"DeviceProfile":{"Path":"/private","Serial":"private",
        "Profile":2,"Profiles":{str(i):{"Value":400*(i+1)} for i in range(6)}},
        "MinDPI":100,"MaxDPI":18000,"userProfiles":{"default":{},"Gaming":{},"../unsafe":{}}})
    assert [s["id"] for s in metadata["stages"]]==list("012345")
    assert metadata["current"]==2 and metadata["maximum"]==18000
    assert metadata["profiles"]==["default","Gaming"]
    assert "private" not in json.dumps(metadata)


@pytest.mark.parametrize("failure",[False,True])
def test_startup_dpi_changes_only_selected_profile_and_rolls_back(tmp_path,monkeypatch,failure):
    install=tmp_path/"OpenLinkHub";profiles=install/"database/profiles";profiles.mkdir(parents=True)
    path=profiles/"fixture.json"
    data={"Product":"Fixture mouse","Serial":"fixture-mouse","Active":True,"Profile":1,
          "Profiles":{"0":{"Value":800},"1":{"Value":1600}},"RGBProfile":"rainbow","Path":str(path)}
    path.write_text(json.dumps(data));before=path.read_bytes()
    def api(*args):
        return {"device":{"DeviceProfile":json.loads(path.read_text()),"userProfiles":{"default":{}}}}
    events=[]
    monkeypatch.setattr(apply_user_space,"_installation_directory",lambda:install)
    monkeypatch.setattr(apply_user_space,"_run_systemctl",events.append)
    from modules.openlinkhub_update.v1_0 import health, startup_defaults
    monkeypatch.setattr(health,"require_user_owner",lambda _path:None)
    monkeypatch.setattr(startup_defaults,"state_file",lambda:tmp_path/"state/defaults.json")
    monkeypatch.setattr(startup_defaults,"hook_file",lambda:tmp_path/"unit/90-ohc-startup-dpi.conf")
    def ready(_path):
        if failure:raise RuntimeError("unhealthy fixture")
    monkeypatch.setattr(health,"wait_ready",ready)
    if failure:
        with pytest.raises(RuntimeError):mouse_profiles.set_startup_stage("fixture-mouse",0,api,"http://127.0.0.1:27003")
        assert path.read_bytes()==before
        assert events==["stop","daemon-reload","start","stop","daemon-reload","start"]
    else:
        assert mouse_profiles.set_startup_stage("fixture-mouse",0,api,"http://127.0.0.1:27003")["ok"]
        after=json.loads(path.read_text());assert after.pop("Profile")==0
        data.pop("Profile");assert after==data
        assert events==["stop","daemon-reload","start"]
    backups=list((tmp_path/".ohc-openlinkhub-profile-backups").glob("*.json"))
    assert len(backups)==1 and backups[0].read_bytes()==before
    assert backups[0].stat().st_mode & 0o777==0o600


def test_lists_grow_shrink_and_track_expansion_without_polling():
    app=QApplication.instance() or QApplication([])
    root=QWidget();layout=QVBoxLayout(root);view=QListWidget();layout.addWidget(view)
    install_content_heights(root);app.processEvents();empty=view.height()
    assert empty<100
    view.addItems(["row"]*20);app.processEvents();assert empty<view.height()<=340
    view.clear();app.processEvents();assert view.height()==empty
    tree=QTreeWidget();tree.setHeaderHidden(True);layout.addWidget(tree)
    parent=QTreeWidgetItem(["parent"]);tree.addTopLevelItem(parent)
    parent.addChildren([QTreeWidgetItem(["child"]) for _ in range(4)])
    install_content_heights(root);app.processEvents();small=tree.height()
    parent.setExpanded(True);app.processEvents();assert tree.height()>small
    parent.setExpanded(False);app.processEvents();assert tree.height()==small
    root.deleteLater();app.processEvents()


@pytest.mark.parametrize("code,state,allowed",[(0,"inactive",True),(4,"",True),(0,"active",False),(1,"",False)])
def test_mouse_startup_stage_requires_clear_single_user_owner(code,state,allowed):
    from modules.openlinkhub_update.v1_0 import health
    result=subprocess.CompletedProcess([],code,state,"")
    with patch.object(health.subprocess,"run",return_value=result),patch.object(health,"wait_ready") as ready:
        if allowed:
            health.require_user_owner(Path("/fixture/OpenLinkHub"));ready.assert_called_once()
        else:
            with pytest.raises(RuntimeError):health.require_user_owner(Path("/fixture/OpenLinkHub"))
            ready.assert_not_called()
