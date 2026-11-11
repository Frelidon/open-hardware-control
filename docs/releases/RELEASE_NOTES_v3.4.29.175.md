# Open Hardware Control 3.4.29.175 INTERN

Der Gerätekatalog führt einzelne Modelle unter Geräteart und Hersteller auf:
Grafikkarten → AMD/NVIDIA → Modell sowie Kühlung, Mainboards, RGB-Controller,
Mäuse, Headsets und Monitore. Herstellerseite und geprüfte Produktseite sind
getrennt; ohne passenden Produktlink erscheint kein Produktknopf. Die
bestehenden GPU-Modellprofile sind als Backend-abhängig gekennzeichnet und
begründen keine neue Hardware-/RGB-Freigabe. Die bisherigen Backend-Übersichten
bleiben in einer eigenen Kategorie erhalten. Quellen stehen in
[der Linkprüfung](../hardware/SUPPORTED_DEVICE_LINKS.md).

Ein reproduzierbarer Qt-Menüsprung ist korrigiert: Untermenüs wurden schon beim
Drücken der Maustaste eingeklappt; eine anschließende Mausbewegung konnte eine
verschobene Zeile auswählen. OHC schaltet jetzt nach Abschluss des Klicks um.
Tastatur, programmatische Auswahl und eigene Menüreihenfolge bleiben erhalten.

Prüfnachweis: 1.556 Tests und fünf Untertests bestanden, einschließlich 220
echten Mausgesten im vollständigen UI-Aufbau in DE/EN/ES/FR.

Alle vier Sprachen, helle/dunkle Paletten und bestehende Hintergrund-, RGB- und
LCD-Animationen bleiben berücksichtigt. Einstellungen und Profile werden nicht
migriert. Prüfung, Paket-/Installations- und Uploadnachweise stehen im
[Projektstatus](../project/PROJECT_STATUS.md). Reale Fedora-Hardwareprüfung bleibt
offen. Diese interne Version wird als Entwicklungsstand auf GitHub hochgeladen;
kein öffentlicher Release-Tag wird automatisch erzeugt.
