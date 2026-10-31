# Crash recovery 1.0

Speichert bereits datenschutzbereinigte Anwendungsprotokollzeilen in einer
privaten, begrenzten JSONL-Datei. Nach einem unvollständigen Programmende
werden ausschließlich die letzten fünf Minuten als `last-crash-context.log`
gesichert und für die neue Sitzung zurückgegeben.

Die Dateien werden mit `0600` geöffnet, symbolische Links werden nicht verfolgt
und ein beschädigter Datensatz wird übersprungen, ohne den Programmstart zu
blockieren.
