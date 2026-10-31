# Open Hardware Control 3.4.29.81 INTERN

Interner Teststand vom 13.09.26. Kein öffentlicher GitHub-Release.

## GPU-Effekte und manuelle LED-Einrichtung

- OHC-Designs wählen für native Sapphire-GPUs passende tatsächlich gemeldete Effekte, beispielsweise Rainbow Wave, Runway, Serial oder Spectrum Cycle. Der bisherige automatische External-Control-Zwang entfällt.
- Das vorhandene persönliche PC-Profil bleibt erhalten und nutzt ohne neue Einrichtung den nativen Standard. Lüfter-, Hub-, RAM- und Komponentenanzahlen werden nicht überschrieben.
- Komponenten-Doppelklick und die neue Schaltfläche „Grafikkarte: Steuerweg und LEDs“ öffnen dieselbe GPU-Einrichtung. Für einen bestätigten 5-V-ARGB-Kabelanschluss lässt sich der reale externe Controller zuordnen und dessen vorhandener Zonen-/LED-Editor öffnen.
- Die LED-Anzahl kann nur innerhalb der vom angeschlossenen Controller gemeldeten Grenzen verändert werden. Die interne Sapphire-Zone bleibt eine logische LED; die physische Strip-Länge wird nicht erraten.
- Der externe Steuerweg bleibt mit stabilen Gerätekennungen in Einstellungen und RGB-Profilen gespeichert. External Control wird bei Designs nur bei expliziter Zuordnung und ausgewählter Direct-Quelle verwendet; fehlende Quellen fallen auf native Effekte zurück. Die Einrichtung erklärt, dass Designs auch die übrigen Zonen des ausgewählten Controllers steuern.

## Sicherheit und Validierung

- Unveränderte Loopback-/Besitzgrenzen und vorhandene OpenRGB-Transporte; keine neuen USB-/SMBus-Kommandos.
- DE/EN/ES/FR mit 1.372 gemeinsamen Spracheinträgen.
- Alle 367 Tests einschließlich hardwarefreier Regressionen für native Modi, unzulässige Zuordnungen, fehlende Quellen, Profilschema, Dialogabbruch und Delegation an den realen LED-Editor bestanden. Vollständiger Offscreen-UI-, Lokalisierungs-, Sicherheits-/Datenschutz-, Modulbudget- und Release-Check erfolgreich.
- Die optische Wirkung auf der Karte muss am realen PC bestätigt werden; erfolgreiche Softwaretests sind keine optische Hardwarebestätigung.
