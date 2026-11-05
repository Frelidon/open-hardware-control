# Open Hardware Control 3.4.29.168 STABLE

Diese öffentliche Ausgabe enthält den vollständigen Funktionsstand aus
3.4.29.167. Die reale Scroll-/Viewport-Sichtbarkeit wird in einer kontrollierten
Qt-Hierarchie geprüft; der vollständige Anwendungstest sichert weiterhin
Medienwahl, Vorschau-Pause/-Fortsetzung, Bestätigungsfallback und alle vier
Sprachen ab, ohne von der virtuellen Desktopgröße eines Runners abzuhängen.
Ein später Snapshot-Aktivitätsprozess-Callback greift nach dem Beenden nicht
mehr auf einen bereits zerstörten Qt-Eigentümer zu.

## Feature-Reifegrade

- RGB-Studio und LCD: Release Candidate `0.9.0-rc1`.
- Übersicht, Grafikkarte, Gehäuse, Kühlung, Profile und Wallpaper Engine: Beta.
- Corsair/OpenLinkHub, Hardware-Checker, Snapshot-Manager,
  Automatisierungszentrale, Programme und Desktop-Designs: Alpha.
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
