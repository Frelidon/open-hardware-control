# Open Hardware Control 3.4.29.56 INTERN

## Freie Display-Effektbibliothek

- Display Effects 1.2 enthält fünf ausgewählte Hauptdesigns: Seamless Smoke, Dark Smoke, Particle Fog, Fluid Waves und Digital Wave.
- Jedes Hauptdesign besitzt die Untervarianten Original, Eisblau, Plasma-Violett und Glut-Orange als stummes H.264-Medium mit 1600×720 und 24 FPS.
- Hauptdesign und Farbe werden getrennt gewählt. Die Vorschau bleibt mit dem aktiven Ebene-2-Sensorlayout verbunden.
- Direkt neben der Auswahl stehen Ersteller, Originalquelle und Lizenz als anklickbare Links. Dieselben Angaben liegen im Asset-README und in `docs/project/THIRD_PARTY_NOTICES.md`.
- Zur Laufzeit wird nichts aus dem Internet geladen. Alle Dateien sind für das Levita-Format zugeschnitten, farblich bearbeitet und lokal validiert.

## Logprüfung und Fehlerkorrektur

- Die protokollierten `QColorDialog`-Ereignisse gehören zum bewusst geöffneten Farbwähler und zeigen keinen Fehler.
- Die einzelnen leeren `FENSTERDIAGNOSE:`-Zeilen waren dagegen ein echter Diagnosefehler: `native_window_summary()` besaß durch eine falsch platzierte Rückgabe keinen Textwert.
- Die native Fensterzusammenfassung ist wiederhergestellt und durch einen Regressionstest gegen leere Zeilen abgesichert.
- Die periodische OpenRGB-Inventarliste und die begrenzten ENE-DRAM-Startnachprüfungen liefen im übersandten Ausschnitt erfolgreich; es lag dort kein RGB-Fehler vor.

## Sicherheit und Grenzen

- Medienauswahl und Vorschau schreiben keine Hardware. Anwenden verwendet weiterhin ausschließlich das Levita-Studio mit Testmodus, Neuverbindungsbarriere, Schutzpause und einem TRCC-Daemon als USB-Besitzer.
- Deutsch, Englisch, Spanisch und Französisch wurden gemeinsam auf 1.098 stabile Nachrichten-IDs erweitert.
- Interne Testversion. Kein GitHub-Push, Tag oder öffentliches Release wurde erstellt.
