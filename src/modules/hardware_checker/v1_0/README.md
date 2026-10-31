# Hardware Checker 1.0

Geführte, ausschließlich lesende Systemprüfung für CPU/SMT/Virtualisierung, PCIe-Grafikkarten,
NVMe-SSDs und Arbeitsspeicher. Normale Linux-/sysfs-Abfragen laufen in einem
begrenzten Hilfsprozess. DMI-Speicherdetails werden optional über eine einzelne
Polkit-Abfrage mit dem fest aufgelösten `dmidecode --type 4,17` gelesen; OHC sieht
oder speichert kein Passwort.

`model.py` enthält reine PCIe-/RAM-Bewertung und Parser. `probe.py` liest
Linux-Systemzustand ohne Schreibzugriff sowie serialfreie Windows-CIM-Daten.
`cards.py` besitzt die wiederhergestellte responsive Übersicht; die Detailtabelle
bleibt separat verfügbar. `page.py` besitzt die Qt-Oberfläche,
Prozessfristen und den ausdrücklich gestarteten, begrenzten glmark2-Lasttest.
Fehlt glmark2, kann das vorhandene Vulkan-Programm `vkcube` denselben kurzen
Messzeitraum abdecken. Ein direkter Klick auf den GPU-Lasttest startet zuerst
selbst die nötige read-only Erkennung, ohne RAM-DMI-Administratorabfrage.
Ein vorzeitig beendeter Grafikprozess bestätigt keine
Messung unter Last; fehlen beide Programme, erklärt die Seite dies sichtbar.
Die Tabelle misst lange Hardwarebezeichnungen und zeigt sie vollständig an.
Der Lasttest ändert keine Takt-, Spannungs-, Lüfter- oder Firmwareeinstellung.
Nicht sicher ermittelbare Sollwerte werden als Hinweis statt als Fehler gezeigt.

Fristen und Signalantworten bleiben an den jeweiligen Hilfs-/Lastprozess
gebunden. Ein früh beendeter Test kann daher keinen später gestarteten Test
scannen oder stoppen; das Beenden leert die Prozessidentitäten vor der
begrenzten Bereinigung, sodass verspätete Antworten wirkungslos bleiben.
