# Open Hardware Control 3.4.16 INTERN

## Schwerpunkt

Diese interne Version macht manuelle RGB-Geschwindigkeitsänderungen zuverlässig und schützt den sichtbaren Gerätebestand vor vorübergehend unvollständigen OpenRGB-Startresultaten.

## Änderungen

- Regleränderungen werden 360 ms zusammengefasst; die zuletzt gewählte Geschwindigkeit, Farbe, Helligkeit und Richtung gewinnt.
- Eine laufende native NZXT-/GPU-Übertragung wird abgeschlossen, bevor der neueste Stand automatisch folgt.
- SDK-Worker-Bestätigungen sind an die genaue Frame-ID und deren Parametersatz gebunden.
- Der Animationsphasenstart wird bei jeder übernommenen Konfiguration neu gesetzt.
- Die fünf NZXT-Geschwindigkeitsstufen bilden 10–200 % gleichmäßiger ab.
- Eine rein lesende Geräteprüfung läuft höchstens einmal pro Minute.
- Ein großer Inventarabfall wie 7 → 2 wird zweimal verzögert bestätigt; bis dahin bleibt die vollständige Liste aktiv.
- Unveränderte Hintergrundprüfungen lösen keinen Neuaufbau der RGB-Oberfläche aus.

## Sicherheit und Kompatibilität

- OpenRGB bleibt ein separat installiertes, von OHC privat und fensterlos verwaltetes Backend auf `127.0.0.1:6742`.
- Ein separat gestartetes OpenRGB blockiert weiterhin OHC-Schreibzugriffe und wird niemals automatisch beendet.
- Die NZXT-Kraken-LCD-/Kühlungskoordination bleibt unverändert: exklusive USB-Kurzpause, Befehl, Wiederaufnahme desselben Framecache.
- Profile und Einstellungen aus 3.4.15 bleiben kompatibel.

## Installation unter Fedora/Nobara

```bash
cd ~/Downloads
sudo dnf install ./open-hardware-control-3.4.16-0.intern1.noarch.rpm
```

Die RPM-Aktualisierung ersetzt die vorherige Paketversion; persönliche Einstellungen bleiben im Benutzerprofil erhalten.
