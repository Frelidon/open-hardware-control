# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixed local assets; titles are canonical German, never translated IDs."""
from pathlib import Path
ASSETS = Path(__file__).resolve().parents[3] / 'assets'
VIDEO_THEMES = {
    'Matrix Code Rain · Video': ASSETS / 'display-effects/ohc-code-rain-large-30.mp4',
    'Aurora Silk · Video': ASSETS / 'app-backgrounds/aurora-silk.mp4',
    'Nebula Depth · Video': ASSETS / 'app-backgrounds/nebula-depth.mp4',
    'Liquid Prism · Video': ASSETS / 'app-backgrounds/liquid-prism.mp4',
    'Ocean Caustics · Video': ASSETS / 'app-backgrounds/ocean-caustics.mp4',
    'Solar Orbit · Video': ASSETS / 'app-backgrounds/solar-orbit.mp4',
}


def profile_source(payload):
    """Interpret saved values only, reject remote/non-regular/oversized media."""
    if not isinstance(payload, dict): return None, None
    from rgb_effects import RGBEffectConfig
    for section, key in (('levita_display', 'media'), ('lcd', 'file')):
        data = payload.get(section)
        if not isinstance(data, dict): continue
        if section == "lcd" and data.get("mode") in {"clock", "hardware", "unchanged"}: continue
        value = data.get(key)
        if not isinstance(value, str) or not value or not Path(value).is_absolute(): continue
        path = Path(value)
        try:
            if path.suffix.lower() in {'.mp4', '.webm', '.mkv', '.mov', '.gif', '.png', '.jpg', '.jpeg', '.webp'} and path.is_file() and path.stat().st_size <= 256*1024*1024:
                return path.resolve(), None
        except (OSError, ValueError, RuntimeError):
            continue
    data = payload.get('rgb')
    if isinstance(data, dict):
        try:
            return None, RGBEffectConfig(str(data.get('studio_effect', 'static')),
                str(data.get('studio_primary', data.get('color1', '00aaff'))).lstrip('#'),
                str(data.get('studio_secondary', data.get('color2', 'ffffff'))).lstrip('#'),
                int(data.get('studio_brightness', 80)), int(data.get('studio_speed', 70)),
                int(data.get('studio_direction', 1))).normalized()
        except (ValueError, TypeError, OverflowError): pass
    return None, None
