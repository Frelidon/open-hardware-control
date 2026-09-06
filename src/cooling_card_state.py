#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Frelidon contributors
"""Pure state helpers for the single-expanded chassis-fan card UI."""

from __future__ import annotations

from collections.abc import Iterable


def normalize_expanded_channel(expanded_channel_id: object, available_channel_ids: Iterable[object]) -> str:
    """Keep an expanded id only while the corresponding channel still exists."""
    expanded = str(expanded_channel_id or "")
    available = {str(channel_id) for channel_id in available_channel_ids}
    return expanded if expanded in available else ""


def toggle_expanded_channel(
    expanded_channel_id: object,
    requested_channel_id: object,
    available_channel_ids: Iterable[object],
) -> str:
    """Expand one requested card, or collapse it when it is already open."""
    requested = str(requested_channel_id or "")
    available = {str(channel_id) for channel_id in available_channel_ids}
    current = normalize_expanded_channel(expanded_channel_id, available)
    if requested not in available:
        return current
    return "" if requested == current else requested
