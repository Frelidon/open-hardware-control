# Open Hardware Control 3.4.29.93 INTERN

- A single explicitly saved Levita default takes precedence over automatically
  restored profiles. Existing settings remain intact, including disabled or
  missing media; no silent fallback to a different profile video.
- Preview/effect browsing cannot rewrite startup or profile staging. Explicit
  save/apply stages media; an explicit profile load still replaces the shared
  standard with complete motion/FPS settings. Stale startup retries expire.
- Daemon recovery replays the last accepted immutable command sequence using
  the same prepared media, independent of later preview selections.
- Memory recovery no longer restarts every stable video above 1 GiB. Immediate
  emergency at 3 GiB; actual MemAvailable <256 MiB when RSS >=1 GiB; sustained
  growth requires three >=64-MiB increases and >=256 MiB above baseline.
  Memory polling skips apply transactions. Exact process ownership, native
  crash quarantine and the five-minute recovery cooldown remain intact.
- Cache identity includes effective configuration and source artwork/videos.
  LCD Runtime 1.1; 1,482 complete DE/EN/ES/FR messages.

Owner .92 log confirms automatic profile startup and a 1138-MiB daemon reset
at 17:29:58 followed by design recovery at 17:30:08. The physical black flash
was not measured separately. Code identifies competing persistence/preview
paths; logs do not contain media paths sufficient to prove which path caused
this particular video replacement. No permanent hardware-run guarantee; real
emergency daemon/USB reconnection can still briefly interrupt output.
No installation, firmware/backend changes or public publishing.

Validation: all 686 release tests passed, including four-language full UI,
security/privacy and module checks; 13 new regressions cover intent/recovery,
cache identity and memory policy. Packages pending.
External .92/.93 backups and checksums pending. DEB toolchain unavailable.

Post-build completion: RPM/runtime/developer/source archives and complete-history
Git bundle built. Both ZIP CRCs and all 229 current Python files match both ZIPs,
source archive and RPM (four standard RPM shebang adjustments). RPM digests/
metadata, bundle and Dist/.92/.93 SHA256 verified. Exactly two complete external
backups remain; .91 rotated under standing approval. DEB unavailable. Recorded
after packaging; archived documents contain the pre-build verification status.
No installation/live hardware changes or permanent LCD soak test performed.
