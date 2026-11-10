# Open Hardware Control 3.4.29.169 STABLE

## RGB-Unterbau, Farben und Bedienung

- Feste monotone 60-Hz-Animationszeitbasis, unabhängig vom gewählten Tempo.
  Veraltete Frames werden ersetzt, nicht als Rückstau nachgesendet.
- Ein dauerhafter nativer Arbeiter pro OpenRGB-Controller; ein langsamer
  Mainboardtransfer bremst keine anderen Controller mehr aus. Ohne optionales
  Plugin bleibt der parallele, geordnete SDK-Arbeiter verfügbar.
- Direct-Geräte erhalten das exakte OHC-Design statt ähnlicher Hardwareeffekte.
  Der RGB-Kanalpackfehler im Plugin ist behoben: Haupt-/Nebenfarbe bleiben
  getrennt statt als Grauwerte anzukommen. Kompilierte Farbtests sichern dies ab.
- Sapphire-GPUs mit bestätigtem externem ARGB-Eingang werden auf `External
  Control` gehalten; Auswahl und gespeicherte Zonenroute bleiben maßgeblich.
- PLAY/STOPP, gespeicherte Designfarben/-geschwindigkeit und Standard-Reset,
  zusätzliche LED-Zahlanzeigen in der Gehäuseansicht sowie Abschlussbeleuchtung
  mit Weiß, Wunschfarbe oder tatsächlich unterstütztem Hardware-Rainbow.
- Unsichtbare verwaltete Qt-Engine, vollständige Geräteerkennung für das private
  OpenRGB 1.1 und behobener Null-Widget-Absturz des nativen Plugins.
- Aktuelle-Generation-Bestätigung statt bloßem Queue-ACK; getrennte Messwerte
  für API-Übergaben und physische USB-Transfers.
- Gemeinsamer RAM-Einrichtungsdialog unverändert in ein Fachmodul ausgelagert;
  Hauptdatei-Größengrenze und vollständige Qt-/Sprachtests bleiben erhalten.

## Nachweis und Grenzen

Der vollständige lokale Release-Wächter besteht mit **1.347 Tests und fünf
Untertests**, einschließlich echtem vier-sprachigem Qt-Aufbau, nativen C++-
Fixtures, Sicherheits-/Datenschutzscan und Modul-/Größen-/Layoutprüfung.

Unter Ubuntu wurden sechs Geräte erkannt. Gemessene Airgoo-USB-Frames steigen
von 3,83 auf 58,52 pro Sekunde. Der separat zu bauende MSI-761-Dirty-Zone-Patch
vermeidet unveränderte Reports; eine geänderte Zone erreicht hier etwa
10,64 vollständige Frames/s statt rund 2,8. Physische 60 FPS auf jedem Gerät
werden ausdrücklich nicht behauptet. Der Eigentümer bestätigt flüssige
Gehäuse- und GPU-Animationen sowie korrekte GPU-Farben.

Das unveränderte Levita-LCD arbeitet nach normalem Start und der vorhandenen
begrenzten Daemon-Wiederherstellung wieder; Status und Eigentümer bestätigen
die Videowiedergabe. LCD-Design, USB-Protokoll und FPS-Einstellungen wurden
nicht geändert. Reale Fedora-Hardwareprüfung des neuen nativen Pfads bleibt offen.

## Installation, Quellcode und Sicherung

ZIP, DEB und RPM enthalten OHC, nicht einen universellen OpenRGB-Binärtreiber.
Der optionale native Pfad benötigt passende OpenRGB-/Qt-Versionen und den
separaten MSI-Patch. Bestehende private Einstellungen und Backends bleiben bei
einem normalen OHC-Update erhalten. Die vollständige
[Installationsanleitung](../INSTALL.md) und die
[native RGB-Anleitung](../hardware/NATIVE_RGB_SETUP.md) erklären Aufbau und
Wiederherstellung. Der vollständige native Quellcode und Patch liegen im
Entwicklerpaket, Quellarchiv und Git-Repository.

Alle Release-Dateien erhalten SHA-256-Prüfsummen. Entwickler-ZIP, Quellarchiv
und Git-Bundle sichern den editierbaren Stand und seine Historie zusätzlich zu
Laufzeit-ZIP, DEB und RPM. Private Profile, Logs, Kameraaufnahmen und lokal
gebaute Backend-Binärdateien werden nicht veröffentlicht. Bestehende
Geräteschutz-, Freigabe-, Übersetzungs- und Eigentümergrenzen bleiben erhalten.
