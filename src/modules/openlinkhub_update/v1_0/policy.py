#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only release check and fixed package-manager plans for OpenLinkHub."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
from typing import Any
from urllib.request import Request, urlopen


RELEASE_API = "https://api.github.com/repos/jurkovic-nikola/OpenLinkHub/releases/latest"
MAX_RELEASE_BYTES = 512 * 1024
MAX_ASSET_BYTES = 128 * 1024 * 1024


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(args, 127, "", str(exc))


def _version_tuple(value: str) -> tuple[int, ...]:
    match = re.search(r"(?<!\d)(\d+(?:\.\d+){1,3})(?!\d)", str(value))
    return tuple(int(part) for part in match.group(1).split(".")) if match else ()


def update_available(installed: str, latest: str) -> bool:
    current = _version_tuple(installed)
    newest = _version_tuple(latest)
    width = max(len(current), len(newest))
    return bool(current and newest and current + (0,) * (width - len(current)) < newest + (0,) * (width - len(newest)))


@dataclass(frozen=True)
class UpdatePlan:
    method: str
    installed_version: str
    commands: tuple[tuple[str, ...], ...]
    automatic: bool
    detail: str


def package_family(path: Path = Path("/etc/os-release")) -> str:
    """Choose the native package family, independent of foreign CLI binaries."""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "manual"
    values = {}
    for line in text.splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('\"\'')
    for identifier in (values.get("ID", ""), *values.get("ID_LIKE", "").split()):
        if identifier.casefold() in {"fedora", "nobara", "rhel", "centos", "rocky", "almalinux"}:
            return "dnf"
        if identifier.casefold() in {"debian", "ubuntu", "linuxmint", "pop"}:
            return "apt"
        if identifier.casefold() in {"arch", "manjaro", "endeavouros", "cachyos", "opensuse", "suse", "sles"}:
            return "manual"
    return "manual"


def update_plan() -> UpdatePlan:
    """Return a bounded update route for package or conventional user installs."""

    pkexec = shutil.which("pkexec")
    family = package_family()
    dnf = shutil.which("dnf")
    if family == "dnf" and pkexec and dnf:
        for package in ("OpenLinkHub", "openlinkhub"):
            found = _run(["rpm", "-q", "--qf", "%{VERSION}-%{RELEASE}", package])
            if found.returncode == 0 and found.stdout.strip():
                return UpdatePlan(
                    "dnf", found.stdout.strip(),
                    ((pkexec, dnf, "upgrade", "--refresh", "-y", package),), True,
                    "RPM-Paket über die bereits eingerichteten DNF-Quellen aktualisieren",
                )
    user_service = Path.home() / ".config/systemd/user/OpenLinkHub.service"
    if user_service.is_file() and not user_service.is_symlink():
        try:
            service_text = user_service.read_text(encoding="utf-8")
        except OSError:
            service_text = ""
        working_match = re.search(r"(?m)^WorkingDirectory=([^\n\r]+)$", service_text)
        executable_match = re.search(r"(?m)^ExecStart=([^\s\n\r]+)$", service_text)
        if working_match and executable_match:
            working = Path(working_match.group(1)).expanduser().resolve()
            executable = Path(executable_match.group(1)).expanduser().resolve()
            try:
                working.relative_to(Path.home().resolve())
            except ValueError:
                pass
            else:
                if executable == working / "OpenLinkHub" and working.is_dir() and executable.is_file() and not executable.is_symlink():
                    installed = "installiert (Version unbekannt)"
                    log = working / "stdout.log"
                    try:
                        with log.open("rb") as stream:
                            stream.seek(0, 2)
                            stream.seek(max(0, stream.tell() - 1_048_576))
                            tail = stream.read(1_048_576).decode("utf-8", errors="replace")
                        versions = re.findall(r'"buildVersion"\s*:\s*"([0-9]+(?:\.[0-9]+){1,3})"', tail)
                        if versions:
                            installed = versions[-1]
                    except OSError:
                        pass
                    return UpdatePlan(
                        "user-space", installed, (), True,
                        f"Offizielles GitHub-Archiv mit SHA-256-Prüfung in {working} aktualisieren",
                    )
    apt = shutil.which("apt-get")
    if family == "apt" and pkexec and apt:
        for package in ("openlinkhub", "OpenLinkHub"):
            found = _run(["dpkg-query", "-W", "-f=${Version}", package])
            if found.returncode == 0 and found.stdout.strip():
                return UpdatePlan(
                    "apt", found.stdout.strip(),
                    (
                        (pkexec, apt, "update"),
                        (pkexec, apt, "install", "--only-upgrade", "-y", package),
                    ), True,
                    "DEB-Paket über die bereits eingerichteten APT-Quellen aktualisieren",
                )
    return UpdatePlan(
        "manual", "nicht paketverwaltet", (), False,
        "Manuelle/Benutzerinstallation erkannt; die offizielle Installationsanleitung ist erforderlich",
    )


