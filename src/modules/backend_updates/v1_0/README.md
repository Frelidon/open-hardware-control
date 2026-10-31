# Backend-Updates v1.0

Der Bereich **Über** kann lokale Versionen von TRCC Linux, OpenLinkHub, OpenRGB,
LACT, CoolerControl, ckb-next, liquidctl, Wallpaper Engine for KDE, MangoHud,
vkmark, Gamescope und Snapper mit den offiziellen stabilen Release-Metadaten
vergleichen. Installierte Pakete werden über DPKG/APT, RPM oder Pacman nur
gelesen; manuelle Installationen ohne geprüfte Versionsmetadaten werden nicht
fälschlich als fehlend oder aktuell bezeichnet. Keine Hardware-Anwendung wird
für die Versionsprüfung gestartet.

Die optionale Netzwerkprüfung läuft außerhalb des GUI-Prozesses mit höchstens
vier parallelen Leseabfragen, ist zeit-/größenbegrenzt und installiert nichts.
OpenRGB verwendet den offiziellen stabilen Release-Index (Codeberg-Verweise),
CoolerControl die datierten offiziellen Changelog-Releases. Für Projekte ohne
GitHub-Release-Objekte werden ausschließlich stabile Versions-Tags ausgewertet.

OpenLinkHub und das Wallpaper-Plugin behalten ihre vorhandenen, ausdrücklich zu
bestätigenden OHC-Aktualisierungswege. Alle paketverwalteten Backends werden nicht
an DNF/APT vorbei ersetzt; die Übersicht verlinkt stattdessen die offizielle
Release-Seite und nennt den sicheren Weg.

Die ausdrücklich installierten Ubuntu-Backends unter
`/usr/local/lib/open-hardware-control-backends/` können vor den Systemprogrammen verwendet
werden. Der Resolver akzeptiert nur fest definierte root-eigene, nicht über
Gruppe/Andere beschreibbare Dateien und Elternverzeichnisse ohne Symlinkpfade.
Die Versionsanzeige liest das ebenso geschützte `backend-version.json`;
Umgebungsvariablen oder benutzerbeschreibbare Programme schalten diese Präferenz
nicht frei. Fedora und andere Distributionen behalten ihren bisherigen Pfad.
Der CAM-Streamer verwendet ausschließlich den so geprüften liquidctl-Python;
die Qt-Laufzeit und paketverwaltete Python-Bibliotheken werden nicht ersetzt.
