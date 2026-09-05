# Open Hardware Control — verbindliches Modulregister

**Stand:** 05.09.26
**Anwendung:** 3.4.29.44 STABLE

Diese Datei ist der verpflichtende erste Wegweiser für lokale und webbasierte Coding-KIs. Sie beantwortet, welches Modul für eine Aufgabe zuständig ist, wo ausschließlich dessen aktuelle Version liegt und welche Dateien dafür gelesen werden müssen. Änderungen an Quellcode, Modulstruktur, Modulversionen oder Verantwortlichkeiten müssen dieses Register im selben Arbeitsschritt aktualisieren. Das Auslassen ist nicht zulässig.

## Pflichtablauf für jede KI

1. `AGENTS.md` und anschließend dieses Modulregister vollständig lesen.
2. In der Tabelle genau das betroffene Modul bestimmen.
3. Für Umsetzungsschritte `AI_DEVELOPMENT_GUIDE.md` lesen und danach nur den aktuellen Modulordner, dessen README, öffentliche Schnittstellen und gezielte Tests laden.
4. Keine ältere Modulversion im Arbeitsbaum suchen oder neu anlegen.
5. Bei einer Änderung Modulversion, Pfad, Abhängigkeiten, Tests und Änderungsregister hier aktualisieren.
6. Datumsangaben ausschließlich als `TT.MM.JJ` erfassen. Keine Uhrzeit und keine lokalen Benutzer-/Rechnerdaten eintragen.

## Größenbudget für lokale KI mit 16 GB VRAM

- Zielwert einer normalen handgeschriebenen Quelldatei: höchstens **600 Zeilen** und **32.000 Zeichen**.
- Ab **800 Zeilen** oder **40.000 Zeichen** muss vor weiterer Fachlogik in Unterdateien aufgeteilt werden.
- Neue handgeschriebene Dateien über **1.200 Zeilen** oder **60.000 Zeichen** sind verboten. Ausnahmen gelten nur für generierte Dateien oder ausdrücklich hier dokumentierte Legacy-Dateien mit aktivem Zerlegungsplan.
- Eine Funktion soll höchstens 80 Zeilen, eine Klasse höchstens 300 Zeilen besitzen. UI-Aufbau, Zustandsmodell, Persistenz, Rendering und Hardwarebefehle gehören in getrennte Dateien.
- Wenn eine Aufgabe das Budget überschreiten würde, wird ein Untermodul angelegt; beispielsweise `layout_model.py`, `layout_canvas.py` und `theme_adapter.py` statt eines neuen großen `display_ui.py`-Blocks.

## Ordner- und Versionsregel

- Neue oder migrierte Fachmodule liegen unter `modules/<modulname>/v<major>_<minor>/`.
- Jeder aktuelle Versionsordner enthält ein `__init__.py`, ein kurzes `README.md` und kleine Dateien nach Verantwortlichkeit.
- Die Modulversion beginnt bei `1.0`. Eine neue Funktion oder ein geänderter Vertrag erhöht sie nachvollziehbar, beispielsweise auf `1.1`; ein grundlegender inkompatibler Vertrag auf `2.0`.
- Im Arbeitsbaum bleibt nur der aktuelle Versionsordner. Git-Historie, Tags und Releases sind die Rückfallebene; parallele `old`, `backup`, `copy` oder veraltete Versionsordner sind nicht erlaubt.
- Ein bestehender Root-Einstieg darf während der schrittweisen Migration als dünne Kompatibilitätsschicht bleiben. Neue Fachlogik darf dort nicht weiter anwachsen.
- Abhängigkeiten zeigen nach innen: Versionsmodule importieren niemals den großen UI-Orchestrator `kraken_control.py` und niemals ihre aufrufende Root-UI-Datei zurück.

## Aktuelle Modulübersicht

