# Open Hardware Control 3.4.8 INTERN

Diese interne Testversion korrigiert den RGB-Ausgabepfad für Geräte, bei denen Version 3.4.7 zwar einen erfolgreichen SDK-Aufruf protokollierte, die Beleuchtung aber unverändert blieb.

## RGB-Korrekturen

- Vor jedem Direct-Write werden Geräteanzahl, Controllerbeschreibung, aktiver Modus, Zonen und Farbpuffer neu aus dem lokalen OpenRGB-SDK gelesen.
- Vollständig abgebildete Controller werden zoneweise geschrieben. Dies betrifft auf dem Referenzsystem insbesondere ENE DRAM, MSI MYSTIC LIGHT und Airgoo AG-DRGB16.
- Veraltete LED-Zahlen aus der CLI-Liste werden sicher auf die aktuelle SDK-Farbpuffergröße abgebildet.
- Erfolg wird erst nach Rücklesung des kompletten Zielzustands gemeldet. Eine bloß erfolgreich an den Socket gesendete Nachricht gilt nicht mehr als Geräteerfolg.
- Eine separat laufende OpenRGB-Oberfläche oder ein Effects-Plugin wird auch ohne aktiven Serverport erkannt. OHC blockiert dann alle RGB-Schreibaktionen und nennt die PID; der fremde Prozess wird nicht beendet.
- Sind alle drei NZXT-Radiator-Kanäle gewählt, verwendet OHC den im Hardwaretest bestätigten `sync`-Pfad. Einzeln gewählte Kanäle bleiben separat steuerbar.

## Teststatus

Die Pakettests prüfen die SDK-Protokolle 4 und 5, vollständige Zonenpakete, Modus-/Farbrücklesung, Prozesskollisionen, NZXT-Kanalbündelung und die bestehenden Sicherheitsgrenzen. Die physische Wirkung auf Frelidons konkrete RAM-/Mainboard-/Airgoo-Verkabelung muss nach der Installation einmal im Geräte-Testmodus bestätigt werden.

Diese Version bleibt `INTERN` und wird nicht öffentlich auf GitHub veröffentlicht.
