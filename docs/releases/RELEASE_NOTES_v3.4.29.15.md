# Open Hardware Control 3.4.29.15 INTERN

## Ebene 2 zuverlässig in der Hauptvorschau

Die Karten der zweiten Levita-Ebene aktualisieren nun bei jedem Klick die große kombinierte Vorschau. Ein ausgewählter Bild- oder Videohintergrund aus Ebene 1 bleibt dabei erhalten. Das bisherige Filter, das bei einer Datenoberfläche nur Videos zuließ, wurde entfernt.

OHC extrahiert weiterhin bevorzugt nur die transparente Datenebene aus `Theme.png` und `00.png`. Fehlt einem importierten TRCC-Layout die Datei `00.png` oder lässt sich keine getrennte obere Ebene erzeugen, wird für die lokale Vorschau die vollständige `Theme.png` verwendet. Importierte Dateien werden dabei nicht verändert.

## Vorschau im echten Displayformat

Die Vorschau ist kein über die gesamte Seitenbreite gestrecktes Grafikfenster mehr. Der eigentliche Displaybereich bleibt mittig, besitzt exakt das Levita-Verhältnis 1600×720 und ist auf 960×432 Bildschirmpixel begrenzt. Nicht benötigte Breite gehört wieder zum blauen OHC-Seitenhintergrund und erscheint nicht als seitlicher Leerbalken innerhalb der Displayvorschau.

Der reale PySide6-Offscreen-Test prüft die kombinierte Bild-/Datenebene, den Rückfall auf ein Theme ohne `00.png` sowie die exakte Größenberechnung 800×360.
