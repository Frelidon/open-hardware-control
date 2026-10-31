# Programme 1.0

`model.py` owns the bounded, Qt-free desktop inventory and the validated saved
profile format. `page.py` owns the optional Qt page and runs inventory and
GitHub work in cancellable worker threads.

GitHub access occurs only after an explicit check/download action. The downloader
accepts only a bounded official release plan, includes both source archives,
checks every byte count, creates SHA-256 metadata and atomically publishes a new
version folder without overwriting one. A downloaded AppImage from the inspected
plan can be assigned directly to a selected AppImage profile only after its exact
file and reported size are present.

`install_plan.py` keeps execution separate from discovery. It prepares exact,
confirmed argument arrays for per-user Flatpak and Polkit-mediated Snap installs,
or validates a local AppImage inside the configured base folder before adding
only the current user's execute bit. Ambiguous system packages remain disabled.
