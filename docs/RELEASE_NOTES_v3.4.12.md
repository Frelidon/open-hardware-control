# Open Hardware Control 3.4.12 INTERN

Diese interne Version konzentriert sich auf die Bedienbarkeit des RGB-Studios und eine neue LCD-Komposition.

## RGB

- Kraken-Radiatorlüfter sind in der PC-Zeichnung als Kanal 1, 2 und 3 erkennbar und physisch sortierbar.
- Frelidons gespeicherte Reihenfolge entspricht hinten `2`, Mitte `3`, vorne `1`.
- 17 eigene animierte Designs stehen als große Kacheln in den Kategorien Ruhig, Spektrum, Bewegung, Energie und Impuls bereit.
- Der Scrollpunkt bleibt beim Anhalten und bei seriellen RGB-Aktionen unverändert.
- Die RGB-Freigabe kann ausdrücklich im Startprofil gespeichert werden. Sie ist standardmäßig aus und bleibt bei fremdem OpenRGB oder einer zweiten OHC-Instanz blockiert.

## LCD

- Bild oder GIF als Hintergrund plus feste oder animierte Hardwaredatenebene.
- Einstellbare Deckkraft, Größe und Position.
- Live-Aktualisierung für CPU/GPU innerhalb des bestehenden exklusiven CAM-nahen Transportpfads.
- Drei neue eigene Layouts: Neonraster, Radar und Wellenkern.

## Lizenzentscheidung

Die neue Galerie und alle neuen Animationen wurden für OHC neu erstellt. SignalRGB dient ausschließlich als Bedienkonzept-Referenz; dessen Effekte und Grafiken werden nicht übernommen. NZXT bestätigt offiziell den Funktionsansatz „Infographic + Image/GIF“, liefert damit aber keine Lizenz zur Übernahme von CAM-Assets. Community-Inhalte werden erst nach einer separaten Datei-für-Datei-Lizenzprüfung gebündelt.
