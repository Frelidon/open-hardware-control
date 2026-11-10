# Quellcode und vollständige Release-Pakete · 3.4.29.169 STABLE

Jede Veröffentlichung enthält den direkt editierbaren OHC-Programmcode und
einen vollständigen Entwicklerstand. Die historische Einstiegsdatei bleibt
`src/kraken_control.py`; Fachmodule liegen unter `src/modules/`.

## Dateien im Release

- `open_hardware_control_v3_4_29_169.zip`: universelles Benutzerpaket mit
  Python-Quellcode, Ressourcen, Dokumentation und Installer.
- `open-hardware-control_3.4.29.169_all.deb`: Debian/Ubuntu/Linux Mint.
- `open-hardware-control-3.4.29.169-1.noarch.rpm`: Fedora/Nobara.
- `open-hardware-control-3.4.29.169-source.tar.gz`: vollständiger Quellsnapshot
  einschließlich Tests, Buildwerkzeugen und GitHub-Workflows.
- `Entwicklerpaket 3.4.29.169.zip`: vollständiger bearbeitbarer Entwicklerbaum.
- `Open_Hardware_Control_3.4.29.169_LOCAL_AI.gitbundle`: Git-Historie und exakter
  Entwickler-Snapshot zur Offline-Wiederherstellung.
- `SHA256SUMS`: SHA-256 aller erzeugten Release-Dateien; ZIPs enthalten zusätzlich
  `MANIFEST.sha256` für ihre Einzeldateien.

Das Benutzer-ZIP enthält absichtlich keine Entwicklungsordner `tests/` oder
`scripts/`. Entwicklerpaket und Quellarchiv enthalten sie vollständig; der
Builder prüft fehlende Dateien. Das Git-Bundle lässt sich mit
`git bundle verify DATEI` prüfen und mit `git clone DATEI arbeitskopie` öffnen.

## Nativer RGB-Code und externe Komponenten

`src/native/openrgb/` enthält das native OHC-Plugin, einschließlich unabhängiger
Controller-Arbeiter und geprüfter RGB-Kanalkonvertierung.
`tools/openrgb/msi-761-dirty-zones.patch` dokumentiert die gesonderte OpenRGB-
Treiberkorrektur. Die [native Anleitung](../hardware/NATIVE_RGB_SETUP.md) nennt
den exakten getesteten OpenRGB-Commit, Qt-Anforderungen und Bau-/Installationswege.

OpenRGB, TRCC, OpenLinkHub, liquidctl und System-Qt bleiben getrennte
Komponenten; die OHC-Pakete enthalten keine pauschal kompatiblen Fremdbinärdateien.
Lokale Binärstände und persönliche Einstellungen gehören in eine private
zusätzliche Sicherung. Kameradiagnose bleibt ein manuell gestartetes lokales
Werkzeug ohne Netzwerkübertragung; Aufnahmen werden nicht veröffentlicht.

## Wiederherstellbarkeit

`scripts/build_release.sh 3.4.29.169` führt die vollständige Prüfung und den
Paketbau aus. Danach liegt der Release zusätzlich im externen Geschwisterordner
`Open Hardware Control Backup`; die zwei neuesten vollständigen Versionen
bleiben mit eigenen Prüfsummen erhalten. Siehe
[RELEASE_BACKUP_POLICY.md](RELEASE_BACKUP_POLICY.md). Eine weitere unabhängige
lokale Kopie schützt vor versehentlicher Rotation, nicht vor Ausfall derselben
Festplatte. GitHub ergänzt die räumlich getrennte Quell-/Release-Sicherung.
