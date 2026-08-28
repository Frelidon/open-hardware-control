# Open Hardware Control by Frelidon 3.4.27 INTERNAL

<!-- project-badges -->
[![CI](https://github.com/Frelidon/open-hardware-control/actions/workflows/ci.yml/badge.svg)](https://github.com/Frelidon/open-hardware-control/actions/workflows/ci.yml) [![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](LICENSE) [![Release](https://img.shields.io/github/v/release/Frelidon/open-hardware-control?display_name=tag)](https://github.com/Frelidon/open-hardware-control/releases)
<!-- /project-badges -->

Open Hardware Control is a free Linux GUI for the **NZXT Kraken LCD**, pump, radiator fans and RGB, for **calibrated motherboard/case fans through Linux hwmon/NCT6687**, with **Corsair integration through OpenLinkHub** and additional RGB devices through an automatically managed local hardware engine. It targets Fedora, Nobara, Debian, Ubuntu, Linux Mint, Arch Linux, Manjaro, EndeavourOS and openSUSE.

![Open Hardware Control dashboard](docs/images/screenshots/01-dashboard-overview.png)

<!-- project-repository -->
Project repository: <https://github.com/Frelidon/open-hardware-control>
<!-- /project-repository -->

> **Unofficial independent community project:** Open Hardware Control is not supported, approved, endorsed, operated by, or affiliated with NZXT, Corsair, be quiet!, OpenLinkHub, OpenRGB, or any other named manufacturer or project. Product and brand names are used only to describe compatibility. Manufacturers and rights holders can contact Frelidon through the public contact address in the GitHub profile or the Steam username **Frelidon**.

Version 3.4.27 INTERNAL combines clearer CoolerControl management with consistent blue-tinted cards and honest Kraken-profile feedback. OHC distinguishes a closed graphical client from the still-running `coolercontrold` service and only marks a Kraken quick profile after successful hardware transmission.

## New in 3.4.27 INTERNAL

- Separate status for the active CoolerControl background daemon and system autostart.
- Confirmed Polkit actions for temporary OHC takeover, persistent disable, or re-enable and immediate start of CoolerControl.
- Safe handoff: disabling CoolerControl never starts OHC fan control automatically; enabling CoolerControl first returns motherboard channels to firmware/BIOS ownership.
- Consistent blue-tinted surfaces across RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About, Help and Kraken details.
- Silent, Balanced and Performance only become fully blue after successful pump and fan writes.
- Complete local-AI handoff for LM Studio/Qwen2.5-Coder with a start prompt, repository rules and guarded GitHub workflow.

## New in 3.4.26 INTERNAL

- Durable AI project memory through `AGENTS.md` plus status, architecture, decision and device-support documents.
- Cursor project rules, slash commands and a session-start hook for reliable handoffs between fresh chats.
- Release validation for version, channel, tests, privacy and reproducible artifacts without an external backup dependency.
- Destructive shell/Git commands require explicit confirmation in Cursor.

## New in 3.4.25 INTERNAL

- compact dark dashboard shell with persistent OHC sidebar and page titles
- no “Community Edition” branding; OHC remains one unified open-source application
- redesigned overview with compact metrics, quick actions, detected hardware and status hints
- separate CPU/Kraken and chassis-fan summary cards in Cooling
- direct Test / Curve / Assign actions on each chassis-fan card
- dedicated fan-curve dialog instead of a distant editor section
- CoolerControl ownership banner directly below the cooling summaries
- four-step fan mapping assistant: Detect, Test, Assign, Save
- dark theme is the default for fresh installs; existing explicit theme settings are preserved
- real PySide6 offscreen GUI smoke test added to the internal release workflow

Version 3.4.23.2 INTERNAL redesigns Cooling around compact CPU/Kraken and chassis-fan cards. Chassis fan headers are shown as individual cards with RPM/PWM, profile, sensor source and curve preview, while CPU_FAN/PUMP_FAN stay in the dedicated Kraken area. CoolerControl ownership is detected to prevent concurrent PWM writes, and a new guided chassis-fan assistant combines a safe contrast test, optional white RGB identification and shared RGB/PWM case-layout mapping.

Version 3.4.23 INTERNAL adds safety-gated motherboard fan control through Linux hwmon/NCT6687. PWM channels are never guessed: each channel must first be briefly tested and physically confirmed. Confirmed channels can then use independent sensor sources, curves, minimum duty, hysteresis and response delay. RGB Studio also exposes ENE-DRAM cold-start initialization and a manual reinitialize button.

## New in 3.4.23.2 INTERNAL

- Compact Cooling dashboard with separate CPU/Kraken and chassis-fan detail cards.
- CPU_FAN/PUMP_FAN are excluded from chassis control and remain in the dedicated Kraken cooling path.
- Chassis fans use full-width cards with RPM, PWM, sensor source, preset and graphical curve preview instead of a nested scrolling table.
- CoolerControl ownership detection prevents concurrent hwmon/PWM writes; explicit takeover/release uses systemd/Polkit.
- Guided chassis-fan assistant with a safe 30%/80% ten-second contrast test, full state restoration, optional 100% white RGB identification and shared RGB/PWM case-layout mapping.
- Persistent PWM-to-case-position assignments integrate with Quiet/Balanced/Performance profiles.

## New in 3.4.23 INTERNAL

- Motherboard fan control through Linux hwmon, with focused NCT6687/NCT6687D and MSI X870-family support.
- Safe calibration: a selected PWM channel is set to 70% for five seconds, then its previous hwmon state is restored; automatic control remains blocked until the user confirms the physical fan group.
- Per confirmed channel: custom name, CPU/GPU/liquid/max/weighted CPU-GPU sensor source, minimum duty, hysteresis, response delay and individual fan curve.
- 70% sensor-failure fallback and 100% emergency request at 90 °C; disabling OHC control or exiting returns channels to firmware/BIOS control where the driver exposes it. When the current nct6687d driver exposes `fan_control_watchdog`, OHC also refreshes a 10-second driver lease so the driver can restore original curves if the controlling process disappears.
- Driver/Secure Boot diagnostics and Fedora NCT6687 setup guidance; OHC does not bypass Secure Boot/MOK and does not write unverified controller registers directly.
- RGB Studio shows ENE-DRAM initialization status and provides an “Reinitialize ENE RAM” action that repeats the proven OpenRGB Direct reclaim.

## New in 3.4.22.1 INTERNAL

- ENE-DRAM/OpenRGB stability hotfix: the long-lived Direct SDK worker is no longer killed by native NZXT/GPU writes.
- The selected Direct device in RGB test mode can force one fresh prepare/Custom-Direct claim, allowing OHC to recover a latched ENE DRAM state without opening the OpenRGB GUI first.
- Animated RGB designs are only marked active after both the first complete Direct SDK frame and all native/NZXT fallbacks have succeeded.
- LCD GIF regression fixed: `prepare_gif()` accepts the additional scale value introduced by the 3.4.21 UI, so bundled and custom GIFs start correctly again.
- The safe liquid-temperature fallback remains active after a failed LCD start.
- Loading the recommended AM5/Kraken profile now immediately activates both CPU-controlled pump and fan curves when a CPU sensor is available.

## New in 3.4.21 INTERNAL

- New central Kraken USB coordinator with request IDs, priorities, owner tracking, retry/error logging and latest-request-wins handling for replaceable LCD operations.
- Clicking a bundled LCD design activates it directly and cleanly replaces an already running LCD design.
- RGB Studio now has its own request coordinator: duplicate short-lived requests are coalesced, obsolete effect changes are dropped, and the long-lived SDK worker is reused.
- Saved RGB profiles are restored only after the OpenRGB device inventory has stabilized; devices that appear later can be brought into the active profile.
- Fixes the Quick Profiles widget that was accidentally created as a detached top-level window in 3.4.20. Tray autostart continues to suppress non-critical modal startup dialogs.
- During system shutdown or controlled exit, the LCD safety request gets critical priority: stop the animation and restore the liquid-temperature screen while USB access is still available.
- Imported NZXT-ESC profiles use a live renderer inside the existing CAM-Raw streamer instead of a slow static refresh path. Embedded ESC preview images are used as a visible base when external media stays blocked.
- LCD target resolution and rendering scale are derived from device capabilities rather than shipping duplicate copies of every design at many resolutions. Verified raw USB transport remains capability-gated for safety.
- Bundled LCD designs gain persistent scale controls, animated hover previews and an optional animated main LCD preview.
- LCD work tiles can be reordered again; long pages keep a compact preview available and middle-mouse scrolling improves navigation.
- Imported profile files use the current filename as the proposed profile name and handle naming collisions explicitly.
- Privacy/release checks are tightened to remove personal test labels and further anonymize diagnostic network identifiers.

## New in 3.4.20 INTERNAL

- ENE/OpenRGB RAM is primed into Direct/Custom exactly once per fresh RGB-worker session. This removes the observed need to open OpenRGB and touch the RAM once after boot while still avoiding repeated mode resets during effects.
- `--autostart` no longer opens setup, fan-profile selection, or other modal startup dialogs on the desktop. Pending setup is deferred until the user deliberately opens the main window.
- On a truly fresh installation, language selection is now the first setup page. German, English, Spanish, and French are applied immediately to the following setup pages.
- Fixed Help button at the bottom left plus `F1`: searchable built-in guides for first steps, LCD, cooling, RGB, profiles, OpenLinkHub, desktop designs, autostart, and diagnostics with direct jumps to the matching page.
- LCD workspace is consolidated further: preview/display/clock at the top, one static/animated content area with image/GIF import and bundled gallery, one hardware/layer area, and collapsed advanced FPS/transport diagnostics.
- Eight original, reproducibly generated OHC LCD GIFs are bundled in a selectable gallery: Nebula Vanguard, Ringworld Runner, Singularity Dive, Abyssal Bloom, Neon Rain, Magma Heart, Polar Aurora, and Firefly Grove.
- The clock can be added as an overlay to GIF/animated background + hardware-data streams, reusing the existing time format, date, font-size, and color settings.
- Current NZXT-ESC v3 exports using `preset.background`, `preset.overlay`, `elementType`, `transform`, and `config` are imported correctly. Embedded `previewImage` data is used as a safe preview/fallback; CSS `rgb()`/`rgba()` colors and current elements such as Metric, Text, Shape, Clock, Analog Clock, Radial Graphic, and Sensor Chart are recognized or approximated.
- External URL/video backgrounds are still never fetched automatically. This remains an intentional security boundary and is explicitly reported during import.

## New in 3.4.19 INTERNAL

- LCD is arranged as a three-column tile workspace instead of one long vertical stack; the large imported-profile manager spans the full width.
- Hardware animation and image/GIF + hardware-layer starts no longer render synchronously in the Qt process and directly use the existing external stream renderer.
- Brightness and orientation use the coordinated PAUSE/RESUME USB handoff while a CAM-Raw stream is active, preserving its frame cache.
- ENE/RAM Direct devices are no longer sent a redundant `SET_CUSTOM_MODE` when OpenRGB already confirms Direct mode.
- Discover/AppStream metadata now includes the application icon, detailed description, GitHub/issue links, search keywords, and screenshot gallery.
- The independent NZXT-ESC compatibility layer and profile library from 3.4.18 remain fully included.

- Independent importer for compatible `.nzxt-esc-preset`/JSON exports with schema-v3 support and tolerant recognition of older field aliases.
- Every import is gated by a preview showing directly supported, approximated, unsupported, and security-blocked elements before anything can be activated.
- Imported profiles are always new local OHC copies; the untouched import state is retained for one-click restoration.
- Profile library with activation, editing, rename, duplicate, delete, individual export, and complete ZIP backup/restore for profiles, previews, local media, fonts, and LCD profile settings.
- Reduced layer editor for sensor source, text, hex colors, sizes, position, rotation, visibility, locking, and drag-and-drop order. Unambiguous CPU/GPU text labels can follow a sensor remap automatically.
- OHC live data for CPU/GPU/liquid temperature plus best-effort Linux load, clock, power, RAM, fan RPM and pump RPM values. Missing sensors are shown safely as unavailable.
- Remote URLs, videos, web media, and NZXT-ESC fonts are never loaded automatically. OHC bundles no NZXT-ESC source code, presets, media, or fonts.

### Complex LCD designs and NZXT-ESC import

Open Hardware Control continues to grow its own LCD designs and graphical layer editor. Because the built-in selection is not intended to compete with a specialized design project, users looking for especially elaborate profiles may also want to look at the independent NZXT-ESC project:

<https://github.com/mrgogo7/nzxt-esc>

Profiles created or exported there can be loaded through Open Hardware Control's import function. Supported CPU, GPU, memory and liquid-cooling metrics are connected to OHC's own live data sources.

Open Hardware Control and NZXT-ESC are independent projects. Open Hardware Control does not include NZXT-ESC source code, bundled designs, fonts, or media. Imported designs and included media remain subject to their authors' respective rights and licence terms.

## New in 3.4.16 INTERNAL

- RGB speed, color, brightness, and direction edits are coalesced for 360 ms; the newest value always wins.
- In-flight NZXT/GPU transfers finish serially before the newest editor state is applied.
- Persistent SDK-worker acknowledgements are tied to the exact submitted frame, so an old frame cannot confirm a newer profile state.
- NZXT's five discrete speed levels are mapped evenly across 10–200%; 75% is now clearly `slower` and 100% `normal`.
- A read-only inventory check runs at most once per minute. A large 7 → 2 drop is confirmed twice while the last complete list remains visible.
- Unchanged background checks do not rebuild the workspace, preserving focus and scroll position.

## New in 3.4.15 INTERNAL

- A dedicated OHC mode list shows each effect, its description, and whether zero, one, or two user colors are meaningful.
- Every active color accepts a `#RRGGBB` value, a built-in color preset, or the normal color picker while remaining compatible with existing RGB profiles.
- RGB Studio now defaults to Engine, Devices and Effects, Thermaltake 360 PC layout, and Groups.
- Major sections in RGB, LCD, and Cooling can be dragged or moved with up/down controls. Each page stores its order and has a default-order reset.
- The dashboard remains the first app page and adds CPU model/topology plus GPU model, VRAM, driver, and PCI path. Every hardware card can be hidden and restored.

## New in 3.4.14 INTERNAL

- NZXT Alternating uses the confirmed two-color `fading` fallback instead of the failing `alternating-4` alias.
- OHC-owned OpenRGB clients no longer trigger a false foreign-process/reclaim loop.
- Asynchronous partial RGB failures are recorded in a bounded in-app list instead of modal pop-ups.
- The Thermaltake 360 template is visibly named “Frelidon PC” while retaining its compatible internal key.

## New in 3.4.13 INTERNAL

- Clicking a design tile immediately starts or transfers it; no second Start click is required.
- New “Solid Color” tile; selecting a new primary color reapplies it directly.
- Persistent, stronger tile outlines distinguish SELECTED from ACTIVE, while a prominent status panel shows the profile, color, and transfer state.
- New “Reclaim RGB control” button safely rebuilds the OHC write path and reapplies the selected pattern.
- Optional automatic recovery is off by default, only observes the separate OpenRGB process, and reapplies the pattern after that process has ended.
- OHC never terminates or writes through a separate OpenRGB process. An unknown or foreign SDK server continues to fail closed.
- The opt-in recovery setting is stored in RGB/full profiles; no automatic hardware access starts without a previously confirmed RGB grant.

## New in 3.4.12 INTERNAL

- Kraken channels 1/2/3 can be dragged into their physical order in the Thermaltake diagram.
- 17 original animated RGB presets grouped into six gallery categories.
- An explicitly opted-in startup profile can restore RGB ownership and its effect; separate OpenRGB and a second OHC instance still block it.
- LCD layers combine a still/GIF background with static or animated live hardware data.
- Three additional original LCD patterns: Neon Grid, Radar, and Liquid Core.

## New in 3.4.11 INTERNAL

- persistent loopback SDK worker instead of one Python process and TCP connection per device and animation frame
- one bounded multi-device frame per tick, 25 Hz target, exactly one in-flight request, and latest-frame-wins coalescing
- measured SDK rate, most recent successful transfer, batch duration, and coalesced-frame count per active device
- six-step RGB setup wizard for ownership, naming, isolated device tests, zone/LED calibration, case layout, and GPU mode
- per-zone visual test that makes the selected controller zone visible while its other zones are black
- automatic preference for Sapphire's reported External Control mode during non-Direct OHC animations
- static changes remain serialized and confirmed; physical ARGB output is still explicitly not electrically readable
- OpenRGB remains separately installed and privately managed; no OpenRGB drivers or Effects Plugin assets are copied

## Since 3.4.7 INTERNAL

- accepts SDK protocol 5 reported by OpenRGB `1.0~rc2` while retaining protocol 4 compatibility
- keeps the SDK endpoint loopback-only and all device, LED and packet bounds intact
- removes unsupported `marquee-4` and `moving-alternating-4` modes from the NZXT 2023 controller
- maps OHC comet to `pulse`, spinner to the validated rainbow flow and alternating to the two-colour `fading` fallback
- acquires a per-user kernel file lock before Qt or hardware initialization
- exits a second launch with a clear notice without opening OpenRGB, liquidctl, Kraken or another controller
- fails closed if the application lock cannot be created for another reason

## Since 3.4.6 INTERNAL

- large selected-device list with control path and last result
- separate GPU/device hardware-mode choice without accidental OHC effect fallback
- one-time `SETCUSTOMMODE` preparation per Direct device and engine lifetime
- per-device failure isolation, hidden NZXT mirror and multi-stage scroll preservation
- automatic current and previous session diagnostics logs

## Since 3.4.5 INTERNAL

- bounded loopback SDK writer for Direct devices outside OpenRGB CLI `ApplyOptions`
- complete editable Thermaltake twelve-fan layout with deterministic initial arrangement

## Since 3.4.4 INTERNAL

- ordered reset/engine restart and fresh discovery before write access is re-enabled
- safe collapse of the mirrored fourteen-entry inventory to seven actual reports
- large draggable Thermaltake PC overview with stored device mapping

## Since 3.4.3 INTERNAL

- recognizes the confirmed OpenRGB `ApplyOptions`/`stl_vector` process-abort signature
- quarantines only the crashing device until OHC is restarted; the block is not persisted
- continues serialized command sequences so device-test mode can still reach its final target
- counts ordinary Direct Mode failures per device instead of resetting them when another device succeeds
- quarantines on the first confirmed process crash or after three ordinary failures of that same device
- logs each detected OpenRGB index, user-visible name, LED count and Direct capability

## Since 3.4.2 INTERNAL

- fixes the immediate `AttributeError: rgb_preview_started` startup failure
- adds a regression check for preview-clock initialization before `build_ui()`
- writes privacy-filtered `startup.log` and `last-crash.log` files below the user's XDG state directory
- includes those records in the read-only diagnostics report

## Since 3.4.1 INTERNAL

- one OpenRGB device per serialized process; bundled repeated `--device` arguments are prohibited
- persistent selection/group state across delayed discovery and hotplug refreshes
- reported native hardware-mode fallbacks for devices without Direct Mode
- distinct and user-editable names for identically reported GPU/controller entries
- a dedicated device test mode that lights only one OHC-owned component, turns the others off, advances to the next device and exposes renaming directly
- a PC diagram with positions, counts, connector notes, groups and selected-device mapping
- built-in Frelidon profile for the Kraken radiator plus A1, A2, B6, B7 and SYS-FAN6
- all-select controls above and below the tile workspace
- NZXT `led1`–`led3` exclusively in the common tile workspace; the separate visible editor is removed
- profile persistence for aliases and PC layout; hardware start remains manual
- the complete reset button remains available

## Since 3.4.0 INTERNAL

- managed windowless RGB backend, device tiles, drag-and-drop groups, ENE DRAM alias filtering, NZXT topology validation and complete reset

## Since 3.2.0 INTERNAL

- direct Fedora 44 support for `qdbus-qt6`, without a compatibility link
- safe Qt 6 D-Bus command discovery across supported distributions
- one-time dependency offer plus a permanent install button in Desktop designs
- fixed DNF, APT, Pacman and Zypper package mappings with no third-party repositories
- automatic recheck and feature enablement after installation
- optional desktop tools never block hardware control

## Since 3.1.0 INTERNAL

- reversible Windows-11-style and macOS-style KDE Plasma 6 layouts
- no-change preview and explicit confirmation before applying
- timestamped backup, automatic rollback and manual restore
- dark and light modes using Breeze, Noto Sans and original GPL SVG wallpapers

Closing to the tray deliberately keeps LCD output and curve control running. A true quit stops the raw GIF streamer first, restores `lcd screen liquid`, then stores the conservative autonomous cooling fallback. Five in-project SVG families cover compact, ergonomic, symmetric, multi-button and MMO mice without vendor photos. Only buttons carrying a safe index reported by OpenLinkHub can be edited; the application never guesses one.

Mouse assignments use OpenLinkHub's documented assignment endpoint and remain locked until writes are explicitly enabled for the session. The macro recorder captures only individual keys and delays while its visible dialog has focus; it installs no global input hook. Cooling and safety logic continue to store Celsius internally, so switching the display to Fahrenheit cannot alter the physical thresholds.

Since 3.0.6, the active LCD mode is stored explicitly in full and LCD profiles. Legacy 3.0.5 profiles containing a GIF are migrated to GIF mode. A saved maximized window state can no longer reopen the hidden autostart window, while manual launches continue to open normally. Orderly desktop-session termination also clears the experimental crash marker before USB cleanup.

Both NZXT curves are now evaluated continuously from Linux hwmon. The controller interpolates between points, smooths short Ryzen temperature spikes, adds hysteresis and rate limits writes. It keeps reading the CPU during LCD GIF streaming and uses the coordinated USB handoff only for relevant duty changes. Existing liquid curves are migrated to safe CPU curves, all AM5 profiles provide updated CPU points, repeated sensor failure applies a 75% fallback, and a clean application exit stores conservative autonomous liquid curves in the Kraken.

CPU curves require the application to keep running. Closing to the system tray preserves control; a real exit installs the safe hardware fallback.

OpenLinkHub controls include reported cooling profiles and manual channel values, RGB profiles, brightness, labels, LCD rotation, mouse DPI/polling/sleep options, keyboard profile/layout/device values and headset ANC/sidetone options. Writes remain locked until explicitly enabled for the current application session.

Pump, radiator-fan, quick-profile and calculated CPU-curve writes use a short ownership handoff: the streamer finishes a frame and releases USB, the GUI sends the cooling transaction exclusively, and the same cached stream reconnects and continues automatically. Kraken status polling remains paused, while CPU sensing and CPU-curve evaluation continue through Linux hwmon.

## Highlights

- hierarchical left sidebar
- automatic device discovery and hardware-filtered modules
- optional display of undetected modules
- migration of existing Kraken Control settings
- OpenLinkHub installation, service-context and local-API detection
- Corsair device and telemetry view plus allow-listed documented write actions
- user-scoped OpenLinkHub start, stop and restart actions
- direct access to the local OpenLinkHub dashboard
- warnings for system context or two active services

## Installation

Fedora/Nobara RPM:

```bash
cd ~/Downloads
sudo dnf install ./open-hardware-control-3.4.27-0.intern2.noarch.rpm
```

Debian/Ubuntu/Linux Mint DEB:

```bash
cd ~/Downloads
sudo apt install './open-hardware-control_3.4.27~intern2_all.deb'
```

Universal ZIP for the supported distro families:

```bash
cd ~/Downloads
unzip open_hardware_control_v3_4_23_INTERN.zip
cd open-hardware-control-3.4.23-INTERN
chmod +x install.sh
./install.sh
```

The existing installation is updated in place and **Open Hardware Control by Frelidon** then appears in the application menu. See [INSTALL.md](INSTALL.md) for all distro-specific dependency commands.

The compatibility command `kraken-control` also launches the new application. OpenLinkHub is installed separately and is not bundled or modified by Open Hardware Control.

The OpenLinkHub adapter only accepts loopback URLs, exposes no full serial numbers in the UI or logs, validates every payload and never changes the system-wide service automatically. The OpenRGB adapter likewise accepts only `127.0.0.1:6742`, explicit SDK client commands and session-approved writes. It blocks devices already owned by the NZXT or OpenLinkHub modules.

See `Open_Hardware_Control_Projekt.md`, `OPENLINKHUB_INTEGRATION.md`, `RGB_STUDIO.md`, `RGB_SECURITY_AUDIT.md`, `SECURITY.md` and `SUPPORTED_DEVICES.md`. The complete NZXT module history remains in `Kraken_Control_Projekt.md` and `USB_CAPTURE_FINDINGS.md`.

Internal experimental beta, provided without warranty. Independent project, not officially affiliated with NZXT, Corsair, OpenLinkHub, Microsoft or Apple. GPL-3.0-or-later.
