# Open Hardware Control 3.4.26 INTERN

3.4.26 is an internal developer-workflow and project-memory release built on the 3.4.25 UI/navigation baseline. Runtime hardware behavior is intentionally preserved; the main change is that coding agents can now recover durable project context and are prevented from pushing a commit to GitHub without an independently confirmed backup.

## Agent memory and handoff

- Added `AGENTS.md`, `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `DEVICE_SUPPORT.md` and `AI_HANDOFF.md`.
- Added Cursor rules and slash commands for project startup, feature completion, backup and release preflight.
- Added a session-start hook that reminds fresh Cursor chats of the repository memory and publication policy.

## Backup gate

- `scripts/agent_backup.py` creates a full Git bundle plus exact-HEAD source archive inside a checksummed outer ZIP.
- Confirmation is bound to the current commit, archive filename and SHA-256; any new commit makes the authorization stale.
- Cursor's `beforeShellExecution` hook blocks direct GitHub push/release commands until the gate verifies.
- `scripts/create_release.sh` and `scripts/publish_github.sh` also enforce the same verifier.
- The intended remote target is the official Cursor Google Drive plugin. OAuth credentials are never stored in this repository.

## Safety

Destructive shell/Git commands matched by the Cursor hook require explicit approval. `BUILD_CHANNEL=INTERN` remains active, so public release publication is still blocked independently of the new backup gate.
