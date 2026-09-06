# Open Hardware Control — Modulkarte für Coding-KIs

Diese Datei wird erst gelesen, nachdem `MODULE_REGISTRY.md` das aktuelle Modul und den einzigen gültigen Versionsordner bestimmt hat. Sie ergänzt das Register um aufgabenspezifische Lesepfade. Praktische Erweiterungsschritte stehen in `docs/ai/AI_DEVELOPMENT_GUIDE.md`.

## Einstieg und Kompatibilitätsgrenze

`src/kraken_control.py` bleibt vorerst der ausführbare Einstiegspunkt und die Kompatibilitäts-Orchestrierung. Bestehende Namen der bereits ausgelagerten Bausteine werden dort importiert und damit weiterhin bereitgestellt. Neue unabhängige Logik soll jedoch nicht wieder in diese Datei gelegt werden.

Die Zerlegung erfolgt in kleinen, testbaren Schritten. Hardware-Schreiblogik, Besitzverwaltung und Oberfläche dürfen nicht gleichzeitig in einem großen Umbau verschoben werden.

## Bereits getrennte Anwendungsmodule

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
| `src/localization_catalog.py` | Übersetzungen und integrierte Hilfethemen | Nein |
| `src/ui_layout.py` | Gespeicherte Navigations- und Layoutmodelle | Nein |
| `src/dashboard_layout.py` | Dashboard-Raster, Benutzerkartenauswahl und hardwareabhängige Kartenverfügbarkeit | Nein |
| `src/modules/window_placement/v1_0/placement.py` | Reine Auswahlrichtlinie für Hauptbildschirm oder stabil benannten Startmonitor mit sicherem Rückfall | Nein |
| `src/modules/lcd_levita/v1_4/layout_model.py` | Reine, fehlertolerant importierte Ebene-2-Blöcke, Koordinaten, Gesamt-Offsets und Override-Persistenz | Nein |
| `src/modules/lcd_levita/v1_4/layout_canvas.py` | Levita-Canvas, stabiles Drag-and-drop und Anforderung des eingebetteten Seiteneditors | Nein |
| `src/modules/lcd_levita/v1_4/panel_geometry.py` | Reine Panel- und Notchkontur | Nein |
| `src/modules/lcd_levita/v1_4/runtime_policy.py` | Reine Validierung persistierter Levita-Laufzeitwerte | Nein |
| `src/modules/lcd_levita/v1_4/theme_adapter.py` | Read-only TRCC-Layoutimport und zusammenhängendes OHC-Cache-Staging für Video, Maske und Live-Blöcke | Nein |
| `src/modules/wallpaper_engine/v1_2/library.py` | Begrenzte, schreibgeschützte Erkennung lokaler Steam-Workshop-Projekte und eigener Videos | Nein |
| `src/modules/wallpaper_engine/v1_2/plasma.py` | Plasma-Konfigurationsleser und validierte Skript-/D-Bus-Befehlserzeugung für Auswahl, DisplayMode und Wiedergabe am registrierten Plasma-Objekt | Nein; schreibt nur nach ausdrücklicher UI-Aktion in Plasma-Einstellungen |
| `src/modules/wallpaper_engine/v1_2/installer.py` | Fedora-/Architektur-passende Auswahl und SHA256-verifizierter Benutzerdownload eines offiziellen CaptSilver-Release-RPM; erzeugt nur einen festen `pkexec dnf install`-Befehl für den geprüften Cachepfad | Download erst nach UI-Bestätigung; Systemschreibzugriff erst nach zweiter Bestätigung und Polkit-Passwortdialog |
| `src/modules/wallpaper_engine/v1_2/onboarding.py` | Erststartdialog, dauerhafte Schritt-für-Schritt-Anleitung, Steam-/Workshop-Links, Einrichtungscheckliste und asynchrone Installer-Orchestrierung | Kein Passwortzugriff; delegiert ausschließlich den geprüften festen Befehl an Polkit/DNF |
| `src/modules/wallpaper_engine/v1_2/page.py` | Wallpaper-/Video-Galerie mit stabilen Apply-Refresh-Kartenmaßen, Bildschirmziel, Wiedergabesteuerung, Skalierungswahl und Start der originalen Plasma-Oberfläche | Nein; delegiert Einstellungen ausschließlich an `plasma.py` |
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

- `src/kraken_control.py`: nur die mit `rg` gefundenen `make_*_tab`, Theme- oder Navigationsmethoden;
- `src/cooling_widgets.py` bei Lüfterkurven;
- `src/ui_layout.py` bei Reihenfolge und Sichtbarkeit;
- `src/localization_catalog.py` nur bei sichtbaren Texten oder Hilfe;
- die zum Verhalten gehörenden UI-Tests.

Für Wallpaper Engine zusätzlich nur `src/modules/wallpaper_engine/v1_2/README.md`, `library.py`, `plasma.py`, `installer.py`, `onboarding.py`, `page.py` und `tests/test_wallpaper_engine_342942.py` lesen. Das installierte CaptSilver-QML bleibt eine externe Oberfläche und wird weder kopiert noch im QWidget-Baum eingebettet.

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
- `layout_model.py` bei Blöcken/Persistenz, `layout_canvas.py` bei Drag/Kontextmenü und `theme_adapter.py` bei TRCC-Import/Cache;
- nur die gezielt betroffenen Abschnitte von `src/thermalright_display.py` und `src/thermalright_display_ui.py` für Import, Vorschau, Notch und Orchestrierung;
- `src/thermalright_cooling.py` sowie die gezielt gefundenen Levita-Methoden in `src/kraken_control.py` für Pumpe/Radiator;
- `src/mainboard_fan_control.py` und `src/cooling_ownership.py` für Schreibsicherheit;
- `tests/test_thermalright_*.py`, `docs/hardware/DEVICE_SUPPORT.md` und `docs/hardware/SUPPORTED_DEVICES.md`.

USB-Display und PWM-Kühlung sind getrennte Transportwege. Niemals aus der USB-ID einen unbestätigten PWM-Schreibzugriff oder einen Kühlmittelwert ableiten.

`config1.dc` niemals schreiben. Änderungen an Datenblöcken werden als OHC-Override gespeichert und für die Laufzeit in einem generierten Cache-`trcc.json` dargestellt.

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
- die zugehörigen Tests und `docs/hardware/DEVICE_SUPPORT.md`.

Corsair bleibt über die validierte lokale OpenLinkHub-API angebunden; keine direkten USB-Schreibwege ergänzen.

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
