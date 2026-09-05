# Third-party software and trademarks

Open Hardware Control uses or interacts with software installed separately on the user's Linux system. These dependencies are not vendored into this repository.

| Component | Role | Upstream | License information |
|---|---|---|---|
| NZXT-ESC | Optional independent LCD-profile authoring/export project; OHC only reads user-selected exported data and vendors no code/designs/fonts/media | https://github.com/mrgogo7/nzxt-esc | CC BY-NC 4.0 upstream; imported user content may have separate rights |
| OpenRGB | Optional separately installed local SDK/hardware backend; no code is vendored | https://gitlab.com/CalcProgrammer1/OpenRGB | GPL-2.0-or-later |
| OpenRGB Effects Plugin | Licence/function reference only; no source code or assets are bundled | https://gitlab.com/OpenRGBDevelopers/OpenRGBEffectsPlugin | GPL-2.0-or-later |
| liquidctl | Kraken/RGB/LCD hardware backend | https://github.com/liquidctl/liquidctl | GPL-3.0-or-later |
| Python | Runtime | https://www.python.org/ | Python Software Foundation License and historical component licenses; see Python's official license page |
| PySide6 / Qt for Python | GUI framework | https://doc.qt.io/qtforpython-6/ | See the official Qt for Python licensing documentation |
| Pillow | Image processing | https://github.com/python-pillow/Pillow | MIT-CMU license; see upstream `LICENSE` |
| KDE Plasma / Breeze | Optional reversible desktop layouts | https://kde.org/plasma-desktop/ | Components remain installed system packages; see KDE upstream licensing metadata |
| CaptSilver Wallpaper Engine for KDE | Optional separately installed Plasma wallpaper plugin; OHC reads local metadata and uses its public local interfaces but vendors no plugin code or media. On Fedora, an explicit setup action may download the exact official release RPM and verify its GitHub-published SHA256 before a separately confirmed Polkit/DNF installation | https://github.com/CaptSilver/wallpaper-engine-kde-plugin | GPL-2.0; Wallpaper Engine itself is separate proprietary software |
| Noto Sans | Optional desktop-layout font | https://fonts.google.com/noto | SIL Open Font License 1.1 |
| TiledScreen | Security/licence reference only; no upstream code or asset is bundled | https://github.com/kavinunethsara/tiledscreen | LGPL-2.1-or-later; audited commits are recorded in `DESKTOP_SECURITY_AUDIT.md` |

NZXT, Kraken, Corsair, OpenRGB, Wallpaper Engine, Steam, Windows 8, Windows 8.1, Windows 11, macOS and other product names are used only to describe compatibility or a general layout style. All trademarks belong to their respective owners. The four desktop wallpapers, OHC icon/cursor variants and OHC RGB effects are original project assets/code; no Microsoft, Apple, Valve, Wallpaper Engine, CaptSilver or OpenRGB media/source is included. Open Hardware Control by Frelidon is independent and is not affiliated with or endorsed by NZXT, Corsair, OpenLinkHub, OpenRGB, Valve, Wallpaper Engine, CaptSilver, Microsoft, Apple, OpenAI, KDE, The Qt Company, the Python Software Foundation, Pillow or liquidctl.

## NZXT-ESC preset compatibility

Open Hardware Control implements its preset reader independently from the exported data format. NZXT-ESC source code, bundled presets, fonts, and media are not copied or redistributed by Open Hardware Control. Remote media referenced by imported profiles is not fetched automatically.
