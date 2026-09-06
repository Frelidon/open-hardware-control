# Open Hardware Control 3.4.29.30 INTERN

Datum: 02.09.26

Die rechte Außenkante der Levita-Bild-/Videofläche wird jetzt direkt am Übergang zum schwarzen Kamera-/Notch-Balken abgerundet. Die rote Markierung im Referenzfoto diente ausschließlich zur Orientierung und wird nicht gezeichnet.

Oberer und unterer Radius stehen standardmäßig gekoppelt auf 48 px. In der eingebetteten Oberfläche können beide gemeinsam oder getrennt im Bereich 0–240 px eingestellt werden. Live-Vorschau und erzeugte Hardwaremaske verwenden dieselbe reine Geometriefunktion, während die äußere physische Panelkontur unabhängig bleibt.

Das Levita-Datenoberflächenmodul steigt wegen des geänderten Geometrievertrags von 1.3 auf 1.4. Im Arbeitsbaum bleibt ausschließlich `modules/lcd_levita/v1_4/` als aktuelle Modulversion.
