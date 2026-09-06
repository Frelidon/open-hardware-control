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
    "Before substantive edits, read AGENTS.md, docs/project/MODULE_REGISTRY.md, docs/ai/AI_DEVELOPMENT_GUIDE.md, "
    "docs/project/PROJECT_STATUS.md, docs/project/DECISIONS.md and docs/project/ARCHITECTURE.md. Use only the current registered module version. "
    "For hardware changes also read docs/hardware/DEVICE_SUPPORT.md/SUPPORTED_DEVICES.md. "
    "Push, tag or release only from a clean tested worktree after an explicit project-owner request."
)
print(json.dumps({'additional_context': context}))
