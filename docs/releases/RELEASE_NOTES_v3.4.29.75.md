# Open Hardware Control 3.4.29.75 INTERN

Interner Linux-Teststand vom 12. September 2026. Kein GitHub-Tag und kein öffentliches Release.

## Stabiler Fensterstart

- Der für KDE/Wayland notwendige kurze Normalzustand ist während der ersten Platzierung geschützt und wird nicht als Benutzeränderung wiederhergestellt.
- Ein automatisch geladenes Startprofil darf die global gewählte Fenstergröße, Maximierung oder den Zielbildschirm nicht verändern und startet keine zweite Platzierungsfolge.
- Manuell angewendete Profile behalten ihre ausdrückliche Fensterdarstellung. Die bestehende einmalige KWin-Zielprüfung bleibt erhalten.

## LCD-Bibliothek und Kacheln

- Ebene 1, Ebene 2, die freie Effektbibliothek und das Sensorlayout unter Display-Effekte berechnen ihre Spalten aus dem tatsächlich sichtbaren Viewport. Bis zu zwölf Kacheln pro Reihe nutzen breite Bildschirme besser und reduzieren Scrollwege.
- Der LCD-Manager verwaltet mehrere Ordner und einzelne Bilder/Videos. Einträge lassen sich in OHC ausblenden oder mit einem eigenen Anzeigenamen versehen; Originaldateien werden niemals umbenannt, verschoben oder gelöscht.
- Externe TRCC-Katalog-IDs erhalten lesbare Namen wie `Natur 012`, `Technik 004` oder `HUD 021`. Externe Designs bleiben lokale Benutzerdaten und werden nicht mit OHC ausgeliefert.
- Die eigenen OHC-Cybermedien und Datenoberflächen besitzen klarere, beschreibende Namen. Gespeicherte Pfade und Profile bleiben kompatibel.

## Temperaturaufzeichnung und Berichte

- Diagrammachsen, Hoveranzeige und Messwerttabelle zeigen lokales Datum und Uhrzeit.
- Diagramm, Sensorliste und Messwerttabelle sind über horizontale und vertikale Trenner frei skalierbar; die gewählten Größen werden gespeichert.
- Ein ausdrücklicher Berichtsdialog wählt Start, Ende, Sensoren und CSV oder JSON. Er exportiert aus dem vollständigen RAM-Sitzungsverlauf, auch wenn einzelne Sensoren zuvor nicht im Diagramm sichtbar waren.
- Die Sensorabfrage bleibt ausschließlich lesend und nimmt keinen Regelungs- oder Übertaktungsbesitz. Ohne einen bewussten Export entsteht keine Datei.

## Prüfung und Grenzen

- Die neue Bibliotheks-, Berichtsexport- und Responsive-Logik ist durch reine Modelltests sowie vollständigen Offscreen-UI-Aufbau abgesichert.
- Reale Bildschirmzuordnung und Layoutwirkung müssen nach der RPM-Installation erneut auf der Referenzhardware bestätigt werden.
- Deutsch, Englisch, Spanisch und Französisch enthalten dieselben 1.291 stabilen Nachrichten-IDs.
