# Open Hardware Control — Modulkarte für Coding-KIs

## .178 Profile und Programm-Hintergründe

`profiles_workspace/v1_0/`: Bibliothek/Karten, reine Filter/Zusammenfassung und
aufklappbare Editor-/Detail-/Transferpanels. Legacy-CRUD bleibt ID-basiert.
`app_backgrounds/v1_0/`: feste Medien, ein Decoder und separater angewendeter
Profilzustand. Keine Vorschau schreibt Hardware oder globale Einstellungen.
`tools/render_app_backgrounds.py` / `render_code_rain.py`: eigene periodische
Videos, Matrix-Zeichengrößen; bestehende Dateien unverändert.

## .95 Display preview paths

`lcd_levita/v1_7/media_preview.py`: selected-video driver, pending/confirmed
composition, firmware release. `lcd_media_manager/v1_0/preview_visibility.py`
and `video_preview.py`: shared exposed-viewport/local decoding without hardware.
`display_effects/v1_11/page.py` / `library.py`: transient exploration, clear/live
fallback, stable data IDs and current translated details. `light_bands_renderer.py`
and `tools/render_light_bands.py`: original actual 4800×2160 source/native loops.
`ui_performance/v1_1/gallery_preparation.py`: reserved row geometry in bounded
insertion. `lcd_levita/v1_7/layout_canvas.py`: unchanged-layer scene reuse.


.94: `pc_case_profiles/v1_5/editor_sections.py` owns live-widget column/tab
reflow for component/fan and inline LED-path forms. The inspector grows left
within 430–860 px, has no inner scroll area and retains domain footer/guards.
`ui_performance/v1_1/dynamic_text.py` refreshes late tab titles.
`rgb_studio/v1_15/gpu_strip_sampling.py` widens quintic moving-strip fades and
uses the shared virtual pair sampling footprint at actual independent counts;
no new clock, LED resize or hardware transport.


## .93 – Default authority and recovery

`lcd_runtime/v1_1/design_state.py`: explicit default precedence, retry generation
and immutable accepted command intent. `memory_guard.py`: pure RSS/growth/pressure
classification. Thin hooks in Levita/profile orchestration; effect previews no
longer stage profile media. Cache identity fix stays in `lcd_levita/v1_7/theme_adapter.py`.
Regression: `tests/test_lcd_design_authority_342993.py` and existing layout/full UI.

## .92 – Module supervision and continuous LCD

`process_runtime/v1_1/diagnostics.py`: private module journal and error evidence.
`restart_policy.py`/`sdk_supervisor.py`: bounded progress-dependent SDK recovery;
`controller.py`: read-only sensor recovery and stderr capture. `health.py`: actual
transfer age and explicit sensor restart. `lcd_runtime/v1_1/progress.py` parses
TRCC CLI acknowledgements; `controller.py` owns watchdogs; `game_probe.py` and
`game_activity.py` own isolated/coalesced read-only detection. Regression file:
`tests/test_module_supervision_342992.py`. No new USB/PWM writer.


Diese Datei wird erst gelesen, nachdem `MODULE_REGISTRY.md` das aktuelle Modul und den einzigen gültigen Versionsordner bestimmt hat. Sie ergänzt das Register um aufgabenspezifische Lesepfade. Praktische Erweiterungsschritte stehen in `docs/ai/AI_DEVELOPMENT_GUIDE.md`.

## Einstieg und Kompatibilitätsgrenze

.91: `process_runtime/v1_1/` besitzt read-only Sensor-IPC, Frische, begrenzten
Supervisor und Ressourcen-/Statusanzeige. `rgb_studio/v1_15/render_plan.py` teilt
Planbau und Worker-Berechnung. `application_shutdown/v1_1/` besitzt private
Phasen/Stack-Diagnose, den begrenzten Elternbeobachter und eigene Qt-Restprozesse.
`pc_case_profiles/v1_5/diagram.py` teilt Beschriftungs- und Treffergeometrie;
`case_animation.py` projiziert GPU-/Halterungs-/RAM-Farben rein lesend in die
nur sichtbar laufende Zeichnung.

