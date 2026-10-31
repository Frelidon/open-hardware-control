# Open Hardware Control — Durable Decisions

## 20.10.26 – Profile-driven optimization; no full Rust rewrite

Open Hardware Control remains a Python/PySide6 application. Rewriting the whole
program in Rust would replace proven Qt behavior, hardware ownership, packaging
and regressions before a bottleneck is established. Performance work starts with
separate measurements for UI latency, worker runtime, cache I/O and display frame
gaps, then changes one bounded responsibility at a time. Blocking discovery,
decoding, network and package operations do not belong on the Qt main thread.

Large pages are reduced through versioned feature modules and pure policy/render
helpers while their public Python interfaces remain stable. Rust may be used only
for an isolated CPU-heavy pure kernel demonstrated by profiling; it must retain
the Python API, an equivalent Python fallback, shared fixtures and explicit DEB/
RPM support. It is not used to combine hardware writes, privileges or Qt object
ownership. Performance claims require a reproducible before/after measurement.

The active roadmap distinguishes repository work from optical or real-hardware
confirmation and long-term ideas. Completed implementation notes are historical
records, not an implicit backlog.

## 06.10.26 – Editable LED drafts and truthful fan previews (.156)

An optional path's commit checkbox must not prevent entering the draft needed
to enable it. Explicit mouse/keyboard gestures activate that draft; opening,
programmatic selection, count/test-index changes and Cancel never invent a
physical path. Explicit unchecking still removes the path on Save. Qt child
polish and inline reparenting must retain these mode-dependent controls.
Spatial direction describes visible travel, not a shared effect phase sign.
Physical chain order, clockwise ring orientation, effect reversal and per-header
direction remain independent. Unmapped headers keep their established local
frames; a global direction alone is no authority to create wiring geometry.
Fan colour previews may be schematic from a single declared header and existing
count, but must share the confirmed writer clock, stay bounded and stop hidden.
They do not claim real rotor speed, physical LED placement or optical readback.

## 06.10.26 – Preserve both distributions and separate stale setup from startup (.155)

Fedora and Ubuntu remain equal supported targets. Distribution-specific fixes
must be isolated, exercised with separate targeted regressions and retain the
other path's commands, features, design templates and settings. Never infer
the distribution from an available foreign package-manager binary. Record
unavailable real hardware tests as pending; an Ubuntu run or Fedora fixture
is not proof of live Fedora hardware compatibility.

A legacy NZXT assistant preset waiting for a device must not permanently
block an explicitly chosen PC/RGB/LCD profile on a confirmed Ubuntu Levita
system. Bypass only the four known presets in that exact no-ready-NZXT lane;
do not reinterpret them as Thermalright cooling requests or delete them in
the shipped policy. Explicit user cooling profiles and their existing
calibration/ownership requirements remain authoritative. Choosing the owner's
current profile for startup is a separately authorized private configuration
operation, not a universal profile migration shipped to other users.

TRCC's explicit occupied-USB-interface error is not missing authorization,
a stuck daemon or an FPS problem. On Ubuntu it stops OHC's own retry paths
without terminating another application or clearing the saved design.
The owner must release the other program and explicitly apply the design
again. Trailing setup hints must not conceal the primary conflict. Existing
Fedora recovery behavior is retained rather than changed by this Ubuntu fix.

## 06.10.26 – Privileged package calls use verified absolute paths

Never carry a relative local package path across a Polkit administrator
boundary. A simulated APT operation may succeed in the caller's directory
while the real privileged operation starts elsewhere. Verify the intended
package/hash, pass its absolute path, and check actual DPKG completion before
claiming installation. A failed path resolution does not justify changing
shared-directory permissions or weakening administrator authentication.
Use the normal local APT acquisition path: on the current Ubuntu host,
`--no-download` rejects the local archive internally even with an absolute
input, while the same command without that flag installs with zero network
download and no additional packages.

Package metadata must not inherit checkout write modes for trusted helpers
and their dedicated policies. The new RAM metadata policy is explicitly 0644
in the shared DEB/RPM stage. If the installed file is group/world-writable,
keep the runtime trust refusal; correct the exact package file mode instead
of relaxing that check or granting a broader action.

The standard-library RPM fallback must carry the same system helper/policy
paths as the normal RPM spec. A complete common stage is not enough if the
fallback's explicit payload manifest drops files. Verify actual DEB and RPM
headers/payloads, including root ownership and the new fixed helper's modes,
instead of treating build success or archive checksums as payload coverage.

## 06.10.26 – Detailed inventory and external GPU routing (.154)

OpenRGB 1.0 changed its CLI: `--list-devices` reports names only. The trusted
Ubuntu 1.0 lane must request `--list-detailed`; older/Fedora commands retain
their established form. A successful process exit is not evidence of complete
device metadata. A names-only response without device types must not replace
the inventory, controller identities, selection or saved physical routes.
Do not require non-empty mode/zone/LED lists: legitimate empty devices omit
those fields in the official CLI and must not be excluded by this guard.

A GPU lighting block may represent a physically confirmed mainboard ARGB
header without any native GPU controller. Its explicit block route owns the
header selection and GPU effect group, while existing Direct/conflict/ownership
guards and whole-device frame validation still govern every write. Missing
sources remain disconnected; never re-enable a disabled native GPU detector
or invent a connector to repair an external route.

Persistent fan authorization, display USB permissions and package installation
are separate privilege boundaries. A display daemon's generic `pkexec` prompt
must not be misdiagnosed as a lost fan grant, and must never justify a blanket
passwordless administrator rule.
Ubuntu OHC-owned TRCC processes instead use a fixed argument-free RAM-DMI
helper with a dedicated active-session Polkit action. It emits only allowed
non-identifying fields and cannot expose dmidecode's file-writing options.
Other automatic metadata probes remain unprivileged; stock TRCC files, its
independent GUI/daemon and Fedora's command path remain untouched.

## 06.10.26 – Preserve feature baselines and isolate Ubuntu backend evolution (.153)

The verified `.148` source archive is the comparison baseline for missing
features, not a reason to roll back later fixes. Restore contracts additively,
cover them with regressions, and keep feature enablement independent of sidebar
visibility. Device routing belongs to the selected PC profile; explicit empty
AIO roles must never be silently filled from another profile or a guess.

Ubuntu may use newer separately installed root-owned backend executables and
explicit SDK 6 negotiation. Fedora keeps its package commands and SDK default.
Never overwrite distro-owned Python libraries or install a foreign Debian
binary merely because its version is newer. Version checks are read-only and
off the GUI thread; actual updates require explicit approval and orderly OHC
shutdown. Service owners and hardware-write guards remain authoritative.

Ubuntu LACT reads use one cancellable bounded process with stale-result
rejection. Optional clocks data cannot make device stats unavailable. OpenLinkHub
HTTP 200 is transport success, not write confirmation: a mutation requires the
documented status=1 response. Nexus backgrounds/buttons reuse OpenLinkHub's
schema and USB ownership, never a guessed Corsair protocol.
Loopback requests must not escape through redirects or environment proxies.
Small GPU windows may scroll vertically when complete labels and curves cannot
fit; hiding or truncating safety/workflow controls is not an acceptable fallback.

## 01.10.26 – Snapshot scheduling may use guarded load detection (.127)

Snapshot Manager may pause new automatic Snapper work for explicit GameMode,
Gamescope, configured-process and KDE active-full-screen signals. It may also
use CPU and GPU load only as an optional conservative fallback: average CPU,
at least roughly one third of logical cores and GPU load must all cross bounded
thresholds for three samples, and three idle samples are required to resume.
This is not a generic game classifier and does not change the earlier Levita
performance decision: Levita still has no load heuristic or continuous Wayland
window inspection. Snapshot Manager uses a one-shot KDE query and a fixed
privileged helper with no arbitrary command, unit or path input. It pauses new
scheduled work and throttles Btrfs discard; it never claims to terminate kernel
cleanup already in progress.

## 22.09.26 – GPU profiles remain exact-device, locally verified data (.120)

A GPU subprofile may contain LACT's full configuration, including fan and
Zero-RPM state, plus stress-test presentation. It may be embedded in a main
profile, but its digest is not a trust signature. Only a profile previously
verified and stored locally for the exact LACT GPU ID may activate hardware or
run at startup. Imported or edited payloads become drafts. Application uses
the existing pending/confirm/revert, power, health and CoolerControl ownership
guards. Model names and illustrations are presentation data and never define
tuning limits. User artwork is normalized into a private copy; the source is
never changed or deleted.

## 20.09.26 – Remove the failing zone packet trial (.117)

The owner's `.116` test enabled both GPU and support zone trials. Both
timed out and the managed OpenRGB process crashed; OHC restart restored the
normal device path. Automatic preference fallback is not sufficient when
the writer process has already crashed. Remove these trial controls and the
per-frame zone write path altogether. Do not alter the confirmed physical
LED counts to conceal optical stepping. Investigate the pre-count animation
and OpenRGB's own visible output separately, without competing writers.

## 20.09.26 – Keep device packets as the default after the MSI regression (.116)

The owner's `.115` log shows timeouts and an OpenRGB engine exit shortly after
the MSI zone-packet path became active. Both GPU and support must default to
the previously working whole-device SDK frames. Ignore the old experiment
setting during upgrade. Keep independent, explicit tests only for the
identified MSI GPU and Airgoo support controllers. On an SDK error or
unexpected engine exit, disable the active tests, log the reason and retain
manual restart quarantine after a process crash. Do not claim optical
success from SDK completion.

## 20.09.26 – Compare MSI GPU SDK paths without changing ownership (.115)

