# AI / Agent Handoff

Use this when moving work between Cursor chats, Codex, Claude Code or another coding agent.

## Start a fresh session

1. Read `AGENTS.md`.
2. Read `PROJECT_STATUS.md`, `DECISIONS.md`, `ARCHITECTURE.md` and `DEVICE_SUPPORT.md`.
3. Read the latest section of `CHANGELOG.md` and current release notes.
4. Inspect `git status`, current branch and recent commits.
5. Inspect the exact code/tests related to the requested feature before proposing edits.

## During work

- Keep changes focused and reversible.
- Add/adjust tests before calling a behavior complete.
- Do not turn uncertain hardware assumptions into write commands.
- Preserve ownership/conflict guards.
- If the task creates a durable design decision, update `DECISIONS.md` immediately.

## End a substantial session

Update `PROJECT_STATUS.md` with what is now true, not what was merely discussed. Update `CHANGELOG.md` for user-visible behavior. Leave unresolved items explicitly marked as pending; never make a future agent infer them from chat history.

## Before GitHub

Run the backup gate described in `BACKUP_AND_RELEASE_POLICY.md`. A successful local test does **not** replace the Google Drive backup requirement.

## Recommended Cursor commands

- `/project-start` — recover project context.
- `/finish-feature` — tests + memory/documentation handoff.
- `/backup-before-push` — create/upload/confirm/verify Drive backup.
- `/release-preflight` — full release safety check.