`.152`: `cooling_state/v1_0/cpu_defaults.py` besitzt die reine Entscheidung
zwischen erkannten CPU-Standardkurven und nutzereigenen Änderungen.
`navigation_settings/v1_0/` besitzt die explizite Modul-Sichtbarkeitsseite.
`pc_case_profiles/v1_5/controller.py` synchronisiert die einstellungsbasierte
CPU_FAN-/PUMP_FAN-/SYS_FAN-Topologie ins aktive lokale PC-Profil; keine dieser
Operationen aktiviert oder beschreibt Hardware.

`src/kraken_control.py` bleibt vorerst der ausführbare Einstiegspunkt und die Kompatibilitäts-Orchestrierung. Bestehende Namen der bereits ausgelagerten Bausteine werden dort importiert und damit weiterhin bereitgestellt. Neue unabhängige Logik soll jedoch nicht wieder in diese Datei gelegt werden.

Die Zerlegung erfolgt in kleinen, testbaren Schritten. Hardware-Schreiblogik, Besitzverwaltung und Oberfläche dürfen nicht gleichzeitig in einem großen Umbau verschoben werden.

## Komplettpakete und LED-Verlauf

`.90`: `ui_performance/v1_1/gallery_preparation.py` portions/idle/reuse,
`dynamic_text.py` late/live canonical text, `controller.py` navigation overlays.
`pc_case_profiles/v1_5/inline_editor.py` owns the single right-side inspector,
`component_editor.py` property form/commit. ARGB/GPU/PWM delegates keep their
existing safety boundaries. `cooling_state/v1_0/controller.py` requested versus
actual master state and fresh-owner actions. `rgb_studio/v1_15/stream_reclaim.py`
validated selected RAM IDs/lease/drain; retry mixin retains other effect clocks.
Regression files end in `342990`; existing four-language UI and full gate remain.

`rgb_studio/v1_15/gpu_strip_sampling.py`: Qt-freie weiche offene GPU-Streifen;
`gpu_support_sync.py`: begrenzte Auflösung ausdrücklich zugeordneter GPU- und
Halterungszonen, gemeinsame Zeit/Effekt ohne neue Geräteauswahl. Integration
in `gpu_routing.py`/`gpu_lighting.py`, Diagnose in `argb_diagnostics.py`;
Kontrolltests `tests/test_gpu_strip_smoothing_342989.py`.

`profile_bundle/v1_0/`: `values.py` für verlustfreie Einstellungstypen und
Pfadumsetzung, `archive.py` für begrenzte ZIP-/Prüfsummenoperationen,
`controller.py`/`worker.py` für Oberfläche/eigenen Datei-Hintergrundprozess,
`restore.py` für bestätigte Wiederherstellung beim Start mit Rückfallkopie,
`legacy_profiles.py` für bestehenden JSON-Austausch. Keine Hardwarebefehle.

`rgb_studio/v1_15/`: `led_topology.py` für reine Streifen-/Ringkoordinaten
und räumliche Abtastung, `led_topology_store.py` für unabhängige Zuordnungen
und vorhandene Gehäusepositionen, `led_topology_editor.py` für Vorschau und
Start-/End-/Drehsinnwahl. Der bestehende Anschlusseditor übernimmt Anzahl,
Test und Grenzen; Direct-Ausgabe bleibt im vorhandenen einzigen Schreibpfad.

## Bereits getrennte Anwendungsmodule

RGB Studio 1.13 enthält `personal_wiring.py` für einmalige bestätigte persönliche
Zuordnungen und `fan_library.py` für begrenzte, wiederverwendbare eigene
Hersteller-/Modell-/Farb-/LED-Deklarationen. Die bisherigen Module
`engine_recovery.py` für ausdrückliche Eigenprozess-
Wiederherstellung, `header_preview.py` für Erkennungs-/Auto-Apply-Pause und
kontrollierte Designrückgabe sowie `fan_profiles.py`/`fan_profile_editor.py`
für begrenzte persönliche Marke/Modell/Farbe/LED-Deklarationen bleiben erhalten. Hardware-
Schreibbesitz und SDK-Grenzen bleiben bei den bisherigen Transportwegen.

