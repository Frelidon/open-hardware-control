# Display effects 1.11

Original Light Bands remove permanent cold outlines and idle narrow centre
highlights. Eight four-second loops are regenerated from actual 4800×2160
frames, reduced to native 1600×720 and encoded at CRF 10, 24 FPS with two threads.
Previous supersampling requests were clamped by the renderer; bounds now admit
the real source resolution. Foreign-source media and their credits are unchanged.

The four project-owned `ohc_original` designs from the complete .148 release
are retained under their original IDs: Prism Drift, Twin Wyrm Orbit,
Neon Particle Garden, and Circuit Chase. Their packaged video/poster pairs are
byte-identical to the original release; four-language descriptions and the
category selector remain part of the ordinary library. Catalog tests guard
the stable IDs, attribution, assets, and selection without hardware access.

`page.py` owns transient exploration: explicit cards/variants or procedural
controls select an effect; outside click, Escape, Clear selection and page hide
reset to the last confirmed LCD composition. Exact catalog matches mirror the
active design. Preview changes never persist startup/profile state or authorize
hardware. Explicit Apply keeps the protected Levita device path; explicit
Remember writes the same canonical start media/layer-2/motion/FPS state as LCD
Studio and enables its saved autostart. Library language refresh preserves
stable choice IDs.

`lcd_levita/v1_7/media_preview.py` stores pending/confirmed canvas state and
animates selected layout videos independently of card hover. Shared decoder and
all-ancestor clipping are in `lcd_media_manager/v1_0/`; this package preserves
its BundledVideoPreview export. Decoding/composition unloads its decoder source
and frame buffer outside the exposed canvas or while hidden/minimized, with a
20-FPS composition cap. The native
hardware ticker remains independent. Static and unsupported-theme media retain
their existing still preview; firmware hand-off clears the live snapshot.

Tests cover actual Qt playback, viewport hide/resume, immutable browsing/failure
fallback, staging isolation, current four-language details and stable first-open
geometry. Rendered source/native assets and complete video decode are checked.
