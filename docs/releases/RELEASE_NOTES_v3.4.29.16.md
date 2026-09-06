# Open Hardware Control 3.4.29.16 INTERN

## Titelloses Startfenster gezielt blockiert und genauer diagnostiziert

Das neue Protokoll weist das weiterhin sichtbare schwarze Fenster nun einem OHC-eigenen Qt-Widget zu: Es ist ein `QFrame` vom Typ `Window`, besitzt weder Titel noch Objektname oder QWidget-Elternfenster und verwendet die Qt-Standardgröße 640×480. Damit stammt die Oberfläche nicht aus einem eigenständigen OpenRGB-, Polkit- oder TRCC-Prozess.

3.4.29.16 blockiert ausschließlich diese vollständige Signatur vor der Bildschirmausgabe. Benannte Frames, normale Dialoge, Popup-Menüs, modale Fenster und Frames mit einer anderen Größe werden nicht erfasst. Für künftige Abweichungen schreibt die integrierte Diagnose zusätzlich Objekt-ID, Fensterflags, Größenhinweis, Layout, direkte QWidget-Kinder, QObject-Elternkette, Fokus-/Aktivzustand, Native-Status, Programmlaufzeit und Fensteralter ins Log. Der zuletzt gestartete Helferprozess wird als rein zeitliche Korrelation gekennzeichnet und nicht fälschlich als Verursacher bezeichnet.

## Doppelte Levita-Videos nur noch einmal anzeigen

Der auf dem Referenzsystem importierte Projektordner enthält mehrere vollständige TRCC-Sicherungsbäume. Dateien wie `d002.mp4`, `d003.mp4` und `d005.mp4` liegen dadurch jeweils unter dem normalen `TRCC-Themes`-Pfad sowie erneut unter Sicherungs- und `alt`-Verzeichnissen. OHC hatte bisher nur identische vollständige Pfade zusammengeführt und zeigte diese Kopien daher zwei- oder dreimal.

3.4.29.16 verwendet für die sichtbare Bibliothek den vollständigen Dateinamen einschließlich Endung als Identität:

- Groß-/Kleinschreibung wird bei der Erkennung ignoriert;
- `d002.mp4` erscheint genau einmal;
- `d002-copy.mp4` bleibt als bewusst anders benannte Datei erhalten;
- `d002.png` bleibt neben `d002.mp4` erhalten, da die vollständigen Namen verschieden sind;
- normale und kurze Pfade werden vor `alt`, `old`, `backup`, `sicherung`, `kopie`, `copy`, `archive` und `archiv` bevorzugt;
- eine gespeicherte Auswahl auf eine ausgeblendete Kopie wird automatisch auf die beibehaltene Datei umgestellt.

Die Bereinigung betrifft ausschließlich den OHC-Katalog. Es werden keine Originaldateien gelöscht, verschoben oder verändert. Auf dem konkret importierten Ordner reduziert die Regel 2.500 gefundene Medieneinträge auf 558 eindeutige Namen und blendet 1.942 Sicherungskopien aus.
