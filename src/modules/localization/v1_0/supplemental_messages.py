# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared overflow data kept outside the four bounded language files."""

from .next_version_messages import NEXT_VERSION_MESSAGES
from .snapshot_messages import SNAPSHOT_MESSAGES
from .program_messages import PROGRAM_MESSAGES
from .lifecycle_messages import LIFECYCLE_MESSAGES

SUPPLEMENTAL_MESSAGES = {
    code: {
        **SNAPSHOT_MESSAGES[code],
        **NEXT_VERSION_MESSAGES[code],
        **PROGRAM_MESSAGES[code],
        **LIFECYCLE_MESSAGES[code],
    }
    for code in SNAPSHOT_MESSAGES
}
