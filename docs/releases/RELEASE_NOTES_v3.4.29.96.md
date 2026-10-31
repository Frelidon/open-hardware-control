# Open Hardware Control 3.4.29.96 INTERN

- Add Hardware Checker 1.0 as a normal configurable main page. One click runs
  bounded read-only CPU, SMT, CPU virtualization, mainboard, PCIe GPU, NVMe and memory inventory
  outside the GUI process.
- Show explicit pass, warning, failure and unavailable states with actual and
  kernel-reported maximum PCIe generation/lane values. Idle GPU downshifts stay
  warnings until an explicit load test; NVMe lane shortfalls remain visible
  without issuing a storage write benchmark.
- Read RAM manufacturer, part number and configured speed through the fixed
  `pkexec dmidecode --type 17` action. Polkit owns the password prompt; OHC
  neither receives nor stores credentials. Manual model and expected MT/s fields
  cover systems whose firmware does not expose reliable DMI data.
- Add an explicit bounded glmark2 GPU test. It runs for at most twelve seconds,
  samples the boot/default render GPU link while loaded and changes no clock,
  voltage, fan, firmware or BIOS setting. Missing glmark2 disables the action.
- Add pure parser/assessment and read-only-policy regressions plus complete
  German, English, Spanish and French UI text (1,530 messages).

Hardware-free verification covers PCIe 1.0–6.0 normalization, idle-vs-load
classification, static NVMe lane shortfalls, private-field-free Type-17 parsing,
manual RAM targets, bounded process calls and full offscreen UI construction.
The local reference read-only probe detected Ryzen 7 9800X3D SMT as active,
the primary Radeon link at PCIe 5.0 ×16 and one NVMe controller negotiating ×2
against a reported ×4 maximum. These observations are not generalized hardware
compatibility claims. No installation, firmware change, live write or public
publication was performed during development.
