# Open Hardware Control 3.4.29.103 INTERN

## LACT setup recovery

LACT 0.10.1 has no `lact --version` option. OHC now verifies the installed
RPM, Pacman or DEB package version before GPU writes. The optional installer
uses package metadata as well; if a previous run installed LACT successfully
but stopped before daemon activation, the confirmed installation resumes by
starting `lactd` without re-enabling the package source. No GPU tuning is
performed by the installer.

On the reference Fedora/Nobara system, the owner-approved LACT installation
was completed: the 0.10.1-1 package and active/enabled daemon are present,
the local socket is accessible and read-only discovery reports two GPUs.
GPU tuning and fan handoff have not been tested on live hardware.

## Main-screen placement

The owner's `.102` startup log requested DP-1, the current KDE primary
screen, yet the window appeared on the left output. On Wayland a requested
global Qt position can be stale after KWin maps the actual surface. The
short, bounded post-mapping check now prefers the mapped QWindow screen and
checks the output a second time after startup, correcting a mismatch and
logging both observations. A deliberately saved non-primary choice remains
respected. Real KWin placement after installing this build needs visual
verification; a synthetic regression cannot prove compositor behavior.

## Verification status

The complete release gate passed 739 tests, including package-version and
window-mapping regressions, as well as security/privacy and module checks.
Package build and external two-version backup are still required before this
internal version is ready. No GPU tuning values were changed.
