# PC case profiles 1.5

The GPU route action also works for a declared external-only GPU component with
empty device IDs. It opens the existing reported Direct-controller/header
selector, persists the block route in the PC hardware snapshot, and leaves LED
counts, geometry and native GPU detection unchanged. The case's read-only GPU
preview uses the same explicitly routed block group as the existing full-device
render plan; selected source and conflict guards still apply.

`spatial_layout.py` stores user-measured direct distance or depth between two
existing component IDs. Millimetres are the canonical unit; the editor defaults
to mm and converts to/from inches using exactly 25.4 mm per inch. Invalid,
stale, duplicate or self-referential links fail closed. `diagram.py` draws
these declared relationships in the original OHC case view. The same panel
links to the existing physical LED/fan-order editor and exposes case travel
direction and RGB speed. These settings never infer dimensions, route RGB or
write PWM.

The central Case page now summarizes mapped PWM channels, routed ARGB headers
and saved LED paths without probing or writing hardware. Its device table shows
construction, lighting and cooling only when the block can actually support
them: display/pump-head components do not expose meaningless LED/PWM actions,
while fan banks retain direct header and PWM assignment entry points.

Version 3.4.29.115 adds `case_animation.py`, a read-only GPU/support/RAM LED
color projection. The visible Case diagram animates dots on declared paths;
components without a saved physical path use clearly schematic positions.
The refresh timer stops when the page is hidden. Preview colors do not
confirm physical output and never send a hardware command.

Version 3.4.29.114 adds a direct GPU control button on the Case page and
GPU/support component forms. A known single ARGB header opens its LED editor
directly; a separate route button remains for changing controllers or ports.
Forms show the component name. `topology_labels.py` supplies saved,
unambiguous LED paths to `diagram.py`, which draws schematic LED route dots
and start/end markers. An undeclared physical direction is never inferred.

`editor_sections.py` keeps the same live form widgets in side-by-side columns
or tabs according to viewport width, preserving draft values and the last tab.
Component/fan and inline LED-path forms use these sections. The inspector
adapts 430–860 px to the left, has no inner scroll area and brings its footer
into the case viewport. Domain validation/commit/cancel and async guards stay
in their existing dialogs. No mapping or physical write follows resizing.


`diagram.py` shares label placement with hit-testing at every viewport size.
Single-click side labels focus and open existing inline properties without
starting drag/reorder or committing positions. Component double-click remains.

`inline_editor.py` owns one right-side inspector. Component, reported ARGB
route/count/path/test, GPU route and PWM mapping forms are embedded Qt widgets,
not KDE/modal windows. Combo selections and incidental outside clicks keep the
draft open; Save, Cancel, Escape and explicit close are the only completion
paths. Only Save commits. Async inspect results carry a generation token, and pending
pixel tests retain their existing guarded restoration even after the form closes.
`component_editor.py` extracts construction/commit from the root orchestrator.
While editing, the profile panel yields its space to the inspector; geometry,
saved positions, independent count/PWM and existing sole-writer guards remain.

`workspace.py` and `case_page.py` own the central Case page after Overview,
direct LED/PWM block actions and a shared topology table. The device list uses
content-sized identity columns and the shared diagnostic table style, without
changing slot selection or assignment behavior. `view_state.py` persists
optional independent cooling positions and visual scale; physical RGB/LED/PWM
mapping stays shared. PWM assignment uses reported chassis channels and the
existing controller without calibrating/enabling/writing them. Version
3.4.29.152 also exposes reported CPU_FAN and PUMP_FAN connectors for radiator
and pump slots, confirms conflicting replacements and synchronizes every
settings-only mapping into the selected local PC profile. Calibration,
activation and ownership boundaries remain unchanged.
Version 3.4.29.153 persists explicit pump/radiator roles as validated
`hardware.aio_channels`, including deliberate empty values. Moving or replacing
a connector clears its former AIO role before the confirmed new assignment.
Current profiles restore only known channel IDs; legacy profiles recover roles
only from their own unambiguous pump and `radiator-top` slot mappings. Loading
a different or empty profile never retains a foreign AIO role. First-run
suggestions wait for an inventory and never refill a user-cleared choice.

