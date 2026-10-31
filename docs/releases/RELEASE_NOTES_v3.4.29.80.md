# Open Hardware Control 3.4.29.80 INTERN

Interner Teststand vom 12.09.26. Kein öffentlicher GitHub-Release.

## Behoben und verbessert

- Der NCT6687-/MOK-Assistent arbeitet jetzt wirklich Schritt für Schritt. Er erkennt die bestätigende `mokutil`-Meldung auch neben der beobachteten Kernel-Keyring-Warnung korrekt und prüft seinen Status ohne blockierende Oberfläche.
- Gehäuselüfter besitzen klare System-Fan-Namen mit getrenntem PWM-Kanal. Ein bestätigter Reset entfernt alle Zuordnungen und Freigaben, behält Kurven und gibt eine laufende Regelung vorher an BIOS/Firmware zurück.
- Auf der Abschlussseite kann der Lüfter-Assistent unmittelbar mit dem nächsten noch offenen Lüfter wieder von vorn beginnen.
- Levita zeigt weder einen fehlenden Kühlmittelsensor noch eine Kühlmittelquelle in den Lüfterkurven. Die sicheren PWM-Untergrenzen stehen in einer eigenen lesbaren Warnfläche.
- Ein Doppelklick auf eine Komponente der PC-Ansicht öffnet das zugeordnete RGB-Gerät und bei Direct-Geräten dessen LED-Zonen. Die Sapphire RX 9070 XT bleibt entsprechend dem gelieferten Log bei ihrem von OpenRGB gemeldeten Hardwaremodus mit einer logischen LED; OHC täuscht keine adressierbaren Segmente vor.
- Das X blendet OHC unter KDE/Wayland wieder aus der Taskleiste in den Infobereich aus, auch wenn Qt keine Geometrie für das tatsächlich sichtbare StatusNotifier-Symbol liefert. „Beenden“ bleibt davon getrennt.

## Sicherheit und Validierung

- Keine automatische Secure-Boot-Änderung, kein automatischer Neustart und kein Passwortzugriff; privilegierte Treiberaktionen bleiben fest vorgegeben und bestätigt.
- Kein neuer RGB-Hardwareschreibpfad und keine erratene LED-Topologie; der Doppelklick verwendet die vorhandene Loopback-OpenRGB-Zonenkonfiguration.
- Gezielte MOK-, Lüfter-, Kühlungs-, RGB-/PC-Ansichts-, Tray-, Lokalisierungs- und Offscreen-UI-Regressionsprüfungen.
