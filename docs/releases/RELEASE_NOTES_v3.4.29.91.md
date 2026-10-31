# Open Hardware Control 3.4.29.91 INTERN

- First staged Process Runtime: separate Qt-free read-only sensor process,
  one in-flight request, three-second timeout, bounded 1/2/4-second restarts and
  2.5-second freshness. GUI/cooling/history/LCD profile metrics share snapshots;
  stale values remain unavailable and existing firmware/watchdog protection stays.
- Pure RGB calculations run in the existing SDK worker from bounded serialized
  plans. Preserve all effects, elapsed time, GPU/support sync, path declarations,
  25-Hz target and sole-writer authorization. No second USB owner.
- Side component labels open the existing inline editor on one click; no move
  is committed by label activation. Renderer and clicks share placement geometry.
- Exit requests, every phase and Qt-loop return go to private shutdown.jsonl.
  A delayed one-shot shutdown-stacks.log and a read-only observer (maximum 90 s)
  diagnose blocked exit. Remaining window-owned QProcesses receive bounded stop
  after hardware restoration; explicit quit calls Qt exit directly. Close-to-tray
  stays distinct; external TRCC/OpenLinkHub/other-app services are not terminated.
- In-page System Status: actual sensor availability/age, retries and owned
  per-process CPU/RSS. Process health is not physical readback or optical FPS.
  Process Runtime 1.0, Application Shutdown 1.1, PC Case Profiles 1.4,
  RGB Studio 1.14; 1,476 complete DE/EN/ES/FR messages.

First staged migration, not an autonomous fan-control daemon. Full core/cooling
service separation, further LCD migration and measured resource-budget tuning
remain later hardware-validated stages. Existing TRCC/renderer/thumbnail processes
are retained. No installation, firmware or public-release action. Owner desktop
shutdown and physical smoothness need an installed check.

Post-build verification: all 656 tests passed; full four-language UI,
security/privacy and module checks passed. Both ZIP CRCs, all 218 Python sources,
RPM digests/metadata and complete-history bundle verified. Dist/.90/.91 SHA256
passed; exactly two complete backups remain and .89 was rotated under standing
approval. DE/FR health renders reviewed. DEB unavailable (no dpkg-deb). This
completion paragraph was added after packaging; archived notes retain the
truthful pre-build status.
