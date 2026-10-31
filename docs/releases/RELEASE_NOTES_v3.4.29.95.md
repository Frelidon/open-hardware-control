# Open Hardware Control 3.4.29.95 INTERN

- Remove permanent grey Light Band edges and narrow idle centre highlights;
  use proportional continuous glow. Regenerate eight loops from real 4800×2160
  source frames to native 1600×720, CRF 10, 24 FPS, four seconds. The previous
  renderer clamped the requested supersampling and changed its aspect ratio.
- Selected layout videos animate without hovering, while the preview is exposed.
  Both local decoders stop outside all enclosing scroll viewports or on hide/
  minimize; previews are capped at 20 FPS and never stop the hardware ticker.
- Effect exploration is transient. Clear/outside click/Escape/page hide restores
  the last successfully confirmed media/layers. Active catalog effects mirror
  exact validated paths. No effect choice disables applying/staging instead of
  sending an unrelated default smoke. Saved start/profile intent stays intact.
- Separate pending/confirmed composition copies withstand browsing/failed applies.
  Firmware hand-off clears the old OHC snapshot; no physical display readback.
- Reserve gallery row height and reuse unchanged/empty canvas layers; current
  design details and variant/category labels refresh correctly in all languages.
- Display Effects 1.11; LCD 1.7 and shared LCD Media Manager 1.0 preview helpers;
  1,483 complete DE/EN/ES/FR messages, reusing existing Clear selection caption.

Owner .94 log confirms animated LCD startup and new quintic GPU/support plans.
It contains no geometry trace proving the reported first-open LCD-Quantum jolt.
Hardware-free regressions cover actual Qt playback, stable first-open geometry,
viewport pause/resume, transient selection/confirmed fallback and staging safety.
All eight videos passed complete FFmpeg decode/native geometry/FPS/duration.
DE/FR live previews rendered/reviewed; full four-language UI coverage passed.
Late tab/animation callbacks are QObject-context bound; deleted hosts are guarded
and covered by a real Qt regression. Synthetic SDK tests clear external ownership.
All 701 release tests and full four-language UI/security/privacy/module checks
passed. RPM/runtime/developer/source archives and full-history Git bundle built.
Both ZIP CRCs, all 233 current Python sources and all 16 regenerated band media
files in ZIP/source/RPM verified; four standard RPM shebang adaptations only.
RPM metadata/digests, complete-history bundle, dist and both external .94/.95
SHA256 manifests passed. Exactly two complete backups remain; .93 rotated under
standing owner approval. DEB unavailable (dpkg-deb missing).
Completion recorded after packaging; archived docs retain pre-build status.
Physical LCD duration/optical verification and display readback not performed.
No installation, firmware/backend changes, live hardware writes or publishing.
