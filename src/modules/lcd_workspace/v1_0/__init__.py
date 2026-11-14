# SPDX-License-Identifier: GPL-3.0-or-later
"""LCD-only UI composition; existing controllers retain settings and devices."""
from .composition import CollectedUi, organize_studio
from .navigation import WorkspaceTabs
from .devices import LcdDeviceShell, LegacyTileGroups
__all__ = ['CollectedUi', 'organize_studio', 'WorkspaceTabs', 'LcdDeviceShell', 'LegacyTileGroups']
