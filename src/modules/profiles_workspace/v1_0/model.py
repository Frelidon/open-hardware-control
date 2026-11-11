# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure, defensive summaries. No settings, files, hardware or mutations."""
SECTIONS = (("cooling", "Kühlung", "cooling"), ("gpu", "GPU", "gpu"),
            ("rgb", "RGB", "rgb_studio"), ("lcd", "LCD", "lcd"),
            ("design", "Design & Anzeige", "settings"))


def matches(profile, query, kind):
    builtin = bool(profile.get("builtin"))
    if kind == "user" and builtin or kind == "builtin" and not builtin:
        return False
    return query.casefold().strip() in " ".join(str(profile.get(key, "")) for key in
                                               ("name", "description", "category")).casefold()


def summaries(payload, tr):
    if not isinstance(payload, dict):
        return []
    result = []
    for key, title, icon in SECTIONS:
        data = payload.get(key)
        if key == "lcd" and not isinstance(data, dict):
            data = payload.get("levita_display")
        if not isinstance(data, dict):
            continue
        lines = []
        if key == "cooling":
            for field, label in (("pump", "Pumpe"), ("fan", "Lüfter")):
                value = data.get(field)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    lines.append(f"{tr(label)} · {value:g} %")
        elif key == "rgb":
            effect = data.get("studio_effect") or data.get("mode")
            if isinstance(effect, str):
                from rgb_effects import EFFECT_BY_ID
                label = EFFECT_BY_ID[effect].title if effect in EFFECT_BY_ID else effect
                lines.append(tr(label))
            value = data.get("studio_brightness")
            if isinstance(value, (int, float)):
                lines.append(f"{tr('Helligkeit')} · {value:g} %")
        elif key == "gpu":
            if isinstance(data.get("name"), str):
                lines.append(data['name'])
        elif key == "lcd":
            from pathlib import PurePath
            media = data.get("media") or data.get("file")
            if isinstance(media, str) and media:
                name = PurePath(media).name
                from modules.display_effects.v1_11.catalog import DESIGNS
                match = next(((design.title, variant.label) for design in DESIGNS for variant in design.variants if variant.filename == name), None)
                lines.append(f"{tr(match[0])} · {tr(match[1])}" if match else name)
            if isinstance(data.get("brightness"), (int, float)):
                lines.append(f"{tr('Helligkeit')} · {data['brightness']} %")
        elif key == "design":
            theme = str(data.get("theme", ""))
            if theme:
                lines.append(tr({"dark": "Dunkel", "light": "Hell"}.get(theme, theme)))
            if isinstance(data.get("background_theme"), str):
                lines.append(tr(data['background_theme']))
        lines.append(f"{len(data)} {tr('Einstellungen')}")
        result.append((key, title, icon, lines))
    return result
