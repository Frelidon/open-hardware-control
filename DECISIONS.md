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

## Hardware ownership and safety

- NZXT Kraken control remains a first-class built-in module.
- Corsair control is mediated through OpenLinkHub's local API; do not add speculative direct Corsair USB writes.
- OpenRGB remains a separately installed backend managed through OHC's private loopback engine; do not bundle/copy its hardware driver source into OHC.
- A foreign OpenRGB process/server blocks OHC writes rather than being killed automatically.
- OpenLinkHub and OpenRGB integrations remain loopback-only unless security architecture is explicitly redesigned.
- Mainboard PWM control requires physical channel confirmation/calibration before automatic control. Never infer electrical fan mapping from board model alone.
- CPU_FAN/PUMP_FAN ownership must not conflict with Kraken cooling ownership.
- Firmware update/flashing features require a separate explicit design/review; no agent may infer or invent firmware-write protocols.

## Assets and licensing

- Use project-owned schematic graphics by default.
- Do not embed third-party product photos, manufacturer renderings or copied UI artwork without verified redistribution rights and required attribution/license handling.

## AI development and memory

- **3.4.26:** Repository memory files and tests are the durable source of truth; a long chat is not.
- **3.4.26:** Agents must update `PROJECT_STATUS.md` after meaningful project changes and this file when a durable decision changes.
- **3.4.26:** Cursor project rules and hooks are version-controlled so fresh chats inherit project constraints.

## Backup and GitHub publication

- **3.4.26:** Before any GitHub push/tag/release, create a backup bound to the exact current Git `HEAD`, upload the exact archive to the configured Google Drive location and confirm that upload locally.
- **3.4.26:** A new commit invalidates the previous backup authorization automatically because the stored `HEAD` no longer matches.
- **3.4.26:** Cursor's `beforeShellExecution` hook must block direct push/release commands when the backup gate is stale/missing. Do not weaken the hook to bypass the policy.
- **3.4.26:** Google OAuth credentials are never stored in the repository.
