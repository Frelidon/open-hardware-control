# Open Hardware Control — Project Status

**Current development version:** 3.4.29.160 STABLE

**Status date:** 4 November 2026

**Release channel:** STABLE — the project owner explicitly requested GitHub publication and local installation after the complete release gate.

Version 3.4.29.160 carries the public OHC-only design catalog and Feature
Lifecycle work from the `.159` candidate, and makes the full Levita UI release
test deterministic on hardware-free CI by selecting its isolated cooling
fixture explicitly. Application detection and hardware paths are unchanged.

Version 3.4.29.159 prepared the public OHC-only design catalog and added the
hardware-inert Feature Lifecycle 1.0 registry. Every main area now has an
independent semantic version and Alpha, Beta, Release Candidate or Stable
maturity label in feature cards and navigation settings.
The former “Beta Plus” description is represented by the standard Release
Candidate label. These values are presentation metadata only and do not enable,
disable, migrate or own hardware. Existing profiles, case-fan RGB animation,
spatial LED routes, PWM mappings and hardware handoff paths remain unchanged.
Bundled stock media and third-party design components are excluded from the
public package while all import, editor, preview and transfer functions remain.
Real Fedora hardware and optical case-RGB confirmation remain open.

Version 3.4.29.158 addresses the two actionable faults in the owner's 3.4.29.157
runtime log. OpenRGB SDK 6 packet 157 is the documented active-profile-change
callback, not a failed ACK; OHC now validates and consumes it without interrupting
MSI Mystic Light frames during the bounded ENE-DRAM recovery. The existing
read-only TRCC correction for the exact 1 MHz AMD idle boundary remains, but the
dynamic source is restored only after three consecutive valid samples. Missing
or malformed measurements reset that evidence. No hardware ownership, profile,
LED count, permission or write path changed. Repository tests do not replace
optical RGB confirmation or a real Fedora hardware run.

Version 3.4.29.157 closes the remaining repository action from the active
Programs roadmap: after a complete verified GitHub download, an exact AppImage
asset can be assigned directly to a selected AppImage profile. The file must
still match the inspected release plan and reported size; installation retains
its independent base-folder, regular-file, size and AppImage-header validation.
The Levita conflict path also distinguishes the exact TRCC daemon registered by
the current OHC session and performs the already established bounded restart and
design restoration once. Foreign, preexisting and PID-mismatched owners remain
untouched. Real Fedora hardware coverage and optical case-RGB brightness,
direction and order confirmation cannot be completed by repository work and
remain explicitly pending.

Planning and performance follow-up 20.10.26: the active roadmap now separates
repository work from owner/real-hardware confirmation and long-term candidates;
the `.130` implementation protocol is explicitly historical. Performance work
is profile-driven and keeps blocking discovery, decoding, network, package and
filesystem activity outside the Qt main thread. Large UI responsibilities are
split incrementally into versioned modules with stable Python interfaces and pure
testable helpers. A complete Rust rewrite is rejected because it would discard
proven UI, hardware, packaging and regression behavior without a measured gain;
Rust remains possible only for a demonstrated isolated CPU hotspot with Python
fallback and identical fixtures. The case fan preview applies a small bounded,
cached brightness lift to non-black RGB segments and a slightly wider light ring,
without changing effect phase, physical mapping, hardware writes or hidden-timer
behavior. The Programs module is implemented within the bounded inventory,
profile, verified-download and confirmed-installation scope described below;
generic distribution system packages remain intentionally fail-closed.

Versions `.151` through `.156` were audited individually against their release
notes, registered modules, regressions and later status evidence. Their described
repository changes are present. Historical package/install caveats for `.151`–
`.154` were superseded by later successful build and Ubuntu installation evidence;
they are not missing code tasks. The honest remaining items are real Fedora
hardware coverage from `.155` and optical case-RGB brightness/direction/order
confirmation from `.156`. Programs 1.0 now adds the non-installing foundation:
a bounded desktop inventory outside the Qt main thread, search, an absolute base
folder and validated saved System/Flatpak/Snap/AppImage profiles. Its separate
explicit GitHub action previews a stable/tagged release, then downloads at most
100 official assets plus both source archives into a new owner/project/version
folder. Per-file and total limits, final-host validation, byte-count checks,
SHA256SUMS, a JSON manifest, atomic publication and no-overwrite behavior apply.
It executes no discovered desktop command, package manager or installation.

The current Programs stage includes explicit manual installation profiles. Flatpak uses
the already configured Flathub remote as a per-user install, Snap uses its exact
validated name and optional channel through Polkit, and AppImage only adds the
current user's execute bit after the file is confirmed inside the selected base
folder with an AppImage/ELF header and size bound. The exact argument-array plan
is shown before confirmation; no shell is involved and process output is capped.
Generic system packages remain fail-closed because a desktop name is not a safe
cross-distribution package identifier. A profile can persist its normalized
GitHub owner/repository and separately remembered source-release version; selecting
that profile restores both fields without conflating the source release with a
Flatpak branch or Snap channel.

Case RGB interaction follow-up 06.10.26: `.156` addresses confirmed UI and pure
rendering bugs from the owner's `.155` interactions. An unchecked optional LED
path group disabled all fresh draft fields, including after native Qt child
polish/reparenting. Draft fields are now editable; explicit user gestures alone
activate the commit flag. Opening, count-only updates and Cancel do not persist
a guessed path. Line/ring applicability and validation remain enforced.
Spatial wave phase was inverted unnecessarily, a header's own spatial direction
was omitted from rectangle construction in global-local mode, and local effect
reversal was ignored. Pure fixes preserve physical numbering, global/per-header
precedence, user group signs, counts and unchanged legacy frames without a path.
The fan view now renders bounded RGB light-ring segments at the same confirmed
effect phase, including schematic colours on unambiguous declared headers without
an exact physical path. Hidden timers stop; this is not measured rotor/RPM motion.
Flow widgets retain drafts through routine refresh and reflect loaded persisted
direction; a translated status explains a missing path rather than implying it
was created. Language source 2824 brings all four catalogs to 2,154 sources.
New targeted Qt/pure tests cover both distribution fixtures; no hardware,
backend commands, profiles, LED counts or permissions were changed in this work.
The full `.156` release gate passed 1,301 tests and five subtests, including
actual four-language Qt coverage, security/privacy and module budgets.
Both actual `.156` packages and all distribution checksums passed. Independent
archive review verified 153 DEB and 123 RPM directories root-owned 0755, twelve
runtime-source contents, fixed system-helper modes/digests and unchanged Fedora
dependencies. Both retained `.155`/`.156` external backup checksum sets pass;
only the recognized older `.154` backup was normally rotated. Private profiles
and configuration were exclusively copied into new verified 0600 local backups
after the old owner exited via its ordinary SIGTERM handler. Its journal reports
successful cleanup and all exact RGB/LCD child owners exited. APT simulation
updates only OHC and removes no packages. The owner confirmed normal Ubuntu
package authentication; APT completed the local update with zero network download
and no other package changes. DPKG verifies `.156~intern2`, package integrity
and all 365 installed Python files match the tested source. Private profiles and
configuration remained byte-identical to the new backups before relaunch.
Noninteractive fan/metadata authorization and the fixed identifier-filtered RAM
read succeeded without another prompt. Normal graphical startup automatically
loaded the saved five-device RGB design, completed both eight-LED DRAM reclaims
and started one SDK worker. The OHC-owned LCD daemon holds the display interface;
two health replies report advancing 452-frame playback at 15 fps. No new Python
exception or crash-log update was observed. This validates process/protocol
progress, not physical lighting; startup grants and login-autostart choices are
unchanged. The built package snapshots contain the pre-installation report;
this final installed-runtime evidence is a post-build source-document update.
Real Fedora hardware and optical RGB confirmation remain separately pending.

Ubuntu startup/USB-owner follow-up 06.10.26: the final `.155` is installed
and its controlled startup is verified. The original owner logs showed complete RGB
inventory followed by manual ownership confirmation, not an automatic
profile start. Read-only settings inspection identified two independent
configuration blockers: a retained NZXT assistant preset and a different
startup profile with its own automation flags off. The new pure Cooling State
policy lets only known NZXT presets stop blocking an explicitly chosen startup
profile in the confirmed Ubuntu/Levita/no-ready-NZXT lane. It leaves that
preset and explicit profile cooling intact; no PWM mapping or calibration is
invented. Selecting the owner's current private profile and cleaning its
obsolete setup selection is a separate authorized, backed-up local operation,
not a shipped migration or release default.

The Ubuntu LCD path now recognizes an explicitly occupied USB interface as
an ownership conflict. It cancels only OHC's apply/startup/ticker retries,
keeps the saved design and reports the primary failure instead of a final
udev hint. It does not kill a foreign process, change FPS or create a second
USB owner; another explicit Apply remains available after owner release.
The four language catalogs contain 2,153 shared sources. The mandatory AI
rules now require separate Fedora/Ubuntu paths, native commands and targeted
regressions, preserving features, templates and settings on both. Real Fedora
hardware has not been tested in this Ubuntu follow-up and remains pending.

The focused startup/RGB/cooling run passed 76 tests; LCD ownership/language
regressions passed 88 tests, with separate unchanged-Fedora branches. The full
final `.155` release gate passed 1,132 tests and five subtests, including real Qt
offscreen four-language coverage, security/privacy and module-budget checks.
The first `.155` build and both retained `.154`/`.155` checksum sets passed.
APT upgraded only OHC with zero network download; DPKG verifies `.155~intern2`
and all 364 installed Python files match the tested source. Existing system
ancestors remain root-owned 0755, DMI helper 0755, policy 0644 and the narrow
fan grant remain intact. Non-interactive read-only DMI and fan authorization
checks succeeded. Independent archive review found fresh-DEB directory mode
0775 could fail helper ancestry trust. Its stage-only correction passed the
real umask-002 regression and final rebuild/archive verification: all 153 DEB
and 123 RPM directories are root-owned 0755; both payloads' five helper/policy
files and the final LCD runtime match source. RPM header/payload digests and
unchanged Fedora dependencies validate. All distribution checksums and both
retained `.154`/`.155` backup sets pass. Only the recognized older `.153`
release backup was rotated under the standing owner policy; private backups,
profiles and unrelated data were not removed. No host-wide permission change
was made. The final normal local-DEB reinstall succeeded with zero download;
DPKG integrity and all 364 installed Python files match the final source.

An authorized private backup preceded selecting the current PC startup profile
and clearing only the known stale setup value. Saved profile bytes, cooling
curves, LED topology and design payloads remain unchanged. OHC and the separate
TRCC GUI exited through their normal handlers; the OHC journal records clean
cleanup and its own children exited. The explicitly approved TRCC GUI login
autostart was disabled reversibly; the unrelated USB quirk service is unchanged.
The installed `.155` normal tray-autostart path now loads the selected RGB
design automatically, completes both eight-LED DRAM Direct reclaims and starts
the five-device SDK worker; confirmed JARGB 1 retains 30 LEDs. The Levita theme
loads successfully, its OHC-owned daemon alone holds the USB interface and
TRCC status replies confirm advancing 452-frame video at 15 fps. The longer
run exposed a pre-existing missing canonical device-key import in the healthy
LCD status callback; every successful probe raised NameError without stopping
the independent video daemon. OHC was stopped cleanly before correcting this
shared import and adding actual Qt class-method/module-global success tests
for both distribution branches, rather than injecting constants into an AST
test. The corrected runtime is now installed and the subsequent tray startup
again takes over RGB and LCD automatically. Repeated successful LCD health
callbacks no longer produce that exception or alter the previous crash log;
the independent daemon reports continuing video frames. No optical RGB
or LCD result is inferred from these acknowledgements. Actual login-autostart
enrollment is still an explicit user choice; a system reboot was not performed.
All `.154` evidence and history below remain applicable to that release.

