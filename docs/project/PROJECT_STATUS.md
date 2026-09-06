# Open Hardware Control — Project Status

**Current development version:** 3.4.29.47 STABLE

**Status date:** 06 September 2026

**Release channel:** STABLE — public release scripts may run only after the complete release checks, clean commit and explicit owner request.

Version 3.4.29.47 completes the repository reorganisation: all application code (`*.py`, `assets/`, `modules/`, `test-gifs/`) lives in `src/`, which mirrors the flat installed application directory; `install.sh`, `uninstall.sh`, `VERSION` and `BUILD_CHANNEL` live in `packaging/`; `INSTALL.md`, `CHANGELOG.md` and `README.en.md` in `docs/`; the full agent instructions in `docs/ai/AGENTS.md` (the root `AGENTS.md` is a short pointer); `SECURITY.md` in `.github/`. Installed layouts and package contents are unchanged. Tests import from `ROOT / "src"`, the registry validator scans `src/modules/`, and `install.sh` resolves `src/` from both the ZIP root and `packaging/`.

Version 3.4.29.46 stops the minutely `openrgb --client --list-devices` background inventory while the main window is hidden in the system tray and no RGB startup profile, write enable or scheduled retry is pending; the guard is covered by `tests/test_rgb_inventory_tray_guard_342946.py`. The repository was reorganised into `docs/project`, `docs/ai`, `docs/hardware`, `docs/security`, `docs/releases`, `packaging/` and `.github/`; `install.sh` and `scripts/build_release.py` still install a flat application directory, and `app_constants.helper_script_path` resolves helper scripts in both layouts. The README gained a clickable seven-screenshot gallery, installation near the top and a four-version history.

Version 3.4.29.45 keeps a saved RGB start profile pending while the managed OpenRGB engine reports its known cold-start partial inventory. The bounded inventory retry can now discover the complete controller set and apply the saved design instead of losing the one-shot profile start. The module-registry validator also follows the declared `packaging/BUILD_CHANNEL`, removing the internal-only gate that previously rejected a valid stable candidate. Stable RPM source preparation now uses a dedicated temporary parent instead of colliding with the identically named runtime ZIP tree. The bundled Levita gallery adds eight owner-created AI backgrounds and one deduplicated 30-second owner-created animation through an explicit allowlist; no manufacturer/TRCC catalog media is present. The clean-runner preview-queue regression cancels and clears constructor thumbnail work before measuring its synthetic 140-video load, removing the final runner-speed race. This version promotes the tested 3.4.29 feature line to the stable release channel.

Version 3.4.29.42 advances the Wallpaper Engine for KDE module to 1.2. Pause, resume, next and mute target `/WallpaperEngine` on Plasma's existing `org.kde.plasmashell` bus service, matching the object exposed by CaptSilver v1.4 even when its optional standalone alias cannot be registered. Because v1.4's advertised Previous method currently advances instead, OHC's back button safely selects the preceding validated local Workshop entry. The page also reads and applies DisplayMode 0/1/2 per selected screen. The main window defaults to Qt's primary screen, persists an optional exact screen name with primary fallback, and repositions restored geometry before display where the compositor permits it. A global eight-pixel scrollbar style makes all pages consistent. Existing hardware ownership and Wallpaper/Steam immutability boundaries are unchanged. The complete two-version backup remains mandatory.

## Current objective

Continue Open Hardware Control as a modular Linux hardware-control application while preserving the mature NZXT Kraken path and expanding validated integrations without introducing competing hardware writers.

Version 3.4.29.42 keeps the guided setup and optional verified Fedora installer from 3.4.29.41. It never modifies Steam Workshop files or an installed CaptSilver plugin in place, rejects selecting the Steam library itself as the recursive personal-video folder and never handles administrator credentials. Playback and scaling remain explicit user actions delegated to the plugin through Plasma.

A theme-matched client-side main-window title bar remains deferred. The current KWin decoration stays in place until system move/resize, maximize, keyboard accessibility, Wayland/X11 and minimized tray startup have dedicated regressions.