About 25 successful SDK frames per second do not establish the optical frame
rate of MSI JARGB 1. For an explicitly routed MSI GPU controller, test
OpenRGB's documented per-zone packet instead of the whole-device packet on
subsequent frames, while retaining one serial SDK writer and the original
path as a saved switch. Send every configured zone so unrelated lights on
the same controller keep their active OHC effect. Fall back to a whole-device
packet if zone offsets cannot be validated. Log the chosen path, not a claim
of physical success. Case animation is read-only and may show a schematic
LED row when no physical path has been declared; never label its order as
measured wiring.

## 20.09.26 – Preview GPU edge changes on the active hardware path (.114)

Only while an OHC RGB effect is already active, slider changes may temporarily
replace the GPU/support motion settings read by the existing serial OpenRGB
worker. Do not persist these changes until Save. Cancel/close clears the draft
so the next frame uses the stored values. The GPU's separately bounded white
peak may reduce saturation without changing the support's brightness. A
reset control restores defaults in the draft. The Case editor should reach
the same GPU controls and show the component name. Display saved LED paths
only when an unambiguous physical header and path are declared; never infer
LED direction from the schematic alone. Physical optical behavior requires
user confirmation.

## 20.09.26 – Fix the shared GPU/support traversal independently of edges (.113)

Both LED rows must use the same open-strip head position. Changing approach
or fade on one row must not shift the other's phase or wrap point. Keep the
physical LED counts and the single OpenRGB writer. Default GPU edges may be
wider while the support keeps its previous shape; the owner must still judge
the optical result on the actual devices.

## 20.09.26 – Keep paired LED motion aligned to delivered frames (.112)

GPU/support motion parameters belong in a draft preview in the existing GPU
routing dialog and are saved only with that dialog. Lead/tail belong to each
strip separately; tempo and phase remain shared. Each row uses the declared
physical LED count. A slow OpenRGB batch must not cause the next virtual
motion frame to jump across several LEDs; slow the shared visual clock instead.
Display measured successful frame rates for both controllers, while stating
that software cannot read the visible LEDs back. Retain the single serial
OpenRGB writer, 25-Hz target and explicit physical controller ownership.

## 20.09.26 – Distinguish GPU fan trial, observed load and reset scope (.110)

The GPU fan test action must invoke LACT's rollback-protected preview;
navigation alone is not a test. Offer fixed speed as a validated LACT mode
alongside the existing curve, and never claim a physical RPM response solely
from a successful short API trial. A longer graphics test defaults to an
8K Phong-shaded scene and requires measured sustained load before a pass.
Discarding uncommitted UI inputs is read-only. Restoring OHC's prior values
requires its matching snapshot. Clearing the active LACT GPU profile needs
separate confirmation and a fresh equality check, and never silently
changes a profile edited outside OHC. Fan release reads LACT's current
configuration so it remains available after an external LACT GUI edit.
Only LACT owns GPU fan writes; the LACT journal and OHC sample history may
be exported locally by explicit user action.

## 19.09.26 – Separate GPU baseline load from tuning rollback (.109)

Permit a longer, cancellable graphics benchmark of the active LACT GPU
configuration even when OHC has not saved an overclock. Such a run performs
no GPU configuration write and therefore has no OHC snapshot to restore.
Only a matching OHC-saved tuning profile may be restored after an observed
fault. Explain in the UI that unsaved Tuning fields are excluded. This
supersedes the `.107` restriction that every longer test needs an OHC-saved
profile; it does not extend LACT's five-second unsaved-preview window.

## 19.09.26 – GPU benchmark setup belongs at the failed test (.108)

When a GPU preview cannot start because `vkmark` and `glmark2` are missing,
offer the confirmed benchmark installation directly in the Tuning page.
Keep this package dependency distinct from LACT; reinstalling LACT is not
a remedy. Ask the user to start the GPU preview again after installation,
so package setup can never apply a pending tuning configuration by itself.

## 19.09.26 – OHC-owned GPU fan curve and bounded long load test (.107)

OHC may create a five-point LACT fan curve from the GPU's reported fan and
temperature capabilities; no LACT GUI profile is required. CoolerControl's
GPU fan channel must be unmanaged before OHC asks LACT to enable it. New
settings remain in LACT's five-second automatic rollback window until the
explicit save. A longer test runs only on a profile already saved by OHC,
because LACT does not permit successive unconfirmed configuration changes.
The test is cancellable and observes load, temperature and throttle status;
on an observed fault OHC may restore only the matching OHC snapshot. The
optional vkmark package is installed only after user confirmation. These
checks do not establish hardware stability or compatibility without a live
test by the owner.

## 19.09.26 – LACT live baselines and exact TRCC ownership (.106)

RDNA4 GPUs may report valid overdrive limits while omitting unset clock
fields from the saved LACT configuration. Read `device_clocks_info` for the
current value and hardware bounds; require active Overdrive and retain the
100 MHz / 5% per-trial caps and separate explicit save. Do not infer a direct
core maximum when LACT reports none. At shutdown, distinguish the originally
owned TRCC PID from the current largest matching daemon. If the former has
already exited, record success without touching a replacement; if it is
still present, preserve the failure and leave the different process alone.

## 19.09.26 – Close always preserves the OHC session (.105)

The owner clarified that the top-right X and window-manager close should
always keep OHC running. Hide to the tray when available, otherwise minimize
to the taskbar. Neither action begins hardware cleanup. Remove the File and
header-menu Quit actions and Ctrl+Q shortcut; those menus may close the
window instead. The tray icon's right-click Beenden is the visible manual
exit path; desktop logout/shutdown retains its separate cleanup path. Journal
automatic tray continuation separately from the old explicit preference so
it does not silently change ordinary-minimize settings. This supersedes the
older `.98` close-setting decision for the X behavior.

## 19.09.26 – KWin is the Wayland output authority; LACT owns Overdrive setup (.105)

On KDE Wayland, Qt's `QWindow.screen()` and global geometry can repeat the
requested output even when KWin shows the mapped window on another monitor.
Use one short-lived KWin script restricted to the current OHC PID and main
window title, and trust KWin's actual output in the log. Move only that window
to the user's selected connector or current primary output. Unload the script
and leave no permanent KWin rule. The first runtime check still requires an
installed-version visual confirmation.

LACT, not OHC, prepares the AMD Overdrive boot setting and any initramfs
update through its documented local command. OHC asks for explicit
confirmation, runs the request outside the GUI process with a bounded wait,
reports failure, and asks the user to restart separately. Opening the page,
refreshing it and cancelling the prompt do not write boot state. Tuning
remains gated by LACT's reported active Overdrive state and baseline profile.

## 19.09.26 – Fresh LACT GPU profile and Overdrive gate (.104)

LACT 0.10.1 returns `null` for `get_gpu_config` until a GPU override exists.
Treat this as an empty profile, keep measurements visible and prefer the
dedicated GPU. Use LACT `system_info.amdgpu_overdrive_enabled` as an explicit
write gate; unknown or disabled status and an empty baseline never enable
OHC tuning. The user can open LACT's GUI to enable Overdrive and create
baseline values, then restart if LACT requires it and refresh OHC. OHC does
not silently alter AMD kernel parameters, initramfs, service ownership or GPU
clocks. An inactive CoolerControl service is a free GPU fan channel, not a
LACT connection failure.

## 19.09.26 – LACT package metadata and bounded Wayland confirmation (.103)

LACT 0.10.1 deliberately exposes no `lact --version` flag. Use installed
distribution package metadata for the write gate and installer instead; a
successful package installation with a failed follow-up may finish by enabling
the service without adding the COPR again. The owner explicitly confirmed the
original installation. The current primary output and saved connector both
point to DP-1. Qt can retain a requested global Wayland position after KWin
maps the surface elsewhere, so trust the mapped QWindow screen before global
geometry and make one later bounded recheck. Preserve an explicitly selected
connector; do not silently reset user preferences. Live window placement needs
confirmation after the new build is installed.

## 19.09.26 – Stop only an OHC-started TRCC daemon on ordered exit (.101)

The live installed `.98` process returned from Qt and exited cleanly, but its
TRCC daemon remained at about 1.3 GiB after `device disconnect`. Ordered OHC
exit must release the Levita to firmware and then ask a daemon it started to
exit through the documented TRCC `kill` IPC action. Capture the daemon PID
after an OHC client creates it. Preserve a daemon already present before OHC,
and refuse to kill a replacement PID. A release request without a daemon must
not auto-spawn one through `TRCC_DAEMON=1`. Keep the independent crash fallback
and do not treat a process exit as proof of physical display restoration.

## 19.09.26 – GPU link load fallback and shared temperature presentation

When glmark2 is absent, use the distribution-provided Vulkan vkcube as the
explicit bounded graphics-load helper. Do not call an early-exited child an
under-load PCIe measurement. A direct GPU-test click first runs the necessary
read-only inventory without opening the unrelated privileged RAM-DMI request.
Display the missing helper clearly. Keep the
existing no-tuning/no-fan-write boundary. A shared compact 0–100 °C scale is
visual context, not a safety threshold; all temperature values come from actual
read-only sensor readings. For the owner's 30-LED Sapphire external ARGB strip,
retain the confirmed count and physical route but use a shorter white head and
visible blue body than the earlier broad envelope. The supplied video is
optical reference only, not hardware feedback or proof of a transmitted frame.


## 15.09.26 – Read-only hardware checker (.96)

The owner requests a one-click CPU/SMT/virtualization, GPU PCIe, SSD and RAM correctness check.
Keep the first stage read-only and outside the GUI process. A green result needs
an explicit observable target: kernel current/max link data or a manual RAM
target. Unknown capability stays unavailable, never guessed from a product name.
GPU PCIe power-saving downshifts are warnings until a user-started bounded load
test; evaluate only the default/boot GPU definitively in multi-GPU systems.
NVMe lane shortfalls may be reported from negotiated/max link width without a
storage write benchmark. RAM manufacturer, part and configured speed may use one
fixed Polkit-owned `dmidecode --type 17` request; OHC never handles a password or
retains serial numbers. Manual RAM model/MT/s covers incomplete firmware.
The optional glmark2 test is time-bounded and does not authorize clock, voltage,
fan, firmware or BIOS changes. AMD SVM or Intel VMX is reported only as exposed
by the running kernel; OHC does not change firmware virtualization settings.