Ubuntu RGB/authorization follow-up 06.10.26: `.154` is installed for the
observed names-only OpenRGB 1.0 inventory regression and the external GPU
editor's incorrect native-controller requirement. Read-only SDK inspection
confirms complete Direct inventory with 8/8/30/114/6 LEDs; the SDK 6 descriptor
is not the cause. The private PC profile still retains the confirmed MSI
JARGB 1 GPU route and 30 LEDs. Preserve those settings and the remaining fan
topology. System authorization logs identify the repeated prompt as TRCC's
RAM-metadata DMI request in its daemon, not the already running fan-helper
session. Ubuntu's actual dmidecode path differs from the upstream policy;
merely granting general dmidecode would expose its file-writing options.
The Ubuntu OHC-child adapter instead uses an argument-free fixed read-only
RAM helper and dedicated action, without changing upstream files or global
PATH. The official USB rule is already present; its missing-rule hint is a
hard-coded-directory false positive. The refreshed release gate passed 1,063 tests
and five subtests, security/privacy scans, four-language checks and module
budgets. The `.154` package build completed; distribution checksums and both
retained `.153`/`.154` backup sets validate. APT simulation upgrades only OHC,
with no other install/removal. OHC was stopped in order. The first approved
package invocation failed before installing because its relative DEB path was
no longer valid after the administrator process changed working directory.
The absolute-path invocation with `--no-download` also failed in APT's local
archive acquisition before installation. The normal absolute-path APT command
then succeeded, with zero network download and no other package changes.
DPKG confirms `.154~intern2` installed with clean integrity verification;
all 363 installed Python source files match the tested source. Postinstall
verification caught a checkout-mode leak: the new policy was copied as 0664,
so the adapter correctly refused to trust it. Its exact installed mode was
corrected to 0644 without changing contents or other policies. The fixed
read-only helper now runs successfully under its dedicated non-interactive
active-session authorization, without a password dialog or device identifiers.
The package stage now enforces 0644 regardless of checkout modes; its five-mode
regression passes. The corrected `.154` build completed, and every distribution
checksum plus both retained `.153`/`.154` backup sets passes verification.
Independent archive inspection confirms DEB helper/policy ownership and modes,
but found that the fallback RPM's explicit manifest omitted the new DMI and
previously staged snapshot system helpers/policies. Its manifest is now
aligned with the normal RPM spec; this packaging-only correction changes no
Ubuntu installed bytes or Fedora commands. The final rebuild passed the full
1,063-test/five-subtest gate again. Independent inspection of the actual DEB
tar and RPM header/newc payload confirms all five required paths, source-identical
contents, root ownership, DMI helper 0755 and DMI policy 0644. Final distribution
and both retained backup checksum sets pass. No further host installation is
needed for this archive-only correction; installed runtime and helper/policy
contents remain identical, with clean DPKG verification.
Only package-stage metadata changed after installation; all runtime Python
files remain identical and the installed policy's corrected mode is 0644.
The existing root-owned per-user fan authorization marker remains intact.
No physical RGB writes/tests were performed;
optical output remains pending owner verification.

Private profile follow-up: after exact orderly OHC shutdown, the confirmed
GPU route/30 LEDs and all fan/PWM settings were retained. Only seven targeted
RGB settings were changed, with a persistent private pre-change backup. The
already shared two-DIMM bank was rebound to the two actually reported DRAM
devices, retaining 8 LEDs each and its common group; no unsupported mapping
between old hashes and individual physical DIMMs was made. The live obsolete
single-DIMM override was removed; the saved profile had no such override.
Both live and saved PC-profile selections now resolve to the verified inventory.

Local completion 06.10.26: the final release gate passed 1,005 tests and five
subtests, security/localization checks and both retained backup checksum sets.
The approved package upgrade completed; DPKG confirms `.153~intern2` installed
and its verification is clean. Critical installed source files match the
validated repository, and the trusted OpenRGB/liquidctl/CAM paths resolve as
the normal user. The existing root-protected fan grant remains present. OHC
was not automatically reopened; physical RGB/LCD/fan verification remains
with the owner.

Ubuntu preservation and backend audit 06.10.26: `.153` restores established
`.148` feature switches/ownership, design automation, snapshot controls,
responsive hardware cards, GPU illustrations, dashboard customization and four
original LCD animations without reverting the later Ubuntu fixes. Navigation
visibility no longer overwrites feature enablement. PC profiles retain their
own explicit radiator/pump routing; changing profiles cannot inherit another
profile's stale AIO mapping. Ubuntu GPU discovery, metrics and clocks run in a
bounded cancellable helper, keeping the GUI responsive even when LACT is slow;
an unavailable clocks table remains optional. GPU power increases require an
explicit inline confirmation. Windows preview scaffolding remains available.

External releases are checked read-only through official sources and native
package metadata. Ubuntu installation commands use `os-release`, include
vkmark, and never select a stray Fedora package manager. OpenRGB SDK 6 is an
explicit Ubuntu lane; protocol 4/5 and Fedora's default negotiation remain.
OpenLinkHub 0.9.2 user installs are recognized, rejected HTTP-200 writes are no
longer reported as successful, and Nexus touch bounds follow its current
inclusive lower-case schema. Portable backend updates are separate from distro
packages and never replace Fedora's executables. Real optical RGB output,
physical fan routing and new tuning writes still require owner verification.

Ubuntu backend updates use only the fixed root-owned versioned tree below
`/usr/local/lib/open-hardware-control-backends/`. The original distro binaries
and private settings backup remain available. The CAM streamer selects the
same trusted liquidctl environment; the GUI's Python/Qt runtime is unchanged.
The approved Ubuntu host update is complete: OpenRGB 1.0 and liquidctl 1.16.0
were verified as the normal user, without a hardware scan. Other installed
audited backends were already current; absent optional programs were not
installed. OHC was stopped in order before updating its backends; package
validation precedes reopening, with no unattended hardware test. All four
language catalogs now contain 2,152 shared messages.

Final regression hardening also binds delayed Hardware Fix/GPU callbacks to
their QObject lifetime and ties Hardware Checker replies to the exact current
process. All 14 delayed LCD callbacks now follow the window's lifetime;
library/progress callbacks cancel on deletion without changing timer or hardware
semantics. OpenLinkHub requests ignore environment proxies and reject redirects.
GPU fan text wraps at narrow sizes, with a vertical-scroll fallback keeping
the entire curve reachable. All 16 optional navigation modules, including the
restored automation centre, have synchronized visibility switches.

LCD preview lifetime and module-design update 05.10.26: `.153` fixes the
observed crash after rapid Levita category changes. Qt may keep a Python weak
reference alive after deleting the underlying preview-card C++ object; the
thumbnail visibility and completion paths now validate and prune those
wrappers before touching them. Delayed Snapshot Manager expiry callbacks apply
the same lifetime guard during shutdown. The restored sidebar module settings now match
the modern OHC design with two-column cards, icons, status dots, and toggle
switches while retaining the existing navigation visibility model. The exact
deleted-card regression and the complete offscreen UI render pass. Fedora
package/setup commands remain unchanged; restored shared UI features are
covered by hardware-disabled regression tests.

CPU/profile and PC PWM topology update 05.10.26: `.152` detects the installed
CPU at startup and loads its verified default curves only while the curve is
still automation-owned; a changed CPU selection, profile or curve remains
user-owned. CPU_FAN and PUMP_FAN are now available in the settings-only case
mapper, conflicts require confirmation, and assignments are synchronized into
the selected local PC profile. The owner-confirmed MSI MAG X870 TOMAHAWK WIFI
layout is migrated once by exact board-provided connector labels, without a
PWM write. The settings page again exposes all hideable sidebar modules. Four
language catalogs contain 1,916 entries. Fedora package/setup behavior is
unchanged.

NCT6687 recovery hardening 05.10.26: an observed obsolete CKB Next PPA caused
Ubuntu `apt update` to fail, and `.150` consequently skipped dependency
installation because both commands were joined with `&&`. Version `.151`
separates those steps, never edits third-party sources automatically, reuses an
existing `~/nct6687d` checkout only through `pull --ff-only`, and safely stops
on a conflicting non-Git directory. The wizard now presents the optional
per-user Polkit fan-helper grant as step five and reflects its root-owned status
marker. On the reference system the narrow grant for UID 1000 is now present;
it does not authorize package management. Four language catalogs contain 1,901
entries.

NCT6687 setup update 05.10.26: the guided driver/MOK flow reads the local
`/etc/os-release` and DMI board identity. Ubuntu, Fedora, and Arch Linux now
receive separate fixed dependency commands; the common upstream clone and DKMS
installation remain shared. MSI-X870-only module settings are emitted only for
a detected MSI X870 board. Unsupported distributions remain fail-closed, and
Arch users of non-default kernels are told to select matching headers. The
current reference host is identified as Ubuntu 26.04.1 LTS with an MSI MAG X870
TOMAHAWK WIFI. Four language catalogs contain 1,895 entries.

Ubuntu DEB update fix 05.10.26: the built `.149` package no longer requires the
obsolete, unavailable `policykit-1` package exclusively. It accepts the current
Ubuntu split `polkitd` plus `pkexec` packages while retaining the legacy
alternative for older Debian-family systems. The running `.148` log confirms
that X intentionally hides OHC to the tray; an update requires the explicit
tray action **Beenden** first. Fedora/RPM dependencies and runtime are unchanged.

RGB/LCD/NEXUS manager work 05.10.26: RGB Studio now presents startup profile,
automation, passive reclaim and current session control together at the top.
The first explicit takeover confirmation enables the two persisted automation
defaults, while every actual session still passes the existing ownership and
external-OpenRGB checks. The shared media library now includes GIF and is wired
to Kraken as well as Levita; bundled OHC designs remain independent of user
sources. A private OpenRGB profile library accepts validated `.orp` and v6 JSON
files but deliberately refuses partial application of opaque legacy profiles.
The new OpenLinkHub Nexus bridge imports 640×48 backgrounds and bounded touch
manifests into a detected user installation with an atomic database update and
backup, then uses the documented local API for activation. No direct Corsair
USB implementation was introduced. Fedora runtime/package behavior is
unchanged. Four language catalogs contain 1,888 entries.

RAM/Levita/restart hotfix 05.10.26: the two detected ENE DRAM modules are now
presented as one RAM bank, while their stable IDs, per-module LED counts and
device frames remain separate. A shared editor persists the count to every
module and the first manual design now executes the same bounded ENE reclaim as
profile autostart. Levita uses hardware mode by default only when USB device and
TRCC backend are both present; otherwise it remains fail-closed in preview.
TRCC 9.10.4 passes 11/11 local doctor checks and detects `87ad:70db`. An OHC
restart now waits for the old process and single-instance lock to end before
launching the replacement. No Fedora runtime or package path was changed.

PC-profile/RGB topology work 05.10.26: user PC profiles now retain the complete
validated settings-only topology instead of only the visible case blocks. This
includes stable ARGB controller/header routes, fan and LED counts, manual
headers, LED paths, RAM/device grouping and aliases, selected case devices,
GPU routes and known PWM-to-case assignments. Loading remains non-writing and
an absent controller/header fails closed. The embedded Case inspector no
longer discards a draft after a combo selection or incidental outside click;
only Save, Cancel, Escape or its close button ends the edit. The supplied
Ubuntu log repeatedly confirms full eight-LED SDK frames for both ENE DRAM
modules; it contains no RAM transport failure. No RGB, fan, GPU or display
value was written during the implementation checks.
The remaining RAM profile fault was a stale single-DIMM route attached to a
two-device RAM block. Multi-device direct blocks now retain every assigned
device, and resolved personal fan defaults are serialized into the user profile.

Ubuntu backend/library work 05.10.26: the detected Levita now gets an explicit
TRCC Linux install action in LCD and first-run setup, using the official pinned
9.10.4 DEB with SHA-256 verification. The existing LACT helper gains an
Ubuntu-26.04 package path without changing its Fedora or Arch branches;
OpenRGB remains wired in setup and RGB Studio. Fresh Levita profiles load OHC's
bundled designs without requiring an external directory, then merge validated
TRCC stock, downloaded catalog and user-media roots. On the reference Ubuntu
system TRCC 9.10.4 and LACT 0.10.1 are installed, `lactd` is active, and the
local library contains 5 stock layouts, 166 catalog videos/previews and 9
user-imported media files. No display design, GPU, fan or RGB value was applied.
Fedora files and runtime behavior were not changed.

Runtime hotfix 05.10.26: two observed starts of installed 3.4.29 build 148 were
followed within six to seven seconds by repeated RX 9070 XT amdgpu SMU
timeouts. OHC's private OpenRGB server was the common trigger and its CLI
clients performed redundant local detection on every inventory retry.
On Ubuntu, `OpenRGBClient.client_command()` now passes `--nodetect`; Fedora's
existing command is unchanged. The affected private Sapphire detector is
disabled locally. A bounded server/client verification kept the other six RGB
devices and produced no new SMU, GFX or ring timeout.
The failed configuration had selected all seven RGB devices including the
Sapphire controller. No RGB value, GPU clock, fan or power setting was written
during the verification test.

Version .131 adopts the installed and physically observed TRCC Linux 9.10.4
runtime contract. A successful hand-off to TRCC's daemon-owned VideoLoop is no
longer recorded or retried as a failed OHC ticker, while daemon memory
supervision remains armed as an emergency bound. The reference run continued
full 1600×720 writes with RSS near 183 MiB, 33 threads and 29 file descriptors
stable across the focused sample. The independent Levita shutdown helper now
adds the installed application root before importing OHC modules, fixing its
observed immediate standalone exception. No GPU, fan, RGB or snapshot write was
performed by this change. The complete release gate passes 839 tests plus the
security, privacy and module-registry checks. Runtime/developer ZIPs, source
archive, Local-AI Git bundle and RPM were built and SHA-256 verified together
with the rolling backup; `dpkg-deb` is unavailable, so no DEB was fabricated.

