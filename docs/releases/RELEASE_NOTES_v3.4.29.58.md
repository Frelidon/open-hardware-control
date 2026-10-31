# Open Hardware Control 3.4.29.58 INTERN

## Designbibliothek wird wirklich angewendet

- Der neue Logausschnitt zeigt mehrere Klicks auf „Effekt auf Gerät anwenden“, ohne dass danach ein Thermalright-Befehl startet. Ein normales LCD-Design wurde unmittelbar danach erfolgreich übertragen.
- Ursache: Die frei lizenzierten Paketvideos wurden an die ausschließlich für privat erzeugte Cachevideos vorgesehene Pfadprüfung übergeben. Dadurch endete die Aktion vor der Levita-Apply-Sequenz.
- Display Effects 1.3 besitzt einen eigenen sicheren Übergabepunkt für gebündelte Offline-Medien. Cache und Paketbibliothek haben getrennte erlaubte Wurzeln und dieselbe strikte MP4-, Symlink- und Pfadprüfung.
- Erfolgreiche Auswahl sowie eine Abweisung werden jetzt im gemeinsamen Log sichtbar. Anschließend läuft unverändert die bestehende Layer-2-, Testmodus-, Schutzpausen- und TRCC-Sequenz.
- Der Rauch-Worker verweist nach der Modulversionsanhebung ebenfalls auf den einzigen aktuellen Ordner, sodass der prozedurale Export erhalten bleibt.

Interne Testversion. Kein GitHub-Push, Tag oder öffentliches Release wurde erstellt.
