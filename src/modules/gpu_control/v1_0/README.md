# GPU Control 1.0

`.153` uses `cockpit_ui.py` for composition, `read_worker.py` for Qt-free bounded read-only LACT requests,
`read_probe.py` for a cancellable QProcess/deadline and `read_ui.py` for validated
stale-result-safe presentation. Ubuntu uses this path; Fedora keeps the prior
read contract. Optional clocks-table errors do not block stats. Ownership
probes are asynchronous, and the restored power confirmation is explicit and
inline. Feature/owner gates also protect direct profile/reset/fan actions.

Fan cards no longer impose a fixed height on translated text. Narrow cockpit
columns stack their workflow and control cards, retain the entire caption in
an accessible clickable wrapped checkbox, and permit vertical scrolling only
when needed. No control or safety note is removed to fit a viewport.

Version 3.4.29.130 keeps both page scrollbars disabled and fits the complete
wide cockpit through compact cards/actions. Custom artwork import/reset is
available beside the GPU image. `preview_requires_graphics_load()` makes the
test split explicit: fan-only candidates use the reversible LACT physical fan
test and never resolve or launch vkmark/glmark2; clock or power changes retain
the guarded load path.

This module reads GPU information from LACT's local Unix socket. Its primary
controls form a responsive three-column cockpit matching the approved visual
reference: overview/tuning, fan workflow and load-test/presentation reflow from
three to two to one column. Compact live cards and synchronized wide
slider/number tracks expose power and clock values without changing the
underlying LACT limits. It can trial
bounded GPU tuning, a validated five-point fan curve or a static fan speed.
LACT reverts unconfirmed
changes, and OHC explicitly verifies baseline restoration before offering a
separate permanent save. The five-point curve supports exact fields, direct
handle dragging and three conservative drafts. The fan page additionally
offers a prominent test-and-apply action plus a default-off option
to commit automatically only after that physical response test passes and only
when the draft contains fan changes, not clocks or power. Static 100% remains
an exact LACT `1.0`; a failed or inconclusive test never commits.
Only LACT 0.10.1 or newer may receive writes.
`version.py` verifies the installed distribution package: LACT 0.10.1 has no
`lact --version` command.
LACT may return a null GPU config before the first override is stored; the
client treats that as an empty profile so read-only metrics remain available.
The page selects a dedicated GPU first and queries LACT's reported AMD
Overdrive state. RDNA4 clock controls use LACT's live `device_clocks_info`
baselines and bounds even if the saved profile has not recorded those fields.
The direct core maximum stays disabled when LACT reports no such range.
Tuning stays locked until Overdrive is enabled. The LACT GUI button lets the user perform that explicit setup. Alternatively,
the user can confirm LACT's own `enable_overdrive` command in OHC. A bounded
child process waits for LACT to prepare its boot setting and initramfs, then
OHC requests a separate manual restart. Opening the page never invokes it;
OHC does not write boot files or reboot the machine itself.

`ownership.py` checks that CoolerControl has no GPU fan assignment before
LACT takes the device. Users may explicitly release LACT's fan channel and
assign the GPU back in CoolerControl. The original LACT configuration is
stored per GPU in QSettings for explicit restoration after an app restart.
`reset_ui.py` handles read-only input discard and an expressly confirmed
reset of the selected active LACT GPU profile. `diagnostics_ui.py` records
OHC actions and measurements, reads bounded lactd journal output without
privilege escalation, and exports a private local report on request.
`stress.py` and `stress_ui.py` offer 4K/8K vkmark and reject low-load runs
as inconclusive. Maximized-with-taskbar is the default; minimized and full
screen are profile values. When Gamescope is available it preserves the
selected internal render size while fitting output to the current monitor.
The short-lived KWin bridge addresses only the benchmark PID. OHC fan writes
await hardware verification.

`profile_ui.py` embeds exact-device profiles from `gpu_profiles/v1_0` without
bypassing the existing test/commit guards. `visuals.py` paints a read-only,
visibility-bound fan and curve preview. Generated neutral family artwork and
user-owned transparent images are presentation only; they never select
hardware limits.

The long and short GPU benchmarks select the LACT GPU by PCI vendor/device
instead of a `DRI_PRIME` ordinal. The long test records vkmark's reported
device, clocks, power and throttling; its scene outlasts the chosen test
duration. A bounded 15-second live run on the reference RX 9070 XT produced
30/30 readings at 100% busy. `power_policy.py` and `power_ui.py` keep OHC's
normal power ceiling at LACT's device-reported default. An explicit unlock
is required to edit up to LACT's maximum. An un-unlocked long run stops after
ten consecutive average-power readings above 105% of default, restoring a
matching OHC snapshot if one exists. `tables.py` owns the bounded read-only
metrics/hardware tables. LACT remains the sole GPU writer. OHC cannot measure
the physical 12V-2x6 connector temperature.

`installer.py` and `packaging/install-lact.sh` offer an opt-in Fedora COPR or
Arch package installation. Other distributions link to LACT's official
package instructions. An installed package whose first service start failed
can be finished without re-enabling the COPR. No package is installed when a
page merely opens.
