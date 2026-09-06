#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP_PYCACHE="$(mktemp -d)"
trap 'rm -rf "$TMP_PYCACHE"' EXIT

mapfile -t python_files < <(find . -type f -name '*.py' -not -path './dist/*' -not -path './build/*' -not -path './.git/*' | sort)
PYTHONPYCACHEPREFIX="$TMP_PYCACHE" python3 -m py_compile "${python_files[@]}"
bash -n install.sh packaging/install-dependencies.sh packaging/install-udev-rule.sh packaging/collect-diagnostics.sh uninstall.sh scripts/*.sh

PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q

PYTHONDONTWRITEBYTECODE=1 python3 scripts/security_scan_release.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_module_registry.py

VERSION="$(tr -d '\r\n' < VERSION)"
CHANNEL="$(tr -d '\r\n' < BUILD_CHANNEL)"
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
  echo "Invalid VERSION: $VERSION" >&2
  exit 1
fi
if ! grep -Fq "APP_VERSION = \"$VERSION\"" app_constants.py; then
  echo "APP_VERSION does not match VERSION $VERSION." >&2
  exit 1
fi
if [[ ! -f "docs/releases/RELEASE_NOTES_v${VERSION}.md" ]]; then
  echo "Missing release notes for $VERSION." >&2
  exit 1
fi

if grep -RInE \
  --exclude-dir=.git --exclude-dir=dist --exclude-dir=__pycache__ \
  --exclude='*.gz' --exclude='*.zip' --exclude='*.rpm' --exclude='*.deb' \
  --exclude='*.png' --exclude='*.gif' --exclude='*.jpg' --exclude='*.jpeg' \
  '(BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})' .; then
  echo "Potential secret detected." >&2
  exit 1
fi

if grep -RInE \
  --exclude-dir=.git --exclude-dir=dist --exclude-dir=__pycache__ \
  --exclude='*.gz' --exclude='*.zip' --exclude='*.rpm' --exclude='*.deb' \
  '/home/[A-Za-z0-9._-]+' . | grep -vE '\[USER\]|exampleuser|collect-diagnostics\.sh|kraken_control\.py|test_runtime_logic_stub\.py'; then
  echo "Potential personal home path detected." >&2
  exit 1
fi

if find . -type d -name __pycache__ -print -quit | grep -q .; then
  echo "Remove __pycache__ before release." >&2
  exit 1
fi

for required in \
  LICENSE README.md README.en.md INSTALL.md CHANGELOG.md SECURITY.md docs/security/PRIVACY.md BUILD_CHANNEL docs/project/MODULE_REGISTRY.md docs/ai/AI_DEVELOPMENT_GUIDE.md docs/project/RELEASE_BACKUP_POLICY.md \
  .github/CONTRIBUTING.md docs/project/SOURCE_CODE.md docs/project/DEVELOPER_PACKAGE.md VERSION AGENTS.md docs/project/PROJECT_STATUS.md docs/project/ARCHITECTURE.md docs/project/MODULE_MAP.md docs/project/DECISIONS.md docs/hardware/DEVICE_SUPPORT.md docs/ai/AI_HANDOFF.md docs/ai/CURSOR_SETUP.md docs/ai/START_HIER_LOKALE_KI.md docs/ai/LM_STUDIO_ANLEITUNG_DE.md docs/ai/LOCAL_AI_STARTPROMPT.txt \
  kraken_control.py app_constants.py command_backend.py cooling_card_state.py cooling_widgets.py dashboard_layout.py localization_catalog.py privacy_logging.py temperature_utils.py kraken_cam_streamer.py openlinkhub_integration.py openrgb_integration.py openrgb_sdk.py rgb_effects.py ui_layout.py desktop_designs.py \
  desktop_assets.py desktop_shell.py docs/security/DESKTOP_SECURITY_AUDIT.md docs/hardware/RGB_STUDIO.md docs/security/RGB_SECURITY_AUDIT.md docs/security/SECURITY_SCAN_REPORT.json \
  scripts/build_release.py scripts/backup_release.py scripts/build_release.sh scripts/check_module_registry.py \
  .github/copilot-instructions.md .cursor/hooks.json .cursor/hooks/session-start.py .cursor/hooks/guard-destructive-shell.py; do
  [[ -f "$required" ]] || { echo "Missing required file: $required" >&2; exit 1; }
done

if [[ "$CHANNEL" == "INTERN" ]]; then
  grep -Fq "open_hardware_control_v${VERSION//./_}_INTERN.zip" README.md
  grep -Fq "open-hardware-control_${VERSION}~intern2_all.deb" README.md
  grep -Fq "open-hardware-control-${VERSION}-0.intern2.noarch.rpm" README.md
else
  grep -Fq "open_hardware_control_v${VERSION//./_}.zip" README.md
  grep -Fq "open-hardware-control_${VERSION}_all.deb" README.md
  grep -Fq "open-hardware-control-${VERSION}-1.noarch.rpm" README.md
fi
grep -Fq 'developer_name = f"Entwicklerpaket {VERSION}' scripts/build_release.py

python3 -m json.tool .cursor/hooks.json >/dev/null

grep -Fq 'alwaysApply: true' .cursor/rules/00-project-core.mdc
grep -Fq 'beforeShellExecution' .cursor/hooks.json
for removed in \
  AGENT_BACKUP_CONFIG.json BACKUP_AND_RELEASE_POLICY.md \
  .cursor/commands/backup-before-push.md .cursor/hooks/guard-github-push.py .cursor/rules/40-git-backup.mdc \
  scripts/agent_backup.py scripts/check_drive_backup.sh scripts/confirm_drive_backup.sh scripts/prepare_drive_backup.sh; do
  [[ ! -e "$removed" ]] || { echo "Removed backup workflow file still exists: $removed" >&2; exit 1; }
done
! grep -Fq 'check_drive_backup.sh' scripts/create_release.sh
! grep -Fq 'check_drive_backup.sh' scripts/publish_github.sh

echo "All repository release checks passed for $VERSION."
