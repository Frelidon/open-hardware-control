from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
assert (ROOT / 'AGENTS.md').is_file()
assert (ROOT / 'PROJECT_STATUS.md').is_file()
assert (ROOT / 'DECISIONS.md').is_file()
assert (ROOT / 'ARCHITECTURE.md').is_file()
assert (ROOT / 'DEVICE_SUPPORT.md').is_file()
assert (ROOT / 'BACKUP_AND_RELEASE_POLICY.md').is_file()
assert (ROOT / '.cursor/hooks.json').is_file()

hooks = json.loads((ROOT / '.cursor/hooks.json').read_text(encoding='utf-8'))
assert hooks['version'] == 1
before = hooks['hooks']['beforeShellExecution']
assert any('guard-github-push.py' in item['command'] and item.get('failClosed') is True for item in before)
assert any('guard-destructive-shell.py' in item['command'] for item in before)

agent = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
assert 'Never upload/push project state to GitHub until the Google Drive backup gate passes.' in agent
assert 'Overview, Navigation customization and Help are permanent navigation safety anchors' in agent

create_release = (ROOT / 'scripts/create_release.sh').read_text(encoding='utf-8')
publish = (ROOT / 'scripts/publish_github.sh').read_text(encoding='utf-8')
assert './scripts/check_drive_backup.sh' in create_release
assert './scripts/check_drive_backup.sh' in publish
print('3.4.26 agent memory, Cursor hooks and Drive backup-gate guards passed.')
