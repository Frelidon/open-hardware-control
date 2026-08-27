# Open Hardware Control 3.2.0 INTERN

Diese interne Version erweitert ausschließlich die optionale KDE-Plasma-Desktopgestaltung. NZXT-/Kraken-,
OpenLinkHub-, LCD-, Pumpen-, Lüfter- und Kurvenlogik bleibt unverändert.

## Neu

- Windows-8- und Windows-8.1-artige Anordnung mit eigener lokaler Kachelübersicht.
- Charms-Leiste an oberer/unterer rechter Bildschirmecke und über `Super+C`.
- Mehrbildschirm-Geometrie sowie `Super+Leertaste` für die Startübersicht.
- KDE-Standard oder freie OHC-Symbole/Mauszeiger: Windowed 11, Orchard und Metro 8.
- Auswählbare Desktop-Backups, Aufbewahrungsgrenze 1–50, Löschen, Export und Import.
- SHA-256-Prüfsummen und strenge Pfad-/Typ-/Größenprüfung für Backup-Archive.
- Automatische Transaktionswiederherstellung; KDE Breeze Light als letzter Notfallfallback.
- Automatisches Paketangebot für QtNetwork/QtDBus auf DNF, APT, Pacman und Zypper.

## Sicherheit und Lizenz

Alle neuen visuellen Dateien werden aus dem mitgelieferten GPL-Quellcode erzeugt oder sind eigene GPL-SVGs.
Originale Microsoft-/Apple-Dateien werden nicht verteilt. TiledScreen und andere Referenzprojekte wurden geprüft,
aber nicht eingebettet. Details stehen in `DESKTOP_SECURITY_AUDIT.md`.

Die Kachelübersicht lädt keine Online-Inhalte. Lokale Programme werden aus `.desktop`-Dateien gelesen und ohne
Shell gestartet; Interpreter-/Shellstarter werden verworfen. Ein Backup-Import führt keine enthaltene Datei aus.

## Später geplant

Windows XT, Windows Vista und Windows 7 sind als zukünftige Designwünsche dokumentiert, gehören aber bewusst
nicht zu 3.2.0.

## Interner Kanal

`BUILD_CHANNEL=INTERN` bleibt aktiv. Diese Version wird nicht automatisch auf GitHub veröffentlicht.
