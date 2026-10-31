# Open Hardware Control 3.4.29.98 INTERN

- Remember the first explicit "keep running in the tray" close choice and hide
  directly on later window-manager close events without another prompt.
- If the new preference does not exist yet, migrate only a real explicit tray
  choice recorded by version `.97` in the bounded private shutdown journal.
- Preserve explicit Quit from the application or tray menu, Cancel, disabled
  tray mode and desktop-session shutdown as separate paths.
- Add regressions for repeated close, persistence and journal migration.

The supplied 17:30:43 application log and the local private journal both prove
an explicit tray choice on this system, so it will be migrated after updating.
No new UI text, elevated action, password handling or hardware write is added.
All 715 release tests, the security/privacy scan and module/repository checks pass.
