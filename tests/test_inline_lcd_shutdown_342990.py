"""Actual hardware-free window, inline inspector, bounded cards and tray exit."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def exercise():
    with tempfile.TemporaryDirectory(prefix="ohc-inline-idle-exit-") as temporary:
        task_root = Path(temporary)
        for key, folder in (("XDG_CONFIG_HOME", "config"), ("XDG_STATE_HOME", "state"),
                            ("XDG_CACHE_HOME", "cache"), ("OHC_DESKTOP_DESIGN_CONFIG_DIR", "desktop"),
                            ("OHC_DESKTOP_DESIGN_STATE_DIR", "desktop-state")):
            os.environ[key] = str(task_root / folder)
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["OHC_DISABLE_HARDWARE_IO"] = "1"
        sys.path.insert(0, str(ROOT / "src"))
        from PySide6.QtCore import QCoreApplication, QEvent, QPoint, QProcess, QTimer, QVariantAnimation, Qt
        from PySide6.QtGui import QImage
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication, QComboBox, QSpinBox
        import kraken_control as application
        from localization_catalog import UI_TRANSLATIONS
        from thermalright_display import MediaEntry
        from openrgb_integration import OpenRGBDevice
        from modules.rgb_studio.v1_15.argb_controls import edit_slot_header
        from modules.rgb_studio.v1_15.gpu_led_editor import configure_argb_header
        from modules.pc_case_profiles.v1_5.case_page import build_slot_pwm_button
        application.KrakenControl.check_dependencies = lambda self: ["no-hardware-ui-test"]
        app = QApplication([])
        app.setQuitOnLastWindowClosed(False)
        window = application.KrakenControl()
        errors = []
        window.show_error = errors.append  # Fail below, never hang a test in a native error dialog.
        from rgb_devices import flori_rgb_layout_profile, RGBGroup
        window.rgb_groups = [RGBGroup("test-fans", "Test Fans")]
        _, window.rgb_layout_slots = flori_rgb_layout_profile("thermalright")
        window.refresh_rgb_layout_editor()
        window.settings.setValue("setup/completed", True)
        window.settings.setValue("dependencies/desktop_design_offer_330", True)
        window.resize(1600, 1000)
        window.tabs.setCurrentIndex(window.case_page_index)
        window.show()
        app.processEvents()
        slot = next(slot for slot in window.rgb_layout_slots if slot.position in {"front", "side", "rear", "bottom"})
        key = slot.slot_id or slot.position
        window.focus_rgb_layout_slot(key)
        window.edit_selected_rgb_layout_slot()
        inspector = window.case_inspector
        form = inspector.active_dialog
        assert form is not None and not form.isWindow() and not form.isModal()
        assert form.parentWidget() is not window
        assert inspector.isVisible()
        scale = form.findChild(QSpinBox, "caseSlotScale")
        scale.setValue(25)
        form.reject()
        assert next(s for s in window.rgb_layout_slots if (s.slot_id or s.position) == key).scale == slot.scale
        assert inspector.isHidden()
        for language in ("de", "en", "es", "fr"):
            window.apply_ui_language(language, log_change=False)
            window.edit_selected_rgb_layout_slot()
            form = inspector.active_dialog
            assert form is not None and not form.isWindow()
            assert inspector.title.text() == window.tr_static("Lüfter-/Komponentenblock bearbeiten") + " · " + slot.name
            position = next(combo for combo in form.findChildren(QComboBox) if combo.findData("front") >= 0)
            assert position.itemText(position.findData("front")) == window.tr_static("Front")
            # Live language changes preserve unsaved field values and data IDs.
            form.findChild(QSpinBox, "caseSlotScale").setValue(35)
            window.apply_ui_language("en", log_change=False)
            assert inspector.title.text() == window.tr_static("Lüfter-/Komponentenblock bearbeiten") + " · " + slot.name
            assert form.findChild(QSpinBox, "caseSlotScale").value() == 35
            assert position.itemText(position.findData("rear")) == UI_TRANSLATIONS["en"]["Heck"]
            render = os.environ.get("OHC_UI_RENDER_DIR")
            if render and language in {"de", "fr"}:
                window.apply_ui_language(language, log_change=False)
                app.processEvents()
                output = Path(render); output.mkdir(parents=True, exist_ok=True)
                assert window.grab().save(str(output / f"case-inline-{language}.png"))
            form.reject()
        window.edit_selected_rgb_layout_slot()
        inspector.active_dialog.findChild(QSpinBox, "caseSlotScale").setValue(40)
        inspector.active_dialog.accept()
        assert next(s for s in window.rgb_layout_slots if (s.slot_id or s.position) == key).scale == .4
        edit_slot_header(window, key)
        assert inspector.active_dialog is not None and not inspector.active_dialog.isWindow()
        assert inspector.active_dialog.findChild(QComboBox, "slotArgbController") is not None
        inspector.dismiss()
        build_slot_pwm_button(window, key).click()
        assert inspector.active_dialog.findChild(QComboBox, "caseInlinePwm") is not None
        QTest.mouseClick(window.rgb_layout_diagram, Qt.MouseButton.LeftButton, pos=QPoint(3, 3))
        # Outside clicks must not discard an unfinished component assignment.
        assert inspector.isVisible()
        inspector.dismiss()
        source = OpenRGBDevice(3, "Synthetic motherboard", device_type="Motherboard", modes=("Direct",), zones=("JARGB 1",))
        window.openrgb_devices = [source]; window.openrgb_stable_ids = {3: "synthetic:board"}
        window.openrgb_server_reachable = True
        window.openrgb_external_server_detected = False  # Synthetic engine belongs to this test.
        window.openrgb_device_conflict = lambda _device: False
        original_backend = window.backend
        original_run_async = original_backend.run_async
        original_client = window.openrgb_client
        callbacks = []
        from types import SimpleNamespace
        window.openrgb_client = SimpleNamespace(sdk_inspect_command=lambda index: ["synthetic-inspect", str(index)])
        window.backend.run_async = lambda _command, **kw: callbacks.append(kw["callback"])
        configure_argb_header(window, source, "JARGB 1")
        assert callbacks and inspector.isVisible()
        inspector.dismiss()
        callbacks.pop()(SimpleNamespace(ok=True, stdout=json.dumps({"zones": []})))
        assert inspector.isHidden() and inspector.active_dialog is None
        window.backend.run_async = original_run_async
        window.openrgb_client = original_client
        window.openrgb_server_reachable = False
        window.openrgb_devices = []; window.openrgb_stable_ids = {}
        window.tabs.setCurrentIndex(3)  # Stable Display & Layout page ID.
        studio = window.thermalright_display_studio
        picture = task_root / "small.png"
        image = QImage(32, 32, QImage.Format.Format_RGB32); image.fill(0xff123456)
        assert image.save(str(picture))
        entries = [MediaEntry(picture, "small.png", "image")]
        studio._rebuild_media_cards(entries)
        window.tabs.setCurrentIndex(window.case_page_index)
        preparation = studio.gallery_preparation
        preparation.last_input = time.monotonic()
        preparation.advance()
        assert not studio._media_cards_materialized
        preparation.last_input -= 4
        before = len(studio.media_card_buttons) + len(studio.hardware_card_buttons)
        preparation.advance()
        assert len(studio.media_card_buttons) + len(studio.hardware_card_buttons) - before <= 4
        deadline = time.monotonic() + 3
        while not studio._media_cards_materialized and time.monotonic() < deadline:
            app.processEvents()
        assert studio._media_cards_materialized and not studio.isVisible()
        assert not studio.layer2_motion_timer.isActive() and not studio.hover_preview_timer.isActive()
        assert not studio.thumbnail_active
        # The live content page owns transitions; the navigation stays still.
        controller = window.ui_performance
        for _ in range(25): controller.play(window.tabs.currentWidget())
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        assert window.navigation.viewport() not in controller.overlays
        assert window.tabs.currentWidget() in controller.overlays
        assert all(overlay.parentWidget() is page for page, overlay in controller.overlays.items())
        assert len(controller.findChildren(QVariantAnimation)) <= 1
        controller.cache_worker.start(sys.executable, ["-c", "import sys; sys.stdin.read()"])
        assert controller.cache_worker.waitForStarted(1000)
        # Empty owned channel inventory makes actual exit restore hardware-free.
        window.mainboard_channels = {}
        window.mainboard_control_active = True
        window.mainboard_startup_pending = False
        app.aboutToQuit.connect(lambda: window.perform_orderly_hardware_exit("test aboutToQuit"))
        app.aboutToQuit.connect(window.backend.shutdown)
        watchdog = QTimer(); watchdog.setSingleShot(True)
        watchdog.timeout.connect(lambda: app.exit(23)); watchdog.start(6000)
        QTimer.singleShot(0, window.tray_quit_action.trigger)
        started = time.monotonic()
        result = app.exec()
        assert result == 0, "explicit tray quit did not exit the real Qt loop"
        assert window.explicit_quit_requested and window.exit_hardware_cleanup_done
        assert not window.tray_quit_action.isEnabled()
        assert window.settings.value("mainboard_fans/master_enabled", False, type=bool)
        assert not preparation.timer.isActive()
        assert controller.cache_worker.state() == QProcess.ProcessState.NotRunning
        assert controller.closing and not controller.maintenance_timer.isActive()
        assert not errors, errors
        assert time.monotonic() - started < 6
        print("inline/localization/idle/navigation/actual-tray-exit: passed", flush=True)


def test_real_window_inline_idle_and_tray_exit():
    completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child"], cwd=ROOT,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True,
                               text=True, timeout=20)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "actual-tray-exit: passed" in completed.stdout


if __name__ == "__main__" and "--child" in sys.argv: exercise()
