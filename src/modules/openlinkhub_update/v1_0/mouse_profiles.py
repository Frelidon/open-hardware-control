# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded mouse metadata and guarded offline startup-stage selection.

OpenLinkHub .9.4 exposes DPI values and user profiles via HTTP, but no endpoint
for selecting the persisted Profile stage. Only its existing user-owned JSON
is changed, with the owning service stopped and a private rollback copy.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time


def mouse_metadata(detail):
    if not isinstance(detail, dict):return {}
    profile=detail.get("DeviceProfile")
    if not isinstance(profile,dict):return {}
    stages=profile.get("Profiles")
    if not isinstance(stages,dict):return {}
    clean=[]
    for key,value in list(stages.items())[:8]:
        if not re.fullmatch(r"[0-7]",str(key)) or not isinstance(value,dict):continue
        dpi=value.get("Value")
        if type(dpi) is int and 50<=dpi<=100000:clean.append({"id":str(key),"dpi":dpi})
    profiles=detail.get("userProfiles",{})
    names=[k for k in profiles if isinstance(k,str) and re.fullmatch(r"[A-Za-z0-9_-]{1,48}",k)] if isinstance(profiles,dict) else []
    active=next((name for name in names if isinstance(profiles[name],dict) and profiles[name].get("Active") is True),None)
    from .startup_defaults import preferred_stage
    return {"stages":sorted(clean,key=lambda x:int(x["id"])),"current":profile.get("Profile"),"active_profile":active,
            "preferred":preferred_stage(profile),
            "profiles":names[:64],"minimum":detail.get("MinDPI",100),"maximum":detail.get("MaxDPI",30000)}


def set_startup_stage(device_id, stage, api_get, api_url):
    from .apply_user_space import _installation_directory, _run_systemctl
    from .health import wait_ready
    if type(stage) is not int or not -1<=stage<=7:raise ValueError("invalid DPI stage")
    detail=api_get(api_url,"/api/devices/"+device_id).get("device")
    if not isinstance(detail,dict) or not mouse_metadata(detail).get("stages"):
        raise ValueError("mouse profile details are unavailable")
    profile=detail.get("DeviceProfile",{})
    root=_installation_directory()
    from .health import require_user_owner
    require_user_owner(root)
    raw=Path(str(profile.get("Path") or ""))
    if not raw.is_absolute() or raw.is_symlink():raise ValueError("unsafe mouse profile path")
    path=raw.resolve()
    path.relative_to((root/"database/profiles").resolve())
    if not path.is_file() or path.stat().st_uid != os.getuid() or path.stat().st_size>1_048_576:
        raise ValueError("mouse profile is not an eligible user-owned file")
    previous=None
    from .startup_defaults import state_file,hook_file,record_default,install_hook,atomic_bytes
    from .startup_defaults import read_rules, MARKER
    read_rules()
    hook=hook_file()
    if hook.is_symlink() or (hook.is_file() and (hook.stat().st_size>16384 or not hook.read_text().startswith(MARKER))):
        raise ValueError("startup DPI hook belongs to another application")
    previous_optional={p:p.read_bytes() if p.is_file() else None for p in (state_file(),hook)}
    _run_systemctl("stop")
    try:
        previous=path.read_bytes()
        data=json.loads(previous)
        if data.get("Serial")!=device_id or data.get("Active") is not True or (stage!=-1 and str(stage) not in data.get("Profiles",{})):
            raise ValueError("mouse profile identity or stage changed")
        if data.get("Product")!=profile.get("Product") or not isinstance(data.get("Profile"),int):
            raise ValueError("mouse profile schema changed")
        directory=root.parent/".ohc-openlinkhub-profile-backups"
        directory.mkdir(mode=0o700,exist_ok=True)
        token=hashlib.sha256(device_id.encode()).hexdigest()[:16]
        backup=directory/f"{token}-{time.time_ns()}.json"
        with backup.open("xb") as f:f.write(previous)
        backup.chmod(0o600)
        if stage!=-1:data["Profile"]=stage
        with tempfile.NamedTemporaryFile(dir=path.parent,delete=False,prefix=".ohc-dpi-",mode="w") as stream:
            temporary=Path(stream.name)
            json.dump(data,stream,ensure_ascii=False,indent=2);stream.write("\n")
        temporary.chmod(path.stat().st_mode & 0o777)
        temporary.replace(path)
        record_default(root,path,data,stage);install_hook()
        _run_systemctl("daemon-reload")
        _run_systemctl("start");wait_ready(root)
        confirmed=api_get(api_url,"/api/devices/"+device_id).get("device",{}).get("DeviceProfile",{})
        if confirmed.get("Profile")!=data["Profile"]:raise RuntimeError("startup DPI was not confirmed")
    except Exception:
        _run_systemctl("stop")
        if previous is not None:path.write_bytes(previous)
        for optional,contents in previous_optional.items():
            if contents is None:optional.unlink(missing_ok=True)
            else:atomic_bytes(optional,contents)
        _run_systemctl("daemon-reload")
        _run_systemctl("start")
        raise
    return {"ok":True,"action":"mouse-default-dpi"}
