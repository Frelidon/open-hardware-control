# Open Hardware Control 3.4.29.33 INTERN

Datum: 03.09.26

Diese Version folgt auf 3.4.29.32. Das Levita-Datenoberflächenmodul bleibt 1.4 unter `modules/lcd_levita/v1_4/`; geändert wurden die bestehende LCD-Orchestrierung, das RGB-Studio und die Seitenkomposition.

Im RGB-Studio bleibt die angeklickte Designkarte nach einem Neustart sichtbar markiert. Haupt- und Zweitfarbe werden bei eingebauten Vorlagen als eigene Designanpassung gespeichert, statt die Auswahl in „Benutzerdefiniert“ umzuwandeln. Aurora-Vortex und Galaxie-Komet ergänzen die Galerie.

ENE-DRAM erhält beim gespeicherten Profilstart weiterhin den bewährten doppelten nativen Direct-Reclaim. Da OpenRGB den echten LED-Zustand nicht zurücklesen kann, folgen nun drei vorsorgliche, begrenzte Reclaims nach 45 Sekunden, weiteren 2 Minuten und weiteren 4 Minuten. Danach wird jeweils das aktuell gewählte OHC-Design erneut angewendet. Deaktivieren, Reset, Backendkonflikt und Programmende brechen die Folge ab; es entsteht keine Endlosschleife.

Das Levita-Studio zeigt Ebene 1 und Ebene 2 als große Felder nebeneinander. Der Button **Eigene Designs importieren · Ordner** liest lokale Medien sowie alte `config1.dc`- und native 1600×720-`trcc.json`-Layouts ein. Das Kontextmenü einer Karte weist vollständige Designs direkt Ebene 1 oder 2 zu und setzt/entfernt Favoriten; **Nur Favoriten** filtert beide Sammlungen. Importierte Originale werden weder verschoben noch verändert.

Der rechte Levita-Notch wird einmalig auf die physisch erforderliche Mindestbreite von 80 Pixeln migriert. Damit startet auch eine bestehende Installation mit der größtmöglichen Bildfläche. Eine anschließend bewusst gewählte andere Breite bleibt gespeichert.

Zwei neue 1600×720-OHC-Datenoberflächen sind enthalten:

- **Nebula Drift**: freie tiefblaue Nebel-/Sternenoberfläche mit Uhr sowie CPU-, GPU- und RAM-Kurzstatus.
- **Orbital Command**: blaues Raumschiff-HUD mit CPU- und GPU-Auslastung, Temperaturen, Taktraten und belegtem GPU-Speicher.

Die Rastergrafiken wurden mit OpenAIs eingebautem Bildgenerator erzeugt. Verwendete Prompts beschrieben ein eigenständiges tiefblau/cyanes Weltraum-Nebelmotiv beziehungsweise ein symmetrisches blaues Raumschiff-HUD mit leeren Datenfeldern, ohne Marken, Text oder Logos. Die acht vom Projektinhaber bereitgestellten Sci-Fi-Bilder dienten nur als Farbstil-/Themenreferenz und wurden nicht in die neuen Dateien kopiert oder dem Paket nochmals hinzugefügt.

Die globale Standardskalierung sinkt auf 90 Prozent; Schrift, Abstände und große Schaltflächen bleiben lesbar, benötigen aber weniger Fläche. „Über“ stellt jede verwendete Software mit ihren Links direkt zusammen und führt feste sowie dynamische Geräteunterstützung getrennt auf. Die Hilfe enthält dieselbe Gerätekategorie in allen vier Oberflächensprachen. Der veraltete NZXT-Kühlerlink wurde auf die aktuelle offizielle Sammlung umgestellt.
