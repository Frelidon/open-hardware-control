# Open Hardware Control 3.4.29.19 INTERN

## Reparierte Levita-Übertragung

Version 3.4.29.18 erzeugte editierbare Ebene-2-Themes korrekt als eigenes Cache-`trcc.json`, blockierte diesen Ordner anschließend aber durch eine ältere OHC-Prüfung, die ausschließlich `config1.dc` akzeptierte. Sichtbar war die Meldung `Kein vollständiges TRCC-Hardwaredesign` mit einem Pfad unter `thermalright-preview/editable-themes/theme-*`.

3.4.29.19 gleicht die Vorprüfung an den tatsächlich installierten TRCC-Linux-Vertrag an. Vollständige Themes dürfen entweder ein Legacy-`config1.dc` oder ein natives `trcc.json` besitzen. Native Dateien werden vor dem Befehl auf begrenzte Größe, JSON-Struktur, Elementliste und exakte 1600×720-Geometrie geprüft. Fehlerhafte oder für andere Displaygrößen bestimmte Dateien bleiben gesperrt.

Bestehende Cacheordner funktionieren ohne Neuerstellung. OHC schreibt weiterhin weder das importierte `config1.dc` noch Originalbilder oder Videos um.

## Flüssigere LCD-Oberfläche

Ein reiner Wechsel der Datenoberfläche baut nicht mehr die vollständige Hintergrundkartenliste mit hunderten Einträgen neu auf. Das versteckte Auswahlmodell löst pro tatsächlicher Auswahl außerdem nur noch eine Vorschau- und Statusaktualisierung statt derselben Arbeit doppelt aus.

## Prüfung

Regressionstests verwenden den exakten protokollierten Pfadtyp `editable-themes/theme-3d6236e94bad47b2aaff04f8`, prüfen den erzeugten `load-theme`-Befehl und weisen fremde 480×480-Geometrie zurück. Die drei bereits vorhandenen realen OHC-Cachethemes wurden lokal und ohne USB-Zugriff erfolgreich durch OHCs neue Vorprüfung akzeptiert.
