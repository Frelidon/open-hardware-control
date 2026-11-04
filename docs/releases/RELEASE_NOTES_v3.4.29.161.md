# Open Hardware Control 3.4.29.161 STABLE

Diese öffentliche Ausgabe enthält den vollständigen Funktionsstand aus
3.4.29.159 und die hardwareunabhängige Levita-Testumgebung aus 3.4.29.160.
Zusätzlich funktioniert das Ausblenden gemerkter eigener LCD-Medien nun auch
auf Rechnern ohne systemweit installierten TRCC-Standardkatalog zuverlässig.
Die Dateien auf der Festplatte bleiben dabei unverändert; die eingebauten
OHC-Designs bleiben verfügbar.

## Feature-Reifegrade und Versionen

- Eine zentrale, hardwarefreie Registry führt für jeden Hauptbereich eine
  unabhängige semantische Feature-Version und einen Reifegrad.
- „Beta Plus“ heißt als üblicher Entwicklungsstand **Release Candidate**.
  RGB-Studio und LCD stehen auf `0.9.0-rc1`; Übersicht, Grafikkarte, Gehäuse,
  Kühlung, Profile und Wallpaper Engine sind Beta.
- Corsair/OpenLinkHub, Hardware-Checker, Snapshot-Manager,
  Automationszentrale, Programme und Desktop-Designs bleiben ehrlich als Alpha
  gekennzeichnet. Einstellungen und Über-Seite sind stabil.
- Der Stand erscheint additiv in „Funktionen & Bereiche“ und den Karten der
  Navigationsverwaltung. Er aktiviert, deaktiviert oder versteckt keine Funktion.

## Öffentlicher Designkatalog

- Pakete und Repository enthalten nur projekt-eigene OHC-Designs und -Effekte.
  Stock-Clips, Kenney-Bestandteile, Hersteller-/TRCC-Katalogmedien und
  importierte Benutzerdateien sind nicht Teil der Veröffentlichung.
- Import-, Katalog-, Editor-, Vorschau- und Hardwareübergabe-Funktionen bleiben
  erhalten. Die animierte Gehäuselüfter-/RGB-Vorschau und räumliche LED-Pfade
  sind weiterhin durch Regressionen geschützt.
- Eigene LCD-Quellen lassen sich unabhängig von einem installierten
  TRCC-Standardkatalog ein- und ausblenden. Ausblenden löscht keine Dateien.

## Release-Absicherung

- Der vollständige UI-Test setzt seinen Levita-Kühlertyp ausdrücklich in den
  isolierten Testeinstellungen und deckt einen Host ohne TRCC-Standardkatalog ab.
- Der Test führt keine Hardware-I/O aus. Geräteerkennung, Profile,
  Hardwarebesitz, LED-/PWM-Zuordnungen und Schreibpfade bleiben unverändert.
- OpenRGB-SDK-6-Profilmeldungen und der dreistufige TRCC-GPU-Taktgrenzschutz aus
  3.4.29.158 sind enthalten.
- Reale Fedora-Hardware und die optische Bestätigung von Gehäusehelligkeit,
  Laufrichtung und physischer LED-Reihenfolge bleiben getrennt offen.
