# Entwicklerpaket 3.4.29.43

Das Entwicklerpaket enthält:

- den vollständigen editierbaren Quellbaum von Open Hardware Control 3.4.29.43 STABLE
- alle Python-, Shell-, Test-, Dokumentations- und GitHub-Workflow-Dateien
- den reproduzierbaren Builder für ZIP, DEB, RPM, Quellarchiv und Prüfsummen
- die fünf eigenen OpenLinkHub-Maus-SVGs und ihre Zuordnungslogik
- den verwalteten Loopback-only RGB-Treiberclient, Geräte-/Gruppenlogik, NZXT-Validierung, zehn eigene RGB-Effekte und ihre Tests
- das reversible KDE-Desktop-Design-Modul und zwei eigene GPL-SVG-Hintergründe
- zentrale Projekt- und OpenLinkHub-Dokumentation
- SHA-256-Prüfsummen
- Cursor/AI-Projektgedächtnis, Regeln, Hooks und Slash-Workflows

Das normale `open_hardware_control_…zip` ist bewusst das schlanke Benutzer-/Installationspaket und enthält daher keine Entwicklungsordner `tests/` und `scripts/`. Für KI-Arbeit, vollständige Tests und reproduzierbare Builds ist ausschließlich das separate `Entwicklerpaket …zip`, das Quellarchiv oder der Repository-Ordner vorgesehen. Der Builder bricht ab, falls im Entwicklerpaket Tests, Release-Skripte, Workflows oder Werkzeuge fehlen.

Die Anwendung wird direkt aus `kraken_control.py` gestartet. Der Dateiname bleibt intern erhalten, weil er das vollständige historische NZXT-Modul trägt; der sichtbare Programmname und der installierte Starter lauten `Open Hardware Control` beziehungsweise `open-hardware-control`.

Kompletter Release-Test:

```bash
./scripts/check_release.sh
```

Einzelne Regressionstests:

```bash
python3 tests/test_security_static.py
python3 tests/test_runtime_logic_stub.py
python3 tests/test_gif_streamer_logic.py
python3 tests/test_lcd_designs.py
python3 tests/test_sensors.py
python3 tests/test_live_render_worker.py
python3 -m unittest tests/test_gif_cooling_handoff.py -v
python3 -m unittest tests/test_openlinkhub_integration.py -v
python3 -m unittest tests/test_openlinkhub_mouse_visuals.py -v
python3 tests/test_desktop_designs.py
python3 -m unittest tests/test_openrgb_integration.py -v
python3 -m unittest tests/test_openrgb_sdk.py -v
python3 -m unittest tests/test_rgb_devices.py -v
python3 -m unittest tests/test_nzxt_rgb.py -v
python3 -m unittest tests/test_rgb_effects.py -v
```

Für einen echten GUI-Test werden PySide6 und eine Desktop-Sitzung benötigt. Schreibtests des NZXT-, OpenLinkHub- oder RGB-Moduls dürfen nur an der passenden Testhardware erfolgen. Die Schreibaktionen sind validiert und standardmäßig bis zur Sitzungsbestätigung gesperrt. OHC startet genau eine eigene lokale Engine; eine fremd gestartete OpenRGB-Instanz blockiert Schreibzugriffe.

Der Installer kann für einen isolierten Pakettest mit `OHC_INSTALL_HOME=/absoluter/testpfad ./install.sh` in ein separates Benutzerverzeichnis schreiben. Ohne diese optionale Variable verwendet er unverändert das normale Benutzerverzeichnis.

Alle Release-Artefakte werden mit folgendem Befehl gebaut. Auf Debian/Ubuntu muss zusätzlich das Paket `rpm` für den Fedora-RPM-Build installiert sein:

```bash
./scripts/build_release.sh 3.4.29.43
```

Auf Fedora wird ein nicht installiertes `dpkg-deb` jetzt automatisch erkannt und nur das DEB übersprungen; RPM, ZIPs, Quellarchiv und Prüfsummen werden weiterhin gebaut. Mit folgender Variable kann das DEB auch auf anderen Systemen ausdrücklich übersprungen werden:

```bash
OHC_SKIP_DEB=1 ./scripts/build_release.sh 3.4.29.43
```

Nach erfolgreichem Abschluss legt der Builder automatisch eine vollständige Sicherung im Geschwisterordner `Open Hardware Control Backup` an. `RELEASE_BACKUP_POLICY.md` beschreibt Inhalt, atomaren Aufbau und die Aufbewahrung der zwei neuesten Versionen. Ein übersprungenes DEB wird nicht vorgetäuscht; bei einem Bau mit DEB wird es automatisch mitgesichert.
