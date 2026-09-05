# AI / Agent Handoff

Use this when moving work between Cursor chats, Codex, Claude Code or another coding agent.

For LM Studio with a local model, begin with `START_HIER_LOKALE_KI.md`; the user-facing setup steps and reusable first prompt are in `LM_STUDIO_ANLEITUNG_DE.md` and `LOCAL_AI_STARTPROMPT.txt`.

## Start a fresh session

1. Read `AGENTS.md`.
2. Read `PROJECT_STATUS.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `MODULE_MAP.md`, `DEVICE_SUPPORT.md` and `RELEASE_BACKUP_POLICY.md`.
3. Read the latest section of `CHANGELOG.md` and current release notes.
4. Inspect `git status`, current branch and recent commits.
5. Inspect the exact code/tests related to the requested feature before proposing edits.

For a context-limited local model, use the task-specific file sets in `MODULE_MAP.md`; do not load all of `kraken_control.py` when a targeted `rg` search and one focused section are sufficient.

## During work

- Keep changes focused and reversible.
- Add/adjust tests before calling a behavior complete.
- Do not turn uncertain hardware assumptions into write commands.
- Preserve ownership/conflict guards.
- If the task creates a durable design decision, update `DECISIONS.md` immediately.

## End a substantial session

Update `PROJECT_STATUS.md` with what is now true, not what was merely discussed. Update `CHANGELOG.md` for user-visible behavior. Leave unresolved items explicitly marked as pending; never make a future agent infer them from chat history.

After a version build, confirm the sibling `Open Hardware Control Backup` directory contains the newest two complete versions and that both `SHA256SUMS` files validate.

## Before GitHub

Require a clean committed worktree, run the relevant release checks and verify the release channel. Push, tag or create a release only after an explicit project-owner request.

## Recommended Cursor commands

- `/project-start` — recover project context.
- `/finish-feature` — tests + memory/documentation handoff.
- `/release-preflight` — full release safety check.
