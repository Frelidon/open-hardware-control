# Open Hardware Control 3.4.29.49 INTERN

Interne Version: Die Übersicht zeigt nach bestätigten Levita-PWM-Tests denselben grünen OK-Zustand wie „Erkannte Hardware“, und das RGB-Studio klappt Geräte, Effekte und native Hardwarekanäle als große Bereiche in der Seite auf. Es wird kein Tag, Push oder öffentliches GitHub-Release erzeugt.

## Übersicht Status & Hinweise

- Nach bestätigten PWM-Tests für Pumpe und Radiator erscheint der Levita-Kühlhinweis mit grünem Punkt und **OK**, analog zur Hardwareliste.
- Offene Tests oder Sensorfehler nutzen einen roten Punkt und **Fehlerhaft**.
- Die übrigen Hinweiszeilen (Kraken, Sensoren, Profile, Datenschutz) folgen demselben Raster.

## RGB-Studio

- **Geräte und Effekte** öffnet und schließt ein großes Feld in der Seite statt eines Extra-Fensters.
- Die native Hardwarekanal-Liste liegt darunter in voller Breite, bleibt beim Seitenwechsel sichtbar und ist ohne zusätzliche Fenster bedienbar.

## Prüfung

Übersichtshinweise, RGB-Studio-Aufbau und vorhandene Hardware-Regressionen werden ohne Schreibzugriff auf Geräte geprüft. Der Build bleibt `INTERN`.
