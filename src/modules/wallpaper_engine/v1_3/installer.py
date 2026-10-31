"""Verified user-space download and bounded administrator install commands."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen


GITHUB_API_URL = "https://api.github.com/repos/CaptSilver/wallpaper-engine-kde-plugin/releases/latest"
GITHUB_RELEASE_PREFIX = "https://github.com/CaptSilver/wallpaper-engine-kde-plugin/releases/download/"
PACKAGE_NAME = "wallpaper-engine-kde-plugin-qt6"
MAX_API_BYTES = 2 * 1024 * 1024
MAX_PACKAGE_BYTES = 200 * 1024 * 1024
ALLOWED_DOWNLOAD_HOSTS = {"github.com", "objects.githubusercontent.com", "release-assets.githubusercontent.com"}
RPM_NAME_RE = re.compile(
    r"^wallpaper-engine-kde-plugin-qt6-[0-9][A-Za-z0-9._+-]*\.fc(?P<fedora>[0-9]+)\.(?P<arch>x86_64|aarch64)\.rpm$"
)
SHA256_RE = re.compile(r"^sha256:(?P<value>[0-9a-f]{64})$")


class PluginInstallError(RuntimeError):
    """A safe, user-displayable installer failure."""


@dataclass(frozen=True, slots=True)
class ReleaseAsset:
    tag: str
    name: str
    url: str
    size: int
    sha256: str


def parse_os_release(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"\'')
    return values


def fedora_version(path: Path = Path("/etc/os-release")) -> str | None:
    try:
        values = parse_os_release(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return None
    identifiers = {values.get("ID", ""), *values.get("ID_LIKE", "").split()}
    version = values.get("VERSION_ID", "").split(".", 1)[0]
    return version if "fedora" in identifiers and version.isdigit() else None


def normalized_architecture(machine: str | None = None) -> str | None:
    value = (machine or platform.machine()).strip().lower()
    return {"amd64": "x86_64", "x86_64": "x86_64", "arm64": "aarch64", "aarch64": "aarch64"}.get(value)


def automatic_install_supported() -> tuple[bool, str]:
    version = fedora_version()
    architecture = normalized_architecture()
    if version is None:
        return False, "Die automatische Installation ist derzeit auf Fedora beschränkt."
    if architecture is None:
        return False, "Für diese Prozessorarchitektur gibt es keinen geprüften Installer."
    if Path("/run/ostree-booted").exists():
        return False, "Auf unveränderlichen rpm-ostree-Systemen bleibt die offizielle manuelle Installation erforderlich."
    if not shutil.which("pkexec") or not shutil.which("dnf"):
        return False, "Für die Installation werden Polkit (pkexec) und DNF benötigt."
    return True, f"Fedora {version} · {architecture}"


def select_release_asset(payload: object, version: str, architecture: str) -> ReleaseAsset:
    if not isinstance(payload, dict) or payload.get("draft") or payload.get("prerelease"):
        raise PluginInstallError("GitHub lieferte kein stabiles Plugin-Release.")
    tag = str(payload.get("tag_name") or "").strip()
    assets = payload.get("assets")
    if not tag or not isinstance(assets, list):
        raise PluginInstallError("Die Release-Metadaten sind unvollständig.")
    for raw in assets:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "")
        match = RPM_NAME_RE.fullmatch(name)
        if match is None or match.group("fedora") != version or match.group("arch") != architecture:
            continue
        url = str(raw.get("browser_download_url") or "")
        digest = SHA256_RE.fullmatch(str(raw.get("digest") or ""))
        try:
            size = int(raw.get("size") or 0)
        except (TypeError, ValueError):
            size = 0
        if not url.startswith(GITHUB_RELEASE_PREFIX) or digest is None:
            raise PluginInstallError("Das passende RPM besitzt keine vertrauenswürdige Downloadadresse oder SHA256-Prüfsumme.")
        if not 1 <= size <= MAX_PACKAGE_BYTES:
            raise PluginInstallError("Die gemeldete RPM-Größe liegt außerhalb der Sicherheitsgrenze.")
        return ReleaseAsset(tag=tag[:80], name=name, url=url, size=size, sha256=digest.group("value"))
    raise PluginInstallError(f"Für Fedora {version} ({architecture}) wurde kein passendes offizielles RPM gefunden.")


def _read_bounded(response: object, maximum: int) -> bytes:
    data = response.read(maximum + 1)
    if len(data) > maximum:
        raise PluginInstallError("Der Download überschreitet die Sicherheitsgrenze.")
    return data


def installer_cache_directory() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")).expanduser()
    target = base / "open-hardware-control" / "wallpaper-engine-installer"
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    if target.is_symlink() or not target.is_dir():
        raise PluginInstallError("Der sichere Installer-Cache konnte nicht angelegt werden.")
    return target


def download_official_fedora_rpm() -> tuple[Path, ReleaseAsset]:
    version = fedora_version()
    architecture = normalized_architecture()
    if version is None or architecture is None:
        raise PluginInstallError("Die automatische RPM-Installation unterstützt dieses System nicht.")
    request = Request(GITHUB_API_URL, headers={"Accept": "application/vnd.github+json", "User-Agent": "Open-Hardware-Control"})
    with urlopen(request, timeout=20) as response:
        payload = json.loads(_read_bounded(response, MAX_API_BYTES).decode("utf-8"))
    asset = select_release_asset(payload, version, architecture)
    download_request = Request(asset.url, headers={"User-Agent": "Open-Hardware-Control"})
    with urlopen(download_request, timeout=60) as response:
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in ALLOWED_DOWNLOAD_HOSTS:
            raise PluginInstallError("GitHub leitete den Download auf einen nicht erlaubten Server um.")
        package = _read_bounded(response, MAX_PACKAGE_BYTES)
    if len(package) != asset.size:
        raise PluginInstallError("Die heruntergeladene RPM-Größe stimmt nicht mit GitHub überein.")
    if not package.startswith(b"\xed\xab\xee\xdb"):
        raise PluginInstallError("Der Download besitzt keinen gültigen RPM-Dateikopf.")
    actual = hashlib.sha256(package).hexdigest()
    if actual != asset.sha256:
        raise PluginInstallError("Die SHA256-Prüfung des Plugin-RPM ist fehlgeschlagen.")
    cache = installer_cache_directory()
    with tempfile.NamedTemporaryFile(prefix="download-", suffix=".rpm", dir=cache, delete=False) as temporary:
        temporary.write(package)
        temporary_path = Path(temporary.name)
    temporary_path.chmod(0o600)
    target = cache / asset.name
    os.replace(temporary_path, target)
    return target, asset


def privileged_install_command(package: Path, expected_sha256: str) -> list[str]:
    pkexec = shutil.which("pkexec")
    dnf = shutil.which("dnf")
    if not pkexec or not dnf or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        return []
    try:
        resolved = package.expanduser().resolve(strict=True)
        resolved.relative_to(installer_cache_directory().resolve())
    except (OSError, ValueError):
        return []
    if resolved.is_symlink() or RPM_NAME_RE.fullmatch(resolved.name) is None:
        return []
    try:
        if not 1 <= resolved.stat().st_size <= MAX_PACKAGE_BYTES:
            return []
        digest = hashlib.sha256()
        with resolved.open("rb") as stream:
            if stream.read(4) != b"\xed\xab\xee\xdb":
                return []
            stream.seek(0)
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return []
    if digest.hexdigest() != expected_sha256:
        return []
    return [pkexec, dnf, "install", "-y", str(resolved)]


def _main() -> int:
    try:
        package, asset = download_official_fedora_rpm()
        print(json.dumps({"path": str(package), "name": asset.name, "tag": asset.tag, "sha256": asset.sha256}))
        return 0
    except (PluginInstallError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(_main())
