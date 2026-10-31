# Open Hardware Control 3.4.29.94 INTERN

- Case property menus adapt to 430–860 px and expand toward the diagram.
  Component/fan properties and LED-path settings/preview use columns on wide
  windows or tabs on smaller windows, without an inner scroll area.
- The same live controls retain unsaved values and the last tab across resizing.
  Save/Cancel and topology validation remain outside the subdivisions. Existing
  async cancellation, outside click, Escape and hide guards remain intact.
- Late tab captions update during a live language change.
- GPU/support spinner and comet use broader quintic colour fades. Paired strips
  share the existing clock and virtual spatial sampling footprint, evaluated
  at each header's actual independent count. Fixed 25-Hz target and 3×4 sample
  budget; no physical resize or additional SDK connection.
- PC Case Profiles 1.5 / RGB Studio 1.15; 1,483 atomic DE/EN/ES/FR messages.

Owner .93 logs show accepted saved LCD default/video transfers, without an LCD
failure; they do not prove a continuous hardware soak. GPU JARGB1 is configured
30, support Airgoo B6 12, while B7 fan bank is 24. The owner mentions support
24; preserve existing counts pending clarification. Pairing tests cover both
30/12 and 30/24 without altering saved settings or physical hardware.
Physical optical smoothness still needs observation on the owner's equipment.

Validation: 54 focused tests and extended GPU-route/PWM-menu geometry passed;
DE/FR wide/narrow component forms and wide LED paths rendered and reviewed.
All 697 release tests and full four-language UI/security/privacy/module checks
passed.

Post-build completion: RPM/runtime/developer/source archives and complete-history Git bundle built.
Both ZIP CRCs, all 230 current Python sources in both ZIPs/source/RPM, RPM
metadata/digests and bundle verified. Dist and both external .93/.94 SHA256
manifests passed. Exactly two complete backups remain; .92 rotated under
standing owner approval. DEB unavailable (dpkg-deb missing). This post-build
completion is recorded after packaging; archived docs retain pre-build status.
No installation, live hardware writes or physical optical/LCD soak test.
No firmware/backend changes or publishing.
