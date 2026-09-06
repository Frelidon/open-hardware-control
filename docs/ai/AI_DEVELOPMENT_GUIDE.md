# Open Hardware Control — Arbeitsanleitung für Coding-KIs

Diese Anleitung ist der praktische Erweiterungsweg für lokale und webbasierte Coding-KIs. `AGENTS.md` definiert die Sicherheitsregeln, `../project/MODULE_REGISTRY.md` nennt immer die aktuelle Modulversion und dieses Dokument beschreibt die Arbeitsschritte. Bei Widersprüchen gelten Sicherheitsentscheidungen und Tests vor dieser Anleitung.

## Verbindlicher Arbeitsablauf

1. `AGENTS.md` und danach `../project/MODULE_REGISTRY.md` vollständig lesen.
2. Im Register genau ein zuständiges Modul und dessen aktuellen Versionsordner bestimmen.
3. Nur dessen `README.md`, öffentliche Schnittstellen, direkte Abhängigkeiten und Pflichttests laden.
4. Vor Änderungen mit `rg` Aufrufer, Einstellungs-Schlüssel und bestehende Regressionen ermitteln.
5. Reines Modell, Persistenz, Qt-Darstellung und Hardwaretransport in getrennten Dateien halten.
6. Zuerst enge Tests ausführen; vor einem Versionspaket zusätzlich `./scripts/check_release.sh`.
7. Bei Paketierung `../project/RELEASE_BACKUP_POLICY.md` befolgen und nach dem Bau die zwei neuesten vollständigen Sicherungen samt SHA256 prüfen.
8. Bei jeder Quell-, Pfad-, Vertrags- oder Versionsänderung `../project/MODULE_REGISTRY.md` im selben Arbeitsschritt aktualisieren. Dort nur `TT.MM.JJ`, niemals eine Uhrzeit, ein Benutzerkonto oder einen Rechnernamen erfassen.

## Kleine Module für 16 GB VRAM

- Eine normale handgeschriebene Datei bleibt möglichst unter 600 Zeilen und 32.000 Zeichen.
- Spätestens vor 800 Zeilen oder 40.000 Zeichen wird nach Verantwortung geteilt.
- Eine neue handgeschriebene Datei über 1.200 Zeilen oder 60.000 Zeichen ist unzulässig, sofern das Register keine generierte oder vorübergehende Legacy-Ausnahme dokumentiert.
- Funktionen bleiben möglichst unter 80 Zeilen, Klassen unter 300 Zeilen.
- Benennung beschreibt die Verantwortung: `*_model.py`, `*_store.py`, `*_canvas.py`, `*_controller.py`, `*_transport.py` und `*_adapter.py` statt unspezifischer Sammeldateien.
- Nur die aktuelle Modulversion liegt unter `modules/<name>/v<major>_<minor>/`. Git-Historie und Releases sind die Rückfallebene; keine `old`, `backup`, `copy` oder parallelen alten Versionsordner anlegen. Davon getrennt hält der externe Geschwisterordner aus `../project/RELEASE_BACKUP_POLICY.md` die letzten zwei gebauten Gesamtversionen.

## UI-Komponente erweitern

1. Sichtbaren Zustand und Benutzeraktion beschreiben; Hardwarebefehle sind noch nicht Teil des Widgets.
2. Reine Zustandsübergänge in ein Modell auslagern und ohne Qt testen.
3. Qt-Widgets oder Canvas-Elemente in einer eigenen UI-Datei aufbauen. Das Widget meldet Absichten über Callbacks/Signale und importiert nie den Hauptorchestrator zurück.
4. Einstellungen über einen stabilen Schlüssel speichern. Bestehende Schlüssel nicht still umbenennen; eine Migration braucht einen Test.
5. Den dünnen Orchestrator nur mit Konstruktion, Signalverdrahtung und Statusmeldung ergänzen.
6. Tastatur-/Mausverhalten, Rücksetzen, ungültige Werte und Offscreen-Konstruktion testen.
7. Sichtbare Änderungen in Changelog und Release Notes dokumentieren; Modulregister immer aktualisieren.

## Sensor-Komponente erweitern

