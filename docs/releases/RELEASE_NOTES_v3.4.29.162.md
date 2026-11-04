# Open Hardware Control 3.4.29.162 STABLE

Diese öffentliche Ausgabe enthält den vollständigen Funktionsstand aus
3.4.29.161. Der isolierte Vorschautest wartet nun innerhalb einer festen Grenze
auf die tatsächlich aufgebaute Offscreen-Geometrie, statt eine bestimmte
Geschwindigkeit des GitHub-Runners vorauszusetzen. Beim Testende wird außerdem
der Snapshot-Probe ausdrücklich beendet. Produktive Vorschau-, Snapshot- und
Hardwarepfade bleiben unverändert.

## Feature-Reifegrade und Versionen

- Eine zentrale, hardwarefreie Registry führt für jeden Hauptbereich eine
  unabhängige semantische Feature-Version und einen Reifegrad.
- „Beta Plus“ heißt als üblicher Entwicklungsstand **Release Candidate**.
  RGB-Studio und LCD stehen auf `0.9.0-rc1`; Übersicht, Grafikkarte, Gehäuse,
  Kühlung, Profile und Wallpaper Engine sind Beta.
- Corsair/OpenLinkHub, Hardware-Checker, Snapshot-Manager,
  Automationszentrale, Programme und Desktop-Designs sind Alpha.
  Einstellungen und Über-Seite sind stabil.
- Die Angaben erscheinen additiv in „Funktionen & Bereiche“ und den Karten der
  Navigationsverwaltung. Sie aktivieren oder verstecken keine Funktion.

## Funktions- und Datenbestand

- Pakete und Repository enthalten nur projekt-eigene OHC-Designs und -Effekte.
- Import-, Katalog-, Editor-, Vorschau- und Hardwareübergabe-Funktionen bleiben
  erhalten. Die animierte Gehäuselüfter-/RGB-Vorschau und räumliche LED-Pfade
  sind weiterhin durch Regressionen geschützt.
- Eigene LCD-Quellen lassen sich auch ohne installierten TRCC-Standardkatalog
  zuverlässig ein- und ausblenden. Ausblenden löscht keine Dateien.

## Release-Absicherung

- Der vollständige UI-Test verwendet isolierte Einstellungen ohne Hardware-I/O.
- Der Vorschautest wartet höchstens zwei Sekunden auf die reale Offscreen-
  Sichtbarkeit und beendet seinen Snapshot-Probe kontrolliert.
- Geräteerkennung, Profile, Hardwarebesitz, LED-/PWM-Zuordnungen und
  Schreibpfade bleiben unverändert.
- Reale Fedora-Hardware und die optische Bestätigung von Gehäusehelligkeit,
  Laufrichtung und physischer LED-Reihenfolge bleiben getrennt offen.
