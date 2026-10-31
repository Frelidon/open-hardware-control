#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, read-only checks against official backend release endpoints."""

from __future__ import annotations

from importlib import metadata
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any
from urllib.request import Request, urlopen

from modules.openlinkhub_update.v1_0.policy import update_plan as openlinkhub_update_plan
from .executables import preferred_backend_version, resolve_liquidctl_executable, resolve_openrgb_executable


MAX_RESPONSE_BYTES = 512 * 1024
GITHUB_RELEASES = {
    "trcc": (
        "TRCC Linux",
        "https://api.github.com/repos/Lexonight1/thermalright-trcc-linux/releases/latest",
        "https://github.com/Lexonight1/thermalright-trcc-linux/releases",
        "trcc-linux",
        "TRCC-Display",
    ),
    "wallpaper": (
        "Wallpaper Engine for KDE",
        "https://api.github.com/repos/CaptSilver/wallpaper-engine-kde-plugin/releases/latest",
        "https://github.com/CaptSilver/wallpaper-engine-kde-plugin/releases",
        "wallpaper-engine-kde-plugin-qt6",
        "OHC-Wallpaper-Assistent",
    ),
    "lact": (
        "LACT",
        "https://api.github.com/repos/ilya-zlobintsev/LACT/releases/latest",
        "https://github.com/ilya-zlobintsev/LACT/releases",
        "lact",
        "Paketverwaltung",
    ),
    "liquidctl": (
        "liquidctl",
        "https://api.github.com/repos/liquidctl/liquidctl/releases/latest",
        "https://github.com/liquidctl/liquidctl/releases",
        "liquidctl",
        "Paketverwaltung",
    ),
    "ckb-next": (
        "ckb-next", "https://api.github.com/repos/ckb-next/ckb-next/releases/latest",
        "https://github.com/ckb-next/ckb-next/releases", "ckb-next", "Paketverwaltung",
    ),
    "mangohud": (
        "MangoHud", "https://api.github.com/repos/flightlessmango/MangoHud/releases/latest",
        "https://github.com/flightlessmango/MangoHud/releases", "mangohud", "Paketverwaltung",
    ),
}
GITHUB_TAGS = {
    "vkmark": ("vkmark", "vkmark/vkmark", "vkmark"),
    "gamescope": ("Gamescope", "ValveSoftware/gamescope", "gamescope"),
    "snapper": ("Snapper", "openSUSE/snapper", "snapper"),
}
OPENRGB_RELEASES_URL = "https://openrgb.org/releases.html"
COOLERCONTROL_CHANGELOG_URL = "https://gitlab.com/coolercontrol/coolercontrol/-/raw/main/CHANGELOG.md"
COOLERCONTROL_RELEASES_URL = "https://gitlab.com/coolercontrol/coolercontrol/-/releases"
OPENLINKHUB_RELEASES_URL = "https://github.com/jurkovic-nikola/OpenLinkHub/releases"
NOT_INSTALLED = "nicht installiert"
UNKNOWN_VERSION = "installiert (Version unbekannt)"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(args, 127, "", str(exc))


def _rpm_version(package: str) -> str:
    if not shutil.which("rpm"):
        return "nicht installiert"
    result = _run(["rpm", "-q", "--qf", "%{VERSION}-%{RELEASE}", package])
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "nicht installiert"


def _package_version(package: str) -> str:
    """Read package metadata only; never launch a hardware application."""
    if shutil.which("dpkg-query"):
        result = _run(["dpkg-query", "-W", "-f=${db:Status-Status}\t${Version}", package])
        status, _, version = result.stdout.strip().partition("\t")
        return version if result.returncode == 0 and status == "installed" and version else NOT_INSTALLED
    if shutil.which("pacman"):
        result = _run(["pacman", "-Q", package])
        parts = result.stdout.strip().split(maxsplit=1)
        return parts[1] if result.returncode == 0 and len(parts) == 2 else NOT_INSTALLED
    return _rpm_version(package)