1. Messquelle, Einheit, Aktualisierungsrate und Zustand „nicht verfügbar“ festlegen.
2. Erkennung und Lesen von Schreiben trennen. Der erste neue Pfad ist read-only.
3. Rohwerte in einem hardwareunabhängigen Modell validieren und normalisieren; keine erfundenen Ersatzwerte als echte Sensorwerte bezeichnen.
4. Gerätebesitz und Konflikte mit NZXT, Mainboard, CoolerControl, OpenRGB oder OpenLinkHub prüfen.
5. Parser-/Grenzwerttests mit aufgezeichneten oder synthetischen Daten ergänzen. Reale Unterstützung erst nach Hardwaretest als bestätigt dokumentieren.
6. UI konsumiert nur den stabilen Sensorvertrag; sie öffnet keine Geräte und schreibt keine sysfs-/USB-Werte.
7. `../hardware/DEVICE_SUPPORT.md`, `../hardware/SUPPORTED_DEVICES.md` und `../project/MODULE_REGISTRY.md` gemeinsam aktualisieren.

## LCD-Komponente erweitern

1. Geometrie, Quelle und Besitzpfad bestimmen; Levita ist 1600×720, Kraken verwendet einen getrennten Transport.
2. Layoutdaten als validiertes Modell abbilden. Position, Darstellung und Live-Datenquelle dürfen nicht im Canvas versteckt sein.
3. Rendering/Interaktion, Persistenz und Backend-Übersetzung in getrennten Dateien halten.
4. Importierte Medien und Herstellerlayouts niemals überschreiben. Levita-`config1.dc` wird nur vom separat installierten TRCC-Decoder gelesen; OHC schreibt ausschließlich ein eigenes Cache-`trcc.json`.
5. Drag-and-drop begrenzen, die Notch-Schutzzone respektieren und logisch zusammengehörige Beschriftung plus Wert als einen Block bewegen.
6. Geräteübertragung bleibt im vorhandenen serialisierten, testmodusgeschützten Backendpfad. Vorschau oder Auswahl allein autorisieren keinen USB-Schreibzugriff.
7. Modell-, Adapter-, statische UI- und Offscreen-Tests ausführen; reale Displayfunktion nicht allein aus einer erfolgreichen Vorschau ableiten.

## Levita Ebene 2 konkret

Aktueller Einstieg ist `modules/lcd_levita/v1_4/README.md`:

- `layout_model.py` besitzt Blöcke, Koordinaten, Gesamt-Offsets und Persistenz.
- `layout_canvas.py` besitzt Drag-and-drop und fordert per Rechtsklick den eingebetteten Editor an; Eigenschaftsänderungen dürfen keine separaten Dialogfenster öffnen.
- `panel_geometry.py` besitzt die getrennt einstellbare obere/untere Rundung der Medienkante vor dem schwarzen Notch-Balken und die davon unabhängige äußere Panelkontur ohne Qt.
- `theme_adapter.py` liest TRCC-Layouts und erzeugt eine unveränderliche Cache-Ansicht.
- `thermalright_display_ui.py` darf diese Teile nur orchestrieren; neue Layout-Fachlogik gehört nicht mehr dort hinein.

Wenn der öffentliche Vertrag erweitert wird, eine neue aktuelle Modulversion anlegen, Importe gezielt umstellen, die vorherige Version aus dem Arbeitsbaum entfernen und das Modulregister im selben Änderungssatz aktualisieren. Eine reine Fehlerkorrektur ohne Vertragsänderung darf in der aktuellen Modulversion bleiben und wird trotzdem im Änderungsregister vermerkt.

## Abschlusskontrolle

- Gehört jede Änderung zum registrierten Modul?
- Bleiben Dateien unter dem Größenbudget oder ist die notwendige Teilung dokumentiert?
- Sind Importgrenzen kreisfrei und Hardware-Schreibpfade unverändert sicher?
- Sind neue Zustände, Fehlerfälle und Persistenz durch Tests abgedeckt?
- Wurden `../project/MODULE_REGISTRY.md`, Status, Entscheidungen und Versionsdokumente passend aktualisiert?
- Wurde weder eine alte Modulkopie noch eine Uhrzeit im Register hinterlassen?
- Liegen nach einem Versionsbau die zwei neuesten vollständigen externen Sicherungen vor und bestehen beide SHA256-Prüfungen?
