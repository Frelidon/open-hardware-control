#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

from build_rpm_fallback import build_noarch_rpm
from backup_release import backup_release

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CHANNEL = (ROOT / "BUILD_CHANNEL").read_text(encoding="utf-8").strip().upper()
INTERNAL = CHANNEL == "INTERN"
if CHANNEL not in {"INTERN", "STABLE"}:
    raise SystemExit("BUILD_CHANNEL must be INTERN or STABLE")
requested = sys.argv[1] if len(sys.argv) > 1 else VERSION
if requested != VERSION:
    raise SystemExit(f"Requested version {requested!r} does not match VERSION {VERSION!r}")
parts = VERSION.split(".")
if len(parts) not in {3, 4} or not all(part.isdigit() for part in parts):
    raise SystemExit("VERSION must be x.y.z or x.y.z.hotfix")

DIST = ROOT / "dist"
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()

EXCLUDED_DIRS = {
    ".git", "dist", "build", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".venv", "venv",
}
EXCLUDED_FILES = {"MANIFEST.sha256", "SHA256SUMS"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
ARCHIVE_MTIME = 946684800  # 2000-01-01 UTC; valid for tar/RPM and reproducible.

RUNTIME_FILES = {
    "BUILD_CHANNEL",
    "71-nzxt-kraken-2023.rules",
    "app_constants.py",
    "branding.py",
    "collect-diagnostics.sh",
    "desktop_designs.py",
    "desktop_assets.py",
    "desktop_shell.py",
    "install-dependencies.sh",
    "install-udev-rule.sh",
    "install.sh",
    "kraken-control.desktop.in",
    "kraken-control.svg",
    "io.github.Frelidon.OpenHardwareControl.metainfo.xml",
    "kraken_cam_streamer.py",
    "hardware_request_coordinator.py",
    "mainboard_fan_control.py",
    "cooling_ownership.py",
    "cooling_card_state.py",
    "cooling_widgets.py",
    "dashboard_layout.py",
    "command_backend.py",
    "ohc_fan_helper.py",
    "io.github.Frelidon.OpenHardwareControl.fan.policy",
    "install-fan-helper.sh",
    "kraken_control.py",
    "kraken_lcd_designs.py",
    "kraken_sensors.py",
    "localization_catalog.py",
    "nzxt_backend.py",
    "LICENSE",
    "LOCAL_AI_STARTPROMPT.txt",
    "openlinkhub_integration.py",
    "openlinkhub_mouse_visuals.py",
    "openrgb_integration.py",
    "openrgb_sdk.py",
    "privacy_logging.py",
    "rgb_devices.py",
    "rgb_effects.py",
    "ui_layout.py",
    "temperature_utils.py",
    "thermalright_cooling.py",
    "thermalright_display.py",
    "thermalright_display_ui.py",
    "window_diagnostics.py",
    "hardware_diagnostics.py",
    "log_view_support.py",
    "nzxt_rgb.py",
    "nzxt_esc_profiles.py",
    "SECURITY_SCAN_REPORT.json",
    "uninstall.sh",
    "VERSION",
}


def should_copy(rel: Path, *, developer: bool) -> bool:
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if rel.name in EXCLUDED_FILES or rel.suffix in EXCLUDED_SUFFIXES:
        return False
    if developer:
        return True
    if len(rel.parts) == 1 and (rel.name in RUNTIME_FILES or rel.suffix == ".md"):
        return True
    return rel.parts[0] in {"assets", "test-gifs", "docs", "modules"}


def copy_tree(src: Path, dst: Path, *, developer: bool) -> None:
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        if not should_copy(rel, developer=developer):
            continue
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def validate_package_profiles(runtime: Path, developer: Path) -> None:
    """Keep the user ZIP lean and prove the developer ZIP is complete."""

    if (runtime / "tests").exists() or (runtime / "scripts").exists():
        raise SystemExit("Runtime ZIP profile unexpectedly contains development-only folders")
    required = (
        "AGENTS.md",
        "MODULE_REGISTRY.md",
        "scripts/check_release.sh",
        "scripts/build_release.py",
        "tests/test_security_static.py",
        "tests/test_thermalright_display_3429.py",
        "tests/test_hardware_diagnostics_342937.py",
        ".github/workflows/ci.yml",
        "tools/analyze_usbpcap.py",
    )
    missing = [name for name in required if not (developer / name).is_file()]
    development_roots = ("tests", "scripts", ".github", ".cursor", "tools")
    source_development_files = {
        path.relative_to(ROOT)
        for name in development_roots
        for path in (ROOT / name).rglob("*")
        if path.is_file() and should_copy(path.relative_to(ROOT), developer=True)
    }
    packaged_development_files = {
        path.relative_to(developer)
        for name in development_roots
        for path in (developer / name).rglob("*")
        if path.is_file()
    }
    missing_development_files = sorted(
        source_development_files - packaged_development_files
    )
    if missing or missing_development_files:
        detail = ", ".join([
            *missing, *(str(path) for path in missing_development_files),
        ])
        raise SystemExit(f"Developer package profile is incomplete: {detail}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(root: Path) -> None:
    lines = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item.name != "MANIFEST.sha256"):
        lines.append(f"{sha256(path)}  ./{path.relative_to(root).as_posix()}")
    (root / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_zip(source: Path, output: Path, archive_root: str) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in source.rglob("*") if item.is_file()):
            name = (Path(archive_root) / path.relative_to(source)).as_posix()
            info = zipfile.ZipInfo.from_file(path, arcname=name)
            info.compress_type = zipfile.ZIP_DEFLATED
            with path.open("rb") as stream:
                archive.writestr(info, stream.read(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def anonymize_tar_metadata(info: tarfile.TarInfo) -> tarfile.TarInfo:
    """Keep local account and machine identities out of distributed archives."""
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    # Extracted source directories can inherit invalid pre-epoch dates.
    # Normalize every entry so rpmbuild stays warning-free and reproducible.
    info.mtime = ARCHIVE_MTIME
    return info


def install_runtime_tree(package_root: Path) -> None:
    app_dir = package_root / "usr/share/open-hardware-control"
    app_dir.mkdir(parents=True)
    for name in sorted(RUNTIME_FILES - {"install.sh", "uninstall.sh", "kraken-control.desktop.in"}):
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, app_dir / name)
    for name in ("assets", "modules"):
        shutil.copytree(ROOT / name, app_dir / name)
    for source in sorted(ROOT.glob("*.md")):
        shutil.copy2(source, app_dir / source.name)

    bin_dir = package_root / "usr/bin"
    bin_dir.mkdir(parents=True)
    launcher = bin_dir / "open-hardware-control"
    launcher.write_text(
        "#!/usr/bin/env bash\nexec python3 /usr/share/open-hardware-control/kraken_control.py \"$@\"\n",
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    compatibility = bin_dir / "kraken-control"
    compatibility.write_text("#!/usr/bin/env bash\nexec /usr/bin/open-hardware-control \"$@\"\n", encoding="utf-8")
    compatibility.chmod(0o755)
    diagnostics = bin_dir / "open-hardware-control-diagnostics"
    diagnostics.write_text(
        "#!/usr/bin/env bash\nexec /usr/share/open-hardware-control/collect-diagnostics.sh \"$@\"\n",
        encoding="utf-8",
    )
    diagnostics.chmod(0o755)
    desktop_shell = bin_dir / "open-hardware-control-desktop-shell"
    desktop_shell.write_text(
        "#!/usr/bin/env bash\nexec python3 /usr/share/open-hardware-control/desktop_shell.py \"$@\"\n",
        encoding="utf-8",
    )
    desktop_shell.chmod(0o755)

    desktop_dir = package_root / "usr/share/applications"
    desktop_dir.mkdir(parents=True)
    desktop = (ROOT / "kraken-control.desktop.in").read_text(encoding="utf-8")
    desktop = desktop.replace("@EXEC@", "/usr/bin/open-hardware-control")
    desktop = desktop.replace(
        "@ICON@",
        "/usr/share/open-hardware-control/assets/branding/open-hardware-control-icon.png",
    )
    (desktop_dir / "open-hardware-control.desktop").write_text(desktop, encoding="utf-8")

    icon_dir = package_root / "usr/share/icons/hicolor/scalable/apps"
    icon_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "kraken-control.svg", icon_dir / "open-hardware-control.svg")
    icon_sources = {
        22: ROOT / "assets/branding/icons/open-hardware-control-22.png",
        32: ROOT / "assets/branding/icons/open-hardware-control-32.png",
        48: ROOT / "assets/branding/icons/open-hardware-control-48.png",
        64: ROOT / "assets/branding/icons/open-hardware-control-64.png",
        128: ROOT / "assets/branding/icons/open-hardware-control-128.png",
        256: ROOT / "assets/branding/icons/open-hardware-control-256.png",
        512: ROOT / "assets/branding/open-hardware-control-icon.png",
    }
    for size, source in icon_sources.items():
        target_dir = package_root / f"usr/share/icons/hicolor/{size}x{size}/apps"
        target_dir.mkdir(parents=True)
        shutil.copy2(source, target_dir / "open-hardware-control.png")

    metainfo_dir = package_root / "usr/share/metainfo"
    metainfo_dir.mkdir(parents=True)
    metainfo = (ROOT / "io.github.Frelidon.OpenHardwareControl.metainfo.xml").read_text(encoding="utf-8")
    metainfo = metainfo.replace("@VERSION@", VERSION).replace("@CHANNEL@", CHANNEL)
    (metainfo_dir / "io.github.Frelidon.OpenHardwareControl.metainfo.xml").write_text(metainfo, encoding="utf-8")

    rules_dir = package_root / "usr/lib/udev/rules.d"
    rules_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "71-nzxt-kraken-2023.rules", rules_dir)

    libexec_dir = package_root / "usr/libexec"
    libexec_dir.mkdir(parents=True, exist_ok=True)
    helper = libexec_dir / "open-hardware-control-fan-helper"
    shutil.copy2(ROOT / "ohc_fan_helper.py", helper)
    helper.chmod(0o755)

    polkit_dir = package_root / "usr/share/polkit-1/actions"
    polkit_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        ROOT / "io.github.Frelidon.OpenHardwareControl.fan.policy",
        polkit_dir / "io.github.Frelidon.OpenHardwareControl.fan.policy",
    )


