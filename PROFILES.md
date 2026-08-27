# Profile – Version 3.4.16 INTERN

## Kategorien

| Kategorie | Gespeicherte Bereiche |
|---|---|
| Gesamt | Kühlung, CPU-Kurven, Sicherheit, LCD, Uhr, RGB, Design, Hintergrund, Anzeige und Fenstergröße |
| Kühlung | feste Werte oder CPU-Temperaturkurven, Sicherheitsgrenzen und CPU-Profil |
| LCD | aktiver Modus, Bild/GIF, Helligkeit, Ausrichtung, Uhr, Hardwaredesign/-animation und Wiederholungsoptionen |
| RGB | ausgewählte Gerätekacheln, eigene Gerätenamen, frei benannte Gruppen, Gerätezuordnungen, verschiebbare PC-Ansicht mit Koordinaten/Luftstrom/Anschlüssen, unabhängige Gruppeneffekte, Farben, Helligkeit, Geschwindigkeit und Richtung |
| Design | Hell/Dunkel/System, Akzentfarbe, Animation, DPI-Skalierung und Layout |

## Aktionen

- neues Profil speichern
- ausgewähltes eigenes Profil aktualisieren
- Standard- oder eigenes Profil duplizieren
- eigenes Profil umbenennen oder löschen
- einzelnes Profil als JSON exportieren
- ein oder mehrere Profile aus JSON importieren
- Profil automatisch beim Start laden
- alternativ das zuletzt verwendete Profil laden

Beim Desktop-Autostart bleibt das Fenster im Tray. Der LCD-Anteil des Startprofils beginnt erst fünf Sekunden nach Anwendungsstart. Ein manuelles Anwenden eines Profils verwendet weiterhin die normale kurze Geräteverzögerung.

Beim echten Beenden wird unabhängig vom gespeicherten Startprofil zunächst ein laufender GIF-Streamer geschlossen und danach die originale Kraken-Wassertemperaturanzeige gesetzt. Das Profil bleibt gespeichert und wird beim nächsten Start wie vorgesehen wieder geladen. Schließen in den Tray löst diese Rückstellung nicht aus.

Ein RGB-/Gesamtprofil lädt Kachelauswahl, eigene Gerätenamen, Gruppen, Zuordnungen, PC-Ansicht und Effektkonfigurationen des RGB-Studios. Es aktiviert niemals selbstständig die sitzungsweise RGB-Schreibfreigabe und startet keine Hardwareanimation. So kann ein importiertes oder automatisches Startprofil keinen zusätzlichen RGB-Schreibpfad öffnen. Zusätzlich liegt direkt im RGB-Studio Frelidons Thermaltake-360-mm-Aufbau mit Kraken-Radiator, Front-, Rückwand-/Seiten-, Boden- und Hecklüftern sowie den bekannten A1-/A2-/B6-/B7-/SYS-FAN-Anschlussnotizen bereit.

## Sicherheit

Standardprofile sind schreibgeschützt. Alte importierte Wassertemperaturkurven mit Endpunkten um 45–50 °C werden nicht als CPU-Kurven interpretiert, sondern durch sichere CPU-Standardkurven ersetzt. LCD-Profile aus 3.0.5 ohne Modusfeld erkennen GIF- und statische Bilddateien automatisch. Sicherheitsabfragen, Berechtigungsprüfung und serielle Befehlswarteschlange bleiben aktiv.
