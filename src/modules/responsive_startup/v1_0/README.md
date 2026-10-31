# Responsive Startup 1.0

This module keeps the read-only CoolerControl ownership inspection outside the
Qt GUI process. The result remains fail-closed: until a successful probe says
otherwise, OHC treats the mainboard fan path as occupied. Requests are
coalesced and periodic checks can therefore never block painting or input.

The helper performs only the existing bounded `systemctl`/`pgrep` reads. It
does not change a service or write fan values. Explicit owner changes still use
the established confirmation and Polkit paths.
