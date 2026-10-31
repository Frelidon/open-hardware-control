# Open Hardware Control 3.4.29.79 INTERN

Interner Teststand vom 12.09.26. Kein öffentlicher GitHub-Release.

## Behoben und verbessert

- Globale, abschaltbare Seitenübergänge bieten Einblenden, Gleiten und Lichtakzent, ohne Seiten aufzunehmen oder doppelt zu rendern.
- Der neue zentrale SSD-Cache kann auf 0, 0,5, 1, 2 oder 4 GiB begrenzt werden und beschleunigt regenerierbare LCD-/Wallpaper-Kataloge sowie Vorschaubilder. Originale und Hardwaredateien bleiben unverändert.
- ENE-DRAM-Wiederherstellung wartet während schneller Navigation; gewöhnliche versteckte Qt-Hilfsflächen erzeugen keine langen Startdiagnosen mehr.
- Die automatische Gehäuselüfterregelung zeigt den tatsächlich aktiven gespeicherten Zustand vollständig blau und korrigiert die Anzeige bei blockierter Übernahme.
- Der neue viersprachige NCT6687-Assistent führt sicher durch Treiberinstallation, DKMS-Zertifikat, MOK-Import im sichtbaren Terminal, physische Bestätigung im MOK Manager und das Laden nach dem Neustart. OHC empfängt kein Passwort, deaktiviert Secure Boot nicht und startet nicht selbst neu.
- Der lokalisierte Wallpaper-Assistent prüft und installiert nach Bestätigung freie KDE-/Qt-D-Bus-Hilfspakete aus den eingerichteten Paketquellen; der Plugin-Installer bleibt getrennt und SHA256-geprüft.
- Das X minimiert bei aktivem Tray-Modus nun auch bei vorübergehend ungültiger Symbolgeometrie, ohne LCD, RGB oder Kühlung abzuschalten. Ein ausdrückliches Beenden fährt die Hardware geordnet zurück und beendet den Prozess zuverlässig.
- Die Schließfläche reicht mit 48×42 Pixeln bis oben rechts in die Ecke und wird dort nicht mehr vom Größenänderungsrand abgefangen.

## Validierung

- Vollständiger Offscreen-UI-Aufbau ohne Hardwarezugriff.
- Cache-, Sichtbarkeits-, Wallpaper-, Fenster-, Kühlungs-, Sicherheits-, Lokalisierungs- und Paketierungsprüfungen.
- Release-Prüfsummen und externe Zwei-Versionen-Sicherung werden beim Build erzeugt.
