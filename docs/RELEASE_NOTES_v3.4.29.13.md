# Open Hardware Control 3.4.29.13 INTERN

## Levita-Designbibliothek

- Ein einmal importierter eigener Designordner bleibt unabhängig vom TRCC-Standardkatalog gespeichert.
- Der Haken „Eigenen Designordner einbeziehen“ blendet ihn nur in OHC aus. Dateien und Verzeichnisse auf der Festplatte bleiben unverändert.
- „Gemerkten Ordner anzeigen“ aktiviert ihn ohne neuen Dateidialog und stellt die letzte gültige Auswahl wieder her.
- Ebene 1 enthält standardmäßig Bilder und Videos; vollständige Themes mit `config1.dc`, Uhrzeit und Hardwarewerten liegen in Ebene 2.
- Zwei ausdrückliche Pfeilaktionen verschieben ein komplettes Theme bei Bedarf zwischen beiden Ebenen. Diese Ausnahme wird gespeichert.
- Videokarten zeigen einen lokal erzeugten ersten Frame und animieren beim Darüberfahren bis zu vier gecachte Vorschauframes.

## Levita-Steuerung und USB-Stabilität

- „Design anpassen“ und „Design direkt anwenden“ stehen im Kopf des Display-Studios.
- Helligkeit von 0 bis 100 Prozent und Ausrichtung mit 0, 90, 180 oder 270 Grad verwenden die echten TRCC-Linux-Befehle `set-brightness` und `set-orientation`; Kraken-Regler werden nicht wiederverwendet.
- Auf einem Thermalright-System ohne Kraken bleibt das Levita-Studio oben, während Kraken-spezifische Displaykarten ans Ende wandern.
- Designwechsel senden `SIGINT` an den laufenden TRCC-Renderer, warten auf die USB-Freigabe und starten erst danach die neue Übertragung.
- Gleichzeitige Levita-Befehle werden abgewiesen statt einen laufenden USB-Befehl zu beenden. Ein nachgewiesener Bulk-LCD-Handshake-Timeout (`Errno 110`) wird nach einer Ruhepause genau einmal wiederholt.

## Kühlung

- Leise, Ausbalanciert und Leistung stehen bei den Gehäuselüftern oben an derselben Stelle wie die CPU-Schnellprofile.
- „Automatische Regelung“ bleibt eine getrennte Aktion. Eine Profilvorlage verändert weiterhin weder die physische Kalibrierung noch die Aktivierung eines PWM-Kanals.

## Sicherheit und Prüfung

- Testmodus bleibt standardmäßig aktiv und verhindert USB-Schreibzugriffe.
- Importierte Medien sowie Benutzerordner werden weder kopiert, gelöscht noch überschrieben.
- Offscreen-UI-, Bibliotheks-, Ebenen-, Befehlsgrenzen-, Lüfter- und Modularisierungstests decken die neuen Pfade ohne Hardwarezugriff ab.
