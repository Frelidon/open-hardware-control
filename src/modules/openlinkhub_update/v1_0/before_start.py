# SPDX-License-Identifier: GPL-3.0-or-later
"""Optional user-service pre-start hook; no network, USB or elevated access."""
try:
    from .startup_defaults import restore_defaults
    from .apply_user_space import _installation_directory
except ImportError:
    from startup_defaults import restore_defaults
    from apply_user_space import _installation_directory


def profile_files_are_unowned(user_state,substate,system_state):
    return (user_state in {"inactive","failed"} or (user_state=="activating" and substate=="start-pre")) and system_state in {"inactive","failed",""}


def prestart_window():
    import subprocess
    def state(user):
        command=["systemctl"]+(["--user"] if user else [])+["show","OpenLinkHub.service","-p","ActiveState,SubState"]
        result=subprocess.run(command,capture_output=True,text=True,timeout=3,check=False)
        if result.returncode not in {0,4}:raise RuntimeError("OpenLinkHub service state is unknown")
        return dict(line.split("=",1) for line in result.stdout.splitlines() if "=" in line)
    user,system=state(True),state(False)
    return profile_files_are_unowned(user.get("ActiveState",""),user.get("SubState",""),system.get("ActiveState",""))


if __name__=="__main__":
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser()
    parser.add_argument("--state",type=Path)
    args=parser.parse_args()
    try:
        if prestart_window():restore_defaults(_installation_directory(),args.state)
    except (OSError,ValueError,RuntimeError):
        # Missing/malformed optional state does not block unrelated devices.
        pass
