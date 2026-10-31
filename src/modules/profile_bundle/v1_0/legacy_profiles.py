# SPDX-License-Identifier: GPL-3.0-or-later
"""Preserved single-profile JSON exchange, separate from whole-app restore."""
import json
from pathlib import Path
import re
import time
from PySide6.QtWidgets import QFileDialog


def export_selected_profile(host):
    profile = host.selected_profile()
    if profile is None:
        host.show_error(host.tr_static("Bitte ein Profil auswählen.")); return
    default_name = re.sub(r"[^A-Za-z0-9._-]+", "_", str(profile.get("name", "profil"))).strip("_") or "profil"
    filename, _ = QFileDialog.getSaveFileName(host, host.tr_static("Profil exportieren"),
                      str(Path.home() / f"{default_name}.kraken-profile.json"), "Kraken-Profile (*.json)")
    if not filename: return
    try:
        Path(filename).write_text(json.dumps(dict(schema=1, profile=profile), ensure_ascii=False, indent=2), encoding="utf-8")
        host.footer_status.setText(host.tr_static("Profil exportiert"))
    except (OSError, ValueError) as exc:
        host.show_error(host.tr_static("Profil konnte nicht exportiert werden.") + "\n" + str(exc)[:300])


def import_profiles(host):
    filename, _ = QFileDialog.getOpenFileName(host, host.tr_static("Profil importieren"), str(Path.home()), "Kraken-Profile (*.json)")
    if not filename: return
    try:
        if Path(filename).stat().st_size > 8 * 1024 ** 2: raise ValueError("PROFILE_SIZE")
        data = json.loads(Path(filename).read_text(encoding="utf-8"))
        candidates = []
        if isinstance(data, dict) and isinstance(data.get("profile"), dict): candidates = [data["profile"]]
        elif isinstance(data, dict) and isinstance(data.get("profiles"), list): candidates = data["profiles"]
        if not candidates or not all(isinstance(p, dict) for p in candidates): raise ValueError("PROFILE_FORMAT")
        filename_stem = Path(filename).name
        for suffix in (".kraken-profile.json", ".ohc-profile.json", ".json"):
            if filename_stem.casefold().endswith(suffix):
                filename_stem = filename_stem[:-len(suffix)]; break
        filename_stem = filename_stem.strip() or host.tr_static("Importiertes Profil")
        existing_names = {str(item.get("name", "")).casefold() for item in host.user_profiles}
        imported_profiles = []
        for source_index, source in enumerate(candidates):
            imported = json.loads(json.dumps(source))
            imported["id"] = f"user-{int(time.time() * 1000)}-{len(host.user_profiles) + source_index}"
            imported["builtin"] = False
            base_name = filename_stem if len(candidates) == 1 else str(imported.get("name", f"{filename_stem} {source_index + 1}"))
            candidate, counter = base_name[:120], 2
            while candidate.casefold() in existing_names:
                tail = f" ({counter})"; candidate = base_name[:max(1, 120 - len(tail))] + tail; counter += 1
            imported["sourceProfileName"] = str(imported.get("name", "")); imported["name"] = candidate
            existing_names.add(candidate.casefold()); imported_profiles.append(imported)
        host.user_profiles.extend(imported_profiles)
        host.save_profiles(); host.refresh_profiles_table()
        host.footer_status.setText(f'{len(candidates)} {host.tr_static("Profil(e) importiert")}')
    except (OSError, ValueError, TypeError) as exc:
        host.show_error(host.tr_static("Profil konnte nicht importiert werden.") + "\n" + str(exc)[:300])
