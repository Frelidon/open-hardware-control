# LCD workspace 1.0

Composes the existing LCD controls into Library, Composition and Display
operation workspaces, with a separate device selector for Levita and the Kraken
compatibility controls. No controls are cloned and selecting a workspace or
device never applies a design, changes the hardware owner or persists a draft.

`composition.py` collects legacy rows into owned widgets before reparenting,
then places their existing controls into shared surfaces and section cards.
The single design Apply action, selection summary and preview/USB mode status
stay visible across the Levita workspaces. Sources, gallery preparation and the
two design galleries belong to Library; the unchanged logical 880×396 canvas,
Layer 2 editor, geometry and overlays belong to Composition. Display operation
contains startup, backend and maintenance controls. Firmware return remains
available as an explicit maintenance action. Complex compatibility forms and
the fixed canvas use bounded viewports rather than widening the whole page.

`navigation.py` measures the current workspace only, so a hidden large editor
does not reserve its height. `devices.py` keeps the existing LCD tile order,
reset, prioritization and visibility API through `LegacyTileGroups`. Saved tile
keys are retained; automatic detection can choose the preferred family until
the user explicitly chooses another. These are UI operations only.

Existing source import/save, design aliases, favorite and layer assignment,
geometry settings, Layer 2 drafts and offsets, rendering, original-media
protection, test mode and the exclusive hardware writer remain owned by the
existing Levita/Kraken modules. A hidden Composition canvas releases the
existing visibility-bound local decoder; gallery and hover work pause outside
Library. The separate Display effects page stays reachable from the Apply bar.
Its Layer 2 edit link selects Levita Composition directly without applying or
saving. Kraken GIF previews and the floating round preview pause or hide when
their inner Composition workspace/device is hidden; physical LCD playback is
independent.

`lcd_workspace_messages.py` supplies 15 atomic captions (including the two device-family names) in DE/EN/ES/FR.
`tests/test_lcd_workspace_3429182.py` covers the adapter contract, draft and
selection preservation, hidden playback and full-window native Qt ownership
and narrow geometry with isolated settings and hardware IO disabled.
