# Cursor Setup for Open Hardware Control

## What is already version-controlled

- `AGENTS.md` durable project instructions.
- `.cursor/rules/*.mdc` scoped persistent rules.
- `.cursor/commands/*.md` reusable workflows.
- `.cursor/hooks.json` + `.cursor/hooks/*.py` safety hooks.
- Project memory documents (`docs/project/PROJECT_STATUS.md`, `docs/project/DECISIONS.md`, `docs/project/ARCHITECTURE.md`, `docs/hardware/DEVICE_SUPPORT.md`).

When the repository is opened as a trusted Cursor workspace, project hooks are loaded from `.cursor/hooks.json`.

## First use

1. Open the repository root in Cursor (not a random extracted subfolder).
2. Mark the workspace trusted so project hooks can run.
3. Open Customize and verify the project rules/hooks are visible.
4. Start a fresh Agent chat and run `/project-start`.
5. Ask the agent to report the current version, channel, Git branch and major modules before editing anything.

## Fresh chat behavior

`AGENTS.md`, always-on Cursor rules and a `sessionStart` hook all point the agent back to repository memory. This does not create an infinite model context; it makes recovery from a new/compacted chat deterministic.

## Hook troubleshooting

Cursor exposes Hooks in Customize and a Hooks output channel. If hooks are not detected after opening the project, verify workspace trust, file permissions and restart/reload Cursor.
