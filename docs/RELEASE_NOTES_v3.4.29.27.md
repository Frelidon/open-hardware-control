# Open Hardware Control 3.4.29.27 INTERN

**Datum:** 02.09.26

Diese Version repariert die große Levita-Live-Vorschau. Die transparente Grafik der Datenebene 2 wurde beim Skalieren bisher auf Schwarz reduziert und danach über den korrekt geladenen Hintergrund gelegt. Dadurch waren Uhr und Sensorblöcke sichtbar, während das ausgewählte Bild oder Video aus Ebene 1 verdeckt blieb. Ebene-2-Grafiken behalten nun ihren Alpha-Kanal, sodass das angeklickte Ebene-1-Medium unmittelbar darunter sichtbar ist.

Ausgewählte Videos erhalten eine neue, begrenzte Vorschaugeneration mit 16 Bildern bei 4 FPS und 800 Pixeln Extraktionsbreite. Diese Bilder laufen mit 250 Millisekunden Abstand in der großen Vorschau; Ebene 2 bleibt darüber erhalten. Alte Vier-Bild-Vorschaucaches werden wegen der neuen Cachekennung nicht wiederverwendet.

Der gelieferte Coredump belegt außerdem einen Absturz des externen `/usr/bin/trcc` innerhalb von `libusb_open`/`hid_exit`. OHC erkennt einen solchen `QProcess.CrashExit` nun ausdrücklich, stoppt automatische USB-Versuche und fordert zum vollständigen Stromlosmachen des Displays auf. Die Änderung repariert nicht den externen libusb/hidapi-Code, verhindert aber irreführende Erfolgsmeldungen und weitere automatische Zugriffe.

Das Levita-Fachmodul bleibt Version 1.3 unter `modules/lcd_levita/v1_3/`, da Datenmodell, Canvas-Vertrag und Theme-Staging unverändert sind. Geändert wurde die noch als Legacy geführte Medien-/UI-Orchestrierung.
