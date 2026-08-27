# Open Hardware Control 3.4.0 INTERN

Interne Testversion vom 22. August 2026. Nicht als öffentliches GitHub-Release vorgesehen.

## RGB-Engine

- OHC startet OpenRGB bei Bedarf selbst als privaten, fensterlosen Hardwaretreiber und beendet nur den eigenen Kindprozess.
- Ein manuell gestarteter OpenRGB-Server oder ein OpenRGB-Fenster ist nicht mehr nötig.
- Eine fremd gestartete Instanz wird nicht übernommen: OHC blockiert Schreibzugriffe, bis sie beendet und die Erkennung wiederholt wurde.
- Eine Linux-Prozesssperre verhindert zwei gleichzeitig schreibende OHC-Instanzen.

## Geräte und Gruppen

- Quadratische Gerätekacheln ersetzen die reine Auswahlliste.
- Alle, einzelne oder gruppenweise Auswahl; Drag & Drop zwischen frei benennbaren Gruppen.
- Drei Startgruppen: Arbeitsspeicher, Lüfter und Grafikkarte.
- Unterschiedliche Gruppen können gleichzeitig unterschiedliche OHC-Effekte behalten.
- Gruppe, Zuordnung und Effektkonfiguration werden in Einstellungen und exportierbaren Profilen gespeichert.
- NZXT `led1` bis `led3` erscheinen gemeinsam mit den zusätzlichen RGB-Geräten.

## Korrekturen

- `ENE DRAM` 0/1 plus `ENE DRAM DRAM` 6/7 wird als zwei echte Riegel dargestellt.
- Die längste gemeldete LED-Liste eines Aliaspaars wird erhalten, sodass sämtliche LEDs des Riegels angesteuert werden.
- NZXT-Effektargumente werden vollständig validiert.
- „Flügel“, Marquee und Alternating werden bei `sync` getrennt auf die drei physischen Lüfterkanäle angewendet.

## Komplett-Zurücksetzen

Der große rote Knopf stoppt alle OHC-Animationen, beendet ausstehende Frameprozesse, wählt nur gemeldete Default-/Hardwaremodi, setzt NZXT auf einen sicheren Spektrum-Modus, löscht aktive Gruppeneffekte, entzieht die Sitzungsfreigabe und beendet die verwaltete Engine.

Bei Geräten ohne gemeldeten Hardware-/Defaultmodus kann OHC keine Firmwareübernahme erzwingen. Es gibt das Gerät dann ohne erfundene oder ungeprüfte SMBus-/I²C-Befehle frei; der letzte Zustand kann bis zum nächsten Hardware- oder Kaltstart sichtbar bleiben.

## Teststatus

Automatisiert geprüft werden Parser, Mehrgerätebefehle, private Engineargumente, Besitzsperre, ENE-Deduplizierung, Gruppenvalidierung, NZXT-Kanalaufteilung, alle zehn Effektgeneratoren, Paketstruktur sowie der vollständige Quell-/Bildscanner. Praktische Tests mit konkreten RAM-Riegeln, Grafikkarte und drei NZXT-Lüftern bleiben erforderlich; deshalb bleibt 3.4.0 intern.
