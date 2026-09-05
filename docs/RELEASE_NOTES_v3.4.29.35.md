# Open Hardware Control 3.4.29.35 INTERN

Datum: 03.09.26

Diese Korrekturversion folgt auf 3.4.29.34 und enthält dessen Cache-/Abschaltkorrekturen sowie alle RGB-, ENE-DRAM-, LCD-Bibliotheks- und Oberflächenverbesserungen aus 3.4.29.33. Das Levita-Datenoberflächenmodul bleibt 1.4 unter `modules/lcd_levita/v1_4/`.

Der vollständige reale Fehler wurde nach einem Abziehen des Displays reproduziert: TRCC bewahrte den alten Handshake auf und meldete über `device state` weiterhin `connected=True`. Der darunterliegende BulkLcd-USB-Transport war jedoch geschlossen und verwarf jeden Frame mit `send() called before connect()`. Da der periodische Tick nur das Einreihen eines Frames bestätigte, konnte OHC trotzdem fälschlich „Video läuft“ anzeigen.

Jeder bewusste Design-Anwendevorgang beginnt deshalb nun mit einem tolerierten `device disconnect` über den vorhandenen TRCC-Daemon. Danach muss `device connect` einen echten neuen Handshake erfolgreich abschließen. Erst anschließend folgen Split-Sicherheitszustand, Theme, Maske, Video und Live-Daten. Dieselbe Neuverbindungsbarriere schützt den physischen Farbtest sowie getrennte Helligkeits- und Ausrichtungsänderungen.

Die Reparatur wurde am verbundenen Display praktisch geprüft: Trennen, Neuverbinden, Handshake mit 1600×720 und Modell-ID 64, Rot/Grün/Blau/Schwarz-Übertragung und anschließendes Wiederherstellen des gespeicherten 148-Frame-Themes waren erfolgreich. Danach traten keine weiteren `not connected`-Sendefehler auf.
