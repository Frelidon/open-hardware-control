# Sicherheit – Open Hardware Control by Frelidon 3.4.23 INTERN

## Projektstatus

Open Hardware Control ist eine **experimentelle Open-Source-Beta**. Die Software wird ohne Garantie bereitgestellt. Sie ersetzt weder die Schutzfunktionen der Gerätefirmware noch die Temperaturüberwachung des Mainboards.

## OpenLinkHub-Modul

Die OpenLinkHub-Integration akzeptiert nur `http://` auf IPv4-/IPv6-Loopback oder `localhost`. Externe Hosts, Zugangsdaten und API-Unterpfade werden verworfen. Antworten sind auf 4 MiB begrenzt und werden mit kurzen Zeitlimits gelesen.

Seriennummern werden nur mit den letzten vier Zeichen an die Oberfläche übergeben. Seit Version 3.0.4 wird zusätzlich eine nicht rückrechenbare SHA-256-Steuerkennung erzeugt. Erst im lokalen Hilfsprozess wird diese unmittelbar vor einem erlaubten Schreibbefehl gegen die aktuelle Geräteliste aufgelöst.

Gemeldete Maustastenbelegungen werden auf höchstens 32 bereinigte Kurzdatensätze begrenzt. Die eigenen SVG-Schemata benötigen keine externen Bildabrufe. Version 3.0.9 erlaubt nur dokumentierte Zuweisungstypen. Makroaufnahmen sind sichtbar, fensterlokal und auf 64 Einzeltasten begrenzt; verdeckte systemweite Eingabeaufzeichnung findet nicht statt.

Direkte Corsair-Schreibzugriffe sind beim Programmstart gesperrt, gelten nach Bestätigung nur für die aktuelle Sitzung und sind bei einem Dienstkonflikt nicht freigebbar. Die App akzeptiert keine frei wählbaren API-Pfade, Methoden oder Nutzlasten. Jede Aktion besitzt ein festes Schema und begrenzte Wertebereiche. Start, Stopp und Neustart bleiben ausschließlich für den vorhandenen OpenLinkHub-Benutzerdienst erlaubt. Der systemweite Dienst wird niemals automatisch geändert.

Wenn Benutzer- und Systemdienst gleichzeitig laufen, muss eine Instanz beendet werden, bevor die Hardware weiter bedient wird. Vollständige Corsair-Einstellungen erfolgen im lokalen OpenLinkHub-Web-Dashboard.

## RGB-Studio und OpenRGB

- OpenRGB ist nicht eingebettet und bleibt ein separat installierter Prozess. Open Hardware Control übernimmt weder dessen Hardwaretreiber noch den C++-Code des Effects Plugins.
- Der Adapter akzeptiert ausschließlich IP-Loopback und verwendet fest `127.0.0.1:6742`. Ein externer Host kann nicht über Oberfläche, Profil oder Kommandozeile eingetragen werden.
- Vor jedem Auftrag muss der lokale Port erreichbar sein. Erkennung und native Nicht-Direct-Modi enthalten ausdrücklich `--client 127.0.0.1:6742`; Direct-Schreibzugriffe gehen über `openrgb_sdk.py` ausschließlich an dieselbe geprüfte Loopback-Adresse. Ein stiller Rückfall auf OpenRGB-Standalone-Hardwarezugriff ist ausgeschlossen.
- Gerätenummern, Modi, Hex-Farben, Helligkeit und LED-Anzahl werden begrenzt und ohne Shell als Argumentliste übergeben.
- Schreibzugriffe sind beim Programmstart gesperrt und gelten nach Warnbestätigung nur für die laufende Sitzung.
- Ein vom aktiven NZXT-Modul erkanntes NZXT-Gerät bleibt im OpenRGB-Pfad gesperrt. Dasselbe gilt für Corsair-Geräte, solange OpenLinkHub erkannt ist.
- Softwareanimationen benötigen den vom Gerät gemeldeten Direct Mode, übertragen über den begrenzten lokalen SDK-Helfer höchstens einen Prozess/Frame gleichzeitig und stoppen nach drei aufeinanderfolgenden Fehlern.
- Open Hardware Control startet das installierte Backend bei Bedarf selbst als privaten, fensterlosen Kindprozess und beendet nur den selbst gestarteten Prozess.
- Eine fremd gestartete OpenRGB-Instanz wird für OHC-Schreibzugriffe gesperrt; zusätzlich verhindert eine Prozesssperre zwei gleichzeitig schreibende OHC-Instanzen.
- Gerätegruppen, ENE-DRAM-Deduplizierung und NZXT-Effektargumente werden vor jedem Hardwarebefehl validiert.
- RGB-Profile laden Einstellungen und Gerätewunsch, starten aber nie automatisch eine Softwareanimation.

