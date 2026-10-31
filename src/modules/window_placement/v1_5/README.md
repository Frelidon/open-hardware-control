# Hauptfenster-Platzierung 1.5

Dieses Modul hält die persistente Bildschirmwahl unabhängig von Qt-UI und
Hardwarezugriff. `primary` ist der sichere Standard. Eine feste Wahl speichert
den von Qt/KDE gemeldeten Bildschirmnamen statt der veränderlichen Position in
der Monitorliste. Fehlt der gewählte Monitor, fällt OHC für diesen Start auf den
aktuellen Hauptbildschirm zurück, ohne die feste Auswahl zu vergessen.

Der Startmodus wird unabhängig davon als `last`, `maximized` oder `windowed`
normalisiert. Die zuletzt echte Maximierung wird getrennt von der sicheren
Normalgeometrie gespeichert, damit ein maximiertes Fenster ohne sichtbaren
Zwischenschritt wieder groß und ein normales Fenster normal startet.

Der Hauptfenster-Orchestrator hält die Oberfläche während der initialen
Platzierung unsichtbar, setzt den ausgewählten `QScreen` und den gespeicherten
Fensterzustand und gibt erst danach den ersten sichtbaren Frame frei. Nach dem
ersten Wayland-Mapping prüft das Modul den vom Compositor tatsächlich gemeldeten
Bildschirm und korrigiert nur eine Abweichung. Dadurch erscheint ein maximierter
Start nicht mehr kurz klein, ohne dass ein Starttoken von Discover oder einem
anderen Programm dauerhaft den Zielmonitor ersetzen kann.

Unter Wayland können sowohl Qt-Geometrie als auch `QWindow.screen()` nur den
angeforderten Ort wiedergeben, während KWin das Fenster tatsächlich auf einem
anderen Ausgang zeigt. Diese Qt-Werte werden nur noch als Hinweis protokolliert.
`kwin_controller.py` startet nach dem Mapping einen kurzlebigen Hintergrund-
Helfer. `kwin_bridge.py` fragt KWin über dessen Scripting-API selbst nach dem
Ausgang des OHC-Hauptfensters und verschiebt ausschließlich ein Fenster mit
passender Prozess-ID und OHC-Titel auf den gewählten Ausgang. KWin meldet
Vorher/Nachher über einen privaten D-Bus-Rückkanal; nur diese Antwort darf als
bestätigt im Log stehen. Das temporäre Skript wird wieder entladen. Bei
fehlendem KWin bleibt die reine Qt-Platzierung bestehen und der Log zeigt
ausdrücklich, dass eine Bestätigung fehlt. Ein einmaliger Wiederholungsversuch
deckt spätes Mapping ab; keine Dauerschleife und keine globalen KWin-Regeln.

Während dieses einmaligen Startzyklus unterdrückt der Orchestrator interne
Fensterzustandsereignisse. Ein verzögert geladenes Startprofil darf weder den
globalen Startmodus noch die Bildschirmwahl anwenden und startet die Platzierung
nicht erneut. Manuell angewendete Profile behalten ihre bisherige Wirkung.