Version 3.4.26 adds a repository-native AI development layer so Cursor, Codex, Claude Code and future coding agents can recover project context from files rather than depending on one long chat.

Version 3.4.29 adds a local-first Thermalright Levita Vision display studio to the LCD page. It imports user-selected local media and TRCC layout folders, provides a safe preview/test mode and delegates real USB communication to the separately installed GPL TRCC Linux backend.

Version 3.4.29.7 suppresses the OHC native window surface before a KDE/Wayland tray-autostart UI is constructed, closing the photographed black-window flash, and makes every OpenRGB Qt client invocation headless as a second window-suppression boundary. It also adds user-facing grant/remove controls for an optional exact-user Polkit rule so the fixed, bounded NCT6687 helper can be authorized once across reboots without storing a password.

Version 3.4.29.8 makes the persistent-fan grant observable through a root-owned readable status marker, adds driver-gated PWM/DC selection and per-fan/global curve presets without weakening calibration, and brings the Levita editor in line with the photographed 80-pixel centered layout. Media is prepared aspect-correct at 1600×720, the mask is directly draggable, overlays have one-step history, local themes are grouped, metric units survive TRCC rendering, and rectangular hardware hides the round Kraken preview. Offscreen UI tests are now explicitly hardware-free; an unexpected managed OpenRGB crash is quarantined until a manual retry.

Version 3.4.29.9 replaces the provisional local theme groups with TRCC Linux's exact current cloud catalog: Gallery `a001–a082`, Tech `b001–b025`, HUD `c001–c072`, Light `d001–d055`, Nature `e001–e054` and Aesthetic `y001–y010`. Local media and layout folders are classified only from a validated in-range original ID and sorted numerically; unrelated names remain custom files. This stays entirely local and neither downloads nor packages manufacturer media.

Version 3.4.29.10 adds a true two-layer Levita composition path: a local video background can run behind an independently selected complete TRCC hardware-data layout whose sensor values remain live. Theme mask art is alpha-composited with the rounded right-hand Levita bar, and the combined layers are previewed in-app. The version also adds the media hover card and closes the remaining empty-window startup path by forcing synchronous OpenRGB version/inventory subprocesses offscreen.

Version 3.4.29.11 instruments the still-unidentified empty startup window without weakening Wayland isolation. Every OHC top-level/dialog/popup/tool window and native Qt surface event is written to the visible and persistent startup logs; Python and Qt helper launches record privacy-bounded command shape plus `QT_QPA_PLATFORM`. It also corrects the Levita bar so only the corners facing into the display are rounded, adopts the new project logo and compact desktop icon, and automatically exposes installed 1600×720 TRCC layouts as direct or multilayer live-data designs.

Version 3.4.29.12 rebuilds the Levita studio around category and design cards, moves bounded local video animation into the main 1600×720 canvas, packages three project-owned backgrounds and persists both selected layers. An explicit opt-in Levita autostart waits for desktop readiness, retries once and remains blocked by test mode. Broad TRCC imports now reject incompatible live-layout geometry. Qt's desktop-file identity plus `StartupWMClass` fixes Plasma association for the running taskbar icon.

Version 3.4.29.13 separates the remembered custom design directory from the standard catalog and makes inclusion reversible without deleting user files. Complete live-data themes are isolated in layer 2 unless explicitly moved, video cards gain cached still/hover previews, and the Levita receives independent real TRCC brightness/orientation controls. USB design swaps now stop the renderer gracefully, wait for endpoint release, reject overlap and retry one confirmed handshake timeout only once. Chassis-fan presets move to the summary card while calibration/activation safeguards remain unchanged.

Version 3.4.29.14 removes the remaining synchronous Levita video-thumbnail extraction from the Qt UI thread. A visible queue runs at most two `ffmpeg` workers, prioritizes the selected video and stores successful results in a source-versioned persistent cache for later application starts. Recent decoding failures are cached temporarily so broken media cannot repeatedly flood the process table.

