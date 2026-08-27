---
name: release-preflight
description: Validate a version before any public release action
---

Read `docs/RELEASE_CHECKLIST.md`, verify version/channel consistency, run `./scripts/check_release.sh`, review `git status`, inspect the release notes and confirm no secrets/personal logs/proprietary assets are present. If public publication is intended, require `BUILD_CHANNEL=STABLE` and complete `/backup-before-push` for the exact final commit. Do not create tags/releases unless the user explicitly requested publication.
