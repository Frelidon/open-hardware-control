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


The .172 `navigation.py` synchronizes Hardware Check/Fix/Supported Devices without duplicating page owners. `supported_devices.py` presents nine described support boundaries with original symbols, localized text, search and verified manufacturer/backend links. Locally confirmed models are distinguished from backend-dependent support.

.175: `device_catalog.py` owns 41 individual model/backend records and reviewed
manufacturer/product destinations; `supported_devices.py` filters category,
vendor and search with stable IDs and per-category vendor memory. Unknown
product URLs produce no button. Existing GPU profile names remain explicitly
backend-dependent, not hardware approval. See `docs/hardware/SUPPORTED_DEVICE_LINKS.md`.
