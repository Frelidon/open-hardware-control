# Open Hardware Control by Frelidon 3.4.29.160 STABLE

<!-- project-badges -->
[![CI](https://github.com/Frelidon/open-hardware-control/actions/workflows/ci.yml/badge.svg)](https://github.com/Frelidon/open-hardware-control/actions/workflows/ci.yml) [![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](../LICENSE) [![Release](https://img.shields.io/github/v/release/Frelidon/open-hardware-control?display_name=tag)](https://github.com/Frelidon/open-hardware-control/releases)
<!-- /project-badges -->

Open Hardware Control is a free Linux GUI for the **NZXT Kraken LCD**, pump, radiator fans and RGB, for the **Thermalright Levita Vision display**, for **calibrated motherboard/case fans through Linux hwmon/NCT6687**, for **Corsair devices through OpenLinkHub** and for additional RGB devices through an automatically managed local hardware engine. It targets Fedora, Nobara, Debian, Ubuntu, Linux Mint, Arch Linux, Manjaro, EndeavourOS and openSUSE.

<!-- project-repository -->
Project repository: <https://github.com/Frelidon/open-hardware-control>
<!-- /project-repository -->

> **Unofficial independent community project:** Open Hardware Control is not supported, approved, endorsed, operated by, or affiliated with NZXT, Corsair, Thermalright, be quiet!, OpenLinkHub, OpenRGB, or any other named manufacturer or project. Product and brand names are used only to describe compatibility. Manufacturers and rights holders can contact Frelidon through the public contact address in the GitHub profile or the Steam username **Frelidon**.

## Screenshots

[![Overview](images/screenshots/01-uebersicht.png)](images/screenshots/01-uebersicht.png)

<table>
  <tr>
    <td align="center" width="33%">
      <a href="images/screenshots/02-kuehlung.png"><img src="images/screenshots/thumbs/02-kuehlung.png" alt="Cooling"></a><br>
      <sub><b>Cooling</b> · Levita/Kraken, case fans, CoolerControl guard</sub>
    </td>
    <td align="center" width="33%">
      <a href="images/screenshots/03-rgb-studio.png"><img src="images/screenshots/thumbs/03-rgb-studio.png" alt="RGB Studio"></a><br>
      <sub><b>RGB Studio</b> · engine, ENE-DRAM, test mode, design gallery</sub>
    </td>
    <td align="center" width="33%">
      <a href="images/screenshots/04-lcd-levita.png"><img src="images/screenshots/thumbs/04-lcd-levita.png" alt="LCD · Thermalright Levita display studio"></a><br>
      <sub><b>LCD</b> · two-layer Thermalright Levita studio</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <a href="images/screenshots/05-wallpaper-engine.png"><img src="images/screenshots/thumbs/05-wallpaper-engine.png" alt="Wallpaper Engine"></a><br>
      <sub><b>Wallpaper Engine</b> · Steam Workshop and Plasma playback</sub>
    </td>
    <td align="center" width="33%">
      <a href="images/screenshots/06-profile.png"><img src="images/screenshots/thumbs/06-profile.png" alt="Profiles"></a><br>
      <sub><b>Profiles</b> · save cooling, RGB, LCD and design together</sub>
    </td>
    <td align="center" width="33%">
      <a href="images/screenshots/07-einstellungen.png"><img src="images/screenshots/thumbs/07-einstellungen.png" alt="Settings"></a><br>
      <sub><b>Settings</b> · theme, language, display, autostart</sub>
    </td>
  </tr>
</table>

<sub>Click an image for the full-size view. Same order as the sidebar in the app (German UI shown; English, Spanish and French are available).</sub>

## Thermalright Levita Vision display

**The 1600×720 display of the Thermalright Levita Vision 360 ARGB Black is supported.** The local display studio combines your own images and videos (layer 1) with a complete TRCC hardware design or freely movable OHC live values for CPU, GPU, RAM, clock and custom text (layer 2). Eleven original OHC backgrounds, twelve original editable data layouts, four original layer-1 animations and five OHC effect families with twelve variants ship with the app. Manufacturer/TRCC catalogs, imported user files, stock clips and third-party design components are not bundled.

The safe preview-only test mode is active by default; real USB transfer happens only through the separately installed GPL backend **TRCC Linux** (9.10.4 recommended). Levita pump and radiator fans run through separately confirmed motherboard PWM headers (`PUMP_FAN`, `CPU_FAN`) with a safe 70 %/10 s test; CoolerControl blocks concurrent writes.

## New in 3.4.29.160 STABLE

- Public build with a fully cleaned design catalog: the repository and packages
  contain only project-owned OHC designs.
- Every main area now shows an independent feature version and its Alpha, Beta,
  Release Candidate or Stable maturity level without changing feature behavior.
- Manufacturer/TRCC catalogs, stock media, Kenney components and imported user
  files are explicitly excluded from the release.
- The complete Levita UI release test uses the same explicit fixture on local
  hardware and hardware-free GitHub runners.
- OpenRGB SDK v6 callbacks and the guarded TRCC GPU-clock recovery from `.158`
  remain included.

Older versions: [Version history](#version-history) · [CHANGELOG.md](CHANGELOG.md) · [docs/releases/](releases)

## Installation

### Fedora and Nobara – RPM

Download `open-hardware-control-3.4.29.160-1.noarch.rpm` to your Downloads folder and run:

```bash
cd ~/Downloads
sudo dnf install ./open-hardware-control-3.4.29.160-1.noarch.rpm
```

### Debian, Ubuntu and Linux Mint – DEB

Download `open-hardware-control_3.4.29.160_all.deb` to your Downloads folder and run:

```bash
cd ~/Downloads
sudo apt install './open-hardware-control_3.4.29.160_all.deb'
```

### Universal installer – ZIP

For Fedora/Nobara, Debian/Ubuntu/Mint, Arch/Manjaro/EndeavourOS and openSUSE. Download `open_hardware_control_v3_4_29_160.zip` and run:

```bash
cd ~/Downloads
unzip open_hardware_control_v3_4_29_160.zip
cd open-hardware-control-3.4.29.160
chmod +x install.sh
./install.sh
```

An existing installation is updated in place. Afterwards **Open Hardware Control by Frelidon** appears in the application menu, or start `~/.local/bin/open-hardware-control` from a terminal (the legacy command `kraken-control` still works). The dependency check detects the common package managers automatically; every distro-specific command is listed in [INSTALL.md](INSTALL.md).

Optional **LACT** (GPU tuning) and **OpenRGB** (RGB devices) can be installed from the wizard or their own areas after confirmation when a supported package source is available. **OpenLinkHub** (Corsair), **TRCC Linux** (Levita display) and **CaptSilver Wallpaper Engine plugin** (KDE) remain separate components; OHC does not bundle them. OpenLinkHub has its own confirmed update path.

## Security

- Writes only reach matching, detected devices: Kraken through liquidctl, Corsair through a fixed validated action list, motherboard PWM only after physical confirmation.
- OpenLinkHub and OpenRGB are addressed exclusively over loopback (`127.0.0.1`); OpenRGB only in explicit `--client` mode against the local SDK server `127.0.0.1:6742`.
- RGB/Corsair write permissions apply to the current session only; competing devices (NZXT ↔ OpenRGB, Corsair ↔ OpenLinkHub) stay locked.
- Polkit grants store no password; system-wide services are never changed automatically. No firmware updates, no cloud, no telemetry.
- Details: [SECURITY.md](../.github/SECURITY.md) · [docs/security/](security)

## Documentation

| Folder | Contents |
|---|---|
| [INSTALL.md](INSTALL.md) · [CHANGELOG.md](CHANGELOG.md) | per-distribution installation, complete change history |
| [docs/hardware/](hardware) | [Supported devices](hardware/SUPPORTED_DEVICES.en.md), [Profiles](hardware/PROFILES.md), [CPU profiles](hardware/CPU_PROFILES.en.md), [RGB Studio](hardware/RGB_STUDIO.md), [OpenLinkHub integration](hardware/OPENLINKHUB_INTEGRATION.md), USB capture findings |
| [docs/project/](project) | [Architecture](project/ARCHITECTURE.md), [Project status](project/PROJECT_STATUS.md), [Module registry](project/MODULE_REGISTRY.md), [Project scope](project/PROJECT_SCOPE.en.md), roadmap, decisions |
| [docs/security/](security) | RGB/desktop security audits, [Privacy](security/PRIVACY.md), scan report |
| [src/](../src) | application code: `kraken_control.py` (entry point), feature modules under `src/modules/`, artwork under `src/assets/` |
| [docs/ai/](ai) | working guides for local and web-based coding assistants |
| [docs/releases/](releases) | release notes for every version, release checklist |
| [packaging/](../packaging) | `install.sh`/`uninstall.sh`, `VERSION`, `BUILD_CHANNEL`, udev rule, Polkit policy, metainfo, desktop file, helper scripts |

German version: [README.md](../README.md)

## Status

Public stable build, provided without warranty. Channel **STABLE**, license **GPL-3.0-or-later**. Contributing: [.github/CONTRIBUTING.md](../.github/CONTRIBUTING.md) · Help: [.github/SUPPORT.md](../.github/SUPPORT.md) · Security reports: [SECURITY.md](../.github/SECURITY.md)

## Modules

### NZXT Kraken 2023

RGB, images, GIFs, clock, static and animated live hardware designs, CPU/GPU live values, software-controlled CPU temperature curves for pump and fans, profiles, four languages and an LCD safety fallback. During an LCD animation Kraken status polling stays paused; required pump/fan changes run as a short exclusive USB transaction before the streamer takes over again.

| Device | USB ID | Scope |
|---|---|---|
| NZXT Kraken 2023 | `1e71:300e` | liquid, pump, radiator fans, LCD |
| NZXT 2023 RGB Controller | `1e71:2012` | three RGB channels |

### Thermalright Levita Vision

Two-layer display studio (see above), new procedural smoke editor under Display Effects, import of local images, videos, `.zt` files and TRCC layout folders, TRCC categories Gallery/Tech/HUD/Light/Nature/Aesthetic, favourites, a custom design folder, autostart of both layers and cooling through confirmed motherboard PWM headers.

### Motherboard and case fans

Linux hwmon/NCT6687 (e.g. MSI X870 family). Every PWM channel is unlocked only after a short physical test; afterwards Silent/Balanced/Performance, custom curves, sensor source, hysteresis, PWM/DC switching only through an existing `pwmN_mode`, a guided fan assistant and hand-back to BIOS/firmware on exit.

### Corsair · OpenLinkHub

Exclusively through the local API `http://127.0.0.1:27003`. Documented write commands for cooling, RGB/LCD, mouse, keyboard and headset; controls only for detected devices. User and system services are detected separately. The version check updates package installations through existing sources or the safe user-service path including the web UI only after confirmation.

### RGB Studio · OpenRGB SDK

OHC starts a private windowless OpenRGB process on demand and uses only the local SDK endpoint. Detected devices, zones, LEDs and modes, static colours, native hardware modes, OHC animations (Direct mode), a device test mode, ENE-DRAM cold-start reinitialisation and a saved startup profile.

### Wallpaper Engine for KDE

Reads only local Steam Workshop metadata, selects wallpapers through Plasma's official scripting configuration and controls playback through the local D-Bus object of the separately installed CaptSilver plugin. Guided setup covers Steam, Workshop, KDE helpers and the plugin; on Fedora the optional RPM remains SHA256-verified and needs a second confirmation before Polkit/DNF.

## Version history

**3.4.29.160** – Public build with OHC-only designs, feature maturity labels and hardware-independent UI release coverage.

**3.4.29.159** – Publication candidate with the OHC-only design catalog and feature maturity labels.

**3.4.29.158** – Correct OpenRGB profile-callback synchronization and a stable GPU-clock boundary guard.

**3.4.29.157** – Programs/profiles, complete GitHub downloads and automatic recovery of OHC's own Levita daemon.

All earlier versions back to 2.9.x: [CHANGELOG.md](CHANGELOG.md) and [docs/releases/](releases).
