# Open Hardware Control 3.4.20 INTERN

> Interner Entwicklungs- und Teststand. Nicht als öffentlicher GitHub-Release vorgesehen.

## Schwerpunkt

3.4.20 ist ein Bedienungs-, Import- und Startstabilitäts-Update. Es konsolidiert den stark gewachsenen LCD-Bereich, ergänzt eine integrierte Hilfe und acht eigene LCD-Animationen und behebt reale Regressionen bei ENE-DRAM/OpenRGB sowie beim minimierten Autostart.

## Änderungen

- ENE-/OpenRGB-RAM wird pro frischer Worker-Sitzung einmalig in Direct/Custom geprimt und danach ohne wiederholte Moduswechsel angesteuert.
- Der Tray-Autostart zeigt keine Setup-, Lüfterprofil- oder sonstigen modalen Startdialoge.
- Auf einer frischen Installation ist die Sprache die erste Assistentenseite; Deutsch, Englisch, Spanisch und Französisch werden sofort angewendet.
- Neuer Hilfe-Button unten links sowie F1 mit Suche, Anleitungen und Sprüngen zu den passenden Programmseiten.
- LCD-Bereich in wenige gemeinsame Kacheln für Vorschau/Display/Uhr, statische oder animierte Inhalte sowie Hardwaredaten/Ebenen zusammengeführt.
- Technische FPS-/Transportwerte liegen unter den erweiterten Animationsoptionen.
- Acht eigene OHC-LCD-GIFs als eingebaute Galerie: Nebula Vanguard, Ringworld Runner, Singularity Dive, Abyssal Bloom, Neon Rain, Magma Heart, Polar Aurora und Firefly Grove.
- Uhr kann als zusätzliche Ebene über animiertem Hintergrund/GIF und Hardwaredaten eingeblendet werden.
- Aktuelle NZXT-ESC-v3-Dateien mit verschachteltem `preset.background`/`preset.overlay` werden importiert. `previewImage`, normalisierte Transformationen und aktuelle Elementtypen werden berücksichtigt.
- CSS-Farben aus aktuellen Exporten (`rgb()`/`rgba()` mit Alpha) werden korrekt normalisiert; `ram_usage` wird als RAM-Auslastung erkannt.
- Externe URL-/Video-Medien werden weiterhin nicht automatisch geladen. Eingebettete Vorschauen dienen als sicherer sichtbarer Fallback und der Importbericht weist nicht lokal verfügbare Inhalte aus.

## Sicherheit

- Keine Firmwareaktualisierung.
- Keine automatischen Downloads aus importierten LCD-Profilen.
- Kraken-Schreibzugriffe und CAM-Raw-LCD-Streaming behalten die koordinierte USB-PAUSE/RESUME-Übergabe.
- OpenRGB-SDK bleibt ausschließlich an den lokalen Loopback-Server gebunden.
