# Open Hardware Control 3.4.29.131 INTERN

Datum: 01.10.2026

## Levita-Dauerbetrieb mit TRCC 9.10.4

- OHC erkennt die exakte erfolgreiche Übergabe von `trcc display play` an den
  daemoninternen `VideoLoop`. Der planmäßig beendete CLI-Helfer wird nicht mehr
  als abgestürzter Taktgeber behandelt und verbraucht kein Neustartbudget.
- Video- und Sensor-Takt laufen dadurch dauerhaft im vorhandenen einzelnen
  TRCC-Daemon weiter. Es wird kein zweiter USB-Besitzer geöffnet.
- Die bestehende Speicheraufsicht bleibt auch nach der Übergabe aktiv und kann
  weiterhin nur den exakt identifizierten eigenen Daemon begrenzt
  wiederherstellen.

## Abschaltwächter

- Der separate Levita-Wächter stellt beim direkten Start über seinen
  Dateipfad den installierten OHC-Modulpfad selbst her. Damit erreicht er das
  Pipe-Warten und die einmalige feste Gerätefreigabe, statt bereits beim Import
  mit `ModuleNotFoundError` zu enden.
- Sauberes Beenden, Testmodus, feste Geräte-ID und die vorhandenen
  Besitz-/Zeitgrenzen bleiben unverändert.

## Referenzprüfung

- Die offizielle TRCC-Linux-Version 9.10.4 wurde mit dem veröffentlichten
  SHA-256-Wert geprüft, systemweit installiert und auf dem angeschlossenen
  Levita-Display beobachtet.
- Der Daemon schrieb fortlaufend vollständige 1600×720-Frames. Über die
  fokussierte Stichprobe blieben etwa 183 MiB RSS, 33 Threads und 29 offene
  Dateideskriptoren stabil.
- Gezielte Regressionen decken die exakte Übergabe, das unverbrauchte
  Neustartbudget und den alleinstehenden Abschaltwächter ab.

## Build und vollständige Prüfung

- Der vollständige Release-Check bestand 839 Tests sowie Sicherheits-,
  Datenschutz- und Modulprüfung. Die Warnungen betreffen bekannte
  Aufteilungsgrenzen und eine angekündigte Pillow-Abkündigung, nicht den
  Release-Erfolg.
- Laufzeit-ZIP, vollständiges Entwicklerpaket, Quellarchiv,
  Local-AI-Git-Bundle und RPM wurden lokal gebaut und zusammen mit der
  rollierenden Sicherung per SHA-256 verifiziert. `dpkg-deb` ist auf diesem
  Rechner nicht verfügbar; deshalb wurde kein DEB vorgetäuscht.