| Datei | Zuständigkeit | Darf Hardware schreiben? |
|---|---|---:|
| `src/app_constants.py` | Programmidentität, Version und gemeinsam genutzte sichere Standardwerte | Nein |
| `src/branding.py` | Projektlogo, Programmsymbol, kompakte Seitenleisten-Marke und eigene 22/32/48/64-Pixel-Rasterstaffelung für das Plasma-System-Tray | Nein |
| `src/temperature_utils.py` | Temperatur-Einheiten und Umrechnungen | Nein |
| `src/privacy_logging.py` | Datenschutzfilter, Start- und Absturzprotokolle | Nein |
| `src/window_diagnostics.py` | Frühe Qt-Fenster-/Helferprozessdiagnose und eng begrenzte Quarantäne des beobachteten elternlosen, namenlosen 640×480-`QFrame` | Nein |
| `src/command_backend.py` | Serieller `QProcess`-/liquidctl-Auftragsweg | Ja, nur über vorhandene validierte Befehle |
| `src/cooling_card_state.py` | Reiner Ein-/Ausklappzustand der Gehäuselüfterkarten | Nein |
| `src/cooling_widgets.py` | Hardwareunabhängiger Kurveneditor und Mini-Vorschau | Nein |
| `src/modules/localization/v1_0/` | Vollständige Sprachdaten in je einer Datei für Deutsch, Englisch, Spanisch und Französisch; Katalogprüfung und dynamische Beschriftungen | Nein |
| `src/localization_catalog.py` | Dünne Kompatibilitätsschnittstelle zum versionierten Sprachmodul | Nein |
| `src/modules/application_activation/v1_0/server.py` | Private lokale Aktivierungsnachricht für das bereits laufende Fenster und ausschließlich autostartspezifische Desktop-Token-Richtlinie | Nein |
| `src/modules/application_shutdown/v1_1/` | EOF-first Beenden des eigenen Pipe-Helfers, getrennt protokollierte Abschaltphasen und Stilllegen eigener Timer/Neustartabsichten | Keine neuen Hardwarebefehle; vorhandene Rückgabe bleibt beim Orchestrator |
| `src/modules/window_chrome/v1_2/chrome.py` | Eigene Hauptfensterleiste, compositor-delegierte Systembewegung/-größenänderung, sichere Randcursor-Freigabe und bis in die Ecke reichende Schließfläche | Nein |
| `src/modules/ui_performance/v1_1/` | Globale leichte Seitenübergänge sowie begrenzter gemeinsamer Cache für regenerierbare Kataloge und Vorschaubilder | Nur im eigenen Benutzer-Cache; keine Originalmedien |
| `src/modules/mainboard_driver_setup/v1_1/` | Read-only Secure-Boot-/MOK-/Distributions-/Boardstatus, getrennte Ubuntu-/Fedora-/Arch-Abhängigkeitsbefehle und geführte, bestätigte NCT6687-DKMS-/MOK-Terminalschritte | Unbekannte Distributionen und nicht passende MSI-Boards fallen geschlossen aus; kein Passwort, Neustart oder Secure-Boot-Umbau |
| `src/modules/ui_themes/v1_0/` | Getrennte helle/dunkle Palette, semantische Oberflächenwerte, Theme-Registry und gemeinsamer Qt-Stilcontroller | Nein |
| `src/modules/hardware_backends/v1_0/` | Reine, fail-closed Auswahl- und Auflösungsrichtlinie für vorhandene Hardware-Unterbauten | Nein |
| `src/modules/temperature_history/v1_2/` | Begrenzter RAM-Sitzungspuffer, datierter interaktiver Qt-Canvas, skalierbare Splitter, rein lesende gruppierte Linux-hwmon-Sensorerkennung und ausdrücklicher CSV-/JSON-Berichtsexport | Nur die vom Nutzer gewählte Berichtsdatei |
| `src/modules/responsive_gallery/v1_0/` | Breitenabhängige Spaltenzahl, Viewport-Resize-Bündelung und gleichmäßige Kachelverteilung | Nein |
| `src/modules/lcd_media_manager/v1_0/` | Mehrere lokale Designordner/Einzelmedien einschließlich GIF, Anzeigenamen und nicht-destruktive Ausblendungen für Levita und Kraken | Nur QSettings; Quelldateien unverändert |
| `src/modules/cooling_safety/v1_0/` | Modellbezogene PWM-Untergrenzen und fail-closed Begrenzung vor Kühlungswrites | Nein |
| `src/modules/pc_case_profiles/v1_5/` | Zentrale Gehäuse-Seite, 30 originale detaillierte Zeichnungen, gemeinsame RGB/LED/PWM-Zuordnung und optionale eigene Kühlungspositionen | Nein; PWM-Zuordnung delegiert nur vorhandenes chassis-only Mapping ohne Aktivierung/Kalibrierung |
| `src/modules/rgb_studio/v1_15/` | Galerie, direkte Block-/ARGB-Auswahl und stabile physische Bindungen, native/zonengenaue GPU-Routen, Direct-Anschlusseditoren, manuelle Profilpins, Anschlussdiagnose und Qt-freie zählabhängige Effektabtastung | Nein; bestehender Hosttransport/SDK-Worker bleibt einziger Schreibpfad |
| `src/modules/display_effects/v1_11/model.py` | Begrenztes, persistierbares Einstellungsmodell für Display-Effekte | Nein |
| `src/modules/display_effects/v1_11/catalog.py` | Validierter, filterbarer Offline-Katalog mit Urheber, Quelle, Lizenz, Farbvarianten und menschenfreien Natur-/Weltraumclips | Nein |
| `src/modules/display_effects/v1_11/handoff.py` | Gemeinsame strikte Root-, Symlink- und MP4-Prüfung für Effektmedien vor der Übergabe | Nein |
| `src/modules/display_effects/v1_11/library.py` | Responsive grafische Ebene-1-Vorschaukacheln, vier Hauptkategorien, Variantenwahl, aktive Pfadsynchronisierung und anklickbare Attribution | Nein |
| `src/modules/display_effects/v1_11/smoke_renderer.py` | Deterministisches prozedurales Rauch-Rendering für Vorschau und Export | Nein |
| `src/modules/display_effects/v1_11/light_bands_renderer.py`, `tools/render_light_bands.py` | Originale deterministische Lichtstäbe mit nahtloser Wanderwelle; 3200×1440-Übersampling für schärfere native 1600×720-Medien in acht Richtungen | Nein; keine Referenzframes, Logos oder Herstellergeometrie |
| `src/modules/lcd_levita/v1_7/motion_renderer.py`, `tools/render_levita_motion.py` | Vier originale deterministische Glow-/Partikelanimationen für Ebene 2 | Nein; vollständig eigene Geometrie und Farben |
| `src/modules/lcd_levita/v1_7/motion_compositor.py` | Lokale validierte Ein-Strom-Komposition aus Ebene 1 und animiertem Dekor | Nein; ffmpeg-Cache, kein USB-Zugriff |
| `src/modules/display_settings/v1_0/` | Qt-Aufbau für Bildschirm-, Fensterstart- und experimentelle Levita-FPS-Einstellungen | Nein; keine Persistenz und kein Hardwarezugriff |
| `src/modules/levita_performance/v1_1/policy.py` | Sichere/experimentelle FPS, Rückstufung, Zehn-Sekunden-Abfrage sowie GameMode/Gamescope/Programmlisten-Signale | Nein |
| `src/modules/display_effects/v1_11/worker.py` | Begrenzter, schneller kodierter Offscreen-H.264-Export in den privaten OHC-Cache | Nein |
| `src/modules/display_effects/v1_11/base_page.py` | Effektseite mit responsiven Ebene-1- und Ebene-2-Vorschaukarten, aktiver Auswahlspiegelung, unabhängiger Dekoranimation und ausdrücklicher Thermalright-Firmware-Rückgabe | Nein; keine automatische Kopplung oder Hardwareübertragung bei Auswahl |
| `src/modules/display_effects/v1_11/page.py`, `video_preview.py` | Sichtbarkeitsgebundene animierte Vorschau genau eines validierten lokalen MP4; Dark Smoke beginnt bei sichtbarer Bewegung | Nein; Qt Multimedia liest nur, Pause/Seitenwechsel/Minimieren/Ende stoppen den Decoder |
| `src/modules/section_tabs/v1_0/tabs.py` | Synchronisiert beliebig viele Unterreiter eines Bereichs über stabile Hauptseiten-IDs | Nein; ausschließlich Navigation und Übersetzung |
| `tools/render_levita_overlays.py` | Reproduzierbares selektives Rendering der acht originalen und fünf aus dokumentierten Kenney-CC0-Komponenten abgeleiteten 1600×720-Layer-2-Themes sowie der Nebula-Glass-Cards; OHC-Layouts enthalten konsistente Schriften und kompakte Uhrrahmen | Nein |
| `src/modules/responsive_startup/v1_0/probe.py` | Zusammengefasster begrenzter Qt-Hintergrundprozess für den Besitzerstatus | Nein |
| `src/modules/responsive_startup/v1_0/ownership_probe.py` | Prozessgetrennte read-only `systemctl`-/`pgrep`-Prüfung | Nein |
| `src/modules/responsive_startup/v1_0/controller.py` | Fail-closed Statusübernahme und bestätigte CoolerControl-Besitzaktionen | Nur die bestehenden bestätigten Polkit-Dienstaktionen; keine PWM-Werte |
| `src/ui_layout.py` | Gespeicherte Navigations- und Layoutmodelle | Nein |
| `src/dashboard_layout.py` | Dashboard-Raster, Benutzerkartenauswahl, hardwareabhängige Kartenverfügbarkeit und reine Übersichtshinweise für Status & Hinweise | Nein |
| `src/modules/window_placement/v1_5/` | Auswahl-, Geometrie- und Startzustandsrichtlinie sowie KWin-bestätigter Wayland-Ausgang über begrenzten PID-/Titel-Rückkanal | Nur OHC-Hauptfenster; keine KWin-Dauerregel |
| `src/modules/lcd_levita/v1_7/layout_model.py` | Reine, fehlertolerant importierte Ebene-2-Blöcke, Koordinaten, Gesamt-Offsets und Override-Persistenz | Nein |
| `src/modules/lcd_levita/v1_7/layout_canvas.py` | Levita-Canvas, stabiles Drag-and-drop und Anforderung des eingebetteten Seiteneditors | Nein |
| `src/modules/lcd_levita/v1_7/panel_geometry.py` | Reine Panel- und Notchkontur | Nein |
| `src/modules/lcd_levita/v1_7/runtime_policy.py` | Reine Validierung persistierter Levita-Laufzeitwerte | Nein |
| `src/modules/lcd_levita/v1_7/stream_recovery.py` | Reine begrenzte Wiederanlauf-/Rückstau-Richtlinie für den daemonseitigen Video-Taktgeber | Nein |
| `src/modules/lcd_levita_shutdown/v1_0/guard.py` | Begrenzte Levita-Firmware-Rückgabe über den vorhandenen TRCC-Daemon und prozessgetrennter Pipe-Wächter nach bestätigtem echtem Schreibzugriff | Nur nach echtem Schreibzugriff oder beim kontrollierten Ende außerhalb des Testmodus |
| `src/modules/lcd_levita/v1_7/theme_adapter.py` | Read-only TRCC-Layoutimport und zusammenhängendes OHC-Cache-Staging für Video, Maske und Live-Blöcke | Nein |
| `src/modules/wallpaper_engine/v1_3/library.py` | Begrenzte, schreibgeschützte Erkennung lokaler Steam-Workshop-Projekte und eigener Videos mit gemeinsamem Metadaten-Cache | Nur regenerierbare Cachemetadaten; Steam bleibt unverändert |
| `src/modules/wallpaper_engine/v1_3/plasma.py` | Plasma-Konfigurationsleser und validierte Skript-/D-Bus-Befehlserzeugung für Auswahl, DisplayMode und Wiedergabe am registrierten Plasma-Objekt | Nein; schreibt nur nach ausdrücklicher UI-Aktion in Plasma-Einstellungen |
| `src/modules/wallpaper_engine/v1_3/installer.py` | Fedora-/Architektur-passende Auswahl und SHA256-verifizierter Benutzerdownload eines offiziellen CaptSilver-Release-RPM; erzeugt nur einen festen `pkexec dnf install`-Befehl für den geprüften Cachepfad | Download erst nach UI-Bestätigung; Systemschreibzugriff erst nach zweiter Bestätigung und Polkit-Passwortdialog |
| `src/modules/wallpaper_engine/v1_3/onboarding.py` | Lokalisierter Erststartdialog, Steam-/Workshop-Schritte, bestätigte KDE-Hilfspakete und asynchrone Plugin-Installer-Orchestrierung | Kein Passwortzugriff; Pakete nur aus eingerichteten Quellen, Plugin nur über geprüften festen Polkit/DNF-Befehl |
| `src/modules/wallpaper_engine/v1_3/page.py` | Wallpaper-/Video-Galerie mit stabilen Kartenmaßen, persistenten skalierten Vorschaubildern, Bildschirmziel, Wiedergabe und Skalierung | Nur regenerierbarer Vorschaubildcache; Plasma-Einstellungen ausschließlich über `plasma.py` |
| `src/modules/openlinkhub_update/v1_0/policy.py` | Fester offizieller Release-Check, Paketplan sowie SHA-256-geprüftes und sicher entpacktes User-Space-Staging | Nur unprivilegierter Download nach Bestätigung |
| `src/modules/openlinkhub_update/v1_0/controller.py` | OpenLinkHub-Seite und asynchroner Bestätigungs-/Updateablauf | Delegiert ausschließlich die validierten Updatepläne |
| `src/modules/openlinkhub_update/v1_0/apply_user_space.py` | Atomarer Austausch der streng erkannten Benutzerinstallation mit Datenübernahme, Backup und Rollback | Ja, nur im Benutzerverzeichnis nach Bestätigung |
| `src/modules/openlinkhub_nexus/v1_0/` | Validierter 640×48-Hintergrund-/Touch-Manifestimport mit `nexus.json`-Backup und atomarem Austausch | Ja, nur erkannte OpenLinkHub-Benutzerinstallation; kein USB-Zugriff |
| `src/modules/hardware_fix/v1_0/` | Eng begrenzte Hardware-Fix-Profile; zunächst MSI MAG 274QPF X30MV – VRR mit anonymisierter EDID, Status, gesperrten Festaktionen und Rücknahme | Nur nach Bestätigung im Terminal; kein beliebiges Root-Skript, kein automatischer Neustart |
| `src/thermalright_display.py` | Levita-Geometrie, strikte 1600×720-Layoutfilterung, nicht destruktive Katalog-Deduplikation nach vollständigem Dateinamen, lokaler Medien-/TRCC-Import, reale Helligkeits-/Ausrichtungsbefehle und Renderdaten | Nein |
| `src/hardware_diagnostics.py` | Reine read-only Plausibilitätsprüfung für Hardwarewerte und AMD-GPU-Takt-Normalisierung | Nein |
| `src/log_view_support.py` | Gemeinsame Aktionen, Begrenzung und Hardware-Kategorisierung der Log-Ansichten | Nein |
| `src/thermalright_display_ui.py` | Bestehende Karten-/Medien-/Prozess-Orchestrierung und Verdrahtung des versionierten Ebene-2-Moduls | Nur nach ausgeschaltetem Testmodus |
| `src/thermalright_cooling.py` | Read-only USB-Erkennung, PWM-Rollenvorschläge und sichere Profilwerte | Nein |
| `src/kraken_control.py` | PySide6-Hauptfenster, Seitenaufbau und noch nicht ausgelagerte Orchestrierung | Teilweise; bestehende Grenzen bewahren |

