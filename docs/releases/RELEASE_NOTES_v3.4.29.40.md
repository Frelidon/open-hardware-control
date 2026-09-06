# Open Hardware Control 3.4.29.40 INTERN

Diese interne Version integriert Wallpaper Engine for KDE als eigenen Bereich in Open Hardware Control.

- Die lokale Steam-Workshop-Bibliothek wird schreibgeschützt eingelesen und mit vorhandenen Vorschaubildern angezeigt. Suche und Typfilter trennen Szenen, Videos und Web-Wallpaper.
- Workshop-Wallpaper und eigene Videos lassen sich für alle oder einen einzelnen Plasma-Bildschirm auswählen. OHC nutzt dafür Plasmas dokumentierte Skript-Konfiguration; Steam-Dateien und das CaptSilver-Plugin werden nicht verändert.
- Eine eigene Kategorie zeigt Videos aus einem ausdrücklich gewählten separaten Ordner. Die Steam-Bibliothek beziehungsweise ein Ordner mit `steamapps` wird blockiert, damit der frühere rekursive Massenscan nicht wieder entsteht.
- Pause, Fortsetzen, Vorheriges, Nächstes und Ton umschalten verwenden die lokale D-Bus-Oberfläche des installierten CaptSilver-Plugins.
- „Originale Plasma-Oberfläche öffnen“ startet das KDE-Hintergrundbildmodul für Playlists und sämtliche spezialisierten Plugin-Optionen. Die externe QML-Oberfläche wird nicht kopiert oder unsicher in PySide eingebettet.
- Der CaptSilver-v1.4-Originalzustand bleibt Standard. Eine optionale Leistungsoptimierung setzt ausschließlich 25 FPS, Pause bei Vollbild, 1000 ms Wiederaufnahme, Present Mode Auto und statische Bibliotheksvorschauen. Ein zweiter Button stellt die originalen Werte wieder her.
- Frühere lokale Plugin-Patches, Cache-Builder und Watcher werden weder installiert noch benötigt. Wallpaper-Auswahl, Steam-Abos, Playlists, XWaylandVideoBridge-Fix und Plasma-Sicherungen bleiben von beiden Profilen unberührt.

Open Hardware Control liefert weder Wallpaper Engine noch das CaptSilver-Plugin oder dessen Medien mit. Die Integration ist unabhängig und inoffiziell.
