# Application backgrounds 1.0

Six fixed local videos: original code rain and five offline-rendered studies.
`tools/render_app_backgrounds.py` produces periodic 1280×720/24 FPS/12-s MP4s;
`tools/render_code_rain.py` supplies the Matrix sizes at 1600×720/30 FPS/12 s.
No audio, web fetch, third-party effect assets or hardware writes.

`MediaBackground` composes inside the existing CPU RGB32 background, preserving
palette/intensity and aspect ratio. One decoder unloads its source while hidden,
minimized, disabled or paused inactive. User frame-rate limits presentation;
render buffers stay <=960×540. Invalid media falls back to the palette.
Local profile media must be regular files <=256 MiB with supported suffixes;
image dimensions are checked before decoding. No I/O in paint.

`profile.py` snapshots a successfully requested/applied profile independently of
legacy last-edited/current IDs. Selection, creation and duplication cannot change
the active backdrop. Only Profiles exposes that snapshot (LCD media preferred,
otherwise saved RGB config); leaving restores the configured app theme without
writing settings. After restart a snapshot appears only once a startup profile
is actually applied. Theme/global animation-disable and inactivity policies win.
