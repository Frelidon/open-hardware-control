# UI-Leistung und SSD-Cache 1.1

Das Modul animiert seit .170 auf ausdrücklichen Eigentümerwunsch die tatsächliche
Inhaltsseite, während das linke Menü ruhig bleibt. `page_transition.py` blendet
eine Hintergrundebene aus und verschiebt optional die lebende Seite um wenige
Pixel. Vier Stile und 220/380/550 ms (Standard 380 ms) sind auswählbar. Keine
Seitenaufnahmen oder Graphics-Effect-Puffer; Abbruch, Resize, Verbergen und
Shutdown stellen die Originalposition wieder her.

`gallery_preparation.py` erstellt höchstens vier LCD-Karten pro Ereignisrunde
mit einem weichen 8-ms-Zeitbudget. Versteckte Seiten bereiten nach drei Sekunden
ohne Eingabe kleine Portionen vor; Eingaben stellen dies zurück. Größe/Spalten
verwenden Karten erneut. Animationen, Thumbnail-Prozesse und Hardwarestreams
werden dadurch nicht auf versteckten Seiten gestartet; Shutdown stoppt die
eigene Warteschlange. Einzelne Dateidekodierungen können das weiche Budget
überschreiten; es wird keine garantierte physische Lade-/Bildrate behauptet.

`thumbnails.py` dekodiert Karten verkleinert und speichert atomare,
quellversionierte 176×79-PNGs im vorhandenen Budgetcache; Originale bleiben
unverändert. `dynamic_text.py` hält späte Karten/Formulare beim Sprachwechsel
werttreu. Der eigene Größenpflegeprozess und Navigationseffekte werden beim
Beenden begrenzt gestoppt; keine privilegierten oder fremden Prozesssignale.

Der gemeinsame SSD-Cache speichert ausschließlich regenerierbare Katalogdaten
und skalierte Vorschaubilder. Sein Budget ist auf 0, 512, 1024, 2048 oder
4096 MB begrenzt. Ein niedrig priorisierter Helfer entfernt die ältesten
Einträge zuerst. Originalmedien und aktive Hardwaredateien gehören nicht zu
diesem Cache und werden niemals verändert.

Seit 3.4.29.130 erfasst ein globaler Eingabefilter die letzte Benutzeraktion.
Cachepflege beginnt erst nach vier bis fünf Sekunden Eingaberuhe, wird wenn
verfügbar mit `ionice -c 3` sowie im Helfer mit Nice 15 ausgeführt und legt
zwischen begrenzten Scan-/Löschportionen kurze kooperative Pausen ein. Eine
begrenzte JSON-Telemetrie meldet Dauer, geprüfte und entfernte Dateien sowie
Restgröße; der Qt-Thread wartet nicht auf die Dateiarbeit.

Late forms also capture canonical tab captions. Live language changes update
existing QTabWidget titles, including responsive case forms, without replacing
widgets or changing draft values. Empty wide-view tabs retain remembered IDs.

Gallery preparation reserves complete row height before bounded insertion so
first materialization does not repeatedly change scroll geometry.

Videovorschauen entladen beim Verbergen ihre Multimediaquelle vollständig,
damit FFmpeg-Decoderthreads und Bildpuffer nicht pro Tab erhalten bleiben. Nach
einem Seitenwechsel oder Minimieren sammelt ein verzögerter, zusammengefasster
Leerlaufdurchlauf Python-Zyklen ein und gibt unter glibc vollständig freie
Heap-Seiten mit `malloc_trim` an das Betriebssystem zurück. Auf anderen
Allocatoren bleibt dieser optionale Schritt wirkungslos; es gibt weder eine
periodische Schleife noch Auslagerung privater Daten auf die SSD.

The global gallery input filter calls `QWidget.window(widget)` through the Qt
class because LCD studios can store their host in a `window` attribute.
This prevents repeated event-filter exceptions during mouse and keyboard input.

Child additions scan for late tab widgets once per Qt cycle, only within the
OHC window. New timers, processes and unrelated windows never queue a global
tab scan. Deleted hosts and shutdown cancel the context-bound callback. This
restores the bounded `.148` input-filter behavior.


The .172 `adaptive_views.py` uses model and Qt events to size item views by visible content, bounds the resulting height and excludes navigation/combo popups. `compact_panels.py` provides disclosure and responsive columns without replacing themes or background layers. Late forms opt into the same sizing contract.
