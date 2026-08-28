# Roadmap

Open Hardware Control is developed incrementally. Features are tested before they are treated as stable.

## Next internal versions

### 3.4.27 INTERN — consistent application design

- Apply the current dashboard design language consistently to RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About and Help.
- Introduce shared module headers, status panels, section cards and action-button states instead of maintaining a separate visual structure on every page.
- Preserve the existing page behavior, navigation anchors and hardware ownership boundaries during the visual migration.
- Clarify CoolerControl ownership messages: distinguish the closed graphical client from the active `coolercontrold` background service and explain whether the service is running or starts automatically.

### 3.4.28 INTERN — cooling interaction

- Mark the Kraken quick profile Leise, Ausbalanciert or Leistung only after pump and fan writes have succeeded; update the profile label and the complete button/card state together.
- Show all chassis-fan cards collapsed by default.
- Give every card a clear `Kurve & Details bearbeiten` action and expand only the selected card.
- Keep the embedded curve editor associated with that selected fan and allow the currently open card to be collapsed again.
- Add regression tests for successful/failed Kraken profile writes, initial collapsed state and single-card expansion.

### 3.4.29 INTERN — UI finish and reliability

- Complete keyboard navigation, focus-state and scaling checks for the migrated pages.
- Review translations and move further user-visible strings toward dedicated translation resources.
- Add visual/static regression coverage for the shared page components and cooling states.
- Broaden real-hardware testing without claiming untested devices as compatible.
- Improve profile validation and migration handling.

## Packaging

After the first source release has proven stable:

- Fedora/Nobara RPM packaging;
- Debian/Ubuntu DEB packaging;
- Arch/AUR PKGBUILD;
- evaluate Flatpak hardware-access constraints before a Flathub submission.

## Longer term

- More Kraken models based on diagnostic reports and real hardware testing.
- Optional shared launcher/control-center concept for separate Frelidon hardware tools.

This roadmap is not a promise of dates or compatibility.
