# Open Hardware Control 3.4.29.3 INTERN

This hotfix addresses the additional startup and long-running cooling errors found in the supplied 3.4.29.1 real-hardware log.

- Mainboard/Thermalright CPU curves now use one authenticated, pipe-bound Polkit helper session instead of launching `pkexec` for every duty change. The helper remains restricted to validated NCT6687 operations and is closed after firmware ownership is restored on orderly exit.
- A helper/authentication failure pauses automatic curve retries for five minutes and reports one actionable message instead of repeatedly opening background dialogs.
- On a Thermalright Levita system with no supported NZXT USB device, startup skips the unnecessary `liquidctl initialize all` command. Mixed NZXT/Thermalright configurations keep the existing NZXT initialization path.
- The round Kraken LCD clock section is hidden while Levita is selected. A stale clock action points to the movable clock in Levita Display Studio instead of reporting that the removed Kraken is disconnected.
- A stable one- or two-device OpenRGB inventory reduction is persisted after 2.5 seconds, so the confirmed seven-to-six hardware change no longer consumes six startup retries. Large temporary cold-start drops remain protected.

The TRCC-not-installed message remains informational: local Levita preview/editing works without TRCC, while real USB display transfer still requires the separately installed backend and explicit test-mode opt-in.

This is an INTERNAL test build and is not published automatically.
