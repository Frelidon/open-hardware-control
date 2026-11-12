# UI redesign — owner review, 12.11.26

## Current implementation .181 — installed and verified locally

The owner approves continuing the UI redesign in bounded steps while preserving
saved profiles, native RGB/LCD animation, animated application backgrounds,
light/dark palettes and hardware ownership. Local orderly shutdown, update and
restart are authorized; publication remains a separate explicit request.

The .181 user and system installations are now verified against 464 Python
sources. The scope below passes 1,732 tests/five subtests plus compilation,
security, privacy, module and remaining release checks after local bytecode
cleanup. All six packages, both .180/.181 backups and installation are verified. The native
Qt layout crash was fixed by assigning a widget owner before extracting existing
case/profile combos from their old layouts. Bounded minimum content hints also
keep the narrow case view inside its viewport. Complete Qt main-window renders
of the hub, case and help now pass, beyond the isolated module previews.

| Request | .181 implementation | Still required |
|---|---|---|
| Case workspace closer to the approved concept | Dedicated case/profile toolbar, PC drawing surface, direct selected-component card, compact advanced/catalog/reference sections. Existing model IDs, drafts and routes remain. | Full-window geometry/lifetime and narrow-width checks passed; installed native dark/light render also passed. |
| Consistent submenu presentation | Shared palette-aware large section cards, used by case/profiles and the existing Disclosure facade. | Section/case and four full UI/localization checks passed; installed native checks also passed. |
| Smooth profile opening/closing | Bounded 420-ms reveal through the existing scrollbar; user gestures and page changes cancel automatic movement. Disabled animations remain honored. | Gradual/cancel/return/lifetime tests passed; installed native opening/closing also passed. |
| Ten more matching designs | Fifteen distinct original LCD sources, ten appended RGB presets; five existing pair IDs and first 35 preset indices preserved. | Full source gate and installed UI passed; optical device confirmation remains separate. |
| Real size control for every design | Per-pair LCD zoom 50–200%, real Matrix glyph variants 100/130/150/200%, previews use matching geometry. Explicit apply prepares an asynchronous bounded cache copy; newer LCD intent and page hiding discard old work, and bounded H.264 metadata is checked. Sensor Layer 2 remains intact. | Current apply/cancel/stale-intent and metadata regressions passed; installed UI passed; optical apply confirmation remains separate. |
| Integrated LCD manager | One embedded draft editor for Levita and Kraken with explicit Save/Cancel and indexed-media snapshot. Original files are never deleted. | State/Save/Cancel regressions and installed embedded-open/Cancel passed; existing schema preserved. |
| Clear progress meaning | Gallery preview preparation has completed/total counts and explicit wording; it is distinct from LCD transfer/playback. | Four-language full-UI coverage and installed dark/light label views passed. |
| Help and status | Top-aligned topic library/article view, explicit static inventory recognition and actual LACT read state, with bounded error logging. | Four combined UI/localization tests and installed help views passed. Recognition never implies live telemetry or write authorization. |

Targeted evidence already available: 30 current hub/size/metadata regressions,
184 RGB loop checks and 12 section/case tests pass. Complete Qt main-window
render cycles cover three sizes in both themes, including all expanded case
sections, stable combo IDs and unchanged topology. Four full UI/localization
tests confirm 2,584 shared language IDs. The MP4 structural validator is bounded
to 1 MiB of metadata, 512 atoms and depth eight; it requires H.264 1600×720 and
positive duration no greater than 35 seconds without decoding video frames.
Installed .181 Wayland views also pass, with temporary settings and hardware IO
disabled. This does not imply optical device confirmation or a Fedora hardware
result. Package checks, preservation hashes and the normal startup evidence are
recorded in `PROJECT_STATUS.md` and `RELEASE_NOTES_v3.4.29.181.md`.

## Approved original review images

- [Case and generic fan catalog](../images/design-concepts/2026-11-11/gehaeuse-entwurf.png)
- [Corsair · OpenLinkHub, mouse example](../images/design-concepts/2026-11-11/openlinkhub-entwurf.png)
- [Exact image-generation prompts](../images/design-concepts/2026-11-11/prompts.txt)

These original image_gen concepts use example illustrations and values. They
do not establish measured distances, live service health, hardware support or
permission to remove sidebar items. Earlier actual isolated .172 views are in
[rendering evidence](../images/rendering-evidence/ui-3.4.29.172/). Current source UI views, rendered with isolated settings and disabled hardware IO:

