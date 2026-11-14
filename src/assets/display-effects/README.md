# OHC display-effect media

This directory contains only original Open Hardware Control media created by
Frelidon for the Thermalright Levita 1600×720 canvas. No Thermalright/TRCC
catalog item, imported user file, manufacturer artwork, stock-library clip or
third-party design component is bundled.

| File prefix | Design | Variants |
|---|---|---:|
| `ohc-light-bands` | Directional travelling light bands | 8 |
| `ohc-prism-drift` | Slowly drifting prism grid | 1 |
| `ohc-twin-wyrm` | Counter-rotating abstract light forms | 1 |
| `ohc-neon-garden` | Growing and fading neon particles | 1 |
| `ohc-circuit-chase` | Energy courier in a circuit maze | 1 |
| `ohc-code-rain` | Original seamless green glyph rain, 12 seconds at 30 source FPS | 1 |

Every video is paired with a local JPEG preview. The source renderers live in
`tools/`; the catalog records Frelidon / Open Hardware Control as creator and
GPL-3.0-or-later as the project license. The release provenance test rejects
unlisted filenames and any bundled Levita layout whose directory is not
project-owned.

`tools/render_code_rain.py` rebuilds Code Rain using NumPy, Pillow, DejaVu Sans
Mono and FFmpeg. It contains no baked-in readings or SignalRGB source/artwork.
Runtime playback uses the existing LCD pipeline, not this development renderer.
