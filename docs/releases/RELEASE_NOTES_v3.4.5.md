# Open Hardware Control 3.4.5 INTERN

Diese interne Hardwaretest-Version adressiert den von Fedora gespeicherten OpenRGB-Coredump. Der Absturz trat bei einem syntaktisch gültigen Einzelgerätebefehl in OpenRGBs interner Funktion `ApplyOptions` auf. OHC überträgt Direct-Mode-Farben deshalb nicht mehr über diesen CLI-Pfad, sondern über einen eigenen, strikt lokalen und begrenzten SDK-Schreibhelfer an die weiterhin separat installierte, von OHC verwaltete OpenRGB-Engine.

Der neue Pfad gilt für statische Farben, den Einzelgeräte-Testmodus und OHC-Softwareanimationen. Geräte ohne Direct Mode verwenden weiterhin ausschließlich einen tatsächlich gemeldeten nativen Hardwaremodus. Ein Hub, der nur eine logische LED meldet, bleibt elektrisch ein gemeinsamer Kanal; OHC erfindet keine nicht vorhandenen Einzelkanäle.

Die RGB-Oberfläche behält ihre Scrollposition auch beim Neubau von Kacheln und Gruppen. Frelidons Thermaltake-Profil zeigt nun geordnet zwölf Lüfter: drei am Kraken-Radiator oben, zwei vorne, drei Reverse-Lüfter an Rückwand/Seite, drei Reverse-Lüfter auf der Netzteilabdeckung vorne und einen Hecklüfter. Eigene Blöcke lassen sich hinzufügen, bearbeiten, entfernen, verschieben und automatisch anordnen.

Die Version bleibt `INTERN`. Vor einer Veröffentlichung sind reale Tests von MSI MYSTIC LIGHT, Airgoo AG-DRGB16, den zwei RAM-Riegeln, Sapphire RX 9070 XT, Kraken-RGB sowie Reset und Programmende erforderlich.
