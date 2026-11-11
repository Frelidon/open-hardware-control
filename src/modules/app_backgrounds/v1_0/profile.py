# SPDX-License-Identifier: GPL-3.0-or-later
"""Active means explicitly applied, independent from the legacy current/edit ID."""
from copy import deepcopy


def mark_applied(host, payload):
    host._applied_profile_background = deepcopy(payload) if isinstance(payload, dict) else None
    sync(host)


def sync(host):
    background = getattr(host, 'background_widget', None)
    tabs = getattr(host, 'tabs', None)
    workspace = getattr(host, 'profile_workspace', None)
    if background is None or tabs is None or workspace is None: return
    page = tabs.currentWidget()
    on_profiles = page is workspace or (page is not None and page.isAncestorOf(workspace))
    background.media_background.set_profile(getattr(host, '_applied_profile_background', None), visible=on_profiles)
