# Umsetzungsprotokoll 3.4.29.130

Stand: 01.10.2026

> **Historisches, abgeschlossenes Umsetzungsprotokoll:** Dieses Dokument ist
> kein aktiver Arbeitsvorrat. Die freigegebenen Punkte wurden mit `.130`
> abgeschlossen und bleiben ausschließlich als prüfbare Herleitung erhalten.
> Aktuelle und noch offene Arbeit steht in `ROADMAP.md` und `PROJECT_STATUS.md`.

## Ergänzung 05.10.2026 · RGB-/LCD-/NEXUS-Manager

- RGB-Startprofil, Automatik, Wiederaufnahme und Sitzungsbesitz stehen gemeinsam
  groß am Seitenanfang; nach der ersten bestätigten Übernahme sind Automatik und
  passive Wiederaufnahme standardmäßig ein.
- Der LCD-Manager verwaltet mehrere Ordner und einzelne Medien, einschließlich
  GIF. Mitgelieferte OHC-Designs bleiben immer sichtbar und unveränderlich.
- Validierte OpenRGB-Profile können privat importiert werden. Alte `.orp`-
  Profile bleiben wegen ihres binären Formats unteilbar; Gerätehaken gelten für
  OHC-Designs, nicht als vorgetäuschter Filter eines fremden Binärprofils.
- iCUE-NEXUS-Hintergründe und optionale Touch-Manifeste werden mit Backup in die
  lokale OpenLinkHub-Benutzerinstallation übernommen. OpenLinkHub bleibt der
  USB-Besitzer; neue dynamische Widgets erfordern eine OpenLinkHub-Erweiterung.

Die freigegebenen Punkte sind in 3.4.29.130 umgesetzt. Die Abschnitte bleiben
als prüfbare Herleitung der Oberfläche und ihrer Sicherheitsgrenzen erhalten.

## Grafikkarte · Lüfterkurve

- Die Punkte der GPU-Lüfterkurve sollen direkt mit der Maus gezogen werden
  können, ähnlich wie im vorhandenen Kühlungsbereich.
- Beim Ziehen müssen die zugehörigen Temperatur- und Prozentwerte unmittelbar
  mitgeführt und in den Zahlenfeldern angezeigt werden.
- Zahlenfelder und Kurvengrafik bleiben in beide Richtungen synchron; die
  vorhandenen LACT-Grenzen, Punktreihenfolge und Sicherheitsprüfungen gelten
  weiterhin.

## Grafikkarte · Tests klar trennen

- „Änderungen kurz testen und anwenden“ darf bei reinen Lüfteränderungen keinen
  Grafik- oder GPU-Lasttest starten.
- Lüfteränderungen verwenden ausschließlich den kurzen physischen Lüftertest
  mit anschließender Rückstellung beziehungsweise bestätigter Übernahme.
- Der Grafik-Lasttest wird nur gestartet, wenn der Benutzer ausdrücklich den
  Grafiktest aus dem dafür vorgesehenen Bereich wählt.

Die Protokolle vom 01.10.2026 bestätigen für den geprüften 100-%-Lüfterlauf
bereits den reinen Lüfterpfad: 0 auf 2.474 RPM, Rückstellung der LACT-Basiswerte
und anschließende ausdrückliche Übernahme. Es wurde dabei kein vkmark-,
glmark2-, vkcube- oder Gamescope-Lasttest protokolliert. Die nächste Version
soll diese Trennung zusätzlich als feste Regression absichern und in der
Oberfläche unmissverständlich benennen.

## Grafikkarte · vollständig ohne Seitenscrollen

- Die komplette GPU-Steuerung soll sich an die verfügbare Fenster- und
  Bildschirmhöhe anpassen, sodass auf der Hauptseite kein vertikales Scrollen
  erforderlich ist.
- Abstände, Grafikkartenbild, Live-Kacheln, Kurvengrafik und Bedienelemente
  werden stufenweise kompakter; bei geringer Breite darf die Spaltenaufteilung
  responsiv wechseln, ohne Felder abzuschneiden.
- Ein eigenes transparentes Grafikkartenbild soll direkt auf der GPU-Seite
  importiert, ausgetauscht und auf das mitgelieferte Standardbild zurückgesetzt
  werden können. Bestehende Datei-, Größen-, Alpha- und Pfadprüfungen bleiben
  verbindlich.

## Leistung · SSD-Cache und Display entkoppeln

- Cache-Prüfung, Katalogscan, Vorschaubilder und Löschpflege dürfen weder den
  Qt-Hauptthread noch den Levita-Framepfad blockieren.
- SSD-Arbeit erhält niedrige CPU- und I/O-Priorität, wird in begrenzte Portionen
  zerlegt und bei sichtbaren Eingaben, aktivem Displaytransfer oder hoher
  Systemlast pausiert beziehungsweise weiter gedrosselt.
- Für die Untersuchung werden getrennte Zeiten für UI-Ereignisse,
  Cache-Dateisystemarbeit, Vorschaudekodierung und Display-Frameabstände
  protokolliert. Die vorliegenden Ausschnitte enthalten keinen eindeutigen
  SSD-Cache-Lauf und belegen daher noch nicht, welcher Teil den beobachteten
  Bildruckler verursacht hat.

## RGB-Studio · Navigation und kompaktes Raster

- Die linke Navigation muss immer die tatsächlich sichtbare Hauptseite
  markieren. Ein Wechsel zwischen „Vorschläge“, „Favoriten“, „Alle Designs“
  oder einer Designkategorie darf niemals „Wallpaper Engine“ auswählen.
- Ein Regressionstest prüft die Übereinstimmung aus aktuellem Hauptseitenindex,
  sichtbarer Seite und ausgewähltem Navigationseintrag nach jedem Galerie- und
  Kategoriewechsel.
- Beschriftungen wie „Alle Designs · 30“ dürfen bei keiner unterstützten
  Skalierung abgeschnitten werden.
- Die Designkarten werden kompakter und dynamischer angeordnet. Auf ausreichend
  breiten Ansichten sind sechs statt höchstens vier Karten pro Reihe das Ziel;
  Vorschau, Name, Status und Favorit bleiben klar erkennbar.
- Die neue Darstellung wird zunächst als Entwurf bestätigt und erst danach
  wertgetreu in der Qt-Oberfläche umgesetzt.

## RGB-Studio · räumliche Designs und 3D-Gehäuse

- Räumliche Designs erhalten eine eigene Aktion „Räumlichen Ablauf einstellen“.
  Dort werden Richtung, Reihenfolge, Tempo und räumliche Tiefe gemeinsam mit
  einer Gehäusevorschau dargestellt.
- Die Vorschau zeigt verständlich, an welchem realen Lüfter-/Komponentenblock
  ein Effekt beginnt und über welche Blöcke er weiterläuft. Richtung und
  Reihenfolge lassen sich direkt ändern und vor dem Anwenden prüfen.
- Die Gehäuseansicht soll von der bisherigen flachen Schemaansicht zu einer
  räumlichen, weiterhin originalen OHC-Darstellung ausgebaut werden.
- Tiefe, Außenmaße, Lüfterpositionen, Radiatorplätze und relevante Abstände
  werden je Modell nur aus offiziellen Herstellerseiten oder Handbüchern
  übernommen. Fehlende Maße werden als unbekannt markiert und nicht errechnet
  oder erfunden. Herstellerbilder werden nicht eingebettet.
