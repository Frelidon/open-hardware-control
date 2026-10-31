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
| TiledScreen | Security/licence reference only; no upstream code or asset is bundled | https://github.com/kavinunethsara/tiledscreen | LGPL-2.1-or-later; audited commits are recorded in `docs/security/DESKTOP_SECURITY_AUDIT.md` |
| Seamless Smoke display effect | Edited 1600×720 colour variants bundled for Layer 1; creator Norberto Navarro Valiente (`doktorkleinmusic`) | https://pixabay.com/videos/smoke-abstract-black-background-337943/ | Pixabay Content License |
| Dark Smoke display effect | Edited 1600×720 colour variants bundled for Layer 1; creator TH-DARK Media | https://www.pexels.com/video/smoke-16488810/ | Pexels License |
| Particle Fog display effect | Edited 1600×720 colour variants bundled for Layer 1; creator ForYouMuchMoreSpecial | https://pixabay.com/videos/abstract-smoke-fog-gray-dark-250440/ | Pixabay Content License |
| Fluid Waves display effect | Edited 1600×720 colour variants bundled for Layer 1; creator Colin Jones | https://www.pexels.com/video/abstract-smoke-animation-on-a-black-background-27607570/ | Pexels License |
| Digital Wave display effect | Edited 1600×720 colour variants bundled for Layer 1; creator WhiteHatDesigner | https://pixabay.com/videos/digital-wave-abstract-particles-309178/ | Pixabay Content License |
| Earth 360 display effect | Edited silent 1600×720 excerpt; creator Wikideas1 | https://commons.wikimedia.org/wiki/File:Earth_360_animation.webm | CC0 1.0 |
| Orion Nebula display effect | Edited silent 1600×720 excerpt; ESO; source music credit Johan B. Monell | https://commons.wikimedia.org/wiki/File:Panning_across_the_Orion_Nebula.webm | CC BY 4.0 |
| Ancient Galaxies display effect | Edited silent 1600×720 excerpt; creator ESO/M. Kornmesser | https://commons.wikimedia.org/wiki/File:Artist%E2%80%99s_impression_of_ancient_galaxy_megamerger_(video).webm | CC BY 4.0 |
| NGC 300 display effect | Edited silent 1600×720 excerpt; creator ESO/Digitized Sky Survey 2 | https://commons.wikimedia.org/wiki/File:Panning_across_the_southern_spiral_NGC_300_(ESO_1037a).webm | CC BY 4.0 |
| Milky Way Night display effect | Edited silent 1600×720 excerpt; creator Astrobond | https://commons.wikimedia.org/wiki/File:A_timelapse_of_the_Milky_Way%27s_movement_against_the_backdrop_of_the_Assy-Turgen_Observatory_at_an_altitude_of_2,750_m._Kazakhstan.webm | CC BY-SA 4.0 |
| Cloudscape display effect | Edited silent 1600×720 excerpt; creator John Fowler | https://commons.wikimedia.org/wiki/File:Cloud_timelapse.webm | CC BY 2.0 |
| Aurora Borealis display effect | Edited silent 1600×720 excerpt; creator Harriniva Hotels & Safaris | https://commons.wikimedia.org/wiki/File:Aurora_borealis_timelapse.webm | CC BY 3.0 |
| Steens Mountain display effect | Edited silent 1600×720 excerpt; BLM Oregon & Washington | https://commons.wikimedia.org/wiki/File:Time_Lapse_Clouds_above_Steens_Mountain_(36203941112).webm | Public Domain |
| Tokyo Sunset display effect | Edited silent 1600×720 excerpt; creator Nesnad | https://commons.wikimedia.org/wiki/File:Sunset_tokyoarea-timelapse-2019-03-17.webm | CC BY-SA 4.0 |
| Lake Garda Sunset display effect | Edited silent 1600×720 excerpt without the source title card; creator 93galas | https://commons.wikimedia.org/wiki/File:Time_Lapse_Sunset_4K_4096x2304.webm | CC BY 3.0 |
| Ocean Waves display effect | Edited silent 1600×720 excerpt; creator Matti Schneider | https://commons.wikimedia.org/wiki/File:Ocean_waves.webm | CC BY-SA 3.0 |
| Forest Waterfall display effect | Edited silent 1600×720 excerpt; creator Editor | https://commons.wikimedia.org/wiki/File:Small_waterfall.webm | CC BY 3.0 |
| Jellyfish Blue display effect | Edited silent 1600×720 excerpt; creator FASTILY | https://commons.wikimedia.org/wiki/File:Jellyfish_at_Monterey_Bay_Aquarium_2_2017-11-21.webm | CC BY-SA 4.0 |
| San Juan Waves display effect | Edited silent 1600×720 excerpt; BLM Oregon & Washington | https://commons.wikimedia.org/wiki/File:Crashing_waves_in_the_San_Juan_Islands_(40007700135).webm | Public Domain |
| Red Sea Reef display effect | Edited silent 1600×720 excerpt; creator Kora27 | https://commons.wikimedia.org/wiki/File:Unterwasserwelt,_Korallenriff_im_Roten_Meer_DSCF1654.webm | CC BY-SA 4.0 |
| Kenney UI Pack: Sci-Fi | One component used in the bundled Space Console Layer-2 derivative | https://kenney.nl/assets/ui-pack-sci-fi | CC0 1.0 Universal |
| Kenney Crosshair Pack | One component used in the bundled Orbital Reticle Layer-2 derivative | https://kenney.nl/assets/crosshair-pack | CC0 1.0 Universal |
| Kenney Minimap Pack | One component used in the bundled Navigator Grid Layer-2 derivative | https://kenney.nl/assets/minimap-pack | CC0 1.0 Universal |
| Kenney Light Masks | One component used in the bundled Ambient Glow Layer-2 derivative | https://kenney.nl/assets/light-masks | CC0 1.0 Universal |
| Kenney UI Pack | One component used in the bundled Clean Telemetry Layer-2 derivative | https://kenney.nl/assets/ui-pack | CC0 1.0 Universal |

The display-effect sources are not redistributed as stock-library downloads. OHC supplies edited, cropped, silent H.264 derivatives for its 1600×720 hardware composition and combines them with the user's selected live Layer-2 design. The fifteen nature/space excerpts were manually reviewed to contain no visible people, title cards or technical overlays. Creator, source and license remain visible in the application. Pixabay's license summary is at https://pixabay.com/service/license-summary/, the Pexels license is at https://www.pexels.com/license/ and Creative Commons license texts are linked from the in-app catalog.

NZXT, Kraken, Corsair, OpenRGB, Wallpaper Engine, Steam, Windows 8, Windows 8.1, Windows 11, macOS and other product names are used only to describe compatibility or a general layout style. All trademarks belong to their respective owners. The four desktop wallpapers, OHC icon/cursor variants and OHC RGB effects are original project src/assets/code; no Microsoft, Apple, Valve, Wallpaper Engine, CaptSilver or OpenRGB media/source is included. Open Hardware Control by Frelidon is independent and is not affiliated with or endorsed by NZXT, Corsair, OpenLinkHub, OpenRGB, Valve, Wallpaper Engine, CaptSilver, Microsoft, Apple, OpenAI, KDE, The Qt Company, the Python Software Foundation, Pillow or liquidctl.

## NZXT-ESC preset compatibility

Open Hardware Control implements its preset reader independently from the exported data format. NZXT-ESC source code, bundled presets, fonts, and media are not copied or redistributed by Open Hardware Control. Remote media referenced by imported profiles is not fetched automatically.
