# Navigation settings 1.0

Adds an explicit settings-page entrance to the existing persisted navigation
visibility model. It does not duplicate page ownership and does not start or
stop hardware. Overview, the sidebar customization control and Help remain
permanent recovery anchors. Settings also remain visible, with a status card but
no visibility switch; both editors and legacy hidden preferences retain that
anchor. Settings can still be reordered. The former `features/enabled` value is refreshed
for backward-compatible diagnostics, while `navigation/hidden` remains the
single visibility source of truth.


The .172 `artwork.py` clips the original square overview logo to rounded corners without distortion, draws original device symbols for category headers/icons and caches navigation icons by palette. Hardware children are fixed and remain attached during reorder/reset.

.175: `sidebar.py:NavigationTree` emits `pageRequested` after a normal pointer
selection finishes, before page-driven tree reflow. Keyboard/programmatic
selection remains immediate; customization retains Qt drag/drop. Regression
uses real press/move/release from LCD, cooling and hardware submenus.
