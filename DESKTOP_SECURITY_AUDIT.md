# Desktop-Komponenten – Quellcode-, Lizenz- und Assetprüfung für 3.2.0 INTERN

## Ergebnis

Open Hardware Control bindet für Windows 8/8.1 **keinen fremden Desktop-Shell-Code und keine fremden Grafiken**
ein. Startübersicht, Charms-Leiste, KWin-Verknüpfung, Hintergründe, Symbole und Mauszeiger sind neue
GPL-3.0-or-later-Projektdateien. Sie besitzen keinen Netzwerkzugriff und keinen Hardwarezugriff.

## Geprüfte Referenzprojekte

| Projekt | festgehaltener Stand | Lizenz | Entscheidung |
|---|---|---|---|
| TiledScreen | `0015fdaffa307dd0c0b7a92bf272eb88b7013fea` | LGPL-2.1-or-later | nicht eingebettet |
| TileComponent | `134a5c736096967bc71b89db698c214aa1290d1f` | LGPL-2.1-or-later | nicht eingebettet |
| Win8DE | bei der 3.2.0-Recherche geprüfter öffentlicher Stand | GPL-2.0 | nicht eingebettet; wlroots statt KDE und keine Charms-Leiste |

TiledScreen war die funktional nächste Referenz, wurde aber nicht übernommen. Die Prüfung fand unter anderem:

- frei konfigurierbare Kachelbefehle mit beliebiger Programmausführung,
- installierbare ZIP-Pakete und Pfad-/Shell-Verkettungen, die für OHC nicht streng genug begrenzt sind,
- nachladbare Online-Kachel-Add-ons,
- einen Netzwerkabruf für iTunes-Metadaten.

Die OHC-Umsetzung ersetzt diese Punkte durch lokale `.desktop`-Erkennung, direkte Argumentlisten ohne Shell,
eine feste Liste eigener Assets, keinen Add-on-Mechanismus und keinen Netzwerkcode.

## Lizenz- und Markenschutz

Die Bezeichnungen Windows 8, Windows 8.1, Windows 11 und macOS werden nur beschreibend für eine allgemeine
Anordnungsrichtung verwendet. Originale Microsoft-/Apple-Logos, Symbole, Mauszeiger, Schriften, Klänge oder
Hintergrundbilder werden weder verteilt noch automatisch heruntergeladen. Projekthinweise nennen die OHC-Pakete
bewusst **Windowed**, **Metro** und **Orchard**, nicht „Original“.

## Releaseprüfung

Vor der internen Ausgabe führt die Releaseprüfung mindestens aus:

- Python-Kompilierung und Unit-/Regressionstests,
- Shell-Syntaxprüfung,
- XML-Parsing aller SVG-Dateien sowie Ablehnung von Skripten, externen Referenzen, Entitäten und `foreignObject`,
- Pillow-Verifikation aller Rasterbilder/GIFs,
- Archiv-Pfadprüfung und Manifest-/SHA-256-Verifikation,
- statische Suche nach Netzwerkabrufen, Shellausführung und unerwarteten ausführbaren Binärdateien.

VirusTotal-Standarduploads werden nicht automatisiert: Standardübermittlungen können mit der
Sicherheitsgemeinschaft geteilt werden. Ohne ausdrückliche Zustimmung und geeigneten privaten Zugang werden
keine internen oder persönlichen Dateien hochgeladen. Vorhandene öffentliche Hashwerte können dagegen ohne
Dateiupload abgefragt werden.