Version 3.4.29.15 makes the lower main preview a centered, exact-aspect 1600×720 Levita stage instead of a full-width graphics viewport. Layer-2 cards preserve image/video backgrounds and always trigger a combined refresh; layouts without a separable `00.png`/`Theme.png` pair fall back to their complete theme preview.

Version 3.4.29.16 deduplicates the Levita catalog by complete case-insensitive filename. It deterministically retains the normal/short path over nested backup copies, migrates saved duplicate selections and reports the hidden count without deleting or modifying any user file. The newest startup trace also identifies the black surface as an OHC-owned, parentless, unnamed, non-modal 640×480 `QFrame`; that exact signature is quarantined before painting while richer object, ancestry, child, layout, timing and process-correlation evidence remains in both logs.

Version 3.4.29.17 fixes the KDE Plasma system-tray branding path itself. The tray no longer requests the unrelated `preferences-system-cooling` theme icon and instead receives OHC's project-owned 22/32/48/64 raster set; packages install the new native 22-pixel icon alongside the existing application sizes.

Version 3.4.29.18 makes every logical Levita layer-2 data block independently draggable, adds whole-layer X/Y offsets and provides right-click editing for color, font size and text/label. Labels, live values and units represented by one format remain one indivisible block. OHC stores overrides separately and stages generated `trcc.json` cache themes without modifying imported `config1.dc`. The first versioned feature folder, mandatory module register and enforced file-size budgets establish the gradual local-AI-oriented architecture path without a broad monolith rewrite.

Version 3.4.29.19 fixes the first real apply regression found in 3.4.29.18: OHC's generated editable cache contains a native `trcc.json`, which TRCC Linux supports, but the older OHC preflight still required `config1.dc`. The preflight now validates either legacy DC or bounded 1600×720 native JSON before emitting `load-theme`. Existing cache paths work without regeneration. Layer selection also avoids rebuilding hundreds of background cards and duplicate preview refreshes.

Version 3.4.29.32 restores readable left navigation in the light theme, moves the LCD “Design anpassen” panel to a right-hand column beside the live preview, and lays out layer-1/2 design cards in a full-width 4–8 column grid. The Levita data-surface module remains 1.4.

Version 3.4.29.33 persists the selected RGB card and per-design colours, adds a bounded four-attempt ENE-DRAM cold-start sequence, and reorganizes the Levita library as two large side-by-side layer panels with custom-folder assignment and favourites. The notch is migrated once to its physical 80-pixel minimum for maximum image area. Two original project-owned space layouts provide a free visual and a complete CPU/GPU/VRAM dashboard. About and Help now expose a readable supported-device list and direct component links, while the default UI scale and common padding are reduced. The Levita data-surface module remains 1.4.

Version 3.4.29.34 restores OHC's private editable Levita cache as a valid runtime theme source without weakening the no-symlink boundary for external imports. Controlled program exit now stops the stream and performs one daemon-only, offscreen `stop-video` request with a 1.5-second ceiling, returning the display to its active TRCC theme. The Levita data-surface module remains 1.4.

Version 3.4.29.35 repairs the stale TRCC-daemon state reproduced after a physical Levita unplug. TRCC reported `connected=True` from a cached handshake while its BulkLcd transport rejected every frame as not connected; asynchronous ticks nevertheless claimed success. OHC now serializes a tolerated detach and mandatory fresh connect before every explicit design apply, colour test and independent display-settings write. The attached panel completed a real 1600×720/model-64 handshake, four-colour transfer and saved-theme restore after this sequence. The Levita data-surface module remains 1.4.

Version 3.4.29.31 makes the LCD “Design anpassen” panel readable after the 3.4.29.30 radius work was already released: number fields and combo boxes keep a usable size, the black-bar checkbox occupies its own full-width row, and window diagnostics detach from the log widget before Qt destroys it. The Levita data-surface module remains 1.4.

