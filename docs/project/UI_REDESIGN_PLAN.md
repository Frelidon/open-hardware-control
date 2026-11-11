# UI redesign — owner review, 11.11.26

Status update: the owner approves both concepts and the additional startup-DPI,
profile, support-card and category-artwork requests. Implementation is now
3.4.29.174 INTERN, validated by 1,544 tests and five subtests. The palette
and independent startup-DPI follow-ups retain the .172 UI implementation. OpenLinkHub .9.4 is already installed after private .9.2
backup. The original review images below remain concepts; actual isolated
[dark/light renders](../images/rendering-evidence/ui-3.4.29.172/) use example
configurations and do not prove physical device output. GitHub is unchanged.

The owner requests the pictures first, before the implementation. For the
subsequent agreed implementation, orderly application shutdown, local update
and restart are explicitly authorized without asking again. GitHub publication
remains pending the owner's separate request. Keep all existing modules,
settings, hardware ownership rules and Ubuntu/Fedora paths; the concepts use a
simplified sidebar and do not authorize removing omitted navigation entries.

## Review images

- [Gehäuse and generic fan catalog](../images/design-concepts/2026-11-11/gehaeuse-entwurf.png)
- [Corsair · OpenLinkHub, mouse example](../images/design-concepts/2026-11-11/openlinkhub-entwurf.png)
- [Exact image-generation prompts](../images/design-concepts/2026-11-11/prompts.txt)

Both were created using the built-in image_gen tool. Illustrations and values
are conceptual examples. In particular, distance values and the OpenLinkHub
connection indicator are not measurements or a new live API health check.

## Case and fans

- Keep the existing original case diagrams and fan/profile machinery. Make the
  selected component's LED count, fan count, order, ARGB route and PWM assignment
  accessible together beside the diagram rather than through nested menus.
- Provide clear Overview, Components and Distances/Depth views. Keep advanced
  details available without permanently occupying vertical space.
- Build original generic fan artwork and organize by LED count and physical
  lighting layout, with search/filtering. Do not require manufacturer grouping.
  Preserve custom definitions and all existing stable model IDs. An LED count
  alone does not establish LED order, rings/hub layout or device compatibility.
- The existing private SignalRGB snapshot from 10.11.26 contains 106 fan
  definitions. Read-only analysis finds 21 distinct declared counts:
  **4, 6, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28, 30, 32,
  34, 54**. These are reference facts, not physically verified manufacturer
  support. The concept displays six representative choices, not the full list.
  Use original OHC drawings, preserve independent ring/hub/order configuration
  and do not copy private catalog images, plugins or executable code.

## Content-sized lists throughout the application

Audit every list, tree and table in empty, one-row and populated states. Prefer
one compact translated empty-state row, grow with visible row/header heights,
then cap growth and scroll. Refresh on insert/remove/reset, filtering, font,
language and scale changes; do not rescan hardware or rebuild whole pages on
every frame. Keep meaningful preview/chart sizes and usable keyboard focus.

Initial static findings, not a completed visual audit:

| Area | Current minimum height / candidate |
|---|---|
| Case distances | `spatial_layout.py`: distance list 108 px |
| Case topology | `case_page.py`: device table 220 px |
| OpenLinkHub | update controller: device table 230 px |
| Hardware check | results table 420 px |
| RGB Studio | originals 150 px, modes 220 px, selection 240 px, issues 150 px, inventory 340 px, device tree 320 px |
| Profiles | contents tree 190 px |
| Snapshot Manager | snapshots 220 px, backends 190 px, program choices 180/100 px |
| Display effects | card scrollers 150/270 px; assess actual content before changing |

Also inspect layouts without explicit minimum heights: Qt size policies and
stretch factors can create empty areas. Preserve intentional editor, diagram,
gallery and chart space; fixed heights are candidates for review, not blanket
instructions to remove every minimum.

## OpenLinkHub

- Group by selected device/category, then show supported settings, original
  mouse drawing, button assignments and DPI together. Keep service, update and
  connection controls compact; collapse advanced/diagnostic sections.
- The most recent readable local startup log reports **0.9.2**. The official
  [latest release](https://github.com/jurkovic-nikola/OpenLinkHub/releases/tag/0.9.4),
  checked on 11.11.26, is **0.9.4**. The search index still showed .3, so the
  direct latest-release redirect was used to verify .4.
- Before updating, inspect the current running service, backup/settings format,
  release checksum/assets and API compatibility, including .4's authentication
  and TLS changes. Preserve loopback-only access, separate Ubuntu/Fedora update
  paths and exactly one hardware-owning service. Never run the old and new
  backends concurrently. No backend update has yet been executed.

## Hardware check naming and navigation

- German: consistently **Hardware-Prüfung**, including sidebar, page title,
  section title, tooltips and the full-check action.
- English: **Hardware Checker**. Spanish: **Comprobación de hardware**.
  French: **Vérification du matériel**. Apply through shared stable localization
  IDs and live refresh, preserving internal keys and saved navigation state.
- Show **Hardware Fix** as an indented expandable child beneath the hardware
  check in the left navigation, using the established LCD subnavigation
  behavior. It currently exists only as an inner tab. Preserve the existing
  diagnostic/fix pages and their process lifetime/ownership behavior.

## Validation after implementation

Use targeted tests for content sizing/model events, navigation persistence and
all four languages, plus the mandatory real offscreen full-UI localization
coverage and complete release gate. Check narrow windows, long names, HiDPI,
empty lists and large inventories. Report Ubuntu/Fedora fixture evidence
separately from available live hardware results. Build a new internal version
with verified release backups, then perform the authorized orderly local
installation/restart. Do not describe these steps as already completed.

## Remaining earlier ideas

Keep the previous open work visible: modular additional manufacturer support,
RGB Studio color selection, more original fan effects, a supported-device
overview, Automation Center program/file/time/calendar/night-light workflows,
GPU page modernization and complete light-theme coverage. This design pass
addresses the case/fan, compact-list, OpenLinkHub and hardware-navigation scope.
OpenRGB Originals explicitly stays; redundant OHC Originals category removal
and redistribution are already prepared in .171, with preset indices preserved.