## Sicherheitsmodell

- Die grafische Anwendung läuft als normaler Benutzer und verwendet kein `sudo`.
- Hardwarebefehle werden ohne Shell über Qt `QProcess` an `liquidctl` übergeben.
- Die mitgelieferte udev-Regel beschränkt den Zugriff auf die bekannten NZXT-USB-IDs und verwendet `0660` plus `uaccess`.
- Die Anwendung enthält keine Telemetrie, keinen Cloud-Dienst und keine automatische Netzwerkübertragung.
- Diagnoseberichte werden lokal erstellt, sind rein lesend und werden mit Dateirechten `0600` gespeichert.
- Beim Desktop-Autostart beginnt ein gespeicherter experimenteller LCD-Modus erst nach zehn Sekunden. Ein vorher erkannter echter Absturz blockiert die automatische Wiederaufnahme weiterhin.
- Ein geordnetes Desktop-Sitzungsende löscht den Crashmarker vor der USB-Bereinigung; ein hart beendeter oder abgestürzter Prozess behält den Sicherheitsfallback.

## KDE-Desktop-Designs

- Der Bereich ist ab 3.4.1 ausdrücklich experimentell, standardmäßig ausgeschaltet und aus Menü sowie Navigation verborgen. In diesem Zustand erscheint auch kein automatisches Paketangebot.
- Das Modul ist ausschließlich in einer erkannten KDE-Plasma-6-Sitzung aktiv.
- Eine Vorschau führt keinen Schreibbefehl aus; das Anwenden und Wiederherstellen erfordern jeweils einen eigenen Bestätigungsdialog.
- Vor dem Anwenden werden nur die ausdrücklich berührten KDE-/Plasma-Konfigurationsdateien und OHC-Integrationsdateien in ein datiertes Benutzer-Backup kopiert.
- Ein Transaktionsmarker erkennt unterbrochene Änderungen. Zuerst wird das Backup geladen; schlägt auch dies fehl, folgt KDE Breeze Light als Notfallzustand.
- Backup-Importe akzeptieren nur erlaubte relative Pfade und reguläre Dateien innerhalb fester Größenlimits und prüfen jede Datei gegen SHA-256.
- Die Windows-8/8.1-Kachelübersicht liest lokale `.desktop`-Dateien, verwirft Shell-/Interpreterstarter und startet ausschließlich bereinigte Argumentlisten ohne Shell.
- Das Modul läuft ohne Administratorrechte, verwendet keine Shell, lädt keine Designs aus dem Internet und fügt keine Paketquellen hinzu.
- Die vier mitgelieferten SVG-Hintergründe und alle OHC-Symbole/Mauszeiger wurden für Open Hardware Control erstellt; Microsoft-/Apple-Logos, -Schriften, -Originalzeiger und -Hintergründe sind nicht enthalten.
- `BUILD_CHANNEL=INTERN` verhindert eine versehentliche Veröffentlichung durch die mitgelieferten GitHub-Skripte.

## Mainboard-Lüftersteuerung ab 3.4.23

Die Mainboard-Funktion schreibt ausschließlich in vom Linux-hwmon-Subsystem bereits bereitgestellte `pwmN`-/`pwmN_enable`-Dateien. OHC öffnet keine Roh-I/O-Ports, führt keine eigenen SMBus-Registersequenzen aus und umgeht weder Secure Boot noch MOK.

Ab 3.4.23.1 bleibt die GUI auch dann unprivilegiert, wenn der Kernel die NCT6687-PWM-Dateien root-schreibbar (`0644`) bereitstellt. Ein separat installierter, root-eigener Polkit-Helfer akzeptiert keine beliebigen Pfade oder Shell-Kommandos, sondern ausschließlich begrenzte Aktionen für den automatisch erkannten `nct6687`-hwmon: Kanäle 1–8, PWM 0–100 %, Firmware-Rückgabe und den Treiber-Watchdog.