Version .130 implements the approved GPU, RGB and spatial-case pass. The GPU
cockpit fits its wide reference viewport without page scrollbars, its fan curve
supports direct dragging plus exact values, custom artwork is managed locally,
and a fan-only trial cannot start a graphics benchmark. RGB Studio keeps the
left navigation aligned with its compact six-column gallery. Spatial effects
gain direction, speed and real LED-order editing plus measured component
distance/depth stored canonically in millimetres and shown in mm or inches.
SSD-cache maintenance waits for user inactivity, runs at idle I/O priority and
yields cooperatively. Four-language strings and focused regressions are
included. The complete gate passes 836 tests plus security/privacy/module
checks. Runtime ZIP, developer ZIP, source archive, Local-AI bundle and RPM
were built and SHA-256 verified together with the rolling backup; `dpkg-deb`
is unavailable on this host, so no DEB was invented. Nothing was installed or
published and no live GPU, RGB, fan or snapshot write was performed.

Version .129 fixes TRCC child ownership after an OHC-controlled Levita daemon
restart. Once the original owned PID is confirmed gone, the newly observed,
exactly identified daemon replaces it in both the UI runtime and the independent
shutdown journal. Normal exit and crash cleanup therefore stop the current
OHC-owned replacement while preserving unrelated TRCC instances.

Version .128 polishes both user-approved control surfaces. Snapshot thresholds
and cleanup limits use synchronized slider/number cards; snapshot metadata can
be exported atomically and a single Snapper entry above zero can be deleted
only after explicit confirmation through the bounded helper. The GPU cockpit
uses compact live cards and wide clock tracks and moves the interactive fan
curve ahead of advanced ownership details. Both pages have real offscreen
rendering evidence. No live GPU or snapshot operation was performed.

Version .127 adds Snapshot Manager 1.0 as a configurable main page. It detects
the Linux distribution, mounted filesystems, available snapshot backends,
Snapper configurations/timers and bounded Btrfs discard state. GameMode,
Gamescope, an optional process list and KDE full-screen are preferred pause
signals; a guarded multi-core CPU-plus-GPU heuristic has hysteresis and is
limited to snapshot scheduling. Manual blocking supports one hour, a chosen
deadline or indefinitely. A fixed root-owned Polkit helper can only control two
known Snapper timers, bounded Btrfs discard limits and validated Snapper
configuration names. It cannot execute arbitrary commands, units or paths.
Four-language UI, focused policy tests and an actual offscreen rendering are
included. The complete gate passes 828 tests plus security/privacy/module
checks. Runtime ZIP, developer ZIP, source archive, Local-AI bundle and RPM
were built and SHA-256 verified; `dpkg-deb` is unavailable on this host, so no
DEB was invented. The rolling `.126`/`.127` release backups both verify. No
live snapshot, timer or filesystem write was performed and nothing was
installed or published.

Version .126 follows the approved GPU interface reference with a responsive
three-column cockpit. Overview/tuning, fan control and load-test/presentation
are visible together on wide displays and reflow on smaller viewports. The
five-point LACT fan curve is editable through exact fields and direct graph
dragging, with three conservative drafts. A prominent combined action tests
physical response and only then confirms the identical fan-only candidate;
test-only rollback and a separate post-test commit remain available. GPU and
LACT diagnostic panes now have explicit clipboard actions. The current render
is inspected offscreen and no live hardware write was performed.

Version .125 evaluates the three supplied runtime logs. Exact AMD
GPU clock readings of 0 MHz are now treated as a valid power-gated idle state,
while negative or over-limit clocks remain anomalies. Repeated identical Qt
helper-start diagnostics are coalesced for five minutes and automatic
mainboard fan writes emit one batch summary instead of one line per channel.
The Case page has a capability-aware device table and a read-only topology
summary; display/pump blocks no longer show impossible LED or PWM actions.
RGB Studio removes its redundant large preview, promotes the animated design
cards and adds six spatial designs using three original algorithms. Declared
ring paths still address every LED of every fan independently. GPU fan tests
accept an opt-in, default-off permanent LACT save after physical response is
confirmed, and only when no clock/power change is mixed in; 100% remains
exactly 100%. No live hardware write was performed. The complete suite passes
821 tests (804 sandboxed plus 17 local-socket tests); dark DE/FR case and RGB
gallery renders were inspected without clipped controls.

.124 development separates the imported case fan count from the selected LED
layout. New paths default to a row; saved rows and rings remain unchanged when
fan counts are refreshed. Ring mode keeps per-fan LED segmentation and order.
The Log page now exposes complete, RGB/fan and hardware-anomaly views backed by
separate bounded 60-minute buffers. RGB/fan diagnostics describe the exact
declared port, layout, fan count, LEDs per fan, endpoints, rotation and spatial
direction. No hardware write was performed during development.

.121 development fixes the native LED-path editor teardown crash, preserves
multi-fan topology, adds per-component animation reversal and uses one bounded
visual clock across partially configured Direct devices. The separate SDK
worker now contains render failures per device. GPU fan testing and permanent
LACT takeover are presented as two explicit actions.

.120 development: GPU Control now has device-bound subprofiles for the exact
LACT configuration, fan curve and Zero-RPM state plus stress-test duration,
resolution and presentation. A subprofile is embedded in the selected main
profile, but imported or edited payloads become non-writing drafts until they
are locally verified for the exact GPU. Optional startup activation uses the
existing LACT pending/confirm/revert path and CoolerControl ownership guard.
The stress test defaults to a maximized KDE window with the taskbar visible;
minimized and full-screen modes are persisted, while optional Gamescope keeps
the internal 4K/8K render size independent of the monitor-sized output. Users
may import transparent PNG/WebP card artwork; OHC normalizes only a private
0600 copy and never changes or deletes the source. AMD RX 9000/7000 and NVIDIA
RTX 50/40 names are presentation-only and never supply hardware limits. Two
original, unbranded family illustrations and an animated, visibility-bound fan
curve preview complete the UI. The actual Qt page now uses the rendered dark
control-deck hierarchy and keeps GPU temperature, hotspot, fan RPM and power in
four permanent live cards; the saved evidence images use the real OHC theme.
No physical GPU write was performed during
development. The complete four-language release gate passes 801 tests plus the
security/privacy/module checks. The runtime/developer archives, source archive,
Local-AI bundle and internal RPM are built with SHA-256 manifests and the
rolling external release backup; nothing is installed or published.

.119 development: The supplied session logs and local journal establish two
different failures. The GPU fan preview raised a Python `TypeError` by
intersecting a set with its change dictionary; it now compares the dictionary
keys and has a focused regression. The later Case/ARGB failure was a native
Python 3.14 SIGSEGV in a PySide signal dispatched from `QTimer::timeout`,
without a surviving Python traceback. The route dialog now owns its inventory
timer wrapper and stops/disconnects it before accepting and opening the LED
editor. Moving the live topology preview no longer discards a Qt form-row
wrapper. A private bounded ring records already-redacted log lines; only the
last five minutes are snapshotted and replayed after an abnormal exit. A
process-lifetime `faulthandler` file records all Python thread stacks on a
future fatal native signal and is archived on restart. No hardware write was
performed during development.

.118 development: The owner's complete OpenRGB video provides a visual
reference for native Serial and Runway, but the external GPU and support
strips still need a physical comparison in OHC. A ten-second, user-rated
calibration wizard now runs only with an active, explicitly paired OHC
Spinner/Comet path. It temporarily blacks out all other selected Direct
zones, compatible native OpenRGB devices and selected NZXT channels, then
restores the selected design on close. Each new candidate waits for a newly
confirmed SDK frame from both controllers before its ten-second observation
window. Paired strips use temporary blue/white; separate LED-count pixel and
fan-zone tests use white on the target and black on other selected OHC LEDs.
This uses the existing whole-device transport and never changes
power, clocks or thermal controls. Device light cannot be optically read
back, so final visual smoothness awaits the owner's confirmation.

.117 development: The owner's installed `.116` log shows normal GPU and
support effects on `device` frames. Both trial switches were then enabled;
both entered `zones`, timed out and the managed OpenRGB engine crashed.
Automatic preference rollback could not restore the crashed process. A full
OHC restart at 03:40 restored six devices and the normal write path. Both
switches and the subsequent zone-write path are removed; saved v1/v2 trial
keys are inert. The proven initial Direct preparation remains. OpenRGB's
documented device update is asynchronous while zone update is immediate,
but the precise driver failure and visible frame rate are unmeasured. The
owner recalls smoother light before the confirmed 30-LED mapping; this is a
lead for a controlled optical comparison, not evidence to alter the LED
count. No physical hardware write was made during development.

.116 development: The installed `.115` log shows the MSI controller enter
`zones` mode at 03:20:40, then SDK timeouts, a stopped OHC animation and an
unexpected managed OpenRGB-engine exit. Cause inside the OpenRGB driver is
not proven, but the new default packet choice is a regression. Both GPU and
support now default to the prior whole-device frame. The `.115` setting key
is ignored. Separate explicit tests can opt each controller into zone
packets, and an SDK failure or engine exit turns active experiments off and
records the fallback. Engine crash quarantine still requires manual restart.
The read-only Case animation remains. Physical testing of the optional paths
is still pending; no live hardware write was made during development.

.115 development: The owner's installed `.114` log and readout show about
24.5–25 successful SDK frames per second for both GPU and support, while the
GPU still looks stepped and RAM looks smooth. This excludes an obvious OHC
socket-rate stall but does not measure MSI's visible output. The mapped MSI
GPU controller now defaults to OpenRGB's documented per-zone SDK packet path
for a reversible optical comparison; the GPU dialog checkbox restores the
prior whole-device path. The serial worker, hardware ownership and validated
zone sizes remain authoritative. The selected path is logged, with no claim
of optical success before the owner's A/B test. The Case drawing animates
GPU, support and RAM during active OHC effects from declared counts and
current frame time. Without a saved physical path it uses a schematic row.
No physical RGB write was made in development.

.114 development: The owner's installed `.113` log confirms the external GPU
route on MSI JARGB 1 with 30 declared LEDs and the support on Airgoo B6 with
12 LEDs. The new phone video shows a saturated, hard-looking GPU white area
while the support fades more gently. The user had tested 50%/50% GPU edges
and 140% tempo and reports the problem at slower speeds too. OHC now offers
a separate bounded GPU white peak (65% default, 35–100% range) and raises
very dim GPU edge levels without shifting the support phase. All motion
sliders apply through the existing sole worker while a running effect is
active; Cancel restores stored values, Save persists, and Defaults is draft
until Save. During an active effect the LED rows use the same paced frame
time as the worker instead of a free-running UI clock. The Case page opens GPU setup directly, an unambiguous known
header opens its LED editor without a redundant route dialog, and each
editor names its component. Saved physical LED paths render as schematic
start/end dots on case blocks; missing paths are not guessed. Hardware frame
rate numbers and optical validation are still required before calling the
physical GPU transition fixed. No live RGB write was made in development.

.113 development: The GPU strip's default approach and fade are broadened to
40%/38%, while the support retains 32%/36%. A fixed shared open-strip cycle
prevents either strip's edge setting from shifting the other's head position.
The current build has automated rendering and transport checks; optical
matching on the owner's GPU and support still needs confirmation.

.112 development: The GPU routing dialog now draws individual LEDs for the
configured GPU and support headers, with separate draft approach/fade controls
per strip and shared speed. It shows the measured SDK transfer rates for each
controller. The pair remains tied to one motion clock, now paced by actual
frame dispatch: delayed SDK writes slow the visual progression rather than
skipping several LEDs at once. Invalid stored preferences fall back to bounded
defaults. The preview was rendered in all four languages and automated tests
cover persistence, counts, pairing and worker output. Physical optical
matching still needs a user check after installing the build.

.111 development: The owner's `.110` diagnosis showed 35% mean/39% peak
load on a 15-second 8K run. A live read-only Vulkan listing proved that
`DRI_PRIME=1` reordered the Ryzen iGPU ahead of the RX 9070 XT; OHC was
measuring the dedicated GPU while vkmark used the iGPU. The long and short
tests now select the LACT GPU by PCI vendor/device ID, and vkmark's reported
device is recorded and verified. A repeated, bounded 15-second 8K run on
the owner's RX 9070 XT produced 30/30 samples at 100% GPU busy without any
LACT configuration write. The long scene duration now extends beyond the
selected 15–120 second test. The `.110` fan log confirmed PWM 255 immediately
but only 0–50 RPM before its two-second rollback; the preview now samples
for up to 3.8 seconds within LACT's rollback window and newly claimed fan
control requires measured spin-up. No physical OHC fan write was made in
this development run. Current LACT reads show 0 MHz GPU offset, no custom
core maximum and a 330 W cap equal to the daemon-reported default; the
owner’s observed 3300 MHz peak was not caused by this benchmark changing
the tuning profile. Future test logs include clock, target, power and
throttling for diagnosis; short tests do not establish long-term stability.

