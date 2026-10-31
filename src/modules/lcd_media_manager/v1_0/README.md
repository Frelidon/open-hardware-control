# LCD media manager 1.0

Stores bounded references to several user-selected folders and individual
supported image/video files, including GIF. It provides editable display aliases, readable
fallback names for TRCC catalog IDs and a non-destructive Qt manager: removing
an entry from OHC never renames, moves or deletes the source.

Shared `preview_visibility.py` clips every enclosing viewport/window;
`video_preview.py` provides local visibility-bound Qt decoding to layout and
effects previews. A hidden preview stops and clears its multimedia source and
last frame so FFmpeg threads and buffers can terminate; the selected path is
kept and reopened only when visible again. This adds no hardware writer or
source mutation.
