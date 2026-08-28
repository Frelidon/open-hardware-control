# Open Hardware Control — Agent Instructions

This repository is the long-term source of truth for Open Hardware Control by Frelidon. Do not rely on chat history as the only project memory.

## Mandatory startup sequence

Before any substantive code change:

1. Read `PROJECT_STATUS.md`.
2. Read `DECISIONS.md`.
3. Read `ARCHITECTURE.md`.
4. Read `DEVICE_SUPPORT.md` and the authoritative `SUPPORTED_DEVICES.md` when hardware support is involved.
5. Read the relevant latest release notes and `CHANGELOG.md`.
6. Inspect `git status` and the relevant code/tests before editing.

If a request conflicts with these files or the current code, stop and explain the conflict instead of silently deleting or redesigning established behavior.

## Project identity and boundaries

- Product: **Open Hardware Control by Frelidon**.
- Main application file: `kraken_control.py` (historical filename retained intentionally).
- Open Radeon Control Center is a separate project and must not be merged into this repository.
- The project is independent and unofficial; manufacturer names are compatibility references, not endorsements or partnerships.
- Never add proprietary manufacturer assets unless their license and redistribution rights are explicitly verified and documented.

## Preserve existing behavior

- Prefer additive, backward-compatible changes.
- Never remove an existing supported feature merely to simplify an implementation.
- Preserve user settings and migrations unless a migration is explicitly designed and tested.
- Overview, Navigation customization and Help are permanent navigation safety anchors and must never be hideable or removable.
- Hardware ownership boundaries must remain intact: NZXT, OpenLinkHub, OpenRGB and mainboard fan paths must not race each other for the same device.

## Hardware safety

- Do not guess USB protocols, IDs, PWM mappings, LED counts, firmware commands or writable sysfs paths.
- New hardware write paths require evidence, validation, bounds checking and a safe failure mode.
- Real hardware compatibility must never be claimed from code inspection alone.
- Never bypass Secure Boot, MOK, kernel protections or permission systems.
- Keep OpenLinkHub network access loopback-only unless the project owner explicitly changes the security model.
- Keep the OpenRGB SDK integration loopback-only and respect external-process ownership detection.
- Mainboard PWM channels require calibration/confirmation before automatic writes; GPU fan control is out of scope unless explicitly designed later.

## Testing and completion

- Run the narrowest relevant tests while developing.
- Before declaring a version/release ready, run `./scripts/check_release.sh`.
- Update or add regression tests for behavior changes.
- Do not weaken tests to make broken behavior pass.
- Update `PROJECT_STATUS.md` after meaningful changes and `DECISIONS.md` when a durable product/architecture decision changes.
- Add a `CHANGELOG.md` entry for user-visible changes and release notes for a versioned release.

## Git and GitHub safety

Before any `git push`, GitHub repository push, tag push or GitHub release action:

1. Ensure the worktree is clean and the intended changes are committed.
2. Run the relevant tests and inspect the final diff.
3. Keep `BUILD_CHANNEL=INTERN` until a public release is intentionally prepared and validated.
4. Require an explicit project-owner request before pushing, tagging or creating a release.

## Destructive commands

Do not run destructive commands (`rm -rf`, `git reset --hard`, `git clean -f`, force-push, branch/tag deletion, mass restore) without explicit user approval. Cursor hooks are configured to require confirmation for these commands.

## Secrets and privacy

- Never commit passwords, OAuth tokens, API keys, private keys, personal logs or unredacted diagnostics.

## Fresh-chat handoff

A fresh agent should begin with `/project-start` in Cursor or manually follow the startup sequence above. At the end of substantial work, use `/finish-feature` so project memory reflects what actually changed.
