# Open Hardware Control 3.4.11 INTERN

## Flüssige OpenRGB-Mehrgeräteanimation

- Ein dauerhafter, ausschließlich lokaler SDK-Worker ersetzt den früheren Python-/TCP-Neustart pro Gerät und Frame.
- Alle ausgewählten Direct-Geräte werden in einem gemeinsamen Frame mit 25-Hz-Ziel übertragen.
- Es bleibt genau ein Frame offen; überholte Zwischenbilder werden nach dem Latest-frame-wins-Prinzip zusammengefasst.
- Direct Mode, Zonengrößen, kompletter Geräteframe und Zonen-Fallback werden je Gerät nur bei der Vorbereitung bestätigt. Folgeframes verwenden den günstigen vollständigen Gerätepfad.
- Die Oberfläche zeigt gemessene SDK-Hz, letzte erfolgreiche Übertragung, Batch-Dauer und zusammengefasste Frames. Physische ARGB-Ausgabe bleibt technisch nicht rücklesbar.

## Geführte Einrichtung

- Neuer sechsstufiger Assistent für OpenRGB-/ckb-next-/OpenLinkHub-Konflikte, Gerätebenennung, isolierten Gerätetest, LED-Zonen, Thermaltake-PC-Aufbau und GPU-Hardwaremodus.
- Der Zonendialog besitzt einen Sichttest, bei dem nur die gewählte Zone desselben Controllers leuchtet.
- Für passende Nicht-Direct-Geräte wird bei OHC-Animationen automatisch der gemeldete Modus `External Control` bevorzugt; dies betrifft auf dem Referenzsystem die Sapphire RX 9070 XT.
- Das Thermaltake-Grundprofil und die bestehende verschiebbare PC-Ansicht bleiben erhalten. Eine physische Lüfter-/LED-Zahl wird nicht erfunden, sondern visuell eingerichtet.

## Sicherheit und Kompatibilität

- OpenRGB bleibt ein separat installiertes, von OHC fensterlos verwaltetes Backend. Es wurden keine Treiber oder Effects-Plugin-Assets übernommen.
- Loopback-Zwang, SDK 4/5, Paket-/Geräte-/LED-Grenzen, explizite Sitzungsfreigabe, Einzelinstanz-Sperre, fremde-OpenRGB-Blockade und vollständiger Reset bleiben erhalten.
- Statische Mehrgeräteaktionen bleiben seriell und fehlertolerant. Der neue Animationsworker verarbeitet Gerätefehler einzeln und verbindet bei unklaren Socketantworten sicher neu.
- Ein Protokolltest bestätigt zwei Folgeframes über dieselbe Verbindung und die einmalige Direct-/Zonenvorbereitung.

Diese Version bleibt intern, bis Airgoo, MSI Mystic Light, ENE DRAM, Sapphire, NZXT und die Konfliktfälle auf dem realen Fedora-System erneut geprüft wurden.