- [Case, dark](../images/rendering-evidence/case-source-3429181-dark.png) / [light](../images/rendering-evidence/case-source-3429181-light.png)
- [Matching designs and size controls](../images/rendering-evidence/design-pairs-source-3429181-dark.png)
- [Help topic workspace](../images/rendering-evidence/help-source-3429181-dark.png)
- [Embedded LCD manager](../images/rendering-evidence/lcd-inline-manager-dark-3429181.png)

The next [GPU concept, dark](../images/rendering-evidence/gpu-concept-3429181-dark.png) /
[light](../images/rendering-evidence/gpu-concept-3429181-light.png) is a Qt layout
proposal with example data, not an implemented replacement. A larger shared fan
curve with adjacent exact inputs draws on the interaction patterns documented by
[FanControl](https://getfancontrol.com/docs/) and the separate GPU information,
overclocking and fan controls in [LACT](https://github.com/ilya-zlobintsev/LACT).
No third-party artwork or UI code was copied. LCD legacy cleanup remains a
separate follow-up.

## Actual installed UI evidence

- [Case dark](../images/rendering-evidence/case-installed-3429181-dark.png) / [light](../images/rendering-evidence/case-installed-3429181-light.png)
- [Matching pairs dark](../images/rendering-evidence/design-pairs-installed-3429181-dark.png) / [light](../images/rendering-evidence/design-pairs-installed-3429181-light.png)
- [LCD manager dark](../images/rendering-evidence/lcd-manager-installed-3429181-dark.png) / [light](../images/rendering-evidence/lcd-manager-installed-3429181-light.png)
- [Help dark](../images/rendering-evidence/help-installed-3429181-dark.png) / [light](../images/rendering-evidence/help-installed-3429181-light.png)

These are captures of the installed user runtime in an actual Wayland window,
using temporary settings and disabled hardware IO. The case view reads a copy of
saved case UI data; blank device readings are intentional in this fixture.
The normal app was restarted separately with its preserved real settings.

## Established work retained

- Generic original fan illustrations cover the existing 21 reference LED counts:
  **4, 6, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28, 30, 32,
  34, 54**. The private read-only SignalRGB snapshot supplied reference facts,
  not copied artwork/code or verified manufacturer support. LED count alone
  never establishes ring/hub order, wiring or compatibility.
- .172–.174 implemented the case/catalog and OpenLinkHub concepts, default-DPI
  preference and theme-aware original icons. OpenLinkHub .9.4 was installed
  after a private .9.2 backup. This is historical evidence, not a new backend
  release check or instruction to update an already running service.
- German uses Hardware-Prüfung; English Hardware Checker; Spanish Comprobación
  de hardware; French Vérification du matériel. Hardware Fix and the supported
  model catalog remain children, with separate manufacturer/product links.
- Content-aware list sizing remains shared; intentional diagrams, galleries,
  charts and editors keep usable sizes. Empty/one-row/populated states and long
  labels need actual checks rather than blanket minimum-height removal.
- .171 removed only the redundant RGB OHC Originals category and redistributed
  its presets. OpenRGB Originals remains. LCD catalog group names are a separate
  feature and are not removed as a consequence of this category change.

## Next staged UI work — not completed by .181

- Review the broader GPU layout and fan-curve concept above, then implement it without
  reducing short-test/rollback, CoolerControl, ownership or LACT validation.
  The .181 truthful read badge is only a status correction.
- Review remaining legacy LCD controls and nested settings, keep every import,
  design, sensor-layer and ownership capability, and simplify through small
  documented modules. Embedding the media editor does not complete this cleanup.
- Continue the cross-page/HiDPI audit beyond this checked batch. The case
  ownership/narrow-width failures are fixed, not remaining blockers.

## Earlier open requests — keep visible

Modular support for additional manufacturers, improved RGB color selection,
more original fan animations and remaining light-theme details are open.
The Automation Center still needs the requested program suggestions/file
selection, time/calendar workflows and night-light options beyond its existing
rules. Current game integration prepares editable process/profile rules;
actual game telemetry and screen ambience remain future work. Windows preview
infrastructure is not Windows hardware-control support. None of these items is
closed by the .181 UI pass or by a locally successful Ubuntu run.

## Completion evidence

This batch completed targeted state/lifetime/geometry checks, four-language
full-UI coverage and all release checks after the final source changes. Keep Fedora and
Ubuntu fixture results separate from available live hardware evidence. All six artifacts and both rolling backups are verified; private settings and
profiles are preserved, both copies installed, the normal app restarted and
the actual installed UI inspected. Record the
observed result rather than changing pending items to done in advance.
