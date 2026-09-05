# LCD Levita module 1.4

Current implementation of the editable Thermalright Levita LCD surface.

- `layout_model.py`: pure validated layer-2 blocks, offsets and persistence format.
- `layout_canvas.py`: Qt-only preview using TRCC centre coordinates, stable background-frame replacement, a right-click request for the integrated side editor and the same configurable inner-right media curve as the generated mask.
- `panel_geometry.py`: pure 1600×720 geometry for independently adjustable top/bottom media radii at the black right notch bar plus the separate outer panel outline.
- `runtime_policy.py`: pure validation for persisted UI/runtime policy values such as the safe split-mode fallback.
- `theme_adapter.py`: read-only TRCC layout adapter and cache-only editable theme staging. It links the selected background video and generated panel mask into the same staged theme so one TRCC `load-theme` connection applies the complete composition.

The imported `config1.dc` is immutable. Runtime cache themes use `trcc.json` and symbolic links to local media; they are not source assets and are never packaged.

Dependencies point inward only: these files may import each other and stable base helpers, but must never import `thermalright_display_ui.py` or `kraken_control.py`.

## Extension rules

1. Add or validate fields in `layout_model.py` without importing Qt.
2. Add mouse interaction only in `layout_canvas.py` and report changes through callbacks. Property editors belong in the surrounding application surface and must not open separate dialog windows.
   TRCC text `x/y` values identify each rendered block's visual centre. Never reinterpret them as a top-left corner. Animated background frames must update the background pixmap in place and must not rebuild draggable layer-2 items.
   The inner media radii belong to the boundary before the black notch bar, not to the physical outer panel corners. Preview and generated hardware mask must call the shared pure geometry.
3. Keep source-theme decoding and cache staging only in `theme_adapter.py`; never write `config1.dc`. Do not split a staged theme's background video or generated mask back into extra USB-attaching CLI commands.
4. Wire the public contract from `thermalright_display_ui.py` without moving backend commands into the model or canvas.
5. Run `tests/test_levita_layout_module_342918.py`, the Thermalright UI/process tests and the full offscreen UI build.
6. Update `MODULE_REGISTRY.md` for every changed responsibility or contract. Bump the module version only for a new/changed public contract; keep exactly one current version folder.