After the owner's connector/power concern, GPU Control now uses LACT's
reported `cap_default` as OHC's ordinary power ceiling (330 W on this
Sapphire card). Values above that require an explicit session unlock and
remain bounded by LACT's `cap_max`; an externally active higher cap is shown
as active but never silently overwritten. The long test stops if LACT's
average power remains more than 5% above the reported default for ten
consecutive seconds without that unlock, then restores a matching OHC
snapshot where available. LACT/driver power and thermal controls remain
authoritative; OHC cannot measure the physical 12V-2x6 contact temperature
or promise hardware protection after OHC exits. No power-limit write was
performed during this development run.

The GPU/support moving-light envelope now uses a wider cubic lead and tail.
Upcoming GPU LEDs become dimly visible before the white head arrives, and the
departure fades more gradually. The paired support retains the same elapsed
clock and each header retains its configured physical LED count. Frame and
worker tests pass; optical inspection on the actual strips remains pending.

.110 development: The installed `.109` log confirms vkmark launches, but the
first long run reached only 12% GPU load and was correctly marked
inconclusive. The `.109` fan button only navigated to the Lüfter tab; a
static 100% profile set directly in LACT appears in the supplied snapshot
with 3852 RPM. OHC now offers an 8K Phong-shaded long test with a sustained
load gate, a static fan editor whose button actually invokes LACT's
bounded preview, reset actions that distinguish inputs/OHC baseline/LACT
defaults, and a per-GPU LACT diagnostic tab. Fan release reads the live
config, so a value set externally in LACT can be released without an OHC
snapshot. The diagnosis includes LACT's journal and read-only fan/RPM
samples; it cannot reconstruct every internal LACT transition. The live
`.109` LACT snapshot reported 100% static fan and 3852 RPM, but the new
OHC write and 8K paths still need owner hardware verification.

Next requested work, after GPU Control `.109` is exercised on the owner's
machine: make the Overview's upper metric cards reorderable and let users
add or remove supported data fields from a visible editor. Preserve the
current card order and visibility on upgrade, retain hardware-availability
gates, and expose a reset action. The owner also wants OHC-designed in-game
hardware overlays later; assess a MangoHud-backed, per-game configuration
path first, with Gamescope/mangoapp handled separately. This overlay is a
future feature, not part of `.109` or the immediate GPU validation.

.109 development: The owner's installed `.108` log confirms that Fedora
vkmark finished installing at 23:46 and later GPU clock-offset previews
passed at 23:48; restarting OHC is unnecessary. The longer load-test button
was still gated by an OHC snapshot, and the user had not saved a tested GPU
change. It now accepts a current-value, read-only benchmark without such a
snapshot. A test on OHC-saved values retains the matching-snapshot rollback
on a detected fault. The UI distinguishes active LACT values from unsaved
Tuning fields. The new regression uses a fake benchmark process and LACT
client and verifies that baseline testing causes no GPU config writes.

.108 development: The owner's installed `.107` log at 23:16 and 23:17 shows
that GPU tuning previews stopped before any LACT write because neither
`vkmark` nor `glmark2` was installed. The user then reinstalled LACT, which
was already present and did not fix the missing benchmark. The Tuning row
now exposes a direct `vkmark` install button, and clicking a preview with
no helper launches the existing confirmed benchmark installer. Installation
cannot apply a GPU profile or auto-start the preview. The Lasttest and
Tuning pages share completion and failure status. Regression tests cover
the no-write missing-helper path and the Fedora package check. The planned
Overview customization remains after GPU validation; the initial version
will use the already available card data rather than a large redesign.

.107 development: The supplied `.106` log confirmed that an RDNA4 offset
preview reverts automatically, but the small graphics helper barely loads
the GPU and the fan tab cannot enable a curve without a prior LACT profile.
The OHC page now constructs a validated five-point curve directly from
LACT-reported fan limits. A stronger optional vkmark scene is preferred,
with a cancellable, monitored 15–120 second test for settings already saved
by OHC. It restores the matching OHC snapshot after an observed fault.
Hardware Checker also prefers vkmark. No live GPU configuration was written,
no benchmark was launched and no package was installed during development.

.106 development: The installed `.105` log shows that GPU clock fields were
locked because LACT omits unset RDNA4 overrides from `get_gpu_config`.
The live, read-only LACT response reports an active Overdrive state, a
0 MHz GPU offset with -500…1000 MHz range, and a 1259 MHz memory maximum
with 97…1500 MHz range for the RX 9070 XT. GPU Control now derives its
editable baselines and bounds from `device_clocks_info`. No live tuning
write was made. The logout log shows successful Levita firmware release and
an obsolete recorded TRCC PID; shutdown now checks that PID directly before
classifying the result. A different daemon is never killed by this change.
The full release check passed 752 tests, security/privacy scanning and the
module registry gate. Internal RPM, runtime/developer ZIPs, source archive
and Local-AI Git bundle were built. Dist and both retained `.105`/`.106`
backup manifests, ZIP integrity and changed RPM module paths passed.
DEB was skipped because `dpkg-deb` is unavailable on this Fedora host. The
currently installed `.105` app was neither stopped nor changed by this work.

.105 local build completed: all 749 release tests plus security/privacy and
module checks passed. Internal RPM, runtime/developer ZIPs, source archive
and full-history Local-AI Git bundle were built. The ZIP CRC and new
KWin/LACT/gallery files in ZIP/RPM passed; dist and both retained external
`.104`/`.105` SHA-256 manifests passed. DEB was skipped because `dpkg-deb`
is unavailable. The installed `.104` app remains stopped after the logged
close event; this task did not restart it. No live LACT setup, GPU tuning,
boot change, reboot, KWin window move or package installation was performed.
The new X/tray behavior and real monitor placement await visual verification
after a deliberate `.105` installation.

.105 development checkpoint: The owner's `.104` startup log again reports
DP-1 as the Qt window output while the visible window appears on the left
HDMI-A-1 monitor. KDE reports DP-1 as primary. Window Placement 1.5 asks KWin
itself to verify and, if needed, move only OHC's own PID/title-matched main
window to the chosen output. A read-only live KWin script with a nonexistent
PID proved the callback and cleanup without moving a window. The owner has
enabled AMD Overdrive through LACT and plans a reboot. OHC now offers an
explicitly confirmed LACT `enable_overdrive` setup through a bounded worker,
with a restart notice and no automatic reboot. No live setup request or GPU
write was made. Hardware/visual confirmation after reboot and installation
is still pending.

The owner's live `.104` app was later found stopped. Its session log records
an explicit "Fenster schließen" click at 19:37:18 and all ordered shutdown
phases, including Levita and OpenRGB release. This task did not close it; the
log does not identify the click's source. Repeated gallery event-filter
exceptions (`KrakenControl object is not callable`) were a separate bug:
the LCD studio shadows `QWidget.window` with a host field. Version `.105`
calls the Qt method via its class for both widgets, with a regression test.
The owner then clarified that the X must never terminate OHC: it now hides
to the tray regardless of the ordinary minimize preference, or minimizes to
the taskbar when the tray is unavailable. Visible manual Quit is restricted
to the tray context menu; desktop session shutdown remains separate. The
automatic journal event cannot migrate the older explicit tray preference.

.104 local build completed: all 742 release tests and security/privacy/module
checks passed. The internal runtime/developer ZIPs, source archive,
full-history Local-AI Git bundle and RPM were built. Both ZIPs, RPM metadata
and GPU/localization package paths, the dist SHA-256 manifest, and both
external `.103`/`.104` backup manifests passed. Exactly two complete backups
remain. DEB was skipped because `dpkg-deb` is unavailable. The installed OHC
version was not changed, and no GPU tuning, kernel setting, service or fan
state was modified. The packaged checkpoint below predates this build; this
completion paragraph is authoritative.

.104 development checkpoint: The owner's `.103` log showed that the LACT
package/service started but GPU controls stayed empty. Read-only live socket
checks show two GPUs, including an RX 9070 XT; `get_gpu_config` is null on both
and `system_info.amdgpu_overdrive_enabled` is false. The GPU page now keeps
read-only measurements visible for an unsaved profile, chooses the dedicated
GPU first, explains the Overdrive gate, opens LACT for explicit setup and
explains that inactive CoolerControl is not a GPU-fan conflict. No kernel
parameter, initramfs, LACT profile, GPU clock or fan setting was changed.
All 742 release tests plus security/privacy and module-registry checks pass.
The package build and external two-version backup remain.

.103 local build completed: all 739 release tests, security/privacy checks and
module registry passed. Runtime/developer ZIPs, source archive, full-history
Local-AI Git bundle and RPM were built. ZIP CRC, the repaired LACT version
module, install helper and Wayland confirmation in ZIP/RPM, dist SHA-256
manifest and external .102/.103 backup manifests passed; exactly two complete
backups remain. DEB was skipped because `dpkg-deb` is unavailable. The
installed OHC RPM is still .102. LACT 0.10.1-1 is active/enabled and the
socket is readable; neither GPU values nor the running OHC installation was
changed. Real KWin placement awaits the owner's .103 update/start. Packaged
status text has the pre-build checkpoint below; this paragraph is final.

.103 development checkpoint: the owner's `.102` startup log says that Qt
requested and confirmed `DP-1`, while the owner observed the window on the
left display. KDE currently calls DP-1 its primary output and the stored
selection is `screen:DP-1`. On Wayland the requested global Qt geometry can
disagree with the mapped surface. The window module now prioritizes the
surface's QScreen and checks it at 350 and 1400 ms, with a bounded correction
on mismatch and both observations in the log. No live OHC restart has been
performed. The owner then reported that LACT's package was installed but the
assistant said the version was missing. Confirmed: `lact --version` fails in
0.10.1. Fedora RPM metadata reports 0.10.1; Python and shell guards now check
the installed package instead. The previously confirmed installation was
finished via Polkit: `lactd` is active/enabled, its local socket is accessible,
and read-only LACT discovery reports two GPUs. No GPU tuning was written.
The complete release gate passed 739 tests and security/privacy/module checks;
package build and external backup are pending.

.102 local build completed: all 733 release tests and the security/privacy
and module checks passed. Runtime and developer ZIPs, source archive,
full-history Local-AI Git bundle and RPM were built. ZIP CRC, modular GPU and
shutdown files in both runtime ZIP and RPM, dist SHA-256 manifest and the
external .101/.102 backup manifests passed. Exactly two complete backup
versions remain. DEB was skipped because `dpkg-deb` is unavailable. Two
hardware-free GPU-page renders were saved under
`docs/images/rendering-evidence/`. LACT remains absent on the reference
machine; no live GPU tuning, fan handoff, installation, hardware write or
GitHub action was performed. Packaged status text contains the pre-build
checkpoint below; this post-build paragraph is authoritative.

.102 development checkpoint: GPU Control 1.0 adds a LACT 0.10.1+ local-socket
page for bounded tuning/fan trials, automatic LACT rollback, explicit permanent
save and per-GPU restoration snapshots. Every GPU write rechecks CoolerControl
fan ownership; users can release LACT's GPU fan and assign it in CoolerControl.
OpenRGB-classified GPU lighting controllers, including supported MSI I²C and
ASUS SMBus models, are visible in the GPU page and open the existing RGB
Studio route without assuming an ARGB cable. The wizard offers opt-in LACT and
OpenRGB installation; Fedora LACT uses the documented COPR, Arch its package.
The lifetime observer logs incomplete exits and releases only exact owned
helpers; normal exit returns a temporarily stopped CoolerControl service.
All four UI catalogs contain 1,597 matching messages. The complete release
gate passed 733 tests and the security/privacy and module-registry checks.
Package build and external backup are pending. No LACT installation, tuning
write, live GPU lighting test or GitHub action has been performed.

.101 local build completed: all 723 release tests and security/privacy/module
checks passed. The developer/runtime ZIPs, source archive, full-history Git
bundle and RPM were built. Both ZIP CRCs, exact shutdown fix content, RPM
metadata, dist manifest and both external `.100`/`.101` SHA-256 manifests
passed; exactly two complete backups remain. DEB was skipped because
`dpkg-deb` is unavailable. The live orphaned TRCC daemon was stopped and
verified absent, while the installed OHC RPM is still `.98`; the new package
has not been installed. No public GitHub action. The packaged source snapshot
contains the pre-build paragraph below; this completion paragraph is final.

