# Open Hardware Control 3.4.29.20 INTERN

**Datum:** 01.09.26

Diese interne Korrektur gleicht die editierbare Levita-Vorschau mit TRCC Linux und dem echten 1600×720-Display ab. Textkoordinaten werden nun als visueller Mittelpunkt eines zusammengehörigen Blocks interpretiert. CPU, GPU, Uhr, Datum und Wochentag sitzen dadurch in der Vorschau an denselben Positionen wie auf dem Display.

Animierte Vorschauframes ersetzen nur noch das Hintergrundobjekt. Die verschiebbaren Elemente der Datenebene bleiben dabei erhalten, sodass insbesondere die Uhr nicht mitten in einer Ziehbewegung neu erzeugt wird. Die erneute Auswahl der aktuellen Hintergrundkarte lädt beide Ebenen sofort neu; während ein Videoframe vorbereitet wird, bleibt das letzte gültige Bild sichtbar.

Ein Rechtsklick auf einen Datenblock öffnet dessen Bearbeitung nun innerhalb des blauen Vorschaubereichs. Farbe, Schriftgröße und – sofern sinnvoll – Text oder Wertvorlage werden rechts neben dem Canvas geändert. Übernehmen, Abbrechen und Block-Reset schließen das Feld wieder; separate Dialogfenster werden dafür nicht mehr erzeugt. Diese neue Schnittstelle ist als Levita-Datenoberflächenmodul 1.1 unter `modules/lcd_levita/v1_1/` registriert.

Auf der Hauptseite wird die Kraken-Kühlmittelkarte nur angezeigt, wenn ein Kraken verbunden ist und tatsächlich einen Kühlmittelwert liefert. Levita-Systeme ohne Kühlmittelsensor zeigen damit weder eine leere Kraken-Karte noch den bisherigen Platzhaltertext. Die gespeicherte Dashboard-Auswahl wird nicht gelöscht.

Die Änderung führt keinen Hardware-Schreibzugriff in der Vorschau ein. Importierte TRCC-Dateien bleiben unverändert; editierte Themes werden weiterhin ausschließlich im OHC-Cache erzeugt.

Der Release-Prüfer führt die Testsuite nun verbindlich über pytest aus, damit auch funktionsbasierte Regressionstests tatsächlich laufen. Der isolierte Laufzeit-Stub stellt danach die echten PySide6-Module wieder her. Für diesen Stand bestehen 210 Tests.
