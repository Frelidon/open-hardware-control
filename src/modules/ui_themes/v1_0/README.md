# UI themes 1.0

Keeps each visual design in its own allowlisted module. `light.py` and
`dark.py` provide immutable palette and semantic style tokens; `registry.py`
resolves saved IDs and is the single extension point for future themes. The
controller applies shared selectors from the focused pure `style_base.py` and
`style_controls.py` fragments, so adding a design does not copy
application logic or change hardware behavior.

`studio.py` restores the opaque Studio Light and Studio Black modes. They use
the same theme-owned LCD, GPU, Snapshot and Automation surfaces, but suppress
background animation without overwriting the user's saved background choice.
