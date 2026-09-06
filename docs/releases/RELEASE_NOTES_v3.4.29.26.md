# Open Hardware Control 3.4.29.26 INTERN

**Datum:** 02.09.26

Diese Version behebt die im realen Levita-Log nachgewiesene Überlastung der USB-Handshakefolge bei mehreren schnellen vollständigen Designwechseln. Das Display blieb dabei weiterhin als `87ad:70db` sichtbar und die Endpunkte `0x01`/`0x81` wurden geöffnet, antwortete nach mehreren erfolgreichen Wechseln aber nicht mehr auf den Bulk-IN-Handshake.

OHC bindet das ausgewählte Hintergrundvideo, die erzeugte Displaymaske und die bearbeiteten Ebene-2-Datenblöcke nun in ein einziges Cache-Theme ein. TRCC kann diese Kombination dadurch in einer verbundenen `load-theme`-Sitzung laden; die bisherigen zusätzlichen USB-Verbindungen für `play-video` und `apply-mask` entfallen. Originale `config1.dc`- und Mediendateien bleiben unverändert.

Vollständige Designwechsel innerhalb von zehn Sekunden nach einem bestätigten Start werden auf die zuletzt gewählte Kombination zusammengefasst. Ein Handshake-Timeout wird insgesamt nur einmal wiederholt. Bleibt der USB-IN-Endpunkt danach stumm, beendet OHC weitere automatische Versuche und fordert zum vollständigen Stromlosmachen des Displays auf.

Das Levita-Datenoberflächen- und Stagingmodul steigt wegen des geänderten Cache-Theme-Vertrags auf 1.3 und liegt ausschließlich unter `modules/lcd_levita/v1_3/`.

An USB-Protokoll, Gerätekennung und den Besitzgrenzen der Kühlung wurde nichts geändert. Die Korrektur ist durch Code- und Offscreen-Prozesstests abgesichert; ein erneuter realer Displaytest erfolgt erst nach vollständiger elektrischer Neuinitialisierung und ausdrücklicher Bestätigung des Benutzers.
