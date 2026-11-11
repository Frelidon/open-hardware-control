# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit requests through the existing guarded RGB and LCD controllers."""
from rgb_effects import BUILTIN_DESIGNS
from modules.display_effects.v1_11.catalog import DESIGNS, validated_asset


def resolve_pair(pair):
    index = next(i for i, (title, _cfg) in enumerate(BUILTIN_DESIGNS)
                 if title == pair.rgb_title)
    design = next(design for design in DESIGNS if design.ident == pair.lcd_id)
    return index, validated_asset(design.variants[0])


def apply_pair(host, pair, target):
    """Selection/preview never calls this. Each target retains its own guards."""
    index, media = resolve_pair(pair)
    rgb = target in {"both", "rgb"}
    lcd = target in {"both", "lcd"}
    if target not in {"both", "rgb", "lcd"}:
        raise ValueError("invalid design target")
    if hasattr(host, "feature_enabled"):
        if (rgb and not host.feature_enabled("rgb")) or (lcd and not host.feature_enabled("lcd")):
            return "Den benötigten RGB- oder LCD-Bereich zuerst in den Einstellungen aktivieren."
    studio = getattr(host, "thermalright_display_studio", None)
    if lcd and (studio is None or not host.is_thermalright_cooling()):
        return "Das LCD-Design benötigt das Levita-Display. RGB kann separat angewendet werden."
    # Validate both assets/targets before changing either selection. These are
    # independent asynchronous requests, not an atomic hardware transaction.
    if lcd:
        studio.select_bundled_effect_media(media, pair.title)
    if rgb:
        host.activate_rgb_design_tile(index)
    if lcd:
        studio.stage_profile_startup_design()
        studio.apply_design()
    return "Anwendung angefordert. Den tatsächlichen Status zeigen RGB Studio und LCD Studio."


def prepare_game_rule(host, game):
    """Open an editable draft; do not save or activate anything on navigation."""
    page = host.design_automation_page
    page.table.clearSelection()
    page.table.setCurrentCell(-1, -1)
    page.name_input.setText(game.title)
    page.trigger_combo.setCurrentIndex(page.trigger_combo.findData("game"))
    page.value_input.setText(game.process)
    page.refresh_profiles()
    page.profile_combo.setCurrentIndex(0)
    page.priority_spin.setValue(50)
    page.enabled_check.setChecked(True)
    page.restore_check.setChecked(True)
    host.tabs.setCurrentIndex(host.design_automation_page_index)
