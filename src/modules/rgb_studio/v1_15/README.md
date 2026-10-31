# RGB Studio 1.15

Ubuntu's trusted OpenRGB 1.0 CLI uses `--list-detailed`: its plain
`--list-devices` now reports names only. Older explicit/distro executables and
Fedora retain their existing command. Runtime inventory rejects any entry
missing the mandatory detailed `Type` field before stable IDs, selection,
routes or profile-start actions can change. SDK6 read-only descriptors retain
real LED/zone counts; a names-only list never means a zero-LED controller.

External-only GPU components use the existing settings-only block-route editor
when no native OpenRGB GPU controller is present. Controller selection and
reported header names remain explicit; a cooler drawing never implies wiring.
Saved GPU block routes (including retained exact routes for an absent native
GPU ID) participate in per-zone GPU rendering and support synchronization only
while their real Direct source is selected and conflict-free. Header counts
remain unchanged, no dummy GPU is added, and the Ubuntu-disabled native Sapphire
detector is never re-enabled by this path. Component buttons retain their own
slot ID even if a different component is selected elsewhere.

`startup_status.py` provides the prominent profile/automation/reclaim summary
without granting hardware ownership. `openrgb_profiles.py` validates and copies
user-supplied legacy `.orp` or v6 JSON profiles into OHC's private library;
opaque legacy profiles are never presented as safely device-filterable.

