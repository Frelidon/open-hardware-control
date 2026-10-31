# Mainboard-Treiber- und MOK-Assistent 1.1

Das Modul führt als statusabhängiger `QWizard` einzeln durch
NCT6687-Treiberinstallation, DKMS-Zertifikat, MOK-Import, physischen
Neustartschritt und anschließendes Laden. Die read-only Statusprüfung läuft
außerhalb des UI-Threads; erledigte Seiten werden übersprungen und notwendige
Aktionen bleiben anklickbar. Version 1.1 liest `/etc/os-release` und bietet
getrennte feste Abhängigkeitsbefehle für Fedora, Ubuntu und Arch Linux an.
Unter Ubuntu sind Paketlisten-Aktualisierung und Installation getrennt; eine
fehlerhafte Fremdquelle wird nicht automatisch verändert. Ein vorhandener
`~/nct6687d`-Checkout wird ausschließlich per Fast-Forward aktualisiert.
Gemeinsame DKMS-/Quellschritte folgen der offiziellen nct6687d-Anleitung.
Die MSI-X870-Moduloption wird nur auf einem entsprechend erkannten MSI-X870-
Mainboard ergänzt; unbekannte Distributionen bleiben ohne geratenen Befehl.
Als fünfter Schritt wird die optionale, benutzerspezifische Polkit-Dauerfreigabe
für den festen Lüfterhelfer angeboten; Paketverwaltung ist nicht freigegeben.
`mokutil`-Text wie `already enrolled` gilt auch
dann als registriert, wenn dessen optionale Kernel-Keyring-Prüfung mit einem
Fehlercode endet. Privilegierte Aktionen bestehen ausschließlich aus festen
`dkms generate_mok`, `mokutil --import /var/lib/dkms/mok.pub` oder
`modprobe nct6687`-Befehlen in einem sichtbaren Terminal nach Bestätigung.

OHC liest oder speichert weder sudo- noch MOK-Passwörter, automatisiert keinen
Neustart, deaktiviert Secure Boot nicht und kann den physischen MOK-Manager im
UEFI nicht ersetzen.
