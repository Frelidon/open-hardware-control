# Open Hardware Control 3.4.29.172 INTERN

Lokaler Umbau vom 11.11.26 auf Grundlage der vom Eigentümer bestätigten
Gehäuse-/OpenLinkHub-Entwürfe. Die Korrekturen aus .170 und .171 sind enthalten.

- Gehäuse: Übersicht, Komponenten und räumliche Abstände als klare Ansichten;
  direkter Komponenteninspektor und eigene Lüfterbilder für 21 LED-Zahlen.
  Bestehende Profile, Anschlüsse, Positionen und animierte Diagramme bleiben.
  Eine Katalogauswahl ändert zunächst nur einen Entwurf.
- OpenLinkHub: getrennte Mauszeichnung und Tastenliste, anpassbare Spalten,
  Start-DPI mit Haussymbol und benannte Mausprofile. Gemeldete Stufen ersetzen
  die pauschale Annahme von fünf Stufen. Offizielle Profilaktionen verwenden
  die lokale API. Die Startstufe steht im vorhandenen Profilfeld `Profile`;
  ihr ausdrückliches Speichern sichert die Datei, stoppt den Benutzerdienst,
  ändert nur dieses Feld und startet mit Gesundheitsprüfung neu. Bei einem
  Fehler wird der Vorwert wiederhergestellt. Keine Firmwareänderung und kein
  erratener DPI-Endpunkt.
- Updates: geprüftes offizielles Archiv, überprüfbarer vorbereiteter Payload,
  korrekter `daemon-reload`, Start-/Prozess-/Loopback-Prüfung und Rückkehrpfad.
  OpenLinkHub 0.9.4 ist lokal nach vollständiger privater 0.9.2-Sicherung aktiv.
  Die reale SABRE-Antwort liefert sechs DPI-Stufen und sechs Tasten. Eine neue
  Start-DPI oder ein neues Mausprofil wurde nicht auf dem Gerät aktiviert.
- Hardware-Prüfung: durchgehende DE/EN/ES/FR-Benennung, Hardware Fix und
  beschriebene unterstützte Geräte als Unterpunkte. Die Geräteansicht zeigt
  originale Symbole, offizielle Seiten und konkrete Unterstützungsgrenzen.
- Programmweite Listenhöhen folgen Modell-, Schrift- und Stilereignissen;
  leere Listen bleiben kompakt. Eigene Kategoriesymbole passen sich der Palette
  an. Die originale Übersichtsgrafik behält ihr Seitenverhältnis und bekommt
  abgerundete Kanten. Hintergrund- und Gehäuseanimationen bleiben auf ihren
  bestehenden Laufzeitpfaden.

Die Benutzer-Backend-Aktualisierung benötigt keine Administratorrechte.
Die reguläre Systempaketinstallation bleibt eine gebündelte Systemaktion;
es wird keine allgemeine passwortlose Administratorfreigabe eingerichtet.

Prüfnachweis: vollständiger Release-Wächter mit 1.529 Tests und fünf Untertests
bestanden, einschließlich echter viersprachiger Qt-UI, nativer RGB-Regressionen,
Inline-Editor-Geometrie, Backend-/DPI-Rückkehr und Payload-Prüfung. Helle und
dunkle isolierte Renderbilder liegen unter `docs/images/rendering-evidence/`
für .172; sie verwenden Beispieldaten und keine Hardware-Schreibzugriffe.
Paket-/Installationsnachweis folgt im Projektstatus. Reale Fedora-Hardwareprüfung
bleibt offen. GitHub-Veröffentlichung ist nicht Teil dieses lokalen Auftrags.
