#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP_PYCACHE="$(mktemp -d)"
trap 'rm -rf "$TMP_PYCACHE"' EXIT

mapfile -t python_files < <(find . -type f -name '*.py' -not -path './dist/*' -not -path './build/*' -not -path './.git/*' | sort)
PYTHONPYCACHEPREFIX="$TMP_PYCACHE" python3 -m py_compile "${python_files[@]}"
bash -n install.sh install-dependencies.sh install-udev-rule.sh collect-diagnostics.sh uninstall.sh scripts/*.sh

for test_file in tests/test_*.py; do
  echo "Running $test_file"
  PYTHONDONTWRITEBYTECODE=1 python3 "$test_file"
done

PYTHONDONTWRITEBYTECODE=1 python3 scripts/security_scan_release.py

VERSION="$(tr -d '\r\n' < VERSION)"
CHANNEL="$(tr -d '\r\n' < BUILD_CHANNEL)"
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
  echo "Invalid VERSION: $VERSION" >&2
  exit 1
fi
if ! grep -Fq "APP_VERSION = \"$VERSION\"" kraken_control.py; then
  echo "APP_VERSION does not match VERSION $VERSION." >&2
  exit 1
fi
if [[ ! -f "docs/RELEASE_NOTES_v${VERSION}.md" ]]; then
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
  LICENSE README.md README.en.md INSTALL.md CHANGELOG.md SECURITY.md PRIVACY.md BUILD_CHANNEL \
  CONTRIBUTING.md SOURCE_CODE.md DEVELOPER_PACKAGE.md VERSION AGENTS.md PROJECT_STATUS.md ARCHITECTURE.md DECISIONS.md DEVICE_SUPPORT.md AI_HANDOFF.md CURSOR_SETUP.md START_HIER_LOKALE_KI.md LM_STUDIO_ANLEITUNG_DE.md LOCAL_AI_STARTPROMPT.txt \
  kraken_control.py kraken_cam_streamer.py openlinkhub_integration.py openrgb_integration.py openrgb_sdk.py rgb_effects.py ui_layout.py desktop_designs.py \
  desktop_assets.py desktop_shell.py DESKTOP_SECURITY_AUDIT.md RGB_STUDIO.md RGB_SECURITY_AUDIT.md SECURITY_SCAN_REPORT.json \
  scripts/build_release.py scripts/build_release.sh \
  .cursor/hooks.json .cursor/hooks/session-start.py .cursor/hooks/guard-destructive-shell.py; do
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
