# SPDX-License-Identifier: GPL-3.0-or-later
"""Confirmed staged restore before startup reads settings; no hardware calls."""
import hashlib
import json
from pathlib import Path
import tempfile
from .archive import MAX_META, json_bytes, strict_path
from .values import decode, encode

PENDING_KEY = "profile_bundle/pending_restore_v1"


def safety_settings(values):
    """Do not inherit authority to write someone else's hardware at restart."""
    result = {k: v for k, v in values.items() if not k.startswith("profile_bundle/")}
    for key in ("mainboard_fans/master_enabled", "thermalright/autostart_enabled", "rgb_studio/profile_autostart",
                "rgb_studio/auto_reclaim", "lcd/keepalive", "lcd/restore", "lcd/experimental_session_active",
                "clock/auto_resend", "clock/active", "hardware_lcd/active", "safety/auto_max", "safety/expert_mode"):
        result[key] = False
    result.update({"profiles/startup": "none", "setup/pending_profile": "", "thermalright/test_mode": True})
    for channel in ("pump", "fan"):
        result[f"cooling/{channel}_mode"] = "unbekannt"
        result[f"cooling/{channel}_mode_detail"] = "Noch nicht durch Kraken Control gesetzt"
    raw = result.get("mainboard_fans/profiles", "{}")
    try:
        profiles = json.loads(str(raw))
        if isinstance(profiles, dict):
            for profile in profiles.values():
                if isinstance(profile, dict):
                    profile.update(enabled=False, calibrated=False)
            result["mainboard_fans/profiles"] = json.dumps(profiles, ensure_ascii=False)
    except (TypeError, ValueError): result["mainboard_fans/profiles"] = "{}"
    result.pop(PENDING_KEY, None)
    return result


def lcd_store_root(settings, config_root):
    default = Path(config_root) / "lcd-profiles"
    raw = str(settings.value("profile_bundle/lcd_store_v1", "") or "")
    if not raw: return default
    try:
        root = strict_path(Path(raw))
        base = strict_path(Path(config_root) / "profile-imports")
        if root.is_dir() and root.is_relative_to(base): return root
    except (OSError, ValueError): pass
    return default


def restore_pending(settings, config_root):
    pending = str(settings.value(PENDING_KEY, "") or "")
    if not pending: return None
    config_root = Path(config_root)
    try:
        record = json.loads(pending)
        stage = strict_path(Path(record["stage"]))
        base = strict_path(config_root / "profile-imports")
        if stage.parent != base: raise ValueError("BUNDLE_STAGE_BOUNDARY")
        ready = stage / "ready.json"
        strict_path(ready)
        if ready.stat().st_size > MAX_META: raise ValueError("BUNDLE_METADATA_SIZE")
        data = ready.read_bytes()
        if hashlib.sha256(data).hexdigest() != record["sha256"]: raise ValueError("BUNDLE_CHECKSUM")
        snapshot = json.loads(data)
        values = safety_settings({k: decode(v) for k, v in snapshot["settings"].items()})
        lcd_root = snapshot.get("lcd_store", "")
        if lcd_root:
            lcd = strict_path(Path(lcd_root))
            if not lcd.is_dir() or not lcd.is_relative_to(stage / "assets"): raise ValueError("BUNDLE_LCD_ROOT")
            values["profile_bundle/lcd_store_v1"] = str(lcd)
        old_values = {k: encode(settings.value(k)) for k in settings.allKeys() if k != PENDING_KEY}
        target = config_root / "profiles.json"
        old_profiles = target.read_bytes() if target.exists() else b""
        if len(old_profiles) > MAX_META: raise ValueError("BUNDLE_METADATA_SIZE")
        rollback = Path(tempfile.mkdtemp(prefix="before-restore-", dir=base))
        (rollback / "settings.json").write_bytes(json_bytes(old_values))
        (rollback / "profiles.json").write_bytes(old_profiles)
        values["profile_bundle/rollback_v1"] = str(rollback)
        profiles = json_bytes(dict(schema=1, profiles=snapshot["profiles"]))
        temporary = config_root / (".profiles-restore-" + stage.name + ".tmp")
        temporary.write_bytes(profiles)
        # Commit only after every value and profile has been validated/prepared.
        try:
            settings.clear()
            for k, v in values.items(): settings.setValue(k, v)
            settings.sync()
            status = getattr(settings, "status", lambda: 0)()
            if getattr(status, "value", status) != 0: raise OSError("BUNDLE_SETTINGS_WRITE")
            temporary.replace(target)
        except Exception:
            settings.clear()
            for k, v in old_values.items(): settings.setValue(k, decode(v))
            settings.sync()
            if temporary.exists(): temporary.unlink()
            raise
        return "restored"
    except (OSError, ValueError, TypeError, KeyError) as exc:
        # Preserve the selected package and existing live settings for diagnosis.
        settings.remove(PENDING_KEY)
        settings.setValue("profile_bundle/restore_error_v1", type(exc).__name__ + ": " + str(exc)[:200])
        settings.sync()
        return "failed"
