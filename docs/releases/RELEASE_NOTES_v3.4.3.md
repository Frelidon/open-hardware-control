# Open Hardware Control 3.4.3 INTERN

## OpenRGB-Hotfix nach vier realen Fedora-Coredumps

Die neuen Protokolle bestätigen einen zweiten Fehlerpfad in OpenRGB `1.0~rc2`: Selbst ein korrekt serialisierter Einzelgerätebefehl kann in OpenRGBs Funktion `ApplyOptions` an einem internen `std::vector`-Indexabgleich abbrechen. Ein statischer Ausschaltbefehl für Gerät 3 sowie Direct-Mode-Frames für die Geräte 6 und 10 lösten denselben `SIGABRT` aus.

Version 3.4.3 erkennt dieses eindeutige Muster und isoliert das verursachende Gerät für die aktuelle OHC-Sitzung. Die übrigen Geräte werden weiter verarbeitet; insbesondere erreicht der Einzelgeräte-Test sein absichtlich zuletzt geschriebenes Ziel. Die Sperre ist nicht dauerhaft und verschwindet mit dem nächsten OHC-Start.

Direct-Mode-Fehler werden jetzt pro Gerät gezählt. Erfolgreiche Frames eines anderen Geräts setzen den Zähler nicht länger zurück. Ein bestätigter OpenRGB-Prozessabsturz sperrt das betroffene Gerät sofort, gewöhnliche Fehler erst nach drei Fehlern dieses Geräts. Andere OpenRGB-Geräte und bereits gestartete NZXT-Hardwareeffekte laufen weiter.

Die Geräteerkennung protokolliert zusätzlich den OpenRGB-Index, den sichtbaren beziehungsweise selbst vergebenen Gerätenamen, die LED-Anzahl und die Direct-Fähigkeit. Damit lassen sich künftige Coredumps eindeutig einer Gerätekachel zuordnen.

Dieser Build bleibt intern, bis der neue Schutzpfad und der Einzelgeräte-Test mit der realen Fedora-44-Hardware geprüft wurden.
