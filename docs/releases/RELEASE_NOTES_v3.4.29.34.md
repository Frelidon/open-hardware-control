# Open Hardware Control 3.4.29.34 INTERN

Datum: 03.09.26

Diese Korrekturversion folgt auf 3.4.29.33 und enthält dessen RGB-Studio-, ENE-DRAM-, LCD-Bibliotheks-, Oberflächen- und Dokumentationsverbesserungen vollständig. Das Levita-Datenoberflächenmodul bleibt 1.4 unter `modules/lcd_levita/v1_4/`.

Die intern vorbereiteten Levita-Datenoberflächen werden wieder als vollständige Themes akzeptiert. OHCs privater, inhaltsadressierter Cache verwendet eine echte validierte `trcc.json`, bindet die bereits geprüften lokalen Bild- und Videodateien jedoch absichtlich über symbolische Verknüpfungen ein. Diese Verknüpfungen sind jetzt ausschließlich für diesen Runtime-Pfad zulässig. Der allgemeine Ordnerimport lehnt verknüpfte Konfigurations- und Mediendateien weiterhin ab und folgt ihnen nicht.

Beim kontrollierten Programmende stoppt OHC zuerst den lokalen Levita-Taktgeber und laufende Befehle. Danach wird über den vorhandenen TRCC-Daemon genau einmal `display stop-video` ausgeführt. Der Aufruf läuft offscreen, ist auf 1,5 Sekunden begrenzt und stellt das aktive TRCC-Originaldesign wieder her. Das gilt für das normale Programmende, Tray-„Beenden“, Logout und die bereits behandelten Abschaltsignale; ein nicht abfangbares erzwungenes Beenden des Prozesses kann keine Abschlussaktion ausführen.

Regressionstests decken die reale Befehlsfolge eines verknüpften OHC-Cache-Themes, den weiterhin strikten externen Import sowie den begrenzten shell-freien Shutdown-Aufruf ab.
