# Open Hardware Control 3.4.29.29 INTERN

Diese interne Korrektur stellt die vollständige Levita-Zwei-Ebenen-Ausgabe wieder her. TRCC 9.9.11 übernimmt `mask_visible` aus einem Cache-Theme nicht als Laufzeitzustand. OHC aktiviert die zusammengefasste `01.png` deshalb nach `load-theme` ausdrücklich; damit erscheinen das originale Ebene-2-Metallgitter beziehungsweise andere Theme-Grafiken und der rechte Notch-Balken gemeinsam.

Das Hintergrundvideo wird weiterhin durch denselben TRCC-Daemon gerendert, der alleiniger Besitzer des USB-Geräts bleibt. Ein separater langlebiger OHC-Prozess sendet nur `TickDisplay`-Anfragen über den Unix-Socket und schaltet dadurch die bereits im Daemon dekodierten Videoframes weiter. Dieser Prozess erhält zwingend `TRCC_DAEMON=1` und `QT_QPA_PLATFORM=offscreen`, öffnet keine zweite libusb-/hidapi-Sitzung und wird vor Designwechseln sowie beim Stoppen oder Beenden geschlossen.

Die lokale Vorschau behält die begrenzte Folge von 16 Bildern bei 4 FPS bei, skaliert diese Bilder jedoch nur einmal beim Laden. Der 250-ms-Timer tauscht danach fertige 1600×720-Bilder aus und führt keine wiederholte hochwertige Skalierung im UI-Thread mehr aus.

Das Levita-Datenoberflächenmodul bleibt bei Version 1.3. Layoutschema, Dateivertrag und Modulpfad ändern sich nicht; die Korrektur liegt in der schrittweise zu zerlegenden Orchestrierung.
