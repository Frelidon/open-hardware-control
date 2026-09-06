# Open Hardware Control — Modulkarte für Coding-KIs

Diese Datei wird erst gelesen, nachdem `MODULE_REGISTRY.md` das aktuelle Modul und den einzigen gültigen Versionsordner bestimmt hat. Sie ergänzt das Register um aufgabenspezifische Lesepfade. Praktische Erweiterungsschritte stehen in `../ai/AI_DEVELOPMENT_GUIDE.md`.

## Einstieg und Kompatibilitätsgrenze

`kraken_control.py` bleibt vorerst der ausführbare Einstiegspunkt und die Kompatibilitäts-Orchestrierung. Bestehende Namen der bereits ausgelagerten Bausteine werden dort importiert und damit weiterhin bereitgestellt. Neue unabhängige Logik soll jedoch nicht wieder in diese Datei gelegt werden.

Die Zerlegung erfolgt in kleinen, testbaren Schritten. Hardware-Schreiblogik, Besitzverwaltung und Oberfläche dürfen nicht gleichzeitig in einem großen Umbau verschoben werden.

## Bereits getrennte Anwendungsmodule

| Datei | Zuständigkeit | Darf Hardware schreiben? |
|---|---|---:|
| `app_constants.py` | Programmidentität, Version und gemeinsam genutzte sichere Standardwerte | Nein |
| `branding.py` | Projektlogo, Programmsymbol, kompakte Seitenleisten-Marke und eigene 22/32/48/64-Pixel-Rasterstaffelung für das Plasma-System-Tray | Nein |
| `temperature_utils.py` | Temperatur-Einheiten und Umrechnungen | Nein |
| `privacy_logging.py` | Datenschutzfilter, Start- und Absturzprotokolle | Nein |
| `window_diagnostics.py` | Frühe Qt-Fenster-/Helferprozessdiagnose und eng begrenzte Quarantäne des beobachteten elternlosen, namenlosen 640×480-`QFrame` | Nein |
| `command_backend.py` | Serieller `QProcess`-/liquidctl-Auftragsweg | Ja, nur über vorhandene validierte Befehle |
| `cooling_card_state.py` | Reiner Ein-/Ausklappzustand der Gehäuselüfterkarten | Nein |
| `cooling_widgets.py` | Hardwareunabhängiger Kurveneditor und Mini-Vorschau | Nein |
| `localization_catalog.py` | Übersetzungen und integrierte Hilfethemen | Nein |
| `ui_layout.py` | Gespeicherte Navigations- und Layoutmodelle | Nein |
| `dashboard_layout.py` | Dashboard-Raster, Benutzerkartenauswahl und hardwareabhängige Kartenverfügbarkeit | Nein |
| `modules/window_placement/v1_0/placement.py` | Reine Auswahlrichtlinie für Hauptbildschirm oder stabil benannten Startmonitor mit sicherem Rückfall | Nein |
| `modules/lcd_levita/v1_4/layout_model.py` | Reine, fehlertolerant importierte Ebene-2-Blöcke, Koordinaten, Gesamt-Offsets und Override-Persistenz | Nein |
| `modules/lcd_levita/v1_4/layout_canvas.py` | Levita-Canvas, stabiles Drag-and-drop und Anforderung des eingebetteten Seiteneditors | Nein |
| `modules/lcd_levita/v1_4/panel_geometry.py` | Reine Panel- und Notchkontur | Nein |
| `modules/lcd_levita/v1_4/runtime_policy.py` | Reine Validierung persistierter Levita-Laufzeitwerte | Nein |
| `modules/lcd_levita/v1_4/theme_adapter.py` | Read-only TRCC-Layoutimport und zusammenhängendes OHC-Cache-Staging für Video, Maske und Live-Blöcke | Nein |
| `modules/wallpaper_engine/v1_2/library.py` | Begrenzte, schreibgeschützte Erkennung lokaler Steam-Workshop-Projekte und eigener Videos | Nein |
| `modules/wallpaper_engine/v1_2/plasma.py` | Plasma-Konfigurationsleser und validierte Skript-/D-Bus-Befehlserzeugung für Auswahl, DisplayMode und Wiedergabe am registrierten Plasma-Objekt | Nein; schreibt nur nach ausdrücklicher UI-Aktion in Plasma-Einstellungen |
| `modules/wallpaper_engine/v1_2/installer.py` | Fedora-/Architektur-passende Auswahl und SHA256-verifizierter Benutzerdownload eines offiziellen CaptSilver-Release-RPM; erzeugt nur einen festen `pkexec dnf install`-Befehl für den geprüften Cachepfad | Download erst nach UI-Bestätigung; Systemschreibzugriff erst nach zweiter Bestätigung und Polkit-Passwortdialog |
| `modules/wallpaper_engine/v1_2/onboarding.py` | Erststartdialog, dauerhafte Schritt-für-Schritt-Anleitung, Steam-/Workshop-Links, Einrichtungscheckliste und asynchrone Installer-Orchestrierung | Kein Passwortzugriff; delegiert ausschließlich den geprüften festen Befehl an Polkit/DNF |
| `modules/wallpaper_engine/v1_2/page.py` | Wallpaper-/Video-Galerie mit stabilen Apply-Refresh-Kartenmaßen, Bildschirmziel, Wiedergabesteuerung, Skalierungswahl und Start der originalen Plasma-Oberfläche | Nein; delegiert Einstellungen ausschließlich an `plasma.py` |
| `thermalright_display.py` | Levita-Geometrie, strikte 1600×720-Layoutfilterung, nicht destruktive Katalog-Deduplikation nach vollständigem Dateinamen, lokaler Medien-/TRCC-Import, reale Helligkeits-/Ausrichtungsbefehle und Renderdaten | Nein |
| `hardware_diagnostics.py` | Reine read-only Plausibilitätsprüfung für Hardwarewerte und AMD-GPU-Takt-Normalisierung | Nein |
| `log_view_support.py` | Gemeinsame Aktionen, Begrenzung und Hardware-Kategorisierung der Log-Ansichten | Nein |
| `thermalright_display_ui.py` | Bestehende Karten-/Medien-/Prozess-Orchestrierung und Verdrahtung des versionierten Ebene-2-Moduls | Nur nach ausgeschaltetem Testmodus |
| `thermalright_cooling.py` | Read-only USB-Erkennung, PWM-Rollenvorschläge und sichere Profilwerte | Nein |
| `kraken_control.py` | PySide6-Hauptfenster, Seitenaufbau und noch nicht ausgelagerte Orchestrierung | Teilweise; bestehende Grenzen bewahren |

