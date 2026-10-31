# Open Hardware Control 3.4.29.150 INTERN

## NCT6687 setup by Linux distribution

- The guided mainboard driver/MOK assistant now reads `/etc/os-release` and
  shows the detected Linux distribution and DMI mainboard identity.
- Ubuntu, Fedora, and Arch Linux receive separate, fixed dependency commands.
  The previous Fedora `dnf` line is no longer presented on Ubuntu.
- The source clone and `make dkms/install` steps remain shared and follow the
  upstream nct6687d installation path.
- The `nct6683` blacklist and `msi_fan_brute_force=1` module setting are added
  only when DMI identifies an MSI X870-family mainboard. Other boards never
  receive these MSI-specific settings by inference.
- Unknown distributions remain blocked instead of receiving a guessed command.
  Arch users are reminded that `linux-headers` is for the default kernel and
  that `linux-lts` or `linux-zen` requires the matching header package.

## Safety and scope

- Detection is read-only. OHC still does not read passwords, disable Secure
  Boot, reboot automatically, or automate the physical MOK Manager step.
- DKMS certificate generation, MOK import, and module loading retain their
  existing fixed, explicitly confirmed terminal actions.
- The new visible text is available in German, English, Spanish, and French.
- Fedora receives its own existing dependency path; no Fedora runtime or
  installed-system state is changed by building this release.

## Version scope

This is source/release version **3.4.29.150 INTERN**. Building it does not
replace or restart an installed Open Hardware Control instance.
