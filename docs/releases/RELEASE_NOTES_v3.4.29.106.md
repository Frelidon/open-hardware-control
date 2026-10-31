# Open Hardware Control 3.4.29.106 INTERN

## GPU tuning

The installed `.105` page locked the RX 9070 XT clock inputs because it
looked only for previously saved LACT overrides. LACT 0.10.1 reported active
Overdrive and live RDNA4 ranges in a read-only query. The page now uses
those ranges and current values for the GPU clock offset and maximum memory
clock. The direct maximum GPU clock remains disabled when LACT reports no
range for it. GPU writes still require an explicit short load test, LACT's
automatic rollback, a successful restoration check and a separate permanent
save. This release did not perform a live GPU tuning write.

## Shutdown diagnosis

The supplied log shows a successful Levita firmware release followed by a
shutdown warning because the originally recorded TRCC daemon PID differed
from the current search result. OHC now checks the originally recorded PID
directly. If that daemon has already exited, cleanup succeeds and any other
TRCC instance stays untouched. If it remains alive or cannot be verified,
the warning remains. No user process was stopped during development.

## Verification

The complete release check passed 752 tests plus security, privacy and module
registry checks. Fedora RPM, runtime/developer ZIPs, source archive and the
full-history Local-AI Git bundle were built. The DEB was skipped because
`dpkg-deb` is unavailable on this Fedora host. Runtime/developer ZIP integrity,
the dist SHA-256 manifest, both retained `.105`/`.106` backup manifests and
the changed RPM module paths were verified.
