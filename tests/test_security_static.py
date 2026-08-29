#!/usr/bin/env python3
"""Dependency-free static release checks for internal version 3.4.23."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
main_code = (ROOT / "kraken_control.py").read_text(encoding="utf-8")
module_names = (
    "app_constants.py", "command_backend.py", "cooling_card_state.py", "cooling_widgets.py",
    "localization_catalog.py", "privacy_logging.py", "temperature_utils.py",
)
module_code = {name: (ROOT / name).read_text(encoding="utf-8") for name in module_names}
# Static guards search the complete runtime implementation even though the
# former monolith is now split into focused modules.
code = main_code + "\n" + "\n".join(module_code.values())
rule = (ROOT / "71-nzxt-kraken-2023.rules").read_text(encoding="utf-8")
installer = (ROOT / "install.sh").read_text(encoding="utf-8")
helper = (ROOT / "install-udev-rule.sh").read_text(encoding="utf-8")
diagnostics = (ROOT / "collect-diagnostics.sh").read_text(encoding="utf-8")

assert 'APP_VERSION = "3.4.29.6"' in code
assert 'BUILD_CHANNEL = "INTERN"' in code
assert 'APP_NAME = "Open Hardware Control"' in code
assert "from command_backend import Backend" in main_code
assert "from cooling_widgets import CurveEditor, FanCurveMiniPreview" in main_code
assert "from localization_catalog import (" in main_code
assert "_ABOUT_SUMMARY_TEXT," in main_code
assert "_GIF_SAFETY_TEXT," in main_code
assert "from privacy_logging import (" in main_code
assert "from temperature_utils import (" in main_code
assert "make_navigation_sidebar" in code
assert "update_navigation_visibility" in code
assert "Nicht erkannte Geräte/Module anzeigen" in code
assert "make_openlinkhub_tab" in code
assert "make_desktop_designs_tab" in code
assert '"experimental/desktop_designs_enabled", False' in code
assert "Experimentelle Desktop-Designs im Menü anzeigen" in code
assert "if not self.experimental_desktop_designs_enabled" in code
assert "make_rgb_tab" in code and "RGB-Studio" in code
assert 'f"Frelidon PC · Thermaltake / 360-mm-Aufbau / {layout_aio_name}"' in code
assert 'LEVITA_DISPLAY_NAME if self.is_thermalright_cooling() else "Kraken 360"' in code
assert '"Floris PC · Thermaltake / 360-mm-Aufbau / Kraken 360"' not in code
assert "fan_order_changed" in code and "reorder_rgb_layout_slot_devices" in code
assert "Kraken-Kanäle räumlich neu geordnet" in code
assert "refresh_rgb_studio" in code
assert "start_openrgb_effect" in code and "stop_openrgb_effect" in code
assert "RGB-Steuerung neu übernehmen" in code
assert 'self.backend.active_process_id_for("openrgb")' in code
assert "RGB-Fehler und Warnungen" in code
assert 'self.record_rgb_issue("FEHLER", description, details)' in code
assert '"RGB-Aktion teilweise fehlgeschlagen"' not in code
assert "Gewähltes Lichtmuster automatisch wieder anwenden" in code
assert "def monitor_rgb_ownership" in code and "def reinitialize_rgb_control" in code
assert "def request_rgb_direct_apply" in code and "def apply_pending_rgb_design" in code
assert "self.rgb_direct_apply_timer.setInterval(140)" in code
assert "def background_scan_rgb_inventory" in code
assert "self.rgb_inventory_timer.setInterval(60_000)" in code
assert "is_suspicious_inventory_drop" in code
assert "laufende Hardwareübertragung wird zuerst abgeschlossen" in code
assert "fremder lokaler SDK-Server antwortet weiterhin · keine Übernahme" in code
assert "Ein noch laufendes separates OpenRGB wird niemals beendet" in code
assert "rgbDesignStatusPanel" in code and "AKTUELL AUSGEWÄHLT" in code
assert "AKTIV BESTÄTIGT" in code and "set_active_index" in code
assert "Bisher besteht keine offizielle Unterstützung, Kooperation, Freigabe oder Verbindung" in code
assert "show_rgb_setup_wizard" in code and "RGB-EINRICHTUNGSASSISTENT STARTEN" in code
assert "Nur diese Zone" in code and "prepare_gpu_external_control" in code
assert "self.openrgb_effect_timer.setInterval(40)" in code
assert "openrgb_worker_frame_inflight" in code and "openrgb_worker_frame_pending" in code
assert "openrgb_worker_coalesced_frames" in code and "update_openrgb_performance_status" in code
assert '"--worker"' in code and "dauerhafter lokaler SDK-Worker" in code
assert "ensure_managed_rgb_engine" in code and "stop_managed_rgb_engine" in code
assert 'environment.insert("QT_QPA_PLATFORM", "offscreen")' in code
assert "openrgb_external_server_detected" in code
assert "RGBSessionLock" in code
assert "ApplicationInstanceLock" in code and "application-instance.lock" in code
assert "Der zweite Start wurde vor jedem Hardwarezugriff beendet" in code
run_application = code.index("def run_application")
instance_acquire = code.index("instance_lock.acquire()", run_application)
hardware_window = code.index("window = KrakenControl()", run_application)
assert instance_acquire < hardware_window
assert "class RGBDeviceTile" in code and "class RGBDropGroup" in code
assert "class PCLayoutDiagram" in code and "load_builtin_rgb_layout_profile" in code
assert "move_rgb_layout_slot" in code and "assign_rgb_device_to_layout_slot" in code
assert "select_rgb_layout_slot" in code and "rename_rgb_device" in code
assert "Thermaltake / 360-mm-Aufbau" in code
assert "rgb_reset_in_progress" in code and "rgb_engine_restart_pending" in code
assert "openrgb_discovery_generation" in code and "openrgb_write_enable_pending" in code
assert "if self.rgb_reset_in_progress or self.rgb_engine_disabled_by_reset" in code
assert "veraltetes Erkennungsergebnis" in code
assert "OpenRGB-Engine nicht erreichbar" in code
assert "Geräte-Testmodus" in code and "run_rgb_device_test" in code
assert "build_rgb_device_test_commands" in code and "rename_selected_rgb_test_device" in code
kraken_class = code.index("class KrakenControl")
kraken_init = code.index("    def __init__", kraken_class)
first_build_ui = code.index("        self.build_ui()", kraken_init)
preview_clock = code.index("        self.rgb_preview_started = time.monotonic()", kraken_init)
assert preview_clock < first_build_ui
assert 'if not hasattr(self, "rgb_preview_started")' in code
assert "install_application_exception_logging" in code
assert 'directory / "startup.log"' in code and 'directory / "last-crash.log"' in code
assert 'STATE_ROOT="${XDG_STATE_HOME:-$HOME/.local/state}/open-hardware-control"' in diagnostics
assert 'tail -n 120 "$STATE_ROOT/startup.log"' in diagnostics
assert 'cat "$STATE_ROOT/last-crash.log"' in diagnostics
assert "move_rgb_device_to_group" in code and "select_rgb_group" in code
assert "reset_all_rgb" in code and "RGB KOMPLETT ZURÜCKSETZEN" in code
assert "prepare_openrgb_devices" in code
assert 'OPENRGB_LOCAL_ADDRESS = "127.0.0.1"' in code
assert (ROOT / "openrgb_integration.py").exists()
assert (ROOT / "openrgb_sdk.py").exists()
sdk_code = (ROOT / "openrgb_sdk.py").read_text(encoding="utf-8")
assert "class OpenRGBPersistentSession" in sdk_code
assert "MAX_WORKER_REQUEST_SIZE = 2 * 1024 * 1024" in sdk_code
assert "MAX_WORKER_DEVICES = 64" in sdk_code
assert "def process_worker_frame" in sdk_code and "def run_worker" in sdk_code
assert "validate_loopback(address)" in sdk_code
assert (ROOT / "rgb_effects.py").exists()
assert (ROOT / "rgb_devices.py").exists()
assert (ROOT / "nzxt_rgb.py").exists()
assert (ROOT / "ui_layout.py").exists()
assert "class ReorderableSectionArea" in code
assert "Standardreihenfolge wiederherstellen" in code
assert '("engine", openrgb_box)' in code
assert 'editor_form.addRow("OHC-Modi", self.rgb_studio_mode_list)' in code
assert 'editor_form.addRow("Modusfarben", colors)' in code
assert "dashboard_fields_hidden" in code and "reset_dashboard_card_visibility" in code
sdk_code = (ROOT / "openrgb_sdk.py").read_text(encoding="utf-8")
assert "SDK_MIN_PROTOCOL_VERSION = 4" in sdk_code
assert "SDK_PROTOCOL_VERSION = 5" in sdk_code
assert "PACKET_UPDATE_ZONE_LEDS = 1051" in sdk_code
assert "PACKET_RESIZE_ZONE = 1000" in sdk_code
assert "KONFIGURATION_ERFORDERLICH" in sdk_code
assert "request_controller_data" in sdk_code and "hat die gesendeten Farben nicht bestätigt" in sdk_code
nzxt_code = (ROOT / "nzxt_rgb.py").read_text(encoding="utf-8")
assert '"comet": "pulse"' in nzxt_code and '"spinner": "rainbow-flow"' in nzxt_code
assert 'NZXTEffect("Marquee", "marquee-4"' not in nzxt_code
assert "coalesce_selected_channels" in nzxt_code
openrgb_code = (ROOT / "openrgb_integration.py").read_text(encoding="utf-8")
assert "color_commands" in openrgb_code and "best_native_mode_for_effect" in openrgb_code
assert "is_openrgb_apply_options_crash" in openrgb_code
assert "running_openrgb_process_ids" in openrgb_code
assert "OpenRGB-Mehrgerätebefehle sind deaktiviert" in openrgb_code
assert ".multi_color_command(" not in code
assert ".sdk_color_command(" in code
assert "LED-Zonen und Lüfter einrichten" in code
assert "normalize_zone_configurations" in code
assert "openrgb_quarantined_devices" in code and "quarantine_openrgb_device" in code
assert "openrgb_effect_failures_by_device" in code
assert "openrgb_process_check_at" in code and "separates OpenRGB gestartet" in code
assert "Befehlsfolge wird ohne" in code and "nächstes Gerät bleibt erreichbar" in code
assert "apply_desktop_design" in code
assert "restore_desktop_design" in code
assert "refresh_openlinkhub_status" in code
assert "class MacroRecorderDialog" in code
assert "edit_selected_openlinkhub_mouse_button" in code
assert "record_openlinkhub_keyboard_macro" in code
assert "on_temperature_unit_changed" in code
assert "hardware_label_color" in code and "hardware_value_color" in code
assert 'OPENLINKHUB_API_URL = "http://127.0.0.1:27003"' in code
assert (ROOT / "openlinkhub_integration.py").exists()
assert (ROOT / "OPENLINKHUB_INTEGRATION.md").exists()
assert (ROOT / "Open_Hardware_Control_Projekt.md").exists()
assert "class CurveEditor" in code
assert "class AnimatedBackgroundWidget" in code
assert "class SetupWizard" in code

assert 'scroll.setObjectName("settingsScrollArea")' in code
assert 'scroll.setWidgetResizable(True)' in code
assert 'scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)' in code
assert 'content.setMinimumWidth(820)' in code
assert 'migration/v292_settings_layout' in code
assert 'self.resize(1280, 880)' in code

assert "class InteractionAuditLogger" in code
assert "QImage.Format.Format_RGB32" in code
assert "WA_TransparentForMouseEvents" in code
assert "ensure_background_layer_order" in code
assert "self.background_widget.lower()" in code
assert "self.content_root.raise_()" in code
assert "content_rgba" in code
assert "QStackedLayout.StackingMode.StackAll" in code
assert "CPU-Offscreen-Renderer" in code
assert "save_application_log" in code
assert "self.log_char_limit = 10000" in code
assert "_trim_log_to_character_limit" in code
assert "app.installEventFilter(self._interaction_audit)" in code
assert "KLICK" in code and "ÄNDERUNG" in code and "NAVIGATION" in code
assert "PROFILES" not in code or "PROFILE_SCHEMA_VERSION" in code
assert "PROFILE_SCHEMA_VERSION = 1" in code
assert "make_profiles_tab" in code
assert "create_profile_from_current" in code
assert "export_selected_profile" in code
assert "import_profiles" in code
assert "apply_startup_profile" in code
assert "screen_summary" in code
assert "devicePixelRatio" in code
assert "21:9" in code and "32:9" in code
assert "DEFAULT_BACKGROUND_THEME" in code
assert "Sternenfeld" in code and "Kosmischer Nebel" in code and "Aurora" in code
assert "prozedural" in code.lower()
assert "Tab and Shift+Tab deliberately pass through" in code
assert "Ctrl+Shift+R" in code
assert "AM5_CPU_PROFILES" in code
assert "AMD Ryzen 7 9800X3D" in code
assert '"Ryzen 9000 X3D", 95' in code
assert '"Ryzen 7000 X3D", 89' in code
assert "read_amd_cpu_temperature" in code
assert 'def kraken_direct_args()' in code
assert '[LIQUIDCTL, "--direct-access", "--match", KRAKEN_MATCH]' in code
assert 'def update_cpu_curve_control' in code
assert 'def interpolate_curve' in code
assert 'def apply_cpu_curve_targets' in code
assert 'CPU_CURVE_SAMPLE_MS = 1000' in code
assert 'Pumpenkurve nach CPU-Temperatur' in code
assert 'Lüfterkurve nach CPU-Temperatur' in code
assert 'table.setHorizontalHeaderLabels([f"CPU {temperature_symbol(self.temperature_unit)}", "Leistung %"])' in code
assert 'restore_safe_hardware_fallback_sync_on_quit' in code
assert 'SAFE_HARDWARE_PUMP_CURVE' in code and 'SAFE_HARDWARE_FAN_CURVE' in code
assert 'KURVEN-MIGRATION 3.0.5' in code
sensor_code = (ROOT / "kraken_sensors.py").read_text(encoding="utf-8")
assert "k10temp" in sensor_code
assert "CPU-Tjmax" in code
assert "Kraken-Wassertemperatur" in code
assert "repair_permissions" in code
assert "show_permission_error" in code
assert "matching_hidraw_nodes" in code
assert 'SUBSYSTEM=="hidraw"' in rule
assert 'SUBSYSTEMS=="usb"' in rule
assert 'MODE="0660"' in rule
assert 'TAG+="uaccess"' in rule
assert "--subsystem-match=hidraw" in helper
assert "install-udev-rule.sh" in installer
assert "CPU_PROFILES.md" in installer
assert "COMPONENT_VERSIONS.md" in installer
assert "ANIMATED_BACKGROUNDS.md" in installer
assert "PROFILES.md" in installer
assert "FEATURES_BY_VERSION.md" in installer
assert "SOURCE_CODE.md" in installer
assert "Kraken_Control_Projekt.md" in installer
assert "USB_CAPTURE_FINDINGS.md" in installer
assert "kraken_cam_streamer.py" in installer
assert "kraken_lcd_designs.py" in installer
assert "kraken_sensors.py" in installer
assert "openlinkhub_integration.py" in installer
assert "openrgb_integration.py" in installer
assert "openrgb_sdk.py" in installer
assert "rgb_effects.py" in installer
assert "rgb_devices.py" in installer
assert "nzxt_rgb.py" in installer
assert "ui_layout.py" in installer
assert "desktop_designs.py" in installer
assert "desktop_assets.py" in installer
assert "desktop_shell.py" in installer
assert "DESKTOP_DESIGNS.md" in installer
assert "Open_Hardware_Control_Projekt.md" in installer
assert "OPENLINKHUB_INTEGRATION.md" in installer
assert (ROOT / "kraken_lcd_designs.py").exists()
assert (ROOT / "kraken_sensors.py").exists()
assert (ROOT / "desktop_designs.py").exists()
assert (ROOT / "desktop_assets.py").exists()
assert (ROOT / "desktop_shell.py").exists()
assert (ROOT / "assets" / "desktop-designs" / "windows11-wallpaper.svg").exists()
assert (ROOT / "assets" / "desktop-designs" / "macos-wallpaper.svg").exists()
assert (ROOT / "assets" / "desktop-designs" / "windows8-wallpaper.svg").exists()
assert (ROOT / "assets" / "desktop-designs" / "windows81-wallpaper.svg").exists()
assert (ROOT / "assets" / "desktop-designs" / "kwin" / "ohc-charms" / "contents" / "code" / "main.js").exists()
assert (ROOT / "CPU_PROFILES.md").exists()
assert (ROOT / "COMPONENT_VERSIONS.md").exists()
assert (ROOT / "ANIMATED_BACKGROUNDS.md").exists()
assert (ROOT / "PROFILES.md").exists()
assert (ROOT / "FEATURES_BY_VERSION.md").exists()
assert (ROOT / "SOURCE_CODE.md").exists()
assert (ROOT / "Kraken_Control_Projekt.md").exists()
assert (ROOT / "USB_CAPTURE_FINDINGS.md").exists()
assert (ROOT / "tools" / "analyze_usbpcap.py").exists()

assert "toggle_expert_mode" in code
assert "configure_expert_mode_controls" in code
assert "Aktiver Kühlmodus" in code
assert "set_cooling_mode" in code
assert "clock_auto_resend" in code
assert "send_clock_keepalive" in code

assert (ROOT / "install-dependencies.sh").exists()
dep_helper = (ROOT / "install-dependencies.sh").read_text(encoding="utf-8")
assert "python3-pyside6" in dep_helper
assert "python3-pillow" in dep_helper
assert "qt6-qtsvg" in dep_helper
assert "dnf:qdbus6" in dep_helper and 'echo "qt6-qttools"' in dep_helper
assert "dnf:kconfig6" in dep_helper and 'echo "kf6-kconfig"' in dep_helper
assert "apt:qdbus6" in dep_helper and 'echo "qdbus-qt6"' in dep_helper
assert "pacman:qdbus6" in dep_helper and 'echo "qt6-tools"' in dep_helper
assert "zypper:qdbus6" in dep_helper and 'echo "qt6-tools-qdbus"' in dep_helper
assert "--check-desktop" in dep_helper and "--install-desktop" in dep_helper
assert "--check-openrgb" in dep_helper and "--install-openrgb" in dep_helper
assert "dnf:openrgb_udev" in dep_helper and 'echo "openrgb-udev-rules"' in dep_helper
assert "liquidctl" in dep_helper
assert "pkexec" in dep_helper
assert "install-dependencies.sh" in installer
assert 'hardware_request_coordinator.py' in installer
assert 'mainboard_fan_control.py' in installer
assert 'nzxt_esc_profiles.py' in installer
build_release_code = (ROOT / "scripts/build_release.py").read_text(encoding="utf-8")
assert 'os.environ.get("OHC_SKIP_DEB") == "1"' in build_release_code
assert '"_buildhost open-hardware-control.invalid"' in build_release_code
assert 'filter=anonymize_tar_metadata' in build_release_code
assert 'info.mtime = ARCHIVE_MTIME' in build_release_code
assert 'Skipping DEB build because dpkg-deb is unavailable on this system' in build_release_code
assert 'info.uname = "root"' in build_release_code
rpm_fallback_code = (ROOT / "scripts/build_rpm_fallback.py").read_text(encoding="utf-8")
assert 'usr/libexec/open-hardware-control-fan-helper' in rpm_fallback_code
assert 'usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.fan.policy' in rpm_fallback_code
assert '"hardware_request_coordinator.py"' in build_release_code
assert '"mainboard_fan_control.py"' in build_release_code
assert '"ohc_fan_helper.py"' in build_release_code
assert '"io.github.Frelidon.OpenHardwareControl.fan.policy"' in build_release_code
assert '"nzxt_esc_profiles.py"' in build_release_code
assert "--check-gui-and-install" in installer
assert "install_missing_dependencies" in code
assert "install_desktop_design_dependencies" in code
assert "maybe_offer_desktop_design_dependencies" in code
assert "Fehlende Pakete &installieren" in code

readme = (ROOT / "README.md").read_text(encoding="utf-8")
assert "# Open Hardware Control by Frelidon 3.4.29.6 INTERN" in readme
assert "Inoffizielles unabhängiges Community-Projekt" in readme
assert "Corsair · OpenLinkHub" in readme
assert "| NZXT 2023 RGB Controller | `1e71:2012`" in readme


# 3.4.23: motherboard fan control must stay calibration-gated and use hwmon only.
mainboard_code = (ROOT / "mainboard_fan_control.py").read_text(encoding="utf-8")
assert "discover_hwmon_controllers" in mainboard_code
assert "set_channel_percent" in mainboard_code
assert "restore_firmware_control" in mainboard_code
assert "decide_curve_output" in mainboard_code
assert "msi_fan_brute_force=1" in mainboard_code
assert "fan_control_watchdog" in mainboard_code
assert "set_fan_control_watchdog" in mainboard_code
assert "channel_can_control" in mainboard_code
assert "DEFAULT_FAN_HELPER" in mainboard_code
assert "/dev/port" not in mainboard_code
assert "i2c_smbus" not in mainboard_code
assert "Kanal sicher testen · 70 % / 10 s" in code
assert "automatische Regelung bleibt gesperrt" in code
assert "ENE-RAM erneut initialisieren" in code
assert "manual_reinitialize_ene_dram" in code
fan_helper = (ROOT / "ohc_fan_helper.py").read_text(encoding="utf-8")
fan_policy = (ROOT / "io.github.Frelidon.OpenHardwareControl.fan.policy").read_text(encoding="utf-8")
assert 'HWMON_ROOT = Path("/sys/class/hwmon")' in fan_helper
assert 'MAX_CHANNEL = 8' in fan_helper
assert 'subprocess' not in fan_helper
assert 'os.system' not in fan_helper
assert 'shell=True' not in fan_helper
assert 'org.freedesktop.policykit.exec.path' in fan_policy
assert '/usr/libexec/open-hardware-control-fan-helper' in fan_policy
assert 'op == "session"' in fan_helper
assert "len(raw_line) > 512" in fan_helper
assert "dispatch(controller(), request)" in fan_helper
assert "PrivilegedFanHelperSession" in mainboard_code
assert '[str(DEFAULT_PKEXEC), str(DEFAULT_FAN_HELPER), "session"]' in mainboard_code
assert "stop_privileged_fan_helper_session" in mainboard_code
assert "allow_active" in fan_policy and "auth_admin_keep" in fan_policy

print("Static release checks passed.")

# 2.9.6 regression: disabling must preserve the last animation theme.
assert 'def on_background_enabled_toggled' in code
assert 'self.background_last_theme' in code
segment = code[code.index('def disable_background'):code.index('def sync_design_controls')]
assert 'self.background_theme_combo.setCurrentText("Aus")' not in segment

# 2.9.6: all cooling writes use direct access and background permission errors stay non-modal.
assert 'Backend.kraken_direct_args() + ["set", channel, "speed", str(duty)]' in code
assert code.count('Backend.kraken_direct_args() + ["set", "pump", "speed", str(pump)]') >= 1
assert code.count('Backend.kraken_direct_args() + ["set", "fan", "speed", str(fan)]') >= 1
assert "foreground = self.isVisible() and self.isActiveWindow()" in code
assert "permission_retry_after" in code

# 2.9.6 regression: LCD clock start must use the current clock_format combo box.
assert "self.clock_24h" not in code
assert 'str(self.clock_format.currentData()) == "24"' in code
assert "LCD-UHR: gestartet" in code
assert "LCD-UHR: Bild erfolgreich übertragen" in code


# 2.9.7 internal: persistent LCD acknowledgement, crash recovery and first localization stage.
assert 'SUPPORTED_UI_LANGUAGES = {"de": "Deutsch", "en": "English", "es": "Español", "fr": "Français"}' in code
assert 'def capture_translation_sources' in code
assert 'def apply_ui_language' in code
assert 'self.settings.setValue("ui/language", language)' in code
assert 'Experimentalhinweise zurücksetzen' in code
assert 'clock/experimental_warning_ack' in code
assert 'lcd/keepalive_warning_ack' in code
assert 'lcd/experimental_session_active' in code
assert 'lcd/recovery_required' in code
assert 'def activate_lcd_safe_mode' in code
assert 'def record_lcd_failure' in code
assert 'LCD_FAILURE_LIMIT = 3' in code
assert 'set", "lcd", "screen", "liquid"' in code
assert 'Unsauber beendete experimentelle LCD-Sitzung erkannt' in code
assert 'LCD-Bild-Fallback' in code
assert 'self.setWindowTitle(f"{DISPLAY_NAME} {APP_DISPLAY_VERSION} — Linux")' in code
assert 'experimental_autostart_blocked' in code


# 2.9.8+ internal: GIF helper, LCD safety coordination and minimized autostart.
assert 'GIF_HELPER_NAME = "kraken_cam_streamer.py"' in code
assert 'def start_gif_stream' in code
assert 'def stop_gif_stream' in code
assert 'gif/experimental_warning_ack' in code
assert '"layers" if self.lcd_layer_active else "hardware_animation" if self.gif_generated_hardware_mode else "imported_profile" if self.gif_imported_profile_mode else "gif"' in code
assert 'def render_lcd_layer_file' in code
assert 'def start_lcd_layers' in code
assert 'class RGBDesignGallery' in code
assert 'studio_autostart_enabled' in code
assert 'gif/fps' in code
assert 'Beim Systemstart minimiert/im Tray starten' in code
assert '"--autostart" in sys.argv' in code
assert 'exec_line += " --autostart"' in code
assert 'def should_start_minimized_from_autostart' in code
assert 'window.apply_initial_window_state()' in code
assert 'AUTOSTART_LCD_DELAY_MS = 5000' in code
assert '"mode": self.current_lcd_profile_mode()' in code
assert 'def resolve_profile_lcd_mode' in code
assert 'self.apply_profile_by_id(profile_id, startup=True)' in code
assert 'if not (startup and self.should_start_minimized_from_autostart())' in code
assert 'QTimer.singleShot(0, self.apply_initial_window_state)' in code
assert 'install_session_signal_handlers(window)' in code
assert 'gif_force_stop_timer' in code
assert 'Bewegungsglättung (Motion-Interpolation)' in code
assert 'for fps in (5, 8, 10, 12, 15, 20)' in code
assert 'CAM-nah · automatisch · empfohlen · max. 25 FPS' in code
assert 'Erweiterte GIF-Optionen anzeigen' in code
assert 'gif/show_advanced' in code
assert 'test-gifs' in installer
assert (ROOT / 'test-gifs' / '02_moving-bars_27fps.gif').exists()
assert (ROOT / 'tools' / 'generate_test_gifs.py').exists()

# 2.9.15 internal: replace 30/32-Hz experiments with CAM-near raw FW2 transport.
helper_code = (ROOT / "kraken_cam_streamer.py").read_text(encoding="utf-8")
assert 'CAM_TRANSPORT_FPS = 80.0 / 3.0' in helper_code
assert 'SAFE_TRANSPORT_FPS = 25.6' in helper_code
assert 'RGB565_FRAME_BYTES = LCD_SIZE[0] * LCD_SIZE[1] * 2' in helper_code
assert 'class CamRawTransport' in helper_code
assert 'START = [0x36, 0x01, 0x00, 0x01, 0x06]' in helper_code
assert 'END = [0x36, 0x02]' in helper_code
assert 'HEADER_PREFIX = [0x12, 0xFA' in helper_code
assert 'self.bulk_write(data)' in helper_code
assert 'estimate_global_motion' in helper_code
assert 'motion_interpolate' in helper_code
assert 'motion-compensated-global' in helper_code
assert 'Image.blend' in helper_code  # only fallback/merge after motion compensation
assert 'time.monotonic()' in helper_code
assert 'choices=("cam", "safe")' in helper_code
assert 'TRANSPORT_MODES = {' in helper_code
assert '"cam": CAM_TRANSPORT_FPS' in helper_code
assert '"safe": SAFE_TRANSPORT_FPS' in helper_code
assert '30 Hz · Smooth · mehr Zwischenbilder' not in code
assert '32 Hz · Experimental · höchste Glättung' not in code
assert 'CAM-Takt · 26,667 Hz · phasenstabil · Standard' in code
assert 'gif/transport_mode' in code
assert '"--transport", transport_mode' in code
assert 'LCD-Frame-Wiederholungen' in code
assert 'LCD-Frame-Sprünge' in code
assert 'P90' in code
assert 'startup_profile_owns_lcd' in code
assert 'clock_last_minute_upload_key' in code
assert 'def update_clock_lcd(self, force: bool = False)' in code
assert not (ROOT / 'kraken_gif_streamer.py').exists()
assert not (ROOT / 'test-gifs' / '02_moving-bars_30fps.gif').exists()
assert not (ROOT / 'test-gifs' / '02_moving-bars_32fps.gif').exists()

print("2.9.15 CAM-raw static checks passed.")

# 2.9.20 internal: exclusive Kraken ownership, matched ACKs and phase-stable playback.
assert 'GIF_STREAM_START_WAIT_SECONDS = 15.0' in code
assert 'GIF_STREAM_WATCHDOG_SECONDS = 12.0' in code
assert 'def is_idle(self)' in code
assert 'def pause_kraken_io_for_gif' in code
assert 'def resume_kraken_io_after_gif' in code
assert 'def kraken_command_blocked_by_gif' in code
assert 'def check_gif_stream_watchdog' in code
assert 'self.status_timer.stop()' in code
assert 'CPU-Kurven lesen Linux-hwmon weiter' in code
assert 'self.gif_process.terminate()' in code
assert 'HID_RESPONSE_READ_ATTEMPTS = 12' in helper_code
assert 'clear_enqueued_reports' in helper_code
assert '_command_with_matching_reply' in helper_code
assert 'expected = bytes(((data[0] + 1) & 0xFF, data[1]))' in helper_code
assert 'unrelated_hid_reports' in helper_code
assert 'ack_matching=True' in helper_code
assert 'CAM_ACK_GUARD_S = 0.0001' in helper_code
assert 'SAFE_DISPLAY_GUARD_S = 0.0002' in helper_code
assert 'next_phase_locked_start' in helper_code
assert 'MAX_PHASE_CORRECTION_STEP_S = 0.00025' in helper_code
assert 'lcd_index = (transport_frames + 1) % len(frames)' in helper_code
assert 'cam-raw-26.667hz-phase-locked' in helper_code
assert 'loop_transition_diagnostics' in helper_code
assert 'Der Loop dieser GIF-Datei enthält wahrscheinlich einen sichtbaren Übergang.' in code

print("2.9.20 exclusive matched-ACK/watchdog, phase-lock and loop-warning checks passed.")

# 2.9.21: rounded hardware dashboards, dGPU sensing and complete live i18n switching.
assert 'from kraken_lcd_designs import' in code
assert 'def read_amd_gpu_temperature' in code
assert 'mem_info_vram_total' in sensor_code
assert 'Hardwaredaten-Designs · Live' in code
assert 'hardware_lcd/active' in code
assert 'hardware_lcd/experimental_warning_ack' in code
assert 'mark_experimental_lcd_active("hardware")' in code
assert 'def refresh_dynamic_translations' in code
assert 'for menu in self.findChildren(QMenu)' in code
assert code.index('self.restore_settings()') < code.index('self.capture_translation_sources()', code.index('self.restore_settings()'))
for language in ('en', 'es', 'fr'):
    assert f'UI_TRANSLATIONS["{language}"].update' in code
assert 'DEFAULT_ACCENT = "#00c8ff"' in (ROOT / "kraken_lcd_designs.py").read_text(encoding="utf-8")

# 2.9.22: scalable text and generated animated sensor dashboards.
design_code = (ROOT / "kraken_lcd_designs.py").read_text(encoding="utf-8")
assert 'def render_hardware_animation' in design_code
assert 'font_scale_percent' in design_code
assert 'phase=index / frame_count' in design_code
assert 'Schrift- und Zahlen-Größe' in code
assert 'Animierte Hardwaredaten · Ringe und Orbits' in code
assert 'def start_hardware_animation' in code
assert 'generated_hardware=True' in code
assert '"layers" if self.lcd_layer_active else "hardware_animation" if self.gif_generated_hardware_mode else "imported_profile" if self.gif_imported_profile_mode else "gif"' in code
assert 'hardware_animation/experimental_warning_ack' in code

# 2.9.23: CPU/GPU values refresh out-of-process while liquid stays the last safe Kraken value.
assert 'self.hardware_animation_spec_file' in code
assert '"--hardware-spec", str(self.hardware_animation_spec_file)' in code
assert 'CPU/GPU live · Wasser letzter sicherer Wert' in code
assert 'sensor_update' in code and 'sensor_update_error' in code
assert 'HARDWARE_SENSOR_INTERVAL_S = 2.0' in helper_code
assert 'ProcessPoolExecutor' in helper_code
assert 'multiprocessing.get_context("spawn")' in helper_code
assert 'def prepare_hardware_animation' in helper_code
assert 'def render_hardware_cache_worker' in helper_code
assert 'def frames_from_cache_file' in helper_code
assert 'read_amd_cpu_temperature' in helper_code and 'read_amd_gpu_temperature' in helper_code
assert 'live_sensor_status=True' in helper_code

# 3.0.1: coordinated cached-stream USB handoff for manual cooling writes.
assert 'def defer_cooling_action_for_gif' in code
assert 'def begin_deferred_gif_cooling_action' in code
assert 'def finish_gif_cooling_when_idle' in code
assert 'def complete_gif_cooling_transaction' in code
assert 'self.gif_process.write(b"PAUSE\\n")' in code
assert 'self.gif_process.write(b"RESUME\\n")' in code
assert 'elif kind == "paused"' in code
assert 'elif kind == "resumed"' in code
assert 'def read_control_command' in helper_code
assert 'command in {"STOP", "PAUSE", "RESUME"}' in helper_code
assert 'device_stack.close()' in helper_code
assert '"paused"' in helper_code and '"resumed"' in helper_code
assert (ROOT / "tests" / "test_gif_cooling_handoff.py").exists()

# 3.0.2: explicit per-channel switch between fixed/manual and hardware curve mode.
assert 'Betriebsart umschalten' in code
assert 'Manuell aktivieren' in code
assert 'Pumpenkurve aktivieren' in code
assert 'Lüfterkurve aktivieren' in code
assert 'button.setObjectName("coolingModeButton")' in code
assert 'def cooling_mode_kind' in code
assert 'def switch_cooling_mode' in code
assert 'def update_cooling_mode_buttons' in code
assert 'self.set_fixed_speed(channel, slider.value())' in code
assert 'self.apply_curve(channel, curve_table)' in code

# 3.0.3: stable active-mode colour without transient Qt check-state flicker.
assert 'button.setProperty("coolingState", "inactive")' in code
cooling_button_start = code.index('button.setObjectName("coolingModeButton")')
cooling_button_end = code.index("switch_hint = QLabel", cooling_button_start)
assert 'button.setCheckable(True)' not in code[cooling_button_start:cooling_button_end]
assert 'QPushButton#coolingModeButton[coolingState="active"]' in code
assert 'button.style().unpolish(button)' in code
assert 'button.style().polish(button)' in code

# 3.0.4: allow-listed, session-gated OpenLinkHub device writes.
openlink_code = (ROOT / "openlinkhub_integration.py").read_text(encoding="utf-8")
assert 'WRITE_ENDPOINTS = {' in openlink_code
assert 'def validate_write_payload' in openlink_code
assert 'def run_write_action' in openlink_code
assert 'def _resolve_device_id' in openlink_code
assert 'hashlib.sha256' in openlink_code
assert '"speed-manual": ("POST", "/api/speed/manual")' in openlink_code
assert '"rgb-profile": ("POST", "/api/color")' in openlink_code
assert '"mouse-dpi": ("POST", "/api/mouse/dpi")' in openlink_code
assert '"mouse-key-assignment": ("POST", "/api/mouse/updateKeyAssignment")' in openlink_code
assert '"macro-create-recording": ("MULTI", "/api/macro/new")' in openlink_code
assert '"headset-anc": ("POST", "/api/headset/anc")' in openlink_code
assert '"keyboard-layout": ("POST", "/api/keyboard/layout")' in openlink_code
assert 'Direkte OpenLinkHub-Schreibzugriffe für diese Programmsitzung aktivieren' in code
assert 'def run_openlinkhub_write' in code
assert 'log_command=False' in code

# 3.0.9: orderly LCD reset and original interactive mouse schematics.
assert 'def restore_original_lcd_sync_on_quit' in code
assert code.count('self.restore_original_lcd_sync_on_quit()') == 1
assert 'self.perform_orderly_hardware_exit("Fenster/Programmende")' in code
assert 'self.perform_orderly_hardware_exit("manuelles Programmende")' in code
assert 'self.perform_orderly_hardware_exit("System-Shutdown/Logout")' in code
assert 'app.aboutToQuit.connect(lambda: window.perform_orderly_hardware_exit("Qt aboutToQuit"))' in code
assert 'Backend.kraken_args() + ["set", "lcd", "screen", "liquid"]' in code
assert code.index('self.shutdown_gif_stream_sync()') < code.index('self.restore_original_lcd_sync_on_quit()')
assert 'class MouseSchematicWidget' in code
assert 'Grafische Tastenbelegung' in code
assert 'def update_openlinkhub_mouse_visual' in code
assert 'openlinkhub_mouse_visuals.py' in installer
assert 'SOURCE_DIR/assets' in installer
mouse_visuals = (ROOT / 'openlinkhub_mouse_visuals.py').read_text(encoding='utf-8')
assert 'def classify_mouse_layout' in mouse_visuals
assert 'def visual_button_rows' in mouse_visuals
assert 'def _mouse_assignments' in openlink_code
for asset in ('mouse-compact.svg', 'mouse-ergonomic.svg', 'mouse-symmetric.svg', 'mouse-multi.svg', 'mouse-mmo.svg'):
    assert (ROOT / 'assets' / asset).exists()

# 3.0.9: verified mouse assignments/macros and complete temperature presentation.
assert 'class MacroRecorderDialog' in code
assert 'def edit_selected_openlinkhub_mouse_button' in code
assert 'def record_openlinkhub_keyboard_macro' in code
assert '"mouse-key-assignment": ("POST", "/api/mouse/updateKeyAssignment")' in openlink_code
assert '"macro-create-recording": ("MULTI", "/api/macro/new")' in openlink_code
assert '"macroType": 3' in openlink_code and '"macroType": 5' in openlink_code
assert 'display/temperature_unit' in code
assert 'def celsius_to_display' in code and 'def display_to_celsius' in code
assert 'hardware_lcd/label_color' in code and 'hardware_lcd/value_color' in code
assert 'hardware_lcd/label_scale' in code and 'hardware_lcd/value_scale' in code

# 3.4.23: consolidated LCD/help/setup plus one-shot ENE-DRAM priming.
openrgb_sdk_code = (ROOT / "openrgb_sdk.py").read_text(encoding="utf-8")
assert 'if set_custom_mode or not controller.direct_active:' in openrgb_sdk_code
assert 'custom_changed = False' in openrgb_sdk_code
assert '"LCD-Einstellungen",' in code
assert 'def write_hardware_animation_spec' in code
assert 'def write_lcd_layer_spec' in code
assert 'source_missing = (not self.gif_generated_hardware_mode and not self.gif_imported_profile_mode)' in code
assert code.count('source_path=None') >= 2
assert 'self.lcd_tile_area = ReorderableTileArea(' in code
assert '("preview", preview_box, 1)' in code
assert '("display", display_box, 1)' in code
assert '("clock", clock_box, 1)' in code
assert '("content", image_box, 3)' in code
assert 'lcd/tile_order' in code
assert 'Uhr zusätzlich einblenden' in code
assert 'def open_help_center' in code
assert 'Sprache / Language / Idioma / Langue' in code
assert (ROOT / "io.github.Frelidon.OpenHardwareControl.metainfo.xml").exists()
