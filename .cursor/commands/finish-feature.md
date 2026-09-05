---
name: finish-feature
description: Finish a feature with tests and durable handoff memory
---

Review the current diff. Run the relevant tests and fix regressions. Update `PROJECT_STATUS.md` with what is now implemented, `DECISIONS.md` if a durable decision changed, compatibility docs if hardware support changed, and `CHANGELOG.md` for user-visible behavior. If a version package was built, follow `RELEASE_BACKUP_POLICY.md` and verify that the latest two complete backup versions and both SHA256 files are valid. Do not push by default. If the project owner explicitly requested a push, follow the distinct branch-push or public-release authorization rules in `AGENTS.md`; never treat this command's default as an absolute ban after that request. Summarize changed files, tests run, backup verification, unresolved risks and recommended next step.
