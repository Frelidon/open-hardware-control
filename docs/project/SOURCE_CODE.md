# Quellcode und reproduzierbare Release-Pakete

Jeder weitergegebene Open-Hardware-Control-Stand soll vollständig nachvollziehbar bleiben.

Das Installations-ZIP 3.4.29.47 enthält den direkt editierbaren Python-Quellcode einschließlich `src/desktop_shell.py`, `src/desktop_assets.py` und `src/desktop_designs.py`:

- `src/kraken_control.py`
- `src/openlinkhub_integration.py` (lokale OpenLinkHub-API-, validierte Schreib- und Benutzerdienst-Anbindung)
- `src/openlinkhub_mouse_visuals.py` (Modellfamilien, lizenzfreie Schema-Geometrie und sichere Zuordnung gemeldeter Tastenbelegungen)
- `src/openrgb_integration.py` (Loopback-only OpenRGB-SDK-/CLI-Client, automatisch verwaltete Engine, Geräteparser und serielle Einzelgerätetransaktionen)
- `src/openrgb_sdk.py` (eigener begrenzter SDK-Protokoll-4/5-Paketwriter mit Controller-/Zonensynchronisation und Farb-/Modusrücklesung ohne OpenRGB-CLI-ApplyOptions)
- `src/rgb_devices.py` (stabile Gerätekennungen, ENE-DRAM-Deduplizierung, Gruppen-/Aliasvalidierung, PC-Skizzenprofile und Prozesssperre)
- `src/nzxt_rgb.py` (feste NZXT-Effektfähigkeiten, Argumentvalidierung und topology-sichere Kanalaufteilung)
- `src/rgb_effects.py` (zehn eigene, deterministische und hardwareunabhängige OHC-Effektalgorithmen)
- `src/desktop_designs.py` (KDE-Erkennung, unverändernde Vorschau, Sicherung, bestätigtes Anwenden und Wiederherstellung)
- `src/modules/wallpaper_engine/v1_2/` (schreibgeschützte Workshop-/Video-Bibliothek, Plasma-/D-Bus- und Skalierungsadapter, Erststart-Assistent, SHA256-verifizierter optionaler Fedora-Installer und native OHC-Seite ohne kopierten CaptSilver-Code)
- `src/kraken_lcd_designs.py` (reiner Pillow-Renderer für fünf lokalisierte, skalierbare statische Layouts und nahtlose 20/25-FPS-Hardwareanimationen)
- `src/kraken_sensors.py` (gemeinsame, rein lesende k10temp-/amdgpu-Sensorauswahl für GUI und Streamer)
- `src/kraken_cam_streamer.py` (CAM-naher Firmware-2.x-Raw-LCD-Streamer mit Bewegungsglättung, eindeutiger ACK-Zuordnung, phasenstabiler Reihenfolge und GIF-Loop-Diagnose)
- alle Installations-, Diagnose- und udev-Skripte
- Desktopdatei, selbst erstelltes SVG-Symbol, fünf eigene Maus-SVGs und zwei eigene Desktop-Hintergründe unter `src/assets/`
- vollständige GPL-Lizenz
- deutsche und englische Dokumentation
- zentrale Projektdokumentation `Open_Hardware_Control_Projekt.md`
- OpenLinkHub-Moduldokumentation `docs/hardware/OPENLINKHUB_INTEGRATION.md`
- RGB-Studio- und Sicherheitsaudit-Dokumentation `docs/hardware/RGB_STUDIO.md`, `docs/security/RGB_SECURITY_AUDIT.md`
- historische NZXT-Moduldokumentation `Kraken_Control_Projekt.md`
- technische USB-Mitschnittauswertung `docs/hardware/USB_CAPTURE_FINDINGS.md`
- reproduzierbares Standardbibliothek-Werkzeug `tools/analyze_usbpcap.py`
- statische, Stub-Laufzeit- und OpenLinkHub-Mauszuordnungstests
- selbst erzeugte 240×240-Test-GIFs für 24, 25, 26 und 27 FPS sowie das Generator-Skript
- `MANIFEST.sha256` mit Prüfsummen der Paketdateien

Zu jedem Release werden aus genau demselben Git-Stand erzeugt:

- `open_hardware_control_v3_4_29_43.zip` – universelles Benutzerpaket
- `open-hardware-control_3.4.29.47_all.deb` – Debian/Ubuntu/Linux-Mint-Paket
- `open-hardware-control-3.4.29.47-1.noarch.rpm` – Fedora/Nobara-Paket
- `open-hardware-control-3.4.29.47-source.tar.gz` – vollständiger Quellcode-Snapshot
- `Entwicklerpaket 3.4.29.47.zip` – vollständiger editierbarer Projektbaum einschließlich Tests, Werkzeuge und GitHub-Automatisierung
- `Open_Hardware_Control_3.4.29.47_LOCAL_AI.gitbundle` – vollständige Git-Historie für lokale KI-Arbeit
- `SHA256SUMS` – Prüfsummen aller Release-Dateien

Das universelle Installations-ZIP enthält den ausführbaren Quellcode und die Laufzeitdokumentation, aber absichtlich keine Entwicklungsordner `tests/` oder `scripts/`. Das **Entwicklerpaket** und das Quellarchiv enthalten diese Ordner vollständig. Der Paketbau vergleicht den vollständigen Testbestand des Repositorys mit dem Entwicklerpaket und bricht bei fehlenden Dateien ab.

Die enthaltenen Test-GIFs werden vollständig aus dem mitgelieferten GPL-Quellcode erzeugt und sind keine externen Mediendateien. `scripts/build_release.py` baut alle Pakete reproduzierbar aus dem ausgecheckten Quellbaum.

Nach einem erfolgreichen Bau sichert der Builder alle erzeugten Artefakte zusätzlich im neben dem Repository liegenden Ordner `Open Hardware Control Backup`. Dort bleiben nach `RELEASE_BACKUP_POLICY.md` die zwei neuesten vollständigen Versionssätze mit eigenen SHA256-Prüfsummen erhalten. Das Entwicklerpaket bildet dabei den vollständigen bearbeitbaren Projektstand ab; ein bei einer Veröffentlichung erzeugtes DEB wird ebenso wie das RPM mitgesichert.