## Wichtige Abhängigkeiten

Die neuen Basismodule importieren `src/kraken_control.py` niemals zurück. Dadurch bleibt der Importgraph kreisfrei:

```text
privacy_logging ──> app_constants
command_backend ──> app_constants + privacy_logging
layout_canvas ──> layout_model + thermalright_display
thermalright_display_ui ──> lcd_levita_shutdown/v1_0/guard
display_effects/page ──> display_effects/model + smoke_renderer + bestehendes thermalright_display_ui
responsive_startup/controller ──> responsive_startup/probe + cooling_ownership
theme_adapter ──> layout_model + optionaler TRCC-Decoder
wallpaper_engine/page ──> wallpaper_engine/library + wallpaper_engine/plasma
ui_performance/controller ──> ui_performance/cache + maintenance
kraken_control ──> window_placement/placement
kraken_control ──> application_activation/server + openlinkhub_update/policy
kraken_control ──> window_chrome/chrome + pc_case_profiles/catalog
kraken_control ──> hardware_backends/policy + temperature_history/model/chart
cooling_widgets ──> temperature_utils
cooling_card_state       (keine Projektabhängigkeit)
localization/v1_0       (keine Projektabhängigkeit)
localization_catalog ──> localization/v1_0
kraken_control ──> alle oben genannten Module
```

