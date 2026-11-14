# Profiles workspace 1.1

`page.py` retains stable-ID selection, refresh and unsaved editor state around the
existing host operations. `composition.py` builds a scrollable library/detail
workspace, clear apply/edit/menu actions and separate profile/complete-package
transfer cards. `layout.py` owns responsive columns and height-for-width summary
reflow. `surfaces.py` paints palette-aware panels and readable expandable section
headers; it does not change the generic disclosure component used elsewhere.
`summary.py` shows only saved values with original curve/swatch artwork and
allowlisted bundled LCD posters. `model.py` remains pure and defensive;
`cards.py` owns pointer/keyboard selection.

The hidden parent-owned table preserves legacy ID-based CRUD, bundle import and
startup contracts. Selection, filters and panel expansion never apply hardware.
No profile schema, persistence key, hardware writer or active-background contract
changes. Live language refresh retains unsaved fields, filter/search, selected ID
and an explicitly new draft with no selected update target. Summary tiles and
expanded section bodies keep their readable minimum height; the outer page
scrolls rather than compressing their content.

Targeted real Qt geometry coverage: `tests/test_profiles_workspace_geometry_3429180.py`
checks three window sizes, four languages and both themes with every panel open.
The full UI construction/localization gate remains mandatory.