.101 live shutdown diagnosis and local fix: RPM reports installed `.98`, not
the newly built `.100`. The `.98` window Close at 16:56 entered tray mode, as
its journal records. Explicit Quit at 17:37 finished every shutdown phase,
returned from Qt and exited the OHC parent. A separate `trcc daemon` process
started at 16:45:53 in the OHC autostart unit remained at about 1.3 GiB RSS;
the earlier shutdown only ran `device disconnect`. It was stopped with the
documented `trcc kill` IPC command, and its PID was verified absent. The new
shutdown path avoids auto-spawning a daemon for release and kills only the PID
observed after OHC first started TRCC; preexisting or replaced daemons remain
untouched. 81 focused shutdown/Levita tests and all 723 release tests plus
security/privacy and module checks pass. `.101` package build pending
at this checkpoint; installed `.98` remains unchanged.

.100 local build completed: all 721 release tests and the security/privacy
and module checks passed after smoothing the compact GPU highlight. Runtime
ZIP, complete developer ZIP, source archive, complete-history Local-AI Git
bundle and RPM were built. Both ZIP CRCs, package contents, RPM metadata,
dist SHA-256 manifest and the external `.99`/`.100` backup manifests passed.
Exactly two complete backups remain. `dpkg-deb` was unavailable, so no DEB was
generated. The supplied GPU hardware launched Vulkan `vkcube` twice in short
bounded smoke checks. Full in-app PCIe observation and optical GPU animation
comparison are still pending. No installation, hardware write, GitHub push,
tag or public release was performed. Package copies retain the following
pre-build checkpoint; this completion paragraph is authoritative.

Pre-build `.100` work: the case device list and Hardware Checker now
share a clearer adaptive table presentation; full board names are measured by
content. A direct GPU click now performs its own initial inventory. The checker
detects Vulkan `vkcube` when `glmark2` is unavailable,
requires a running load helper for a definitive PCIe observation, and explains
missing helpers. Overview, cooling and recording share a compact 12-segment
temperature display based on actual Celsius readings; recording also has a
live three-source summary. The owner-supplied GPU video shows a very broad white
head over a blue 30-LED line. GPU strip sampling now keeps a visible blue body
and a narrower moving head, without changing saved LED counts or the 25-Hz
target. Five offscreen UI renders and a four-frame light preview were created;
70 focused tests pass. A full release gate passed 721 tests plus the
security/privacy and module checks; the LED gradient was softened after that
gate exposed a spatial-step regression. The fixed Vulkan command launched the local RX 9070 XT
twice for a bounded two- to three-second smoke check; the full in-app PCIe
observation and RGB optical readback remain unverified. No installation or
package build has been performed for these uncommitted changes at this
pre-build checkpoint. All temperature-focused first views use the shared
segments; unrelated menus retain their existing controls.

.99 local build completed: the owner-provided `.98` log proves the reported
taskbar close was intentionally redirected into the tray (`FENSTER
AUSGEBLENDET` plus `INFOBEREICH`), not a stuck ordered exit. Minimize-to-tray is
now a separately persisted action and every real Close runs the existing
ordered hardware return and Qt exit. Display Effects writes the same canonical
Levita startup keys as LCD Studio. Live read-only measurement found two retained
decoders for one 1600×720 video, 60 main-process threads and 713 MiB private
dirty memory. Hidden previews now unload sources and frames; an isolated
two-player check reduced 107 decoder-era threads to 3 after hiding, followed by
one debounced Python/glibc idle reclaim. Logs remain bounded and disk-persisted
and were not the memory source. All 716 release tests, security/privacy scan and
module/repository checks pass. RPM, runtime/source archives, developer package
and complete-history Local-AI Git bundle were built and verified; DEB was
correctly skipped because `dpkg-deb` is unavailable. The `.99` runtime ZIP and
RPM contain the new memory helper and decoder lifecycle. Rolling `.98`/`.99`
backups are the only retained versions and both complete SHA-256 manifests pass.
Packaged status text reflects the pre-build checkpoint; this post-build
completion is authoritative. No installation, hardware setting change, GitHub
push, tag or public release was performed.

.98 local build completed: an explicit "keep running in the tray" close choice now
sets the private `app/tray_close_confirmed` preference. Later window-manager
close events hide directly without another dialog. If that setting is absent,
Application Shutdown 1.1 migrates only a real `.97` `window-close-choice=tray`
record from the bounded private journal; the supplied 17:30:43 log and local
journal contain that exact choice, so this system will not be asked again after
the update. Explicit Quit, Cancel, disabled tray mode and session shutdown keep
their existing behavior. No new UI string, hardware write or privilege path.
All 715 release tests, the security/privacy scan and module/repository checks
pass. RPM, runtime/source archives, developer package and complete-history
Local-AI Git bundle were built and verified; DEB was correctly skipped because
`dpkg-deb` is unavailable. The runtime ZIP contains the saved-choice logic and
journal migration. Rolling `.97`/`.98` backups are the only retained versions
and both complete SHA-256 manifests pass. Packaged status text reflects the
pre-build check state; this post-build completion is authoritative. No install,
GitHub push, tag or public release was performed.

.97 local build completed: the owner-provided private shutdown journal proves that the
reported incidents were close-to-tray events, not stuck ordered-exit phases;
every subsequent explicit Quit in the inspected journal reached Qt loop return,
Python atexit and observer-confirmed parent exit. With tray continuation enabled,
every ambiguous window-manager close now asks explicitly for Quit, keep running
in the tray, or Cancel. The Quit choice enters the existing idempotent ordered
hardware hand-back immediately. Application Shutdown 1.1 adds a bounded read-only
journal interpreter and System Status displays clean/tray/cancelled/incomplete/
stuck state plus a proven unfinished phase. No forced kill, new hardware write,
preference reset or password access. All 713 release tests, the security/privacy
scan and the module/repository checks pass. RPM, runtime/source archives,
developer package and complete-history Local-AI Git bundle were built and
verified; DEB was correctly skipped because `dpkg-deb` is not installed. The
runtime ZIP and RPM both contain the new shutdown interpreter and status UI.
Rolling `.96`/`.97` backups are the only retained versions and both complete
SHA-256 manifests pass. Packaged status text reflects the pre-build check state;
this post-build completion is authoritative. No installation, GitHub push, tag
or public release was performed.

.96 local build completed: Hardware Checker 1.0 adds one-click bounded read-only CPU,
SMT, CPU virtualization, board, PCIe GPU, NVMe and memory inventory outside the GUI process. PCIe
current/max generation and lane count receive pass/warning/fail/unavailable
states. GPU idle downshifts are warnings until the explicit bounded glmark2
test; NVMe lane shortfalls remain visible without a storage write benchmark.
One fixed `pkexec dmidecode --type 17` request obtains optional RAM manufacturer,
part and configured speed while Polkit exclusively handles the password. Manual
RAM model/expected MT/s covers incomplete firmware. No clock, voltage, fan,
firmware or BIOS setting is changed. The local read-only reference probe found
Ryzen 7 9800X3D SMT active, primary Radeon PCIe 5.0 ×16 and one NVMe at ×2
against a reported ×4 maximum; this is system evidence, not a general support
claim. 1,530 atomic four-language messages. All 708 release tests and the
security/file gate passed. RPM, runtime/source archives, developer package and
Local-AI Git bundle were built; DEB was correctly skipped because `dpkg-deb` is
not installed. Rolling `.95`/`.96` backups and both SHA-256 manifests passed.
No installation, GitHub push, tag or public release was performed.



.95 local build completed: Display Effects 1.11 removes permanent cold band borders and
idle centre highlights, with continuous proportional glow. Eight original
loops are regenerated from actual 4800×2160 frames to native 1600×720, H.264
CRF 10, 24 FPS, four seconds, bounded two-thread encoding. The old tool asked
for 3200×1440 but the renderer clamped to 1920×1080 and distorted aspect ratio.
LCD 1.7 `media_preview.py` owns selected local video decoding without hover
and a separate pending/confirmed composition copy. Only a successful apply
confirms it; browsing, failed applies and effect exploration cannot replace it.
Shared LCD Media Manager 1.0 `preview_visibility.py` / `video_preview.py`
clip both preview decoders to all enclosing scroll viewports and window state.
Transient effect selection clears on outside click, Escape, the clear button
or page hide. No choice falls back to the last confirmed media/layers; an active
catalog effect is mirrored by exact path. Disable apply/staging without an
actual effect choice. Firmware hand-off clears the local active snapshot.
Null/repeated motion/background frames no longer rebuild draggable scenes;
galleries reserve final row height before bounded card insertion and measure
actual viewport width. Live category/variant/details track the current design.
1,483 atomic four-language messages, reusing existing Clear selection caption.
73 focused tests passed after language-detail corrections. DE/FR live effect
previews rendered and reviewed; all eight videos passed complete FFmpeg decode,
native geometry/FPS/duration checks. Full UI coverage passed; a late tab callback
was additionally found during destruction and is now context-bound/deleted-host
guarded, with a real Qt regression. Synthetic engine tests explicitly clear
external ownership state; preview paths normalize to decoder source identity.
All 701 release tests and the full four-language UI/security/privacy/module
checks passed. RPM/runtime/developer/source archives and full-history Git
bundle built. Both ZIP CRCs, 233 current Python sources and all 16 regenerated
band videos/posters in both ZIPs/source/RPM verified; only four standard RPM
shebang adaptations. RPM digests/metadata and complete-history bundle passed.
Dist and external .94/.95 SHA256 manifests passed. Exactly two complete
backups remain; .93 rotated under standing owner approval. DEB unavailable
(dpkg-deb missing). This completion is recorded after packaging; archived docs
retain the pre-build check status. No physical display readback/optical soak.
The supplied .94 log confirms continuous video startup and quintic paired GPU
plans, but contains no measurable LCD-Quantum geometry or hardware fault.
No installation or live hardware action.

.94 local build completed: PC Case Profiles 1.5 adapts the right inspector to 430–860 px,
with the same live component/fan and LED-path widgets in columns or tabs, no
inner scroll area and an always reachable Save/Cancel footer. Preserve drafts,
last tab, cancel/outside/Escape/hide and asynchronous generation guards. UI
Performance 1.1 tracks late tab titles for live language changes. RGB Studio
1.15 widens spinner/comet fronts and tails with quintic blending and a shared
virtual sampling footprint for paired GPU/support strips. Physical LED counts,
paths, directions, settings and sole-writer transport are unchanged. Shared
elapsed time already existed; do not introduce another clock or connection.
Owner .93 logs show GPU 30 and support B6 12 (B7 fan bank 24). The new request
mentions support 24; retain saved/personal counts pending clarification and test
both 30/12 and 30/24. .93 LCD logs show accepted default and video sends without
an LCD failure; they do not establish continuous hardware duration.
1,483 atomic language messages. 54 focused tests passed, including ten new
GPU gradient/worker/pair regressions and real four-language case geometry at
1600×1000, 1200×800 and wide LED paths at 2000×1000. Extended GPU route/PWM form
coverage passed. DE/FR wide/narrow forms and LED paths rendered and reviewed.
All 697 release tests and full four-language UI/security/privacy/module checks
passed.
RPM/runtime/developer/source archives and complete-history Git bundle built.
Both ZIP CRCs, all 230 current Python sources in both ZIPs/source/RPM, RPM
metadata/digests and bundle verified. Dist and both external .93/.94 SHA256
manifests passed. Exactly two complete backups remain; .92 rotated under
standing owner approval. DEB unavailable (dpkg-deb missing). This post-build
completion is recorded after packaging; archived docs retain pre-build status.
No installation, live hardware writes or physical optical/LCD soak test.


.93 local build completed with one explicit saved Levita default. Automatic profile startup
cannot replace a saved (including disabled/missing) default; explicit profile
loads still replace the shared default with complete FPS/motion persistence.
Preview/effect browsing cannot mutate startup or profile staging. Explicit
save/apply invalidates delayed startup retries. Immutable accepted command
intent and prepared assets are replayed on daemon recovery, independent of
preview. Cache identity includes effective config and source assets.
LCD Runtime 1.1 adds measured stable-video tolerance with 3-GiB emergency,
actual low available-memory and sustained-growth guards; apply transactions
are not interrupted by memory polling. Owner .92 log proves the 17:29:58
1138-MiB limit restart; it does not prove a native crash or physical duration.
1,482 atomic languages. All 686 release tests and four-language full UI,
security/privacy/module checks passed; 13 new regressions cover persistence,
recovery/retry intent, cache identity and memory protection. RPM/runtime/developer/source archives and
complete-history Git bundle built. Both ZIP CRCs, all 229 current Python
sources in both ZIPs/source/RPM, RPM digests/metadata and Git bundle verified.
Dist and both external .92/.93 SHA256 manifests passed; exactly two complete
backups remain and .91 rotated under standing owner approval. No DEB toolchain.
Post-build completion recorded here; packaged docs retain pre-build status.
No live hardware action or installation.

