# Localization 1.0

Dieser Modulordner enthält den vollständigen Sprachbestand der Oberfläche ohne Qt- oder Hardwareabhängigkeit.

2.153 gleiche stabile IDs in allen vier Sprachmodulen. Der reine Datenbestand nutzt
`dict(enumerate([...]))` für bestehende IDs und explizite neue IDs in `update`;
häufige Produktbegriffe werden beim Laden aus kompakten Platzhaltern ergänzt;
dies spart Formatzeichen ohne einen Text oder eine ID zu entfernen. Die vier
Snapshot-Manager-Blöcke liegen gemeinsam in `snapshot_messages.py` und werden
von jeder Sprachdatei als reine Daten eingebunden. Weitere vierfache Blöcke
liegen fokussiert in `next_version_messages.py`, `retained_lcd_messages.py`,
`retained_feature_messages.py` und `retained_ui_messages.py`. Jede Sprachdatei bleibt
unter dem verbindlichen 78.000-Zeichen-Limit.

- `de.py` ist die kanonische deutsche Quellsprache.
- `en.py`, `es.py` und `fr.py` enthalten Übersetzungen unter denselben stabilen Nachrichten-IDs.
- `catalog.py` prüft eindeutige deutsche Quellen sowie identische ID-Mengen, bevor es die öffentlichen Wörterbücher zusammensetzt.
- `policy.py` behandelt ausschließlich eng begrenzte dynamische Karten-, Zähler- und Farbbeschriftungen.

Ein neuer sichtbarer Text erhält die nächste freie Nachrichten-ID in allen vier Sprachdateien; ein geänderter Text behält seine vorhandene ID. Der vollständige Offscreen-Test prüft zusätzlich die Abdeckung der real aufgebauten Bedienelemente und den Sprachwechsel. Technische IDs, Messwerte und Eigennamen sind die einzigen Ausnahmen.
