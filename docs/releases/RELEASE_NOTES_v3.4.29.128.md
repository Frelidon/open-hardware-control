# Open Hardware Control 3.4.29.128 INTERN

Datum: 01.10.2026

## Oberfläche

- Snapshot-Schwellen und Desktop-/Spielraten erscheinen als moderne Karten
  mit gekoppeltem Regler und exaktem Zahlenfeld.
- Das GPU-Cockpit folgt der freigegebenen Referenz enger: vier kompakte
  Live-Kacheln, breite blaue Leistungs-/Taktbahnen, eindeutige Zahlenfelder
  und eine früher sichtbare interaktive Lüfterkurve.
- Die drei GPU-Arbeitsbereiche Übersicht/Taktung, Lüfter und
  Lasttest/Darstellung bleiben auf breiten Fenstern nebeneinander und fließen
  auf kleineren Ansichten weiter responsiv um.

## Snapshot-Aktionen

- Die aktuell geladene Snapper-Liste kann atomar als UTF-8-JSON exportiert
  werden. Sie enthält ausschließlich Metadaten, nicht die gesicherten Dateien.
- Ein ausgewählter Snapshot ab Nummer 1 kann nach einer ausdrücklichen
  Bestätigung über den festen root-owned Polkit-Helfer gelöscht werden.
- Snapshot 0, beliebige Pfade/Befehle und ein vollständiger Ein-Klick-Rollback
  bleiben ausgeschlossen.

## Sicherheit und Prüfung

- Die bestehende LACT-Kurztest-, Rückstell-, Grenzwert- und
  CoolerControl-Besitzlogik wurde nicht umgangen.
- Vier Sprachen enthalten denselben Satz von 1.808 Nachrichten.
- Reale Offscreen-Render liegen unter
  `docs/images/rendering-evidence/snapshot-manager-3.4.29.128.png` und
  `docs/images/rendering-evidence/gpu-cockpit-3.4.29.128.png`.
- Während Entwicklung und Rendering wurden keine Live-GPU- oder
  Snapshot-Schreibaktionen ausgeführt.
