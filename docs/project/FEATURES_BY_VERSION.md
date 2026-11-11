# Funktionsübersicht nach Version

## 3.4.29.178 INTERN · 11.11.26

- Profilbibliothek mit Karten, Suche und gespeicherten Bereichskacheln.
- Sechs eigene Videohintergründe und temporärer aktiver Profilhintergrund.
- Matrix-LCD-Zeichen +30 %, +50 % und +100 %, Original bleibt verfügbar.

## 3.4.29.153 INTERN · 05.10.26

- Levita-Vorschauwarteschlange verwirft gelöschte Qt-Kacheln nach schnellen
  Kategorienwechseln und kann denselben Absturz nicht mehr über Scrollsignale
  wiederholen.
- Die Modul-Sichtbarkeit erscheint als zweispaltige Kartenansicht mit Symbolen,
  Statuspunkten und Schaltern; Seitenleiste und Einstellungen bleiben synchron.
- Regressionstest mit gelöschtem C++-Vorschauobjekt und vollständiger
  Offscreen-Render der Einstellungsseite.

## 3.4.29.152 INTERN · 05.10.26

- CPU-Startautomatik mit geprüftem Modellprofil und dauerhaftem Vorrang jeder
  späteren Nutzerauswahl oder bearbeiteten Kurve.
- Vollständige PWM-Topologie im PC-Profil einschließlich CPU_FAN, PUMP_FAN,
  Radiator und Pumpe; konfliktbehaftete Neuzuordnungen erfordern Bestätigung.
- Einmalige, anschlussnamensbasierte Übernahme der bestätigten MSI-X870-
  Referenzbelegung sowie wieder sichtbare Modulverwaltung in Einstellungen.

## 3.4.29.151 INTERN · 05.10.26

- Ubuntu-Paketaktualisierung und Installation getrennt, fehlerhafte Fremdquelle
  sichtbar gelassen und bestehender nct6687d-Checkout sicher wiederverwendet.
- Optionale dauerhafte NCT6687-Lüfterberechtigung als fünfter Assistentenschritt;
  allgemeine Paketinstallation bleibt geschützt.

## 3.4.29.150 INTERN · 05.10.26

- Der NCT6687-/DKMS-/MOK-Assistent erkennt Ubuntu, Fedora und Arch Linux und
  kopiert je Distribution einen eigenen Abhängigkeitsbefehl.
- Gemeinsame Upstream-/DKMS-Schritte bleiben identisch; MSI-X870-spezifische
  Optionen werden ausschließlich bei passend erkanntem Mainboard ergänzt.

## 3.4.29.149 INTERN · 05.10.26

- Hardware Checker → Hardware Fix for the explicitly named MSI MAG 274QPF
  X30MV, with anonymized EDID resources and Ubuntu/Fedora-separated execution.
- RGB startup/resume status, LCD source imports, OpenRGB profile library, and
  local OpenLinkHub iCUE NEXUS static designs.

## 3.4.29.131 INTERN · 01.10.26

TRCC Linux 9.10.4 übernimmt die Levita-Wiedergabe dauerhaft im eigenen
VideoLoop. OHC erkennt die genaue erfolgreiche CLI-Übergabe, lässt
Speicherüberwachung und Notbremse aktiv und erzeugt keine falschen
Taktgeber-Neustarts. Der getrennte Firmwarewächter stellt seinen Modulpfad
eigenständig her. Der Referenzlauf bestätigte fortlaufende 1600×720-Frames bei
stabilen RSS-, Thread- und Dateideskriptorwerten.

## 3.4.29.130 INTERN · 01.10.26

Die freigegebenen GPU-, RGB- und Gehäuseentwürfe sind umgesetzt. Das kompakte
GPU-Cockpit benötigt in der breiten Hauptansicht keine Seitenscrollleiste;
Lüfterpunkte sind direkt und über exakte Felder bearbeitbar, eigene GPU-Bilder
lassen sich importieren/zurücksetzen und reine Lüftertests erzeugen keine
Grafiklast. RGB Studio ordnet bis zu sechs kleinere Karten je Reihe an und hält
Galerie sowie Navigation synchron. Räumliche Effekte verwenden gespeicherte
Richtung, Tempo und echte LED-Reihenfolge; selbst gemessene Abstände und Tiefe
werden intern in Millimetern gespeichert und wahlweise in mm oder Inch
bearbeitet. Cachepflege wartet auf Eingaberuhe und läuft mit niedriger
CPU-/I/O-Priorität.

## 3.4.29.129 INTERN · 01.10.26

Nach einem von OHC kontrollierten Neustart der Levita-Display-Steuerung wird
die neue TRCC-Prozess-ID nur dann übernommen, wenn die bisherige eigene Instanz
nachweislich beendet und der Ersatzprozess exakt als TRCC-Daemon erkannt wurde.
Der Abschlusswächter überträgt dieselbe Zuordnung. Normales Beenden und
Absturzbereinigung erfassen damit den aktuellen OHC-Kindprozess, ohne fremde
TRCC-Instanzen anzutasten.

## 3.4.29.128 INTERN · 01.10.26

Der Snapshot-Manager verwendet moderne Reglerkarten für CPU, GPU und beide
Btrfs-Raten. Seine geladene Liste lässt sich atomar als JSON-Metadaten
exportieren; ein einzelner Snapper-Stand ab Nummer 1 kann nur nach deutlicher
Bestätigung über den begrenzten Helfer gelöscht werden. Die GPU-Seite nähert
sich der freigegebenen Drei-Spalten-Referenz weiter an: kompakte Live-Kacheln,
breite blaue Taktbahnen mit Zahlenfeldern und eine früher sichtbare Lüfterkurve.

## 3.4.29.127 INTERN · 01.10.26

Der neue Snapshot-Manager erkennt Linux, Dateisysteme und verfügbare
Snapshot-Werkzeuge, zeigt aktive Snapper-/Btrfs-Systeme und lädt Snapper-Stände
lesend. Automatische Zeitpläne pausieren bei GameMode, Gamescope,
KDE-Vollbild oder einer Programmliste; optional ergänzt eine mehrfach
bestätigte Mehrkern-CPU-/GPU-Last. Desktop- und Spielgrenzen drosseln
Btrfs-Discard. Manuelle Sperren gelten eine Stunde, bis zu einem Zeitpunkt
oder dauerhaft. Der privilegierte Helfer akzeptiert nur feste Timer und eng
begrenzte Werte; Rollback bleibt bewusst manuell erklärt.

## 3.4.29.126 INTERN · 25.09.26

Die Grafikkartenseite verwendet ein responsives Drei-Spalten-Cockpit nach der
freigegebenen Designreferenz. Taktung, Lüfter und Lasttest bleiben auf breiten
Bildschirmen gemeinsam sichtbar. Die fünf Lüfterpunkte sind als Zahlen und
direkt in der Kurvengrafik editierbar. Ein klarer kombinierter Weg testet die
physische Reaktion und übernimmt denselben Entwurf danach dauerhaft in LACT;
ein reiner Rückstelltest bleibt erhalten. GPU- und LACT-Protokolle besitzen
eigene Kopieraktionen.

## 3.4.29.125 INTERN · 25.09.26

Die Gehäuseseite blendet unmögliche LED-/PWM-Felder aus und fasst die
gespeicherte Topologie lesend zusammen. RGB Studio nutzt größere animierte
Karten statt einer doppelten Live-Vorschau und erhält sechs räumliche Designs
mit drei neuen Algorithmen. GPU-Lüftertests können nach bestätigter Reaktion
optional dauerhaft gespeichert werden; die Option bleibt standardmäßig aus.
0 MHz GPU-Takt ist im AMD-Energiesparzustand kein Diagnosefehler mehr und
wiederkehrende Prozess-/Lüfterlogs werden ohne Verlust von Zustandswechseln
gebündelt.

