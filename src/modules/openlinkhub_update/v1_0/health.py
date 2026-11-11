# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded read-only checks before committing a user-service replacement."""
import json
import subprocess
import time
from pathlib import Path
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RuntimeError("OpenLinkHub health redirect refused")


def require_user_owner(installed: Path) -> None:
    system = subprocess.run(
        ["systemctl", "show", "OpenLinkHub.service", "-p", "ActiveState", "--value"],
        capture_output=True, text=True, timeout=3, check=False,
    )
    if system.returncode not in {0,4} or system.stdout.strip() not in {"", "inactive", "failed"}:
        raise RuntimeError("OpenLinkHub system ownership is not clear")
    wait_ready(installed, timeout=2)


def wait_ready(installed: Path, timeout: float = 18.0) -> None:
    configuration = json.loads((installed / "config.json").read_text(encoding="utf-8"))
    address = configuration.get("listenAddress", "127.0.0.1")
    port = configuration.get("listenPort", 27003)
    if address not in {"127.0.0.1", "localhost", "::1"} or type(port) is not int or not 1 <= port <= 65535:
        raise RuntimeError("OpenLinkHub health requires a loopback listener")
    authority = "[::1]" if address == "::1" else address
    request = Request(f"http://{authority}:{port}/api/devices/", headers={"Accept": "application/json"})
    opener = build_opener(ProxyHandler({}), NoRedirect())
    deadline = time.monotonic() + timeout
    detail = "service did not become ready"
    while time.monotonic() < deadline:
        try:
            process = subprocess.run(
                ["systemctl", "--user", "show", "OpenLinkHub.service", "-p", "MainPID", "--value"],
                capture_output=True, text=True, timeout=2, check=True,
            )
            pid = int(process.stdout.strip())
            if pid <= 0 or Path(f"/proc/{pid}/exe").resolve() != installed / "OpenLinkHub":
                raise RuntimeError("unexpected OpenLinkHub service executable")
            with opener.open(request, timeout=1) as response:
                raw = response.read(2_097_153)
                if response.status != 200 or len(raw) > 2_097_152:
                    raise RuntimeError("invalid OpenLinkHub health response")
            payload = json.loads(raw)
            if not isinstance(payload, dict) or not isinstance(payload.get("devices"), dict):
                raise RuntimeError("OpenLinkHub device API is unavailable")
            return
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            detail = str(exc)[:200]
        time.sleep(.25)
    raise RuntimeError(f"OpenLinkHub startup health failed: {detail}")