Version 3.4.29.30 rounds the right edge of the selected image/video where it meets the black camera/notch bar. Top and bottom default to 48 px and can be adjusted together or independently from 0 to 240 px in the embedded Levita controls. Preview and generated hardware mask use the same pure geometry; the red guide drawn on the reference photo is not part of the UI or rendered output. The sole-USB-owner daemon, IPC-only video ticker and explicit combined-mask activation from 3.4.29.29 remain unchanged. The changed geometry contract raises the Levita data-surface module from 1.3 to 1.4.

Version 3.4.29.27 fixes the remaining black layer-1 preview. Editable `01.png` layer artwork now keeps its alpha channel while being fitted to the 1600×720 canvas instead of being flattened onto opaque black above the selected background. Selected videos use a new bounded 16-frame preview generation at 4 FPS and animate directly in the large canvas. A TRCC process crash is distinguished from an ordinary command error, stops automatic USB retries and is reported as the external backend/libusb failure demonstrated by the supplied coredump. The Levita module remains 1.4 because its data/canvas contract is unchanged.

Version 3.4.29.26 prevents rapid complete Levita design changes from exhausting the panel's bulk-USB handshake response. The selected video, generated panel mask and editable live blocks are linked into one OHC cache theme and applied by one connected `load-theme` process. Requests within the ten-second post-start protection interval are coalesced to the latest selection. A handshake timeout receives at most one retry in total; nested startup retries no longer keep addressing an enumerated but unresponsive endpoint. The Levita module is 1.4.

Version 3.4.29.25 makes GitHub authorization unambiguous for future coding agents. `BUILD_CHANNEL=INTERN` continues to block public tags and releases, while a normal push to a tested non-release development branch or an explicitly requested pull request is permitted only after a concrete project-owner request. Pull requests, tags, releases, force-pushes and remote deletion remain separate actions that never inherit permission from a normal branch push.

Version 3.4.29.24 integrates and revalidates the internal 22/23 bugfixes in the complete repository. Imported layouts skip only malformed records, TRCC discovery rejects symlinked config/artwork, split mode safely defaults to Off, renderer success waits for `QProcess.started`, failed autostart retains one bounded retry, and shutdown terminates the hover-preview timers/process. The versioned Levita module is 1.2. Runtime and developer package profiles are now validated separately so the developer ZIP cannot silently omit tests, release scripts, workflows or tools.

Version 3.4.29.23 introduced the renderer-start confirmation, safe split fallback and hover-preview shutdown fixes in an incomplete comparison archive. Version 3.4.29.22 introduced malformed-record recovery and stricter no-symlink theme discovery. Both intermediate histories are retained in release notes, while 3.4.29.24 is the first integration against the full test and script inventory.

Version 3.4.29.21 finishes the Levita studio geometry and the immediate Ebene-1 preview. The camera/notch bar keeps a straight inner edge; only the two outer-right 1600×720 display corners are rounded, matching in the editor and in prepared cache images. Clicking a background card paints its image or cached first video frame in the same event instead of leaving a black preview. The layer-2 module was 1.1.

Version 3.4.29.20 aligns editable preview geometry with TRCC's centre-based text coordinates and keeps draggable scene items alive while video frames update only the background. Re-selecting the current media card reloads both preview layers immediately, and the last valid video frame remains visible during asynchronous preparation. Right-click requests an integrated editor beside the canvas for colour, font size, text and block reset; applying or cancelling hides it without opening a separate top-level dialog. The dashboard now gates the Kraken coolant card on both an actual Kraken connection and a real liquid-temperature value, while preserving the user's saved card preference.

The 3.4.29 codebase has also begun an incremental local-AI-oriented split of the historical `src/kraken_control.py` monolith. The executable remains compatible, while independent constants, temperature helpers, privacy logging, the serial command backend, cooling widgets and localization/help data now live in focused modules documented by `MODULE_MAP.md`.

## What 3.4.29 adds so far

