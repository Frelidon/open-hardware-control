# Designs & Games 1.1

`catalog.py` owns 15 stable RGB/LCD pair IDs, exact original asset membership
and navigation-order migration. The five existing pair IDs and first 35 RGB
preset indices remain unchanged; ten matched presets are appended.
`rain.py` is the original Qt-free periodic LED data-rain sampler. The existing
RGB engine consumes it; gallery, native and SDK paths still share that engine.
`page.py` and `preview.py` compose a visibility-bound paired preview and explicit
independent RGB/LCD actions. The LCD action preserves the current sensor layer
and uses the existing bundled-media validation and sole-owner apply path.
`size_controls.py` remembers separate `design_hub/zoom/<pair-id>` values
(50–200%, five-percent steps) and a real Matrix glyph variant under
`design_hub/variant/matrix` (100/130/150/200%, default 130%). Moving a slider
changes the preview and its preference only; it never applies a device command.
`scaling.py` creates pure aspect-correct fit/zoom/pad/crop plans matching the
preview. `preparation.py` owns one cancellable, 180-second-bounded ffmpeg process
for explicit LCD apply requests. It uses two encoder threads, bounded output,
private temporary files and atomic cached MP4 completion. A selected pair/size
change, replacement request, leaving the page or shutdown cancels obsolete preparation. Hardware
handoff accepts only the expected fixed source/zoom/cache fingerprint; no
arbitrary derivative path is accepted. The original video is never overwritten.
The page also records the LCD design-intent generation when preparation starts.
A newer LCD intent discards the late result instead of replacing newer output.
`mp4_metadata.py` checks cached MP4 structure without decoding video or starting a
GUI-thread subprocess: at most 1 MiB of metadata, 512 atoms and depth eight, one
H.264 video track with 1600×720 track/sample geometry, valid codec configuration
and a positive duration of at most 35 seconds. Video payloads are skipped by this
structural check; it is not a full frame-decoding claim.
Encoder failures retain at most 2 KiB of detail and use the existing private
error-log/GUI bridge; ordinary cancellation is not logged as an error.
`games.py` prepares editable game/process rules in the existing Automation
Center. It does not claim live telemetry or screen capture support.
`navigation.py` attaches three fixed children to one reorderable section between
RGB and LCD. Existing automation rules, visibility keys and custom ordering
are preserved. `controller.py` connects existing host APIs without importing
the application class or granting hardware permissions.

Matrix Code Rain uses original glyph artwork and a reproducible packaged MP4;
`tools/render_code_rain.py` rebuilds it. It contains no example sensor values.
Pairing is visual coordination, not frame-locked RGB/LCD synchronization.

Ten additional pairs use the existing original Light Bands, five original app
background studies, and four existing original Levita videos. The four small
`assets/design-hub/*.jpg` posters are derived at one second from those bundled
videos; no external media or third-party design source is introduced. Generic
zoom affects Layer 1 only, preserving the existing Layer 2 sensor composition.
Both apply targets retain their own asynchronous status/ownership checks; a
successful request is not a claim that physical hardware has completed it.

Focused coverage includes `tests/test_design_hub_size_3429181.py` and
`tests/test_design_hub_mp4_3429181.py` for cancellation, newer-intent rejection,
hidden-page cleanup, bounded metadata, malformed files and real encoded geometry.
Full-window Qt renders of the hub, case and help views now pass with the case
toolbar ownership fix; source validation passes all 1,732 tests/five subtests and the security/privacy/
module checks. All six packages and both .180/.181 backups pass verification; 464 runtime Python
files and 169 original assets match across formats. User and system .181 copies
are installed with byte-identical Python sources. The installed hub, inline
manager, case, help and profile opening/closing pass isolated native Wayland
checks in both themes. No real design apply/optical device check is inferred.
