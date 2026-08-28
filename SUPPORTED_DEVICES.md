# Unterstützte Geräte – Open Hardware Control 3.4.28 INTERN

## Direkt getestetes NZXT-Modul

| Gerät | USB-ID | Backend | Umfang |
|---|---|---|---|
| NZXT Kraken 2023 | `1e71:300e` | liquidctl | Wasser, Pumpe, Radiatorlüfter, LCD |
| NZXT 2023 RGB Controller | `1e71:2012` | liquidctl | drei RGB-Kanäle |

Der Schwerpunkt bleibt die NZXT Kraken RGB 360 (2023, Standard / Non-Elite) mit Firmware 2.0.0. Andere Kraken-Varianten gelten erst nach realem Hardwaretest als bestätigt.

## Corsair über OpenLinkHub

Open Hardware Control besitzt keine eigene feste Corsair-USB-Geräteliste. Es zeigt die Geräte an, die der lokal installierte OpenLinkHub-Dienst über `/api/devices/` meldet. Damit folgt der Erkennungsumfang der tatsächlich installierten OpenLinkHub-Version.

Seit Version 3.0.4 gibt es direkte Einstellungen nur für Geräte, Kanäle und Profile, die der lokale OpenLinkHub-Dienst meldet. Kühlung, RGB/LCD, Maus, Tastatur und Headset besitzen getrennte, validierte Aktionen. Nicht gemeldete oder komplexe gerätespezifische Funktionen bleiben im Web-Dashboard. Die reale Kompatibilität muss mit OpenLinkHub 0.9.0 und den angeschlossenen Corsair-Geräten geprüft werden.

Version 3.0.9 ordnet erkannte Mäuse anhand des Produktnamens einem generischen SVG-Schema zu. Berücksichtigt werden insbesondere Scimitar-, M55-/M75-, M65-/Dark-Core-/Ironclaw-/Glaive-/Sabre-, Darkstar-/Nightsabre-, Katar- und Harpoon-Familien. Unbekannte Mäuse erhalten das kompakte Standardschema. Das ist eine visuelle Orientierung und keine Aussage über eine exakte Gehäusegeometrie.

Eine Maustaste ist direkt belegbar, wenn OpenLinkHub für sie einen eindeutigen Tastenindex meldet. Unterstützt werden Keine, Medien, DPI, Tastatur, Sniper-DPI, Maus und vorhandene Makros. Die fensterlokale Makroaufnahme erzeugt nur Tastatur-/Pausenschritte; komplexe Folgen bleiben im OpenLinkHub-Web-Dashboard. Welche Zuweisungen ein konkretes Modell tatsächlich annimmt, hängt von der installierten OpenLinkHub-Version und deren Gerätetreiber ab.

## Zusätzliche RGB-Geräte über OpenRGB

Version 3.4.23 besitzt bewusst keine kopierte OpenRGB-USB-Geräteliste. OHC startet das installierte Backend selbst als privaten, fensterlosen Kindprozess und zeigt ausschließlich die von ihm gemeldeten Geräte, Zonen, LEDs und Modi an. Damit entspricht die Hardwareabdeckung der installierten OpenRGB-Version und deren aktivierten Treibern/udev-Regeln.

Direct-Geräte werden seit 3.4.5 für Farbe und OHC-Effekte über den lokalen SDK-Helfer geschrieben und erreichen den bestätigten CLI-`ApplyOptions`-/`stl_vector`-Absturzpfad nicht mehr. 3.4.7 handelt die auf Fedora gemeldeten SDK-Protokollrevisionen 4 und 5 kompatibel aus. 3.4.9 richtet variable Zonen ein und bestätigt Servermodus sowie Farbpuffer durch Rücklesung. 3.4.10 sendet zusätzlich immer den vollständigen Geräteframe und beim ersten Direct-Wechsel einmal vollständige Zonenframes als Treiber-Fallback. Bei nativen Nicht-Direct-Modi sperrt OHC weiterhin nur das tatsächlich abstürzende Gerät bis zum nächsten Programmstart.

3.4.23 hält für Softwareanimationen eine SDK-Verbindung offen und sendet alle ausgewählten Direct-Geräte in einem gemeinsamen, begrenzten Frame mit 25-Hz-Ziel. Ein ARGB-Controller kann die Zahl verketteter Lüfter/LEDs weiterhin nicht elektrisch erkennen; der Einrichtungsassistent und der Einzelzonen-Sichttest führen deshalb durch die reale Zuordnung.

ARGB-Controller können Zonen melden, ohne die Zahl der elektrisch angeschlossenen LEDs zu kennen. 3.4.9 bietet deshalb „LED-Zonen und Lüfter einrichten“ an: OHC übernimmt vorhandene OpenRGB-Werte, schlägt bei einer passenden PC-Position die bekannte Lüfterzahl vor und lässt pro Zone Lüfterzahl sowie LEDs je Lüfter festlegen. 3.4.10 ergänzt Profile für TZMRIT/Jungle-Leopard Interstellar V2 Normal und Reverse mit 24 LEDs je Lüfter sowie Plausibilitätswarnungen. Die physische LED-Zahl ist nicht elektrisch rücklesbar; die Serverbestätigung wird deshalb nicht als sichtbare Hardwarebestätigung ausgegeben.