## 14.09.26 – Exposed selected-video previews and confirmed composition (.95)

The owner wants identical visible animation behavior in layout and effects
previews. Use one bounded local decoder per exposed preview, with no hover
requirement, and clip through every ancestor/scroll viewport. Hardware ticker
and control timers remain independent from page visibility.
Keep a separate pending and successfully confirmed composition copy. Effect
exploration cannot persist start/profile intent or masquerade as applied media;
clearing/leaving falls back to confirmed media/layers. A matching active catalog
effect is mirrored. Without a choice, disable apply/staging instead of applying
an unrelated default smoke. After firmware hand-off, do not show stale OHC media.
Render original Light Bands at actual 4800×2160 and output native 1600×720;
remove permanent pen/idle centre highlights, keep warm bodies and smooth glow.
The first-open jolt is not proven by the log; eliminate observed empty-motion
scene rebuilding and incremental gallery geometry churn, then test actual UI.


## 14.09.26 – Responsive case forms and paired colour fields (.94)

Owner rejects scrolling inside case property menus. Reserve more width to the
left and reparent the same live widgets into columns on wide windows or tabs
on smaller windows. Do not clone fields or trigger domain commits on resize;
keep validation and Save/Cancel outside the subdivisions. The whole case page
keeps its normal scrolling, with the active inspector brought into view.
Broaden GPU/support spinner/comet fades with a quintic curve, without raising
the 25-Hz target or fixed 3×4 sample budget. Paired strips share virtual time
and sampling footprint, then sample their actual independent LED counts.
No hardware resizes, new transport or changed PWM ownership. A spoken 24-LED
support count differs from the logged/saved B6 12; keep existing counts until
clarified, and cover both sizes in hardware-free regression tests.


## 14.09.26 – One Levita default and immutable recovery (.93)

Owner supersedes the older automatic-profile-over-standalone priority after
Cyber video reverted to landscape. Retain existing startup keys without a
lossy migration: any saved standard wins over automatic profile restoration,
including disabled or missing media; show the existing error instead of silently
falling back. An explicit profile load may replace the same shared standard.
Only explicit save/apply stages profile media; previews never persist the
startup default. Cancel superseded startup retries by generation.
Recovery replays accepted prepared commands, never a later preview selection.
The .92 log shows a stable-video-size 1138-MiB RSS restart. Replace the 1-GiB
absolute trigger with stable-video tolerance, sustained growth and real system
pressure, retaining a 3-GiB emergency bound and existing five-minute cooldown.
This does not promise a flash-free emergency USB reconnection or hardware soak.

## 14.09.26 – Continuous static LCD and progress-based worker recovery (.92)

Use TRCC's existing daemon IPC ticker for static and animated designs, because
the official CLI documents its static-display timeout prevention. Inspect the
installed 9.9.12 source for the positive sent-bytes acknowledgement contract;
never count startup banners, arbitrary output or a live PID as send progress.
Keep native backend quarantine, calibrated PWM and sole-writer ownership.
Bound automatic restarts and record actual evidence/retry policy privately.
Manual sensor recovery is read-only and cannot restart an exiting application.
Game detection must not scan /proc or block on GameMode in the GUI thread.
Full autonomous cooling/core migration still needs hardware validation.


## 14.09.26 – Staged process boundaries and diagnosable exit (.91)

Owner approves the staged architecture recommendation: first durable exit
diagnostics and side-label activation, shared read-only sensor snapshots and
actual process health, then targeted pure RGB/LCD work separation, autonomous
core/cooling last after hardware validation. Do not represent the first read-only
runtime as an autonomous fan daemon. Existing TRCC/OpenRGB/OpenLinkHub owners,
native-crash quarantine and calibrated watchdog protection stay authoritative.
Own sensor restarts are bounded; stale snapshots are unavailable, never renewed
just by a live process. Resource caps need measurements, not guessed defaults.
Explicit Beenden stops OHC-owned runtime and workers after restoration; closing
to tray remains a separate configured operation. Persistent private phases,
one delayed stack dump and a bounded non-signalling exact-parent observer expose
hangs without os._exit, kill-by-name or privilege escalation. Never auto-upload
diagnostics. Shared temperature exports remain lazy so pure workers import no Qt.

This file records decisions that future agents must preserve unless the project owner explicitly changes them. New durable decisions should be appended with a date/version and rationale.

## 13.09.26 – Complete private settings packages and physical LED direction

