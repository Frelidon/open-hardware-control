# Open Hardware Control 3.4.29.71 INTERN

Interner Linux-Teststand vom 12. September 2026. Kein GitHub-Tag und kein öffentliches Release.

## Display-Effekte und LCD

- Die freie Ebene-1-Designbibliothek verwendet jetzt große grafische Vorschaukacheln statt der versteckten Hauptdesign-Liste. Kategorie und Farbvariante bleiben auswählbar.
- Die drei anklickbaren Angaben für Urheber, Originalquelle und Lizenz bleiben unter den Kacheln vollständig erhalten.
- **OHC Spektrumring · Animiert** ist ein eigener, reproduzierbarer und nahtloser 1600×720-H.264-Loop. Acht Farbsegmente drehen sich um die Live-Datenfläche; der physische 80-Pixel-Notchbereich bleibt schwarz.
- Bei Auswahl des Spektrumrings wird automatisch die passende editierbare Ebene-2-Datenoberfläche gewählt. Eine spätere manuelle Auswahl eines anderen Layouts bleibt möglich.
- Eigene OHC-Datenoberflächen nutzen konsistente DejaVu-Schriftangaben und kompakte mehrschichtige Glasrahmen für Uhren. Der statische Spektrumring wurde abgeschwächt, damit die Bewegung darunter sichtbar bleibt.

## Programmfenster und lokale Bibliothek

- Unter **Einstellungen → Programmfenster, Bildschirm und DPI** stehen sowohl „Hauptbildschirm (Standard)“ als auch alle festen Anschlüsse einschließlich des aktuellen Hauptbildschirms zur Wahl.
- Ein maximiertes Fenster wird zuerst mit sicher begrenzter Normalgeometrie auf dem Zielmonitor platziert und erst im folgenden Qt-Zyklus erneut maximiert. Das adressiert den im Log bestätigten KWin-Wiederherstellungsversatz auf den Nebenbildschirm.
- Acht lokale Cyber-Bilder tragen aussagekräftige Namen. Vom dreifach vorhandenen Cyber-Korridor bleibt die qualitativ beste 2560×1440-/30-s-Fassung als **Cyber-Korridor-Reise** in der OHC-Bibliothek; die zwei kleineren Fassungen liegen wiederherstellbar außerhalb des gescannten Ordners.

## Sicherheit und Kompatibilität

- Auswahl und Vorschau schreiben keine Hardware. Das Anwenden beim nächsten Start erfordert weiterhin **Profile → Ausgewähltes Profil aktualisieren**.
- Kein zweiter TRCC-Prozess und kein neuer USB-, Lüfter- oder Kühlungs-Schreibpfad.
- Deutsch, Englisch, Spanisch und Französisch enthalten dieselben 1.250 stabilen Nachrichten-IDs.
