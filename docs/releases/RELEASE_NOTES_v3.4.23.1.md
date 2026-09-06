# Open Hardware Control 3.4.23.1 INTERN

3.4.23.1 ist ein gezielter Mainboard-Lüfter-Hotfix für Linux/NCT6687. Die OHC-GUI bleibt unprivilegiert; ein eng begrenzter Polkit-Helfer übernimmt ausschließlich validierte NCT6687-hwmon-Schreibzugriffe auf PWM-Kanäle 1–8, Firmware-Rückgabe und den optionalen Treiber-Watchdog.

Die sichere Kalibrierung läuft nun 10 Sekunden bei 70 % und beobachtet den RPM-Verlauf. Damit berücksichtigt OHC das auf MSI-X870/NCT6687 beobachtete verzögerte EC-Verhalten, bei dem der unmittelbar gelesene `pwmN`-Wert nicht zwingend sofort dem Zielwert entspricht. Die physische Zuordnung bleibt weiterhin bestätigungspflichtig.

Bei vorheriger Firmwareautomatik stellt OHC über `pwmN_enable=2` zurück, sodass der aktuelle nct6687d-Treiber seine gesicherte vollständige Firmware-/MSI-Kurve wiederherstellen kann. Der Watchdog wird während aktiver Regelung begrenzt erneuert; ein unerwartetes Ende kann dadurch weiterhin vom Treiber abgefangen werden.
