# Open Hardware Control 3.4.29.39 INTERN

Diese interne Korrektur bereinigt die temporäre Fensterdiagnose, ohne ihre Schutzfunktion gegen unbekannte oder verdächtige Fenster abzuschwächen.

- Normale Qt-Tooltips werden nicht mehr als geöffnete, ausgeblendete, geschlossene oder native Fenster protokolliert.
- Die internen `QFrame`-Popups direkt unter einer `QComboBox` werden ebenfalls nicht mehr protokolliert. Dadurch erzeugen die Auswahlfelder der Lüfterkarten beim Profilwechsel keine irreführenden Fensterdiagnosezeilen mehr.
- Andere Popupfenster bleiben sichtbar in der Diagnose. Die exakte Quarantäne des bekannten elternlosen, titellosen 640×480-`QFrame` bleibt unverändert aktiv.
- TRCC Linux 9.9.12 bleibt die empfohlene kompatible Levita-Backend-Version; der reale Hardwaretest ist weiterhin transparent als 9.9.11-Test dokumentiert.

Die in 3.4.29.38 eingeführten RGB-Studio-Verbesserungen und RGB-Studio-Modul 1.1 bleiben unverändert enthalten.
