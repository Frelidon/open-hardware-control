# Open Hardware Control — Agent entry point

The complete, authoritative agent instructions live in [docs/ai/AGENTS.md](docs/ai/AGENTS.md). Read that file first, then follow its mandatory startup sequence (`docs/project/PROJECT_STATUS.md`, `docs/project/MODULE_REGISTRY.md`, `docs/ai/AI_DEVELOPMENT_GUIDE.md`, …).

Repository layout: application sources in `src/`, packaging and installer files in `packaging/`, documentation in `docs/`, tests in `tests/`, release tooling in `scripts/`.

**Never add files or folders to this root.** The layout table and the short-README rules in `docs/ai/AGENTS.md` are mandatory and enforced by `tests/test_repository_layout_342947.py`.