## Wichtige Abhängigkeiten

Die neuen Basismodule importieren `kraken_control.py` niemals zurück. Dadurch bleibt der Importgraph kreisfrei:

```text
privacy_logging ──> app_constants
command_backend ──> app_constants + privacy_logging
layout_canvas ──> layout_model + thermalright_display
theme_adapter ──> layout_model + optionaler TRCC-Decoder
wallpaper_engine/page ──> wallpaper_engine/library + wallpaper_engine/plasma
kraken_control ──> window_placement/placement
cooling_widgets ──> temperature_utils
cooling_card_state       (keine Projektabhängigkeit)
localization_catalog    (keine Projektabhängigkeit)
kraken_control ──> alle oben genannten Module
```

## Dateien nach Aufgabenart laden

### Oberfläche, Design oder Navigation

Zuerst lesen:

- `kraken_control.py`: nur die mit `rg` gefundenen `make_*_tab`, Theme- oder Navigationsmethoden;
- `cooling_widgets.py` bei Lüfterkurven;
- `ui_layout.py` bei Reihenfolge und Sichtbarkeit;
- `localization_catalog.py` nur bei sichtbaren Texten oder Hilfe;
- die zum Verhalten gehörenden UI-Tests.

Für Wallpaper Engine zusätzlich nur `modules/wallpaper_engine/v1_2/README.md`, `library.py`, `plasma.py`, `installer.py`, `onboarding.py`, `page.py` und `tests/test_wallpaper_engine_342942.py` lesen. Das installierte CaptSilver-QML bleibt eine externe Oberfläche und wird weder kopiert noch im QWidget-Baum eingebettet.

### Kraken-Kühlung oder LCD

Zuerst lesen:

- die betroffenen Methoden in `kraken_control.py`;
- `command_backend.py`, `hardware_request_coordinator.py` und `cooling_ownership.py`;
- je nach Aufgabe `nzxt_backend.py`, `kraken_sensors.py`, `kraken_cam_streamer.py`, `kraken_lcd_designs.py` oder `nzxt_esc_profiles.py`;
- die passenden Tests.

