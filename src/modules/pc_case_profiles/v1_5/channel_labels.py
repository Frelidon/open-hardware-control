# SPDX-License-Identifier: GPL-3.0-or-later
"""Physical driver-provided connector names, with technical identity in details."""
import re


def channel_caption(host, channel):
    # Prefer the reported board connector over a slot-derived profile alias.
    name = str(channel.display_name)
    match = re.fullmatch(r"System Fan\s*#?\s*(\d+)", name, re.IGNORECASE)
    return f"SYS_FAN{match.group(1)}" if match else name


def channel_details(channel):
    return f"{channel.stable_id} · {channel.name} · PWM {channel.index}"
