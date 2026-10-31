# Snapshot Manager 1.0

This module detects Linux snapshot systems without writing, presents bounded
snapshot history and owns the user policy for desktop, game and manual block
modes.

- `model.py` validates policies and applies hysteresis to game/load signals.
- `probe.py` performs bounded read-only OS, filesystem and backend discovery
  outside the GUI process.
- `activity_probe.py` samples CPU/GPU activity and conservative game signals
  outside the GUI process.
- `activity_runtime.py` keeps one low-priority bounded JSON-lines worker alive
  instead of spawning Python for each poll.
- `views.py` owns the restored program selector, resource controls, snapshot
  creation/filter row and graphical deadline controls.
- `process_runtime.py` owns process identity, expiry, helper selection and
  shutdown. Deferred callbacks are bound to the owning Qt object.
- `snapshot_actions.py` owns explicit creation and fixed-root setup, including
  manual-action priority and truthful success reporting after a list failure.
- `helper.py` is installed behind two path-bound Polkit actions. The control
  entry point owns read-only listing and explicitly authorized automation;
  the separate admin entry point owns only fixed Snapper root setup/create
  and validated positive Snapper-number deletion. A persistent automation
  grant can therefore never suppress authentication for a manual write.
- `page.py` builds the Qt surface and persists user choices. It never writes
  snapshot data itself. Each Polkit request logs preparation, process start,
  helper/PID/session context and a categorized success, rejection, timeout or
  process failure without recording passwords.

Automatic activity detection prefers Feral GameMode, Gamescope, an explicit
process list and KDE full-screen state. The optional CPU/GPU heuristic requires
several consecutive high samples and uses a release delay. A running Btrfs
kernel cleanup is throttled rather than killed. The loaded snapshot list can
be atomically exported as JSON metadata. Deletion is a one-row, explicitly
confirmed action and rejects snapshot zero; restore remains explanatory and
there is deliberately no one-click rollback.

When Btrfs and Snapper are present but no configuration exists, a manual
creation request invokes the fixed `setup-root` action through KDE/Polkit and
continues with the requested description after success. OHC-created entries
carry a bounded `[OHC]` description marker; parsing removes it for display and
exposes a source field. The default list remains complete, with optional OHC
or system/other filters.
