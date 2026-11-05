# Open Hardware Control 3.4.29.164 STABLE

Diese öffentliche Ausgabe enthält den vollständigen Funktionsstand aus
3.4.29.163. Der isolierte Vorschautest verwendet ein responsives 760×700-Fenster,
das auch in die kleinste virtuelle Qt-CI-Bildschirmfläche passt. Damit bleiben
echtes Scrollen, Sichtbarkeit sowie Video-Pause/-Fortsetzung geprüft, ohne einen
auf dem Runner nicht vorhandenen nativen 1600×1000-Bildschirm vorauszusetzen.
Produktive Oberfläche und Hardwarepfade bleiben unverändert.

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
