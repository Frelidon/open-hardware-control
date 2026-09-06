# Open Hardware Control 3.4.29.31 INTERN

Datum: 02.09.26

Diese Version folgt auf die bereits ausgegebene 3.4.29.30 (einstellbarer rechter Medienradius). Sie ändert die Levita-Geometrie nicht erneut.

Das Panel **Design anpassen** auf der LCD-Seite zeigt Zahlenfelder und Auswahlfenster in lesbarer Größe. Die Checkbox für den schwarzen Balken steht in einer eigenen vollen Zeile, damit sie die Werte daneben nicht mehr zusammendrückt.

Beim Beenden schreibt die Fensterdiagnose nicht mehr in ein bereits zerstörtes Log-Widget. Ein normales SIGTERM oder Qt-aboutToQuit erzeugt dadurch keinen Shiboken-Fehler `QPlainTextEdit already deleted` mehr.

Das Levita-Datenoberflächenmodul bleibt 1.4 unter `modules/lcd_levita/v1_4/`.
