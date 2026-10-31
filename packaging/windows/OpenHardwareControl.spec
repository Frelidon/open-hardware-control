# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller onedir build for the Windows preview."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT = Path(SPECPATH).resolve().parents[1]
SRC = ROOT / "src"

datas = [
    (str(SRC / "assets"), "assets"),
    (str(SRC / "modules"), "modules"),
    (str(ROOT / "LICENSE"), "."),
    (str(ROOT / "packaging" / "VERSION"), "."),
    (str(ROOT / "packaging" / "BUILD_CHANNEL"), "."),
]

hiddenimports = collect_submodules("PIL") + collect_submodules("liquidctl")

a = Analysis(
    [str(SRC / "kraken_control.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="OpenHardwareControl",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="OpenHardwareControl",
)
