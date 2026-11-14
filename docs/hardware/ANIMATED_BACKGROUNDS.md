# Animierte Programm-Hintergründe · 3.4.29.178 INTERN

Zwölf prozedurale QPainter-Themen und sechs eigene lokale Videohintergründe
stehen unter Einstellungen → Animierter Hintergrund zur Auswahl. Matrix Code
Rain ergänzt Aurora Silk, Nebula Depth, Liquid Prism, Ocean Caustics und Solar
Orbit. Keine fremden Stockvideos, Downloads oder SignalRGB-Dateien werden benutzt.
Die Offline-Renderer unter tools und die berechneten Schleifennachweise sind
im Entwicklerpaket enthalten. Die Videos laufen ohne Ton, mit begrenzter
CPU-Komposition und einem sichtbarkeitsgebundenen Qt-Videodecoder.

Die globale Auswahl und Intensität bleiben gespeichert. Ausgeschaltet,
unsichtbar, minimiert oder gemäß Einstellung inaktiv werden Videodecoder und
Frame-Timer angehalten beziehungsweise entladen. Studio-Themes behalten ihre
Animationssperre. Im hellen Design bleibt die Darstellung abgeschwächt lesbar.

Auf Profile kann das ausdrücklich angewendete Profil ein eigenes LCD-Basismedium
oder seinen gespeicherten RGB-Effekt zeigen. Die Auswahl anderer Karten wendet
keine Geräte an und wechselt diesen aktiven Hintergrund nicht. Beim Verlassen
kehrt die globale Auswahl zurück, ohne die temporäre Wahl zu speichern.
Die Sensordatenebene des LCD bleibt unverändert; der Programm-Hintergrund zeigt
nur dessen Basismedium. Nach Neustart entsteht ein aktiver Hintergrund erst bei
wirklicher Anwendung eines Startprofils. Explizites Animation-Aus hat Vorrang.

Siehe [Entwurf und tatsächliche Qt-Renderings](PROFILE_WORKSPACE_DESIGN.md),
[Modulregister](../project/MODULE_REGISTRY.md) und
[Release Notes](../releases/RELEASE_NOTES_v3.4.29.178.md).

## Ursprüngliche prozedurale Themen

1. Sternenfeld
2. Kosmischer Nebel
3. Aurora
4. Spiralgalaxie
5. Warp-Tunnel
6. Schwebende Partikel
7. Bokeh
8. Ozeanwellen
9. Digitaler Regen
10. Sonnenaufgang
11. Eisnebel
12. Minimaler Fluss

## Leistung

- 15 FPS: sparsam
- 30 FPS: empfohlener Standard
- 60 FPS: flüssiger, aber höherer Ressourcenverbrauch
- „Pausieren, wenn die App nicht aktiv ist“ sollte aktiviert bleiben

Die Animation ist rein dekorativ. Kühlungs- und Sicherheitsbefehle laufen weiterhin unabhängig über die serielle `QProcess`-Warteschlange.

## Kompatibilitätsrenderer ab 2.9.1

Die Animation wird in einem CPU-seitigen `QImage` mit begrenzter interner Auflösung erzeugt und anschließend auf die Fenstergröße skaliert. Hintergrund und Bedienoberfläche sind getrennte Ebenen. Diese Architektur verhindert, dass ein fehlerhaft dargestellter Hintergrund die Bedienelemente übermalt, und reduziert die Last auf Ultrawide- und HiDPI-Monitoren.

Tritt dennoch eine interne Renderausnahme auf, stoppt die App den Animationstimer, zeichnet die normale Designfarbe und schreibt den Fehler in das Programmlog.


## Version 2.9.4

„Animation ausschalten“ deaktiviert nur den Renderer. Das zuletzt gewählte Thema bleibt erhalten. Beim erneuten Aktivieren wird es wiederhergestellt; bei alten Einstellungen mit „Aus“ wird Sternenfeld als Standard verwendet.