## Dateien nach Aufgabenart laden

### Oberfläche, Design oder Navigation

Zuerst lesen:

- `src/kraken_control.py`: nur die mit `rg` gefundenen `make_*_tab`, Theme- oder Navigationsmethoden;
- `src/cooling_widgets.py` bei Lüfterkurven;
- `src/ui_layout.py` bei Reihenfolge und Sichtbarkeit;
- `src/modules/localization/v1_0/de.py`, `en.py`, `es.py` und `fr.py` gemeinsam bei sichtbaren Texten oder Hilfe;
- `src/modules/localization/v1_0/policy.py` nur bei begrenzten dynamischen Beschriftungen;
- die zum Verhalten gehörenden UI-Tests.

Für Wallpaper Engine zusätzlich nur `src/modules/wallpaper_engine/v1_3/README.md`, `library.py`, `plasma.py`, `installer.py`, `onboarding.py`, `page.py` und `tests/test_wallpaper_engine_342942.py` lesen. Das installierte CaptSilver-QML bleibt eine externe Oberfläche und wird weder kopiert noch im QWidget-Baum eingebettet.

### Kraken-Kühlung oder LCD

Zuerst lesen:

- die betroffenen Methoden in `src/kraken_control.py`;
- `src/command_backend.py`, `src/hardware_request_coordinator.py` und `src/cooling_ownership.py`;
- je nach Aufgabe `src/nzxt_backend.py`, `src/kraken_sensors.py`, `src/kraken_cam_streamer.py`, `src/kraken_lcd_designs.py` oder `src/nzxt_esc_profiles.py`;
- die passenden Tests.

