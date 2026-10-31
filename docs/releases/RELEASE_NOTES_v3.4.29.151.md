# Open Hardware Control 3.4.29.151 INTERN

## Robust Ubuntu NCT6687 setup

- Ubuntu package-list refresh and dependency installation are copied as
  separate commands. A failing third-party repository is visible and no longer
  makes the combined line silently skip the install command.
- OHC never disables, removes, or edits a third-party package source. The user
  remains in control of correcting an obsolete source such as the observed CKB
  Next PPA.
- A pre-existing `~/nct6687d` Git checkout is updated with `pull --ff-only`.
  The repository is cloned into that fixed location only when absent; a
  conflicting non-Git directory stops the sequence without overwrite.

## Persistent fan authorization

- The guided NCT6687/MOK flow now includes optional persistent fan-helper
  authorization as step five.
- The grant is bound to the current desktop account and the fixed, bounded
  NCT6687 helper. It persists across OHC package updates and restarts.
- The grant does not authorize APT, DNF, Pacman, arbitrary commands, arbitrary
  filesystem paths, Secure Boot changes, or automatic reboot.
- The wizard reads the actual root-owned rule/status marker and hides the grant
  button once authorization is active.

## Scope

This is source/release version **3.4.29.151 INTERN**. Fedora keeps its existing
DNF path; no Fedora package source or runtime setting is modified.
