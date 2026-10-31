#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Unprivileged OHC entry into the installed TRCC backend on Ubuntu only."""
from __future__ import annotations

from pathlib import Path
import sys


def main(argv: list[str]) -> int | None:
    # A directly executed versioned module needs OHC's installed src root.
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from modules.trcc_backend.v1_0.runtime import SYSTEM_TRCC, configure_backend
    if len(argv) < 2 or argv[1] not in SYSTEM_TRCC:
        print("Unknown TRCC entry point.", file=sys.stderr)
        return 64
    if argv[2:] in (["--version"], ["-V"]):
        # Version verification is metadata-only: no CLI/App construction,
        # sensor probe, logging setup, USB access or daemon auto-start.
        from trcc.__version__ import __version__
        print(f"trcc {__version__}")
        return 0
    from trcc.adapters.system import linux
    from trcc import daemon
    prefix = (sys.executable, str(Path(__file__).resolve()), argv[1])
    configure_backend(linux, daemon, prefix)
    sys.argv = [argv[1], *argv[2:]]
    from trcc._entry import main as trcc_main
    return trcc_main()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
