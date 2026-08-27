#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    payload = json.load(sys.stdin)
except Exception as exc:
    print(json.dumps({'permission': 'deny', 'user_message': f'Backup guard could not parse Cursor hook input: {exc}', 'agent_message': 'Do not push. Repair the backup hook first.'}))
    raise SystemExit(0)

root = Path(os.environ.get('CURSOR_PROJECT_DIR') or payload.get('cwd') or Path.cwd()).resolve()
checker = root / 'scripts' / 'agent_backup.py'
if not checker.exists():
    print(json.dumps({'permission': 'deny', 'user_message': 'GitHub push blocked: scripts/agent_backup.py is missing.', 'agent_message': 'Restore the repository backup guard; do not bypass it.'}))
    raise SystemExit(0)

proc = subprocess.run([sys.executable, str(checker), 'verify', '--quiet'], cwd=root, text=True, capture_output=True)
if proc.returncode == 0:
    print(json.dumps({'permission': 'allow', 'agent_message': 'Drive backup gate verified for the current Git HEAD.'}))
else:
    reason = (proc.stderr or proc.stdout or 'backup is missing or stale').strip()
    print(json.dumps({
        'permission': 'deny',
        'user_message': 'GitHub push blocked: the Google Drive backup gate is not valid for the current commit.',
        'agent_message': (
            'Do not bypass this guard. Ensure changes are committed and worktree is clean; run ./scripts/prepare_drive_backup.sh; '
            'upload the exact generated archive through the official Google Drive plugin; only after successful upload run '
            './scripts/confirm_drive_backup.sh --remote-name "<uploaded filename>"; then run ./scripts/check_drive_backup.sh. '
            f'Current verifier detail: {reason}'
        )
    }))
