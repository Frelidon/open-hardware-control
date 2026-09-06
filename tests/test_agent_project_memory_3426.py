from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
assert (ROOT / 'AGENTS.md').is_file()
assert (ROOT / 'docs/project/PROJECT_STATUS.md').is_file()
assert (ROOT / 'docs/project/DECISIONS.md').is_file()
assert (ROOT / 'docs/project/ARCHITECTURE.md').is_file()
assert (ROOT / 'docs/hardware/DEVICE_SUPPORT.md').is_file()
assert (ROOT / 'docs/project/RELEASE_BACKUP_POLICY.md').is_file()
assert (ROOT / '.github/copilot-instructions.md').is_file()
assert (ROOT / '.cursor/hooks.json').is_file()

hooks = json.loads((ROOT / '.cursor/hooks.json').read_text(encoding='utf-8'))
assert hooks['version'] == 1
before = hooks['hooks']['beforeShellExecution']
assert any('guard-destructive-shell.py' in item['command'] for item in before)

agent = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
assert 'Overview, Navigation customization and Help are permanent navigation safety anchors' in agent
assert 'explicit project-owner request' in agent
assert 'A normal push of committed, tested work to a non-release development branch is explicitly permitted' in agent
assert '`BUILD_CHANNEL=INTERN` does not block such a branch push' in agent
assert 'docs/project/RELEASE_BACKUP_POLICY.md' in agent

backup_policy = (ROOT / 'docs/project/RELEASE_BACKUP_POLICY.md').read_text(encoding='utf-8')
assert 'Open Hardware Control Backup' in backup_policy
assert 'mindestens die zwei neuesten' in backup_policy
assert 'SHA256SUMS' in backup_policy
copilot = (ROOT / '.github/copilot-instructions.md').read_text(encoding='utf-8')
assert 'docs/project/RELEASE_BACKUP_POLICY.md' in copilot
assert 'zwei neuesten vollständigen Versionsordner' in copilot
builder = (ROOT / 'scripts/build_release.py').read_text(encoding='utf-8')
assert 'backup_release(ROOT, DIST, VERSION, CHANNEL)' in builder

publishing = (ROOT / 'docs/project/GITHUB_PUBLISHING_GUIDE_DE.md').read_text(encoding='utf-8')
assert '3.4.29.46 STABLE – GitHub-Veröffentlichung' in publishing
assert 'erfolgreicher vollständiger Prüfung, sauberem Commit und realem KDE-/Hardwaretest' in publishing
assert 'Die Erlaubnis für den normalen Branch-Push erlaubt niemals automatisch Force-Push' in publishing

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