def _installed_version(component: str, package: str) -> str:
    resolver = {"liquidctl": resolve_liquidctl_executable, "openrgb": resolve_openrgb_executable}.get(component)
    if resolver is not None and resolver(""):
        return preferred_backend_version(component) or UNKNOWN_VERSION
    if component == "liquidctl":
        try:
            return metadata.version("liquidctl")
        except metadata.PackageNotFoundError:
            pass
    aliases = {
        "coolercontrol": ("coolercontrol", "coolercontrold"),
        "wallpaper": (package, "wallpaper-engine-kde-plugin"),
    }.get(component, (package,))
    for alias in aliases:
        version = _package_version(alias)
        if version != NOT_INSTALLED:
            return version
    # A manually installed binary is not missing merely because it is not in
    # the package database. Its version must not be guessed or hardware-probed.
    executables = {"trcc": "trcc", "coolercontrol": "coolercontrold"}
    executable = executables.get(component, component)
    return UNKNOWN_VERSION if shutil.which(executable) else NOT_INSTALLED


def _version_parts(value: str) -> tuple[int, ...]:
    match = re.search(r"(?<!\d)(\d+(?:\.\d+){1,3})(?!\d)", str(value))
    return tuple(int(part) for part in match.group(1).split(".")) if match else ()


def version_is_newer(installed: str, latest: str) -> bool:
    current = _version_parts(installed)
    newest = _version_parts(latest)
    if not current or not newest:
        return False
    width = max(len(current), len(newest))
    padded_current = current + (0,) * (width - len(current))
    padded_newest = newest + (0,) * (width - len(newest))
    if padded_current != padded_newest:
        return padded_current < padded_newest
    prerelease = bool(re.search(r"(?:~|-|_)?(?:rc|alpha|beta|candidate)\s*\d*", installed, re.IGNORECASE))
    latest_prerelease = bool(re.search(r"(?:~|-|_)?(?:rc|alpha|beta|candidate)\s*\d*", latest, re.IGNORECASE))
    return prerelease and not latest_prerelease


