# RGB-Studio – Quellcode-, Lizenz- und Sicherheitsprüfung für 3.4.16 INTERN

## Prüfung für 3.4.16

- Die 17 RGB-Vorschauen und drei zusätzlichen LCD-Layouts sind neu geschriebener OHC-Code ohne importierte Bild-, Effekt- oder Profildateien.
- SignalRGBs Kachel-/Kategorieprinzip wurde nur als allgemeine Bedienreferenz betrachtet. Die offiziellen Nutzungsbedingungen ordnen Plattform, Effekte und Grafiken dem Anbieter bzw. seinen Lizenzgebern zu; deshalb wird davon nichts kopiert oder gebündelt.
- NZXTs offizielle Dokumentation bestätigt „Infographic + Image/GIF“ als Produktfunktion. OHC bildet die Idee mit eigenem Renderer und dem bereits geprüften lokalen Transport nach; CAM-Code und CAM-Assets werden nicht übernommen.
- OpenRGB bleibt ein separat installiertes Backend unter GPL-2.0-or-later. OHC nutzt seine lokale SDK-Schnittstelle und kopiert weder die Effects-Plugin-Bibliothek noch USB-Treiberquellen in dieses Paket.
- Das betrachtete Community-Projekt KrakenZPlayground ist GPL-3.0, zielt jedoch auf Kraken-Z-Geräte und QML. 3.4.16 übernimmt daraus weder Code noch Beispiele; spätere Übernahmen benötigen eine konkrete Kompatibilitäts- und Attributionprüfung pro Datei.

Stand: 23. August 2026

## Architekturentscheidung

OpenRGB bleibt ein separat installiertes Hardwarebackend. Version 3.4.16 startet es bei Bedarf als privaten, fensterlosen Kindprozess und beendet genau diesen eigenen Prozess wieder. Dadurch sieht und bedient der Benutzer nur Open Hardware Control, ohne dass OHC ungeprüfte RAM-/Mainboard-Protokolle selbst implementieren muss. In der Prozessliste bleibt der separat lizenzierte Treiber technisch erkennbar. Eine andere OpenRGB-PID blockiert OHCs Engine und Schreibzugriffe, wird aber niemals automatisch beendet.

Es wurde kein OpenRGB- oder Effects-Plugin-Quellcode und kein fremdes Effektasset eingebettet. Die OHC-Effektengine, Geräteaufbereitung, Gruppierung, NZXT-Validierung und der minimale SDK-Paketwriter sind eigener GPL-3.0-or-later-Code.

| Projekt | Verwendung | Lizenz | Ergebnis |
|---|---|---|---|
| OpenRGB | lokal verwaltetes Gerätebackend | GPL-2.0-or-later | separat installiert, kein Code eingebettet |
| OpenRGB SDK | lokale Clientkommunikation | Projektdokumentation | fest auf Loopback begrenzt |
| OpenRGB Effects Plugin | Funktions-/Lizenzvergleich | GPL-2.0-or-later | weder Code noch Assets übernommen |
| liquidctl | NZXT 2023 RGB Controller | GPL-3.0-or-later | dokumentierte CLI; feste validierte Argumentlisten |

GPL-2.0-or-later könnte bei Wahl von GPLv3 grundsätzlich kombiniert werden. Die Trennung ist daher eine Wartungs- und Hardware-Sicherheitsentscheidung, keine pauschale Lizenzsperre.

### Eindämmung gerätespezifischer Backend-Abstürze

OpenRGB `1.0~rc2` auf Fedora 44 kann nachweislich auch bei validierten Einzelgerätebefehlen in seiner Funktion `ApplyOptions` mit `SIGABRT` enden. Der neue Coredump benennt den gültigen Befehl für Airgoo-Gerät 6 und bestätigt `std::vector::operator[] → ApplyOptions`. Version 3.4.5 führt Direct-Farben deshalb gar nicht mehr durch diesen CLI-Code, sondern sendet sie mit dem eigenen Loopback-SDK-Helfer an den weiterhin separaten OpenRGB-Server. Die bestehende Sitzungssperre bleibt als Rückfall für native Nicht-Direct-CLI-Modi erhalten.

Quellen:

- <https://gitlab.com/CalcProgrammer1/OpenRGB>
- <https://gitlab.com/CalcProgrammer1/OpenRGB/-/blob/master/LICENSE>
- <https://openrgb.org/sdk.html>
- <https://gitlab.com/OpenRGBDevelopers/OpenRGBEffectsPlugin>
- <https://github.com/liquidctl/liquidctl/blob/main/docs/nzxt-hue2-guide.md>

## Technische Sicherheitsgrenzen

`src/openrgb_integration.py`:

- akzeptiert ausschließlich Loopback-Adressen und in der App fest Port 6742;
- prüft die Erreichbarkeit vor jedem Clientbefehl;
- setzt immer den ausdrücklichen `--client`-Endpunkt;
- startet die verwaltete Engine mit privatem Konfigurationsordner und `--noautoconnect`;
- validiert Gerätenummern, Modusnamen und `RRGGBB`-Farben;
- verbietet mehrere `--device`-Blöcke in einem CLI-Aufruf und erzeugt stattdessen höchstens 64 serielle Einzelgerätebefehle;
- begrenzt Farblisten auf 4096 LEDs;
- verwendet nie `shell=True`.

`src/openrgb_sdk.py`:

- akzeptiert nur IPv4-/IPv6-Loopback und Port 1024–65535;
- fordert SDK-Protokollversion 5 an, verwendet mit dem Server die niedrigere unterstützte Revision und verlangt mindestens Revision 4;
- begrenzt Paketgröße, Gerätenummer und LED-Anzahl, prüft jede `RRGGBB`-Farbe und verwendet kurze Socket-Zeitlimits;
- begrenzt Worker-Aufträge auf 2 MiB und 64 eindeutige Geräte und akzeptiert ausschließlich JSON-Zeilen über die private Standardeingabe des OHC-Kindprozesses;
- hält während einer Animation genau eine lokale SDK-Verbindung offen, bereitet jedes Direct-Gerät nur einmal vor und trennt die Verbindung bei einer unklaren Socket-/Paketantwort sicher;
- sendet nur Clientname, validierte `RESIZEZONE`-Aufträge, Direct-/Custom-Umschaltung und fertige LED-Farben; Hardwareerkennung und Controllerprotokolle bleiben vollständig in OpenRGB;
- enthält keine Fernzugriffe, Downloads, Shellausführung oder Hersteller-USB-Protokolle.

`src/rgb_devices.py`:

- dedupliziert nur DRAM-Namensvarianten mit gleich großen Aliasgruppen;
- erhält mehrere reale Module mit gleichem Namen;
- validiert Gruppennamen, Kennungen und maximal 32 Gruppen;
- validiert benutzerdefinierte Gerätenamen und höchstens 64 PC-Layoutblöcke mit begrenzten Koordinaten und Größen;
- verwendet eine nicht blockierende Prozesssperre gegen zwei OHC-Schreiber;
- hält zusätzlich vor jeder Hardwareinitialisierung eine nicht vererbbare Kernel-Sperre für genau eine gesamte OHC-Anwendungsinstanz.

`src/nzxt_rgb.py`:

- enthält eine feste Positivliste dokumentierter NZXT-Effekte;
- validiert Kanal, Farbanzahl, Hexfarben, Geschwindigkeit und Richtung;
- zerlegt topology-sensitive `sync`-Effekte in drei einzelne Lüfterkanäle;
- enthält für den NZXT 2023 RGB Controller keine vom liquidctl-1.16-Treiber abgewiesenen `marquee-4`-/`alternating-4`-/`moving-alternating-4`-Aliasse;
- führt selbst keine Geräte- oder Prozesszugriffe aus.

`src/kraken_control.py`:

- beendet einen zweiten Programmstart vor Qt-Fenster-, Backend- und Hardwareaufbau;
- öffnet kein OpenRGB-Fenster;
- blockiert eine fremd gestartete OpenRGB-Instanz für Schreibzugriffe;
- schließt eigene kurzlebige OpenRGB-Clientprozesse aus der Fremdprozessprüfung aus;
- sammelt asynchrone RGB-Gerätefehler begrenzt im Programm, statt wiederkehrende modale Desktopdialoge zu öffnen;
- sperrt NZXT-/OpenLinkHub-Besitzkonflikte;
- verlangt eine Sitzungsfreigabe;
- sendet statische Änderungen weiterhin seriell; Animationen halten höchstens einen gemeinsamen Mehrgeräteframe gleichzeitig offen und fassen überholte Zwischenbilder zusammen;
- übernimmt variable Zonengrößen nur nach ausdrücklicher Benutzereingabe, prüft sie gegen die vom Server gemeldeten Grenzen und liest die neue Größe zurück;
- verwendet bei Geräten ohne Direct Mode nur tatsächlich gemeldete native Fallbackmodi;
- stoppt nach drei Fehlern;
- startet Profilanimationen nie automatisch;
- besitzt einen bestätigungspflichtigen Komplett-Reset und beendet nur die selbst gestartete Engine.

## Kein automatischer VirusTotal-Upload

Der Release-Scanner parst Python als AST, prüft Shellskripte syntaktisch, validiert Rasterbilder, verwirft aktive/externe SVG-Inhalte und sucht unerwartete ELF-/PE-Dateien. Automatische VirusTotal-Uploads bleiben aus, weil Standarduploads interne Dateien mit Dritten teilen können. Releaseartefakte erhalten reproduzierbare SHA-256-Prüfsummen und können vom Tester selbst zusätzlich gescannt werden.

## Grenzen und reale Hardwaretests

- Der verwaltete Treiber ist weiterhin ein separater OpenRGB-Prozess, kein neu geschriebener OHC-Hardwaretreiber.
- Eine Sitzungssperre kann ein in OpenRGB abstürzendes Gerät nicht zurücksetzen; „RGB komplett zurücksetzen“ beendet jedoch weiterhin die verwaltete Engine und gibt den Gerätebesitz frei.
- Nicht jedes Gerät meldet einen Hardware-/Defaultmodus; vollständige Firmwareübernahme kann deshalb erst nach Neustart oder Kaltstart erfolgen.
- Die ENE-Deduplizierung braucht einen Test mit der konkreten Liste `ENE DRAM` 0/1 und `ENE DRAM DRAM` 6/7.
- LED-Anzahl, Direct-Mode-Fähigkeit und native Fallbackmodi stammen aus der Geräteliste des installierten Backends.
- Die zwei gleichnamigen Sapphire-Einträge müssen auf dem realen PC einmal der Grafikkarte und der B6-Halterung zugeordnet bzw. bei Bedarf vertauscht werden.
- NZXT „Flügel“ sowie die drei Einzelkanäle müssen mit den angeschlossenen F120/F140-Lüftern visuell geprüft werden.
- Suspend/Resume, Gerätewechsel und udev-Zugriff bleiben auf Fedora, Debian, Arch und openSUSE praktisch zu testen.

Bis diese Tests abgeschlossen sind, bleibt Version 3.4.16 intern.
