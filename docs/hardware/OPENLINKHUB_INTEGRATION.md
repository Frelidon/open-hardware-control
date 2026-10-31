# Corsair-/OpenLinkHub-Integration in 3.4.29.55 INTERN

## Unterstützter Umfang

Open Hardware Control erkennt eine lokale OpenLinkHub-Installation, den aktiven Dienstkontext und die lokale API. Es liest `GET /api/devices/`, zeigt Geräte, Firmware, Kanäle, Temperatur, Drehzahl, Profil und RGB-Bezeichnung an und öffnet das Web-Dashboard unter `http://127.0.0.1:27003`.

Die App kann einen bereits installierten Benutzerdienst starten, stoppen oder neu starten. Systemweite Dienststrukturen werden nicht erfunden oder ersetzt.

## Bestätigtes Update von OpenLinkHub und Web-UI

OHC prüft ausschließlich den festen offiziellen GitHub-Endpunkt auf eine neuere OpenLinkHub-Version. Eine vorhandene RPM-/DEB-Installation wird nach ausdrücklicher Bestätigung über ihre bereits eingerichteten DNF-/APT-Quellen aktualisiert. Für eine Benutzerinstallation muss `~/.config/systemd/user/OpenLinkHub.service` eindeutig auf ein echtes Arbeitsverzeichnis und dessen `OpenLinkHub`-Programm innerhalb des Home-Verzeichnisses zeigen.

Beim Benutzerpfad akzeptiert OHC nur das offizielle amd64-Release-Archiv mit der von GitHub veröffentlichten SHA-256 und der angegebenen Größe. Links, Gerätedateien, absolute Pfade, Traversierung und übergroße Archive werden abgewiesen. Nach dem Dienststopp wird die neue Version atomar eingesetzt; Konfiguration, Dashboard-/Displayeinstellungen sowie Datenbank/Profile bleiben erhalten. Die vorherige Installation bleibt als lokales Geschwister-Backup bestehen, und ein fehlgeschlagener Neustart löst ein Rollback aus. Die Web-UI gehört zum OpenLinkHub-Paket und wird gemeinsam aktualisiert; nachher kann lediglich ein Browser-Cache-Neuladen nötig sein.

OHC führt kein aus dem Internet geladenes Installationsskript als Root aus und verändert beim User-Space-Update keine root-eigene udev-Regel. Benötigt eine spätere OpenLinkHub-Version neue Systemregeln, bleibt dafür die offizielle Installationsanleitung maßgeblich.

Nach ausdrücklicher Freigabe für die aktuelle Programmsitzung kann die App dokumentierte OpenLinkHub-Befehle für Kühlkanäle, RGB/LCD, Maus, Tastatur, Headset und Netzteil übertragen. Angezeigt werden nur erkannte Geräte und die von der API gemeldeten Kanäle beziehungsweise Profile. Der vollständige RGB-Editor bleibt im Web-Dashboard.

## iCUE NEXUS-Designmanager

Bei einer eindeutig erkannten OpenLinkHub-Benutzerinstallation kann OHC ein
Bild auf 640×48 Pixel vorbereiten und als zusätzliches Nexus-Profil eintragen.
Ein optionales `.ohcnexus.json`-Manifest (Schema 1) darf bis zu zwölf
Schaltflächen mit begrenzter Geometrie, nicht überlappenden Touch-Bereichen und
bekannten OpenLinkHub-Aktionscodes 1–146 beschreiben. Pfadtraversierung,
Symlinks, übergroße Dateien, unbekannte Farben und außerhalb liegende Elemente
werden abgewiesen. Symbole aus beliebigen Pfaden werden absichtlich nicht
übernommen.

Vor jedem Import wird `database/nexus/nexus.json` zeitgestempelt gesichert;
Bild und JSON werden atomar ersetzt. Anschließend wird ausschließlich der
Benutzerdienst neu gestartet. Die Auswahl „Auf NEXUS anzeigen“ verwendet den
dokumentierten lokalen Endpunkt `POST /api/lcd/profile`. Open Hardware Control
besitzt keinen eigenen Corsair-USB-Treiber.

OpenLinkHub rendert generische Profile als statischen Hintergrund mit
Touchflächen; CPU-, GPU- und Zeitansichten sind in OpenLinkHub selbst fest
implementiert. Weitere dynamische Sensorfunktionen erfordern deshalb eine
Erweiterung von OpenLinkHub und lassen sich nicht allein durch das Kopieren
eines Designs hinzufügen.

## Grafische Mausansicht in 3.0.9