3.4.29.90: case component, ARGB/count/path/pixel-test, GPU route and PWM properties
belong in one dismissible inline right-side inspector, never separate native
property windows. Save alone commits; stale async reports cannot reopen it.
Retain existing physical-test restoration and sole-writer/ownership safeguards.
Navigation transitions may animate only the left menu. Follow KDE's inline-drawer
pattern (https://develop.kde.org/docs/getting-started/kirigami/components-controls/)
without importing a new framework or copying artwork. LCD prewarm is bounded,
input-idle read-only card/cache preparation, never hidden animation/USB work.
Precautionary RAM retries must isolate selected RAM and keep unrelated effect
clocks. Stored cooling startup intent is not acquired PWM ownership; the UI
shows actual state, and fresh owner results/calibration remain required. Explicit
tray quit is idempotent with queued Qt exit after best-effort phase cleanup;
never use os._exit or kill-by-name to conceal shutdown errors.

3.4.29.89: GPU light heads may use a dedicated bounded open-strip sampler,
never modular end-to-start physical neighbors. GPU/support synchronization
shares effect/time and normalized progress only across existing explicit,
selected conflict-free routes. Keep per-header counts, PWM, transport ownership
and physical test numbering unchanged. Missing/ambiguous/ring partners fail
closed; the optional checkbox is independent physical setup, not effect profile
state, and complete ZIP packages preserve it. Software rate diagnostics never
claim measured optical FPS or firmware repair.

3.4.29.88: declared fan-chain reversal is independent of rotation within each
ring. Default legacy ordering stays unchanged; preview, sampling, logs and full
packages share the bounded optional boolean. Import asset types must match the
export allowlist; reject file/directory conflicts before staging. Quiesce local
timers/restart intentions before cancelling the owned package worker so a
cancellation exception cannot skip later hardware-release phases.

Keep existing profile JSON exchange; add a complete app ZIP with supported
typed settings, user/current profiles, geometry, RGB/PWM, fan library and
associated media/themes/fonts/LCD store. No other apps' settings or recursive
home/system backup. File work belongs in an owned bounded worker, not UI or
hardware queues. Import validates types, canonical paths, sizes and SHA256;
stage privately, relocate references, apply only on confirmed next startup,
keep rollback. Imported automation, CPU regulation and PWM calibration are
not portable hardware authority and require local reactivation. Private
packages contain personal paths/media and are not distributable app releases.

Store declared LED strip/ring coordinates independently from effect designs.
LED 1/end, ring count/start/clockwise order are physical user declarations;
pixel tests retain actual 1-based numbering. Eight directions use existing
unambiguous case blocks and count-aware interpolation without changing the
sole-writer transport. Unconfigured or invalid paths retain local rendering;
do not infer cabling, auto-resize or claim optical FPS/native crash resolution.

## 13.09.26 – Revised personal Airgoo wiring and reusable custom fan library

The owner supersedes the older 24-LED support reference: B6 is 12 addressable
LEDs. Front normal fans use A1 (2×8, SYS_FAN4), bottom reverse intake B7
(3×8, SYS_FAN6), rear normal exhaust B8 (1×8, SYS_FAN1), and Thermalright
radiator A8 (3×10). These are personal observations, not manufacturer-wide
defaults or inferred pwmN identities. Correct only this personal Thermalright
layout once against uniquely reported AG-DRGB16 ports, preserving presentation
and PWM control state. Pin complete saved counts; never invent missing server
zone lengths or continually reset subsequent manual choices. Reusable custom
fan manufacturer/model/color/count records are bounded metadata selected by
explicit user action; saving them cannot itself resize hardware or write PWM.

## 13.09.26 – Exclusive LED preview and explicit controller recovery (3.4.29.86)

The owner confirms restoring the selected design after LED test/save and
deprioritizes duplicate-display redesign. Pause inventory/auto-apply while the
LED editor owns a preview, preventing old saved zone lengths from being
reapplied during tests. Never overlap tests, retry failed writes indefinitely,
enable disabled writes or restore stale design/selection after changed intent.
Preserve actual ownership/quarantine while allowing offline settings-only
wiring. Explicit manual recovery invalidates stale discovery state and can
restart only the concrete OHC-owned engine; native crash loops stay quarantined.
Personal fan declarations are bounded settings separate from effects/PWM;
black/white are model metadata, not LED colors or PWM routing. The observed
eight-LED ASIN reference is personal, not manufacturer-wide verified support.

## 13.09.26 – EOF-first helper shutdown (3.4.29.86)

The existing root-owned fan-helper session exits on stdin EOF. Close that pipe
and wait before attempting bounded user-level signals; permission denial must
not abort unrelated cleanup or require broader Polkit privileges. Isolate the
existing shutdown phases and cancel owned timers/backend callbacks before
explicit Qt exit. Preserve close-to-tray and hardware ownership/restore paths.
Never clear the clean LCD marker before the restoration sequence succeeds.
Pending helper exit and SDK completion are diagnostics, not physical readback.
No RGB crash-restart policy is changed without a clear owner-selected trigger;
unbounded crash loops and guessed lighting outputs remain prohibited.

## 13.09.26 – Direct per-block ARGB assignment (3.4.29.85)

The owner requests controller/header choice, count editing and pixel testing
directly from case blocks without requiring device-tile drag/drop. Persist
explicit stable controller/reported-zone bindings as physical setup, separate
from design/position snapshots and PWM. A missing saved controller/zone never
falls back to another header. An explicit empty binding suppresses legacy
device/note hints; cancellation changes nothing. Binding alone writes settings,
never hardware or PWM. Count/test actions reuse the existing bounded SDK editor
and sole-writer queue. GPU blocks retain existing GPU-route authority, not a
second independent route. Reuse complete stable four-language captions.

## 13.09.26 – Visual scale and physical connector names (3.4.29.84)

Component scale is a bounded 25–200% presentation property, never a change to
LED counts, fan millimeters, PWM identity or regulation. RGB/cooling share it
unless independent presentation is selected; positions and scale are the only
independent fields. Corner drag previews locally, commits once on release and
cancels on Escape/hide. Old profiles default to 100%; startup never rearranges
saved coordinates. Explicit arrangement and render geometry remain schematics,
not exact CAD. Display reported System Fan labels as SYS_FAN identifiers, never
guess an index offset; preserve the original pwmN stable ID in technical details.
Unassigned RGB blocks still open their component editor, because PWM and lighting
are independent physical paths.

## 13.09.26 – Default all-writable RGB selection (3.4.29.84)

The owner requests all devices selected by default. Default mode follows the
currently writable inventory, excluding locked/read-only devices, without
starting hardware output. A visible individual-mode checkbox and checkable
inventory rows support subsets. Explicit group/slot subsets, deselection, clear
and reset opt into individual mode so they are not silently refilled. Persist
the mode in settings and new full profiles; old profiles preserve the current
mode. Single-device identification tests remain single-device.

## 13.09.26 – Standing approval for two-version release-backup rotation (3.4.29.83)

The owner explicitly authorized automatic pruning of older recognized packaged release backups during requested local version builds without asking each time. Create the complete new release set first, retain the two newest complete semantic versions in the fixed external sibling backup directory and verify their SHA256 files. This narrowly scoped permission includes the .81 to .82/.83 rotation; it never authorizes unrelated deletions, fewer than two retained complete existing sets, installation or publishing. Unsafe/incomplete targets remain a stop condition. The established backup tool already rotates by default with a minimum retention of two; only the persistent authorization rule changes.

## 13.09.26 – Shared physical topology, optional independent positions (3.4.29.83)

The central Case page follows Overview and owns the existing RGB component layout plus reported chassis-PWM assignments. RGB and cooling share physical device IDs, connection notes, declared LED counts and PWM mappings. Opting out of synchronization stores only bounded independent cooling positions, never a conflicting second wiring topology. Assignment delegates the existing chassis-only controller and does not calibrate, enable or write PWM; calibration/ownership gates remain unchanged. Existing navigation indices stay stable; Case is appended internally and inserted first in sidebar order without disturbing custom relative ordering.

## 13.09.26 – Declared ARGB counts and count-aware rendering (3.4.29.83)

The owner visually verified 30 LEDs on their Sapphire NITRO+ connected to MSI JARGB 1. This is a personal reference observation, not a new manufacturer/default count. Every reported Direct ARGB zone uses the bounded single-header editor and pixel test. Explicit manual counts are pinned separately from design snapshots; untouched zones retain profile semantics. Diagnostic logs distinguish declared sizes, server buffers, frame offsets and SDK completion from unavailable physical readback. All configured zones render independently; bounded pixel-area sampling and soft motion/colour transitions reduce short-strip aliasing without changing the 25-Hz transport target or guaranteeing optical FPS. Intentional lightning flashes remain. Lazy RGB module exports keep pure effect helpers Qt-free and avoid circular imports. Case drawings are original code-native illustrations; no manufacturer images are shipped and decorative fan/LED marks are not physical topology measurements.

## 13.09.26 – GPU hardware routing is separate from design snapshots (3.4.29.82)

External GPU ARGB wiring is a stable controller ID plus an explicitly chosen reported zone name. Render a routed GPU strip independently from the controller's total LED count; other zones retain their own lengths and controller effect. Current saved physical routes and GPU-header counts take precedence over RGB design snapshots, including old startup profiles. Native selection is an explicit persisted override. The single-header editor changes one device's count within SDK-reported limits and never rewrites other headers; its explicit pixel test temporarily blacks other controller zones and requires reapplying the design. One-time JARGB 1 routing is restricted to the owner's personal layout and uniquely matched Sapphire 9070/MSI devices, based on the owner's confirmed wiring, not inference from a board model. The owner's 80/90 values are test declarations, not manufacturer pixel counts. No new raw hardware protocol or writer is introduced.

## 13.09.26 – GPU native effects are the automatic default (3.4.29.81)

One reported logical Sapphire GPU LED is not an addressable strip-length measurement. Choose only reported native animation modes for OHC designs; never automatically enable External Control merely because the firmware reports it. External ARGB sync requires an explicit stable-ID mapping to the physically connected, selected Direct controller. Manual LED counts use that controller's existing bounded zone editor, not invented GPU segments. Missing/unselected sources fall back to native effects. Preserve existing personal layouts and LED topology; profiles without the new mapping remain native by default. Controller-wide effects and optical validation limits must be explained honestly.

## 11.09.26 – Fan-card toggle buttons name the next action

Each calibrated motherboard/case-fan card must label its toggle with the action a click performs: enable while inactive and disable while active. A state-only caption such as “Automatik aus” is not sufficient because it can be mistaken for an off command. Curves, calibration gates, ownership protection, watchdog and firmware return remain independent of this presentation rule.

## 11.09.26 – Bundled Layer-2 values retain readable backing surfaces

Bright bundled backgrounds such as Nebula Drift must place live values on a restrained dark backing surface instead of relying on text colour alone. Project-owned layout families should remain visibly distinct through their geometry while preserving editable metric positions and the right notch-safe area. These decorative changes never alter sensor sources or create another display hardware writer.

## 11.09.26 – Levita display effects are restored through the selected startup profile

Selecting a library Display Effect stages its validated Layer-1 medium together with the current Layer 2 for the next LCD/full profile update; a generated effect is staged once its video exists. Staging is also available as an explicit action and never writes hardware. Only updating a user profile persists the association; when that profile is selected for startup, its Levita payload becomes authoritative before the existing delayed Levita start. Media validation, reconnect/cooldown rules and the sole TRCC hardware writer remain unchanged.

## 10.09.26 – Application themes are registered data modules; effect videos run only while visible

Light and dark application styles live separately under `src/modules/ui_themes/v1_0/`; `registry.py` is the single extension point for future designs and the shared controller no longer owns palette definitions. Bundled display-effect video is decoded only from the validated local catalog and only while the effect page is visible. Pause, page changes, a hidden/minimized window and controlled shutdown stop the decoder. This preview path owns neither TRCC nor USB and does not change the existing hardware hand-off.

## Product and repository

- **2026-08 / current:** Product name is Open Hardware Control by Frelidon. The historical filename `src/kraken_control.py` remains because it contains the integrated mature NZXT module; renaming the file is not required for branding.
- **2026-08 / current:** Open Radeon Control Center stays a separate project.
- **19.09.26 / Entwicklung 3.4.29.102:** OHC ergänzt eine eigene GPU-Seite über die dokumentierte lokale LACT-API, ohne ORCC-Code zu übernehmen. Jede Änderung wird begrenzt unter Last geprüft, durch LACT automatisch zurückgestellt und nur nach gesondertem Klick dauerhaft bestätigt. OHC speichert vor dem ersten eigenen Commit die Vorwerte pro GPU für die spätere ausdrückliche Rückgabe. Vor GPU-Schreibzugriff muss ein aktiver CoolerControl-GPU-Lüfterkanal auf „Unmanaged“ gestellt werden; Gehäuselüfter dürfen dort bleiben. GPU-Licht bleibt beim getrennten OpenRGB-SDK-Besitzer. MSI-/ASUS-RGB-Unterstützung folgt ausschließlich tatsächlich gemeldeten OpenRGB-GPU-Controllern und ihren Modi, nie bloßen Herstellernamen.
- **2026-08 / current:** The project remains manufacturer-neutral and unofficial. Compatibility names do not imply partnership, approval or support from manufacturers or related open-source projects.

## Navigation and UI

- **10.09.26 / 3.4.29.60:** Maximized compositor work-area bounds are never persisted as OHC's normal floating geometry. Normal geometry is stored separately, clamped on all edges to the chosen screen and replaced with a bounded preferred size when it resembles maximized bounds. `Ctrl+Alt+0` remains an accessible recovery path. The PC view links only manufacturer sources; the owner's personal Amazon purchase link is not application UI. Case visuals remain original OHC schematics, with no copied manufacturer artwork.
- **10.09.26 / 3.4.29.59:** The OHC main window uses client-side chrome. Movement and resize must remain compositor-delegated through Qt system operations for Wayland/X11; maximize/restore, accessible action names, the pre-construction tray-autostart surface suppression and existing tray-aware close path are mandatory. Ordinary dialogs retain native platform decoration.
- **10.09.26 / 3.4.29.59:** LCD owns Display & Layout and Display Effects as collapsing child navigation. RGB Studio initially shows four suggestions and keeps device/group/details compact; favorites and full categorized access must not change existing saved design indices.
- **10.09.26 / 3.4.29.59:** The exact personal case is Thermaltake Retro 360 TG (official ATX/Micro-ATX/Mini-ITX specification; Amazon ASIN B0CPDHXVF4). Other case choices are original editable OHC schematics, never bundled manufacturer artwork or claims of millimetre-accurate geometry.
- **09.09.26 / 3.4.29.58:** Generated Display Effects and packaged offline library media use separate explicit trusted roots feeding one shared strict MP4/symlink/path validator. Bundled media must enter Levita Studio through its dedicated method; both paths still delegate to the same Layer-2/apply queue and sole TRCC hardware owner. Pre-apply rejection must be visible in the shared log.
- **09.09.26 / 3.4.29.57:** An unexpectedly ended long-running Levita `display play` ticker may restart automatically only through the existing TRCC daemon IPC. Recovery is bounded to 1/2/4-second backoff, renews after a stable run and never performs USB reconnect or creates another hardware owner. Backend output included in shared logs must remain shortened and privacy-filtered.
- **09.09.26 / 3.4.29.56:** Bundled third-party Display Effects must be edited for the physical 1600x720 target, remain fully offline at runtime, and expose creator, original source and license directly beside the main/colour selection. The same records belong in `THIRD_PARTY_NOTICES.md`; selecting or previewing media never creates another TRCC/USB writer.
- **09.09.26 / 3.4.29.55:** Startup may schedule device discovery and local Levita library construction only after the first Qt event turn. Read-only CoolerControl detection runs outside the GUI process and is coalesced; an unknown or failed result is treated as occupied, never as permission to write Mainboard PWM.
- **09.09.26 / 3.4.29.55:** Display Effects mirrors the LCD Studio's graphical Layer-2 selection and keeps effect type inside the settings panel. Faster local encoding and cache reuse may shorten preparation, but the ten-second Levita hardware cooldown, reconnect barrier and sole TRCC owner must not be bypassed for perceived speed.
- **09.09.26 / 3.4.29.54:** Display Effects is a first-class page immediately beside LCD. Procedural renderers may produce only bounded media in OHC's private cache; applying that media must pass through the existing Levita studio so layer 2, masks, test mode, queueing, reconnect rules and the sole TRCC hardware owner remain authoritative.
- **09.09.26 / 3.4.29.54:** A second OHC launch sends only a fixed `show` message over a private local socket, then exits without acquiring hardware ownership. The existing process lock remains authoritative. Desktop activation tokens and startup feedback are suppressed only for `--autostart`; a deliberate normal launch keeps standard feedback.
- **09.09.26 / 3.4.29.54:** Every visible UI addition or changed caption must update the complete DE/EN/ES/FR files in `src/modules/localization/v1_0/` in the same change. Technical identifiers and values may remain literal; navigation, page headers, dynamic cards and actions may not silently fall back to German.
- **3.4.29.40:** Wallpaper Engine for KDE is a first-class, reorderable OHC navigation page. OHC implements a native local gallery and opens Plasma's original wallpaper KCM for advanced options; it does not embed, copy or patch CaptSilver's external QML surface. Workshop, personal videos and per-screen targets remain visibly separate.
- **3.4.29.40:** CaptSilver v1.4 stock values are the default. The optional OHC performance profile is explicitly reversible and may change only `AnimatedPreview`, `Fps`, `PauseMode`, `ResumeTime` and `PresentMode`. It must not install the discarded plugin patches, cache builders or watchers, and neither profile may alter active wallpaper, Steam subscriptions, playlists or XWaylandVideoBridge state.
- **3.4.29.41:** Wallpaper onboarding is shown only on the first deliberate visit and remains manually reopenable. Automatic plugin installation is Fedora-only in this version: OHC downloads as the unprivileged user exclusively from CaptSilver's official stable GitHub release, requires an exact Fedora-major/architecture RPM plus the API-published SHA256 digest, then asks a second time before handing one fixed local package path to `pkexec dnf install`. Polkit owns the visible password prompt; OHC never receives or stores credentials. Other distributions receive upstream instructions instead of guessed privileged commands.
- **3.4.29.41:** The default navigation places Wallpaper Engine immediately after LCD, followed by optional OpenLinkHub, Profile, Settings, About and Log. Only saved orders exactly matching an earlier OHC default are migrated; user-customized orders are preserved.
- **3.4.29.42:** CaptSilver pause, resume, next and mute calls use the `/WallpaperEngine` object registered on `org.kde.plasmashell` and include the full `com.github.captsilver.WallpaperEngine` interface method. The optional standalone service alias is not a reliable dependency. CaptSilver v1.4's advertised Previous method is not a true back operation, so OHC resolves the preceding bounded local Workshop entry and applies it through the existing Plasma script path. Scaling writes only CaptSilver's documented integer `DisplayMode` values 0, 1 or 2 to the explicitly selected Plasma screen target.
- **3.4.29.42:** Main-window screen preference stores `primary` or an exact bounded `QScreen.name()`, never a transient list index. Primary is the default and the fallback for an unavailable saved screen. OHC requests that screen before showing and bounds restored normal size, but must state that a Wayland compositor such as KWin retains final placement authority. Tray-autostart surface suppression remains authoritative.
- **3.4.29.42:** All standard Qt scroll areas, lists, trees, text views and tables inherit one global eight-pixel scrollbar style in both axes and all OHC themes; individual feature pages must not reintroduce competing wide scrollbar styling.
- **Post-3.4.29.41:** Keep KWin's native server-side title bar for 3.4.29.41. A theme-matched client-side title bar is a separate change because `FramelessWindowHint` also transfers move, resize, maximize, keyboard and accessibility responsibilities to OHC, with dedicated KDE Wayland/X11 and tray-autostart regression coverage required before activation.
- **3.4.29.39:** Temporary window diagnostics ignore only routine Qt `ToolTip` surfaces and `QFrame` popups whose direct parent is a `QComboBox`. Other popup types remain observable, and the exact parentless, untitled 640×480 startup-frame quarantine remains unchanged.
- **3.4.29.35:** TRCC's cached `Device.is_connected` cannot prove that the underlying Levita USB transport remains open after an unplug. Before each explicit design, colour-test or display-settings write, OHC must serialize a tolerated daemon detach and a mandatory fresh connect/handshake; only then may later commands report success. The existing ten-second design-change cooldown and bounded retry still apply.
- **3.4.29.34:** Symlink rejection is an external Levita import-boundary rule. OHC's private content-addressed editable-theme cache may link previously validated artwork while retaining a real, bounded `trcc.json`; controlled application shutdown sends exactly one bounded daemon-only `stop-video` request after stopping local clients so the active TRCC theme returns.
- **3.4.29.33:** The selected RGB preset and its per-preset colour overrides are persistent UI state. A colour edit must not silently turn a built-in preset into an unmarked custom entry. Levita layer 1 and 2 remain two equal side-by-side libraries; folder imports, layer assignment and favourites store references only and never move or rewrite original media.
- **3.4.29.30:** The Levita inner media radius belongs at the boundary between image/video content and the black right camera/notch bar. It is independent of the physical outer panel contour. Preview and generated hardware mask must share the pure `panel_geometry.py` implementation; top and bottom default to linked 48 px but may be adjusted independently from 0 to 240 px.
- **3.4.29.32:** Light theme navigation must keep dark text on a light rail. Selected items must not use white `HighlightedText` against a pale accent wash. The LCD “Design anpassen” editor belongs beside the live preview, not in a squeezed strip under it. Layer-1/2 galleries fill the available width with up to eight cards.
- **3.4.29.31:** The LCD “Design anpassen” controls must remain readable: number fields and combo boxes keep a usable minimum size, and long checkboxes such as the black-bar option occupy their own full-width row instead of sharing a squeezed grid cell with a value editor.
- **3.4.25:** Main navigation can be reordered by drag & drop and applicable categories can be shown/hidden.
- **3.4.25:** **Overview, Navigation customization and Help are permanent safety anchors. They can never be removed or hidden.** Reset-to-default navigation must remain available.
- **3.4.25:** Modern compact PySide6 visual language should stay consistent across Overview, Cooling, RGB Studio, LCD, Profiles, Log, OpenLinkHub, Settings, About, Help and Desktop Designs.
- **3.4.25:** Chassis fan curves use the embedded interactive editor and stored table values remain synchronized with draggable points.
- **3.4.27:** Kraken quick-profile buttons represent confirmed device state, not click intent. A profile becomes active only after both pump and radiator-fan writes succeed; manual values, curves and general profiles clear the quick-profile highlight.
- **3.4.27:** Internal mainboard-channel selection and visible chassis-fan-card expansion are separate states. Detection may select a channel for compatibility, but it must not open a card; only an explicit user action expands at most one card.

## Hardware ownership and safety

- **09.09.26 / 3.4.29.54:** OpenLinkHub updates are never automatic. After explicit confirmation, package-managed installs use only fixed DNF/APT argument lists and existing repositories. A user-space install is eligible only when its exact service working directory and executable resolve safely inside the user's home; only the fixed official GitHub release asset with its published SHA-256 is accepted. Extraction rejects links/devices/traversal, the previous installation remains recoverable, and startup failure rolls back. The bundled Web UI is updated with the same package. OHC must never pipe a remote installer into a shell or silently replace root-owned rules.
- **3.4.29.43:** A saved RGB startup profile must not be discarded while the managed OpenRGB engine's first known-incomplete inventory is deliberately withheld. OHC retains its already-acquired session lock, waits through the existing bounded discovery policy and either starts against a usable inventory or releases ownership after the bounded retry path ends.
- NZXT Kraken control remains a first-class built-in module.
- Wallpaper Engine integration is desktop configuration, not a hardware writer. Steam Workshop files and the installed CaptSilver package remain immutable; a Steam library may never be accepted as the recursive personal-video folder.
- Corsair control is mediated through OpenLinkHub's local API; do not add speculative direct Corsair USB writes.
- OpenRGB remains a separately installed backend managed through OHC's private loopback engine; do not bundle/copy its hardware driver source into OHC.
- **3.4.29.33:** OpenRGB cannot confirm whether an ENE DRAM LED is physically lit. Cold-start recovery therefore uses one immediate reclaim plus exactly three delayed precautionary retries (45 s, 2 min, 4 min), then stops. Disabling writes, reset, conflicts, backend exit and application shutdown cancel the sequence.
- A foreign OpenRGB process/server blocks OHC writes rather than being killed automatically.
- OpenLinkHub and OpenRGB integrations remain loopback-only unless security architecture is explicitly redesigned.
- Mainboard PWM control requires physical channel confirmation/calibration before automatic control. Never infer electrical fan mapping from board model alone.
- CPU_FAN/PUMP_FAN ownership must not conflict with Kraken cooling ownership.
- **3.4.27:** CoolerControl service autostart may be changed from OHC only through an explicit confirmation and Polkit authorization. Disabling the service must not start OHC fan control automatically; enabling it must first stop OHC mainboard control and restore firmware/BIOS ownership.
- Firmware update/flashing features require a separate explicit design/review; no agent may infer or invent firmware-write protocols.
- **3.4.29:** Thermalright Levita display USB and pump/radiator motherboard PWM are separate ownership paths. USB presence may select the display/editor but never authorizes a PWM write. Both cooling headers require individual physical confirmation, CoolerControl remains mutually exclusive, and OHC must restore owned headers to firmware control on exit.
- **3.4.29:** The current Levita path exposes no coolant sensor. OHC may show CPU/GPU measurements and use CPU-based software curves, but must never label a derived value as coolant temperature.
- **3.4.29:** The reference ENE-DRAM controller requires two ordered Direct reclaim passes at saved-profile cold start. A successful OpenRGB command remains protocol evidence only, not proof that LEDs changed visibly.
- **3.4.29.2:** In Frelidon's confirmed personal Airgoo wiring, Channel B6 is the separate Jungle Leopard GPU support with 24 LEDs. It must remain a component zone independent from both ENE-DRAM controllers; this reference default must not be generalized to unrelated layouts or hubs.
- **3.4.29.3:** Mainboard PWM curve writes may reuse one explicitly authorized, fixed-path Polkit helper child for the OHC process lifetime. The helper protocol must remain pipe-bound, length-limited and restricted to validated NCT6687 probe/percent/restore/watchdog operations; OHC restores firmware ownership before ending the session on orderly exit.
- **3.4.29.5:** OHC must neutralise persisted external TRCC split state before loading any Levita media. Decorative split styles remain preview-only while the installed/backend Qt renderer is known to crash; the physical 80-pixel cutout remains an independent OHC overlay-safety boundary.
- **3.4.29.6:** The visible Levita camera/notch exclusion is an explicit user-adjustable OHC mask, not inferred from a speculative USB write. OHC may prepare shifted local cache copies of supported media but must never rewrite imported designs; movable metrics must be clamped against the selected mask boundary.
- **3.4.29.7:** A user may explicitly install a persistent Polkit authorization for the fan helper and remove it again from OHC. The rule is restricted to the exact invoking local account and the existing fixed helper action; no password is stored, no arbitrary path/command is accepted, and calibration, ownership, watchdog and firmware-return safeguards remain mandatory.
- **3.4.29.7:** Every invocation of the Qt-based OpenRGB executable, including short-lived CLI clients, must use an offscreen Qt platform. The private loopback and external-process ownership boundaries remain unchanged.
- **3.4.29.7:** A minimized tray autostart must suppress the OHC native window surface before constructing the UI and retain that suppression through background profile restoration. Only an explicit user open action releases the surface; a desktop without a tray may instead release it and show the normal minimized fallback.
- **3.4.29.8:** Electrical DC/PWM mode may be changed only when the kernel exposes the exact channel's fixed `pwmN_mode` node. A mode change requires explicit confirmation, stops OHC automation, invalidates calibration and requires the physical test again; OHC must never infer electrical mode from a board or fan name.
- **3.4.29.8:** A persistent fan-helper rule may have a root-owned, world-readable status marker so the unprivileged UI can report grant state on Fedora systems where the Polkit rule directory is intentionally non-traversable. The marker is not authority; Polkit remains authoritative, and grant/revoke must update rule and marker together.
- **3.4.29.8:** Automated/offscreen UI construction tests must not launch hardware-owning helper processes. An unexpectedly crashed OHC-managed OpenRGB engine is quarantined for the current session to prevent restart/coredump loops; only an explicit manual retry clears that quarantine.
- **3.4.29.8:** Levita images and ordinary videos are prepared into aspect-preserving 1600×720 cache copies; imported originals remain immutable. The photographed reference default is a centered background with an 80-pixel right mask, while saved user geometry remains adjustable. Manufacturer assets are grouped locally by stable filename prefix and are never fetched or packaged by OHC.
- **3.4.29.9:** Levita theme categories mirror TRCC Linux's current `CzhordeCatalog` exactly: Gallery `a001–a082`, Tech `b001–b025`, HUD `c001–c072`, Light `d001–d055`, Nature `e001–e054` and Aesthetic `y001–y010`. OHC classifies only a validated, in-range original ID and otherwise uses custom files; it may not guess from media contents, download the catalog or package manufacturer assets.
- **3.4.29.10:** Levita list previews remain embedded and local. Video hover animation may create bounded cached thumbnail frames through headless `ffmpeg`, but it must not launch an external player or fetch media. Every invocation of the Qt-based OpenRGB binary, including synchronous version/inventory probes during page construction, remains explicitly offscreen.
- **3.4.29.10:** Complete Levita hardware-data designs remain a separate live layer above local videos. OHC must use the backend's established `load-theme` then `play-video` sequence so `config1.dc` is adopted without parsing or rewriting it, and must combine a selected theme's `01.png` with the physical right-bar mask instead of replacing either. The custom movable OHC metrics are an alternative upper layer, not an automatic duplicate of a complete TRCC design.
- **3.4.29.11:** Until the unexplained empty startup window is identified, OHC keeps privacy-bounded diagnostics for every own Qt top-level/native surface event and every helper-process launch. Diagnostics must never enumerate unrelated Wayland clients, expose positional secret arguments or block a process start; they write both to the early persistent startup log and the visible session log.
- **3.4.29.11:** The user-supplied full Open Hardware Control logo is the in-app brand mark. Its separately generated text-free transparent derivative is the canonical window/tray/taskbar icon and must remain available in standard Linux PNG sizes.
- **3.4.29.11:** Automatic TRCC design discovery is restricted to the verified Levita landscape directory `~/.trcc/data/theme1600720l`. Loading a complete design adopts its existing `config1.dc` through TRCC without parsing or rewriting it; test mode remains the default and discovery alone never authorizes a USB write.
- **3.4.29.12:** Levita display autostart is opt-in and stores one exact background/data-layer pair. It runs only after desktop startup quiet time, remains blocked by test mode, serializes through the existing TRCC queue and may retry a busy/not-ready display exactly once. Kraken LCD profile restoration and Levita display restoration remain separate device writers.
- **3.4.29.12:** OHC may package project-owned 1600×720 backgrounds, but never manufacturer catalog assets. A broad TRCC import may expose a `config1.dc` theme only when a verified `1600720l` path or exact 1600×720 PNG preview proves the Levita geometry.
- **3.4.29.12:** The canonical Linux window identity is `open-hardware-control.desktop`; Qt desktop-file ID, `StartupWMClass` and installed icon-cache basename must stay aligned so Plasma can associate the running window without changing hardware behavior.
- **3.4.29.13:** A remembered Levita custom-media path and whether it is included are separate settings. Disabling inclusion removes only its catalog entries; it must never delete, move or rewrite user media, and re-enabling restores the last valid custom selection without a new picker.
- **3.4.29.13:** Complete `config1.dc` themes default exclusively to data layer 2; layer 1 defaults to images/videos without live values. A persisted, explicit per-theme move may override that classification. This UI classification never parses or rewrites manufacturer theme data.
- **3.4.29.13:** Levita brightness and orientation use TRCC's bounded `set-brightness` and `set-orientation` commands and remain separate from Kraken LCD controls. Levita USB writers may not overlap: the play loop must release first, a bounded quiet period precedes the next handshake, and a confirmed timeout may be retried at most once.
- **3.4.29.13:** Applying a global chassis-fan preset changes only stored curves. It never marks a header calibrated, enables automation or bypasses CoolerControl/firmware ownership.
- **3.4.29.50:** The owner-defined chassis-fan **Leistung** preset is a constant 100-percent curve. Selecting it while OHC control is already active forces immediate reevaluation, but still writes only physically confirmed, individually enabled channels and never bypasses CoolerControl ownership. The existing 3.4.29.13 no-auto-activation rule remains intact.
- **3.4.29.50:** When a driver exposes no `pwmN_mode`, OHC must state that electrical PWM/DC selection remains firmware/BIOS-owned and may still use the documented `pwmN` duty/DC value. It must not infer or write unknown Super-I/O mode registers. A bounded confirmed 0-percent stop test is the supported identification path and restores the previous state.
- **3.4.29.14:** Levita card thumbnails must never be decoded synchronously on the Qt UI thread. Use a bounded background queue and persist results under a cache identity derived from source path, size and modification time; recent failures must be suppressed temporarily rather than retried on every filter rebuild.
- **3.4.29.15:** The Levita main preview represents the physical 1600×720 display, not the available page width. It stays centered at that aspect ratio, while layer 2 must remain visible over either an image or video background and may use a complete `Theme.png` only as a preview fallback when no transparent data layer can be extracted.
- **3.4.29.16:** Levita media catalog deduplication is case-insensitive by complete basename including suffix. It may hide duplicate cards and migrate selections, but must never delete, move or rewrite the underlying user files. A genuinely different filename remains independently selectable.
- **3.4.29.16:** The confirmed unwanted startup surface is an OHC-owned exact `QFrame` signature: top-level `Window`, no QWidget parent, no title/object name, non-modal and exactly 640×480. Only that full signature may be quarantined automatically. Named frames, dialogs, popups and other geometries remain observable but unblocked; helper-process proximity is diagnostic timing context, never proof of ownership.
- **3.4.29.17:** The Plasma system-tray entry must use OHC's own compact raster set and never request an unrelated generic theme icon. A native transparent 22×22 asset is installed in `hicolor`; 32/48/64 variants remain embedded in the runtime `QIcon` for host-specific tray requests.
- **3.4.29.18:** A Levita layer-2 element is one logical live-data block. When label, live value and unit share one format, they must move together; each block may be positioned and reset independently, while a separate X/Y offset may move the complete layer. User edits belong to OHC settings/cache only. Imported `config1.dc`, artwork and media remain immutable.
- **3.4.29.19:** A complete Levita theme may use either legacy `config1.dc` or TRCC's next-native `trcc.json`. OHC validates native JSON size, object/element shape and exact 1600×720 geometry before constructing `load-theme`; it must never fabricate a compatibility DC merely to satisfy an OHC preflight.
- **3.4.29.20:** TRCC text `x/y` coordinates are visual block centres in both preview and staged hardware themes. Background video frames may update only the background pixmap; they must not recreate layer-2 drag items. A dashboard card whose required hardware value is unavailable remains hidden without overwriting its saved user-selection preference.
- **3.4.29.21:** The Levita camera bar keeps a straight inner edge. Only the two outer-right corners of the 1600×720 display are rounded, in the preview and in prepared cache images. Selecting an Ebene-1 card must paint that image or a cached first video frame immediately; a black canvas is not an acceptable waiting state when a still is already available.
- **3.4.29.24:** Imported Levita records fail independently within the existing bounded input limit, and TRCC themes containing symlinked config/artwork are not trusted as local themes. Persisted preview-only split mode defaults to Off on missing or malformed data. A long-running renderer is active only after confirmed process start. Runtime and developer archives are separate profiles: only the developer profile must carry the complete tests/scripts/workflows/tools inventory, and the builder enforces that distinction.

## Assets and licensing

- Use project-owned schematic graphics by default.
- Do not embed third-party product photos, manufacturer renderings or copied UI artwork without verified redistribution rights and required attribution/license handling.

## AI development and memory

- **3.4.26:** Repository memory files and tests are the durable source of truth; a long chat is not.
- **3.4.26:** Agents must update `PROJECT_STATUS.md` after meaningful project changes and this file when a durable decision changes.
- **3.4.26:** Cursor project rules and hooks are version-controlled so fresh chats inherit project constraints.
- **3.4.27:** The historical `src/kraken_control.py` monolith is reduced incrementally through focused, non-circular modules. During migration it remains the executable compatibility orchestrator and re-exports moved names; large simultaneous UI and hardware-writer rewrites are not accepted.
- **3.4.27:** `MODULE_MAP.md` is the task-routing guide for context-limited local coding models. Agents should read targeted functions and their direct dependencies instead of loading the complete main file for every task.
- **3.4.29.18:** `MODULE_REGISTRY.md` is the mandatory current-version index and must be updated with every source, responsibility, path, dependency or module-version change. Its change dates use `TT.MM.JJ` without a time. New or migrated modules keep exactly one current `src/modules/<name>/v<major>_<minor>/` folder; Git history replaces source backup folders.
- **3.4.29.18:** Handwritten modules target at most 600 lines/32,000 characters and must be split before 800 lines/40,000 characters. New files above 1,200 lines/60,000 characters require an explicitly registered generated/legacy exception. UI, state, persistence, rendering and hardware transport remain separate responsibilities.
- **3.4.29.51:** Localization is a required part of every UI change. German source text plus English, Spanish and French must be changed atomically; interactive controls are guarded by the full offscreen UI build. Dynamic captions use translated fragments, while stable data IDs – never localized labels – drive logic. Exemptions are limited to technical identifiers, measured values and proper names.
- **3.4.29.52:** Localization is a versioned module with one complete data file per supported language under `src/modules/localization/v1_0/`. German is the canonical source; every language uses the same stable message IDs, and `catalog.py` rejects duplicate German sources or missing/extra IDs. The root `localization_catalog.py` remains only as a compatibility facade.
- **3.4.29.53:** A controlled Levita shutdown must release the fixed `87ad:70db` device from the single-owner TRCC daemon after stopping OHC clients; `stop-video` alone is insufficient because the daemon can keep re-rendering the persisted OHC cache theme. The firmware's built-in Thermalright screen is the fallback after its documented no-frame timeout. A separate pipe-bound helper may repeat only that validated, bounded daemon disconnect after unexpected parent loss, is armed only after a confirmed real write, and is cancelled after a confirmed clean restore. No process-level guard can guarantee execution after complete power loss or an operating-system-wide simultaneous hard kill.
- **3.4.29.66:** Backend choice is persisted independently from hardware detection. Automatic mode may resolve only to an implemented adapter; an explicit unavailable choice fails closed and is never silently replaced. Planned native Levita and CoolerControl adapters are visible but disabled until they have a validated transport and ownership contract.
- **3.4.29.66:** Overview temperature history is session-only and consumes existing validated readings. It opens no sensor itself, stores nothing on disk and never invents a coolant value when hardware reports none.
- **3.4.29.67:** Detailed temperature recording may read every plausible Linux-hwmon source, but it remains read-only, in-memory and non-owning. Open Radeon Control Center or another monitor may read the same kernel attributes concurrently; any future GPU/CPU tuning writer requires a separate explicit ownership contract and must never be inferred from sensor access.
- **3.4.29.67:** Thermalright publishes Levita maximum RPM but no minimum PWM duty. OHC must not call its floor a manufacturer specification; it enforces a conservative internal 50% pump and 25% radiator minimum at input, profile, curve and final-write boundaries until stronger model evidence exists.
- **3.4.29.70:** The LCD import workflow will be replaced in one of the next two or three internal versions by a non-destructive Design Manager. It will manage multiple source folders and individual image/video entries; removing an entry from OHC must not delete its source file unless a separate explicit destructive action is introduced and confirmed.
- **3.4.29.69:** Every main section with multiple child pages should expose both expandable sidebar children and synchronized browser-like in-page tabs. Stable page IDs, never translated captions, drive navigation. Display Effects mirrors an active bundled medium by exact validated path; programmatic synchronization must block user-change side effects and hardware writes.
- **3.4.29.71:** Animated Layer-2 decoration is composed as a validated local Layer-1 video paired with the editable data layout; OHC must not simulate animation by repeatedly rewriting a USB mask. Display-effect design cards always retain visible creator, original-source and licence links. Under KWin, a maximized main window is first placed normally on its requested screen and re-maximized on the following Qt cycle so compositor restore state cannot silently override the selected output.
- **3.4.29.72:** The physical Levita display keeps 15 FPS as its conservative default. A 60-FPS choice requires an explicit experimental Settings opt-in, carries a technical-risk warning without claiming to waive statutory rights and falls back through 30/20/15 after unexpected ticker failures. Automatic game mode accepts only Feral GameMode, Gamescope, an explicit process allow-list or the manual switch; it uses neither load heuristics nor generic Wayland window observation. Animated decoration belongs to editable Layer 2 and is locally composed with Layer 1 into the existing single TRCC stream. Main-window normal geometry, last maximized state and forced startup mode remain separate persisted values.
- **3.4.29.73:** Restoring a cooler's original screen is model-specific. Thermalright Levita stops OHC clients and disconnects the existing single-owner TRCC daemon so firmware can resume after its timeout; NZXT Kraken retains its validated liquid-temperature command. The Thermalright action uses no second transport, is write-free in test mode, accepts an already-detached daemon idempotently and does not alter the saved startup profile. Explicit tray Quit sets a dedicated final-exit state before invoking the existing cleanup exactly once. Light Bands remain native 1600×720 media; sharpness is improved through deterministic 2× supersampling and higher-quality encoding rather than unsupported panel resolution.
- **3.4.29.74:** A requested maximized state must not be applied synchronously before the first Wayland mapping. OHC first maps a normal window on the selected `QScreen`, maximizes in the next Qt event-loop cycle and then compares the compositor-observed screen with the target after a bounded delay. A correction is permitted only for a mismatch; it never polls continuously or fights later user movement. Tray activation follows the same visible-then-place-confirm ordering. Diagnostics distinguish requested target from observed mapping.
- **3.4.29.75:** The internal normal-map transition is guarded from state persistence until the requested startup presentation is finished. Automatically loaded profiles do not own window size, maximization or target screen and must not schedule a second placement pass; manual profile application remains explicit. LCD and effect card columns derive from the actual viewport. The LCD manager stores only bounded local references, aliases and exclusions and never renames, moves or deletes source media. Temperature sampling continues for every discovered read-only sensor regardless of chart visibility; a disk file exists only after an explicit selected-range CSV/JSON export.
- **3.4.29.76:** Long-running Levita protection monitors only the exact current-user TRCC daemon and never signals an arbitrary process. At the bounded 1-GiB RSS threshold or a recognized lost-IPC stream failure, OHC stops its ticker, uses TRCC's idempotent IPC kill command and reapplies the selected design through the existing sole-writer queue; a five-minute cooldown prevents loops. Visible logs retain one hour with hard memory caps, while privacy-redacted errors are additionally stored in a private bounded file.
- **3.4.29.77:** Expensive previews and gallery construction are owned by page visibility; hidden LCD/RGB pages must not keep their high-frequency animation work alive. Emergency Levita release may signal only a freshly revalidated exact same-user `trcc daemon` and must reuse the existing serialized apply queue. The first visible main-window frame must already carry the persisted presentation state. External backends remain separately installed and are never silently upgraded by OHC; compatibility is documented against official releases, while real hardware validation remains explicitly distinct.
- **3.4.29.78:** Continuous presentation rendering is owned by actual visibility across the application. Hidden pages pause local decoders, animation timers and thumbnail work, while physical RGB/LCD output, sensor sampling and cooling control remain active because they are hardware responsibilities rather than UI rendering. Gallery painters process only the exposed viewport. Display Effects may cache validated local posters and reuse card widgets, and its local composition is capped at 20 FPS independently of physical display FPS. Close-to-tray is permitted only when Qt reports a visible tray icon with valid geometry; otherwise closing performs the existing orderly hardware exit.
- **3.4.29.79:** A requested close-to-tray action must never trigger hardware shutdown merely because Plasma temporarily reports an invalid tray-icon rectangle. OHC keeps the window visibly minimized in that case; only explicit/no-tray exit owns orderly hardware cleanup. The frameless close target reaches the physical top-right corner and is excluded from resize-edge interception. UI transitions paint only a short-lived transparent overlay and never capture a page. The shared SSD cache owns only regenerable OHC catalogs and scaled previews, is user-bounded to 0–4 GiB, and evicts oldest entries without touching source or active hardware files. Potentially multi-second ENE recovery waits until navigation is idle. The NCT6687 assistant may inspect signing state read-only and offer only fixed confirmed DKMS/MOK/module terminal actions; passwords, reboot and physical firmware enrollment remain outside OHC, and Secure Boot is never disabled or bypassed.
- **3.4.29.80:** On KDE/Wayland, a visible `QSystemTrayIcon` with an available system tray is a valid StatusNotifier target even when Qt cannot expose its rectangle; geometry remains diagnostic only. Chassis-assignment reset must stop active OHC control, restore firmware ownership, clear calibration/activation/positions and retain curves. Missing physical sensors are absent from choices rather than represented as warnings. A PC-layout double-click may route only to an already assigned device and the existing bounded OpenRGB editor; it never upgrades a native-mode/one-logical-LED device into invented Direct segments. Affirmative `mokutil` enrollment text remains authoritative when an unrelated optional kernel-keyring access warning changes only the process exit code.
- **3.4.29.68:** Cooling owns two fixed, non-hideable child entries under its reorderable main navigation item, matching LCD. Sidebar selection and the internal Cooling view must stay synchronized so a feature is never present but undiscoverable; the child entries do not represent separate hardware owners.

## GPU-Testtrennung, räumliche Maße und UI-Leerlauf · 3.4.29.130

- Ein GPU-Lüfterentwurf darf keinen Grafikbenchmark starten. Fan-only nutzt den
  rückstellenden LACT-Lüfterpfad; Takt/Leistung und ausdrücklich gestartete
  Lasttests bleiben die einzigen Besitzer von Grafiklast.
- Räumliche Gehäusebeziehungen sind Nutzermesswerte, keine Hardwareerkennung.
  Sie verweisen ausschließlich auf vorhandene Komponenten-IDs, werden intern
  in Millimetern gespeichert und dürfen in Millimeter oder Inch bearbeitet
  werden. Fehlende Herstellermaße werden nicht berechnet oder erfunden.
- SSD-Cachepflege ist regenerierbare Hintergrundarbeit. Sie wartet nach
  Eingaben, läuft mit niedriger CPU-/I/O-Priorität und gibt kooperativ Zeit an
  Qt-Oberfläche und Displaypfad zurück; Originale und aktive Hardwaredateien
  bleiben außerhalb ihres Besitzes.

## TRCC-daemoninterner Levita-Dauerbetrieb · 3.4.29.131

- TRCC Linux 9.10.4 besitzt nach einem erfolgreichen `display play`-Aufruf
  Video- und Sensor-Takt dauerhaft im daemoninternen `VideoLoop`. Nur die
  exakte Erfolgsbestätigung des Backends gilt als geplante Übergabe; andere
  Prozessenden bleiben Fehler und unterliegen dem begrenzten Neustartbudget.
- Die Übergabe beendet nur den kurzlebigen CLI-Helfer. OHC lässt seine
  Speicheraufsicht und die begrenzte Notfallwiederherstellung aktiv, startet
  aber keinen nutzlosen zweiten Taktgeber und öffnet keinen zweiten
  USB-Besitzer.
- Der unabhängige Levita-Abschaltwächter muss auch als direkt per Dateipfad
  gestarteter Python-Prozess funktionieren. Er ergänzt deshalb vor dem Import
  versionierter OHC-Module genau seinen installierten Anwendungsstamm; die
  bestehende feste Geräte-ID, Pipe-Bindung und einmalige Freigabe bleiben
  unverändert.
- Externe Backends werden nicht still durch OHC aktualisiert. Die auf dem
  Referenzrechner ausdrücklich installierte offizielle TRCC-Version 9.10.4 ist
  die aktuelle Empfehlung und wurde getrennt von OHC paketiert und geprüft.

## GitHub publication

- **06.09.26 / 3.4.29.47:** The repository layout is fixed and the GitHub front page must stay short. The root holds only `README.md`, `LICENSE`, `CITATION.cff`, a short `AGENTS.md` pointer and dotfiles. All application code lives in `src/` (mirroring the flat installed directory), installer and version files in `packaging/`, every document in a `docs/` subfolder, community and security policies in `.github/`. `README.md`/`docs/README.en.md` stay under 200 lines with a fixed section order, one replaced-per-release "Neu in" section, a clickable screenshot gallery and at most four history entries; longer text goes to `docs/CHANGELOG.md` and `docs/releases/`. `tests/test_repository_layout_342947.py` enforces this; installed package layouts are unchanged.

- **2026-08-27 / 3.4.26:** The project owner explicitly removed the Google Drive backup workflow and its mandatory push gate. GitHub publication does not depend on Google Drive or another external backup provider.
- **2026-08-27 / 3.4.26:** Pushes, tags and releases still require a clean committed worktree, relevant successful tests, the correct release channel and an explicit project-owner request.
- **2026-08-27 / 3.4.26:** Authentication credentials and tokens must never be stored in the repository.
- **03.09.26 / 3.4.29.36:** Every successful version build creates a complete local release backup in the sibling directory `Open Hardware Control Backup`. The two newest semantic versions are retained with runtime archive, complete developer package, source archive, Local-AI Git bundle, every generated DEB/RPM package, release notes and independently generated SHA256 checksums. This is the sole exception to the prohibition on source backup folders, remains outside the repository, does not restore the removed Google Drive workflow and is not a GitHub push gate.
- **03.09.26 / 3.4.29.37:** Levita layouts with literal units must transmit `show_unit=true`, because TRCC otherwise strips `%`, `°C`, `MHz` and related suffixes from an already formatted value. OHC migrates its bundled saved overrides automatically. Layer intensity is a presentation-only 25–150% setting; Orbital defaults to 130% and Nebula remains 100%. The AMD idle-clock workaround is read-only and may update only the affected live block through the existing TRCC daemon socket; it never opens another USB owner and logs state transitions only.
- **02.09.26 / 3.4.29.25:** `BUILD_CHANNEL=INTERN` blocks public release publication, not an owner-requested normal push to a non-release development branch or an owner-requested pull request. A branch push requires committed intended changes, a clean worktree and relevant successful tests. Tags, public releases, force-pushes and remote deletion are distinct actions that require separate explicit owner authorization; public tags/releases additionally require the validated `STABLE` channel. Default no-push wording must never be interpreted as an absolute inability to act after an explicit owner request.
- **02.09.26 / 3.4.29.26:** A Levita layer-2 apply stages its selected background video, generated panel mask and editable data blocks into one cache theme so one connected TRCC `load-theme` process owns the complete composition. Complete design switches are coalesced behind a ten-second post-start USB protection interval. A handshake timeout receives only one total retry; an enumerated device whose bulk IN endpoint remains silent is not hammered by a second nested startup retry and requires a complete power cycle before real validation continues.
- **02.09.26 / 3.4.29.27:** Layer-2 preview artwork is composited as transparent artwork and must never be passed through the opaque background-fitting path. A selected MP4 remains bounded to cached preview frames rather than a permanent decoder process. `QProcess.CrashExit` from TRCC is an external backend failure: OHC stops automatic USB attempts and reports it separately instead of presenting device enumeration as proof that the transport is healthy.
- **02.09.26 / 3.4.29.28:** OHC uses TRCC's documented daemon mode as the sole Levita USB owner. Every TRCC CLI process receives `TRCC_DAEMON=1` and acts only as a Unix-socket client; the daemon's built-in metrics loop owns continuous rendering. OHC must not launch a second `display play` process after `load-theme`, because a fresh in-process App repeats the handshake and can race libusb/hidapi teardown.
- **02.09.26 / 3.4.29.29:** Runtime logs corrected one part of the 3.4.29.28 assumption: TRCC's daemon metrics loop re-renders sensor values but does not dispatch `TickDisplay`, so it cannot advance a video cursor. OHC may run one long-lived `display play` process only with `TRCC_DAEMON=1`; it is an IPC ticker against the already connected daemon and therefore not a second USB-owning App. Editable cache themes must explicitly apply their combined mask after `load-theme`, because theme metadata does not override a persisted runtime `mask_visible=False` state.
- **16.09.26 / 3.4.29.98:** The first explicit choice to keep OHC running in the tray is a durable user preference, so later window-manager close events hide without repeating the dialog. On upgrade, only an actual bounded private `window-close-choice=tray` record may seed the new setting; the older state “tray checkbox enabled” alone is insufficient. Explicit Quit, Cancel, disabled tray mode and desktop-session shutdown remain separate and must not be redirected by this preference.
- **17.09.26 / 3.4.29.99:** Minimize-to-tray and Close are separate contracts. The existing tray preference is migrated to `app/minimize_to_tray` and applies only to minimization; any real window-manager or taskbar Close performs the ordered hardware hand-back and exits. The `.98` remembered close-choice key remains harmless legacy data and no longer redirects Close. Display Effects and LCD Studio also share one canonical Levita startup design. Hidden Qt multimedia previews unload their decoder sources, followed by one debounced idle collection/optional glibc heap trim; there is no periodic memory task or SSD swapping of private runtime state.