def build_deb(temp: Path) -> Path:
    if not shutil.which("dpkg-deb"):
        raise SystemExit("dpkg-deb is required to build the Debian package")
    root = temp / "deb-root"
    install_runtime_tree(root)
    control_dir = root / "DEBIAN"
    control_dir.mkdir()
    (control_dir / "control").write_text(
        "\n".join(
            [
                "Package: open-hardware-control",
                f"Version: {VERSION + '~intern2' if INTERNAL else VERSION}",
                "Section: utils",
                "Priority: optional",
                "Architecture: all",
                "Maintainer: Frelidon <noreply@github.com>",
                "Depends: python3, liquidctl, python3-pil, python3-pyside6.qtwidgets, python3-pyside6.qtnetwork, python3-pyside6.qtdbus, python3-pyside6.qtsvg, policykit-1",
                "Homepage: https://github.com/Frelidon/open-hardware-control",
                "Description: NZXT Kraken, Thermalright Levita, OpenLinkHub and RGB for Linux",
                " Open-source Linux GUI for NZXT Kraken and Thermalright Levita display/cooling",
                " with local OpenLinkHub and optional loopback-only OpenRGB SDK integration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    deb_version = VERSION + "~intern2" if INTERNAL else VERSION
    output = DIST / f"open-hardware-control_{deb_version}_all.deb"
    # Use a single gzip worker for broad apt/dpkg compatibility.  The explicit
    # payload check below also rejects the control-only package observed on the
    # current overlay-based internal builder instead of publishing it.
    subprocess.run(
        [
            "dpkg-deb",
            "-Zgzip",
            "-z9",
            "--threads-max=1",
            "--build",
            "--root-owner-group",
            str(root),
            str(output),
        ],
        check=True,
    )
    listing = subprocess.run(
        ["dpkg-deb", "--contents", str(output)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    if "./usr/share/open-hardware-control/VERSION" not in listing or output.stat().st_size < 64 * 1024:
        raise SystemExit("Debian package validation failed: runtime payload is incomplete")
    return output


def build_rpm(temp: Path) -> Path:
    rpm_release = "0.intern2" if INTERNAL else "1"
    output = DIST / f"open-hardware-control-{VERSION}-{rpm_release}.noarch.rpm"
    if not shutil.which("rpmbuild"):
        payload = temp / f"open-hardware-control-{VERSION}-fallback-root"
        payload.mkdir()
        install_runtime_tree(payload)
        build_noarch_rpm(
            payload,
            output,
            version=VERSION,
            release=rpm_release,
            channel=CHANNEL,
        )
        print("Built RPM with the standard-library fallback writer (rpmbuild unavailable)")
        return output
    top = temp / "rpmbuild"
    for name in ("BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"):
        (top / name).mkdir(parents=True)

    # Stable runtime ZIPs use ``temp/open-hardware-control-VERSION`` already.
    # Keep rpmbuild's identically named source root below a dedicated parent
    # so stable builds cannot collide with the prepared runtime tree.
    payload = temp / "rpm-source" / f"open-hardware-control-{VERSION}"
    payload.mkdir(parents=True)
    install_runtime_tree(payload)
    source = top / "SOURCES" / f"open-hardware-control-{VERSION}.tar.gz"
    with tarfile.open(source, "w:gz") as archive:
        archive.add(payload, arcname=payload.name, filter=anonymize_tar_metadata)

    spec = top / "SPECS" / "open-hardware-control.spec"
    spec.write_text(
        f"""Name:           open-hardware-control
Version:        {VERSION}
Release:        {"0.intern2" if INTERNAL else "1"}%{{?dist}}
Summary:        NZXT Kraken, Thermalright Levita, OpenLinkHub and RGB for Linux
License:        GPL-3.0-or-later
URL:            https://github.com/Frelidon/open-hardware-control
Source0:        %{{name}}-%{{version}}.tar.gz
BuildArch:      noarch
Requires:       python3
Requires:       liquidctl
Requires:       python3-pyside6
Requires:       python3-pillow
Requires:       qt6-qtsvg
Requires:       polkit

%description
Open-source Linux GUI for NZXT Kraken and Thermalright Levita display/cooling
with local OpenLinkHub and optional loopback-only OpenRGB SDK integration.

%prep
%setup -q

%build

%install
mkdir -p %{{buildroot}}
cp -a usr %{{buildroot}}/

%files
/usr/bin/open-hardware-control
/usr/bin/open-hardware-control-diagnostics
/usr/bin/open-hardware-control-desktop-shell
/usr/bin/kraken-control
/usr/share/open-hardware-control
/usr/share/applications/open-hardware-control.desktop
/usr/share/icons/hicolor/scalable/apps/open-hardware-control.svg
/usr/share/icons/hicolor/*/apps/open-hardware-control.png
/usr/share/metainfo/io.github.Frelidon.OpenHardwareControl.metainfo.xml
/usr/lib/udev/rules.d/71-nzxt-kraken-2023.rules
/usr/libexec/open-hardware-control-fan-helper
/usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.fan.policy

%changelog
* Fri Aug 28 2026 Frelidon <noreply@github.com> - {VERSION}-{"0.intern2" if INTERNAL else "1"}
- Open Hardware Control {VERSION} {CHANNEL}
""",
        encoding="utf-8",
    )
    subprocess.run(
        [
            "rpmbuild",
            "-bb",
            "--define",
            f"_topdir {top}",
            "--define",
            "_buildhost open-hardware-control.invalid",
            str(spec),
        ],
        check=True,
    )
    built = next((top / "RPMS").rglob("*.rpm"))
    shutil.copy2(built, output)
    return output


def build_local_ai_git_bundle(developer: Path, temp: Path) -> Path:
    """Bundle repository history plus the exact validated developer snapshot."""

    if not shutil.which("git"):
        raise SystemExit("git is required to build the local-AI handoff bundle")
    snapshot = temp / "local-ai-snapshot"
    subprocess.run(
        ["git", "clone", "--local", "--no-hardlinks", str(ROOT), str(snapshot)],
        capture_output=True, text=True, check=True,
    )
    for path in snapshot.iterdir():
        if path.name == ".git":
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    shutil.copytree(developer, snapshot, dirs_exist_ok=True)
    subprocess.run(["git", "add", "-A"], cwd=snapshot, check=True)
    subprocess.run(
        [
            "git", "-c", "user.name=Open Hardware Control Builder",
            "-c", "user.email=noreply@open-hardware-control.invalid",
            "commit", "-m", f"Open Hardware Control {VERSION} {CHANNEL} source snapshot",
        ],
        cwd=snapshot, capture_output=True, text=True, check=True,
        env={
            **os.environ,
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
        },
    )
    suffix = "_INTERN" if INTERNAL else ""
    output = DIST / f"Open_Hardware_Control_{VERSION}{suffix}_LOCAL_AI.gitbundle"
    subprocess.run(
        ["git", "bundle", "create", str(output), "HEAD"],
        cwd=snapshot,
        check=True,
    )
    subprocess.run(["git", "bundle", "verify", str(output)], cwd=snapshot, check=True)
    return output


with tempfile.TemporaryDirectory(prefix="open-hardware-control-release-") as temp_name:
    temp = Path(temp_name)

    suffix = "-INTERN" if INTERNAL else ""
    runtime_name = f"open-hardware-control-{VERSION}{suffix}"
    runtime = temp / runtime_name
    runtime.mkdir()
    copy_tree(ROOT, runtime, developer=False)
    write_manifest(runtime)
    zip_suffix = "_INTERN" if INTERNAL else ""
    write_zip(runtime, DIST / f"open_hardware_control_v{VERSION.replace('.', '_')}{zip_suffix}.zip", runtime_name)

    developer_name = f"Entwicklerpaket {VERSION}{' INTERN' if INTERNAL else ''}"
    developer = temp / developer_name
    developer.mkdir()
    copy_tree(ROOT, developer, developer=True)
    validate_package_profiles(runtime, developer)
    write_manifest(developer)
    write_zip(developer, DIST / f"{developer_name}.zip", developer_name)

    source_name = f"open-hardware-control-{VERSION}{'-INTERN' if INTERNAL else ''}-source"
    source_root = temp / source_name
    source_root.mkdir()
    copy_tree(ROOT, source_root, developer=True)
    write_manifest(source_root)
    with tarfile.open(DIST / f"{source_name}.tar.gz", "w:gz") as archive:
        archive.add(source_root, arcname=source_name, filter=anonymize_tar_metadata)

    build_local_ai_git_bundle(developer, temp)

    if os.environ.get("OHC_SKIP_DEB") == "1":
        print("Skipping DEB build because OHC_SKIP_DEB=1")
    elif not shutil.which("dpkg-deb"):
        print("Skipping DEB build because dpkg-deb is unavailable on this system")
    else:
        build_deb(temp)
    if os.environ.get("OHC_SKIP_RPM") == "1":
        print("Skipping RPM build because OHC_SKIP_RPM=1")
    else:
        build_rpm(temp)

checks = []
for path in sorted(DIST.iterdir()):
    if path.is_file() and path.name != "SHA256SUMS":
        checks.append(f"{sha256(path)}  {path.name}")
(DIST / "SHA256SUMS").write_text("\n".join(checks) + "\n", encoding="utf-8")

backup_target = backup_release(ROOT, DIST, VERSION, CHANNEL)

print("Built release assets:")
for path in sorted(DIST.iterdir()):
    print(f"  {path.name}")
print(f"Stored rolling release backup: {backup_target}")