| Modul | Modulversion | Aktueller Pfad | Einstieg / Verantwortung | Status |
|---|---:|---|---|---|
| Levita LCD-Datenoberfläche | 1.4 | `modules/lcd_levita/v1_4/` | `layout_model.py` für fehlertolerante Datenblöcke/Persistenz, `layout_canvas.py` für Mittelpunkt-geometrisches Drag-and-drop und die konfigurierbare rechte Bildkante, `panel_geometry.py` für getrennte obere/untere innere Bildradien sowie die äußere Panelkontur, `runtime_policy.py` für sichere persistierte UI-Werte, `theme_adapter.py` für read-only TRCC und ein zusammenhängendes Cache-Theme aus Video, Maske und Live-Blöcken | Versionierter Modulordner |
| Levita LCD-Orchestrierung | Legacy 3.4.29.43 | `thermalright_display_ui.py`, `thermalright_display.py` | Zwei große Ebenengalerien; explizite Allowlist für elf eigene Hintergründe und eine eigene 30-Sekunden-Animation; persistente Intensität 25–150 % für beide Ebenen; Orbital-Standard 130 %; read-only AMD-Taktprüfung und begrenztes `overlay-update` über den vorhandenen TRCC-Daemon; Neuverbindungsbarriere, IPC-Warteschlange und daemon-sicheres Beenden | Schrittweise Zerlegung aktiv |
| Hauptfenster und Seitenkomposition | Legacy 3.4.29.43 | `kraken_control.py`, `dashboard_layout.py`, `localization_catalog.py` | Anwendungseinstieg und noch nicht extrahierte Controller; verzögerter RGB-Profilstart bei vorläufiger OpenRGB-Teilerkennung; benannter Startbildschirm mit Hauptbildschirm-Rückfall; global einheitliche schmale Scrollleisten; kompakte Oberfläche, Hilfeseiten und Dashboard-Anordnung | Größen-Ausnahme; neue Monitor- und Wallpaper-Fachlogik ausgelagert |
| NZXT Kraken | 1.0 legacy | `nzxt_backend.py`, `kraken_sensors.py`, `kraken_cam_streamer.py`, `kraken_lcd_designs.py`, `nzxt_rgb.py` | Erkennung, Sensoren, LCD-Transport und RGB | Ordner-Migration ausstehend |
| Mainboard-Kühlung | 1.0 legacy | `mainboard_fan_control.py`, `ohc_fan_helper.py`, `cooling_ownership.py` | hwmon/NCT6687, Polkit-Helfer und Besitzschutz | Ordner-Migration ausstehend |
| OpenRGB Studio | 1.1 | `modules/rgb_studio/v1_1/`, `openrgb_integration.py`, `openrgb_sdk.py`, `rgb_devices.py`, `rgb_effects.py`, Legacy-UI in `kraken_control.py` | `ene_start_recovery.py` für die begrenzte zeitversetzte ENE-DRAM-Startfolge; `design_gallery.py` für die hardwarefreie Galerie mit Auswahl und Rechtsklick-Absicht; Engine-Schalter, Gesamthelligkeit und native Ergebnisliste bleiben bis zur weiteren UI-Auslagerung im Orchestrator | Galerie und ENE-Startlogik versioniert; weitere UI-Migration ausstehend |
| Corsair/OpenLinkHub | 1.0 legacy | `openlinkhub_integration.py`, `openlinkhub_mouse_visuals.py` | Validierte lokale API und Mausdarstellung | Ordner-Migration ausstehend |
| Wallpaper Engine for KDE | 1.2 | `modules/wallpaper_engine/v1_2/` | `library.py` für schreibgeschützte Steam-/Video-Erkennung; `plasma.py` für Plasma-Zustand, DisplayMode-Skripte und Wiedergabe am registrierten Plasma-D-Bus-Objekt; `installer.py` für versions-/architekturgenaue offizielle RPM-Auswahl, begrenzten Download und SHA256-Prüfung; `onboarding.py` für Erststartanleitung und zweistufig bestätigte Polkit-/DNF-Installation; `page.py` für Galerie, stabile Kartenmaße, Bildschirmziel, Wiedergabe, Skalierung, Original-KCM und rücksetzbare Profile | Versionierter Modulordner; keine Upstream-Dateien oder Medien enthalten; Passwort bleibt ausschließlich bei Polkit |
| Fensterplatzierung | 1.0 | `modules/window_placement/v1_0/` | `placement.py` normalisiert Hauptbildschirm-/Namenspräferenzen, löst den gewünschten `QScreen` ohne Qt-Abhängigkeit auf und fällt bei fehlendem Monitor auf den Hauptbildschirm zurück | Reines Richtlinienmodul; KWin behält unter Wayland die endgültige Platzierungsentscheidung |
| Desktop-Designs | 1.0 legacy | `desktop_shell.py`, `desktop_designs.py`, `desktop_assets.py` | KDE-Designvorschau, Backup und Anwendung | Ordner-Migration ausstehend |
| Gemeinsame Infrastruktur | 1.0 legacy | `app_constants.py`, `command_backend.py`, `privacy_logging.py`, `window_diagnostics.py`, `hardware_diagnostics.py`, `log_view_support.py`, `temperature_utils.py`, `ui_layout.py`, `dashboard_layout.py` | Identität, Prozesse, Datenschutz, read-only Sensor-Plausibilitätsprüfung, getrennte Log-Ansichten, Diagnose und kleine Dashboard-Komposition | Ordner-Migration nur bei konkreter Änderung |
| Release-Paketierung | 1.0 | `scripts/build_release.py`, `scripts/backup_release.py`, `scripts/check_release.sh` | Reproduzierbare Pakete plus atomare externe Sicherung der zwei neuesten vollständigen Versionssätze nach `RELEASE_BACKUP_POLICY.md` | Aktiv |