- Eine reine Geräteerkennung ist schreibfrei.
- Ein PWM-Kanal darf erst nach dem ausdrücklich bestätigten 70-%-/10-s-Sicht-/Hörtest mit RPM-Beobachtung für automatische Regelung aktiviert werden; Mainboardname und `pwmN` werden niemals blind einer physischen Lüftergruppe zugeordnet.
- Der Kalibrierungstest speichert den vorherigen PWM-/Enable-Zustand und versucht ihn nach zehn Sekunden auch dann wiederherzustellen, wenn die physische Zuordnung nicht bestätigt wird.
- Die automatische Regelung schreibt nur Kanäle, die zugleich schreibbar, kalibriert und einzeln aktiviert sind.
- Drei aufeinanderfolgende fehlende Sensorwerte lösen für den betroffenen aktiven Kanal einen 70-%-Fallback aus. Ab 90 °C fordert die Regelung 100 % an. Diese Softwarefallbacks ersetzen keine BIOS-/Firmware-Schutzfunktionen.
- Beim Abschalten der OHC-Regelung und beim geordneten Programmende versucht OHC, die Firmware-/BIOS-Steuerung über den vom Treiber angebotenen `pwmN_enable`-Modus wiederherzustellen. Bietet nct6687d zusätzlich `fan_control_watchdog` an, wird während aktiver OHC-Regelung ein 10-s-Lease aufgefrischt; endet der steuernde Prozess unerwartet, kann der Treiber geänderte Kanäle selbst auf die zuvor gesicherte Firmwarekurve zurückstellen. Ein harter Stromausfall kann naturgemäß keinen letzten Softwarebefehl garantieren.
- Ist ein sysfs-PWM-Kanal für den aktuellen Benutzer nicht schreibbar, versucht OHC keinen privilegierten versteckten Schreibweg. Die Anwendung zeigt stattdessen Treiber-/Secure-Boot-Diagnose und Einrichtungshinweise.

Vor der ersten produktiven Nutzung müssen die realen Lüftergruppen einzeln kalibriert und ihre Drehzahlen beobachtet werden.

## Kühlung

- Pumpenwerte unter 30 Prozent und Lüfterwerte unter 20 Prozent erfordern eine ausdrückliche Bestätigung.
- CPU-Temperaturkurven dürfen bei steigender Temperatur nicht langsamer werden.
- Eine CPU-Kurve endet abhängig vom AM5-Profil sicher bei 85 oder 90 Grad Celsius mit 100 Prozent; 20–50-Grad-Altkurven werden als frühere Flüssigkeitskurven migriert.
- Die Manuell-/Kurven-Schaltflächen übertragen die gewählte Betriebsart sofort; die feste grüne Markierung wechselt erst nach erfolgreichem Gerätebefehl und bleibt bei Fehlern im letzten bestätigten Zustand.
- Das reine Bearbeiten eines Reglers oder einer Kurventabelle verändert die aktive Kraken-Betriebsart noch nicht.
- Das sichere Standardprofil setzt Pumpe und Lüfter auf 65 Prozent und aktiviert die automatische kritische Umschaltung.
- Die automatische 100-Prozent-Umschaltung funktioniert nur, solange App, USB-Verbindung und Statusabfrage funktionieren. Sie ist kein hardwareseitiger Notfallschutz.

## LCD

Der Wiederholungs-Fallback, die Uhr und die Live-Hardwaredesigns erzeugen regelmäßig neue LCD-Uploads. Es ist nicht ausreichend dokumentiert, ob und wie häufige Uploads den Displayspeicher langfristig belasten. Deshalb:

- sind wiederholte Uploads nach dem Update zunächst ausgeschaltet;
- erscheint vor dem Aktivieren eine Warnung;
- sollte der Fallback nur verwendet werden, wenn das Bild tatsächlich zurückspringt;
- ist die LCD-Uhr ausdrücklich experimentell.
- stellt ein geordnetes echtes Programm-/Sitzungsende nach dem Streamstopp synchron die originale Flüssigkeitstemperaturanzeige wieder her; ein harter Stromverlust kann naturgemäß keinen letzten USB-Befehl mehr übertragen.

## Live-Hardwaredesigns in 2.9.21

- Das kleinste wählbare Aktualisierungsintervall beträgt fünf Sekunden.
- Vor der ersten Aktivierung erscheint eine dauerhafte Experimentalwarnung.
- Nur ein LCD-Schreiber ist gleichzeitig aktiv: Hardwaredesign, Uhr, Bild-Fallback und GIF-Streamer werden gegenseitig gestoppt beziehungsweise koordiniert.
- Drei fehlgeschlagene Uploads aktivieren den bestehenden Sicherheitsfallback auf die Flüssigkeitstemperatur.
- Ein unsauber beendeter Live-Modus wird beim nächsten Start nicht automatisch fortgesetzt, bevor die Standardanzeige sicher wiederhergestellt wurde.
- CPU- und GPU-Werte werden rein lesend aus Linux-hwmon gelesen. Die GPU-Erfassung steuert keine GPU- oder Grafikkartenlüfter.