## 3.4.29.124 INTERN

Lüfterzahl und physische Anordnung sind getrennt: Neue LED-Verläufe starten
als Reihe; eine gespeicherte Reihe oder ein ausdrücklich gewählter Ring bleibt
erhalten. Ringpfade segmentieren weiterhin jeden Lüfter. Das Log bietet eine
Gesamtansicht, einen RGB-/Lüfterfilter und Hardware-Auffälligkeiten; die
Topologiediagnose nennt Anschluss, Anordnung und exakte LED-Aufteilung.

## 3.4.29.123 INTERN

Der LED-Verlauf übernimmt Lüfteranzahl und LED-Gesamtzahl aus dem zugehörigen
Gehäuseblock. Die erste Umsetzung bereitete kompatible alte Streifenpfade beim
Bearbeiten als Ringgruppe vor; `.124` korrigiert diesen Anordnungszwang.

## 3.4.29.122 INTERN

Gehäuse-Laufrichtungen gehören jetzt zum einzelnen LED-Pfad. Lüftergruppen,
GPU und GPU-Halterung überschreiben sich nicht mehr gegenseitig. Die
Ringvorschau validiert Combo-Zwischenzustände vor dem nativen Zeichnen.

## 3.4.29.121 INTERN

LED-Verlauf-Dialoge schließen ohne verzögerten Qt-Restore-Callback. Physische
Lüfterbänke behalten ihre Einheiten, unterstützen komponentenweises Umkehren
und erscheinen animiert in der Gehäuseansicht. Eine gemeinsame begrenzte Uhr
glättet Direct-Effekte auch bei langsamen 1080-LED-Frames; Renderfehler bleiben
im getrennten Worker pro Gerät isoliert. Der GPU-Lüfterablauf trennt Test und
dauerhafte LACT-Übernahme sichtbar.

## 3.4.29.120 INTERN

Die Grafikkartenseite besitzt exakte GPU-Unterprofile samt Taktung, Leistung,
Lüfterkurve, Zero-RPM und Lasttestdarstellung. Das gewählte Unterprofil wird im
Hauptprofil gespeichert; automatische Aktivierung bleibt auf lokal geprüfte
Daten derselben GPU und die vorhandenen LACT-/CoolerControl-Sicherheitswege
begrenzt. 4K/8K kann über Gamescope monitorfüllend skaliert werden. Eigene
transparente Kartenbilder werden nur als private Kopie verwaltet. Neutrale
Originalgrafiken, Einbaurichtung und animierte Lüfterkurve ergänzen das Design.

## 3.4.29.101 INTERN

Nach der Levita-Firmware-Rückgabe stoppt OHC beim geordneten Programmende einen
von ihm gestarteten TRCC-Daemon. Ein vor OHC vorhandener oder inzwischen
ersetzter Daemon bleibt unberührt. Ohne laufenden Daemon erzeugt die
Abschaltroutine keinen neuen Prozess. Der vor Ort beobachtete `.98`-Hauptprozess
hatte sauber beendet; die 1,3 GiB Arbeitsspeicher stammten aus dem separaten
TRCC-Daemon.

## 3.4.29.100 INTERN

Gehäusegeräte, Hardware-Checker und Temperaturstatistik teilen ein modernes,
anpassungsfähiges Tabellenbild; Mainboardnamen werden nach Inhalt bemessen.
Übersicht, Kühlung und Temperaturaufzeichnung nutzen dieselbe zwölfteilige
Temperaturanzeige mit echten Celsiuswerten. Der direkte GPU-Lasttest prüft die
Hardware zuerst automatisch, kann neben glmark2 auch Vulkan-vkcube verwenden
und bewertet PCIe unter Last nur bei laufendem Testprozess. Nach dem Videoabgleich
bewegt sich ein schmalerer weißer Lichtkopf über der blauen 30-LED-GPU-Basis.

## 3.4.29.99 INTERN

Display-Effekte und LCD-Studio speichern nun denselben verbindlichen
Levita-Startzustand einschließlich Ebene 2, Bewegungswahl und Bildraten.
Minimieren nutzt auf Wunsch weiterhin den Infobereich; Schließen ist davon
getrennt und beendet OHC immer über die geordnete Hardware-Rückgabe. Verborgene
Videovorschauen entladen ihre Decoder und Bildpuffer. Nach Navigation oder
Minimieren gibt eine verzögerte Leerlaufbereinigung freie Heap-Seiten zurück,
ohne periodische CPU-Aufgabe oder Auslagerung privater Daten in den SSD-Cache.

## 3.4.29.98 INTERN

Eine ausdrücklich gewählte Fortsetzung im Infobereich wird dauerhaft in den
Einstellungen gespeichert. Weitere Schließereignisse blenden das Fenster ohne
erneuten Dialog aus. Beim ersten Start der neuen Version kann eine bereits in
`.97` protokollierte echte Auswahl einmalig übernommen werden; ein älteres bloßes
Schließen mit aktivem Tray-Häkchen reicht dafür nicht. Ausdrückliches Beenden,
Abbrechen und Sitzungsende bleiben getrennte Pfade.

## 3.4.29.97 INTERN

Mehrdeutige Schließereignisse bei aktivem Infobereich-Modus zeigen eine klare
Auswahl für Beenden, Weiterlaufen oder Abbrechen. Ein bestätigtes Beenden nutzt
direkt die vorhandene geordnete Hardware-Rückgabe und den Qt-Ausstieg. Die
private, begrenzte Beenden-Diagnose klassifiziert den letzten Versuch und zeigt
im Systemstatus bei einem nachgewiesenen Hänger die letzte unvollständige Phase.
Sie liest höchstens das vorhandene Journal und führt keine Hardwareaktion aus.

## 3.4.29.96 INTERN

Konfigurierbare Hauptseite Hardware-Checker 1.0 mit begrenzter read-only
CPU-/SMT-/Virtualisierungs-, Board-, PCIe-GPU-, NVMe- und RAM-Prüfung. Ist-
und Kernel-Maximum für PCIe mit Leerlaufwarnung; ausdrücklicher optionaler
glmark2-Lasttest für die endgültige GPU-Linkbewertung. Polkit liest auf Wunsch
DMI-RAM-Daten, ohne dass OHC das Passwort erhält; kein SSD-Schreibbenchmark und
keine Änderung an BIOS, Takt, Spannung, Lüfter oder Firmware. 1.530 vollständige
DE/EN/ES/FR-Nachrichten.

## 3.4.29.95 INTERN

Clean warm Light Bands without idle edge/centre stripes, eight actual 4800×2160
renders at native output and CRF 10. Visible selected-video layout playback,
shared ancestor-clipped previews and transient effect exploration defaulting
to the last confirmed display composition. Stable gallery/empty-motion scene
geometry, current translated design details; no preview-driven startup staging.


## 3.4.29.94 INTERN

Responsive right case properties, same live fields in columns/tabs without an
inner scroll area; footer remains reachable and unsaved values survive resize.
Component/fan and LED-path form divisions, live translated late tabs. Wider
quintic GPU/support spinner/comet colour fades with a shared virtual clock and
spatial footprint, sampled at actual independent LED counts. 1,483 atomic
DE/EN/ES/FR messages; existing hardware ownership/settings remain unchanged.


## 3.4.29.93 INTERN

LCD Runtime 1.1 separates explicit startup standard, preview and immutable
accepted hardware commands; automatic profiles cannot replace saved defaults.
Explicit save/apply staging and generation-cancelled startup retries. Recovery
reuses prepared media. Stable-video-aware memory protection with growth,
MemAvailable and emergency bounds. Cache identities include config/source assets.
1,482 complete language messages; existing native quarantine/sole-owner paths.

## 3.4.29.92 INTERN

