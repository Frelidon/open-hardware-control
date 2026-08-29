# Open Hardware Control 3.4.29.6 INTERN

This Levita display-layout update addresses the remaining visible camera/notch coverage and crowded hardware text reported after the 3.4.29.5 compatibility hotfix.

- OHC now creates a full 1600×720 transparent PNG mask with a truly opaque black right-hand bar and applies it through TRCC after loading the selected media. The width is adjustable from 80 to 800 pixels and defaults to 320 pixels on the reference hardware.
- A one-click wide preset combines that 320-pixel bar with a 160-pixel left background shift. Persistent X and Y controls allow further adjustment.
- Image and ordinary video movement is rendered into a content-addressed local cache copy. Imported originals are never overwritten. Complete TRCC layouts and `.zt` files remain untransformed and produce an explicit notice.
- Hardware overlays are clamped outside the selected bar and can be arranged with two-row or vertical presets, then fine-tuned using the existing X, Y and size controls.
- Temperature and percentage formats use `--hide-unit` because their templates already include `°C` or `%`; the duplicate suffix visible on the physical display is removed.
- Command-order regressions require split-mode neutralisation, media load, real mask application and mask positioning to occur before metric elements are added.

This is an INTERNAL test build and is not published automatically.
