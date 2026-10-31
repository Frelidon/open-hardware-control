# Profile Bundle 1.0

Explicit local ZIP packages contain a typed QSettings snapshot, all saved user
profiles, a current full profile, LCD-profile store and referenced local media/
theme files. Existing single-profile JSON export/import remains available.
`archive.py` owns bounded, atomic archive I/O and strict hash/path/link checks;
`values.py` preserves Qt value types and rewrites portable asset references.
`controller.py` owns Qt dialogs and a bounded background `QProcess`; its
`worker.py` performs file traversal/copy/hash work without Qt GUI or hardware.
Imports accept only the same asset extensions as exports and reject conflicting
file/directory paths before creating the private staging directory.
`restore.py` applies a confirmed staged import before startup settings are read,
keeps rollback metadata and disables imported hardware automation/calibration
until the user confirms it on the actual machine. No installation, service,
driver, external app settings, logs or arbitrary executable is exported.
Private packages contain personal file references; they are not public releases.
