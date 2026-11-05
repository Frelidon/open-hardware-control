# Open Hardware Control 3.4.29.165 STABLE

Diese öffentliche Ausgabe enthält den vollständigen Funktionsstand aus
3.4.29.164. Der isolierte echte Viewport-Test verwendet Qt `minimal`: weiterhin
vollständig headless, jedoch mit definierter Fensterexposition. Qt `offscreen`
garantiert diese Semantik auf GitHub-Runnern nicht. Das responsive 760×700-
Testfenster prüft echtes Scrollen, Sichtbarkeit und Video-Pause/-Fortsetzung.
Die produktive QPA-Auswahl, Oberfläche und Hardwarepfade bleiben unverändert.

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
