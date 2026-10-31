# Open Hardware Control 3.4.29.108 INTERN

## GPU benchmark setup

The installed `.107` log shows that both attempted GPU tuning previews
stopped before applying a LACT configuration because neither vkmark nor
glmark2 was installed. The subsequent LACT reinstall was unnecessary and
could not supply the missing benchmark.

The Tuning tab now places **vkmark installieren** beside the short-test
button. Clicking the short test without a load helper offers the same
confirmed installer directly. On Fedora, the helper requests vkmark from
configured distribution repositories; no Phoronix Test Suite is required.
Installation and its result are shown in both GPU tabs. The tuning preview
starts only after another explicit click. GPU clocks, power and fan values
are never written by the package installation path.

## Verification

Simulated GPU and package-helper regression checks exercise the missing
benchmark path without LACT writes. Full release results are documented in
the project status. No benchmark, package installation or GPU tuning write
was run on the owner's machine while preparing this version.
