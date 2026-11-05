# Open Hardware Control 3.4.29.166 STABLE

Diese öffentliche Ausgabe enthält den vollständigen Funktionsstand aus
3.4.29.165. Der isolierte Vorschau-Kindprozess erhält Qt `minimal` ausdrücklich
in seiner eigenen Umgebung. Damit kann ein zuvor von der Gesamtsuite geerbter
`offscreen`-Wert den echten Viewport-Vertrag nicht mehr überschreiben.
Produktive QPA-Auswahl, Oberfläche und Hardwarepfade bleiben unverändert.

## Feature-Reifegrade

- RGB-Studio und LCD: Release Candidate `0.9.0-rc1`.
- Übersicht, Grafikkarte, Gehäuse, Kühlung, Profile und Wallpaper Engine: Beta.
- Corsair/OpenLinkHub, Hardware-Checker, Snapshot-Manager,
  Automationszentrale, Programme und Desktop-Designs: Alpha.
- Einstellungen und Über-Seite: Stabil.

## Erhaltener Funktionsbestand

- Repository und Pakete enthalten ausschließlich projekt-eigene OHC-Designs.
- Import, Katalog, Editor, Vorschau und Hardwareübergabe bleiben erhalten.
- Die animierte Gehäuselüfter-/RGB-Vorschau, räumliche LED-Pfade, Profile und
  PWM-Zuordnungen bleiben unverändert und regressionsgeschützt.
- Eigene LCD-Medien lassen sich auch ohne systemweiten TRCC-Katalog ausblenden,
  ohne Dateien zu löschen.

Reale Fedora-Hardware sowie die optische Bestätigung von Gehäusehelligkeit,
Laufrichtung und physischer LED-Reihenfolge bleiben getrennt offen.
