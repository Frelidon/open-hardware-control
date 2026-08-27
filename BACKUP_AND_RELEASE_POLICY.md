# Backup and GitHub Release Policy

## Goal

Every GitHub upload must have an independent recoverable backup of the exact committed state first.

The backup gate is intentionally bound to Git `HEAD`: if another commit is created, the old confirmation no longer authorizes a push.

## One-time Cursor setup

1. Open Cursor **Customize**.
2. Install the official **Google Drive** plugin (`google-drive`) and sign in with Google OAuth.
3. Let the agent create/find the configured folder from `AGENT_BACKUP_CONFIG.json` (`OpenHardware-Control/Backups` by default).
4. Do not copy OAuth tokens or Google credentials into project files.

## Normal backup-before-push workflow

From a clean Git worktree:

```bash
./scripts/prepare_drive_backup.sh
```

This creates `.ohc-backups/pending/<name>.zip` containing:

- a Git bundle with repository history/refs;
- a ZIP snapshot of the exact committed `HEAD` source tree;
- metadata identifying version, branch and commit;
- SHA-256 information.

Then upload **that exact ZIP** to the configured Google Drive folder through Cursor's Google Drive plugin.

Only after the Drive tool reports a successful upload, confirm it locally:

```bash
./scripts/confirm_drive_backup.sh --remote-name "<uploaded filename>"
```

If the Drive result exposes a file ID, record it too:

```bash
./scripts/confirm_drive_backup.sh --remote-name "<uploaded filename>" --drive-file-id "<id>"
```

Finally:

```bash
./scripts/check_drive_backup.sh
```

Only a successful check authorizes `git push` for the current `HEAD`.

## Why confirmation is separate

A shell script cannot safely impersonate Cursor's Google OAuth session. The project therefore creates and verifies the archive locally, while Cursor's official plugin performs the authenticated Drive action. The local confirmation is an auditable assertion that the plugin reported success for the exact archive.

## Fallback: locally mounted/synced Drive directory

If the official plugin cannot upload a binary archive in the current Cursor environment, copy the exact generated ZIP into a user-controlled Google Drive mount/sync folder, verify the copied SHA-256, then run the same confirmation command. Do not weaken or disable the GitHub gate.

## Enforcement

- `.cursor/hooks.json` checks direct `git push`, `gh repo create --push` and `gh release create` commands.
- `scripts/create_release.sh` and `scripts/publish_github.sh` also call the backup verifier internally.
- Hook failures are fail-closed for the GitHub backup guard.
- Destructive shell commands require an explicit confirmation prompt through a second Cursor hook.

## Restore

Keep both the outer ZIP checksum and the archive itself. `repository.bundle` can recreate repository history with Git; `head-source.zip` provides the exact file snapshot even without Git tooling.
