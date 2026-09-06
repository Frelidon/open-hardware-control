# Open Hardware Control 3.4.17 INTERN

## Schwerpunkt

3.4.17 ergänzt die erste unabhängige Kompatibilitätsschicht für exportierte NZXT-ESC-LCD-Profile. Der Import ist bewusst datenbasiert: Open Hardware Control enthält keinen NZXT-ESC-Quellcode und liefert keine fremden Designs, Fonts oder Medien mit.

## NZXT-ESC-Import

- Schema-v3-Profile und bekannte ältere Feldvarianten werden lokal eingelesen.
- Vor jedem Import wird zwingend eine 240×240-Vorschau mit Kompatibilitätsbericht angezeigt.
- Unterstützt werden Messwerte, Text, Trenner, Uhr und Datum; unbekannte Typen bleiben als deaktivierte Ebene erhalten.
- Externe URLs/Webmedien werden nicht automatisch geladen. Lokale Medienverweise müssen in OHC bewusst neu zugeordnet werden.
- Importierte Profile werden nie ungefragt überschrieben, sondern als neue lokale OHC-Kopie gespeichert.

## Profilverwaltung und Editor

- Aktivieren, Bearbeiten, Umbenennen, Duplizieren und Löschen.
- Einzelne Profile können im OHC-eigenen JSON-Format exportiert werden.
- Vollständige ZIP-Sicherung und Wiederherstellung von Profilen, Vorschauen, lokalen Medien, Schriften und LCD-Profileinstellungen.
- „Ungespeicherte Änderungen verwerfen“, „Importierten Originalzustand wiederherstellen“ und „OHC-Standardprofil als neue Kopie anlegen“.
- Sensorquelle, Text, Hex-Farben, Größen, Position, Drehung, Sichtbarkeit und Sperre sind editierbar; Ebenen können per Drag-and-drop sortiert werden.
- Bei eindeutigen CPU-/GPU-Textlabels kann ein Sensorwechsel die passende Beschriftung automatisch mitändern.

## Live-Daten

Direkt bzw. best-effort angebunden sind CPU-/GPU-/Kühlmitteltemperatur, CPU-/GPU-Auslastung, CPU-/GPU-Takt, CPU-/GPU-Leistung, RAM-Nutzung/Gesamtgröße sowie Pumpen- und Lüfterdrehzahl. Nicht verfügbare Linux-Sensoren werden als fehlend dargestellt und führen nicht zu erfundenen Werten.

## Sicherheit und Rechte

NZXT-ESC ist ein unabhängiges Projekt. Open Hardware Control kopiert keinen NZXT-ESC-Quellcode und verteilt keine NZXT-ESC-Designs oder -Medien. Für importierte Dateien gelten die Rechte und Lizenzbedingungen ihrer jeweiligen Urheber. Die Importvorschau lädt keine externen Medien aus dem Internet.

## Interne Pakete

- `open-hardware-control-3.4.17-0.intern1.noarch.rpm`
- `open-hardware-control_3.4.17~intern1_all.deb`
- `open_hardware_control_v3_4_17_INTERN.zip`
- `open-hardware-control-3.4.17-INTERN-source.tar.gz`
- `Entwicklerpaket 3.4.17 INTERN.zip`
