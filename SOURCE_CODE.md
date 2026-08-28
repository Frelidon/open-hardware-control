# Quellcode und reproduzierbare Release-Pakete

Jeder weitergegebene Open-Hardware-Control-Stand soll vollständig nachvollziehbar bleiben.

Das interne Installations-ZIP 3.4.17 enthält den direkt editierbaren Python-Quellcode einschließlich `desktop_shell.py`, `desktop_assets.py` und `desktop_designs.py`:

- `kraken_control.py`
- `openlinkhub_integration.py` (lokale OpenLinkHub-API-, validierte Schreib- und Benutzerdienst-Anbindung)
- `openlinkhub_mouse_visuals.py` (Modellfamilien, lizenzfreie Schema-Geometrie und sichere Zuordnung gemeldeter Tastenbelegungen)
- `openrgb_integration.py` (Loopback-only OpenRGB-SDK-/CLI-Client, automatisch verwaltete Engine, Geräteparser und serielle Einzelgerätetransaktionen)
- `openrgb_sdk.py` (eigener begrenzter SDK-Protokoll-4/5-Paketwriter mit Controller-/Zonensynchronisation und Farb-/Modusrücklesung ohne OpenRGB-CLI-ApplyOptions)
- `rgb_devices.py` (stabile Gerätekennungen, ENE-DRAM-Deduplizierung, Gruppen-/Aliasvalidierung, PC-Skizzenprofile und Prozesssperre)
- `nzxt_rgb.py` (feste NZXT-Effektfähigkeiten, Argumentvalidierung und topology-sichere Kanalaufteilung)
- `rgb_effects.py` (zehn eigene, deterministische und hardwareunabhängige OHC-Effektalgorithmen)
- `desktop_designs.py` (KDE-Erkennung, unverändernde Vorschau, Sicherung, bestätigtes Anwenden und Wiederherstellung)
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

- `open_hardware_control_v3_4_16_INTERN.zip` – universelles internes Benutzerpaket
- `open-hardware-control_3.4.27~intern2_all.deb` – internes Debian/Ubuntu/Linux-Mint-Paket
- `open-hardware-control-3.4.27-0.intern2.noarch.rpm` – internes Fedora/Nobara-Paket
- `open-hardware-control-3.4.17-INTERN-source.tar.gz` – vollständiger Quellcode-Snapshot
- `Entwicklerpaket 3.4.17 INTERN.zip` – vollständiger editierbarer Projektbaum einschließlich Tests, Werkzeuge und GitHub-Automatisierung
- `SHA256SUMS` – Prüfsummen aller Release-Dateien

Die enthaltenen Test-GIFs werden vollständig aus dem mitgelieferten GPL-Quellcode erzeugt und sind keine externen Mediendateien. `scripts/build_release.py` baut alle Pakete reproduzierbar aus dem ausgecheckten Quellbaum.