Keine USB-Kommandos, Produkt-IDs oder Hardwarebestätigungen erraten.

### Mainboard- und Gehäuselüfter

Zuerst lesen:

- die betroffenen Cooling-/Mainboard-Methoden in `kraken_control.py`;
- `mainboard_fan_control.py`, `ohc_fan_helper.py`, `cooling_ownership.py`;
- `../hardware/DEVICE_SUPPORT.md`, `../hardware/SUPPORTED_DEVICES.md` und passende Tests.

CPU_FAN, PUMP_FAN, Kraken und CoolerControl dürfen keine konkurrierenden Besitzer erhalten.

### Thermalright Levita

Zuerst lesen:

- den in `MODULE_REGISTRY.md` genannten aktuellen Levita-Ordner und dessen `README.md`;
- `layout_model.py` bei Blöcken/Persistenz, `layout_canvas.py` bei Drag/Kontextmenü und `theme_adapter.py` bei TRCC-Import/Cache;
- nur die gezielt betroffenen Abschnitte von `thermalright_display.py` und `thermalright_display_ui.py` für Import, Vorschau, Notch und Orchestrierung;
- `thermalright_cooling.py` sowie die gezielt gefundenen Levita-Methoden in `kraken_control.py` für Pumpe/Radiator;
- `mainboard_fan_control.py` und `cooling_ownership.py` für Schreibsicherheit;
- `tests/test_thermalright_*.py`, `../hardware/DEVICE_SUPPORT.md` und `../hardware/SUPPORTED_DEVICES.md`.

USB-Display und PWM-Kühlung sind getrennte Transportwege. Niemals aus der USB-ID einen unbestätigten PWM-Schreibzugriff oder einen Kühlmittelwert ableiten.

`config1.dc` niemals schreiben. Änderungen an Datenblöcken werden als OHC-Override gespeichert und für die Laufzeit in einem generierten Cache-`trcc.json` dargestellt.

### RGB Studio

Zuerst lesen:

- die betroffenen RGB-Methoden in `kraken_control.py`;
- `openrgb_integration.py`, `openrgb_sdk.py`, `rgb_devices.py`, `rgb_effects.py`;
- bei NZXT-Zonen zusätzlich `nzxt_rgb.py`;
- RGB-Ownership- und Sicherheitstests.

### Corsair / OpenLinkHub

Zuerst lesen:

- die betroffenen OpenLinkHub-Methoden in `kraken_control.py`;
- `openlinkhub_integration.py`, bei Mausdarstellung `openlinkhub_mouse_visuals.py`;
- die zugehörigen Tests und `../hardware/DEVICE_SUPPORT.md`.

Corsair bleibt über die validierte lokale OpenLinkHub-API angebunden; keine direkten USB-Schreibwege ergänzen.

### Release, RPM/DEB oder GitHub

Zuerst lesen:

- `BUILD_CHANNEL`, `VERSION`, `AGENTS.md`;
- `scripts/check_release.sh`, `scripts/build_release.py` und die Veröffentlichungsanleitung;
- aktuelle Release Notes und `CHANGELOG.md`.

GitHub-Aktionen benötigen weiterhin eine ausdrückliche aktuelle Freigabe.

## Nächste sinnvolle Zerlegungsschritte

1. Levita-Katalog und Thumbnail-Warteschlange aus `thermalright_display_ui.py` in ein kleines Untermodul auslagern.
2. Theme- und Stylesheet-Erzeugung ohne Verhaltensänderung auslagern.
3. Große Seitenbauer wie LCD, RGB Studio und Kühlung einzeln in klar benannte UI-Module oder Mixins verschieben.
4. Profil- und Einstellungs-Persistenz hinter kleinen, typisierten Schnittstellen bündeln.
5. LCD- und RGB-Orchestrierung erst danach jeweils separat vom Fenster lösen.

Jeder Schritt muss vorhandene öffentliche Namen und Einstellungs-Schlüssel erhalten, enge Regressionstests ergänzen, das Modulregister ohne Ausnahme aktualisieren und vor dem nächsten großen Schnitt vollständig grün sein.
