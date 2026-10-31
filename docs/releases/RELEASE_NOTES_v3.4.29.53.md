# Open Hardware Control 3.4.29.53 INTERN

Diese interne Version beseitigt den stehenbleibenden Levita-Bildschirm beim echten Beenden. OHC stoppt zuerst seine lokalen Video- und Hilfsprozesse und löst das Display anschließend mit dem dokumentierten TRCC-Daemonbefehl `device disconnect` aus der laufenden Softwaresteuerung. Da danach keine Live- oder Keepalive-Frames mehr gesendet werden, kehrt die Levita nach dem eigenen Firmware-Zeitlimit von ungefähr zwei bis drei Sekunden zu ihrem eingebauten Thermalright-Standardbild zurück.

Nach einem bestätigten echten Displayzugriff läuft außerdem ein kleiner, vom Hauptprozess getrennter Pipe-Wächter. Ein sauberer Programmabschluss bestätigt ihm die erfolgreiche Rückgabe und beendet ihn ohne zweiten Hardwarezugriff. Verschwindet OHC dagegen unerwartet, versucht der Wächter genau einmal denselben begrenzten, offscreen ausgeführten Daemon-Disconnect. Die reine Vorschau bleibt schreibfrei und startet keinen Wächter. Nicht abfangbarer Stromverlust oder das gleichzeitige harte Beenden sämtlicher Prozesse kann naturgemäß keine Abschlussroutine garantieren.

Der Kraken-Pfad wurde gegen die zentrale Shutdown-Reihenfolge geprüft und bleibt unverändert aktiv: Ein laufender LCD-Stream wird zuerst synchron beendet, danach stellt liquidctl die originale Flüssigkeitstemperaturanzeige wieder her. Für eine unsauber beendete experimentelle Kraken-LCD-Sitzung bleibt zusätzlich der vorhandene persistente Wiederherstellungsmarker erhalten.

Die Version enthält weiterhin die modularen vollständigen Sprachdateien für Deutsch, Englisch, Spanisch und Französisch sowie alle drei neuen projekt-eigenen 1600×720-Levita-3D-Animationen. Es gibt keinen GitHub-Push, Tag oder öffentlichen Release.
