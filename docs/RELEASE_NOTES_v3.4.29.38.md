# Open Hardware Control 3.4.29.38 INTERN

Diese interne Version modernisiert das RGB-Studio und aktualisiert die Thermalright-Backend-Empfehlung auf TRCC Linux 9.9.12.

- Die OHC-RGB-Engine liegt direkt im Bereich „Geräte und Effekte“. Freigabe, Startprofil-Automatik und Wiederübernahme verwenden eindeutige Ein/Aus-Schalter; technische Details bleiben innerhalb derselben Seite aufklappbar.
- „Design direkt anwenden“ besitzt eine unmittelbar zugeordnete Gesamthelligkeit von 0 bis 100 Prozent. Native OpenRGB- und NZXT-Hardwarekanäle werden nach der Übertragung in einer eingebetteten Ergebnisliste angezeigt.
- Ein Rechtsklick auf eine Designkachel oder einen Effekt bietet genau die verwendete Zahl an Farben an. Die bereits vorhandene persistente Farbanpassung pro Design bleibt erhalten.
- Abgewiesene RGB-Befehlsfolgen schließen ihren Fehler-Callback ab. Eine ENE-DRAM-Reinitialisierung kann dadurch nicht mehr bis zum Programmneustart als laufend markiert bleiben.
- Die hardwarefreie RGB-Galerie liegt im versionierten Modul `modules/rgb_studio/v1_1/`; der Hauptorchestrator bleibt unter seinem Größenbudget.
- TRCC Linux 9.9.12 ist die empfohlene kompatible Levita-Backend-Version. Das Upstream-Update behebt insbesondere den Fedora-RPM-Dateikonflikt mit `python3-sounddevice`; OHCs Daemon-/Unix-Socket- und Displaybefehle bleiben unverändert kompatibel.
- Die reale Levita-Bestätigung bleibt ausdrücklich an TRCC Linux 9.9.11 gebunden: Modell 64/Sub 3, 1600×720 und sichtbarer Farbzyklus. Aus der reinen Kompatibilitätsprüfung wird kein neuer Hardwaretest behauptet.

TRCC bleibt separat installiert und bleibt der einzige Levita-USB-Besitzer. Diese Version integriert oder startet keinen zweiten USB-Treiber.
