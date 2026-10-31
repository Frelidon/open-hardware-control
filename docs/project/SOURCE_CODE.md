# Quellcode und reproduzierbare Release-Pakete

Jeder weitergegebene Open-Hardware-Control-Stand soll vollständig nachvollziehbar bleiben.

Das interne Installations-ZIP 3.4.29.82 enthält den direkt editierbaren Python-Quellcode einschließlich `src/desktop_shell.py`, `src/desktop_assets.py` und `src/desktop_designs.py`:

- `src/kraken_control.py`
- `src/openlinkhub_integration.py` (lokale OpenLinkHub-API-, validierte Schreib- und Benutzerdienst-Anbindung)
- `src/openlinkhub_mouse_visuals.py` (Modellfamilien, lizenzfreie Schema-Geometrie und sichere Zuordnung gemeldeter Tastenbelegungen)
- `src/openrgb_integration.py` (Loopback-only OpenRGB-SDK-/CLI-Client, automatisch verwaltete Engine, Geräteparser und serielle Einzelgerätetransaktionen)
- `src/openrgb_sdk.py` (eigener begrenzter SDK-Protokoll-4/5-Paketwriter mit Controller-/Zonensynchronisation und Farb-/Modusrücklesung ohne OpenRGB-CLI-ApplyOptions)
- `src/rgb_devices.py` (stabile Gerätekennungen, ENE-DRAM-Deduplizierung, Gruppen-/Aliasvalidierung, PC-Skizzenprofile und Prozesssperre)
- `src/nzxt_rgb.py` (feste NZXT-Effektfähigkeiten, Argumentvalidierung und topology-sichere Kanalaufteilung)
- `src/rgb_effects.py` (zehn eigene, deterministische und hardwareunabhängige OHC-Effektalgorithmen)
- `src/modules/localization/v1_0/` (je eine vollständige Datei für Deutsch, Englisch, Spanisch und Französisch sowie Katalog- und Dynamikprüfung)
- `src/modules/ui_performance/v1_1/` (leichte globale Seitenübergänge und begrenzter gemeinsamer SSD-Cache für regenerierbare Kataloge/Vorschaubilder)
- `src/modules/responsive_startup/v1_0/` (zusammengefasste, fail-closed CoolerControl-Prüfung außerhalb des GUI-Prozesses)
- `src/modules/display_effects/v1_11/` (Rauchrenderer, responsiver attribuierter Offline-Medienkatalog, aktive Haupt-/Farbvariantensynchronisierung, grafische Sensorlayout-Auswahl, Firmware-Rückgabe, Profilstart-Vormerkung und hochwertig übersampelte Lichtbänder)
- `src/modules/lcd_media_manager/v1_0/`, `responsive_gallery/v1_0/` und `temperature_history/v1_2/` (nicht-destruktive Quellenverwaltung, dynamische Kachelraster und datierter CSV-/JSON-Berichtsexport)
- `src/modules/section_tabs/v1_0/` (wiederverwendbare, synchronisierte Unterreiter für Bereiche mit Seitenleisten-Unterpunkten)
- `src/modules/lcd_levita/v1_7/` (Datenoberfläche, Geometrie, Theme-Staging, vier originale Glow-/Partikelrenderer und lokale Ein-Strom-Komposition), `src/modules/levita_performance/v1_1/` (FPS-, Spielsignal- und Abfragerichtlinie) sowie `tools/render_levita_overlays.py` und `tools/render_levita_motion.py` für reproduzierbare Layer-2-Stile und Bewegungen
- `src/desktop_designs.py` (KDE-Erkennung, unverändernde Vorschau, Sicherung, bestätigtes Anwenden und Wiederherstellung)
- `src/modules/wallpaper_engine/v1_3/` (schreibgeschützte zwischengespeicherte Workshop-/Video-Bibliothek, Plasma-/D-Bus- und Skalierungsadapter, lokalisierter Assistent mit KDE-Hilfspaketen, SHA256-verifizierter optionaler Fedora-Installer und native OHC-Seite ohne kopierten CaptSilver-Code)
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

- `open_hardware_control_v3_4_29_79_INTERN.zip` – universelles internes Benutzerpaket
- `open-hardware-control_3.4.29.82~intern2_all.deb` – internes Debian/Ubuntu/Linux-Mint-Paket
- `open-hardware-control-3.4.29.82-0.intern2.noarch.rpm` – internes Fedora/Nobara-Paket
- `open-hardware-control-3.4.29.82-INTERN-source.tar.gz` – vollständiger Quellcode-Snapshot
- `Entwicklerpaket 3.4.29.82 INTERN.zip` – vollständiger editierbarer Projektbaum einschließlich Tests, Werkzeuge und GitHub-Automatisierung
- `Open_Hardware_Control_3.4.29.82_INTERN_LOCAL_AI.gitbundle` – vollständige Git-Historie für lokale KI-Arbeit
- `SHA256SUMS` – Prüfsummen aller Release-Dateien

Das universelle Installations-ZIP enthält den ausführbaren Quellcode und die Laufzeitdokumentation, aber absichtlich keine Entwicklungsordner `tests/` oder `scripts/`. Das **Entwicklerpaket** und das Quellarchiv enthalten diese Ordner vollständig. Der Paketbau vergleicht den vollständigen Testbestand des Repositorys mit dem Entwicklerpaket und bricht bei fehlenden Dateien ab.

Die enthaltenen Test-GIFs werden vollständig aus dem mitgelieferten GPL-Quellcode erzeugt und sind keine externen Mediendateien. `scripts/build_release.py` baut alle Pakete reproduzierbar aus dem ausgecheckten Quellbaum.

Nach einem erfolgreichen Bau sichert der Builder alle erzeugten Artefakte zusätzlich im neben dem Repository liegenden Ordner `Open Hardware Control Backup`. Dort bleiben nach `RELEASE_BACKUP_POLICY.md` die zwei neuesten vollständigen Versionssätze mit eigenen SHA256-Prüfsummen erhalten. Das Entwicklerpaket bildet dabei den vollständigen bearbeitbaren Projektstand ab; ein bei einer Veröffentlichung erzeugtes DEB wird ebenso wie das RPM mitgesichert.
