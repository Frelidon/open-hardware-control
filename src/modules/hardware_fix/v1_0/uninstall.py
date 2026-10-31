#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Conservative profile-scoped MSI EDID override removal."""

from __future__ import annotations

import datetime
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

NAME = "msi-mag274qpf-x30mv-vrr.bin"
PARAM = "drm.edid_firmware=DP:edid/" + NAME
KNOWN_FILES = (
    Path("/etc/dracut.conf.d/99-msi-vrr.conf"),
    Path("/etc/initramfs-tools/hooks/msi-vrr-edid"),
    Path("/etc/default/grub.d/99-msi-vrr.cfg"),
)


def run(argv: list[str]) -> None:
    print("+", " ".join(argv), flush=True)
    subprocess.run(argv, check=True)


def known_profile_file(path: Path, text: str) -> bool:
    return NAME in text and (
        "MSI-VRR-RECOVERY" in text
        or "MSI MAG 274QPF X30MV" in text
        or path == Path("/etc/dracut.conf.d/99-msi-vrr.conf")
        or path.name == "msi-vrr-edid"
    )


def profile_edid(data: bytes) -> bool:
    return (
        len(data) == 384
        and data[:8] == b"\x00\xff\xff\xff\xff\xff\xff\x00"
        and data[8:12] == bytes.fromhex("3669f05c")
        and b"MAG 274 X30MV" in data[:128]
        and data[0x64] == 1
        and all(sum(data[index:index + 128]) % 256 == 0 for index in range(0, 384, 128))
    )


def main(arguments: list[str]) -> int:
    if len(arguments) != 1 or arguments[0] not in {"ubuntu", "fedora"}:
        return 2
    family = arguments[0]
    if os.geteuid() != 0:
        if family == "ubuntu":
            automation = Path(__file__).resolve().parent / "assets/msi-mag274qpf-x30mv-vrr/05-Ubuntu-VRR-Automatik.sh"
            unit = Path.home() / ".config/systemd/user/msi-vrr-games.service"
            if unit.exists():
                result = subprocess.run(["/usr/bin/bash", os.fspath(automation), "--ruecknahme"])
                if result.returncode != 0:
                    raise RuntimeError("Ubuntu-Automatik konnte nicht sicher entfernt werden; Boot-Rücknahme abgebrochen.")
        sudo = shutil.which("sudo")
        if not sudo:
            raise RuntimeError("sudo fehlt; keine Änderung vorgenommen.")
        return subprocess.run([sudo, sys.executable, os.fspath(Path(__file__).resolve()), family]).returncode
    lock = Path("/run/lock/open-hardware-control-msi-vrr.lock").open("a+")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise RuntimeError("Ein anderer MSI-VRR-Systemjob läuft bereits.")
    firmware = Path("/usr/lib/firmware/edid") / NAME
    if firmware.exists() and not profile_edid(firmware.read_bytes()):
        raise RuntimeError("Firmwaredatei hat einen fremden Inhalt; Deinstallation abgebrochen.")
    candidates: list[Path] = []
    for path in KNOWN_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not known_profile_file(path, text):
            raise RuntimeError(f"Unbekannte Datei am Profilpfad: {path}")
        candidates.append(path)
    grub_default = Path("/etc/default/grub")
    if grub_default.exists() and PARAM in grub_default.read_text(encoding="utf-8", errors="replace"):
        raise RuntimeError("Parameter steht direkt in /etc/default/grub; automatische Entfernung wäre nicht eindeutig.")
    backup = Path("/var/backups/ohc-hardware-fix") / (
        "msi-vrr-uninstall-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    )
    backup.mkdir(parents=True, exist_ok=False)
    manifest: list[dict[str, str]] = []
    for path in [*candidates, firmware, Path("/etc/kernel/cmdline")]:
        if path.exists():
            target = backup / str(len(manifest))
            shutil.copy2(path, target)
            manifest.append({"path": os.fspath(path), "backup": target.name})
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for path in candidates:
        path.unlink()
    kernel_cmdline = Path("/etc/kernel/cmdline")
    if kernel_cmdline.exists() and PARAM in kernel_cmdline.read_text().split():
        tokens = [token for token in kernel_cmdline.read_text().split() if token != PARAM]
        kernel_cmdline.write_text(" ".join(tokens) + "\n")
    if family == "fedora":
        run(["grubby", "--update-kernel=ALL", "--remove-args=" + PARAM])
    if firmware.exists():
        firmware.unlink()
    if family == "ubuntu":
        run(["update-initramfs", "-u", "-k", "all"])
        run(["update-grub"])
    else:
        for modules in sorted(Path("/lib/modules").glob("*")):
            image = Path("/boot") / f"initramfs-{modules.name}.img"
            if image.is_file():
                run(["dracut", "--force", os.fspath(image), modules.name])
    print("FERTIG: Profilbezogene Boot-Konfiguration entfernt. Neustart erforderlich.")
    print("Sicherung:", backup)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        print("FEHLER:", error, file=sys.stderr)
        raise SystemExit(1)
