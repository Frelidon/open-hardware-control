param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Version = (Get-Content (Join-Path $Root "packaging/VERSION") -Raw).Trim()
$BuildRoot = Join-Path $Root "build/windows"
$DistRoot = Join-Path $Root "dist/windows"
$Venv = Join-Path $BuildRoot "venv"

if (-not $IsWindows) {
    throw "The Windows EXE must be built on Windows; PyInstaller is not a cross-compiler."
}

New-Item -ItemType Directory -Force $BuildRoot | Out-Null
New-Item -ItemType Directory -Force $DistRoot | Out-Null
& $Python -m venv $Venv
$VenvPython = Join-Path $Venv "Scripts/python.exe"
& $VenvPython -m pip install --disable-pip-version-check --upgrade pip
& $VenvPython -m pip install --disable-pip-version-check -r (Join-Path $Root "packaging/windows/requirements-windows.txt")

$env:QT_QPA_PLATFORM = "offscreen"
& $VenvPython -m pytest -q `
    (Join-Path $Root "tests/test_windows_platform_3429135.py") `
    (Join-Path $Root "tests/test_ui_themes_342961.py") `
    (Join-Path $Root "tests/test_setup_features_3429135.py")

& $VenvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --distpath $DistRoot `
    --workpath (Join-Path $BuildRoot "pyinstaller") `
    (Join-Path $Root "packaging/windows/OpenHardwareControl.spec")

$AppDirectory = Join-Path $DistRoot "OpenHardwareControl"
$Executable = Join-Path $AppDirectory "OpenHardwareControl.exe"
if (-not (Test-Path $Executable -PathType Leaf)) {
    throw "Windows executable was not produced: $Executable"
}

$Archive = Join-Path $DistRoot "OpenHardwareControl-$Version-Windows-x64-preview.zip"
if (Test-Path $Archive) { Remove-Item $Archive -Force }
Compress-Archive -Path $AppDirectory -DestinationPath $Archive -CompressionLevel Optimal
$Hash = (Get-FileHash $Archive -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -Path "$Archive.sha256" -Value "$Hash  $(Split-Path $Archive -Leaf)" -Encoding ascii
Write-Host "Windows preview created: $Archive"