## Erlaubte Abhängigkeiten für Levita LCD 1.4

```text
thermalright_display_ui.py
  -> modules/lcd_levita/v1_4/layout_canvas.py
  -> modules/lcd_levita/v1_4/layout_model.py
  -> modules/lcd_levita/v1_4/theme_adapter.py
  -> modules/lcd_levita/v1_4/panel_geometry.py
  -> modules/lcd_levita/v1_4/runtime_policy.py
  -> thermalright_display.py

layout_canvas.py -> layout_model.py + panel_geometry.py + stabile Geometrie aus thermalright_display.py
theme_adapter.py -> layout_model.py + optional installiertes TRCC-Lesemodul
panel_geometry.py -> keine Qt-, UI- oder Hardwareabhängigkeit
runtime_policy.py -> keine Qt-, UI- oder Hardwareabhängigkeit
layout_model.py  -> keine Qt-, UI- oder Hardwareabhängigkeit
```

`config1.dc` wird ausschließlich gelesen und niemals verändert. Editierbare Laufzeit-Themes liegen im OHC-Cache, verwenden `trcc.json` und verweisen nur symbolisch auf lokale Originalmedien.

## Gezielte Tests

| Modul | Pflichttests |
|---|---|
| Levita LCD 1.4 | `tests/test_levita_layout_module_342918.py`, `tests/test_thermalright_display_3429.py`, `tests/test_thermalright_preview_queue_342914.py`, `tests/test_thermalright_ui_static_3429.py`, Offscreen-UI-Aufbau |
| OpenRGB Studio 1.1 | `tests/test_rgb_profile_autostart_342943.py`, `tests/test_openrgb_integration.py`, `tests/test_openrgb_sdk.py`, `tests/test_ene_dram_cold_boot_34221.py`, Offscreen-UI-Aufbau |
| Wallpaper Engine for KDE 1.2 | `tests/test_wallpaper_engine_342942.py`, `tests/test_full_ui_build_34291.py`, `tests/test_ui_customization_3425.py` |
| Fensterplatzierung 1.0 | `tests/test_window_placement_342942.py`, `tests/test_full_ui_build_34291.py` |
| Modulstruktur/Regeln | `tests/test_module_registry_342918.py`, `tests/test_modularization_3427.py`, `tests/test_agent_project_memory_3426.py` |
| Release-Paket | `tests/test_release_backup_342936.py`, `tests/test_thermalright_ui_static_3429.py`, `scripts/check_release.sh` |

## Legacy-Ausnahmen mit aktivem Zerlegungsplan

| Datei | Grund | Nächster Schnitt |
|---|---|---|
| `kraken_control.py` | Historischer Anwendungseinstieg mit Kompatibilitätsnamen | Jeweils eine Seite oder einen Controller pro Version in einen Modulordner extrahieren |
| `thermalright_display_ui.py` | Bereits laufend entwickelte Karten-, Vorschau- und Prozessoberfläche | Katalog/Thumbnail-Warteschlange als nächstes getrennt auslagern; keine neue Layout-Fachlogik mehr hier ablegen |

## Änderungsregister

