# Open Hardware Control 3.4.29.21 INTERN

**Datum:** 02.09.26

Diese interne Korrektur schließt die nach 3.4.29.20 offengebliebene Levita-Geometrie und die sofortige Hintergrundvorschau ab. Der schwarze Kamera-/Notchbalken behält eine gerade Innenkante. Abgerundet werden ausschließlich die beiden äußeren rechten Ecken der 1600×720-Displayfläche, in der Vorschau und im erzeugten Cachebild identisch. Die bisherige Innenrundung an der Trennkante zum Bildinhalt entfällt.

Ein Klick auf eine Karte in „Ebene 1 · Hintergrund“ übernimmt deren Bild oder den bereits zwischengespeicherten ersten Videoframe noch im selben Ereignis in die große Live-Vorschau. Ein schwarzer Zwischenzustand entsteht dadurch nicht mehr, sobald eine lesbare Vorschauquelle vorhanden ist. Fehlt der Videostill noch, bleibt der letzte gültige Frame sichtbar, während höchstens zwei Hintergrundarbeiter den neuen Stand vorbereiten.

Die reine Panelgeometrie liegt in `modules/lcd_levita/v1_1/panel_geometry.py`. Das Datenoberflächenmodul bleibt 1.1; der öffentliche Blockvertrag ändert sich nicht. Importierte TRCC-Dateien bleiben unverändert. Vorschau und Kartenauswahl autorisieren keinen USB-Schreibzugriff.

DEB bleibt in den Bau-Skripten enthalten, wird auf diesem Fedora/Nobara-System jedoch übersprungen, weil `dpkg-deb` nicht installiert ist.
