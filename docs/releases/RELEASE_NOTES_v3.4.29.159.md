# Open Hardware Control 3.4.29.159 STABLE

Diese öffentliche Ausgabe bewahrt die vollständige Funktionsoberfläche von
3.4.29.158 und ergänzt nachvollziehbare Entwicklungsstände je Hauptbereich.
Bestehende Profile, Hardwarebesitz, LED-/PWM-Zuordnungen und Schreibpfade werden
nicht migriert oder verändert.

## Feature-Reifegrade und Versionen

- Eine zentrale, hardwarefreie Registry führt für jeden Hauptbereich eine
  unabhängige semantische Feature-Version und einen Reifegrad.
- „Beta Plus“ wird als üblicher **Release Candidate** bezeichnet. RGB-Studio
  und LCD stehen auf `0.9.0-rc1`; Übersicht, Grafikkarte, Gehäuse, Kühlung,
  Profile und Wallpaper Engine sind Beta.
- Corsair/OpenLinkHub, Hardware-Checker, Snapshot-Manager,
  Automationszentrale, Programme und Desktop-Designs bleiben ehrlich als Alpha
  gekennzeichnet. Einstellungen und Über-Seite sind stabil.
- Der Stand erscheint additiv in „Funktionen & Bereiche“ und den Karten der
  Navigationsverwaltung. Er aktiviert, deaktiviert oder versteckt keine Funktion.

## Öffentlicher Designkatalog

- Pakete und Repository enthalten nur projekt-eigene OHC-Designs und -Effekte.
  Stock-Clips, Kenney-Bestandteile, Hersteller-/TRCC-Katalogmedien und
  importierte Benutzerdateien sind nicht Teil der Veröffentlichung.
- Die bestehenden Import-, Katalog-, Editor-, Vorschau- und Hardwareübergabe-
  Funktionen bleiben erhalten. Entfernt wurden nur gebündelte fremde Medien,
  nicht die zugehörigen Funktionspfade.

## Bewahrte Funktionen und Grenzen

- Die animierte Gehäuselüfter-/RGB-Vorschau, räumliche LED-Pfade, Profile,
  RGB-Studio, LCD, Wallpaper Engine, GPU, Snapshots, Programme und
  Automatisierungen bleiben durch Regressionen abgedeckt.
- OpenRGB-SDK-6-Profilmeldungen und der dreistufige TRCC-GPU-Taktgrenzschutz aus
  3.4.29.158 sind enthalten.
- Reale Fedora-Hardware und die optische Bestätigung von Gehäusehelligkeit,
  Laufrichtung und physischer LED-Reihenfolge bleiben getrennt offen; simulierte
  Tests werden nicht als Hardwarebestätigung ausgegeben.
