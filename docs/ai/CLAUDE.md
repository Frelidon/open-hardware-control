# Claude Code entry point

This project uses `AGENTS.md` and the repository memory files as the canonical cross-agent instructions.

Before editing, read:

1. `AGENTS.md`
2. `docs/project/PROJECT_STATUS.md`
3. `docs/project/DECISIONS.md`
4. `docs/project/ARCHITECTURE.md`
5. `docs/hardware/DEVICE_SUPPORT.md`

Do not push, tag or publish without a clean tested worktree and an explicit project-owner request.

Repository layout is fixed (see "Repository layout and README" in `AGENTS.md`): never add files to the repository root; code goes to `src/`, installer/version files to `packaging/`, documents to the matching `docs/` subfolder, policies to `.github/`. Keep `README.md` under 200 lines with one "Neu in" section and at most four history entries; `tests/test_repository_layout_342947.py` enforces this.

Localization is part of every UI change, not a follow-up: update the same stable message ID in `src/modules/localization/v1_0/de.py`, `en.py`, `es.py` and `fr.py`, translate dynamic captions through the localization API, keep logic on stable data IDs rather than display strings, and run the offscreen completeness test. Only technical identifiers, measured values and proper product/design names may remain untranslated.
