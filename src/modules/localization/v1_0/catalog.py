#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Assemble the four independent language modules into the stable catalog API."""

from __future__ import annotations

from . import de, en, es, fr

_LANGUAGE_MODULES = {module.LANGUAGE_CODE: module for module in (de, en, es, fr)}
SUPPORTED_LANGUAGE_CODES = tuple(_LANGUAGE_MODULES)
_GERMAN_MESSAGES = de.UI_MESSAGES
_MESSAGE_IDS = tuple(_GERMAN_MESSAGES)
_GERMAN_SOURCES = tuple(_GERMAN_MESSAGES.values())

if len(_GERMAN_SOURCES) != len(set(_GERMAN_SOURCES)):
    _duplicate_sources = sorted({source for source in _GERMAN_SOURCES if _GERMAN_SOURCES.count(source) > 1})
    raise RuntimeError(
        "The canonical German localization file contains duplicate UI sources: "
        + ", ".join(repr(source) for source in _duplicate_sources[:20])
    )

UI_TRANSLATIONS: dict[str, dict[str, str]] = {}
SETUP_TRANSLATIONS: dict[str, dict[str, str]] = {}
HELP_TOPICS: dict[str, dict[str, dict[str, object]]] = {}
for _code, _module in _LANGUAGE_MODULES.items():
    _missing_ids = sorted(set(_MESSAGE_IDS) - set(_module.UI_MESSAGES))
    _extra_ids = sorted(set(_module.UI_MESSAGES) - set(_MESSAGE_IDS))
    if _missing_ids or _extra_ids:
        raise RuntimeError(
            f"Language {_code!r} has mismatched message IDs; "
            f"missing={_missing_ids}, extra={_extra_ids}"
        )
    UI_TRANSLATIONS[_code] = {
        _GERMAN_MESSAGES[_message_id]: _module.UI_MESSAGES[_message_id]
        for _message_id in _MESSAGE_IDS
    }
    SETUP_TRANSLATIONS[_code] = _module.SETUP_TRANSLATIONS
    HELP_TOPICS[_code] = _module.HELP_TOPICS

GIF_SAFETY_TEXT = de.GIF_SAFETY_TEXT
ABOUT_SUMMARY_TEXT = de.ABOUT_SUMMARY_TEXT
