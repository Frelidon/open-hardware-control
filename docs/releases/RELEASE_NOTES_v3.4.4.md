# Open Hardware Control 3.4.4 INTERN

## Behobene Ursache

Das Hardwareprotokoll zeigte, dass eine neue OpenRGB-Erkennung noch während des vollständigen RGB-Resets gestartet wurde. Die Geräteliste traf ein, danach beendete der Reset die verwaltete Engine. Die Oberfläche behielt dadurch alte auswählbare Kacheln, obwohl der Backendprozess nicht mehr erreichbar war. Beim anschließenden statischen Grün wurden folgerichtig nur die drei NZXT-Kanäle über `liquidctl` geschrieben.

Version 3.4.4 behandelt Reset, Engine-Neustart und neue Erkennung als geordnete Zustandsfolge. Laufende Erkennungsantworten werden invalidiert, ein während des Resets angeforderter Neustart wird vorgemerkt, und eine bestätigte Schreibfreigabe wird erst nach erfolgreicher neuer Geräteliste aktiv. Nicht erreichbare OpenRGB-Geräte können nicht mehr über einen veralteten Oberflächenzustand ausgewählt werden.

## Doppelte Geräte

Die übermittelten Geräte `0…6` und `7…13` bilden dasselbe sieben Geräte lange Inventar in derselben Reihenfolge. OHC führt dieses Spiegelinventar nun nur dann zusammen, wenn mindestens vier Paare vorhanden sind, der Indexabstand konstant ist und Name, Gerätetyp, Beschreibung, LED-Anzahl, Modi und Zonen jedes Paars exakt übereinstimmen. Zusätzlich werden identische belastbare Seriennummern oder vollständige Hardwarepfade berücksichtigt. Zwei reale gleichnamige RAM-Riegel bleiben getrennt; die gespiegelten Riegel 3 und 4 verschwinden.

Der vermeintlich zweite Sapphire-Eintrag lag ebenfalls exakt sieben Indizes hinter dem ersten und war damit Teil derselben Spiegelung. Er wird nicht länger automatisch als Grafikkartenhalterung behandelt. Die tatsächliche Halterung und einzelne Lüfterstränge müssen über die vom Airgoo-/Mainboard-Controller gemeldeten Zonen beziehungsweise durch den Einzelgeräte-Test identifiziert werden.

## Neue PC-Ansicht

Der Formular-Editor für einzelne Positionen wurde entfernt. Stattdessen gibt es eine große verschiebbare Thermaltake-PC-Ansicht:

- Kraken-360-Radiator mit drei 120-mm-Lüftern oben, Abluft
- zwei normale 120-mm-Frontlüfter, Ansaugung
- drei 120-mm-Reverse-Lüfter an Rückwand/Seite, Ansaugung
- drei 120-mm-Reverse-Lüfter am Boden, Ansaugung
- ein 120-mm-Hecklüfter, Abluft
- Grafikkarte, Halterung, zwei 16-GB-DDR5-6000-Riegel und Pumpenkopf als eigene Blöcke

Blöcke lassen sich direkt verschieben. OHC leitet daraus die Gehäusezone ab und speichert Koordinaten, Luftstromrichtung und Zuordnungen in Einstellungen sowie RGB-/Gesamtprofilen. Gerätekacheln können per Drag & Drop auf einen Block gelegt werden; ein Doppelklick wählt die zugeordneten steuerbaren Geräte aus.

## Noch auf echter Hardware zu prüfen

OpenRGB `1.0~rc2` hat bei einzelnen Controllern weiterhin eigene `ApplyOptions`-/`stl_vector`-Abstürze gezeigt. OHC isoliert solche Geräte weiterhin, kann aber einen Fehler im externen Gerätetreiber nicht selbst reparieren. Die neue Zonenprotokollierung soll im nächsten Test zeigen, ob Airgoo B6/B7 und die Lüfterstränge als einzelne Zonen oder nur als ein gemeinsamer Controller gemeldet werden. Bis diese reale Zuordnung bestätigt ist, sind B6/B7 Anschlussnotizen und keine behauptete automatische Portsteuerung.

Diese Fassung bleibt intern und wird nicht automatisch öffentlich veröffentlicht.