Continuous static/animated LCD via the existing daemon IPC ticker; monitor
acknowledged sends, finite command/start deadlines and SDK stalls. Isolate
bounded client recovery with private failure evidence. Move read-only game
probes out of Qt and expose manual sensor restart/actual LCD transfer age.
No native crash-loop restart or new hardware authority.

| Version | Erstmals hinzugekommene Hauptfunktionen |
|---|---|
| 3.4.29.91 INTERN | Erste überwachte read-only Sensorprozessgrenze mit gemeinsamen frischen Messwerten; RGB-Berechnung im vorhandenen SDK-Worker; klickbare Seitenbeschriftungen; dauerhafte private Beenden-Phasen/Stack-Diagnose und begrenzter Elternbeobachter; eigener Prozessabschluss und eingebettete echte CPU/RSS-/Sensoranzeige. Autonomer Core/Kühlungsdienst bleibt nächste validierte Stufe. |
| 3.4.29.90 INTERN | Portionsweiser LCD-Erstaufbau und Leerlauf-Vorbereitung ohne versteckte Wiedergabe; wiederverwendete Größenanpassung; RAM-Nachprüfung ohne Reset übriger RGB-Effektzeiten; eingebettete rechte Komponenten-/ARGB-/PWM-Einstellungen; persistierte frisch geprüfte Kühlungsstartabsicht; idempotentes Qt-Tray-Ende und nur linke Navigationsübergänge. |
| 3.4.29.89 INTERN | Weiche offene GPU-Streifen mit zählabhängig langsamer Bewegung und Ein-/Auslauf; optionale gemeinsame GPU-/Halterungsphase und GPU-Effekt trotz unterschiedlicher LED-Anzahl/Controller; begrenzte Strip-Plan-Diagnose ohne FPS-Rücklesebehauptung. |
| 3.4.29.88 INTERN | Alle .87-Verbesserungen; umgekehrte physische Lüfterring-Reihenfolge mit LED 1 unten/rechts, unabhängig von Ringrotation; strengere Paketdateitypen/Pfadkonfliktprüfung vor Staging; Timer-/Neustartstopp vor eigenem Exportarbeiter-Abbruch. |
| 3.4.29.87 INTERN | Vollständige private Profilpakete samt allen Einstellungen, Positionen, RGB/PWM/Lüftermodellen/Medien; Hintergrundexport und geprüfter Start-Import mit Rückfallkopie; unabhängiger physischer LED-Streifen-/Ringverlauf und acht räumliche Laufrichtungen; korrigierte persönliche Airgoo-Anschlüsse. |
| 3.4.29.86 INTERN | EOF-first Helferabschluss und isoliertes Beenden; Offline-Controllerwahl, ausdrückliche Eigen-Engine-Wiederherstellung, pausierte Erkennung während LED-Tests; persönliche Lüfterdeklarationen und kontrollierte Designrückgabe. |
| 3.4.29.85 INTERN | Unzugeordnete Gehäuseblöcke direkt mit Controller/ARGB-Port verbinden, LED-Anzahl bearbeiten und einzelne LEDs testen; unabhängige stabile Bindung gegenüber Designs. |
| 3.4.29.84 INTERN | Komponenten am Eckgriff oder numerisch skalieren; proportionale räumliche Gehäusevorschau; SYS_FAN-Anschlussnamen statt doppelter Treibernummer; unzugeordnete RGB-Blöcke bearbeiten; alle steuerbaren RGB-Geräte standardmäßig auswählen, einzelne direkt in der Liste. |
| 3.4.29.83 INTERN | Zentrale Gehäuse-/LED-/PWM-Topologie, unabhängige Kühlungspositionen, Direct-ARGB-Einzeltest und manuelle LED-Werte, zählabhängig weichere Zonenanimation, 30 originale Modellzeichnungen und größere Übertragungsanzeige. |
| 3.4.29.82 INTERN | Zonengenaue GPU-ARGB-Routen, eigene Strip-Koordinaten, einzelner Anschluss-/Pixeltest und manuelle LED-Zahl dauerhaft gegenüber alten Designprofilen; einmalige bestätigte persönliche JARGB-1-Migration. |
| 3.4.29.81 INTERN | Native Sapphire-Animationen statt automatischem External Control; explizite GPU-ARGB-Zuordnung, manueller LED-Zonen-Editor und Profilpersistenz ohne erfundene GPU-LEDs oder Änderungen an der persönlichen Ansicht. |
| 3.4.29.80 INTERN | Geführter statusabhängiger NCT6687-/DKMS-/MOK-Assistent mit robuster `mokutil`-Auswertung; lesbare Kühlungshinweise ohne nicht vorhandenen Levita-Kühlmittelsensor; eindeutige Lüfternamen, Gesamtreset und fortlaufende Einzelzuordnung; Doppelklick aus der PC-Ansicht in echte RGB-Geräte/Zonen; KDE-/Wayland-Tray-Erreichbarkeit ohne unzuverlässige Geometrieprüfung. |
| 3.4.29.79 INTERN | Wählbare leichte globale Seitenübergänge ohne Doppelrendering; zentraler 0–4-GiB-SSD-Cache; lokalisierte Wallpaper- und NCT6687/DKMS/MOK-Assistenten; verzögerte ENE-Wiederherstellung während Navigation; zuverlässige blaue Lüfterautomatik; X-Trefferfläche bis in die Ecke und fehlerfreies Tray-Minimieren ohne Display-Abschaltung. |
| 3.4.29.78 INTERN | Sichtbarkeitsgebundenes Rendering in allen kontinuierlichen UI-Vorschauen; feste und gekürzte RGB-Kartenschriften; neu geordnetes RGB-Studio; verzögert startende animierte Display-Effekt-Vorschau mit wiederverwendeten Karten/Bildern und 20-FPS-Grenze; geordneter Fensterschluss bei nicht erreichbarem Infobereich. |
| 3.4.29.77 INTERN | Sichtbarkeitsgebundene LCD-/RGB-Vorschauen und verzögerter Galerieaufbau; Zehn-Sekunden-Spielabfrage; streng validierte automatische/manuelle Levita-Freigabe; persistente blau markierte Mainboard-Automatik; korrekter Zustand im ersten sichtbaren Fensterframe; Unterbau-Abgleich mit TRCC 9.9.12, OpenLinkHub 0.9.1, liquidctl 1.16.0, OpenRGB 1.0-rc3.1, Qt/PySide 6.11.2 und Pillow 12.3.0. |
| 3.4.29.76 INTERN | Sichtbare 60-Minuten-Ringprotokolle mit hartem Speicherlimit; separates privates und rotiertes Fehlerlog; Levita-Wiederherstellung nach verlorener TRCC-IPC-Verbindung; exakter Eigenprozess-Speicherwächter mit kontrolliertem Daemon-Neustart vor System-OOM. |
| 3.4.29.75 INTERN | Einmaliger flackerfreier Fensterstart ohne Startprofil-Doppelplatzierung; responsive LCD-/Effektgalerien bis zwölf Spalten; nicht-destruktiver Multi-Ordner-/Einzelmedienmanager mit Aliasen und lesbaren TRCC-Namen; datierte, frei skalierbare Temperaturansicht und CSV-/JSON-Berichte für Zeitraum und Sensorwahl. |
| 3.4.29.74 INTERN | Normalabbildung auf dem Zielmonitor vor verzögerter Maximierung; Bestätigung des tatsächlichen KWin-/Wayland-Bildschirms mit begrenzter Nachkorrektur; aussagekräftige Ziel-/Ist-/Geometrie-Diagnose auch beim Öffnen aus dem Tray. |
| 3.4.29.73 INTERN | Modellrichtige Originalanzeige für Thermalright im Tray, auf der LCD-Seite und unter Display-Effekte; ein-klickiges ausdrückliches Tray-Beenden; schärfere OHC-Lichtbänder durch 2×-Supersampling und hochwertige native Ausgabe. |
| 3.4.29.72 INTERN | Vier originale schaltbare Glow-/Partikelanimationen ausschließlich in Ebene 2; lokale Ein-Strom-Komposition mit frei gewählter Ebene 1; getrennte Vorschau-/LCD-FPS mit 15-FPS-Standard, experimenteller 60-FPS-Freigabe und Rückstufung; GameMode/Gamescope/Programmlisten-/manueller Spielmodus; flackerfreie Fensterzustandswiederherstellung und sichere Cursor-Freigabe. |
| 3.4.29.71 INTERN | Grafische Ebene-1-Kacheln mit erhaltenen Quellenlinks; eigener animierter Spektrumring mit passender Ebene 2; polierte OHC-Layouts; feste Haupt-/Anschlussmonitorwahl und KWin-sichere Maximierung. |
| 3.4.29.70 INTERN | Vier originale bunte Levita-Datenlayouts; bis zu zwölf frei positionierbare eigene Texte mit lokalen Schriften; größenstabile 880×396-Vorschau; Design-Manager für eine der nächsten zwei bis drei Versionen vorgemerkt. |
| 3.4.29.69 INTERN | Synchronisierte LCD-Unterreiter zusätzlich zur Seitenleiste; Display-Effekte folgt dem aktiven Bibliotheksmedium; originaler OHC-Light-Ribbons-Loop mit acht Richtungen ohne Logo oder übernommenes Referenzmaterial. |
| 3.4.29.68 INTERN | Kühlung klappt in der Hauptnavigation wie LCD in zwei feste Unterpunkte auf; bidirektionale Synchronisierung von „Steuerung & Profile“ und „Temperaturaufzeichnung“ mit der tatsächlich sichtbaren Unterseite. |
| 3.4.29.67 INTERN | Eigene Kühlungs-Unterseite mit interaktiver Aufzeichnung aller plausiblen read-only hwmon-Temperaturen; konservative Levita-Untergrenzen an allen PWM-Grenzen; breite, auswahlstabile Profilliste mit Inhaltsbaum und frei kombinierbaren Bereichen. |
| 3.4.29.66 INTERN | Eindeutige Profil-Festwerte statt „Manuell“ bei Kühlungs-Schnellprofilen; interaktiver, auswählbarer RAM-Sitzungstemperaturverlauf; fail-closed Auswahl vorhandener Display-/Lüfter-Unterbauten mit sichtbaren, deaktivierten Zukunftsadaptern. |
| 3.4.29.65 INTERN | Fotografisch ermittelte TRCC-Schriftreserve für Nebula Drift; automatische wert- und schriftgrößenabhängige Rahmenskalierung mit 22 % Breiten- und 12 % Höhenreserve; drei neu erzeugte Varianten. |
| 3.4.29.64 INTERN | Nebula Drift wieder als leichte transparente Ebene; drei fertige Varianten Minimal, System und Leistung; kompakte dunkle Flächen nur direkt hinter den Live-Werten; reale Zwei-Ebenen-Galerievorschau. |
| 3.4.29.63 INTERN | Eindeutige Ein-/Ausschaltaktionen je kalibrierter Gehäuselüfterkarte; dunkle Glass Cards für Nebula Drift; deutlich getrennte Ring-, Wellen-, Glasleisten- und Winkelstile der vier eigenen generierten Layer-2-Layouts; skalierbare Vorschau-Schriften. |
| 3.4.29.62 INTERN | 15 menschenfreie, attribuierte Weltall-/Landschafts-/Wasserclips; vier Filterkategorien; fünf CC0-Kenney-basierte und vier originale editierbare Layer-2-Themes. |
| 3.4.29.61 INTERN | Getrennte registrierte Hell-/Dunkel-Theme-Module; durchgängig kontrastreicher heller Modus; animierte, sichtbarkeitsgebundene Vorschau aller Display-Effektvideos mit sichtbarem Dark-Smoke-Einstieg. |
| 3.4.29.60 INTERN | Sichere separate Fenstermodus-Geometrie mit Allkanten-/HiDPI-Begrenzung, Größenwert und Strg+Alt+0-Rettung; zweispaltige modellabhängige OHC-Gehäuseansicht mit AIO/Luft, Luftstromumkehr und einzeln verschiebbaren Lüftern; privater Amazon-Knopf entfernt. |
| 3.4.29.59 INTERN | Eigene Qt/KWin-delegierte Fensterleiste; einklappbare LCD-Unterkategorien; kompaktes RGB-Studio mit vier Vorschlägen, vier neuen Effekten, Favoriten und Gesamtbibliothek; 30 Gehäuse-Schemata, exaktes Retro 360 TG und lokale PC-Profile. |
| 3.4.29.58 INTERN | Reparierte Übergabe der gebündelten Display-Effektbibliothek über eine eigene erlaubte Paketwurzel; gemeinsame strikte MP4-/Symlink-/Pfadprüfung für Cache und Paket; sichtbares Auswahlprotokoll vor dem bestehenden Levita-Apply-Pfad. |
| 3.4.29.57 INTERN | Begrenzter automatischer 1/2/4-s-Wiederanlauf eines unerwartet beendeten Levita-Video-Taktgebers; erneuertes Budget nach stabilem Lauf; gekürzte datenschutzgefilterte TRCC-Fehlerausgabe ohne USB-Neuverbindung oder zweiten Hardwarebesitzer. |
| 3.4.29.56 INTERN | Fünf frei lizenzierte Display-Videodesigns mit je vier offline gebündelten Farbvarianten; getrennte Haupt-/Farbauswahl und sichtbare Urheber-, Quellen- und Lizenzlinks; reparierte native Fensterdiagnose ohne leere Zusammenfassungszeilen. |
| 3.4.29.55 INTERN | Reaktionsfähiger erster Fensteraufbau vor Geräteinitialisierung und Levita-Bibliothek; zusammengefasste fail-closed CoolerControl-Prüfung außerhalb des GUI-Prozesses; grafische Ebene-2-Sensorlayout-Karten in Display-Effekte; schnellerer Effekt-Export und direkter Cachepfad ohne redundanten Galerie-Neuaufbau. |
| 3.4.29.54 INTERN | Eigene Levita-Seite „Display-Effekte“ mit prozeduralem Rauch, großer Vorschau und unveränderter Ebene 2; bestätigungspflichtiges OpenLinkHub-/Web-UI-Update mit offiziellen Paketquellen oder GitHub-SHA-256, Backup und Rollback; vollständige dynamische DE/EN/ES/FR-Oberfläche; Tray-Autostart ohne Taskleistenfeedback und Zweitstart aktiviert das vorhandene Fenster. |
| 3.4.29.53 INTERN | Levita-Rückgabe an das eingebaute Thermalright-Firmwarebild durch begrenzten TRCC-Daemon-Disconnect beim echten Programm-/Systemende; prozessgetrennter Pipe-Wächter für unerwartetes Elternprozessende; bestehender Kraken-Flüssigkeitstemperatur-Rückfall erneut geprüft. |
| 3.4.29.52 INTERN | Versioniertes Lokalisierungsmodul mit je einer vollständigen Datei für DE/EN/ES/FR; stabile gemeinsame Nachrichten-IDs und automatische Prüfung auf eindeutige deutsche Quellen sowie fehlende/zusätzliche IDs; kleiner kompatibler Root-Katalog. |
| 3.4.29.51 INTERN | Sprachwechsel für alle im vollständigen UI-Aufbau erkannten interaktiven Texte in DE/EN/ES/FR; dynamische Galerieübersetzung; verbindliche Vier-Sprachen-Regel und Offscreen-Wächtertest für künftige UI-Änderungen. |
| 3.4.29.50 INTERN | Gehäuselüfter-Leistungsprofil als konstanter, sofort neu ausgewerteter 100-%-Override für bestätigte aktive Kanäle; direkter 0-%-/10-s-Stopptest pro Lüfterkarte; BIOS-Erklärung bei fehlendem `pwmN_mode`, ohne geratenen DC-Registerpfad. |
| 3.4.29.49 INTERN | Übersicht „Status & Hinweise“ folgt bestätigten Levita-PWM-Tests (OK/Fehlerhaft wie Erkannte Hardware); RGB-Studio klappt Geräte/Effekte und native Hardwarekanäle als große Bereiche in der Seite auf. |
| 3.4.29.48 STABLE | Verbindliche Ablage- und Kurz-README-Regel für alle Coding-KIs mit Wächtertest `tests/test_repository_layout_342947.py`; Release-Workflow liest `packaging/VERSION`. |
| 3.4.29.47 STABLE | Anwendungscode nach `src/`, Installer und Versionsdateien nach `packaging/`, alle Dokumente nach `docs/`; Wurzelverzeichnis nur noch README, LICENSE, CITATION und AGENTS-Wegweiser; installierte Struktur unverändert. |
| 3.4.29.46 STABLE | Minütliche OpenRGB-Hintergrundinventur pausiert, solange OHC im Infobereich verborgen ist und keine RGB-Aktion aussteht; Repository in `docs/{project,ai,hardware,security,releases}`, `packaging/` und `.github/` sortiert; sieben aktuelle Screenshots und kompakte README. |
| 3.4.29.45 STABLE | Deterministisch isolierter 140-Video-Levita-Vorschautest ohne Rennen gegen bereits gestartete gebündelte Medien; finaler öffentlicher Release der vollständig geprüften 3.4.29-Reihe. |
| 3.4.29.44 STABLE | Bereinigter öffentlicher Release der 3.4.29-Funktionsreihe; GitHub-Runner mit vollständiger Qt/EGL-Testumgebung; cache-unabhängiger Levita-Videovorschau-Test für die gebündelte 30-Sekunden-Animation. |
| 3.4.29.43 STABLE | Gespeicherter RGB-Profilstart wartet bei vorläufiger OpenRGB-Teilerkennung auf den vollständigen Bestand; stabile Modulregisterprüfung; Veröffentlichung der geprüften 3.4.29-Levita-, RGB-, Wallpaper-, Lüfter-, Diagnose- und KDE-/Wayland-Erweiterungen. |
| 3.4.29.42 INTERN | Reparierte Wallpaper-Wiedergabeknöpfe über das registrierte Plasma-D-Bus-Objekt; drei CaptSilver-Skalierungsmodi pro Zielbildschirm; Programmstart standardmäßig auf dem Hauptbildschirm oder einem fest gewählten benannten Monitor mit Rückfall; global einheitliche schmale Scrollleisten; Wallpaper-Modul 1.2 und Fensterplatzierungsmodul 1.0. |
| 3.4.29.41 INTERN | Wallpaper-Erststart-Assistent mit Fünf-Workshop-Checkliste und wiederaufrufbarer Anleitung; Fedora-Installer lädt nur das passende offizielle CaptSilver-RPM, prüft GitHub-SHA256 und verlangt vor Polkit/DNF eine zweite Bestätigung; feste Galerie-Kartenmaße nach Apply-Refresh; Wallpaper Engine direkt nach LCD in der neuen Standardnavigation bei Erhalt individueller Reihenfolgen. |
| 3.4.29.40 INTERN | Eigener Wallpaper-Engine-Menüpunkt mit lokaler Steam-Workshop-Galerie, Szenen-/Video-/Web-Filter, separater Kategorie für eigene Videos, Multi-Monitor-Auswahl, CaptSilver-D-Bus-Wiedergabesteuerung, direktem Plasma-Einstellungsaufruf und vollständig rücksetzbarer optionaler Optimierung ohne Plugin-Patches. |
| 3.4.29.39 INTERN | Fensterdiagnose filtert normale Qt-Tooltips und direkte ComboBox-Popups, behält aber unbekannte Popupfenster und die exakte 640×480-Startfensterquarantäne bei. |
| 3.4.29.38 INTERN | Modernisiertes eingebettetes RGB-Studio mit Ein/Aus-Schaltern, persistenten effektabhängigen Rechtsklick-Farben, Gesamthelligkeit, nativer Kanalliste und zuverlässigem ENE-Abschluss; RGB-Studio-Modul 1.1; TRCC Linux 9.9.12 als kompatible Fedora-Empfehlung. |
| 3.4.29.37 INTERN | Levita-Einheiten/Prozentzeichen auf dem physischen Display; persistente 25–150-%-Intensitätsregler für beide Ebenen; kräftigerer Orbital-Standard; read-only Korrektur des TRCC-GPU-Taktgrenzfalls; eigene Hardware-Auffälligkeitsansicht ohne Messwertspam. |
| 3.4.29.36 INTERN | Automatische vollständige Sicherung jedes erfolgreichen Versionsbaus im externen Geschwisterordner; zwei neueste Versionen mit Laufzeit-/Entwicklerpaket, Quellen, Git-Bundle, erzeugten RPM/DEB und gültigen SHA256; verbindliche Regel für GitHub-, Cursor- und lokale KIs. |
| 3.4.29.35 INTERN | Echte Levita-Neuverbindung vor Design, Farbtest und Displayeinstellungen; veralteter Daemon-Handshake und geschlossener USB-Transport werden gemeinsam ersetzt, bevor Erfolg gemeldet wird. |
| 3.4.29.34 INTERN | Reparierte Anwendung intern vorbereiteter Levita-Datenoberflächen bei weiterhin strengem Symlink-Schutz für externe Importe; schnelles Zurückschalten auf das aktive TRCC-Originaldesign beim kontrollierten Programmende. |
| 3.4.29.33 INTERN | Dauerhafte RGB-Designmarkierung und Designfarben; vier begrenzte ENE-DRAM-Startversuche; LCD-Ebenen nebeneinander mit Ordnerimport, Zuordnung und Favoriten; zwei eigene Weltraum-Datenoberflächen; kompaktere globale Oberfläche und überarbeitete Geräte-/Linklisten in Über und Hilfe. |
| 3.4.29.32 INTERN | Helles Design mit lesbarer linker Navigation; LCD-Menü „Design anpassen“ rechts neben der Live-Vorschau; Hintergrund- und Datenkarten in 4–8 Spalten über die volle Galeriebreite. |
| 3.4.29.31 INTERN | Lesbares LCD-Menü „Design anpassen“ mit nutzbarer Größe für Zahlenfelder und Auswahlfenster; eigene Zeile für den schwarzen Balken; sauberes Beenden ohne Schreiben in ein zerstörtes Log-Widget. |
| 3.4.29.30 INTERN | Einstellbare Rundung der rechten Bild-/Videokante direkt vor dem schwarzen Levita-Notch-Balken; 48-px-Standard, gekoppelte oder getrennte obere/untere Regler und identische Geometrie in Vorschau und Hardwaremaske; Levita-Modul 1.4. |
| 3.4.29.29 INTERN | Ebene-2-Grafik und Notch-Maske wieder sichtbar; daemon-sicherer Video-IPC-Taktgeber; vorab skalierte, flüssigere Videovorschau. |
| 3.4.29.28 INTERN | Ein einziger TRCC-Daemon als dauerhafter Levita-USB-Besitzer; sämtliche Befehle über Unix-Socket; kein zweiter `display play`-Handshake nach erfolgreichem Theme-Laden. |
| 3.4.29.27 INTERN | Ebene-1-Bild/Video bleibt unter transparenter Ebene-2-Grafik sichtbar; große Videovorschau mit 16 Bildern bei 4 FPS; ausdrückliche Erkennung eines externen TRCC-/libusb-Prozessabsturzes. |
| 3.4.29.26 INTERN | Robuste Levita-Übertragung als ein zusammenhängendes Cache-Theme mit Video, Maske und Live-Blöcken; zusammengefasste schnelle Designwechsel, zehn Sekunden USB-Schutzpause und höchstens ein Handshake-Retry; Levita-Modul 1.3. |
| 3.4.29.25 INTERN | Eindeutige GitHub-Arbeitsregeln für Coding-KIs: ausdrücklich beauftragter normaler Entwicklungsbranch-Push auch bei `INTERN`, getrennte Freigaben für Pull Request, Tag, öffentlichen Release, Force-Push und Remote-Löschung. |
| 3.4.29.24 INTERN | Vollständig geprüfte Integration der 22/23-Levita-Bugfixes: fehlertoleranter Layoutimport, Symlink-Schutz, sicherer Split-Standard, bestätigter Rendererstart, vollständiges Vorschau-Shutdown, Levita-Modul 1.2 und validierte Benutzer-/Entwicklerpaketprofile. |
| 3.4.29.23 INTERN | Interner Zwischenstand mit sicherem Split-Fallback, bestätigter Renderer-Aktivmeldung und Hover-ffmpeg-Shutdown; vollständige Repository-Integration in 3.4.29.24. |
| 3.4.29.22 INTERN | Interner Zwischenstand mit isolierter Behandlung beschädigter Layoutdatensätze und Symlink-Schutz beim TRCC-Import; vollständige Repository-Integration in 3.4.29.24. |
| 3.4.28 INTERN | Standardmäßig eingeklappte Gehäuselüfterkarten, höchstens eine geöffnete Kurvenbearbeitung, weiter modularisierte lokale-KI-Struktur und robuster Fedora-Paketbau ohne zwingendes `dpkg-deb`. |
| 3.4.27 INTERN | Getrennte CoolerControl-Daemon-/Autostartanzeige, bestätigte Polkit-Dienstaktionen, einheitliche blau getönte Detailflächen auf allen Hauptseiten sowie vollständig blaue Kraken-Schnellprofile erst nach erfolgreicher Hardwareübertragung. |
| 3.4.25 INTERN | Neues PySide6-Dashboarddesign, kompakte Navigation ohne Community-Edition-Branding, neue Übersicht, modernisierte Kühlungszentrale, direkte System-Fan-Karten, separater Kurvendialog und vierstufiger Lüfter-Zuordnungsassistent. |
| 3.4.23.2 INTERN | Kompaktes Cooling-Dashboard, CoolerControl-Ownership-Sperre, einzelne System-Fan-Karten mit Kurvenvorschau sowie grafischer PWM/RGB-Gehäuse-Assistent mit sicherem 30/80-%-Kontrasttest und persistenter Einbauplatz-Zuordnung. |
| 3.4.23.1 INTERN | Polkit-geschützter NCT6687-Fan-Helper für root-geschützte hwmon-PWM-Schreibzugriffe, 10-s-Kalibrierung mit RPM-Verlauf, MSI-EC-verträgliche Zielbestätigung und treibereigene Firmwarekurven-Rückgabe über pwmN_enable=2. |
| 3.4.23 INTERN | Sichere Mainboard-Lüftersteuerung über Linux-hwmon/NCT6687 mit bestätigungspflichtiger 70-%-Kalibrierung, individuellen Sensorquellen/Kurven je PWM-Kanal, Leise/Ausbalanciert/Leistung-Vorlagen mit sicherer Empfehlung, Sensor-Fallback, optionalem nct6687d-10-s-Watchdog, Firmware-Rückgabe, Secure-Boot-/Treiberdiagnose sowie ENE-DRAM-Reinitialisierung im RGB-Studio. |
| 3.4.22 INTERN | RGB-/ENE-Stabilitäts-Hotfix mit wirklich langlebigem SDK-Worker, Direct+Native-Bestätigungsbarriere, gezieltem RAM-Reclaim im Einzeltest, repariertem LCD-GIF-Skalierungsaufruf und direkt aktivierten AM5-CPU-Kurven. |
| 3.4.21 INTERN | Zentraler Kraken-USB-/RGB-Request-Koordinator, stabiler RGB-Profilstart nach vollständiger Geräteerkennung, Shutdown-LCD-Fallback, reparierte Schnellprofile-Einbettung, ESC-Live-Renderer, dynamische LCD-Zielauflösung sowie skalierbare und animierte LCD-Vorschauen. |
| 3.4.20 INTERN | Einmaliges ENE-DRAM-Priming, popupfreier Tray-Autostart, Sprache zuerst im Setup, integrierte Hilfe, konsolidierter LCD-Arbeitsbereich, acht eingebaute OHC-GIFs, Uhr als Animationsebene und Import des aktuellen verschachtelten NZXT-ESC-v3-Formats. |
| 3.4.19 INTERN | LCD-Kachel-Dashboard, flüssigere externe GIF/Hardware-Rendererstarts, PAUSE/RESUME für LCD-Displayeinstellungen, stabileres ENE-DRAM-Direct und vollständige Discover/AppStream-Metadaten. |
| 3.4.18 INTERN | Unabhängiger NZXT-ESC-Schema-v3-Importer mit Pflicht-Vorschau/Kompatibilitätsbericht, lokale LCD-Profilbibliothek, einfacher Drag-and-drop-Editor, Sensor-Remapping, Originalzustand sowie vollständiges Backup/Restore ohne gebündelten Fremdcode oder Designs. |
| 3.4.16 INTERN | Serialisierte Latest-value-wins-Übernahme für RGB-Geschwindigkeit und andere Effektparameter, exakte SDK-Framebestätigung sowie ressourcenschonende automatische Geräteprüfung mit Schutz vor vorübergehenden 7→2-Inventarabfällen. |
| 3.4.15 INTERN | Modusabhängige Hex-/Standardfarben, benutzersortierbare RGB-/LCD-/Kühlungsbereiche sowie erweiterte und kartenweise ein-/ausblendbare CPU-/GPU-Übersicht. |
| 3.4.14 INTERN | NZXT-Alternating-Fallback ohne `KeyError`, sichere Unterscheidung eigener OpenRGB-Clients, begrenzte interne RGB-Fehlerliste ohne modale Teilfehlerdialoge sowie sichtbare Vorlage „Frelidon PC“. |
| 3.4.13 INTERN | Direkt anwendbare RGB-Kacheln einschließlich „Feste Farbe“, dauerhafte Ausgewählt-/Aktiv-Anzeige sowie sichere manuelle oder optionale automatische RGB-Wiederübernahme nach separatem OpenRGB. |
| 3.4.12 INTERN | Sortierbare Kraken-Kanäle, animierte RGB-Galerie, sicherer Profilstart, stabiler RGB-Scrollpunkt und LCD-Ebenenmodus mit drei neuen Originaldesigns. |
| 3.4.11 INTERN | Dauerhafter Loopback-SDK-Worker, gemeinsame 25-Hz-Mehrgeräteframes mit Latest-frame-wins, gemessene Übertragungsrate, RGB-Einrichtungsassistent, Einzelzonen-Sichttest und automatische Sapphire-External-Control-Vorbereitung. |
| 3.4.10 INTERN | Vollständige OpenRGB-Geräteframes mit einmaligem Zonen-Fallback, 24-LED-Profile für Interstellar V2 Normal/Reverse, Plausibilitätswarnungen, ehrlicher Status zwischen Serverbestätigung und physischer Ausgabe, ckb-next-Konflikterkennung sowie robusterer Auswahl-/Scrollschutz. |
| 3.4.9 INTERN | Sichere OpenRGB-ARGB-Zoneneinrichtung mit `Lüfter/Geräte × LEDs`, Thermaltake-Portvorschlägen, validiertem SDK-`RESIZEZONE`, profilgespeicherten Größen, konfigurationsbedingten Fehlern ohne Quarantäne und priorisierten NZXT-Aufträgen. |
| 3.4.8 INTERN | Bestätigte OpenRGB-Direct-Ausgabe über aktuelle Controllerdaten und vollständige Zonenwrites, Modus-/Farbrücklesung, Sperre separat laufender OpenRGB-Prozesse sowie NZXT-`sync` bei gemeinsamer Dreikanalauswahl. |
| 3.4.7 INTERN | OpenRGB-SDK-Protokoll 4/5 mit kompatibler Aushandlung für ENE-RAM, bereinigte NZXT-2023-Effektzuordnung ohne `marquee-4` sowie harte Einzelinstanz-Sperre vor sämtlichen Hardwarezugriffen. |
| 3.4.6 INTERN | Klarere Liste ausgewählter RGB-Geräte mit Steuerweg und Ergebnisstatus, automatische Sitzungsprotokolle, fehlertolerante Mehrgeräteaktionen, einmalige Direct-Mode-Vorbereitung pro Gerät, getrennte GPU-/Hardwaremodus-Auswahl, Scrollpositionsschutz sowie Ausblendung des doppelt dargestellten NZXT-Controllers. |
| 3.4.5 INTERN | Begrenzter Loopback-SDK-Schreibpfad für Direct-Geräte ohne OpenRGB-CLI-`ApplyOptions`, Scrollpositionsschutz, geordnetes 12-Lüfter-Thermaltake-Profil und Hinzufügen/Bearbeiten/Entfernen/Auto-Anordnen eigener PC-Blöcke. |
| 3.4.4 INTERN | Atomare Reset-/Engine-Neustartfolge, vorgemerkte Schreibfreigabe bis zur frischen Erkennung, Zusammenführung vollständig gespiegelter OpenRGB-Inventare, Zonenprotokollierung und verschiebbare Thermaltake-PC-Ansicht mit aktuellem 120-mm-Lüfterlayout. |
| 3.4.3 INTERN | Sitzungsspezifische Isolation einzelner OpenRGB-`ApplyOptions`-Absturzgeräte, fortgesetzte Test-/Befehlsfolgen, echte Fehlerzählung pro Direct-Gerät und eindeutige OpenRGB-Indexdiagnose. |
| 3.4.2 INTERN | Start-Hotfix für die zu früh gelesene RGB-Vorschauuhr, defensiver Initialisierungsfallback sowie automatische private Start-/Absturzprotokolle im XDG-Zustandsverzeichnis. |
| 3.4.1 INTERN | Serielle OpenRGB-Einzelgerätebefehle gegen den rc2-Mehrgeräteabsturz, persistente Auswahl/Gruppen, native Fallbacks für Geräte ohne Direct Mode, eindeutige Gerätenamen, Einzelgeräte-Testmodus sowie PC-Skizze mit Frelidons A1-/A2-/B6-/B7-/SYS-FAN6-/Kraken-Profil. |
| 3.4.0 INTERN | Automatisch verwaltete fensterlose RGB-Engine, Fremdinstanz- und Mehrfachprozess-Sperre, Gerätekacheln, Drag-&-Drop-Gruppen mit unabhängigen Effekten, ENE-DRAM-Deduplizierung, topology-sichere NZXT-Effekte und bestätigter Komplett-Reset. |
| 3.3.0 INTERN | Eigenes RGB-Studio über lokalen OpenRGB-SDK-Client, statische Einzelgerätefarben, native Modi, zehn OHC-Effekte, sieben Vorlagen, Profilintegration, sitzungsweise Schreib-/Besitzsperren und standardmäßig verborgene experimentelle Desktop-Designs. |
| 3.2.0 INTERN | Windows-8/8.1-Kachelübersicht und Charms-Leiste, freie auswählbare OHC-Symbole/Mauszeiger, selektierbare Backups mit Aufbewahrung und sicherem Export/Import sowie Breeze-Light-Notfallrücksetzung. |
| 3.1.1 INTERN | Distributionsübergreifende Qt-6-D-Bus-Erkennung, Fedora-`qdbus-qt6`-Korrektur sowie bestätigte automatische Installation optionaler KDE-Desktop-Werkzeuge über DNF, APT, Pacman und Zypper. |
| 3.1.0 INTERN | Reversible KDE-Plasma-Desktop-Designs im Windows-11- und macOS-Stil mit Vorschau, Bestätigung, Backup, automatischem Rollback und interner Paketkennzeichnung. |
| 3.0.9 | Öffentliche Multi-Hardware-Version: direkte OpenLinkHub-Maustastenbelegung, begrenzte fensterlokale Tastaturmakros, saubere LCD-Temperaturbilder, Celsius/Fahrenheit sowie RPM-/DEB-/ZIP-Pakete. |
| 3.0.7 INTERN | Originale Kraken-Wassertemperaturanzeige beim echten Beenden sowie eigene interaktive OpenLinkHub-Maus-SVGs mit Modellfamilien, Hotspots und auslesbaren Tastenfunktionen. |
| 3.0.6 INTERN | Vollständige LCD-/GIF-Moduswiederherstellung aus Startprofilen, fünf Sekunden verzögerter LCD-Autostart, zuverlässiger Tray-Zustand und geordnete Sitzungssignale. |
| 3.0.5 INTERN | Softwaregeregelte Pumpen- und Lüfterkurven nach CPU-Temperatur mit Glättung, Hysterese, GIF-USB-Koordination, Profilmigration, Sensorfehler- und Beenden-Fallback. |
| 3.0.4 INTERN | Sitzungsweise freigegebene, validierte OpenLinkHub-Steuerung für Kühlung, RGB/LCD, Maus, Tastatur und Headset über die lokale API. |
| 3.0.3 INTERN | Stabile, theme-unabhängige Aktivfarbe für Manuell/Kurve auf Basis des zuletzt bestätigten Gerätebefehls; kein vorzeitiger Qt-Checkzustand. |
| 3.0.2 INTERN | Eindeutige kanalgetrennte Umschaltung zwischen manueller fester Drehzahl und Pumpen-/Lüfter-Hardwarekurve mit synchroner Aktivmarkierung. |
| 3.0.1 INTERN | Koordinierte PAUSE-/RESUME-USB-Übergabe: Pumpen-, Lüfter-, Kurven- und Profiländerungen während GIF-/Hardwareanimation; derselbe vorbereitete Stream läuft danach automatisch weiter. |
| 3.0.0 INTERN | Gemeinsame Open-Hardware-Control-Oberfläche, hierarchische Navigation, hardwareabhängige Module, vollständiges NZXT-Modul und sichere read-only OpenLinkHub-Geräteintegration mit Benutzerdienst-Aktionen. |
| 2.9.23 INTERN | Live aktualisierte CPU-/GPU-Werte in animierten Hardwaredesigns über isolierten Renderprozess; Wasser bleibt letzter sicherer Kraken-Wert. |
| 2.9.22 INTERN | Fünf nahtlose 20/25-FPS-Hardwareanimationen mit Ringen/Orbits sowie gemeinsamer 70–150-%-Regler für Schrift- und Zahlengröße. |
| 2.9.21 INTERN | Fünf runde Live-Hardwaredesigns für Wasser/CPU/GPU, dGPU-Sensorauswahl, Eisblau plus Farbvorlagen und `#RRGGBB`, vollständige Sprachumschaltung nach Einstellungswiederherstellung. |
| 1.0 | Erste Grundsteuerung der NZXT Kraken über liquidctl. |
| 2.0 | PySide6-Oberfläche, Live-Status, feste Pumpen-/Lüfterwerte, Schnellprofile, Kurven, Sicherheitsumschaltung, RGB, LCD-Bilder, Einstellungen, Autostart, Tray, Installer und Deinstaller. |
| 2.1 | Serielle asynchrone QProcess-Warteschlange; Entfernung des absturzanfälligen QThreadPool/QRunnable-Aufbaus. |
| 2.2 | Eindeutige LCD-Einzelübertragung und optionaler Wiederholungs-Fallback. |
| 2.3 | LCD-Uhr, runde Vorschau, Frelidon-Branding, Über-Bereich, GPL-Lizenz, Diagnosewerkzeug und englische Grunddokumentation. |
| 2.3.1 | Sicherheitsbestätigungen, sichere Kurvenprüfung, 65/65-Standardprofil, stärkere Anonymisierung und ../../.github/SECURITY.md. |
| 2.4 | Transparente Links zu Websites, Quellcode und Lizenzen; offizieller NZXT-Gerätelink. |
| 2.5 | Klare Beschränkung auf Kraken, zugehörige Radiatorlüfter, LCD und separaten NZXT-RGB-Controller. |
| 2.6 | Grafischer Kurveneditor, Live-Temperaturmarker, Hell/Dunkel/System und Hex-Akzentfarben. |
| 2.7 | Tastaturbedienung, AMD-AM5-Profile, CPU-Temperatur und -Assistenz, udev-Reparatur und dynamische Komponentenstände. |
| 2.7.1 | Direct-Access-Hotfix für Pumpen- und Lüfterkurven. |
| 2.8 | Expertenmodus, Anzeige des aktiven Kühlmodus und automatisches erneutes Senden der LCD-Uhr. |
| 2.8.1 | Abhängigkeitsprüfung vor PySide6-Start und kontrollierte DNF-Installation. |
| 2.9 | Ersteinrichtungsassistent, zwölf prozedurale Animationen, adaptive DPI-/Monitorlayouts, kategorisierte Profile, Import/Export, Startprofile und vollständiger Quellcode-Snapshot. |
| 2.9.1 | CPU-Offscreen-Renderer und getrennte Hintergrund-/Inhaltsebenen; vollständigeres Klick-, Änderungs-, Menü-, Tastatur- und Navigationsprotokoll mit Log-Export. |
| 2.9.2 | Scrollbare Einstellungen, größeres Hauptfenster und einmalige Layoutmigration für bestehende Installationen. |
| 2.9.3 | Light-Theme-/Hintergrund-Hotfix für stabile Ebenenreihenfolge und RGB32-Rendering. |
| 2.9.4 | Animationen lassen sich nach dem Ausschalten wieder aktivieren; letztes Thema bleibt erhalten. |
| 2.9.5 | Direct Access für alle Kühlungswrites, stiller Hintergrundbetrieb bei Berechtigungsfehlern und 10.000-Zeichen-Loglimit. |
| 2.9.6 | LCD-Uhr-Regression beim Start behoben und durch Regressionstest abgesichert. |
| 2.9.20 INTERN | Vereinfachte normale FPS-Auswahl, erweiterte Diagnoseoptionen, wahrscheinliche GIF-Loop-Warnung und nahtlos neu erzeugte Moving-Bars-Testdateien. |
| 2.9.19 INTERN | Streng fortlaufende LCD-Phasen, phasenstabiler 26,667-Hz-CAM-Zieltakt und sanfter Abbau einzelner Überläufe in höchstens 0,25-ms-Schritten. |
| 2.9.17 INTERN | ACK-synchronisierte CAM-Taktung direkt nach `37 02`, 0,10-ms-CAM-Abstand und Diagnosekennung `cam-raw-ack-paced` gegen horizontales Tearing und Mikroruckler. |
| 2.9.16 INTERN | Exklusiver Kraken-Zugriff während GIF-Streaming, eindeutige `37 01`/`37 02`-ACK-Zuordnung trotz ungefragter Statusberichte, 12-Sekunden-Watchdog und automatischer Wiederanlauf von Statusabfragen/Kühlbefehlen. |

