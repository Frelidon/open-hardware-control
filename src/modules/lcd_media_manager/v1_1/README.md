# LCD media manager 1.1

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


`panel.py` owns an embeddable source/media editor with explicit Save, Cancel and
Close, in-place display-name editing and stable path-backed rows. The Levita page
embeds it directly; its former open-manager action toggles the panel instead of
opening a second window. Source removal only edits OHC references/exclusions.
Pass the already indexed `known_media` snapshot (maximum 2,500 paths) so opening
the panel does not recursively scan folders. Adding a new source only changes
the draft; the existing host catalog reload runs after explicit Save. Source
limits remain 32 folders and 500 individual files. `dialog.py` is a small legacy
wrapper around the same panel for compatibility, not a second editor.

Gallery progress is explicitly labeled as preparing cached gallery previews and
shows completed/total counts. It does not report LCD transfer progress or change
playback. The existing visibility-bound preview and single hardware-owner
lifecycle stay unchanged. Focused regression coverage lives in
`tests/test_lcd_inline_manager_3429181.py`.