.92 local build completed: LCD Runtime 1.0 observes acknowledged successful CLI sends,
uses the same IPC ticker for static media and bounds startup/commands (45 s)
and missing established send progress (15 s). Process Runtime 1.1 diagnoses
sensor exceptions/invalid IPC and SDK readiness/frame stalls (5 s), with bounded
1/2/4-s recovery. Private module-events.jsonl retains PID/exit/request/runtime/
reason/stderr/traceback and retry decisions, integrated in explicit diagnostics.
Read-only process/GameMode probes run outside Qt with current-intent guards.
System Status exposes transfer age and manual read-only sensor recovery.
1,481 atomic language messages. All 17 new fault-injection tests and the final
673-test release gate passed, including four-language UI/security/privacy/module
checks. DE/FR System Status rendered and reviewed.
Local .92 RPM/runtime/developer/source archives and complete-history Git bundle
are built and verified. Both ZIP CRCs, all 227 current Python sources in ZIPs,
source archive and RPM passed (four standard RPM shebang adjustments); corrected
ZIP folder examples are included. RPM digests/metadata, bundle and Dist/.91/.92
SHA256 passed. Exactly two complete external backups .91/.92 remain; .90 rotated
under standing approval. No DEB (dpkg-deb unavailable). This completion record
was added after packaging; archived notes retain the pre-build status. Supplied .91 log shows two successful animated starts and
tray operation, no crash, but less than five minutes cannot prove permanence.
No installation/live hardware write or public action. Autonomous core/cooling
remain hardware-validated future stages.

.91 in development: first staged read-only Process Runtime 1.0 supplies bounded
fresh sensor snapshots to GUI/cooling/history/LCD profile metrics, supervises
three retries with backoff, and fails unavailable on stale data. RGB Studio 1.14
serializes existing pure render parameters to the existing sole-writer SDK
worker; authorization, rates and physical GPU/support paths stay unchanged.
PC Case Profiles 1.4 uses shared render/hit geometry for single-click side labels.
Application Shutdown 1.1 durably journals requests/phases/Qt return, has one
delayed private stack dump and a non-signalling parent-starttime observer bounded
to 90 seconds; remaining owned QProcesses stop after hardware restoration.
Explicit quit requests Qt exit directly rather than relying on another event
turn. In-page health shows actual per-process CPU/RSS (not unique-memory totals).
1,476 atomic messages. The repeated build gate passed all 656 tests, including
four-language full UI, security/privacy and module budgets. Both ZIP CRCs and
all 218 current Python sources match ZIP/source/RPM contents (four standard RPM
shebang adjustments); RPM header/payload digests/metadata, complete-history
bundle and Dist/.90/.91 SHA256 checks passed. DE/FR health renders reviewed.
Exactly two complete backups .90/.91 remain; .89 rotated under standing approval.
No DEB: dpkg-deb unavailable. Post-build completion is recorded here; packaged
notes retain the pre-build status. No installation/live hardware write/firmware
or public-release action. Autonomous cooling/core service
and further LCD migration remain subsequent hardware-validated stages. Latest
.90 owner log ends before exit and cannot establish which exit phase hangs.

Version 3.4.29.90 development: bounded GUI-thread LCD card portions, three-second
input-idle preparation without hidden playback or thumbnail workers, reuse on
resize and late/live text tracking. A right-side embedded inspector owns case
component/ARGB/path/test/GPU/PWM property forms; cancel/outside/hide invalidates
async inspection, pending physical tests retain their guarded restoration.
Precautionary RAM reclaims lease only selected RAM away from the existing SDK
frame, drain the last affected frame and retain other assignments/elapsed clocks.
Persist master startup intent separately from acquired cooling control; fresh
ownership checks precede dashboard/lower-master activation, confirmation remains
mandatory. Explicit tray exit is idempotent and queues Qt exit after isolated
cleanup, preserving cooling startup intent. Transition overlays only cover the
left navigation; finished animations are deleted. 1,467 atomic messages.
The complete 621-test gate passed, including four-language UI, security/privacy
and module checks. Seven RAM-isolation tests also passed after adding the final
in-flight drain regression. DE/FR inline editor renders were visually reviewed;
the hardware-free full Qt event loop exits and stops its own cache worker.
The repeated build gate passed all 622 tests. Local RPM/runtime/developer/source
archives and the complete-history Git bundle are built. All 208 current Python
sources match both ZIPs, the source archive and the RPM (four standard executable
shebangs normalized by rpmbuild); ZIP CRCs, RPM header/payload digests and metadata,
bundle verification and Dist/.89/.90 SHA256 checks passed. Exactly two complete
external backups remain; .88 was rotated under standing owner approval.
DEB was not built because dpkg-deb is unavailable. Package snapshots contain the
pre-build verification status; this post-build completion record lives here.
The supplied .89 logs show five-second whole-stream RAM retries at two pauses;
19:05:39 proves six-channel master activation and later quiet preset persistence.
They contain no shutdown or physical FPS evidence. No live hardware/backend/
firmware action or installation performed.

Version 3.4.29.89 adds smoother open-strip GPU spinner/comet heads with
count-aware speed, wider smooth fronts/tails and bounded temporal/area sampling.
GPU Support Sync uses the explicitly assigned support header and exactly one
selected, conflict-free GPU route; share config/clock/normalized progress, not
LED counts, PWM or write authority. Optional GPU-setup checkbox persists only
on commit and travels in complete packages. Missing/ambiguous/blocked/ring
partners stay separate. Other zones, native GPU modes, true physical pixel tests
and the 25-Hz transport remain unchanged. 1,448 atomic language messages;
105 targeted regression tests and the complete 597-test gate passed, including
the real four-language UI, security/privacy scan and module budgets. GPU dialog
DE/FR surfaces rendered and visually reviewed. The repeated build gate passed
all 597 tests. Local .89 RPM/runtime/developer/source/Git-bundle packaging is
complete. RPM digests/metadata and 44 current sources (only the usual entrypoint
shebang normalized), both ZIP CRCs/44 exact sources and source archive passed.
Git bundle records complete history. Dist and retained .88/.89 SHA256 manifests
passed; exactly two complete private backups remain. .87 was pruned under
standing approval after .89 completed. DEB unavailable because dpkg-deb is absent.
Completion recorded after artifact verification; no installation, live hardware,
firmware/backend change or publication.
The supplied .88
log confirms JARGB 1 = 30, B6 = 12 and comet at 83%, but contains no physical
FPS readback and does not prove the source of every observed optical stutter.

Version 3.4.29.88 completes reversed physical fan-ring chain order in RGB
Studio 1.11, independently of ring rotation, while retaining legacy mappings,
real test numbering and existing transport authority. Complete profile packages
preserve the optional bounded declaration. Imports reject unsupported asset
types and file/directory collisions before staging. Shutdown quiesces timers/
restart intent before owned worker cancellation. All four languages updated
atomically (1,446 messages). All 104 targeted tests and the full 555-test gate,
real four-language UI build, security/privacy scan and module budgets passed.
LED editor DE/FR surfaces rendered and visually reviewed. Repeated build gate
passed all 555 tests. Local .88 RPM/runtime/developer/source/Git-bundle
packaging completed; RPM digest/metadata checks and 42 current source digests
(only entrypoint shebang normalized by rpmbuild), ZIP CRC/42 exact sources and
source archive checks passed. Bundle has complete history. Dist and retained
.87/.88 SHA256 manifests passed; exactly two complete backups remain, .86
pruned under standing approval after the new set completed. DEB unavailable
because dpkg-deb is absent. Completion recorded after artifact verification;
no installation, live hardware operation, firmware/backend update or publishing.

Version 3.4.29.87 adds Profile Bundle 1.0: complete private typed settings/
profile ZIP plus associated LCD/media/theme/font files, strict hashes/paths,
background worker, relocated nested paths and confirmed startup-only restore
with rollback and hardware automation/calibration fail-closed. Legacy JSON
exchange remains. RGB Studio 1.10 adds separate physical strip/ring paths,
preview of actual LED numbering and eight case-space travel directions without
new transport or guessed topology. 1,442 atomic language entries. Narrow
roundtrip/path/render/editor and real full-UI snapshot coverage passed (43).
Complete 546-test gate, four-language real UI build, security/privacy and
module budgets passed. New full Profiles and DE/FR LED editor surfaces
rendered and visually reviewed. Repeated build gate passed all 546 tests;
local .87 RPM/runtime/developer/source/Git-bundle packaging completed.
RPM digests/metadata and exact 34 source hashes passed; runtime/developer ZIP
CRC plus 33 exact current source files and source archive checks passed.
Dist and retained .86/.87 SHA256 manifests passed. Exactly two complete
versions remain; .85 was pruned under standing approval. DEB unavailable
because dpkg-deb is absent. Completion recorded after verification; no
installation, backend/firmware update, live hardware write or publishing.

Development after the packaged .86 baseline: RGB Studio 1.9 implements the
owner's revised personal wiring (front A1 2×8, bottom B7 3×8, rear B8 1×8,
Thermalright radiator A8 3×10, support B6 1×12). One-time settings migration
preserves geometry/PWM and unrelated zones; existing complete buffers are
pinned independently from designs. Remove the recurring B6 default override.
A bounded reusable custom fan library exposes saved manufacturers/models in
block and zone editors; Thermalright ten-LED radiator reference is personal,
not universal electrical detection. New save caption is complete in all four
languages (1,395 entries). Final targeted suite: 83 passed; full gate: all 516
tests, real four-language UI construction, security/privacy and module budgets
passed. New model editor screenshots were reviewed in German and French.
No new package, installed-settings edit or real hardware write performed.

Version 3.4.29.86 implements Application Shutdown 1.0 and RGB Studio 1.8.
EOF-first fan-helper exit and isolated cleanup passed the initial 474-test gate.
Further changes retain offline wiring choices with real ownership guards,
explicit owned-engine restart with stale generation/busy invalidation, live
route-selector refresh, and preview-depth suspension of inventory/auto-apply.
This prevents automatic reapplication of old zone sizes during pixel tests.
Completed preview close/save restores the unchanged selected design once only
with enabled writes and available owned engine. Overlapping/failed/offline tests
fail closed; automatic native crash loops remain blocked.
Fan block editors offer brand/model/black-white/LED declarations and dynamic
count suggestions through existing SDK bounds. Personal ASIN B0CN39T7QN uses
owner-observed eight addressable LEDs, two fans = 16; other headers/GPU/PWM are
not bulk migrated. 1,394 complete four-language entries. Latest narrow suite:
99 passed before the final suggestion/bounds cases. The repeated build gate
passed all 500 tests, complete DE/EN/ES/FR UI build, security/privacy and module
budgets. Four-language fan/routing screenshots, full case and transfer surfaces
rendered; DE fan and FR route layouts visually verified. Local .86 RPM/runtime/
developer/source/Git-bundle packaging completed. RPM digests/metadata and exact
current module payload hashes, runtime/developer ZIP and source archive source
checks passed. Dist plus retained .85/.86 SHA256 manifests passed. The .84
packaged backup was pruned under standing approval; exactly two complete
versions remain. DEB unavailable because dpkg-deb is absent. Completion recorded
after verification; no installation or real hardware compatibility claim.
Owner deprioritized duplicate-display redesign. Research found AG-DRGB16
stuttering report #4970 and an older simultaneous resize/update crash #681
(closed as fixed in 2024); neither proves this native crash or defective
hardware. Official Airgoo guide names OpenRGB rc3; no driver update, live
hardware test, settings edit, installation or publishing was performed.

Version 3.4.29.85 fixes direct ARGB setup for unassigned case blocks in RGB
Studio 1.7. The block action now selects a currently reported Direct controller
and header, then exposes existing bounded LED-count/pixel testing. Explicit
stable bindings persist in their own bounded settings map across restart and
design/position snapshots; PWM and groups remain independent. Missing ports
never reroute; GPU blocks keep the existing GPU-route authority. No physical
LED count or connector is guessed and no new hardware transport is introduced.
New regression tests cover all reported headers, cancellation, rebinding,
unassignment, stale inventory, persistence and complete DE/EN/ES/FR captions.
All 442 tests, complete hardware-free DE/EN/ES/FR UI build, release/version/
module-budget and privacy/security gates passed. Four-language route-dialog
screenshots and full case/transfer surfaces rendered; DE/FR selection layouts
visually verified. Local .85 RPM/runtime/developer/source/Git-bundle packaging
completed after the repeated 442-test gate. RPM digests, metadata, payload
version and exact routing source passed; runtime ZIP current modules/source
verified. Dist and both retained .84/.85 SHA256 manifests passed. The old .83
packaged backup was permanently pruned under standing approval; exactly two
complete versions remain. No live hardware/settings edits, installation, tag
or publishing. DEB unavailable because dpkg-deb is not installed. Completion
recorded after artifact verification.

