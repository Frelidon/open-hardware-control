# Open Hardware Control 3.4.29.73 INTERN

Interner Linux-Teststand vom 12. September 2026. Kein GitHub-Tag und kein öffentliches Release.

## Originalanzeige des Kühlers

- Die Tray-Aktion ist nun modellabhängig. Bei Thermalright Levita beendet sie den OHC-Stream, trennt den vorhandenen TRCC-Daemon und gibt das Display an die eingebaute Thermalright-Firmware zurück. Bei NZXT Kraken bleibt die vorhandene Flüssigkeitstemperaturanzeige erhalten.
- Auf der LCD-Hauptseite und unter Display-Effekte gibt es jeweils einen gut sichtbaren Knopf zum Wiederherstellen der Thermalright-Originalanzeige.
- Die Rückgabe verwendet ausschließlich den bestehenden einzelnen TRCC-Besitzer. Im Testmodus werden keine USB-Daten gesendet; eine bereits getrennte Verbindung wird sicher als erreichtes Ziel behandelt.
- Das gespeicherte Startprofil bleibt unverändert. Es kann später wieder über **Profile → Ausgewähltes Profil aktualisieren** angewendet werden.

## Tray und Programmende

- **Beenden** im Tray setzt nun zuerst einen ausdrücklichen Endzustand. Dadurch greift die normale Funktion „Schließen minimiert ins Tray“ nicht mehr dazwischen und ein Klick beendet das Programm.
- Der vorhandene Aufräum- und Firmware-Schutzpfad wird weiterhin genau einmal ausgeführt.

## Schärfere OHC-Lichtbänder

- Alle acht eigenen Richtungsvarianten werden deterministisch in 3200×1440 erzeugt, hochwertig auf die native Levita-Auflösung 1600×720 verkleinert und mit einer höheren H.264-Qualität gespeichert.
- Die Displayauflösung und sichere 15-FPS-Voreinstellung bleiben unverändert. Die Verbesserung betrifft Kanten, Leuchtkerne und Kompressionsartefakte.

## Prüfgrenze

- Deutsch, Englisch, Spanisch und Französisch enthalten dieselben 1.277 stabilen Nachrichten-IDs.
- Die Firmware-Rückgabe und die optische Verbesserung sind automatisiert prüfbar; die sichtbare Reaktion des echten Levita-Displays muss am Referenzrechner bestätigt werden.