## Animierte Hardwaredaten in 2.9.23

- CPU- und GPU-Temperaturen werden während der Animation alle zwei Sekunden rein lesend aus Linux-hwmon gelesen. Es werden keine GPU-, Lüfter- oder Tuningwerte verändert.
- Bei einer sichtbar geänderten ganzen Gradzahl erzeugt ein separater Spawn-Prozess einen vollständigen neuen Phasencache. Der USB-Prozess übernimmt nur erfolgreich fertiggestellte Caches als Ganzes.
- Die Wassertemperatur bleibt der letzte vor dem Stream sicher gelesene Kraken-Wert. CPU- und GPU-Werte werden weiter live aktualisiert; die kleinen `LIVE`-/`LETZTER WERT`-Markierungen werden in 3.0.9 bewusst nicht mehr gerendert.
- Während des CAM-Raw-Streams bleiben normale Kraken-Statusabfragen pausiert. Manuelle Pumpen-, Lüfter-, Kurven- und Profiländerungen verwenden eine koordinierte USB-Kurzpause; sie laufen niemals gleichzeitig mit einem LCD-Frame.
- Der Streamer bestätigt die Freigabe erst nach geschlossenem HID-/Bulk-Zugriff. Erst nach leerer liquidctl-Warteschlange darf derselbe Streamer wieder verbinden und die Animation aus dem vorhandenen Framecache fortsetzen.
- Zeitüberschreitungen bei PAUSE oder RESUME führen zum Sicherheitsstopp und nicht zu einem zweiten parallelen Schreibversuch.
- Die App weist vor dem ersten Start ausdrücklich auf diesen Zustand und die unbekannten Langzeitwirkungen häufiger LCD-Uploads hin.
- Die Animationen verwenden höchstens 25 FPS Inhalt und werden durch denselben exklusiven Gerätepfad, dieselbe ACK-Prüfung und denselben 12-Sekunden-Watchdog wie eigene GIF-Dateien übertragen.
- Ein Fehler oder ausbleibendes Lebenszeichen beendet die Animation und aktiviert den vorhandenen Flüssigkeitstemperatur-Sicherheitsfallback.
- Schlägt nur die Erzeugung eines neuen Livewert-Caches fehl, bleibt der letzte vollständige Cache aktiv; die UI protokolliert den Fehler.

## Experimenteller GIF-Raw-Streamer in 2.9.20

- Der Streamer akzeptiert nur Kraken 2023 `1e71:300e` und Firmware-Hauptversion 2.
- Vor jedem Start-/Endbefehl werden alte HID-Berichte verworfen; nur `37 01` beziehungsweise `37 02` gelten als passende Antwort.
- Der phasenstabile Standard überträgt vorbereitete LCD-Phasen streng in Reihenfolge. Ein neuer Frame beginnt erst nach dem vollständig bestätigten `37 02`-Ende; Transfers werden nie überlappt und nie in Aufhol-Bursts gesendet.
- Einzelne Timingüberläufe werden nur bei realem USB-Spielraum und höchstens in 0,25-ms-Schritten abgebaut.
- Die GIF-Loop-Warnung ist nur eine Wahrscheinlichkeitsprüfung und verändert oder blockiert die ausgewählte Datei nicht.
- Während des Streams pausieren normale Kraken-Statusabfragen. Neue Pumpen-/Radiatorlüfterbefehle werden nur innerhalb der bestätigten PAUSE-/RESUME-Übergabe gesendet, damit kein zweiter Prozess dieselbe Geräteverbindung stört.
- Bereits in der Kraken gespeicherte Pumpen-/Lüfterkurven laufen hardwareseitig weiter. Vor dem Test muss deshalb eine sichere Kurve im Gerät gespeichert sein.
- Die App-basierte CPU-Assistenz und automatische temperaturabhängige 100-Prozent-Umschaltung können ohne neue normale Statuswerte während des Streams nicht zuverlässig reagieren. Manuelle Befehle funktionieren, ersetzen aber keine sichere Hardwarekurve.
- Nach einem sauberen Stop werden Status und Kühlbefehle automatisch freigegeben.
- Bleibt nach Beginn des Hardwarezugriffs länger als zwölf Sekunden ein Lebenszeichen aus, wird der Helfer beendet und die Flüssigkeitstemperaturanzeige wiederhergestellt.
- Die Funktion führt keine Firmwareaktualisierung durch.

## Diagnose und Datenschutz

