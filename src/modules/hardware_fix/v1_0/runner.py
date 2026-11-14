#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixed-action terminal runner with a real result file and per-profile lock."""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

if __package__ in {None, ""}:
    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[3]))
    from modules.hardware_fix.v1_0.profile import ASSET_ROOT, STATE_ROOT, os_family, validate_profile_assets
    from modules.hardware_fix.v1_0.status import status_json, inspect_status
    from modules.hardware_fix.v1_0.workflow import install_local
    from privacy_logging import redact_private_text
else:
    from .profile import ASSET_ROOT, STATE_ROOT, os_family, validate_profile_assets
    from .status import status_json, inspect_status
    from .workflow import install_local
    from privacy_logging import redact_private_text


ACTIONS = {
    "preflight", "status", "install", "install-local", "desktop", "automation-install",
    "automation-status", "automation-remove", "game-test", "uninstall",
}


def _atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def _command(action: str, family: str) -> list[str]:
    bash = "/usr/bin/bash" if Path("/usr/bin/bash").is_file() else "/bin/bash"
    if action == "preflight":
        script = "01-Installieren-Ubuntu.sh" if family == "ubuntu" else "01-Installieren-Fedora.sh"
        return [bash, os.fspath(ASSET_ROOT / script), "--check"]
    if action == "status":
        return [bash, os.fspath(ASSET_ROOT / "03-VRR-Status-pruefen.sh")]
    if action == "install":
        script = "01-Installieren-Ubuntu.sh" if family == "ubuntu" else "01-Installieren-Fedora.sh"
        return [bash, os.fspath(ASSET_ROOT / script)]
    if action == "desktop":
        return [bash, os.fspath(ASSET_ROOT / "02-VRR-im-Desktop-aktivieren.sh")]
    if action == "automation-install":
        return [bash, os.fspath(ASSET_ROOT / "05-Ubuntu-VRR-Automatik.sh")]
    if action == "automation-status":
        return [bash, os.fspath(ASSET_ROOT / "05-Ubuntu-VRR-Automatik.sh"), "--status"]
    if action == "automation-remove":
        return [bash, os.fspath(ASSET_ROOT / "05-Ubuntu-VRR-Automatik.sh"), "--ruecknahme"]
    if action == "game-test":
        return [bash, os.fspath(ASSET_ROOT / "03-VRR-Status-pruefen.sh"), "--watch", "60", "--delay", "10"]
    if action == "uninstall":
        return [sys.executable, os.fspath(Path(__file__).with_name("uninstall.py")), family]
    raise ValueError("Unbekannte Aktion")


def main(arguments: list[str]) -> int:
    if (len(arguments) not in {1, 2} or arguments[0] not in ACTIONS
            or (len(arguments) == 2 and not re.fullmatch(r"[0-9a-f]{32}", arguments[1]))):
        print("Unbekannte Hardware-Fix-Aktion.", file=sys.stderr)
        return 2
    action = arguments[0]
    family = os_family()
    if family not in {"ubuntu", "fedora"}:
        print("Dieser Hardware-Fix unterstützt hier nur Ubuntu und Fedora.", file=sys.stderr)
        return 2
    if family == "fedora" and action.startswith("automation"):
        print("Die Ubuntu-AppIndicators-Automatik wird auf Fedora nicht ausgeführt.", file=sys.stderr)
        return 2
    valid, detail = validate_profile_assets()
    if not valid:
        print(detail, file=sys.stderr)
        return 2
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    lock_path = STATE_ROOT / "job.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Für dieses Profil läuft bereits eine Aktion.", file=sys.stderr)
            return 3
        job_id = arguments[1] if len(arguments) == 2 else uuid.uuid4().hex
        log_path = STATE_ROOT / f"{job_id}.log"
        result_path = STATE_ROOT / "last-result.json"
        payload: dict[str, object] = {
            "job_id": job_id, "profile_id": "msi-mag274qpf-x30mv-vrr",
            "action": action, "os_family": family, "started_at": int(time.time()),
            "finished": False, "exit_code": None, "log_path": os.fspath(log_path),
            "boot_id_before": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
        }
        _atomic_json(result_path, payload)
        reboot_pending = False
        backup = ""
        with log_path.open("w", encoding="utf-8") as log:
            def execute(step: str) -> int:
                nonlocal backup
                print("Hardware Fix:", step, "·", family, flush=True)
                log.write("Hardware Fix: " + step + " · " + family + "\n")
                process = subprocess.Popen(_command(step, family), stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, text=True)
                assert process.stdout is not None
                marker = {
                    "install": "FERTIG: EDID im Boot-Abbild und Bootparameter geprüft.",
                    "automation-install": "FERTIG: Ubuntu-Automatik installiert",
                }.get(step)
                found = marker is None
                written = 0
                for line in process.stdout:
                    found = found or bool(marker and marker in line)
                    match = re.search(r"^Sicherung:\s*(/var/backups/msi-vrr-recovery/[^\s]+)", line)
                    if match:
                        backup = match.group(1)
                    safe = redact_private_text(line[:8192])
                    if written < 1_000_000:
                        log.write(safe)
                        log.flush()
                        written += len(safe)
                    print(safe, end="", flush=True)
                result = process.wait()
                return result if result else (0 if found else 1)

            try:
                if action == "install-local":
                    exit_code, reboot_pending = install_local(
                        family, os.environ.get("XDG_CURRENT_DESKTOP", ""), inspect_status, execute,
                    )
                else:
                    exit_code = execute(action)
                success = exit_code == 0
                if success and action in {"install-local", "install", "automation-install", "automation-remove", "uninstall"}:
                    # The standalone local service is independent of OHC's GUI.
                    _atomic_json(STATE_ROOT / "provider.json", {"selected": "local", "actual": "local"})
                after = json.loads(status_json())
            except Exception as error:
                message = redact_private_text(str(error))
                print("FEHLER:", message, file=sys.stderr, flush=True)
                log.write("FEHLER: " + message + "\n")
                exit_code, success, after = 1, False, None
        payload.update({
            "finished": True, "finished_at": int(time.time()), "exit_code": exit_code,
            "success": success, "backup_directory": backup,
            "reboot_pending": reboot_pending, "status_after": after,
        })
        _atomic_json(result_path, payload)
        print("\nErgebnis:", "erfolgreich" if success else "fehlgeschlagen", flush=True)
        return 0 if success else (exit_code or 1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
