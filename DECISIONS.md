# Open Hardware Control — Durable Decisions

This file records decisions that future agents must preserve unless the project owner explicitly changes them. New durable decisions should be appended with a date/version and rationale.

## Product and repository

- **2026-08 / current:** Product name is Open Hardware Control by Frelidon. The historical filename `kraken_control.py` remains because it contains the integrated mature NZXT module; renaming the file is not required for branding.
- **2026-08 / current:** Open Radeon Control Center stays a separate project.
- **2026-08 / current:** The project remains manufacturer-neutral and unofficial. Compatibility names do not imply partnership, approval or support from manufacturers or related open-source projects.

## Navigation and UI

- **3.4.25:** Main navigation can be reordered by drag & drop and applicable categories can be shown/hidden.
- **3.4.25:** **Overview, Navigation customization and Help are permanent safety anchors. They can never be removed or hidden.** Reset-to-default navigation must remain available.
- **3.4.25:** Modern compact PySide6 visual language should stay consistent across Overview, Cooling, RGB Studio, LCD, Profiles, Log, OpenLinkHub, Settings, About, Help and Desktop Designs.
- **3.4.25:** Chassis fan curves use the embedded interactive editor and stored table values remain synchronized with draggable points.
- **3.4.27:** Kraken quick-profile buttons represent confirmed device state, not click intent. A profile becomes active only after both pump and radiator-fan writes succeed; manual values, curves and general profiles clear the quick-profile highlight.
- **3.4.27:** Internal mainboard-channel selection and visible chassis-fan-card expansion are separate states. Detection may select a channel for compatibility, but it must not open a card; only an explicit user action expands at most one card.

## Hardware ownership and safety

- NZXT Kraken control remains a first-class built-in module.
- Corsair control is mediated through OpenLinkHub's local API; do not add speculative direct Corsair USB writes.
- OpenRGB remains a separately installed backend managed through OHC's private loopback engine; do not bundle/copy its hardware driver source into OHC.
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

## Assets and licensing

- Use project-owned schematic graphics by default.
- Do not embed third-party product photos, manufacturer renderings or copied UI artwork without verified redistribution rights and required attribution/license handling.

## AI development and memory

- **3.4.26:** Repository memory files and tests are the durable source of truth; a long chat is not.
- **3.4.26:** Agents must update `PROJECT_STATUS.md` after meaningful project changes and this file when a durable decision changes.
- **3.4.26:** Cursor project rules and hooks are version-controlled so fresh chats inherit project constraints.
- **3.4.27:** The historical `kraken_control.py` monolith is reduced incrementally through focused, non-circular modules. During migration it remains the executable compatibility orchestrator and re-exports moved names; large simultaneous UI and hardware-writer rewrites are not accepted.
- **3.4.27:** `MODULE_MAP.md` is the task-routing guide for context-limited local coding models. Agents should read targeted functions and their direct dependencies instead of loading the complete main file for every task.

## GitHub publication

- **2026-08-27 / 3.4.26:** The project owner explicitly removed the Google Drive backup workflow and its mandatory push gate. GitHub publication does not depend on Google Drive or another external backup provider.
- **2026-08-27 / 3.4.26:** Pushes, tags and releases still require a clean committed worktree, relevant successful tests, the correct release channel and an explicit project-owner request.
- **2026-08-27 / 3.4.26:** Authentication credentials and tokens must never be stored in the repository.