## Funktionen nach Kategorien

### Kühlung

- Live-Wassertemperatur, Pumpen- und Lüfterwerte – 2.0
- feste Werte und Schnellprofile – 2.0
- Temperaturkurven – 2.0
- grafischer Kurveneditor – 2.6
- AMD-AM5-CPU-Assistenz – 2.7
- Direct Access für Kurven – 2.7.1
- Expertenmodus und aktive Modusanzeige – 2.8
- kategorisierte Kühl- und Gesamtprofile – 2.9
- Mainboard-PWM-Erkennung über Linux-hwmon/NCT6687 ohne feste Kanalzuordnung – 3.4.23
- sichere 70-%-/10-s-Kalibrierung mit RPM-Beobachtung und automatischer Wiederherstellung – 3.4.23.1
- individuelle Mainboard-Lüfterkurven mit CPU/GPU/Kühlmittel/Maximum/gewichteter Sensorquelle – 3.4.23
- Sensorfehler-Fallback, 90-°C-Notanforderung und Firmware-Rückgabe – 3.4.23

### LCD

- statische Bilder, Helligkeit und Ausrichtung – 2.0
- eindeutiger Wiederholungs-Fallback – 2.2
- Uhr, Datum und runde Vorschau – 2.3
- automatisches erneutes Senden der Uhr – 2.8
- LCD- und Gesamtprofile – 2.9

