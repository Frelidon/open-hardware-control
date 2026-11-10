#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP_PYCACHE="$(mktemp -d)"
trap 'rm -rf "$TMP_PYCACHE"' EXIT

mapfile -t python_files < <(find . -type f -name '*.py' -not -path './dist/*' -not -path './build/*' -not -path './.git/*' | sort)
PYTHONPYCACHEPREFIX="$TMP_PYCACHE" python3 -m py_compile "${python_files[@]}"
bash -n packaging/install.sh packaging/uninstall.sh packaging/install-dependencies.sh packaging/install-lact.sh packaging/install-trcc.sh packaging/install-udev-rule.sh packaging/install-fan-helper.sh packaging/install-snapshot-helper.sh packaging/collect-diagnostics.sh scripts/*.sh

PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q

PYTHONDONTWRITEBYTECODE=1 python3 scripts/security_scan_release.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_module_registry.py

VERSION="$(tr -d '\r\n' < packaging/VERSION)"
CHANNEL="$(tr -d '\r\n' < packaging/BUILD_CHANNEL)"
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
  echo "Invalid VERSION: $VERSION" >&2
  exit 1
fi
if ! grep -Fq "APP_VERSION = \"$VERSION\"" src/app_constants.py; then
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

for required in LICENSE README.md docs/README.en.md docs/INSTALL.md docs/CHANGELOG.md .github/SECURITY.md docs/security/PRIVACY.md \
  packaging/BUILD_CHANNEL docs/project/MODULE_REGISTRY.md docs/ai/AI_DEVELOPMENT_GUIDE.md docs/project/RELEASE_BACKUP_POLICY.md \
  .github/CONTRIBUTING.md docs/project/SOURCE_CODE.md docs/project/DEVELOPER_PACKAGE.md packaging/VERSION docs/ai/AGENTS.md \
  docs/project/PROJECT_STATUS.md docs/project/ARCHITECTURE.md docs/project/MODULE_MAP.md docs/project/DECISIONS.md docs/hardware/DEVICE_SUPPORT.md \
  docs/ai/AI_HANDOFF.md docs/ai/CURSOR_SETUP.md docs/ai/START_HIER_LOKALE_KI.md docs/ai/LM_STUDIO_ANLEITUNG_DE.md docs/ai/LOCAL_AI_STARTPROMPT.txt \
  src/kraken_control.py src/app_constants.py src/command_backend.py src/cooling_card_state.py src/cooling_widgets.py src/dashboard_layout.py src/modules/lcd_levita_shutdown/v1_0/guard.py src/modules/lcd_levita/v1_7/stream_recovery.py src/modules/lcd_levita/v1_7/motion_renderer.py src/modules/lcd_levita/v1_7/motion_compositor.py \
  src/modules/application_activation/v1_0/server.py src/modules/display_effects/v1_11/model.py src/modules/display_effects/v1_11/catalog.py src/modules/display_effects/v1_11/handoff.py src/modules/display_effects/v1_11/library.py src/modules/display_effects/v1_11/smoke_renderer.py src/modules/display_effects/v1_11/light_bands_renderer.py src/modules/display_effects/v1_11/worker.py src/modules/lcd_media_manager/v1_0/preview_visibility.py src/modules/lcd_media_manager/v1_0/video_preview.py src/modules/lcd_levita/v1_7/media_preview.py src/modules/display_effects/v1_11/base_page.py src/modules/display_effects/v1_11/page.py src/modules/display_effects/v1_11/video_preview.py src/modules/display_settings/v1_0/page.py src/modules/levita_performance/v1_1/policy.py src/modules/section_tabs/v1_0/tabs.py \
  src/modules/responsive_gallery/v1_0/layout.py src/modules/lcd_media_manager/v1_0/model.py src/modules/lcd_media_manager/v1_0/dialog.py src/modules/temperature_history/v1_2/model.py src/modules/temperature_history/v1_2/chart.py src/modules/temperature_history/v1_2/sensors.py src/modules/temperature_history/v1_2/report.py src/modules/temperature_history/v1_2/report_dialog.py src/modules/temperature_history/v1_2/panel.py \
  src/modules/window_chrome/v1_2/chrome.py src/modules/window_placement/v1_5/placement.py src/modules/window_placement/v1_5/confirmation.py src/modules/window_placement/v1_5/kwin_controller.py src/modules/window_placement/v1_5/kwin_bridge.py src/modules/gpu_control/v1_0/overdrive_worker.py src/modules/pc_case_profiles/v1_5/editor_sections.py src/modules/pc_case_profiles/v1_5/catalog.py src/modules/pc_case_profiles/v1_5/profiles.py src/modules/pc_case_profiles/v1_5/controller.py src/modules/rgb_studio/v1_15/design_gallery.py src/modules/rgb_studio/v1_15/studio_panels.py src/modules/rgb_studio/v1_15/ene_start_recovery.py src/modules/rgb_studio/v1_15/shutdown_lighting.py \
  src/modules/rgb_studio/v1_15/slot_routes.py src/modules/rgb_studio/v1_15/slot_route_editor.py \
  src/modules/rgb_studio/v1_15/led_topology.py src/modules/rgb_studio/v1_15/led_topology_store.py src/modules/rgb_studio/v1_15/led_topology_editor.py \
  src/modules/rgb_studio/v1_15/gpu_strip_sampling.py src/modules/rgb_studio/v1_15/gpu_support_sync.py src/modules/rgb_studio/v1_15/gpu_motion_wizard.py src/modules/rgb_studio/v1_15/led_test_isolation.py \
  src/modules/profile_bundle/v1_0/archive.py src/modules/profile_bundle/v1_0/values.py src/modules/profile_bundle/v1_0/controller.py src/modules/profile_bundle/v1_0/worker.py src/modules/profile_bundle/v1_0/restore.py src/modules/profile_bundle/v1_0/legacy_profiles.py \
  src/modules/rgb_studio/v1_15/gpu_lighting.py src/modules/rgb_studio/v1_15/gpu_routing.py src/modules/rgb_studio/v1_15/gpu_led_editor.py src/modules/responsive_startup/v1_0/probe.py src/modules/responsive_startup/v1_0/ownership_probe.py src/modules/responsive_startup/v1_0/controller.py \
  src/modules/ui_themes/v1_0/model.py src/modules/ui_themes/v1_0/light.py src/modules/ui_themes/v1_0/dark.py src/modules/ui_themes/v1_0/registry.py src/modules/ui_themes/v1_0/controller.py \
  src/modules/ui_performance/v1_1/cache.py src/modules/ui_performance/v1_1/maintenance.py src/modules/ui_performance/v1_1/memory.py src/modules/ui_performance/v1_1/controller.py \
  src/modules/ui_performance/v1_1/gallery_preparation.py src/modules/ui_performance/v1_1/thumbnails.py src/modules/ui_performance/v1_1/dynamic_text.py \
  src/modules/pc_case_profiles/v1_5/inline_editor.py src/modules/pc_case_profiles/v1_5/component_editor.py src/modules/rgb_studio/v1_15/stream_reclaim.py src/modules/cooling_state/v1_0/controller.py \
  src/modules/process_runtime/v1_1/controller.py src/modules/process_runtime/v1_1/sensor_worker.py src/modules/process_runtime/v1_1/health.py src/modules/process_runtime/v1_1/resource_metrics.py \
  src/modules/rgb_studio/v1_15/render_plan.py src/modules/application_shutdown/v1_1/journal.py src/modules/application_shutdown/v1_1/diagnostics.py src/modules/application_shutdown/v1_1/watcher.py src/modules/application_shutdown/v1_1/qt_processes.py \
  src/modules/openlinkhub_update/v1_0/policy.py src/modules/openlinkhub_update/v1_0/controller.py src/modules/openlinkhub_update/v1_0/check.py src/modules/openlinkhub_update/v1_0/apply_user_space.py \
  src/modules/wallpaper_engine/v1_3/library.py src/modules/wallpaper_engine/v1_3/onboarding.py src/modules/wallpaper_engine/v1_3/page.py \
  src/localization_catalog.py src/modules/localization/v1_0/de.py src/modules/localization/v1_0/en.py src/modules/localization/v1_0/es.py src/modules/localization/v1_0/fr.py src/modules/localization/v1_0/snapshot_messages.py src/modules/localization/v1_0/shutdown_lighting_messages.py src/modules/localization/v1_0/catalog.py src/modules/localization/v1_0/policy.py src/modules/snapshot_manager/v1_0/model.py src/modules/snapshot_manager/v1_0/probe.py src/modules/snapshot_manager/v1_0/activity_probe.py src/modules/snapshot_manager/v1_0/fullscreen_probe.py src/modules/snapshot_manager/v1_0/helper.py src/modules/snapshot_manager/v1_0/page.py src/privacy_logging.py src/temperature_utils.py src/kraken_cam_streamer.py src/openlinkhub_integration.py \
  src/modules/localization/v1_0/rgb_speed_messages.py src/modules/rgb_studio/v1_15/design_tuning.py \
  src/openrgb_integration.py src/openrgb_sdk.py src/rgb_effects.py src/ui_layout.py src/desktop_designs.py src/desktop_assets.py src/desktop_shell.py \
  docs/security/DESKTOP_SECURITY_AUDIT.md docs/hardware/RGB_STUDIO.md docs/hardware/NATIVE_RGB_SETUP.md docs/security/RGB_SECURITY_AUDIT.md docs/security/SECURITY_SCAN_REPORT.json \
  src/native/openrgb/OHCNativePlugin.cpp src/native/openrgb/ColorCodec.h src/native/openrgb/LatestFrameWorker.h src/native/openrgb/CMakeLists.txt tools/openrgb/msi-761-dirty-zones.patch \
  scripts/build_release.py scripts/backup_release.py scripts/build_release.sh scripts/check_module_registry.py .github/copilot-instructions.md \
  .cursor/hooks.json .cursor/hooks/session-start.py .cursor/hooks/guard-destructive-shell.py AGENTS.md packaging/install.sh packaging/uninstall.sh packaging/install-snapshot-helper.sh packaging/io.github.Frelidon.OpenHardwareControl.snapshot.policy tools/render_snapshot_manager.py \
  docs/ai/CLAUDE.md; do
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
