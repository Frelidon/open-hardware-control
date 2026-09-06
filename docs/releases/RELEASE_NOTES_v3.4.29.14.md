# Open Hardware Control 3.4.29.14 INTERN

## Levita-Videovorschauen ohne blockierende Oberfläche

Das mitgelieferte Benutzerprotokoll zeigte beim Öffnen von „Gallery“ 132 synchrone `ffmpeg`-Aufrufe innerhalb von ungefähr zehn Sekunden und beim nächsten Kategorienwechsel weitere 125. Jede einzelne Karten-Vorschau wartete dabei im Qt-Hauptthread auf das erste Videobild. Dadurch wirkte Open Hardware Control eingefroren.

3.4.29.14 ersetzt diesen Pfad durch eine nicht blockierende Warteschlange:

- höchstens zwei `ffmpeg`-Worker gleichzeitig;
- Fortschrittsbalken und Anzahl der noch ausstehenden Vorschauen direkt im Levita-Studio;
- die ausgewählte große Vorschau wird vor den übrigen Karten eingeplant;
- erfolgreiche Startbilder bleiben anhand von Pfad, Größe und Änderungszeit dauerhaft im OHC-Konfigurationscache;
- unveränderte Videos benötigen bei späteren Programmstarts keinen neuen Decoder-Aufruf;
- unlesbare Dateien werden sechs Stunden lang als fehlgeschlagen gemerkt und können daher keine wiederholte Prozesslawine auslösen;
- jeder einzelne Worker bleibt auf acht Sekunden begrenzt und wird beim Beenden von OHC sauber gestoppt.

Der neue Regressionstest baut 140 ungecachte Videokarten auf, verlangt eine sofortige Rückkehr der Oberfläche, prüft die Grenze von zwei Workern und bestätigt die Wiederverwendung eines dauerhaft gespeicherten Vorschaubilds.
