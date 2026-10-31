# Platform Support 1.0

Defines the visible desktop platform name and a constrained subprocess contract
for source checkouts and PyInstaller bundles. Bundled child processes may only
dispatch Python helpers located inside the packaged OHC source tree; arbitrary
paths and parent traversal are rejected.
