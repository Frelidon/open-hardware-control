# Profile – Version 3.4.29.180 INTERN

## Profilbibliothek und gespeicherte Bereiche

Die Bibliothek lässt sich durchsuchen und nach allen, eigenen oder Standardprofilen
filtern. Die Profilkarte daneben zeigt nur tatsächlich gespeicherte Bereiche und
Werte, mit passenden Symbolen, Farbproben, Kurven oder bekannten LCD-Vorschaubildern.
Auswählen, Filtern und Aufklappen verändert keine Geräte. Erst „Profil anwenden“
lädt das Profil über die bestehenden geschützten Wege.

„Bearbeiten“ öffnet den Editor innerhalb der Profilkarte. Technische Details und
„Import, Export & Sicherung“ besitzen eigene große Bereichsköpfe. Auch wenn alle
Bereiche offen sind, bleiben Werte lesbar; die Seite lässt sich entsprechend
scrollen. Einzelne JSON-Profile und die vollständige Sicherung stehen getrennt.
Weitere Aktionen wie Duplizieren, Umbenennen und Löschen befinden sich im Menü.
Standardprofile bleiben schreibgeschützt; Duplizieren erzeugt eine eigene Kopie.
Ein neuer Entwurf und seine leere Auswahl bleiben beim Sprachwechsel erhalten.

Auf dieser Seite kann das ausdrücklich angewendete Profil sein LCD-Basismedium
oder den gespeicherten RGB-Effekt als Hintergrund zeigen. Das bloße Auswählen
oder Bearbeiten aktiviert diesen Hintergrund nicht; andere Seiten verwenden
wieder die globale Hintergrundwahl. Globale Animations- und Sichtbarkeitsregeln
gelten weiterhin.

## Vollständiges Komplettpaket

Unter „Profile“ zusätzlich „Komplettpaket exportieren“ wählen. Das private ZIP
enthält alle App-Einstellungen, eigene Profile plus aktuelles Gesamtprofil,
Gehäusepositionen/Skalierung, RGB-/PWM-Zuordnungen, manuelle LED-Anzahl,
physische LED-Verläufe, eigene Lüfterhersteller/-modelle, den LCD-Profilspeicher
und zugehörige lokale Medien, Theme-Dateien und Schriftarten. Unterordner und
Pfadverweise innerhalb JSON-Themes werden beim Import auf die Kopien umgesetzt.
Fehlende Medien werden gemeldet. Der bisherige einzelne JSON-Export bleibt.

„Komplettpaket importieren“ prüft ZIP-Pfade, Werttypen, Größen und SHA256,
kopiert ausschließlich in einen neuen privaten App-Unterordner und übernimmt
Einstellungen nach Bestätigung erst beim nächsten Start. Eine Rückfallkopie
unter `profile-imports/before-restore-*` enthält vorherige Einstellungen und
Profile. Hardwareautomatik, aktive CPU-Regelung und PWM-Kalibrierung werden nicht
als Gerätefreigabe übernommen: am tatsächlichen PC erneut bestätigen/anwenden.
Konfigurationen und Kurven bleiben im Gesamtprofil zur manuellen Anwendung.

Kopieren und Prüfen laufen im eigenen Hintergrundprozess. Grenzen: maximal
8.192 ZIP-Einträge, 1 GiB je Datei, 4 GiB insgesamt, 8 MiB Metadaten. Keine
rekursive Home-/System-Sicherung, Logs, ausführbaren Programme, Treiber,
Dienste oder Einstellungen fremder Apps. Das ZIP enthält persönliche
Dateipfade und private Medien; nur bewusst weitergeben, nicht öffentlich
hochladen. Rechte an eigenen importierten Medien bleiben beim Nutzer.

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

Ein RGB-/Gesamtprofil lädt Kachelauswahl, eigene Gerätenamen, Gruppen,
Zuordnungen, PC-Ansicht und Effektkonfigurationen des RGB-Studios. Erst nachdem
der Nutzer OHC einmal ausdrücklich als RGB-Steuerung bestätigt hat, ist die
Startprofil-Automatik standardmäßig aktiv. Das gespeicherte Startprofil darf
danach die neue Sitzung anfordern, umgeht aber weder Besitzsperre noch
Fremdprozessprüfung; bei Konflikt bleibt die Hardware unangetastet. Zusätzlich
liegt direkt im RGB-Studio Frelidons Thermaltake-360-mm-Aufbau mit
Kraken-Radiator, Front-, Rückwand-/Seiten-, Boden- und Hecklüftern sowie den
bekannten A1-/A2-/B6-/B7-/SYS-FAN-Anschlussnotizen bereit.

## Sicherheit

Standardprofile sind schreibgeschützt. Alte importierte Wassertemperaturkurven mit Endpunkten um 45–50 °C werden nicht als CPU-Kurven interpretiert, sondern durch sichere CPU-Standardkurven ersetzt. LCD-Profile aus 3.0.5 ohne Modusfeld erkennen GIF- und statische Bilddateien automatisch. Sicherheitsabfragen, Berechtigungsprüfung und serielle Befehlswarteschlange bleiben aktiv.