def _read_text(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": "Open-Hardware-Control"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed official HTTPS endpoints only
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("Antwort überschreitet 512 KiB")
    return raw.decode("utf-8")


def _read_json(url: str, timeout: float) -> Any:
    return json.loads(_read_text(url, timeout))


def _github_latest(url: str, timeout: float) -> tuple[str, str]:
    payload = _read_json(url, timeout)
    if not isinstance(payload, dict) or payload.get("draft") or payload.get("prerelease"):
        raise RuntimeError("kein stabiles Release gemeldet")
    tag = str(payload.get("tag_name") or "").strip()
    page = str(payload.get("html_url") or "").strip()
    if not _version_parts(tag) or not page.startswith("https://github.com/"):
        raise RuntimeError("unvollständige Release-Metadaten")
    return tag, page


def _openrgb_latest(timeout: float) -> tuple[str, str]:
    page = _read_text(OPENRGB_RELEASES_URL, timeout)
    # The official release index links stable releases on Codeberg and labels
    # pipeline/RC builds separately. Never confuse a development build with 1.0.
    releases = re.findall(r"<h[1-6][^>]*>\s*Release\s+(\d+(?:\.\d+){1,3})\s*\(", page, re.IGNORECASE)
    if not releases:
        raise RuntimeError("kein stabiles OpenRGB-Release gefunden")
    version = max(releases, key=_version_parts)
    return version, f"https://codeberg.org/OpenRGB/OpenRGB/releases/tag/release_{version}"


def _github_tag_latest(repository: str, timeout: float) -> tuple[str, str]:
    payload = _read_json(f"https://api.github.com/repos/{repository}/tags?per_page=30", timeout)
    if not isinstance(payload, list):
        raise RuntimeError("ungültige Tag-Antwort")
    tags = [str(item.get("name") or "") for item in payload if isinstance(item, dict)]
    stable = [tag for tag in tags if re.fullmatch(r"v?\d+(?:\.\d+){1,3}", tag)]
    if not stable:
        raise RuntimeError("kein stabiler Versions-Tag gefunden")
    tag = max(stable, key=_version_parts)
    return tag, f"https://github.com/{repository}/releases/tag/{tag}"


def _coolercontrol_latest(timeout: float) -> tuple[str, str]:
    changelog = _read_text(COOLERCONTROL_CHANGELOG_URL, timeout)
    stable = re.findall(r"(?m)^##\s+\[(\d+(?:\.\d+){1,3})\]\s*-\s*\d{4}-\d{2}-\d{2}\s*$", changelog)
    if not stable:
        raise RuntimeError("kein stabiler CoolerControl-Stand gefunden")
    return max(stable, key=_version_parts), COOLERCONTROL_RELEASES_URL


def _entry(name: str, installed: str, latest: str, release_url: str, route: str) -> dict[str, object]:
    missing = installed == "nicht installiert"
    return {
        "name": name,
        "installed": installed,
        "latest": latest,
        "release_url": release_url,
        "update_available": False if missing else version_is_newer(installed, latest),
        "missing": missing,
        "version_known": bool(_version_parts(installed)),
        "route": route,
    }


def collect_backend_updates(timeout: float = 8.0) -> dict[str, object]:
    """Return local and official versions without installing or modifying anything."""

    components: list[dict[str, object]] = []
    errors: list[str] = []
    timeout = max(0.1, min(8.0, float(timeout)))

    def github_component(spec):
        key, (name, api, fallback_url, package, route) = spec
        installed = _installed_version(key, package)
        try:
            latest, release_url = _github_latest(api, timeout)
            return _entry(name, installed, latest, release_url, route), ""
        except (OSError, UnicodeError, json.JSONDecodeError, RuntimeError) as exc:
            return _entry(name, installed, "Prüfung fehlgeschlagen", fallback_url, route), f"{name}: {exc}"

    def tagged_component(spec):
        key, (name, repository, package) = spec
        installed = _installed_version(key, package)
        try:
            latest, release_url = _github_tag_latest(repository, timeout)
            return _entry(name, installed, latest, release_url, "Paketverwaltung"), ""
        except (OSError, UnicodeError, json.JSONDecodeError, RuntimeError) as exc:
            return _entry(name, installed, "Prüfung fehlgeschlagen", f"https://github.com/{repository}/tags", "Paketverwaltung"), f"{name}: {exc}"

    def specialized_component(key: str):
        if key == "openlinkhub":
            plan = openlinkhub_update_plan()
            installed = plan.installed_version
            name, fallback, route = "OpenLinkHub", OPENLINKHUB_RELEASES_URL, "OHC-OpenLinkHub-Updater"
            query = lambda: _github_latest("https://api.github.com/repos/jurkovic-nikola/OpenLinkHub/releases/latest", timeout)
        elif key == "openrgb":
            installed = _installed_version("openrgb", "openrgb")
            name, fallback, route = "OpenRGB", OPENRGB_RELEASES_URL, "Paketverwaltung"
            query = lambda: _openrgb_latest(timeout)
        else:
            installed = _installed_version("coolercontrol", "coolercontrol")
            name, fallback, route = "CoolerControl", COOLERCONTROL_RELEASES_URL, "Paketverwaltung"
            query = lambda: _coolercontrol_latest(timeout)
        try:
            latest, url = query()
            item = _entry(name, installed, latest, url, route)
            if key == "openlinkhub":
                item["automatic"] = plan.automatic
            return item, ""
        except (OSError, UnicodeError, json.JSONDecodeError, RuntimeError) as exc:
            return _entry(name, installed, "Prüfung fehlgeschlagen", fallback, route), f"{name}: {exc}"

    # All workers perform read-only package/HTTPS queries. Keep this optional
    # audit bounded even when several upstream endpoints are unavailable.
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(github_component, spec) for spec in GITHUB_RELEASES.items()]
        futures += [pool.submit(tagged_component, spec) for spec in GITHUB_TAGS.items()]
        futures += [pool.submit(specialized_component, key) for key in ("openrgb", "coolercontrol", "openlinkhub")]
        for future in futures:
            item, error = future.result()
            components.append(item)
            if error:
                errors.append(error)

    order = {name: index for index, name in enumerate(("TRCC Linux", "OpenLinkHub", "OpenRGB", "LACT", "CoolerControl", "ckb-next", "liquidctl", "Wallpaper Engine for KDE", "MangoHud", "vkmark", "Gamescope", "Snapper"))}
    components.sort(key=lambda item: order.get(str(item["name"]), 99))
    return {"ok": True, "components": components, "errors": errors}
