# Open Hardware Control 3.4.29.90 INTERN

- LCD first-visit galleries use at most four GUI-thread cards per turn with a
  soft 8-ms budget. Three seconds without app input permit small hidden read-only
  portions; input defers them. Resizing reuses cards. Hidden video/preview timers,
  thumbnail workers and USB playback are not started by prewarm.
  Still cards decode small and reuse source-versioned 176×79 PNG cache entries;
  original assets stay immutable and the existing cache budget remains.
- Precautionary ENE RAM retries isolate selected RAM stable IDs and drain the
  last affected SDK frame; GPU, support and fans keep elapsed effect clocks.
  Reset/stop invalidates the exact lease. Cold initial/manual whole-stream
  reclaim remains ordered; no new transport or higher 25-Hz target.
- One right-side inline case inspector embeds component, ARGB route/count/path/
  test, GPU route and PWM forms. Save commits; outside/Escape/hide cancels.
  Stale inspect reports cannot reopen a dismissed form. Pending single-pixel
  tests retain existing guarded design restoration. No new write authority.
- Cooling startup intent persists separately from actual acquired regulation.
  Fresh owner checks gate both master controls; calibration/backend availability
  remain required. Quiet curves and explicit individual flags are retained.
- Explicit tray Beenden is idempotent and queues Qt exit after isolated cleanup;
  closing X may still hide to tray when configured. Transitions cover only left
  navigation; finished animation objects are deleted. UI Performance 1.1, PC
  Case Profiles 1.3, RGB Studio 1.13, Cooling State 1.0; 1,467 atomic messages.

Internal local RPM/archives only. The full 621-test gate passed, including
four-language UI, security/privacy and module checks. Seven RAM tests passed
after the final drain regression; DE/FR inline editor renders were reviewed.
The builder repeats the complete gate before producing any packages.
Post-build verification: all 622 tests passed. RPM/runtime/developer/source
archives and the complete-history Git bundle were built locally; all 208 current
Python sources, ZIP CRCs, RPM digests/metadata, bundle and Dist/.89/.90 SHA256
checks passed. Exactly two complete backups remain; .88 was rotated under
standing approval. DEB unavailable (no dpkg-deb). This completion paragraph was
added after packaging; packaged notes retain the truthful pre-build test status.
No installation, live hardware, backend/firmware change or public
release. Tests do not prove optical FPS or native KDE tray behavior on the owner’s
desktop; these need an installed-version check.