Für erkannte Corsair-Mäuse wählt die Anwendung eines von fünf eigenen schematischen SVG-Layouts: kompakt, ergonomisch, symmetrisch, Mehrknopf oder MMO. Diese Grafiken wurden vollständig für Open Hardware Control erstellt, stehen mit dem übrigen Projekt unter GPL-3.0-or-later und kopieren weder Herstellerfotografie noch OpenLinkHub-Bildmaterial.

Über den SVGs liegen anklickbare und per Tastatur erreichbare Hotspots. Eine Auswahl markiert gleichzeitig die Tabellenzeile mit Tastennummer, verständlicher Position und Funktion. Modellnamen wie Scimitar, M55/M75, M65/Dark Core/Ironclaw, Darkstar/Nightsabre, Katar und Harpoon werden einer geeigneten generischen Form zugeordnet. Die Darstellung ist ausdrücklich ein Orientierungsschema, kein maßstabgetreues Produktbild.

Soweit die lokale `/api/devices/`-Antwort Belegungscontainer enthält, übernimmt das Hilfsmodul höchstens 32 kurze Einträge. Unbekannte Rohfelder, lange Gerätekennungen und vollständige Seriennummern werden nicht an die Oberfläche weitergegeben. Liefert die installierte OpenLinkHub-Version keine auslesbare Belegung, werden die üblichen Grundfunktionen klar als Rückfallansicht gezeigt.

Ein Klick auf eine gemeldete Taste öffnet den Belegungsdialog. Unterstützt werden die offiziellen Zuweisungstypen Keine, Medien, DPI, Tastatur, Sniper-DPI, Maus und vorhandenes Makro. Originalfunktion, Gedrückthalten und Ausführen beim Loslassen werden ebenfalls übertragen. Fehlt ein von OpenLinkHub gemeldeter Tastenindex, bleibt die schematische Taste absichtlich nicht beschreibbar; die App rät keinen Index.

Der Makro-Recorder erfasst einzelne Tastendrücke und ihre Pausen nur innerhalb seines sichtbaren aktiven Dialogs. Er greift nicht systemweit auf Eingabegeräte zu und zeichnet keine Passwörter, Mausbewegungen oder gehaltenen Modifikatorkombinationen auf. Pro Aufnahme gelten höchstens 64 Tastenschritte und höchstens fünf Sekunden Pause je Schritt. Danach steht das Makro als vorhandenes OpenLinkHub-Makro für eine Maustaste bereit.

## System- und Benutzerkontext

Medienwiedergabe und virtuelles Audio benötigen laut OpenLinkHub-API-Dokumentation den Benutzerkontext. Bei erkanntem Systemdienst zeigt Open Hardware Control deshalb einen Migrationshinweis und verlinkt die offizielle Benutzerinstallation.

Vor dem Start des Benutzerdiensts muss der systemweite Dienst beendet und deaktiviert werden. Zwei aktive OpenLinkHub-Instanzen dürfen nicht gleichzeitig auf dieselbe Corsair-Hardware zugreifen.

## Datenschutz und Sicherheit

- API-Zugriff nur über IPv4-/IPv6-Loopback oder `localhost`
- keine Zugangsdaten in der API-Adresse
- maximal 4 MiB JSON-Antwort
- kurze Netzwerk- und Prozesszeitlimits
- Seriennummern nur als vierstelliger Suffix
- feste Aktionsliste statt frei wählbarer API-Pfade oder Methoden
- strenge Wertebereiche und erneute Zuordnung gegen die aktuelle lokale Geräteliste
- vollständige Seriennummern bleiben im Hilfsprozess; die GUI erhält nur Suffix und SHA-256-Steuerkennung
- Tastenbelegungen auf höchstens 32 bereinigte Kurzdatensätze begrenzt
- Makroaufnahmen auf 64 Einzeltasten mit begrenzten Pausen beschränkt
- Schreibfreigabe nur für die aktuelle Programmsitzung und Sperre bei Dienstkonflikt
- fest begrenzte User-Service-Aktionen
- Update erst nach ausdrücklicher Bestätigung; feste offizielle Herkunft, veröffentlichte SHA-256, sichere Archivgrenzen, Backup und Rollback

## Offizielle Quellen

- Projekt und Installation: <https://github.com/jurkovic-nikola/OpenLinkHub>
- API: <https://github.com/jurkovic-nikola/OpenLinkHub/blob/main/api/README.md>
- Benutzerinstallation: <https://github.com/jurkovic-nikola/OpenLinkHub/blob/main/install-user-space.sh>