- Statische Farbe: pro gemeldetem Gerät.
- Nativer Modus: nur aus der vom Gerät gemeldeten Modusliste.
- OHC-Softwareeffekte: bei gemeldetem `Direct` Mode; andere ausgewählte Geräte erhalten einen passenden tatsächlich gemeldeten nativen Hardwaremodus.
- NZXT: gesperrt, solange das eingebaute NZXT-/liquidctl-Modul das Gerät besitzt.
- Corsair: gesperrt, solange OpenLinkHub erkannt ist.
- Externe SDK-Server: nicht unterstützt; nur `127.0.0.1:6742`.
- Veränderliche ARGB-Zonen: sichere Größenkonfiguration pro Zone mit Lüfterzahl × LEDs je Lüfter; eine gespeicherte PC-Position dient nur als Vorschlag, nicht als elektrische Erkennung.
- ENE-DRAM-Aliaspaare werden dedupliziert; ein vollständig gespiegeltes Gesamtinventar wird auf die erste reale Hälfte reduziert. Mehrere reale Module mit identischem Namen bleiben erhalten.
- NZXT `led1` bis `led3` erscheinen als eigene Kacheln und können mit anderen Geräten gruppiert werden.
- Gleichnamige GPU-/Controller-Einträge bleiben getrennt, werden nummeriert und können benannt sowie einer PC-Position zugeordnet werden.
- Frelidons mitgelieferte verschiebbare PC-Ansicht bildet zwölf Lüfter ab: Kraken 360 oben, zwei Frontlüfter, drei Reverse-Intakes an Rückwand/Seite, drei Reverse-Intakes auf der Netzteilabdeckung vorne und einen Hecklüfter. Anschlussnotizen wie A1/A2, B6/B7 und die SYS-FAN-Kanäle bleiben editierbare Dokumentation und sind keine automatische elektrische Port-Erkennung.

Die indirekte OpenRGB-Kompatibilität ist keine reale Bestätigung jedes einzelnen Gerätemodells. Neue Controller sollten zuerst mit einer statischen Farbe und geringer Helligkeit getestet werden.

## Mainboard-/Gehäuselüfter über Linux hwmon

Version 3.4.23 kann PWM-Kanäle steuern, die Linux über `/sys/class/hwmon` bereitstellt. Der erste Schwerpunkt ist NCT6687/NCT6687D, insbesondere MSI-X870-Systeme. Eine Boardbezeichnung wird nur zur Diagnose verwendet; OHC leitet daraus **keine** feste PWM-Zuordnung ab.

- Jeder PWM-Kanal muss vor automatischer Regelung mit dem geführten 70-%-/10-s-Test mit RPM-Beobachtung physisch bestätigt werden.
- Erst bestätigte und ausdrücklich aktivierte Kanäle dürfen von der 1-s-Regelschleife geschrieben werden.
- Sensorquellen: CPU, GPU, Kraken-Kühlmittel, Maximum oder gewichtete CPU/GPU-Temperatur.
- Pro Kanal: eigene Kurve, Mindestleistung, Hysterese und Reaktionsverzögerung.
- Bei drei aufeinanderfolgenden fehlenden Sensorwerten fordert OHC 70 % als sicheren Laufzeit-Fallback an; ab 90 °C werden 100 % angefordert.
- Beim Deaktivieren der OHC-Regelung und beim geordneten Programmende wird die Firmware-/BIOS-Steuerung über `pwmN_enable` wiederhergestellt, soweit der Treiber dies schreibbar anbietet. Ein vorhandenes nct6687d-`fan_control_watchdog` wird während aktiver Regelung als zusätzliche 10-s-Absturzsicherung aufgefrischt.
- Wenn die PWM-sysfs-Dateien für den angemeldeten Benutzer nicht schreibbar sind, führt OHC **keinen** Schreibversuch aus. Der Treiber-/Secure-Boot-Dialog zeigt Diagnose und Einrichtungshinweise; Secure Boot/MOK wird nicht umgangen.
- GPU-Lüfter sind ausdrücklich nicht Teil dieser Funktion.

Die reale elektrische Zuordnung und die Schreibbarkeit hängen vom installierten Kernel-/NCT6687-Treiber und der konkreten Board-Firmware ab. Deshalb bleibt die Kalibrierung verpflichtend, auch wenn dasselbe Mainboardmodell bereits bekannt ist.

## Nicht enthalten

- allgemeines Mainboard-/Spannungs-/Takt-Tuning außerhalb der kalibrierten hwmon-PWM-Lüftersteuerung
- GPU-Lüftersteuerung
- Firmwareaktualisierungen
- Open Radeon Control Center; dieses bleibt eigenständig
- ungetestete direkte USB-Schreibzugriffe auf Corsair-Geräte
- eingebettete OpenRGB-Hardwaretreiber; der separat installierte Backendprozess wird von OHC verwaltet

Produktnamen dienen nur der Kompatibilitätsangabe. Open Hardware Control ist kein offizielles Produkt von NZXT, Corsair, OpenLinkHub oder OpenRGB.
