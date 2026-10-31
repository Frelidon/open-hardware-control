# Open Hardware Control 3.4.29.70 INTERN

Interner Linux-Teststand vom 12. September 2026. Kein GitHub-Tag und kein öffentliches Release.

## LCD und Datenoberflächen

- Vier vollständig eigene bunte Layer-2-Layouts: **Spectrum Ring**, **Neon Double Arc**, **Prism Segments** und **Aurora Radar**.
- Die Layouts verwenden nur selbst erzeugte Formen und übernehmen weder be-quiet!-Schriftzug noch Herstellerlogo, Kühlerkontur oder Einzelbilder des Referenzvideos.
- Im Editor können bis zu zwölf eigene Textelemente ergänzt, einzeln entfernt und in Inhalt, lokal installierter Schrift, Größe, Farbe, Sichtbarkeit und Position verändert werden.
- Der native Anwendeweg übernimmt Texte und Schriftnamen in ein privates validiertes Cache-Theme; die vorhandene einzelne TRCC-Warteschlange bleibt alleiniger Display-/USB-Besitzer.
- Die große Vorschau ist auf 880×396 festgelegt. Das entspricht exakt 1600:720 und verhindert das bisherige Größenspringen beim Öffnen, Schließen, Wechseln oder Scrollen der Werkzeuge.

## Vorgemerkte nächste Arbeit

Für eine der nächsten zwei bis drei internen Versionen ist ein moderner LCD-Design-Manager verbindlich vorgemerkt: mehrere Quellordner hinzufügen/entfernen, einzelne Bilder und Videos importieren/aus der OHC-Bibliothek entfernen sowie Herkunft und Verfügbarkeit übersichtlich anzeigen. Das Entfernen aus OHC löscht die Originaldatei standardmäßig nicht.

## Sicherheit und Kompatibilität

- Keine Kühlkurve, PWM-Untergrenze, CoolerControl-Sperre oder Profil-Hardwareaktion wurde verändert.
- Kein zweiter TRCC-Prozess und kein neuer USB-Schreibpfad.
- Deutsch, Englisch, Spanisch und Französisch enthalten dieselben 1.226 stabilen Nachrichten-IDs.
