# Open Hardware Control 3.4.29.18 INTERN

## Verschiebbare Levita-Datenoberfläche 2

Jeder logische Live-Datenblock eines unterstützten 1600×720-TRCC-Layouts kann in der großen Vorschau einzeln gezogen werden. Eine gemeinsame Darstellung wie `CPU 30 %` bleibt dabei ein Block. Zwei zusätzliche Regler verschieben die vollständige Datenebene gemeinsam.

Ein Rechtsklick auf einen Block öffnet die Bearbeitung für Farbe, Schriftgröße und Text beziehungsweise Sensorbezeichnung; außerdem kann jeder Block einzeln auf seine importierte Ausgangsposition zurückgesetzt werden. Die Änderungen werden pro Layout in OHC gespeichert.

## Unveränderte Originaldesigns

OHC überschreibt weder `config1.dc` noch Bilder oder Videos. Native `trcc.json`-Layouts werden direkt gelesen; das separat installierte TRCC-Linux-Backend dekodiert ältere DC-Layouts. Für die Übertragung erzeugt OHC eine eigene inhaltsadressierte Cache-Ansicht mit `trcc.json` und Verweisen auf die lokalen Originalmedien.

## Modulstruktur für lokale KIs

Die neue Fachlogik ist in `modules/lcd_levita/v1_0/` nach Modell, Canvas und TRCC-Adapter getrennt. `MODULE_REGISTRY.md` ist der verpflichtende Index für aktuelle Modulversionen und Pfade. Die neue `AI_DEVELOPMENT_GUIDE.md` beschreibt die Erweiterung von UI-, Sensor- und LCD-Komponenten. Automatische Prüfungen erzwingen genau einen aktuellen Versionsordner und die für lokale Modelle mit 16 GB VRAM festgelegten Dateigrößenbudgets.

## Sicherheit und Teststatus

Testmodus, serialisierte TRCC-Übertragung, Notch-Schutz und die getrennte PWM-Kühlungszuständigkeit bleiben unverändert. Neue Regressionen decken Modell/Persistenz, read-only Staging, UI-Verträge, Modulregister und die vollständige hardwarefreie Offscreen-Konstruktion ab. Ein realer Langzeittest des vollständigen Designs auf dem physischen Levita-Display bleibt weiterhin erforderlich, bevor weitergehende Hardwareaussagen getroffen werden.
