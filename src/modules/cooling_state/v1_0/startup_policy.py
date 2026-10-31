# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure policy for a pending legacy NZXT setup versus independent PC startup."""

from __future__ import annotations

from thermalright_cooling import LEVITA_COOLER_KEY


_NZXT_SETUP_PRESETS = frozenset({"quiet", "balanced", "performance", "safe"})


def pending_setup_blocks_profile_start(
    pending: str,
    *,
    ubuntu_runtime: bool,
    thermalright_present: bool,
    nzxt_ready: bool,
    cooling_kind: str,
) -> bool:
    """Retain the NZXT guard except for the confirmed Ubuntu Levita lane.

    The assistant's four fixed presets wait for ``devices_ready`` (NZXT),
    which stays false on Levita. They must not permanently block an explicitly
    selected PC profile there. This decision neither consumes that preset nor
    interprets it as motherboard PWM intent. Unknown pending values and every
    other platform/hardware lane keep their existing blocking behavior.
    """

    if not pending:
        return False
    independent_levita_start = (
        pending in _NZXT_SETUP_PRESETS
        and ubuntu_runtime
        and thermalright_present
        and not nzxt_ready
        and cooling_kind in {"auto", LEVITA_COOLER_KEY}
    )
    return not independent_levita_start
