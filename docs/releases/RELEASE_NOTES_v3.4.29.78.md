# Open Hardware Control 3.4.29.78 INTERN

Interner Teststand vom 12.09.26. Kein öffentlicher GitHub-Release.

## Behoben und verbessert

- Die Schriftgrößen der RGB-Designkarten wachsen nicht mehr von Karte zu Karte. Lange Namen werden passend gekürzt, Kategorien und Favoritensterne überlappen nicht.
- Das RGB-Studio zeigt Aktionen, Live-Vorschau und Designgalerie zuerst. Danach folgen PC-Ansicht sowie die tieferen Geräte- und Effektoptionen.
- Die RGB-Vorschau visualisiert auch Geräte mit sehr wenigen LEDs verständlich, ohne die Anzahl oder Daten der echten Hardwareübertragung zu verändern.
- Display-Effekte verwenden Karten und Vorschaubilder wieder, begrenzen die lokale Vorschau auf 20 FPS und starten Videoanimationen erst nach dem ersten sichtbaren Seitenbild.
- Kontinuierliche Vorschauarbeit läuft nur dort, wo sie sichtbar ist: RGB-Ausschnitt, LCD-GIF, Levita-Vorschau samt Thumbnail-Prozessen, Display-Effekt, animierter App-Hintergrund, Wallpaper-Karten und Desktop-Shell-Uhr stoppen beziehungsweise pausieren außerhalb ihrer Oberfläche beziehungsweise ihres Viewports.
- Physische RGB-/LCD-Ausgabe, Sensorabfragen und Kühlungsregelung bleiben im Hintergrund aktiv.
- Wenn das Infobereichssymbol nicht erreichbar ist, beendet Schließen die Anwendung samt sicherer Hardware-Rückgabe, statt einen unsichtbaren Prozess zurückzulassen.

## Validierung

- Vollständiger Offscreen-UI-Aufbau ohne Hardwarezugriff.
- Sichtbarkeits-, RGB-, Display-Effekt-, Wallpaper-, Fenster-, Kühlungs-, Sicherheits-, Lokalisierungs- und Paketierungsprüfungen.
- Release-Prüfsummen und externe Zwei-Versionen-Sicherung werden beim Build erzeugt.
