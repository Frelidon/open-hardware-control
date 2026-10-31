# Open Hardware Control 3.4.29.55 INTERN

## Reaktionsfähiger Programmstart

- Geräteinitialisierung beginnt erst nach dem ersten Qt-Ereigniszyklus, damit das Hauptfenster vorher gezeichnet und bedient werden kann.
- Die Startprüfung der Laufzeitabhängigkeiten verwendet direkte lokale Fähigkeitsprüfungen und wartet nicht mehr synchron bis zu 30 Sekunden auf ein Shell-Hilfsprogramm.
- Die lokale Levita-/TRCC-Medienbibliothek und ihre Vorschaukarten werden nach dem ersten Fensteraufbau geladen. Vorschaubilder für Videos bleiben wie bisher auf höchstens zwei Hintergrundprozesse begrenzt und im Cache erhalten.

## CoolerControl ohne GUI-Blockade

- Das neue Modul Responsive Startup 1.0 führt die vorhandenen read-only `systemctl`-/`pgrep`-Prüfungen in einem begrenzten, zusammengefassten `QProcess`-Helfer außerhalb des GUI-Prozesses aus.
- Ein noch unbekannter oder fehlgeschlagener Besitzerstatus bleibt fail-closed: OHC behandelt den Mainboard-PWM-Pfad bis zur Bestätigung als belegt.
- Wird CoolerControl während aktiver OHC-Regelung erkannt, stellt OHC die betroffenen Mainboardkanäle weiterhin an Firmware/BIOS zurück. Bestätigte Polkit-Aktionen für Übernahme, Rückgabe und Autostart bleiben unverändert.

## Display-Effekte und schnelleres Anwenden

- Ebene 2 wird in Display-Effekte nicht mehr nur als Textliste gezeigt, sondern als einheitliche Galerie aus Mini-Vorschaukarten aus dem LCD-Studio. Die aktive Karte ist sichtbar markiert und öffnet sich weiterhin zur Bearbeitung im LCD-Studio.
- Die Effektart steht jetzt als oberster Hauptpunkt in den Effekteinstellungen, damit spätere zusätzliche Effekte dort konsistent ergänzt werden können.
- Neue Rauchvideos verwenden die kompatible H.264-Kodierung mit dem schnelleren ffmpeg-Preset `veryfast`; identische Einstellungen verwenden weiterhin den vorhandenen Inhaltscache.
- Wiederholtes Anwenden eines bereits bekannten Effektvideos überspringt den unnötigen kompletten Galerie-Neuaufbau.

## Sicherheit und Grenzen

- Die vorhandene zehnsekündige Levita-Schutzpause, Neuverbindungsbarriere, ein TRCC-Daemon als alleiniger USB-Besitzer, Testmodus und Abschaltrückgabe bleiben unverändert.
- Deutsch, Englisch, Spanisch und Französisch wurden gemeinsam ergänzt und durch den vollständigen Offscreen-Oberflächentest geprüft.
- Interne Testversion. Kein GitHub-Push, Tag oder öffentliches Release wurde erstellt.
