# OpenLinkHub update integration 1.0

This module checks the fixed official GitHub releases endpoint with a bounded
response and compares the latest tag with the locally installed package.
Automatic updates are offered only for an existing RPM/DEB installation and
use a fixed `pkexec` + DNF/APT argument list from already configured package
sources. No shell, downloaded installer script or arbitrary package name is
accepted.

The package route is selected from `/etc/os-release` before probing an installed
RPM or DEB. A foreign `dnf` binary on Ubuntu or an `apt-get` binary on Fedora
cannot change the update plan; the established native package commands remain
unchanged. Conventional user-service updates stay independent of this choice.

`controller.py` contains the page builder and asynchronous confirmation flow;
the large compatibility orchestrator only mixes in that bounded UI contract.

OpenLinkHub's web dashboard is bundled with OpenLinkHub and is therefore
updated with the same package. Manual and immutable/user-space installations
are distinguished from package installations. A conventional user service
inside the current home directory can use the upstream amd64 archive only when
GitHub publishes its SHA-256 digest. OHC extracts it without links or path
traversal, stops the user service, keeps the previous installation as a
recoverable sibling backup, preserves configuration/database content and
rolls back automatically if the new service does not start.


The .172 UI extracts `device_ui.py`, uses responsive mouse columns with a separate drawing/table, and adds `mouse_ui.py` and `mouse_profiles.py` for reported stages and official user-profile actions. OpenLinkHub .9.4 has no HTTP startup-stage endpoint: a confirmed user-service action changes only Profile in its verified existing JSON with backup/stop/restart/rollback. `health.py` verifies PID/executable and loopback API; `stage_integrity.py` detects stale or damaged stages before stopping anything. daemon-reload takes no service argument. Ubuntu/Fedora package plans remain separate.


The .174 `startup_defaults.py` keeps an independent private per-profile startup
stage, since upstream ModifyDpi also persists the currently active stage.
`before_start.py` runs through an optional, marked user ExecStartPre only after
an explicit Save. It checks the inactive/start-pre window and competing system
ownership, validates existing profile identity/path and changes only Profile.
The explicit state path works independently of the service environment. The
native preference removes the rule. Rollback includes profile, rule and drop-in;
a missing OHC helper never blocks the backend. Future module-folder migrations
must retarget already marked drop-ins while preserving rules, just like the
existing recognized autostart migration; never create a hook without opt-in.
