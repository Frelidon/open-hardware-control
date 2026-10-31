# Open Hardware Control 3.4.29.99 INTERN

- Display Effects now writes its selected validated video to the same canonical
  Levita startup state as “Save current selection as startup design” in LCD
  Studio. The matching layer-2 design, motion choice and FPS values are stored
  together and automatic Levita startup is enabled.
- Minimize-to-tray and Close are separate operations. The saved tray checkbox
  applies to minimization; Close from the title bar or taskbar always runs the
  ordered hardware hand-back, owned-process cleanup and Qt exit.
- Hidden LCD and Display Effects video previews stop and unload their Qt/FFmpeg
  source, releasing decoder threads and frame buffers. Reopening a visible page
  reloads only its selected local source.
- A debounced idle reclaim after page switches or tray minimization collects
  Python cycles and, where glibc provides it, returns fully free heap pages to
  Linux. There is no periodic cleanup loop and no original media or active
  hardware file is moved to the SSD cache.
- The supplied `.98` trace was diagnosed against the live system: window Close
  intentionally entered tray mode; the main process held two decoders for the
  same video. Logs were already bounded to 4 MiB/30,000 entries and persisted
  to disk, so they were not the source of the measured memory usage.

No installation, GitHub push, tag or public release is performed by this build.
