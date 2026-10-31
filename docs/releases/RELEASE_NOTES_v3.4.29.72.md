# Open Hardware Control 3.4.29.72 INTERN

Interner Linux-Teststand vom 12. September 2026. Kein GitHub-Tag und kein öffentliches Release.

## LCD-Animation und Bildrate

- Spectrum Ring, Neon Double Arc, Prism Segments und Aurora Radar besitzen eigene nahtlose Glow-/Partikelanimationen ausschließlich in Ebene 2. Jede lässt sich direkt ein- oder ausschalten und ist standardmäßig aktiv.
- Ein frei gewähltes Ebene-1-Bild oder -Video wird lokal mit dem bewegten Dekor zu einem validierten 1600×720-Cache-Video zusammengesetzt. Live-Daten bleiben editierbar; der vorhandene TRCC-Daemon bleibt der einzige USB-Besitzer.
- Vorschau-FPS und echte LCD-FPS sind getrennt. Das physische Display bleibt standardmäßig bei 15 FPS. 60 FPS wird nur nach einer bewussten experimentellen Freigabe in den Einstellungen angeboten und fällt bei einem unerwarteten Taktgeberfehler begrenzt über 30 und 20 auf 15 FPS zurück.
- Der Spielmodus erkennt Feral GameMode, Gamescope oder ausdrücklich eingetragene Prozesse und besitzt einen manuellen Schalter. Er verwendet keine CPU-/GPU-Lastheuristik und liest unter Wayland nicht allgemein fremde Fenster aus.
- Die frühere Ebene-1-Kachel „OHC Spektrumring · Animiert“ und ihre automatische Kopplung an ein Datenlayout sind entfernt.

## Programmfenster

- Bildschirmwahl, sichere normale Fenstergeometrie und letzter echter Maximierungszustand werden getrennt gespeichert. Zur Wahl stehen letzter Zustand, immer maximiert und immer als Fenster.
- Zielbildschirm und Endzustand werden vor dem ersten sichtbaren Frame gesetzt, damit das Fenster beim Start nicht sichtbar von klein zu groß springt.
- Der rahmenlose Größenänderungszeiger wird beim Verlassen, Ausblenden, Schließen, Fokusverlust und jedem Fensterzustandswechsel zuverlässig freigegeben. OHC bewegt oder fängt den Mauszeiger nicht.

## Sicherheit und Testgrenze

- Die 60-FPS-Option weist ausdrücklich auf den experimentellen Zustand und mögliche höhere USB-/Renderlast hin. Gesetzliche Rechte bleiben unberührt; ein Haftungsausschluss wird nicht als technische Freigabe behandelt.
- Auswahl und Vorschau schreiben keine Hardware. Das Anwenden beim nächsten Start erfordert weiterhin **Profile → Ausgewähltes Profil aktualisieren**.
- Deutsch, Englisch, Spanisch und Französisch enthalten dieselben 1.268 stabilen Nachrichten-IDs.
- 60 FPS ist auf dem echten Levita-Referenzgerät nicht als stabil bestätigt; 15 FPS bleibt deshalb die sichere Voreinstellung.
