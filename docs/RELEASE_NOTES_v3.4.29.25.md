# Open Hardware Control 3.4.29.25 INTERN

**Datum:** 02.09.26

Diese interne Version präzisiert ausschließlich die GitHub- und KI-Arbeitsregeln. Ein normaler Push eines vollständig committed und getesteten Arbeitsstands auf einen Entwicklungsbranch ist nach einem ausdrücklichen Auftrag des Projektinhabers auch mit `BUILD_CHANNEL=INTERN` erlaubt. Gleiches gilt für einen Pull Request nur dann, wenn er ebenfalls konkret beauftragt wurde.

`BUILD_CHANNEL=INTERN` blockiert weiterhin Tags und öffentliche GitHub-Releases. Ein normaler Branch-Push erteilt niemals automatisch die Erlaubnis für einen Pull Request, Force-Push, eine Branch- oder Tag-Löschung, einen Tag oder einen Release. Diese Aktionen bleiben getrennt freizugeben; ein öffentlicher Tag oder Release benötigt zusätzlich den validierten Kanal `STABLE`.

An Hardwaresteuerung, Geräteunterstützung und dem Levita-LCD-Modul 1.2 wurde nichts geändert.
