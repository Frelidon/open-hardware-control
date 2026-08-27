#!/usr/bin/env python3
import json
import os
from pathlib import Path

try:
    json.load(__import__('sys').stdin)
except Exception:
    pass
root = Path(os.environ.get('CURSOR_PROJECT_DIR', Path.cwd()))
version = (root / 'VERSION').read_text(encoding='utf-8').strip() if (root / 'VERSION').exists() else 'unknown'
channel = (root / 'BUILD_CHANNEL').read_text(encoding='utf-8').strip() if (root / 'BUILD_CHANNEL').exists() else 'unknown'
context = (
    f"Open Hardware Control project session. Repository version={version}, channel={channel}. "
    "Before substantive edits, read AGENTS.md, PROJECT_STATUS.md, DECISIONS.md and ARCHITECTURE.md. "
    "For hardware changes also read DEVICE_SUPPORT.md/SUPPORTED_DEVICES.md. "
    "Never push/release to GitHub until BACKUP_AND_RELEASE_POLICY.md is satisfied and scripts/check_drive_backup.sh passes."
)
print(json.dumps({'additional_context': context}))
