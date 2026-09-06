# Open Hardware Control 3.4.22 INTERN

## Schwerpunkt

3.4.22 ist ein gezielter Stabilitäts-Hotfix auf Basis von 3.4.21. Die große Mainboard-Lüftersteuerung bleibt bewusst für 3.4.23 verschoben.

## Behoben

- Der langlebige OpenRGB-SDK-Worker wird bei nativen NZXT-/GPU-Schreibvorgängen nicht mehr beendet. Dadurch bleibt insbesondere der einmal vorbereitete ENE-DRAM-Direct-Zustand erhalten.
- Der RGB-Einzeltest kann das ausgewählte Direct-Gerät einmal neu primen, statt sich auf einen möglicherweise nur logisch gemeldeten Direct-Zustand zu verlassen.
- Ein animiertes RGB-Design wird erst als aktiv bestätigt, wenn sowohl der erste vollständige Direct-SDK-Frame als auch die nativen/NZXT-Befehle erfolgreich bestätigt wurden.
- LCD-GIFs starten wieder: der in 3.4.21 hinzugefügte Skalierungswert wird von `prepare_gif()` korrekt akzeptiert und beim Frame-Preprocessing verwendet.
- Bei einem fehlgeschlagenen LCD-Start bleibt die sichere Rückstellung auf Flüssigkeitstemperatur erhalten.
- Das Laden eines empfohlenen AM5-Profils aktiviert bei verfügbarem CPU-Sensor direkt die Pumpen- und Lüfterkurve auf CPU-Basis.

## Testfokus

- Kaltstart ohne manuelles Öffnen von OpenRGB; beide ENE-RAM-Riegel müssen vom gespeicherten RGB-Profil übernommen werden.
- RGB-Einzeltest der beiden RAM-Riegel und anschließende Rückkehr zu einem OHC-Design.
- Mehrere schnelle RGB-Designwechsel ohne wiederholten SDK-Worker-Neustart.
- Magma Heart, Polar Aurora und eigene GIFs starten mit 100 % sowie veränderter Skalierung.
- Ryzen-AM5-Profil laden: beide CPU-Kurven werden direkt aktiv.