Keine USB-Kommandos, Produkt-IDs oder Hardwarebestätigungen erraten.

### Mainboard- und Gehäuselüfter

Zuerst lesen:

- die betroffenen Cooling-/Mainboard-Methoden in `src/kraken_control.py`;
- `src/mainboard_fan_control.py`, `src/ohc_fan_helper.py`, `src/cooling_ownership.py`;
- `docs/hardware/DEVICE_SUPPORT.md`, `docs/hardware/SUPPORTED_DEVICES.md` und passende Tests.

CPU_FAN, PUMP_FAN, Kraken und CoolerControl dürfen keine konkurrierenden Besitzer erhalten.

### Thermalright Levita

Zuerst lesen:

- den in `MODULE_REGISTRY.md` genannten aktuellen Levita-Ordner und dessen `README.md`;
- bei Beenden-/Absturzaufgaben zusätzlich `src/modules/lcd_levita_shutdown/v1_0/README.md` und `guard.py`;
- `layout_model.py` bei Blöcken/Persistenz, `layout_canvas.py` bei Drag/Kontextmenü und `theme_adapter.py` bei TRCC-Import/Cache;
- nur die gezielt betroffenen Abschnitte von `src/thermalright_display.py` und `src/thermalright_display_ui.py` für Import, Vorschau, Notch und Orchestrierung;
- `src/thermalright_cooling.py` sowie die gezielt gefundenen Levita-Methoden in `src/kraken_control.py` für Pumpe/Radiator;
- `src/mainboard_fan_control.py` und `src/cooling_ownership.py` für Schreibsicherheit;
- `tests/test_thermalright_*.py`, `docs/hardware/DEVICE_SUPPORT.md` und `docs/hardware/SUPPORTED_DEVICES.md`.

