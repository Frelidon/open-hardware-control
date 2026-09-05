# Open Hardware Control 3.4.29.10 INTERN

## Zwei echte Displayebenen

Das Levita-Studio trennt Hintergrund und Hardwaredaten jetzt wie das originale TRCC-Programm. In Ebene 1 wird ein lokales Video ausgewählt. In Ebene 2 kann unabhängig davon ein vollständiges importiertes TRCC-Layout gewählt werden. OHC lädt zuerst dessen `config1.dc` mit Positionen, Farben und Sensorzuordnungen und ersetzt danach ausschließlich den Hintergrund durch das Video. Die Hardwarewerte bleiben live darüber liegen und werden nicht als starres Bild in das Video eingebrannt.

Die Auswahl zeigt nur gültige Videos, sobald ein komplettes Hardwaredesign aktiv ist. „Eigene OHC-Werte“ bleibt als alternative obere Ebene mit den bisherigen frei verschiebbaren CPU-/GPU-/RAM-/Uhr-Elementen verfügbar. Die Herstellerdateien werden weder verändert noch kopiert.

Eine neue lokale Ebenenvorschau trennt Beispielwerte und Gestaltung des `Theme.png` vom zugehörigen `00.png` und legt sie im Editor über das ausgewählte Videoframe. Enthält das TRCC-Design eine eigene `01.png`-Maske, wird diese beim Übertragen mit dem rechten Levita-Balken alpha-komponiert; dadurch gehen Rahmen, Verläufe und Beschriftungen des Designs nicht verloren.

## Abgerundeter Levita-Balken und lokale Hover-Vorschau

Der schwarze rechte Levita-Balken besitzt jetzt oben und unten an seiner zum Displayinhalt zeigenden linken Kante einen dezenten Radius von 18 Renderpixeln. Die rechte physische Außenkante bleibt bündig und schwarz. Diese Form ist sowohl in der 1600×720-Editorvorschau als auch in der transparenten Maskendatei enthalten, die im Hardwaremodus an TRCC Linux übergeben wird.

Links neben der lokalen Designliste zeigt eine kompakte Kachel das gerade überfahrene Bild oder TRCC-Layout. Bei gewöhnlichen Videos erzeugt das lokal vorhandene `ffmpeg` höchstens vier kleine Cacheframes, die OHC direkt als kurze Schleife abspielt. Es wird kein externer Videoplayer geöffnet, kein Medium aus dem Netz geladen und kein importiertes Original verändert.

## Verbleibendes leeres Startfenster geschlossen

Die bisherige Offscreen-Grenze für den verwalteten OpenRGB-Server und asynchrone OpenRGB-Clients gilt nun auch für die synchrone `--version`-Abfrage beim Aufbau der Über-Seite sowie den direkten Inventarpfad. Damit kann kein Qt-basierter OpenRGB-Hilfsaufruf beim OHC-Start ein leeres Fenster auf dem Desktop abbilden.

Alle Sicherheits-, Eigentums- und Hardwaregrenzen aus 3.4.29.9 bleiben unverändert.