def latest_release(timeout: float = 8.0) -> dict[str, object]:
    request = Request(RELEASE_API, headers={"Accept": "application/vnd.github+json", "User-Agent": "Open-Hardware-Control"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed official HTTPS origin
        if response.status != 200:
            raise RuntimeError(f"GitHub HTTP {response.status}")
        raw = response.read(MAX_RELEASE_BYTES + 1)
    if len(raw) > MAX_RELEASE_BYTES:
        raise RuntimeError("OpenLinkHub release response exceeds 512 KiB")
    payload: Any = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("invalid OpenLinkHub release response")
    tag = str(payload.get("tag_name") or "").strip()
    page = str(payload.get("html_url") or "").strip()
    if not _version_tuple(tag) or not page.startswith("https://github.com/jurkovic-nikola/OpenLinkHub/releases/"):
        raise RuntimeError("OpenLinkHub release metadata is incomplete")
    assets = payload.get("assets") if isinstance(payload.get("assets"), list) else []
    archive: dict[str, object] = {}
    for raw_asset in assets:
        if not isinstance(raw_asset, dict):
            continue
        name = str(raw_asset.get("name") or "")
        download = str(raw_asset.get("browser_download_url") or "")
        digest = str(raw_asset.get("digest") or "")
        size = raw_asset.get("size")
        expected_prefix = f"https://github.com/jurkovic-nikola/OpenLinkHub/releases/download/{tag}/"
        if (
            name == f"OpenLinkHub_{tag}_amd64.tar.gz"
            and download == expected_prefix + name
            and re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
            and isinstance(size, int) and 1_000_000 <= size <= MAX_ASSET_BYTES
        ):
            archive = {"name": name, "download_url": download, "digest": digest, "size": size}
            break
    return {"version": tag, "url": page, "archive": archive}


def collect_update_status() -> dict[str, object]:
    plan = update_plan()
    release = latest_release()
    result = asdict(plan)
    result["commands"] = [list(command) for command in plan.commands]
    result["latest_version"] = release["version"]
    result["release_url"] = release["url"]
    result["update_available"] = update_available(plan.installed_version, release["version"])
    result["ok"] = True
    return result


def _safe_extract_archive(archive: Path, destination: Path) -> Path:
    """Extract a bounded release archive without links, devices or traversal."""

    total = 0
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        if not 1 <= len(members) <= 10_000:
            raise RuntimeError("OpenLinkHub archive contains an invalid file count")
        for member in members:
            relative = Path(member.name)
            if relative.is_absolute() or ".." in relative.parts or member.issym() or member.islnk() or member.isdev():
                raise RuntimeError("OpenLinkHub archive contains an unsafe path or link")
            if not (member.isdir() or member.isfile()):
                raise RuntimeError("OpenLinkHub archive contains an unsupported entry")
            total += max(0, int(member.size))
            if total > 384 * 1024 * 1024:
                raise RuntimeError("OpenLinkHub archive expands beyond the safety limit")
        for member in members:
            target = destination / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = bundle.extractfile(member)
            if source is None:
                raise RuntimeError("OpenLinkHub archive entry could not be read")
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            target.chmod(member.mode & 0o755)
    candidates = [path.parent for path in destination.rglob("OpenLinkHub") if path.is_file() and path.parent.joinpath("web").is_dir()]
    if len(candidates) != 1:
        raise RuntimeError("OpenLinkHub archive does not contain one unambiguous application directory")
    return candidates[0]


def prepare_user_space_update(cache_root: Path, timeout: float = 30.0) -> dict[str, str]:
    """Download, digest-check and safely stage the official user-space archive."""

    plan = update_plan()
    if plan.method != "user-space":
        raise RuntimeError("the local installation is not an eligible user-space installation")
    release = latest_release(timeout=min(timeout, 10.0))
    asset = release.get("archive")
    if not isinstance(asset, dict) or not asset:
        raise RuntimeError("latest OpenLinkHub release has no digest-protected amd64 archive")
    root = cache_root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    if root.is_symlink() or not root.is_dir():
        raise RuntimeError("invalid OpenLinkHub update cache")
    digest = str(asset["digest"]).split(":", 1)[1]
    final_stage = root / f"stage-{release['version']}-{digest[:12]}"
    if (final_stage / "OpenLinkHub").is_file() and (final_stage / "web").is_dir():
        return {"stage": str(final_stage), "version": str(release["version"]), "digest": digest}
    archive = root / str(asset["name"])
    temporary_archive = archive.with_suffix(".download")
    request = Request(str(asset["download_url"]), headers={"User-Agent": "Open-Hardware-Control"})
    hasher = hashlib.sha256()
    received = 0
    with urlopen(request, timeout=timeout) as response, temporary_archive.open("wb") as output:  # noqa: S310 - validated official URL
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            received += len(chunk)
            if received > int(asset["size"]) or received > MAX_ASSET_BYTES:
                raise RuntimeError("OpenLinkHub download exceeds the advertised size")
            hasher.update(chunk)
            output.write(chunk)
    if received != int(asset["size"]) or hasher.hexdigest() != digest:
        temporary_archive.unlink(missing_ok=True)
        raise RuntimeError("OpenLinkHub archive failed its published SHA-256 check")
    temporary_archive.replace(archive)
    with tempfile.TemporaryDirectory(prefix="openlinkhub-stage-", dir=root) as temporary_dir:
        extracted = _safe_extract_archive(archive, Path(temporary_dir))
        if final_stage.exists():
            raise RuntimeError("stale OpenLinkHub staging directory blocks the update")
        extracted.rename(final_stage)
    return {"stage": str(final_stage), "version": str(release["version"]), "digest": digest}