Version 3.4.29.84 implements PC Case Profiles 1.2 and RGB Studio 1.6:
bounded visual-only component resizing, proportional fitted geometry and
original 2.5-D depth; explicit case-family mounting arrangements without
resetting saved coordinates; shared or independent cooling scale; normal
editing of blocks without RGB devices; physical SYS_FAN connector captions
with unchanged driver identity in details; default all-writable RGB selection
and an explicit persisted checkable individual-device list. DE/EN/ES/FR have
1,390 shared entries. All 415 tests, the complete hardware-free offscreen
DE/EN/ES/FR build, release/module/version and security/privacy checks passed.
Real Qt screenshots and all 30 vector case illustrations were rendered.
Three-line side callouts show configured LEDs and physical SYS_FAN connectors;
unknown values remain —, without guessing electrical topology. Local RPM
packaging completed after the repeated 415-test release gate. No live settings or
hardware were modified. The existing sole-writer,
LED counts, physical fan sizes, PWM calibration and ownership stay unchanged.
The complete .84 RPM/runtime/developer/source/Git-bundle set was built; RPM
digests, metadata and payload version/current modules passed. Dist and both
retained .83/.84 SHA256 manifests passed. The .82 packaged backup was
permanently pruned under the owner's standing rule; exactly .83/.84 remain.
No installation, tag or push occurred. DEB was not generated because dpkg-deb
is unavailable. This completion note was recorded after artifact verification.

Version 3.4.29.83 adds PC Case Profiles 1.1 and RGB Studio 1.5: central Case navigation, direct LED/PWM editing and a shared topology table; optional independent cooling positions only; 30 detailed original case illustrations; generic reported Direct-header pixel testing, protected manual counts and semantic ARGB diagnostics. Every configured zone renders independently, with bounded count-adaptive sampling and soft spinner/comet/colour/sparkle transitions. The existing sole-writer queue, ownership guards and 25-Hz transport target are unchanged. DE/EN/ES/FR contain 1,387 shared entries. All 394 tests, complete hardware-free offscreen DE/EN/ES/FR localization, release/version/module-budget and security/privacy checks passed. Real Qt screenshots and all 30 case illustrations were rendered; collision-free personal-layout callouts have a regression test. The owner visually verified the personal Sapphire NITRO+ strip as 30 LEDs on MSI JARGB 1; the newly smoothed animation still needs optical verification.

The owner authorized local .83 RPM packaging and permanently approved routine older release-backup rotation without repeated questions on 13 September 2026. Create the complete new set first and retain the two newest complete semantic versions, .82/.83; .81 may be pruned automatically. The standing exception is recorded in the backup policy, agent instructions and decisions and covers only recognized packaged releases in the fixed external backup directory, never unrelated data or fewer than two retained complete sets. Check both SHA256 manifests after each build. Installed settings and the running application remain untouched; installation, tags and publishing require separate requests.

Packaging completed: local 3.4.29.83 INTERN RPM, runtime/developer ZIPs, source archive and Local-AI Git bundle built successfully. RPM metadata/payload version and digests passed; dist and both retained .82/.83 SHA256 manifests passed. The .81 packaged backup was permanently pruned; exactly .82/.83 remain. No DEB was generated because dpkg-deb is unavailable; no installation, tag or push occurred. This completion note was recorded after artifact verification.

Version 3.4.29.82 was locally packaged after 374 passing tests and explicit approval to prune .80, retaining .81/.82. It introduced controller-and-zone GPU routing, manual count retention and a pixel test. At that release the owner’s 80/90 values were unverified declarations; the subsequent owner test establishes 30 only for their personal setup.

Version 3.4.29.80 turns the NCT6687/DKMS/MOK flow into a status-gated wizard and accepts the observed affirmative `already enrolled` result even when `mokutil` also returns a kernel-keyring error. Case-fan cards now separate friendly System Fan names from their technical `PWM N` channel, all chassis assignments can be reset without deleting curves, and the wizard can immediately continue with the next fan. Thermalright Levita hides unavailable coolant status and curve sources; its safe PWM-floor text occupies a dedicated readable warning panel. PC-view component double-click selects the assigned device and opens the existing Direct-mode zone editor where supported; the supplied Sapphire remains honestly limited to OpenRGB's one logical LED and native hardware mode. The same log proves the tray symbol was operational despite an invalid Qt rectangle, so KDE/Wayland StatusNotifier visibility—not geometry—now controls close-to-tray. DE/EN/ES/FR remain complete at 1,365 shared message entries.

Version 3.4.29.79 adds application-wide optional fade, slide and glow transitions that paint only a short-lived overlay and stop outside the visible page. A central user-selectable 0/0.5/1/2/4-GiB SSD cache accelerates Levita and Wallpaper catalogs plus scaled previews; a low-priority worker removes the oldest regenerable entries without modifying source media or active hardware files. ENE-DRAM recovery waits until rapid navigation is idle. The localized Wallpaper setup now checks and, after confirmation, installs free KDE/Qt D-Bus helpers from configured repositories before the separate SHA256-verified CaptSilver plugin flow. The case-fan automatic-control button stays synchronized with the real persisted controller state and is fully blue only while active. A localized NCT6687 assistant now separates driver setup, DKMS key generation, fixed MOK import, physical UEFI enrollment and post-restart loading; OHC never receives the password, disables Secure Boot or reboots automatically. The supplied log proved that a transiently invalid tray geometry previously selected orderly hardware exit even though the process survived; close-to-tray now visibly minimizes in that case and keeps LCD/RGB/cooling running, while explicit exit always completes cleanup and quits. The 48×42-pixel close target reaches the top-right corner without resize-edge interception. The compatibility baseline remains TRCC Linux 9.9.12, OpenLinkHub 0.9.1, liquidctl 1.16.0, OpenRGB 1.0-rc3.1 with SDK 5, Qt/PySide 6.11.2 and Pillow 12.3.0. DE/EN/ES/FR remain complete at 1,353 shared message IDs.

Version 3.4.29.76 diagnoses the supplied five-hour-plus Levita freeze from the complete session and kernel logs. At 11:36:54 the TRCC daemon was OOM-killed after growing to about 15.5 GB RSS; its replacement held the USB interface while the existing ticker had lost IPC, so bounded ticker-only retries could not recover. OHC samples only the exact current-user `trcc daemon` process once per minute and, at 1 GiB RSS or an explicit lost-daemon stream error, stops the ticker, closes the daemon through its own IPC command and reapplies the selected design through the existing sole-writer queue. A five-minute cooldown prevents loops. Visible logs are 60-minute ring buffers with hard bounds; full current/previous session logs remain, and redacted errors additionally rotate in private `errors.log`.

Version 3.4.29.75 removes the subsequent size oscillation proven by the supplied 3.4.29.74 trace: the intentional normal mapping is now guarded from the old state-restore timer, startup profiles do not apply stored window presentation, and their duplicate full placement call is gone. The LCD and Display Effects galleries now reflow from their actual viewport width. LCD Media Manager 1.0 stores several folders, individual media, exclusions and aliases without altering sources; external TRCC IDs receive readable category labels. Temperature History 1.2 adds local dates, resizable split views and an explicit selected-range CSV/JSON manager over all already recorded read-only sensors. DE/EN/ES/FR contain 1,291 shared message IDs. Hardware ownership and the sole TRCC writer remain unchanged.

Version 3.4.29.74 fixed the remaining KDE/Wayland multi-monitor startup race exposed by the supplied 3.4.29.73 log and local KWin output configuration. The log proved that OHC requested `DP-1` at 3440×1440 and calculated a geometry inside its work area, while KWin could still remap a synchronously maximized top-level window according to the Discover launch context. OHC maps a normal window on the selected target, maximizes only in the next Qt cycle and checks the screen actually observed after 350 ms. Only a mismatch triggers a bounded reposition; diagnostics record target, observed screen and final geometry. Tray activation follows the same show-then-place-confirm order.

Version 3.4.29.73 makes the cooler-original-display action model-aware. On Thermalright Levita it stops OHC streaming, releases the sole TRCC daemon owner and lets the cooler firmware redraw its built-in display; on NZXT Kraken the existing liquid-temperature command remains unchanged. The same Thermalright action is prominent on the LCD page and available under Display Effects. Test mode performs no USB write, an already-detached daemon is accepted idempotently and saved startup profiles remain untouched. Explicit tray Quit now bypasses close-to-tray and completes through the existing cleanup path on the first click. All eight original OHC Light Bands are rendered from 3200×1440 supersampled frames and delivered at native 1600×720 with higher-quality encoding. DE/EN/ES/FR contain 1,277 shared message IDs.

Version 3.4.29.72 moves the four original Spectrum Ring, Neon Double Arc, Prism Segments and Aurora Radar motions exclusively into editable Layer 2. Each uses an original glow/particle animation with an on/off control; a selected Layer-1 background is composed locally into one cached stream beneath the live data, so the existing TRCC daemon remains the sole USB owner. Preview FPS and physical LCD FPS are separate. The display stays at the conservative 15-FPS default; 60 FPS appears only after an explicit experimental opt-in in Settings and has bounded automatic fallback. Automatic game mode uses Feral GameMode, Gamescope or an explicit process allow-list, with a manual override and no load heuristic or generic Wayland window inspection. The main window now restores its real normal/maximized state without a visible size jump, and resize cursors are cleared on every exit/state path. DE/EN/ES/FR contain 1,268 shared message IDs.

The supplied latest log shows successful theme staging and no TRCC/USB transport failure. It also confirmed the obsolete automatic Layer-1 Spectrum selection; that coupling and its catalog card are removed in this version.

Version 3.4.29.71 turns the Display Effects Layer-1 catalog into a graphical card gallery while retaining category and colour filtering plus direct creator, source and license links. A new original 1600×720 OHC Spectrum Ring loop rotates eight coloured segments and automatically pairs with its editable live-data Layer-2 layout; original OHC layouts receive consistent DejaVu typography and compact glass clock frames. Settings now exposes both the moving primary choice and fixed connector choices for every screen, and maximized KWin windows are placed normally on the requested output before being re-maximized. The owner's local cyber media were renamed descriptively and the two lower-quality corridor encodes were moved to a recoverable archive outside the scanned library. Hardware selection remains write-free, profile update remains required, and DE/EN/ES/FR contain 1,250 shared message IDs.

Version 3.4.29.70 raises the Levita data-surface module to 1.6. It adds four original colourful telemetry layouts—Spectrum Ring, Neon Double Arc, Prism Segments and Aurora Radar—without carrying over a manufacturer logo, cooler outline or reference-video frame. The editor supports up to twelve independently removable custom text elements with content, locally installed Qt font, size, colour, visibility and free position. A fixed 880×396 preview viewport preserves the exact 1600:720 aspect ratio when tool panels are opened, closed, switched or scrolled. Fonts and text are staged into a private validated native theme and still use the sole TRCC queue; no second USB owner or cooling write path is introduced. DE/EN/ES/FR remain complete with 1,226 shared message IDs.

Version 3.4.29.69 adds synchronized browser-like tabs to both LCD child pages while preserving the expandable sidebar. Display Effects 1.7 recognizes an active bundled effect by its exact validated path and selects the matching type, category, design and variant. It also adds the original OHC Light Ribbons design: eight reproducibly rendered seamless 1600×720 directions based only on the observed travelling-light concept, with no copied video, cooler geometry or product logo. Programmatic synchronization blocks selection signals, so opening the page neither restages a profile nor writes hardware. Section Tabs 1.0 establishes the reusable pattern for future child pages; DE/EN/ES/FR remain complete with 1,220 shared message IDs.

Version 3.4.29.68 makes the detailed recorder unmistakably reachable: Cooling now expands in the main sidebar into `Control & profiles` and `Temperature recording`, matching the existing LCD child navigation. Sidebar children and the internal view remain synchronized in both directions and survive navigation reset/customization. The supplied log and installed-package query confirmed that 3.4.29.67 was running and that this was a discoverability problem, not a sensor or hardware failure. No cooling, sampling or hardware-write path changed.

Version 3.4.29.67 keeps the compact overview graph and adds a dedicated Cooling temperature recorder for grouped CPU, GPU/hotspot/VRAM, RAM, SSD/NVMe, motherboard, VRM, PCH and other plausible read-only Linux-hwmon sources. It provides per-series selection, hover timestamps and current/minimum/maximum statistics for up to the in-memory session limit. A new model-aware safety policy enforces conservative Levita floors of 50% pump and 25% radiator duty because Thermalright publishes only maximum RPM. The profile table no longer collapses after update; selection, detailed stored content and arbitrary section combinations are supported. Sensor reads remain non-owning and compatible with separate Open Radeon Control Center development.