`sdk_v6.py` validates the documented SDK6 controller-ID, ACK and callback
envelopes. Ubuntu explicitly allows SDK6 and maps OHC inventory indices to
the server's uint32 IDs; the default cap stays at SDK5 for Fedora. New zone
modes, names, segment matrices and flags are parsed within the existing
packet/count bounds. Non-Direct zone overrides, rejected ACKs, malformed or
unknown packets, excessive callbacks and changed inventories fail closed.
SDK6 writes require an ACK in addition to initial mode/color readback. Cached
frames consume callbacks instead of letting them accumulate; an inventory
change invalidates the worker until OHC restarts it after fresh discovery.
No ACK or server color readback proves that physical LEDs visibly worked.
The published contract was checked against the official
[SDK documentation](https://gitlab.com/CalcProgrammer1/OpenRGB/-/raw/master/Documentation/OpenRGBSDK.md)
and [protocol header](https://gitlab.com/CalcProgrammer1/OpenRGB/-/raw/master/NetworkProtocol.h)
on 2026-10-06. No live controller scan or write is part of the fixture tests.

Version 3.4.29.130 uses compact cards and up to six columns on a wide viewport.
Every gallery/category switch synchronizes the RGB navigation state. The
spatial action opens the Case editor, where direction and speed are saved with
the real per-header LED/fan order. Changing global travel direction updates
declared paths only and never creates a controller route or LED count.

The studio now opens with the animated design gallery instead of a second,
redundant large live-preview panel. Larger gradient cards carry category,
selection and active state. Six Spatial presets use the new `converge`,
`crossflow` and `depthwave` algorithms; saved case direction and physical
strip/ring coordinates project them across the case. A ring still maps every
physical LED inside each fan segment and preserves fan order and rotation.

Version 3.4.29.118 adds `gpu_motion_wizard.py` for a temporary paired
GPU/support visual test. It requires an already running OHC Spinner or Comet
on both explicitly saved ARGB ports. `render_plan.py` blackens all other
selected Direct zones within the existing whole-device frame; compatible
selected native OpenRGB and NZXT lights are switched off during the test.
Each bounded candidate waits for newly confirmed frames from both controllers
and then runs for ten seconds before the user can accept or request a slower,
broader GPU edge. Cancel restores the prior draft; close requests the selected
design again when OHC still owns the RGB engine. Hardware light remains
optically unreadable, so device confirmation remains a user judgment.
The paired preview uses temporary blue and white. Header pixel and fan-zone
tests light the selected pixel/zone white while other selected OHC LEDs go
dark. `HeaderPreview` requests the prior design even after a failed test if
the RGB engine and hardware ownership are still healthy.

Version 3.4.29.117 removes both per-frame zone-packet trials and their
dialog controls. The owner's `.116` log shows they timed out and crashed the
managed OpenRGB engine; a full OHC restart restored the ordinary device
path. Old trial settings are inert. Running effects send whole-device
packets after the existing one-time Direct setup. Confirmed physical LED
counts, GPU/support motion parameters and read-only Case preview remain.

Version 3.4.29.116 restores whole-device packets as the GPU and support
default after the owner's `.115` log showed timeouts and an OpenRGB engine
exit. The old trial key is ignored. Independent, unchecked trials allow the
identified MSI GPU and Airgoo support to compare zone packets; the host
disables a failing trial and logs component, path and fallback. An engine
crash still requires manual restart. No SDK acknowledgement proves visible
LED delivery.

Version 3.4.29.115 adds a reversible MSI Mystic Light GPU transport comparison.
After the full Direct setup frame, the existing single OpenRGB SDK worker can
send validated zone updates on that explicitly selected GPU controller. The
GPU dialog can disable the trial and restore whole-device updates. Other
controllers, including the Airgoo support, keep their prior packet path.
The log reports packet path changes and socket acknowledgement; neither
proves that the physical LEDs displayed every intermediate frame.

Version 3.4.29.114 uses a transient GPU/support motion draft while a design
is active. Sliders feed the existing sole SDK worker without saving; closing
the editor restores persisted values, and Save commits them. Defaults resets
the draft. A bounded GPU white peak and a lifted dim-edge curve reduce
saturation and make intermediate LED levels visible earlier. The support
keeps its former brightness curve and shared motion phase. A GPU render error
is reported rather than quietly substituting the generic sharp effect.
Optical confirmation and measured controller rates remain necessary.

Version 3.4.29.112 adds `gpu_motion.py` for strict saved per-strip edge bounds,
shared tempo and a
paced shared visual clock. `gpu_motion_editor.py` previews the two actual
configured LED rows and measured SDK acknowledgement rates in the existing
GPU dialog. The editor is draft-only until that dialog saves. `render_plan.py`
ships the same timestamp and tuning to the sole SDK worker for both strips;
cancel never touches the hardware or saved settings. Slow transfers lower
visual motion speed rather than skipping physical LEDs. Optical frame delivery
remains unobservable from OHC.
Version 3.4.29.113: `strip_clock()` keeps the shared travel cycle fixed when either strip's lead
or tail changes, preserving the other strip's phase.

The owner's 19 September GPU video shows a broad white moving region over a
blue 30-LED strip. Sampling now keeps the blue body lit and narrows the moving
white head for this open-strip effect. The connected header's saved count,
direction, pairing, 25-Hz transport target and sole writer remain unchanged.

Moving open GPU/support strips use broader cubic fronts/tails in
`gpu_strip_sampling.py`. Pairing shares the existing elapsed clock, virtual
count and spatial footprint; each header retains its actual LED count. Fixed
25-Hz target and 3×4 samples, no extra connection or resize. Regression tests
cover 30/24 and 30/12, gradient width/steps, early pixel glow, SDK-worker
equivalence and settings. The brighter low-intensity approach and afterglow
soften transitions between adjacent GPU LEDs without changing paired timing.


`render_plan.py` separates pure host-side plan construction from SDK-worker
effect calculation. Counts/shape/config/time/mappings are bounded; existing GPU
pairing, physical paths and elapsed math remain identical. The GUI authorizes
each frame and retains one in-flight request; the worker does not autonomously
acquire devices. No extra USB writer, new rate or automatic native restart.

Version 1.13 adds identity-scoped `stream_reclaim.py` leases for precautionary
RAM retries. Only selected ENE RAM stable IDs leave the existing SDK frame;
other zones retain the same timer, assignments and elapsed effect clock.
After native commands settle, the same lease is released and RAM Direct readiness
is invalidated. Stop/reset/shutdown invalidate the lease rather than resurrecting
old intent. Cold initial and manual reclaim retain their ordered whole-stream
policy; no additional transport, hardware detection or write authority is added.

Version 1.12 adds pure `gpu_strip_sampling.py`: continuous signed-distance
open-strip heads for explicitly routed GPU spinner/comet effects. Count-aware
rate, wider smooth head/tail and bounded 3×4 temporal/area samples fade at the
ends instead of wrapping the last LED onto the first. Other zones stay legacy.
`gpu_support_sync.py` pairs exactly one selected, conflict-free routed GPU
with an explicitly wired `gpu-support` block, using bounded declared counts.
The optional default-on setting shares GPU config and normalized strip progress
with its support, never LED sizes, PWM, selection or write authority. Ambiguous/
missing/blocked/ring partners stay unpaired. GPU setup saves the checkbox only
on commit; complete packages retain it. Start diagnostics report real per-header
counts, the shared clock count, kernel widths and software rate, not optical FPS.
The existing 25-Hz sole-writer transport and real single-pixel tests are unchanged.

Version 1.11 adds explicit reversed fan-ring chain order. Physical LED 1 may
start in the bottom/right fan while per-ring start and clockwise order remain
independent. Existing paths retain the original top/left order. The bounded
optional boolean persists in existing settings and complete profile packages;
preview, all spatial effect samplers and semantic save logs use the same map.
Neither count, physical test index nor transport changes automatically.

Version 1.10 adds declared physical LED geometry in `led_topology.py`, bounded
independent settings and case-position adaptation in `led_topology_store.py`,
and a strip/ring preview in `led_topology_editor.py`. The header editor shares
actual count/index controls with a separate LED-path tab. Start/end, ring count
and clockwise order are explicit declarations, not electrical detection.
Eight spatial travel directions project the physical path into existing case
blocks, preserving the single-writer transport and independent zone lengths.
Unmapped paths and local direction preserve legacy frames exactly. Invalid
changed ring counts fall back locally, never resize hardware automatically.
Physical test numbering remains unchanged; full Profile Bundle 1.0 includes
these settings, while design changes do not overwrite them.

Version 1.9 adds `fan_library.py`: bounded reusable custom manufacturer/model/
black-white/LED declarations selectable in block and zone editors. Saving a
model is settings-only. Thermalright Levita reference radiator fans have ten
owner-observed addressable LEDs, not a universal manufacturer specification.
`personal_wiring.py` applies the owner's five corrected Airgoo assignments once
only to the personal Thermalright layout and uniquely reported AG-DRGB16 ports.
It preserves positions, scale, PWM state and unrelated zones; complete existing
zone buffers receive separate manual pins. Partial buffers are not zero-filled.
B6 is twelve LEDs, not the older 24-LED reference. Later manual choices win;
inventory refresh no longer continuously forces B6 to a default count.

Version 1.8 separates offline settings-only wiring from actual write ownership.
The open route selector follows inventory changes and offers explicit recovery.
`engine_recovery.py` invalidates stale discovery/busy state and restarts only an
owned engine; automatic crash loops remain blocked. `header_preview.py` pauses
inventory and auto-apply during preview, then restores the unchanged selected
design once after closing/saving and successful pending test completion. It
never enables writes, replaces newer intent or runs across foreign ownership,
crash quarantine or shutdown. Tests are non-overlapping and fail closed offline.
`fan_profiles.py` stores bounded independent physical model declarations;
`fan_profile_editor.py` offers editable brand/model, black/white and per-fan LEDs.
The personal ASIN reference's owner-observed eight addressable LEDs do not
overwrite other headers or constitute manufacturer-wide electrical detection.
Optional count suggestions use existing SDK bounds and serial write paths.

Version 1.7 adds direct controller/reported-zone selection from any case block
in `slot_route_editor.py`. `slot_routes.py` owns bounded settings-only stable
bindings, independent of PWM, positions, groups and design snapshots. Missing
controllers/ports never fall back to another header. Explicit unassignment
suppresses legacy hints; cancellation changes nothing. Counts and single-pixel
testing delegate to the existing bounded SDK editor and serial sole-writer
queue. GPU blocks use existing GPU routing authority, not a competing map.
An unassigned block no longer stops at an error or recursively opens itself.
All captions reuse complete stable DE/EN/ES/FR entries.

Version 1.6 adds `selection.py`: default all writable devices, explicit
persisted individual mode and checkable inventory rows in the visible list.
Locked/read-only devices never join default selection. A deliberate deselection,
group/slot subset or clear action opts into individual mode; selecting a tile
in default mode retains all writable devices. New full profiles serialize the
mode; old profiles retain the current mode. Selection alone adds no hardware
write or transport path. The device identification test remains single-device.

Version 1.5 generalizes bounded header editing/pixel testing to every reported
Direct ARGB zone. `argb_controls.py` connects central Case and block editors;
`argb_store.py` pins explicit manual counts independently of design profiles;
`argb_diagnostics.py` logs counts, bounds, offsets and SDK completion only on
configuration/test/start events, never physical readback or every frame.
`effect_sampling.py` supplies Qt-free bounded count-aware area sampling and
soft motion envelopes. Every configured zone renders independently, preserving
GPU overrides. Lazy public exports avoid import cycles and keep pure renderer
imports Qt-free. The serial sole-writer transport and 25-Hz target are unchanged;
the full-width transfer panel shows measured SDK throughput, not physical FPS.

Version 1.4 adds explicit controller-and-zone GPU routing and independent strip
coordinates in `gpu_routing.py`. `gpu_lighting.py` owns setup, profile retention
and the one-time owner-confirmed personal JARGB 1 migration. `gpu_led_editor.py`
reads real SDK bounds and changes only the chosen header's count; its explicit
single-pixel test uses the existing serial command queue, temporarily blacks
other controller zones and requires reapplying the design. No physical GPU LED
count is guessed. Current cabling/counts take precedence over design snapshots.
Legacy controller-only routes remain readable without inventing a header;
unrelated layouts receive no automatic mapping. Native effects remain default.

Version 1.2 adds four-item suggestions, persistent card favorites, a grouped
all-design view and compact-by-default device/effect panels. Four new original
OHC presets extend the gallery without changing existing saved indices.

`ene_start_recovery.py` owns the bounded delayed ENE-DRAM cold-start policy.
It coordinates only existing public controller operations and performs no raw
SMBus or USB access. The host remains responsible for OpenRGB ownership,
device classification and applying the current design.

`design_gallery.py` owns the hardware-independent Qt gallery for built-in RGB
designs, including left-click selection and right-click color-edit requests.
It keeps title/category/star fonts independent for every card, elides long
titles and paints only cards intersecting Qt's exposed viewport. The host
updates gallery animation only while the RGB page is visible.

`studio_panels.py` owns the in-page expand/collapse of „Geräte und Effekte“ and
the native hardware-channel list. The host still composes the surrounding RGB
page and must not open extra windows for these panels.

The host orchestrator keeps a saved profile start pending while OpenRGB's first
cold-start inventory is intentionally treated as incomplete. The existing
bounded inventory retry must either provide writable devices and continue the
profile or release the already-acquired RGB session without an unbounded loop.

`.156` keeps fresh optional LED-path drafts editable even after Qt polish,
inline reparenting and parent re-enabling. Genuine combo/button/units gestures
activate saving; opening, count-only/test-index changes and programmatic restore
do not create a path. Explicit unchecking still removes the path on Save.
Both the worker plan and legacy GPU fallback provide rectangles for per-header
spatial directions in global-local mode. Spatial wave travel keeps its original
forward phase; rainbow alone needs phase inversion. Local effect reversal is
independent of physical numbering. Without a declared path legacy frames remain
local, and no hardware, route, count or detector setting is inferred.