- Hotfix 3.4.29.1 restores application startup by importing both private localized LCD/About source strings that were missed during the first modularization pass. A real offscreen construction test now builds all 11 main pages without initializing hardware.
- Hotfix 3.4.29.2 removes the graphical Qt dependency from the desktop-shell stop path, skips obsolete Kraken LCD profile writes on Levita systems and synchronizes manual controls with an activated temperature curve.
- The personal Thermaltake PC view now migrates its AIO labels to Thermalright Levita Vision 360 and records the Jungle Leopard GPU support as Airgoo Channel B6 with 24 LEDs, independently from both ENE-DRAM modules.
- Hotfix 3.4.29.3 keeps one narrowly validated Polkit fan-helper session alive after explicit authorization, so a running CPU curve no longer times out after the authorization cache expires. It also skips unnecessary liquidctl initialization on Thermalright-only systems, hides obsolete Kraken clock controls and learns a stable 7-to-6 OpenRGB inventory change without weakening the large-drop cold-start safeguard.
- Hotfix 3.4.29.4 fixes startup when the LCD studio restores a saved TRCC media directory before the main Log page exists. The regression now starts the complete UI with a persisted real image. TRCC Linux 9.9.11 has also physically completed the red/green/blue/black cycle on the reference `87ad:70db` display; its full handshake confirms model ID 64, sub-byte 3 and 1600×720.
- Hotfix 3.4.29.5 resets TRCC's persisted decorative split mode to zero before loading media. This avoids the confirmed TRCC 9.9.11/PySide6 6.11 `QImage.mirrored()` crash; styles A–C stay available as clearly marked local previews, while the physical 80-pixel right cutout remains protected.
- Version 3.4.29.6 applies a real adjustable black TRCC mask over the camera/notch area instead of merely drawing a preview guide. Its wider 320-pixel reference default, persistent background X/Y shift and two overlay spacing presets remain user-adjustable; locally prepared image/video copies never overwrite imported originals. Formats that already include `°C` or `%` now suppress TRCC's second unit suffix.
- Hotfix 3.4.29.7 prevents the photographed black OHC surface during minimized KDE/Wayland autostart, keeps every OpenRGB CLI process offscreen and offers explicit persistent-fan-authorization grant/remove controls without storing a password or weakening PWM calibration.
- Hotfix 3.4.29.8 adds kernel-reported PWM/DC selection, individual/global fan presets and curve reset; reliable persistent-authorization state; aspect-correct Levita media, direct mask drag, overlay undo, categorized local themes and visible metric units; device-aware LCD tiles; hardware-free UI tests; and session quarantine after an unexpected managed OpenRGB crash.
- Hotfix 3.4.29.9 mirrors TRCC Linux's exact Gallery/Tech/HUD/Light/Nature/Aesthetic catalog and ID ranges, numerically orders recognized local themes and leaves every unrecognized file under custom media without any runtime download.
- Hotfix 3.4.29.10 adds separate Levita video/hardware-data layers, preserves theme masks while adding the rounded right bar, adds an in-app media-list hover preview and completes offscreen coverage for every OpenRGB startup query.
- Hotfix 3.4.29.11 adds temporary window/helper-process diagnostics, the new full/compact branding, automatic installed TRCC 1600×720 design discovery and direct `config1.dc` value adoption, and corrects the Levita radius direction while keeping the outer panel edge flush.
- Hotfix 3.4.29.12 adds the card-based Levita library, animated main preview, three original OHC backgrounds, explicit saved two-layer display autostart with one bounded retry, strict broad-import geometry filtering and reliable Plasma window-icon association.
- Hotfix 3.4.29.13 adds reversible custom-folder inclusion, strict background/data-theme separation with explicit layer moves, card video previews, independent Levita brightness/orientation, serialized timeout-aware USB switching and aligned top-level chassis-fan presets.
- Hotfix 3.4.29.14 moves every Levita video-card still into a bounded background queue, displays progress and persists source-versioned results across starts.
- Hotfix 3.4.29.15 centers the exact-aspect Levita preview and guarantees that selected layer-2 layouts remain visible over image or video backgrounds.
- Hotfix 3.4.29.16 collapses repeated filenames to one deterministic catalog card while keeping every original file untouched, and blocks only the exact observed OHC-owned blank 640×480 frame while preserving deeper diagnostics.
- Hotfix 3.4.29.17 gives the Plasma system-tray entry the compact OHC emblem at a native 22×22 size instead of the generic cooling theme icon.
- Hotfix 3.4.29.18 adds independently draggable and context-editable layer-2 blocks, whole-layout offsets, read-only TRCC adaptation and the mandatory versioned module registry.
- Hotfix 3.4.29.19 restores native-JSON editable-theme transmission and removes redundant preview/catalog work during layer selection.
- Hotfix 3.4.29.20 fixes centre-coordinate preview alignment, uninterrupted dragging over animated backgrounds, an embedded no-popup block editor, immediate background reload and automatic hiding of unavailable Kraken coolant data.
- Hotfix 3.4.29.33 persists RGB design choice/colours, adds bounded ENE-DRAM delayed start recovery, reorganizes Levita layers with imports/favourites, bundles two original space layouts and improves global scale plus About/Help.
- Hotfix 3.4.29.34 restores internally staged Levita themes and returns the display to its active TRCC theme on controlled application exit.
- Hotfix 3.4.29.35 replaces stale Levita daemon transports with a confirmed fresh handshake before design, test and display-settings writes.
- Hotfix 3.4.29.32 restores light-theme sidebar contrast, places Design anpassen beside the Levita preview and fills design galleries with 4–8 cards per row.
- Hotfix 3.4.29.31 makes Design anpassen controls readable and detaches window diagnostics from a destroyed log widget on shutdown.
- Hotfix 3.4.29.24 integrates and fully tests the 22/23 Levita parser, symlink, safe-default, process-start and shutdown fixes; package-profile validation protects the complete developer inventory.
- Hotfix 3.4.29.23 confirms renderer startup and closes hover-preview processes on shutdown.
- Hotfix 3.4.29.22 preserves valid blocks after malformed imported elements and rejects symlinked theme files.
- Hotfix 3.4.29.21 paints a selected Ebene-1 card immediately, rounds only the outer-right display corners and keeps the notch inner edge straight.

