# Open Hardware Control 3.4.29.57 INTERN

## Levita-Video bleibt nach einem Taktgeberfehler in Bewegung

- Das neue Log bestätigt um 19:28:55 ein unerwartetes Ende des langfristigen daemonseitigen `display play`-Taktgebers. OHC meldete den Fehler, ließ das aktive Video aber bislang dauerhaft als Standbild stehen.
- Levita-Laufzeitmodul 1.5 startet ausschließlich diesen IPC-Taktgeber nach 1, 2 und 4 Sekunden neu. Nach mindestens 30 Sekunden stabilem Lauf steht das volle Budget erneut zur Verfügung.
- Drei schnelle aufeinanderfolgende Fehler beenden die Wiederholung kontrolliert. Es gibt keine Endlosschleife, keine USB-Neuverbindung und keinen zweiten Hardwarebesitzer.
- Die letzte TRCC-Ausgabe wird auf 1.200 Zeichen begrenzt, von privaten Pfaden und Netzwerkkennungen bereinigt und im Status-/Anwendungslog festgehalten.

## Unveränderte Grenzen

- Der TRCC-Daemon bleibt der einzige Besitzer des Levita-USB-Geräts.
- Anwenden, zehnsekündige Schutzpause, Testmodus, Neuverbindungsbarriere und Firmware-Rückgabe bleiben unverändert.
- Display Effects 1.2 mit fünf freien Hauptdesigns und 20 Farbvarianten aus 3.4.29.56 ist vollständig enthalten.
- Interne Testversion. Kein GitHub-Push, Tag oder öffentliches Release wurde erstellt.
