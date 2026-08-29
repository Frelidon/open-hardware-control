# Open Hardware Control — Modulkarte für Coding-KIs

Diese Datei wird nach `START_HIER_LOKALE_KI.md` und den dort genannten Pflichtdateien gelesen. Sie hilft besonders lokalen Modellen mit begrenztem Kontext, nur die für eine Aufgabe nötigen Dateien zu laden.

## Einstieg und Kompatibilitätsgrenze

`kraken_control.py` bleibt vorerst der ausführbare Einstiegspunkt und die Kompatibilitäts-Orchestrierung. Bestehende Namen der bereits ausgelagerten Bausteine werden dort importiert und damit weiterhin bereitgestellt. Neue unabhängige Logik soll jedoch nicht wieder in diese Datei gelegt werden.

Die Zerlegung erfolgt in kleinen, testbaren Schritten. Hardware-Schreiblogik, Besitzverwaltung und Oberfläche dürfen nicht gleichzeitig in einem großen Umbau verschoben werden.

## Bereits getrennte Anwendungsmodule

| Datei | Zuständigkeit | Darf Hardware schreiben? |
|---|---|---:|
| `app_constants.py` | Programmidentität, Version und gemeinsam genutzte sichere Standardwerte | Nein |
| `temperature_utils.py` | Temperatur-Einheiten und Umrechnungen | Nein |
| `privacy_logging.py` | Datenschutzfilter, Start- und Absturzprotokolle | Nein |
| `command_backend.py` | Serieller `QProcess`-/liquidctl-Auftragsweg | Ja, nur über vorhandene validierte Befehle |
| `cooling_card_state.py` | Reiner Ein-/Ausklappzustand der Gehäuselüfterkarten | Nein |
| `cooling_widgets.py` | Hardwareunabhängiger Kurveneditor und Mini-Vorschau | Nein |
| `localization_catalog.py` | Übersetzungen und integrierte Hilfethemen | Nein |
| `ui_layout.py` | Gespeicherte Navigations- und Layoutmodelle | Nein |
| `thermalright_display.py` | Levita-Geometrie, lokaler Medien-/TRCC-Import und Renderdaten | Nein |
| `thermalright_display_ui.py` | Levita-Editor, Testmodus und begrenzte optionale TRCC-Aufrufe | Nur nach ausgeschaltetem Testmodus |
| `thermalright_cooling.py` | Read-only USB-Erkennung, PWM-Rollenvorschläge und sichere Profilwerte | Nein |
| `kraken_control.py` | PySide6-Hauptfenster, Seitenaufbau und noch nicht ausgelagerte Orchestrierung | Teilweise; bestehende Grenzen bewahren |

## Wichtige Abhängigkeiten

Die neuen Basismodule importieren `kraken_control.py` niemals zurück. Dadurch bleibt der Importgraph kreisfrei:

```text
privacy_logging ──> app_constants
command_backend ──> app_constants + privacy_logging
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
- `DEVICE_SUPPORT.md`, `SUPPORTED_DEVICES.md` und passende Tests.

CPU_FAN, PUMP_FAN, Kraken und CoolerControl dürfen keine konkurrierenden Besitzer erhalten.

### Thermalright Levita

Zuerst lesen:

- `thermalright_display.py` und `thermalright_display_ui.py` für Import, Vorschau, Notch, Overlays und TRCC;
- `thermalright_cooling.py` sowie die gezielt gefundenen Levita-Methoden in `kraken_control.py` für Pumpe/Radiator;
- `mainboard_fan_control.py` und `cooling_ownership.py` für Schreibsicherheit;
- `tests/test_thermalright_*.py`, `DEVICE_SUPPORT.md` und `SUPPORTED_DEVICES.md`.

USB-Display und PWM-Kühlung sind getrennte Transportwege. Niemals aus der USB-ID einen unbestätigten PWM-Schreibzugriff oder einen Kühlmittelwert ableiten.

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
- die zugehörigen Tests und `DEVICE_SUPPORT.md`.

Corsair bleibt über die validierte lokale OpenLinkHub-API angebunden; keine direkten USB-Schreibwege ergänzen.

### Release, RPM/DEB oder GitHub

Zuerst lesen:

- `BUILD_CHANNEL`, `VERSION`, `AGENTS.md`;
- `scripts/check_release.sh`, `scripts/build_release.py` und die Veröffentlichungsanleitung;
- aktuelle Release Notes und `CHANGELOG.md`.

GitHub-Aktionen benötigen weiterhin eine ausdrückliche aktuelle Freigabe.

## Nächste sinnvolle Zerlegungsschritte

1. Theme- und Stylesheet-Erzeugung ohne Verhaltensänderung auslagern.
2. Große Seitenbauer wie LCD, RGB Studio und Kühlung einzeln in klar benannte UI-Module oder Mixins verschieben.
3. Profil- und Einstellungs-Persistenz hinter kleinen, typisierten Schnittstellen bündeln.
4. LCD- und RGB-Orchestrierung erst danach jeweils separat vom Fenster lösen.

Jeder Schritt muss vorhandene öffentliche Namen und Einstellungs-Schlüssel erhalten, enge Regressionstests ergänzen und vor dem nächsten großen Schnitt vollständig grün sein.