USB-Display und PWM-Kühlung sind getrennte Transportwege. Niemals aus der USB-ID einen unbestätigten PWM-Schreibzugriff oder einen Kühlmittelwert ableiten.

`config1.dc` niemals schreiben. Änderungen an Datenblöcken werden als OHC-Override gespeichert und für die Laufzeit in einem generierten Cache-`trcc.json` dargestellt.

Für Display-Effekte zusätzlich nur `src/modules/display_effects/v1_11/README.md`, `model.py`, `catalog.py`, `handoff.py`, `library.py`, `smoke_renderer.py`, `light_bands_renderer.py`, `worker.py`, `base_page.py`, `page.py`, `video_preview.py`, `tools/render_light_bands.py` und `tests/test_display_effects_342954.py` lesen. Animationen der Datenoberfläche gehören ausschließlich in `src/modules/lcd_levita/v1_7/`; ein Ebene-1-Effekt darf die Ebene-2-Wahl nicht automatisch ändern.

### RGB Studio

Zuerst lesen:

- die betroffenen RGB-Methoden in `src/kraken_control.py`;
- `src/openrgb_integration.py`, `src/openrgb_sdk.py`, `src/rgb_devices.py`, `src/rgb_effects.py`;
- bei NZXT-Zonen zusätzlich `src/nzxt_rgb.py`;
- RGB-Ownership- und Sicherheitstests.

