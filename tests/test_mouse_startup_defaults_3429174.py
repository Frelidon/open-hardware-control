"""A house-marked default survives physical DPI changes and service restarts."""
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from modules.openlinkhub_update.v1_0 import startup_defaults as defaults


@pytest.fixture
def profiles(tmp_path,monkeypatch):
    root=tmp_path/"OpenLinkHub";folder=root/"database/profiles";folder.mkdir(parents=True)
    path=folder/"synthetic.json"
    data={"Active":True,"Serial":"fixture","Product":"Fixture mouse","Profile":1,
          "Profiles":{"0":{"Value":800},"1":{"Value":1600}},"RGBProfile":"wave","Path":str(path)}
    path.write_text(json.dumps(data))
    monkeypatch.setattr(defaults,"state_file",lambda:tmp_path/"state/defaults.json")
    monkeypatch.setattr(defaults,"hook_file",lambda:tmp_path/"unit/90-ohc-startup-dpi.conf")
    return root,path,data


def test_selected_default_survives_a_later_hardware_dpi_change(profiles):
    root,path,data=profiles
    defaults.record_default(root,path,data,0)
    # OpenLinkHub persists the current DPI after pressing a physical DPI key.
    data["Profile"]=1;path.write_text(json.dumps(data))
    assert defaults.preferred_stage(data)==0
    assert defaults.restore_defaults(root)==1
    after=json.loads(path.read_text());assert after["Profile"]==0
    after["Profile"]=data["Profile"];assert after==data
    assert defaults.restore_defaults(root)==0


def test_native_behavior_can_be_restored_without_overwriting_current_stage(profiles):
    root,path,data=profiles
    defaults.record_default(root,path,data,0)
    defaults.record_default(root,path,data,-1)
    before=path.read_bytes()
    assert defaults.preferred_stage(data) is None
    assert defaults.restore_defaults(root)==0 and path.read_bytes()==before


@pytest.mark.parametrize("change",["inactive","serial","product","outside","symlink"])
def test_prestart_does_not_touch_unrelated_or_unsafe_profiles(profiles,tmp_path,change):
    root,path,data=profiles;defaults.record_default(root,path,data,0)
    if change=="inactive":data["Active"]=False
    elif change=="serial":data["Serial"]="unrelated"
    elif change=="product":data["Product"]="different"
    elif change in {"outside","symlink"}:
        other=tmp_path/"unrelated.json";other.write_text(json.dumps(data))
        if change=="outside":
            rules=defaults.read_rules();next(iter(rules.values()))["path"]=str(other)
            defaults.state_file().write_text(json.dumps(rules))
        else:path.unlink();path.symlink_to(other)
    if change not in {"outside","symlink"}:path.write_text(json.dumps(data))
    before=path.read_bytes();assert defaults.restore_defaults(root)==0;assert path.read_bytes()==before


def test_hook_is_optional_and_never_replaces_another_applications_hook(profiles):
    defaults.install_hook();text=defaults.hook_file().read_text()
    assert text.startswith(defaults.MARKER)
    assert 'ExecStartPre=-' in text and 'before_start.py' in text
    assert 'sudo' not in text and 'pkexec' not in text
    defaults.hook_file().write_text('[Service]\n# foreign\n')
    with pytest.raises(ValueError):defaults.install_hook()


def test_default_state_is_private_and_per_profile(profiles):
    root,path,data=profiles
    defaults.record_default(root,path,data,0)
    second=path.with_name("gaming.json");other=dict(data,Path=str(second),Active=False)
    second.write_text(json.dumps(other));defaults.record_default(root,second,other,1)
    assert defaults.preferred_stage(data)==0 and defaults.preferred_stage(other)==1
    assert defaults.state_file().stat().st_mode&0o777==0o600


@pytest.mark.parametrize("user,substate,system,allowed",[
    ("activating","start-pre","inactive",True),
    ("inactive","dead","inactive",True),
    ("active","running","inactive",False),
    ("activating","start-post","inactive",False),
    ("activating","start-pre","active",False),
    ("","","inactive",False),
])
def test_profile_restore_is_limited_to_the_unowned_prestart_window(user,substate,system,allowed):
    from modules.openlinkhub_update.v1_0.before_start import profile_files_are_unowned
    assert profile_files_are_unowned(user,substate,system)==allowed
