# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent per-profile DPI defaults, restored before the backend starts."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

MARKER="# Open Hardware Control: user-requested startup DPI\n"


def state_file():
    base=Path(os.environ.get("XDG_STATE_HOME",str(Path.home()/".local/state")))
    return base/"open-hardware-control/openlinkhub-startup-dpi.json"


def hook_file():
    return Path.home()/".config/systemd/user/OpenLinkHub.service.d/90-ohc-startup-dpi.conf"


def atomic_bytes(path,data,mode=0o600):
    if path.is_symlink():raise ValueError("DPI state symlink refused")
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix=".ohc-dpi-",delete=False) as stream:
        temporary=Path(stream.name)
        try:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True);raise
    temporary.chmod(mode);temporary.replace(path)


def read_rules(path=None):
    path=state_file() if path is None else path
    if not path.exists():return {}
    if path.is_symlink() or path.stat().st_uid!=os.getuid() or path.stat().st_size>262144:
        raise ValueError("unsafe startup DPI state")
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict) or len(data)>128:raise ValueError("invalid startup DPI state")
    return data


def key_for(path):
    return hashlib.sha256(str(path).encode()).hexdigest()


def preferred_stage(profile):
    try:
        path=Path(str(profile.get("Path") or ""))
        rule=read_rules().get(key_for(path),{})
        stage=rule.get("stage")
        if rule.get("serial")==profile.get("Serial") and type(stage) is int and 0<=stage<=7:
            return stage
    except (OSError,ValueError):pass
    return None


def record_default(root,path,data,stage):
    rules=read_rules();key=key_for(path)
    if stage==-1:rules.pop(key,None)
    else:
        rules[key]={"root":str(root),"path":str(path),"serial":data["Serial"],
                    "product":data["Product"],"stage":stage}
    if len(rules)>128:raise ValueError("startup DPI profile limit reached")
    atomic_bytes(state_file(),json.dumps(rules,sort_keys=True).encode())


def install_hook():
    hook=hook_file()
    if hook.parent.is_symlink() or hook.is_symlink():raise ValueError("unsafe startup DPI hook")
    if hook.exists() and not hook.read_text().startswith(MARKER):
        raise ValueError("startup DPI hook belongs to another application")
    # A missing/uninstalled OHC helper must never prevent the backend starting.
    def quoted(value):
        if any(ord(c)<32 for c in value):raise ValueError("unsafe systemd argument")
        return '"'+value.replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
    helper=Path(__file__).with_name("before_start.py")
    text=MARKER+'[Service]\nExecStartPre=-'+quoted(sys.executable)+' '+quoted(str(helper))+' --state '+quoted(str(state_file().resolve()))+'\n'
    atomic_bytes(hook,text.encode())


def restore_defaults(root,state_path=None):
    """Called by ExecStartPre: backend owns no profile yet; never opens USB."""
    count=0
    base=(root/"database/profiles").resolve()
    base.relative_to(root.resolve())
    for rule in read_rules(state_path).values():
        if not isinstance(rule,dict) or rule.get("root")!=str(root):continue
        path=Path(str(rule.get("path") or ""));stage=rule.get("stage")
        if type(stage) is not int or not 0<=stage<=7 or path.is_symlink():continue
        try:
            path.resolve().relative_to(base)
            if path.stat().st_uid!=os.getuid() or path.stat().st_size>1_048_576:continue
            data=json.loads(path.read_text())
            if (data.get("Active") is not True or data.get("Serial")!=rule.get("serial")
                    or data.get("Product")!=rule.get("product") or str(stage) not in data.get("Profiles",{})):
                continue
            if data.get("Profile")==stage:continue
            data["Profile"]=stage
            atomic_bytes(path,(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode(),path.stat().st_mode & 0o777)
            count+=1
        except (OSError,ValueError):continue
    return count
