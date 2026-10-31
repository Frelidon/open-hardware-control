#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure presentation state for RGB takeover/start/resume controls."""

from __future__ import annotations

from collections.abc import Callable, Iterable


def startup_profile_caption(
    value: object,
    profiles: Iterable[dict[str, object]],
    translator: Callable[[str], str] | None = None,
) -> str:
    """Resolve the persisted startup selector without changing profile state."""

    translate = translator or (lambda text: text)
    selected = str(value or "none")
    if selected == "none":
        return translate("Keins")
    if selected == "last":
        return translate("Zuletzt verwendet")
    for profile in profiles:
        if str(profile.get("id") or "") == selected:
            return str(profile.get("name") or "Profil")[:96]
    return translate("Nicht mehr vorhanden")


def startup_status_summary(
    profile_caption: str,
    *,
    control_enabled: bool,
    control_pending: bool,
    autostart_enabled: bool,
    reclaim_enabled: bool,
    consent_confirmed: bool,
    translator: Callable[[str], str] | None = None,
) -> str:
    """Return one compact, user-readable summary for the prominent panel."""

    translate = translator or (lambda text: text)
    on, off = translate("EIN"), translate("AUS")
    control = translate("STARTET …") if control_pending else on if control_enabled else off
    consent = translate("bestätigt") if consent_confirmed else translate("noch nicht bestätigt")
    return translate(
        "Startprofil: {profile} · Automatik: {autostart} · Wiederaufnahme: {reclaim} · "
        "RGB-Steuerung: {control} ({consent})"
    ).format(
        profile=profile_caption,
        autostart=on if autostart_enabled else off,
        reclaim=on if reclaim_enabled else off,
        control=control,
        consent=consent,
    )
