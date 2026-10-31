# Open Hardware Control 3.4.29.82 INTERN

Interner GPU-ARGB-Fix vom 13.09.26. Kein öffentlicher Release.

- Die GPU-Einrichtung wählt Controller und konkreten ARGB-Anschluss. MSI JARGB 1 entspricht dem bestätigten JARGB_V2_1; die vierpolige JRGB-Beleuchtung ist kein ARGB-Ersatz.
- Der GPU-Effekt wird über die LED-Länge dieser Zone berechnet, nicht über alle MSI-LEDs zusammen. Andere Zonen erhalten unabhängige Effektlängen und behalten den Controller-Effekt.
- Ein eigener Anschlusseditor speichert eine Grafikkarte als ein Gerät mit manuell eingetragener LED-Anzahl. Der begrenzte Einzel-LED-Sichttest beleuchtet nur den gewählten Index; andere Controllerzonen werden vorübergehend schwarz. Danach das gewünschte Design erneut anwenden.
- Aktuell gespeicherte GPU-Verkabelung und LED-Anzahl bleiben bei Profilwechsel und altem Startprofil erhalten. Eine ausdrücklich gewählte native Steuerung bleibt ebenfalls erhalten.
- Nur die persönliche Frelidon-Ansicht erhält einmalig die bestätigte Sapphire-9070/MSI-JARGB-1-Zuordnung. Die irrtümliche Deklaration 3 × 80/90 wird dort auf ein Gerät mit dem bisherigen Testwert korrigiert. Andere Anschlüsse und eigene explizite Zuordnungen bleiben erhalten. 80/90 sind keine bestätigten physischen Herstellerangaben.
- RGB Studio 1.4, DE/EN/ES/FR mit 1.381 gemeinsamen Einträgen. Vorhandener Loopback-SDK-Transport, Besitzgrenzen und Schreibfreigabe unverändert; kein neuer USB-/SMBus-Schreibpfad.

374 hardwarefreie Tests einschließlich Zonenkoordinaten, realem Qt-Anschlusseditor, Pixeloffset, Profilübernahme, Migration, voller UI und DE/EN/ES/FR bestanden. Release-, Sicherheits-/Datenschutz- und Modulbudgetprüfung erfolgreich. Der Besitzer hat die automatische Entfernung der älteren Sicherung .80 ausdrücklich freigegeben; der lokale Paketbau bewahrt .81 und .82. Installation und Veröffentlichung sind nicht Bestandteil des Paketbaus. Die sichtbare Wirkung ist am realen PC noch zu prüfen.
