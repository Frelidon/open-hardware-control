# Quellcode und reproduzierbare Release-Pakete

Jeder weitergegebene Open-Hardware-Control-Stand soll vollständig nachvollziehbar bleiben.

Das Installations-ZIP 3.4.29.43 enthält den direkt editierbaren Python-Quellcode einschließlich `desktop_shell.py`, `desktop_assets.py` und `desktop_designs.py`:

- `kraken_control.py`
- `openlinkhub_integration.py` (lokale OpenLinkHub-API-, validierte Schreib- und Benutzerdienst-Anbindung)
- `openlinkhub_mouse_visuals.py` (Modellfamilien, lizenzfreie Schema-Geometrie und sichere Zuordnung gemeldeter Tastenbelegungen)
- `openrgb_integration.py` (Loopback-only OpenRGB-SDK-/CLI-Client, automatisch verwaltete Engine, Geräteparser und serielle Einzelgerätetransaktionen)
- `openrgb_sdk.py` (eigener begrenzter SDK-Protokoll-4/5-Paketwriter mit Controller-/Zonensynchronisation und Farb-/Modusrücklesung ohne OpenRGB-CLI-ApplyOptions)
- `rgb_devices.py` (stabile Gerätekennungen, ENE-DRAM-Deduplizierung, Gruppen-/Aliasvalidierung, PC-Skizzenprofile und Prozesssperre)
- `nzxt_rgb.py` (feste NZXT-Effektfähigkeiten, Argumentvalidierung und topology-sichere Kanalaufteilung)
- `rgb_effects.py` (zehn eigene, deterministische und hardwareunabhängige OHC-Effektalgorithmen)
- `desktop_designs.py` (KDE-Erkennung, unverändernde Vorschau, Sicherung, bestätigtes Anwenden und Wiederherstellung)
- `modules/wallpaper_engine/v1_2/` (schreibgeschützte Workshop-/Video-Bibliothek, Plasma-/D-Bus- und Skalierungsadapter, Erststart-Assistent, SHA256-verifizierter optionaler Fedora-Installer und native OHC-Seite ohne kopierten CaptSilver-Code)
- `kraken_lcd_designs.py` (reiner Pillow-Renderer für fünf lokalisierte, skalierbare statische Layouts und nahtlose 20/25-FPS-Hardwareanimationen)
- `kraken_sensors.py` (gemeinsame, rein lesende k10temp-/amdgpu-Sensorauswahl für GUI und Streamer)
- `kraken_cam_streamer.py` (CAM-naher Firmware-2.x-Raw-LCD-Streamer mit Bewegungsglättung, eindeutiger ACK-Zuordnung, phasenstabiler Reihenfolge und GIF-Loop-Diagnose)
- alle Installations-, Diagnose- und udev-Skripte
- Desktopdatei, selbst erstelltes SVG-Symbol, fünf eigene Maus-SVGs und zwei eigene Desktop-Hintergründe unter `assets/`
- vollständige GPL-Lizenz
- deutsche und englische Dokumentation
- zentrale Projektdokumentation `Open_Hardware_Control_Projekt.md`
- OpenLinkHub-Moduldokumentation `OPENLINKHUB_INTEGRATION.md`
- RGB-Studio- und Sicherheitsaudit-Dokumentation `RGB_STUDIO.md`, `RGB_SECURITY_AUDIT.md`
- historische NZXT-Moduldokumentation `Kraken_Control_Projekt.md`
- technische USB-Mitschnittauswertung `USB_CAPTURE_FINDINGS.md`
- reproduzierbares Standardbibliothek-Werkzeug `tools/analyze_usbpcap.py`
- statische, Stub-Laufzeit- und OpenLinkHub-Mauszuordnungstests
- selbst erzeugte 240×240-Test-GIFs für 24, 25, 26 und 27 FPS sowie das Generator-Skript
- `MANIFEST.sha256` mit Prüfsummen der Paketdateien

Zu jedem Release werden aus genau demselben Git-Stand erzeugt:

- `open_hardware_control_v3_4_29_43.zip` – universelles Benutzerpaket
- `open-hardware-control_3.4.29.43_all.deb` – Debian/Ubuntu/Linux-Mint-Paket
- `open-hardware-control-3.4.29.43-1.noarch.rpm` – Fedora/Nobara-Paket
- `open-hardware-control-3.4.29.43-source.tar.gz` – vollständiger Quellcode-Snapshot
- `Entwicklerpaket 3.4.29.43.zip` – vollständiger editierbarer Projektbaum einschließlich Tests, Werkzeuge und GitHub-Automatisierung
- `Open_Hardware_Control_3.4.29.43_LOCAL_AI.gitbundle` – vollständige Git-Historie für lokale KI-Arbeit
- `SHA256SUMS` – Prüfsummen aller Release-Dateien

Das universelle Installations-ZIP enthält den ausführbaren Quellcode und die Laufzeitdokumentation, aber absichtlich keine Entwicklungsordner `tests/` oder `scripts/`. Das **Entwicklerpaket** und das Quellarchiv enthalten diese Ordner vollständig. Der Paketbau vergleicht den vollständigen Testbestand des Repositorys mit dem Entwicklerpaket und bricht bei fehlenden Dateien ab.

Die enthaltenen Test-GIFs werden vollständig aus dem mitgelieferten GPL-Quellcode erzeugt und sind keine externen Mediendateien. `scripts/build_release.py` baut alle Pakete reproduzierbar aus dem ausgecheckten Quellbaum.

Nach einem erfolgreichen Bau sichert der Builder alle erzeugten Artefakte zusätzlich im neben dem Repository liegenden Ordner `Open Hardware Control Backup`. Dort bleiben nach `RELEASE_BACKUP_POLICY.md` die zwei neuesten vollständigen Versionssätze mit eigenen SHA256-Prüfsummen erhalten. Das Entwicklerpaket bildet dabei den vollständigen bearbeitbaren Projektstand ab; ein bei einer Veröffentlichung erzeugtes DEB wird ebenso wie das RPM mitgesichert.