`kraken-control-diagnostics` führt keine Initialisierung und keine Schreibbefehle aus. Es sammelt nur die für Hardwarekompatibilität relevanten System-, USB-, udev- und liquidctl-Daten. Seriennummern, Home-Verzeichnisse, Benutzerkennungen, Hostnamen sowie Machine- und Boot-IDs werden entfernt. Berichte sollten vor einer Veröffentlichung trotzdem manuell kontrolliert werden.

Auch die kopierbare Programmausgabe kürzt Home-Pfade und entfernt typische Serien- und Systemkennungen.

## Abhängigkeiten

Sicherheitsaktualisierungen für `liquidctl`, Python, PySide6/Qt und Pillow sollten zeitnah installiert werden. Öffne nach Möglichkeit nur vertrauenswürdige Bilddateien.

## Sicherheitsprobleme melden

Sicherheitsprobleme sollten nicht sofort mit vollständigen persönlichen Diagnoseinformationen öffentlich gepostet werden. Teile zunächst nur eine kurze Beschreibung, die Programmversion und die betroffene Hardware. Ein öffentlicher Kontaktkanal wird ergänzt, sobald die separate Projektadresse feststeht.

## CPU-Temperatur-Assistenz in 2.7

Die Assistenz liest AMD-Temperaturen ausschließlich über den Linux-k10temp-hwmon-Treiber. Ab einem profilspezifischen Schwellwert setzt sie erhöhte feste Kraken-Werte; nach Abkühlung werden die gespeicherten Wasserkurven wiederhergestellt. Bei einem Absturz können erhöhte, aber sichere feste Werte bestehen bleiben. CPU-Tjmax darf nicht als Kraken-Wassergrenze verwendet werden.

## udev und Schreibzugriff

Kurvenänderungen benötigen Lese- und Schreibzugriff auf das passende `/dev/hidraw*`. Version 2.8 prüft diesen Zugriff vor Schreibbefehlen und bietet eine polkit-gestützte Reparatur der mitgelieferten Regel an.

## Expertenmodus in 2.8

Der Expertenmodus öffnet die Eingabebereiche der Kraken-Wassertemperaturgrenzen weit und hebt die automatische Sortierung von Warn- und Kritisch-Grenze auf. Er ändert keine physikalische Schutzgrenze der Hardware. Ungeeignete Werte können Warnungen und die automatische 100-Prozent-Umschaltung unwirksam machen. Vor der Aktivierung erscheint deshalb eine ausdrückliche Bestätigung. Beim Deaktivieren werden wieder die vorsichtigen Standardbereiche verwendet.

Die LCD-Uhr kann ihr aktuelles Minutenbild zusätzlich in einem einstellbaren Intervall erneut senden. Diese Wiederholung ist unabhängig von der Aktualisierung zum Minutenwechsel und bleibt wegen unbekannter Langzeitwirkungen häufiger LCD-Uploads experimentell.

## Abhängigkeitsinstallation ab 2.8.1

- Die Anwendung installiert niemals Pakete ohne vorherige Bestätigung.
- Unterstützt werden ausschließlich die fest codierten Fedora/Nobara-Pakete `liquidctl`, `python3-pyside6` und `python3-pillow`.
- Es werden keine zusätzlichen Paketquellen eingerichtet und keine Paketnamen aus Benutzereingaben übernommen.
- Die eigentliche Installation läuft über DNF und die normale polkit-/pkexec-Administratorabfrage.
- Auf anderen Distributionen zeigt die Anwendung nur die fehlenden Pakete an; eine automatische Installation erfolgt dort nicht.

## Profile und animierte Hintergründe ab 2.9

- Profile sind lokale JSON-Daten und führen keine beliebigen Shellbefehle aus.
- Hardwarewerte aus Profilen laufen weiterhin durch die vorhandenen Berechtigungs- und Sicherheitswege.
- Profile aus unbekannten Quellen sollten vor dem Import geprüft werden.
- Prozedurale Hintergründe greifen nicht auf Netzwerk, Kamera, Mikrofon oder externe Dateien zu.
- 60 FPS können CPU-/GPU-Verbrauch erhöhen; die Pause bei inaktiver App ist standardmäßig vorgesehen.
- Die Anzeigeeinstellung ändert ausschließlich die App-Skalierung, nicht die Systemauflösung.

## Aktionsprotokoll ab 2.9.1

Das In-App-Log erfasst bewusst viele Bedienaktionen zur Fehlersuche. Es protokolliert keine Tastatureingaben Zeichen für Zeichen und keine Passwörter. Textwerte werden gekürzt und durch die vorhandene Datenschutzbereinigung geleitet. Vor einer öffentlichen Weitergabe sollte der Bericht trotzdem kurz geprüft werden.