| Datum | Modul | Version | Änderung |
|---|---|---:|---|
| 05.09.26 | Release-Paketierung / Levita-Testumgebung | 1.0 / Legacy 3.4.29.43 | GitHub Actions installiert die vollständigen Python-/Qt-Testabhängigkeiten samt EGL-Laufzeit; Vorschau-Warteschlangentest misst vorhandene gebündelte Medien relativ zum echten Anfangszustand statt einen leeren Cache vorauszusetzen |
| 05.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.43 | Acht weitere eigene 1600×720-KI-Hintergründe und genau eine deduplizierte 30-Sekunden-Animation über eine feste Paket-Allowlist in die OHC-Galerie aufgenommen; Hersteller-/TRCC-Katalogmedien bleiben ausgeschlossen |
| 05.09.26 | Hauptfenster und Seitenkomposition / OpenRGB Studio | Legacy 3.4.29.43 / 1.1 | Gespeicherten RGB-Profilstart bei absichtlich zurückgehaltener erster OpenRGB-Teilerkennung vorgemerkt gehalten; begrenzte Inventarwiederholung übernimmt das Design nach vollständiger Erkennung statt den einmaligen Startwunsch zu verwerfen |
| 05.09.26 | Release-Paketierung | 1.0 | Modulregisterprüfung vom fest verdrahteten internen Kanal auf den validierten Inhalt von `BUILD_CHANNEL` umgestellt; stabilen RPM-Quellbaum unter einen eigenen temporären Elternordner gelegt, damit er nicht mit dem gleichnamigen Laufzeitbaum kollidiert |
| 05.09.26 | Wallpaper Engine for KDE | 1.2 | Pause/Fortsetzen/Weiter/Ton vom nicht vorhandenen separaten Alias auf das nachweislich unter `org.kde.plasmashell` registrierte `/WallpaperEngine`-Objekt umgestellt; Zurück wegen fehlender echter CaptSilver-v1.4-API über die vorherige validierte lokale Workshop-Karte umgesetzt; DisplayMode 0/1/2 pro Zielbildschirm ergänzt |
| 05.09.26 | Fensterplatzierung | 1.0 | Hauptbildschirm als Standard sowie persistente Auswahl über den stabilen Qt-Bildschirmnamen mit sicherem Hauptbildschirm-Rückfall eingeführt; Platzierung bleibt unter Wayland eine Anforderung an KWin |
| 05.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.42 | Wiederhergestellte Fenstergeometrie vor dem Anzeigen an die Bildschirmpräferenz gebunden und alle Scrollbereiche, Listen und Tabellen über ein gemeinsames acht Pixel schmales Scrollleisten-Design vereinheitlicht |
| 05.09.26 | Wallpaper Engine for KDE | 1.1 | Wiederaufrufbaren Erststart-Assistenten, Fünf-Workshop-Checkliste, Steam-/Workshop-Links und Fedora-Installer ergänzt; offizielles RPM wird vor der getrennt bestätigten Polkit-/DNF-Aktion anhand GitHub-Metadaten, Fedora-Version, Architektur, Größe und SHA256 geprüft; Galerie behält nach Apply-Refresh feste Kartenmaße |
| 05.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.41 | Neue Standardfolge LCD → Wallpaper Engine → optional OpenLinkHub → Profile → Einstellungen → Über → Log; nur exakt alte Standardfolgen werden migriert, eigene Sortierungen bleiben erhalten; eigene Wayland-Fensterdekoration wegen separatem Eingabe-/Resize-Testumfang bewusst auf eine Folgeversion verschoben |
| 05.09.26 | Release-Paketierung | 1.0 | Sicherheitsbericht weist den einzigen ausdrücklich ausgelösten und SHA256-verifizierten Plugin-Download getrennt von weiterhin verbotenen automatischen Desktop-Downloads aus |
| 05.09.26 | Wallpaper Engine for KDE | 1.0 | Lokale Workshop-/Video-Galerie, Multi-Monitor-Auswahl, CaptSilver-D-Bus-Steuerung, Original-KCM, sichere Videoordnergrenze und rücksetzbares Leistungsprofil ohne Upstream-Patches ergänzt |
| 05.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.40 | Wallpaper Engine als frei anordenbaren sichtbaren Navigationspunkt und zwölfte Hauptseite ergänzt; integriertes Hilfethema verweist auf den sicheren Original-/Optimierungsweg |
| 04.09.26 | Gemeinsame Infrastruktur | Legacy 3.4.29.39 | Normale Qt-Tooltips und direkte ComboBox-Popupframes aus der Fensterdiagnose gefiltert; unbekannte Popups und exakte 640×480-Quarantäne bleiben aktiv |
| 04.09.26 | OpenRGB Studio | 1.1 | Hardwarefreie Designgalerie aus dem Hauptorchestrator ausgelagert; Engine-Steuerung in „Geräte und Effekte“ eingebettet, Ein/Aus-Schalter, persistente effektabhängige Rechtsklick-Farben, Gesamthelligkeitsleiste und native Kanalergebnisse ergänzt; frühe Sequenzabbrüche schließen ENE-Callbacks zuverlässig ab |
| 03.09.26 | Release-Paketierung | 1.0 | Externen Geschwisterordner `Open Hardware Control Backup` eingeführt; erfolgreiche Builds sichern atomar alle Artefakte, Entwicklerquellen und SHA256 und bewahren ausschließlich die zwei neuesten erkannten Versionsordner auf |
| 03.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.35 | Veralteten TRCC-Handshake nach Abziehen reproduziert; vor Design, Farbtest und Displayeinstellungen eine serialisierte Trennen-/Neuverbinden-Barriere mit verpflichtendem echtem Handshake ergänzt und am 1600×720-Gerät validiert |
| 03.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.34 | Validierten privaten Cache mit verknüpften Medien wieder als Runtime-Theme zugelassen, externe Importgrenze symlink-strikt belassen und beim kontrollierten Beenden einen auf 1,5 Sekunden begrenzten `stop-video`-Daemonaufruf ergänzt |
| 01.09.26 | Levita LCD-Datenoberfläche | 1.0 | Versionierten Modulordner eingeführt; einzelne Live-Datenblöcke einschließlich zusammengefasster CPU/GPU-Beschriftung plus Auslastungswert, gemeinsamer Offset, Kontextbearbeitung, klare Cache-Statusmeldungen, OHC-Override-Persistenz und read-only TRCC-Staging getrennt |
| 01.09.26 | Projektarchitektur | 1.0 | Verbindliche Modul-, Größen-, unabhängige Anwendungs-/Modulversions-, Datums- und Registerpflege-Regeln für lokale KIs eingeführt |
| 01.09.26 | KI-Entwicklungsanleitung | 1.0 | Verbindliche Schrittfolgen für UI-, Sensor- und LCD-Erweiterungen sowie Abschlusskontrolle ergänzt |
| 01.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.19 | Editierbare Cache-Themes mit validiertem `trcc.json` als vollständige TRCC-Hardwaredesigns zugelassen; doppelte Vorschauaufbauten beim Auswahlwechsel entfernt |
| 01.09.26 | Levita LCD-Datenoberfläche | 1.1 | Vorschau auf TRCC-Mittelpunkt-Koordinaten korrigiert; Videoframes aktualisieren nur den Hintergrund und lassen aktive Drag-Objekte bestehen; Rechtsklick fordert den eingebetteten Seiteneditor statt externer Dialoge an |
| 01.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.20 | Erneute Auswahl lädt Hintergrund und Datenebene sofort; letzter gültiger Videoframe bleibt während asynchroner Vorbereitung sichtbar |
| 01.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.20 | Dashboard-Anordnung in `dashboard_layout.py` extrahiert; Kraken-Wassertemperaturkarte ohne verbundene Hardware oder echten Kühlmittelwert automatisch verborgen, gespeicherte Benutzerauswahl bleibt erhalten |
| 02.09.26 | Levita LCD-Datenoberfläche | 1.1 | Gerade Notch-Innenkante und abgerundete äußere rechte Displayecken in `panel_geometry.py`; Vorschau und erzeugtes Cachebild nutzen dieselbe Kontur |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.21 | Klick auf eine Ebene-1-Karte setzt Bild oder gecachten Videoframe sofort in die große Vorschau; kein erzwungenes Schwarz vor dem ersten Standbild |
| 02.09.26 | Levita LCD-Datenoberfläche | 1.2 | Fehlerhafte importierte Einzelelemente werden isoliert übersprungen; sichere Split-Modus-Richtlinie ergänzt und einzigen aktuellen Modulordner auf `v1_2` angehoben |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.24 | Symlink-Dateien in TRCC-Themes abgewiesen; Livestream erst nach `QProcess.started` als aktiv gemeldet; Startfehler in begrenzten Autostart-Retry geführt; Hover-ffmpeg und Timer beim Beenden vollständig gestoppt |
| 02.09.26 | Release-Paketierung | 3.4.29.24 | Installationspaket und vollständiges Entwicklerpaket als getrennte Profile validiert; Local-AI-Gitbundle aus einem temporären Snapshot exakt des geprüften Entwicklerbaums statt aus möglicherweise älterem Commit erzeugt |
| 02.09.26 | GitHub-/KI-Arbeitsregeln | 3.4.29.25 | Normalen, ausdrücklich beauftragten Entwicklungsbranch-Push auch bei `INTERN` eindeutig von Pull Request, Tag, öffentlichem Release, Force-Push und Remote-Löschung getrennt; widersprüchliche absolute Push-Sperre entfernt |
| 02.09.26 | Levita LCD-Datenoberfläche | 1.3 | Gewähltes Hintergrundvideo und erzeugte Displaymaske gemeinsam mit den bearbeiteten Live-Blöcken in ein Cache-Theme eingebunden; TRCC kann die komplette Komposition in einer verbundenen `load-theme`-Sitzung anwenden |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.26 | Schnelle vollständige Designwechsel auf den letzten Wunsch zusammengefasst, zehn Sekunden Schutzpause nach bestätigtem Start und Handshake-Timeout auf insgesamt einen Retry begrenzt |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.27 | Alpha-Kanal der Ebene-2-Grafik in der großen Vorschau erhalten, ausgewählte Videos als begrenzte 16-Bild-Folge animiert und externe TRCC-/libusb-Prozessabstürze ausdrücklich erkannt |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.28 | Alle TRCC-Befehle über den offiziellen Daemon-/Unix-Socket-Modus an einen einzigen USB-Besitzer geleitet und den zweiten `display play`-Prozess nach erfolgreichem `load-theme` entfernt |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.29 | Kombinierte Design-/Notch-Maske nach `load-theme` ausdrücklich aktiviert, Video über einen reinen Daemon-IPC-Taktgeber weitergeschaltet und Vorschauframes nur einmal vorab skaliert; Levita-Fachmodul bleibt 1.3 |
| 02.09.26 | Levita LCD-Datenoberfläche | 1.4 | Rechte Außenkante der sichtbaren Video-/Bildfläche am schwarzen Balken mit getrennt einstellbarem oberen und unteren Radius versehen; gekoppelte Bedienung bleibt Standard, Vorschau und Hardwaremaske verwenden dieselbe reine Geometrie |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.30 | Eingebettete Radiusregler mit 48-px-Standard, 0–240-px-Bereich und optional getrennter oberer/unterer Einstellung ergänzt; rote Fotomarkierung ist kein UI- oder Renderbestandteil |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.31 | „Design anpassen“-Felder und Auswahlfenster lesbar vergrößert: eigene Zeile für den schwarzen Balken, Mindestmaße für Zahlen- und Auswahllisten, Panel darf nicht unter seine natürliche Höhe schrumpfen |
| 02.09.26 | Gemeinsame Infrastruktur | 1.0 legacy | Fensterdiagnose löst das Log-Widget vor Qt-aboutToQuit; gelöschte Log-Widgets erzeugen beim Beenden keinen Shiboken-RuntimeError mehr |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.32 | „Design anpassen“ rechts neben die Live-Vorschau gelegt; Hintergrund- und Datenkarten füllen 4–8 Spalten über die volle Galeriebreite |
| 02.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.32 | Helles Design: Navigationsleiste hell, Menütext und Auswahl dunkel, keine weiße Highlight-Schrift auf blassem Akzent |
| 03.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.33 | Ebene-1/2-Galerien nebeneinander; eigener Ordner mit direkter Ebenenzuweisung; Favoritenfilter; zwei projekt-eigene Weltraum-Layouts; native `trcc.json`-Ordner im sicheren Import; einmalige Migration des Notch auf das physische 80-px-Minimum |
| 03.09.26 | OpenRGB Studio | 1.0 legacy | Ausgewählte Vorlage und je Vorlage angepasste Farben dauerhaft gespeichert; Aurora-Vortex und Galaxie-Komet ergänzt; ENE-DRAM nach direktem Startreclaim dreimal zeitversetzt und begrenzt erneut initialisiert |
| 03.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.33 | Standard-Skalierung und gemeinsame Abstände verkleinert; Softwarelinks in kurzen Komponentenkarten; unterstützte Geräte in Über und Hilfe ergänzt |
| 03.09.26 | Levita LCD-Orchestrierung / gemeinsame Infrastruktur | Legacy 3.4.29.37 | Persistente Intensitätsregler für beide Ebenen, explizite Einheitenmigration, Orbital-Standard 130 %, read-only GPU-Taktgrenzfallkorrektur über Daemon-IPC und getrennte Hardware-Auffälligkeitsansicht ergänzt |
