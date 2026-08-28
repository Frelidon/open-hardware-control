from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
assert (ROOT / 'AGENTS.md').is_file()
assert (ROOT / 'PROJECT_STATUS.md').is_file()
assert (ROOT / 'DECISIONS.md').is_file()
assert (ROOT / 'ARCHITECTURE.md').is_file()
assert (ROOT / 'DEVICE_SUPPORT.md').is_file()
assert (ROOT / '.cursor/hooks.json').is_file()

hooks = json.loads((ROOT / '.cursor/hooks.json').read_text(encoding='utf-8'))
assert hooks['version'] == 1
before = hooks['hooks']['beforeShellExecution']
assert any('guard-destructive-shell.py' in item['command'] for item in before)

agent = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
assert 'Overview, Navigation customization and Help are permanent navigation safety anchors' in agent
assert 'explicit project-owner request' in agent

removed = [
    'AGENT_BACKUP_CONFIG.json',
    'BACKUP_AND_RELEASE_POLICY.md',
    '.cursor/commands/backup-before-push.md',
    '.cursor/hooks/guard-github-push.py',
    '.cursor/rules/40-git-backup.mdc',
    'scripts/agent_backup.py',
    'scripts/check_drive_backup.sh',
    'scripts/confirm_drive_backup.sh',
    'scripts/prepare_drive_backup.sh',
]
assert all(not (ROOT / path).exists() for path in removed)
print('3.4.26 agent memory and Cursor safety guards passed without an external backup gate.')
