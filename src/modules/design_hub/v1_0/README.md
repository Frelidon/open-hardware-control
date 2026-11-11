# Designs & Games 1.0

`catalog.py` owns stable RGB/LCD pair IDs and navigation-order migration.
`rain.py` is the original Qt-free periodic LED data-rain sampler. The existing
RGB engine consumes it; gallery, native and SDK paths still share that engine.
`page.py` and `preview.py` compose a visibility-bound paired preview and explicit
independent RGB/LCD actions. The LCD action preserves the current sensor layer
and uses the existing bundled-media validation and sole-owner apply path.
`games.py` prepares editable game/process rules in the existing Automation
Center. It does not claim live telemetry or screen capture support.
`navigation.py` attaches three fixed children to one reorderable section between
RGB and LCD. Existing automation rules, visibility keys and custom ordering
are preserved. `controller.py` connects existing host APIs without importing
the application class or granting hardware permissions.

Matrix Code Rain uses original glyph artwork and a reproducible packaged MP4;
`tools/render_code_rain.py` rebuilds it. It contains no example sensor values.
Pairing is visual coordination, not frame-locked RGB/LCD synchronization.