Version 3.4.29.62 extends Display Effects 1.6 with fifteen individually attributed, silent 1600×720 space, landscape and water videos. Every selected excerpt was reviewed without visible people; rejected Saturn-tech, artificial 3D galaxy fly-through and Grand Canyon people clips are absent. Four local category filters keep the now 35 media variants manageable. Levita Studio additionally bundles five editable Layer-2 themes derived from named CC0 Kenney components and four original OHC themes; every theme keeps live CPU/GPU/RAM/clock blocks and the right notch-safe area. Selection, preview, profile-start staging and the sole TRCC writer retain their existing safety boundaries and do not use runtime networking.

Version 3.4.29.60 fixes the confirmed KDE/Wayland floating-window restore regression. The supplied trace showed the maximized `3440×1394` work area being retained at desktop origin `1920,0`; OHC now stores a separate bounded normal rectangle, rejects work-area-sized restore candidates, clamps all edges and adapts minimum dimensions to small logical HiDPI areas. A 60–95% windowed-size preference and `Ctrl+Alt+0` rescue are available. RGB Studio's PC view follows the approved two-column concept, removes the personal Amazon action, retains manufacturer sources and renders original OHC silhouette families with AIO/air visualization, airflow reversal and fan-block splitting. Devices and Effects migrates once to collapsed. No hardware write path changed.

Version 3.4.29.59 implements the approved compact application shell. LCD owns the Display & Layout and Display Effects child pages and collapses when another area is selected. A custom accessible title bar delegates movement and edge resizing to Qt's compositor APIs on Wayland/X11 while retaining the existing tray-aware close path. RGB Studio opens with four suggestions, adds four original presets, persistent favorites and a grouped full library, and keeps device/group/detail panels compact by default. PC Case Profiles 1.0 supplies 30 original schematic starting layouts, the exact Thermaltake Retro 360 TG reference layout and local user-created profiles. No manufacturer artwork or new hardware write path is added.

Version 3.4.29.57 fixes the confirmed long-running Levita video freeze from the supplied trace. The daemon IPC `display play` ticker ended unexpectedly at 19:28:55 and OHC previously left the design as a still frame. Levita runtime module 1.5 now restarts only that non-owning ticker with bounded 1/2/4-second backoff, renews the budget after a stable run and stops after three rapid failures. The last shortened, privacy-filtered backend output is retained for diagnosis. USB reconnect, the sole TRCC hardware owner, the ten-second apply cooldown and shutdown restoration are unchanged.

Version 3.4.29.56 expands Display Effects 1.2 with five freely licensed, edited 1600x720 source designs and four locally bundled colour variants per design. Main design and colour are separate choices; creator, original source and license remain visible as clickable links. Runtime use is offline and applying still delegates to the existing Levita studio and sole TRCC owner. The supplied window trace also exposed an unrelated diagnostics defect: native surface summaries returned no text because their return block was unreachable. The summary is restored and covered by regression testing; the logged QColorDialog itself was the expected colour picker, not a fault.

Version 3.4.29.55 makes the main window responsive before device discovery, dependency helper execution or Levita library card construction can delay first paint. The new Responsive Startup 1.0 module runs CoolerControl ownership detection in a coalesced bounded subprocess and stays fail-closed until a result is known. Display Effects now presents Layer-2 sensor layouts as the same graphical preview cards used by LCD Studio, places effect type at the top of Effect settings, uses faster compatible H.264 encoding and skips redundant gallery rebuilding for cached effects. The ten-second Levita hardware cooldown and all existing ownership/reconnect safeguards remain unchanged.

Version 3.4.29.54 adds a separate Levita Display Effects page with a procedural, configurable smoke loop and a large live preview that retains the selected layer-2 sensor layout. Rendering is bounded and offscreen; applying hands the generated H.264 media to the existing Levita studio, which remains the sole TRCC/hardware writer. The same release completes dynamic DE/EN/ES/FR translation of navigation, page headers, fan cards and About content, activates an existing window on a second launch, and suppresses desktop startup feedback only for tray autostart. OpenLinkHub can now check the fixed official GitHub release endpoint and, after explicit confirmation, update an existing RPM/DEB package through configured repositories or a strictly detected user-space service through a published-SHA-256 archive, retained backup and automatic rollback. Its bundled Web UI updates with the package. The reference installation remains untouched at 0.9.0 until the user confirms the offered 0.9.1 update.

Version 3.4.29.53 fixes Levita shutdown at the ownership boundary. Stopping video alone kept OHC's generated cache theme active inside the TRCC daemon, whose live renderer could continue refreshing the same visible frame. A real application exit, tray Quit, logout or handled shutdown now stops local clients and issues one bounded daemon `device disconnect`, allowing the panel firmware's documented built-in Thermalright screen to return after roughly two to three seconds without frames. A separate pipe-bound guard is armed only after a confirmed real Levita write and repeats that fixed release once if the OHC parent disappears unexpectedly; a clean confirmed restore cancels it. Preview-only use never arms the guard. The existing Kraken order remains stream-stop followed by synchronous liquid-temperature restore, with its persistent unclean-session recovery marker unchanged.

Version 3.4.29.52 moves the complete localization inventory into the versioned `src/modules/localization/v1_0/` module. German, English, Spanish and French each own one data file containing UI, setup-assistant and help text. Every language uses the same stable message IDs; a small assembler rejects duplicate German source strings and missing or extra IDs before exposing the existing catalog API. The former root catalog is now only a compatibility facade. Installer and release packages carry the module through the standard `src/modules/` path.

Version 3.4.29.51 repairs language switching across the fully constructed UI. Atomic German/English/Spanish/French control catalogs now cover every translation-required interactive caption found by the offscreen build; dynamic gallery file types, counts and colour labels are translated without changing their data values. Prominent page and status explanations were expanded as well. Every future visible UI change must update all four languages in the same change, and `tests/test_full_ui_build_34291.py` enforces that contract.

Version 3.4.29.50 synchronizes the top and saved cooling profiles with chassis-fan profiles. **Leistung** is a constant 100-percent override for pump, radiator and calibrated, individually enabled chassis-fan channels and is evaluated immediately when OHC control is active. Every chassis-fan card exposes the bounded, confirmed 0-percent/10-second identification test and restores the previous hwmon/firmware state afterwards. The reference NCT6687 driver exposes `pwm1` through `pwm8` but no `pwmN_mode`; OHC now explains that electrical PWM/DC remains configured in BIOS instead of implying a missing app feature. Drivers that do expose `pwmN_mode` retain the warning, automation stop and mandatory recalibration. Hardware ownership, CoolerControl conflict protection, watchdog and firmware return are unchanged.

The same internal version adds three project-owned seamless Levita 3D loops at the physical 1600×720 resolution: Orbital Ring, Neon Apex and Quantum Core. They are silent H.264 videos generated from repository-owned Blender geometry with no manufacturer models, logos or stock media, and are exposed through the existing explicit built-in-media allowlist.

Version 3.4.29.49 is an internal UI follow-up: Overview „Status & Hinweise“ follows confirmed Levita PWM tests (green **OK** after pump and radiator confirmation, red **Fehlerhaft** while tests are open or sensors fail) in the same row layout as „Erkannte Hardware“. RGB Studio expands „Geräte und Effekte“ and the native hardware-channel list as in-page panels; the channel list stays visible when leaving the page. Hardware write paths are unchanged.

Version 3.4.29.48 makes the repository layout a permanent owner decision: `docs/ai/AGENTS.md` carries the mandatory placement table and README rules, mirrored in the Cursor rule `70-repository-layout.mdc`, the Copilot and Claude instructions and `DECISIONS.md`; `tests/test_repository_layout_342947.py` enforces the root allowlist, the 200-line README limit and the four-entry history. The release workflow reads `packaging/VERSION`/`packaging/BUILD_CHANNEL`; tag `v3.4.29.47` has no published release.

Version 3.4.29.47 completes the repository reorganisation: all application code (`*.py`, `assets/`, `modules/`, `test-gifs/`) lives in `src/`, which mirrors the flat installed application directory; `install.sh`, `uninstall.sh`, `VERSION` and `BUILD_CHANNEL` live in `packaging/`; `INSTALL.md`, `CHANGELOG.md` and `README.en.md` in `docs/`; the full agent instructions in `docs/ai/AGENTS.md` (the root `AGENTS.md` is a short pointer); `SECURITY.md` in `.github/`. Installed layouts and package contents are unchanged. Tests import from `ROOT / "src"`, the registry validator scans `src/modules/`, and `install.sh` resolves `src/` from both the ZIP root and `packaging/`.

Version 3.4.29.46 stops the minutely `openrgb --client --list-devices` background inventory while the main window is hidden in the system tray and no RGB startup profile, write enable or scheduled retry is pending; the guard is covered by `tests/test_rgb_inventory_tray_guard_342946.py`. The repository was reorganised into `docs/project`, `docs/ai`, `docs/hardware`, `docs/security`, `docs/releases`, `packaging/` and `.github/`; `install.sh` and `scripts/build_release.py` still install a flat application directory, and `app_constants.helper_script_path` resolves helper scripts in both layouts. The README gained a clickable seven-screenshot gallery, installation near the top and a four-version history.

Version 3.4.29.45 keeps a saved RGB start profile pending while the managed OpenRGB engine reports its known cold-start partial inventory. The bounded inventory retry can now discover the complete controller set and apply the saved design instead of losing the one-shot profile start. The module-registry validator also follows the declared `packaging/BUILD_CHANNEL`, removing the internal-only gate that previously rejected a valid stable candidate. Stable RPM source preparation now uses a dedicated temporary parent instead of colliding with the identically named runtime ZIP tree. The bundled Levita gallery adds eight owner-created AI backgrounds and one deduplicated 30-second owner-created animation through an explicit allowlist; no manufacturer/TRCC catalog media is present. The clean-runner preview-queue regression cancels and clears constructor thumbnail work before measuring its synthetic 140-video load, removing the final runner-speed race. This version promotes the tested 3.4.29 feature line to the stable release channel.

Version 3.4.29.42 advances the Wallpaper Engine for KDE module to 1.2. Pause, resume, next and mute target `/WallpaperEngine` on Plasma's existing `org.kde.plasmashell` bus service, matching the object exposed by CaptSilver v1.4 even when its optional standalone alias cannot be registered. Because v1.4's advertised Previous method currently advances instead, OHC's back button safely selects the preceding validated local Workshop entry. The page also reads and applies DisplayMode 0/1/2 per selected screen. The main window defaults to Qt's primary screen, persists an optional exact screen name with primary fallback, and repositions restored geometry before display where the compositor permits it. A global eight-pixel scrollbar style makes all pages consistent. Existing hardware ownership and Wallpaper/Steam immutability boundaries are unchanged. The complete two-version backup remains mandatory.

## Current objective

Continue Open Hardware Control as a modular Linux hardware-control application while preserving the mature NZXT Kraken path and expanding validated integrations without introducing competing hardware writers.

Version 3.4.29.42 keeps the guided setup and optional verified Fedora installer from 3.4.29.41. It never modifies Steam Workshop files or an installed CaptSilver plugin in place, rejects selecting the Steam library itself as the recursive personal-video folder and never handles administrator credentials. Playback and scaling remain explicit user actions delegated to the plugin through Plasma.

The theme-matched client-side main-window title bar is active since 3.4.29.59. It uses Qt system move/resize rather than manual global geometry, preserves maximize/restore and the tray-aware close path, and has dedicated offscreen edge, full-UI and autostart guards. Native KWin decoration is intentionally disabled only for the OHC main window; dialogs keep their platform decoration.

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
- Main GUI and orchestration: `src/kraken_control.py`, `src/cooling_widgets.py`, `src/ui_layout.py`; localization: `src/modules/localization/v1_0/` with the `src/localization_catalog.py` compatibility facade.
- Shared application infrastructure: `src/app_constants.py`, `src/temperature_utils.py`, `src/privacy_logging.py`, `src/window_diagnostics.py`, `src/command_backend.py`.
- Hardware request coordination: `src/hardware_request_coordinator.py`, `src/cooling_ownership.py`.
- Mainboard fan control: `src/mainboard_fan_control.py`, `src/ohc_fan_helper.py` plus Polkit policy.
- Thermalright display/cooling: `src/modules/lcd_levita/v1_7/`, `src/modules/levita_daemon_health/v1_1/`, `src/modules/levita_performance/v1_1/`, `src/thermalright_display.py`, `src/thermalright_display_ui.py`, `src/thermalright_cooling.py`.
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

## Before finishing 3.4.29.103 INTERN

- Keep `BUILD_CHANNEL=INTERN`; do not run GitHub push, tag or public release scripts.
- Run all release checks.
- Verify current documentation/version references.
- Confirm no secrets/personal logs are present.
- Complete the local package build and the two-version external backup.
- Require an explicit project-owner request before any GitHub push/tag/release.