### Design und Anzeige

- Hell, Dunkel, System und Hex-Akzent – 2.6
- Ersteinrichtungsassistent – 2.9
- zwölf animierte prozedurale Hintergründe – 2.9
- DPI-/Monitorerkennung, 16:10, 16:9, 21:9 und 32:9 – 2.9
- UI-Skalierung 80–180 Prozent – 2.9
- Design- und Gesamtprofile – 2.9
- sicherer CPU-Offscreen-Hintergrundrenderer – 2.9.1
- scrollbare Einstellungen und vergrößertes Hauptfenster – 2.9.2
- experimentelle Desktop-Designs standardmäßig aus und verborgen – 3.3.0

### RGB-Studio

- statische Farbe pro OpenRGB-Gerät und gemeldete native Hardwaremodi – 3.3.0
- zehn eigene OHC-Softwareeffekte und sieben Designvorlagen – 3.3.0
- Loopback-only SDK-Client, Sitzungsfreigabe und Gerätebesitzsperren – 3.3.0
- Speicherung in exportierbaren Gesamt-/RGB-Profilen – 3.3.0
- verwaltete RGB-Engine ohne manuellen Serverstart – 3.4.0
- Gerätekacheln, Mehrfachauswahl und Drag-&-Drop-Gruppen – 3.4.0
- unabhängige Gruppeneffekte und gemeinsame NZXT-/OpenRGB-Auswahl – 3.4.0
- ENE-DRAM-Aliasfilter und vollständige LED-Listenübernahme – 3.4.0
- topology-sichere NZXT-Effekte und kompletter Geräte-Reset – 3.4.0
- serielle Einzelgeräteausgabe, native Fallbacks und persistente Gruppenzuordnung – 3.4.1
- PC-Skizze, freie Gerätenamen und Frelidons vorbereitetes Hub-/Lüfterprofil – 3.4.1

### Installation und Dokumentation

- Installer, Desktopdatei und Deinstaller – 2.0
- Diagnosewerkzeug – 2.3
- Sicherheitsdokumentation – 2.3.1
- Software-, Quellcode- und Lizenzlinks – 2.4
- Komponentenstände – 2.7
- Abhängigkeitsinstallation – 2.8.1
- zusätzlicher Quellcode-Snapshot und Manifest – 2.9
- detailliertes Benutzeraktionsprotokoll und Log-Export – 2.9.1


### 2.9.4
- Reaktivierbare Hintergrundanimationen mit gespeichertem letzten Thema.
