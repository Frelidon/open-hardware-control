# Open Hardware Control 3.4.26 INTERN

3.4.26 is an internal developer-workflow and project-memory release built on the 3.4.25 UI/navigation baseline. Runtime hardware behavior is intentionally preserved; the main change is that coding agents can now recover durable project context and use consistent development and release checks.

## Agent memory and handoff

- Added `AGENTS.md`, `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `DEVICE_SUPPORT.md` and `AI_HANDOFF.md`.
- Added Cursor rules and slash commands for project startup, feature completion and release preflight.
- Added a session-start hook that reminds fresh Cursor chats of the repository memory and publication policy.

## Publication workflow

- Release scripts require the correct build channel, GitHub authentication, a clean committed worktree and successful release checks.
- Google Drive and external backup providers are intentionally not part of the publication workflow.
- Pushes, tags and releases require an explicit project-owner request.

## Safety

Destructive shell/Git commands matched by the Cursor hook require explicit approval. `BUILD_CHANNEL=INTERN` remains active, so public release publication stays blocked until an intentional stable release is prepared.
