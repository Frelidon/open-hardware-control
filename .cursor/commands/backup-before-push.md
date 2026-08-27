---
name: backup-before-push
description: Create and verify the required Google Drive backup before GitHub
---

Follow `BACKUP_AND_RELEASE_POLICY.md`. Ensure the intended changes are committed and the worktree is clean. Run `./scripts/prepare_drive_backup.sh`. Upload the exact generated ZIP to the Google Drive folder in `AGENT_BACKUP_CONFIG.json` using the official Google Drive plugin. Only after the tool reports successful upload, run `./scripts/confirm_drive_backup.sh --remote-name "<exact uploaded filename>"` (and include `--drive-file-id` when available), then run `./scripts/check_drive_backup.sh`. Do not push unless verification succeeds and the user has actually requested the push.