- Full-width Thermalright Levita Vision studio inside the existing LCD page.
- Two-layer Levita renderer flow: `load-theme` adopts the imported `config1.dc` layout, then `play-video` replaces only its background so live values remain above the animation.
- Local-only import for images, videos, `.zt` media and complete TRCC layout directories containing `config1.dc`; imported manufacturer assets are neither copied nor packaged.
- A true 1600×720 editor with aspect-preserving contain/cover modes, a real directly draggable 80–800-pixel black right-hand mask (80-pixel photographed reference default), background X/Y movement and matching dynamic protection for movable hardware values.
- Movable, hideable, resizable and recolorable CPU temperature/load, GPU temperature/load, memory and clock overlays.
- Test mode enabled by default: previews and the local color-cycle test perform no USB writes.
- Hardware detection, color test, media/theme loading and the live metric render loop use bounded shell-free commands through the separately installed TRCC Linux backend. Decorative split modes remain preview-only until the confirmed TRCC Qt compatibility defect is fixed.
- Exact Thermalright Levita Vision 360 ARGB Black cooling identity with separate, user-confirmed motherboard mappings for its 4-pin PWM pump and radiator fans.
- Conservative cooling profiles and CPU-temperature curves become writable only after both relevant headers have passed the existing 70-percent/10-second physical test. CoolerControl ownership remains exclusive and OHC restores firmware control on exit.
- ENE-DRAM cold-start reclaim now runs two ordered Direct passes before profile animation, because the latest real log confirmed that one successful protocol pass can still leave the physical LEDs asleep.
- The previous 3.4.28 chassis-card behavior, modularization, CoolerControl ownership, application-wide blue design and confirmed Kraken profiles remain intact.

## What 3.4.26 adds