### Corsair / OpenLinkHub

Zuerst lesen:

- die betroffenen OpenLinkHub-Methoden in `src/kraken_control.py`;
- `src/openlinkhub_integration.py`, bei Mausdarstellung `src/openlinkhub_mouse_visuals.py`;
- bei Updates ausschließlich `src/modules/openlinkhub_update/v1_0/README.md`, `policy.py`, `controller.py`, `apply_user_space.py` und `tests/test_openlinkhub_update_342954.py`;
- die zugehörigen Tests und `docs/hardware/DEVICE_SUPPORT.md`.

Corsair bleibt über die validierte lokale OpenLinkHub-API angebunden; keine direkten USB-Schreibwege ergänzen. Updates benötigen eine Bestätigung und dürfen weder fremde Download-URLs noch per Shell eingelesene Remote-Installer verwenden.

### Release, RPM/DEB oder GitHub

Zuerst lesen:

- `packaging/BUILD_CHANNEL`, `packaging/VERSION`, `docs/ai/AGENTS.md`;
- `scripts/check_release.sh`, `scripts/build_release.py` und die Veröffentlichungsanleitung;
- aktuelle Release Notes und `docs/CHANGELOG.md`.

GitHub-Aktionen benötigen weiterhin eine ausdrückliche aktuelle Freigabe.

## Nächste sinnvolle Zerlegungsschritte

1. Levita-Katalog und Thumbnail-Warteschlange aus `src/thermalright_display_ui.py` in ein kleines Untermodul auslagern.
2. Theme- und Stylesheet-Erzeugung ohne Verhaltensänderung auslagern.
3. Große Seitenbauer wie LCD, RGB Studio und Kühlung einzeln in klar benannte UI-Module oder Mixins verschieben.
4. Profil- und Einstellungs-Persistenz hinter kleinen, typisierten Schnittstellen bündeln.
5. LCD- und RGB-Orchestrierung erst danach jeweils separat vom Fenster lösen.

Jeder Schritt muss vorhandene öffentliche Namen und Einstellungs-Schlüssel erhalten, enge Regressionstests ergänzen, das Modulregister ohne Ausnahme aktualisieren und vor dem nächsten großen Schnitt vollständig grün sein.