Contains a hardware-independent catalog of 30 selectable case templates,
model-specific original vector fronts, chassis materials, motherboard tray,
PSU shroud, framed fans, GPU/RAM/AIO details and bounded two-line labels.
Saved normalized positions remain unchanged. Rendering and hit targets share
proportional fitted geometry in `case_geometry.py`. Explicit arrangement uses
case-family mounting centers; Retro front mounts sit below the drive fascia.
`resize_interaction.py` previews corner drags and commits once on release,
with Escape/hide cancellation. Scale is bounded 25–200%, independent from
count, physical millimeters, RGB wiring and PWM. Old profiles default to 100%.
`depth_renderer.py` adds original projected 2.5-D edges and component shadows.
`channel_labels.py` displays the reported SYS_FAN connector; technical driver
identity remains in tooltips. Unassigned RGB blocks open their normal editor.
`topology_labels.py` supplies configured per-zone LED counts and physical fan
connectors for three-line side callouts. Unknown remains —, never electrical
detection; explicit header hints narrow display only, not hardware routing.
Renderer parameters are artistic proportions, not mechanical specifications.
Manufacturer images are reference-only and are never downloaded or bundled.

Also contains original OHC silhouette families and safe serialization for
user-created PC layout profiles including their AIO/air-cooling presentation.
`profiles.py` additionally validates a settings-only hardware snapshot with
stable ARGB controller/header routes, fan and LED counts, manual headers, LED
paths, case devices/RAM, GPU routes and known PWM slot assignments. Loading the
snapshot never writes hardware and missing identifiers never select a fallback.
Owner-observed personal fan defaults are resolved before saving, and a
multi-device RAM block is never narrowed by an obsolete route to one DIMM.
On the matching MSI MAG X870 TOMAHAWK WIFI, the owner-confirmed reference PWM
layout is migrated once using exact driver-reported connector labels. Existing
assignments win and no numeric pwm index is guessed.

`controller.py` is the host mixin for building the compact selectors, applying
schematic slots, opening assigned RGB devices, and coordinating chassis-fan
slot selection. It also owns the safe assignment reset and the wizard handoff
to the next unassigned fan while leaving reusable curves intact.

The Thermaltake Retro 360 TG entry follows Thermaltake's official manual and is
the exact built-in default. The UI links only the selected manufacturer's
source, not the owner's private purchase link. Other entries are explicitly
presented as editable schematic starting layouts; OHC does not bundle
manufacturer artwork or claim millimetre-accurate geometry for them. Fan blocks
can be reversed, split into individually draggable fans and saved locally.

Double-clicking a component opens its inline properties, including explicit
reported route selection and real zone/LED configuration.
Devices without Direct Mode stay limited to the backend-reported hardware modes
and topology; the layout never invents additional addressable LEDs.

`.156` retains editable LED drafts through Qt polish/reparenting. Flow controls
keep unfinished choices on ordinary refresh and reflect changed saved profile
direction; an explicit missing-path status avoids claiming inferred geometry.
`fan_preview.py` draws bounded schematic light-ring segments from the confirmed
effect frame. A single configured header can preview colours without an exact
physical ring path; ambiguous headers remain unresolved. Saved physical paths
refine the view without changing routing/counts. Case rectangles are cached per
controller during spec creation, not re-queried each frame. Visible active RGB
uses a 40-ms timer; hidden views stop. This is not a rotor/RPM simulation.


The .172 workspace reuses all stores and animated diagrams in three tabs. `component_summary.py` edits declared fan count/LED drafts only on Save. `inline_editor.py` sizes for its natural form/footer and reveals Overview before embedding forms. Original profile controls remain in a disclosure.

.176 assistant channel changes cancel active identification before switching;
continuation skips explicitly disconnected ports and completes when none remain.
Stored connection flags retain curves; only explicit successful calibration
restores a connected state. Layout/profile ownership remains unchanged.