- Root `docs/ai/AGENTS.md` as the primary durable agent instruction set.
- `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `docs/hardware/DEVICE_SUPPORT.md` and `docs/ai/AI_HANDOFF.md` as maintained project memory.
- Cursor project rules under `.cursor/rules/`.
- Cursor slash workflows under `.cursor/commands/`.
- Project-level Cursor hooks with session context injection and destructive-command confirmation.
- Release/publish scripts that enforce release channel, clean-worktree, authentication and test requirements without an external backup dependency.

## Current major modules

- NZXT Kraken control: `src/nzxt_backend.py`, `src/kraken_sensors.py`, `src/kraken_cam_streamer.py`, `src/kraken_lcd_designs.py`, `src/nzxt_rgb.py`, `src/nzxt_esc_profiles.py`.
- Main GUI and orchestration: `src/kraken_control.py`, `src/cooling_widgets.py`, `src/localization_catalog.py`, `src/ui_layout.py`.
- Shared application infrastructure: `src/app_constants.py`, `src/temperature_utils.py`, `src/privacy_logging.py`, `src/window_diagnostics.py`, `src/command_backend.py`.
- Hardware request coordination: `src/hardware_request_coordinator.py`, `src/cooling_ownership.py`.
- Mainboard fan control: `src/mainboard_fan_control.py`, `src/ohc_fan_helper.py` plus Polkit policy.
- Thermalright display/cooling: `src/modules/lcd_levita/v1_4/`, `src/thermalright_display.py`, `src/thermalright_display_ui.py`, `src/thermalright_cooling.py`.
- Corsair/OpenLinkHub: `src/openlinkhub_integration.py`, `src/openlinkhub_mouse_visuals.py`.
- RGB/OpenRGB: `src/openrgb_integration.py`, `src/openrgb_sdk.py`, `src/rgb_devices.py`, `src/rgb_effects.py`.
- Desktop customization: `src/desktop_shell.py`, `src/desktop_designs.py`, `src/desktop_assets.py`.
- Release/security tooling: `scripts/` and `.github/workflows/`.

## Important current product behavior

- Persistent sidebar customization supports drag/drop and per-module visibility.
- Overview, Navigation customization and Help are permanent and cannot be hidden or removed.
- Cooling UI uses compact system-fan cards and embedded curve editing.
- Mainboard chassis fans default to CPU temperature for untouched legacy defaults and retain calibration/safety ownership logic.
- RGB Studio manages a private loopback OpenRGB engine and isolates conflicting/external writers.
- Corsair remains mediated through local OpenLinkHub rather than direct, guessed Corsair USB writes.
- LCD/GIF and Kraken hardware requests remain coordinated so simultaneous subsystems do not fight for the same device.

## Confirmed next work and 3.4.29 progress

- RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About and Help now share the current blue-tinted dashboard surface design.
- Kraken quick-profile buttons now track the last fully successful Leise, Ausbalanciert or Leistung write instead of displaying a static default.
- Mainboard chassis-fan cards keep their internal channel selection separate from visible expansion; all cards start collapsed and at most one explicitly opened card is expanded.
- CoolerControl ownership now distinguishes the `coolercontrold` background daemon from the closed graphical client, reports its autostart state and provides confirmed controls for temporary takeover or permanent service disable/enable.

## Known boundaries / not automatically claimed

- Hardware support beyond explicitly tested devices remains provisional until real-hardware verification.
- Thermalright Levita hardware support remains provisional: local editor/import/test mode, USB detection and read-only PWM/RPM discovery are verified. The physical display write via `trcc` and actual PWM response still require an in-app user confirmation; OHC therefore keeps every write behind explicit calibration.
- Firmware flashing/version switching is not a supported feature in this repository.
- GPU fan control is not part of the mainboard PWM subsystem.
- Open Radeon Control Center remains separate.

## Before publishing 3.4.29.47

- Keep `BUILD_CHANNEL=STABLE`; return to `INTERN` if the real desktop/hardware release-candidate test exposes a regression.
- Run all release checks.
- Verify current documentation/version references.
- Confirm no secrets/personal logs are present.
- Require a clean committed state and explicit project-owner approval before any GitHub push/tag/release.
