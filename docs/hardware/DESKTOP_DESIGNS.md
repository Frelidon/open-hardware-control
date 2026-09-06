# Desktop-Designs – Version 3.4.16 INTERN

Der Bereich **System → Desktop-Designs** verändert ausschließlich eine laufende KDE-Plasma-6-Sitzung.
Andere Desktopumgebungen werden erkannt, aber nicht verändert. Das Modul ist von NZXT-, Kraken- und
OpenLinkHub-Zugriffen vollständig getrennt.

Ab Version 3.4.1 ist dieser Bereich ausdrücklich **experimentell und standardmäßig ausgeschaltet**. Menüpunkt,
Navigation und automatisches Paketangebot bleiben unsichtbar, bis „Experimentelle Desktop-Designs im Menü anzeigen“
unter Einstellungen → Programm aktiviert wird.

## Enthaltene Stile

- **Windows-11-Stil:** untere 48-Pixel-Leiste, mittiger Starter-/Programmbereich, Systembereich rechts.
- **macOS-Stil:** obere Systemleiste und zentriertes, automatisch ausblendbares Dock unten.
- **Windows-8-Stil:** untere Desktop-Leiste, lokale bildschirmfüllende Kachelübersicht und Charms-Leiste.
- **Windows-8.1-Stil:** eigenständige Farb-/Leistenvariante derselben sicheren Kachel- und Charms-Grundtechnik.

Die Charms-Leiste öffnet sich an der oberen oder unteren rechten Ecke des jeweiligen Bildschirms sowie über
`Super+C`. `Super+Leertaste` öffnet die Startübersicht. Die Kacheln stammen nur aus lokal installierten
Freedesktop-`.desktop`-Dateien. Interpreter, Shell-`-c`-Befehle, Online-Kacheln, Nachladecode und beliebige
benutzerdefinierte Kachelbefehle werden nicht unterstützt.

## Symbole und Mauszeiger

Zur Auswahl stehen KDE Breeze sowie die originalen OHC-Varianten **Windowed 11**, **Orchard** und **Metro 8**.
Sie werden lokal aus `src/desktop_assets.py` erzeugt. Jede Installation enthält `SOURCE.json` und einen Lizenzhinweis.
Die Pakete enthalten keine Microsoft-/Apple-Logos, Originalzeiger, Schriften, Hintergrundbilder oder sonstige
proprietäre Herstellerbestandteile. Die Namen beschreiben nur die angestrebte Bedienungsrichtung.

Originale Herstellerpakete werden auch nicht automatisch heruntergeladen. Falls sie später separat angeboten
werden, darf dies nur als klar gekennzeichneter externer Benutzerdownload mit eigener Lizenzprüfung geschehen.

## Backups und Notfallrücksetzung

Vor jeder Änderung entsteht ein datiertes Backup aller berührten Plasma-Konfigurationsdateien und der von OHC
verwalteten Autostart-/KWin-Komponenten. In der Oberfläche können Anwender:

- ein bestimmtes Backup auswählen und laden,
- die maximale Aufbewahrungsanzahl zwischen 1 und 50 einstellen,
- einzelne Backups löschen,
- ein Backup als ZIP mit SHA-256-Dateiliste exportieren,
- ein exportiertes Backup wieder importieren.

Der Import akzeptiert nur bekannte Konfigurationspfade, begrenzt Datei- und Gesamtgröße, weist absolute Pfade,
`..`, symbolische Links und unbekannte Dateien ab und verifiziert jede SHA-256-Prüfsumme.

Vor dem Anwenden wird zusätzlich ein Transaktionsmarker geschrieben. Wird Open Hardware Control oder Plasma
währenddessen beendet, stellt der nächste Start automatisch das zugehörige Backup wieder her. Ist auch dieses
beschädigt, werden KDE Breeze Light, Breeze-Symbole, Breeze-Mauszeiger, eine normale untere Leiste und die
Standard-Fensterschaltflächen gesetzt.

## Optionale KDE-/PySide-Werkzeuge

Fehlende Komponenten werden nach Bestätigung ausschließlich aus bereits eingerichteten Paketquellen installiert.

| Paketfamilie | `kwriteconfig6` | Qt-6-`qdbus` | Kachel-/Charms-PySide |
|---|---|---|---|
| Fedora/Nobara – DNF | `kf6-kconfig` | `qt6-qttools` | `python3-pyside6` |
| Debian/Ubuntu/Mint – APT | `libkf6config-bin` | `qdbus-qt6` | `python3-pyside6.qtnetwork`, `python3-pyside6.qtdbus` |
| Arch/Manjaro/EndeavourOS – Pacman | `kconfig` | `qt6-tools` | `pyside6` |
| openSUSE – Zypper | `kf6-kconfig` | `qt6-tools-qdbus` | `python3-pyside6` |

Ohne die optionalen Desktop-Werkzeuge bleiben sämtliche Hardwarefunktionen verfügbar.
