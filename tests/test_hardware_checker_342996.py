#!/usr/bin/env python3
"""Hardware Checker 1.0 pure parser and safety regressions."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.hardware_checker.v1_0.model import (  # noqa: E402
    assess_memory, assess_nvme_link, assess_pcie_link, parse_dmidecode_memory,
    pcie_generation,
)
from modules.hardware_checker.v1_0.probe import _friendly_pci_name, cpu_info  # noqa: E402
from modules.hardware_checker.v1_0.page import gpu_load_command  # noqa: E402


def _link(current_speed="32.0 GT/s PCIe", current_width=16, max_speed="32.0 GT/s PCIe", max_width=16):
    return {
        "current_speed": current_speed, "current_width": current_width,
        "max_speed": max_speed, "max_width": max_width,
    }


def test_pcie_generation_and_idle_downshift_are_not_false_failures() -> None:
    assert pcie_generation("32.0 GT/s PCIe") == 5
    idle = assess_pcie_link(_link(current_speed="2.5 GT/s PCIe", current_width=1))
    assert idle.state == "warning"
    loaded = assess_pcie_link(_link(current_speed="16.0 GT/s PCIe", current_width=8), under_load=True)
    assert loaded.state == "fail"
    assert assess_pcie_link(_link()).state == "pass"


def test_pci_display_name_omits_duplicated_bus_and_numeric_id() -> None:
    raw = "0000:03:00.0 VGA compatible controller [0300]: AMD Navi 48 [1002:7550] (rev c0)"
    assert _friendly_pci_name(raw) == "AMD Navi 48"


def test_nvme_lane_shortfall_is_visible_without_writing_a_benchmark() -> None:
    assessment = assess_nvme_link(_link(current_speed="8.0 GT/s PCIe", current_width=2, max_speed="8.0 GT/s PCIe", max_width=4))
    assert assessment.state == "fail"
    assert "Lanes" in assessment.detail


def test_dmidecode_parser_omits_serials_and_assesses_manual_target() -> None:
    raw = """
Memory Device
        Size: 16 GB
        Locator: DIMMA2
        Type: DDR5
        Speed: 6000 MT/s
        Manufacturer: Kingston
        Serial Number: PRIVATE-SERIAL
        Part Number: KF560C30
        Configured Memory Speed: 6000 MT/s

Memory Device
        Size: No Module Installed
        Locator: DIMMA1
"""
    modules = parse_dmidecode_memory(raw)
    assert len(modules) == 1
    assert modules[0]["part"] == "KF560C30"
    assert "serial" not in modules[0]
    assert assess_memory(modules, expected_mts=6000).state == "pass"
    assert assess_memory(modules, expected_mts=6400).state == "fail"


def test_probe_is_read_only_and_bounded() -> None:
    code = (ROOT / "src/modules/hardware_checker/v1_0/probe.py").read_text(encoding="utf-8")
    assert "subprocess.run" in code
    assert "capture_output=True" in code
    assert "timeout=" in code
    for forbidden in ("write_text", "write_bytes", "open(\"w", "shell=True", "sudo"):
        assert forbidden not in code


def test_privileged_dmi_uses_only_fixed_system_paths() -> None:
    code = (ROOT / "src/modules/hardware_checker/v1_0/page.py").read_text(encoding="utf-8")
    assert '("/usr/bin/pkexec", "/bin/pkexec")' in code
    assert '("/usr/sbin/dmidecode", "/usr/bin/dmidecode")' in code
    assert 'shutil.which("pkexec")' not in code


def test_cpu_virtualization_is_reported_without_changing_bios_state() -> None:
    cpu = cpu_info()
    assert cpu["virtualization_state"] in {"enabled", "disabled", "unknown"}
    if cpu["virtualization_state"] == "enabled":
        assert cpu["virtualization_type"] in {"AMD-V / SVM", "Intel VT-x / VMX"}


def test_gpu_load_falls_back_to_bounded_vulkan_helper(monkeypatch) -> None:
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    executable, arguments = gpu_load_command({"vkmark": "/usr/bin/vkmark", "vkcube": "/usr/bin/vkcube"})
    assert executable == "/usr/bin/vkmark"
    assert "1600x900" in arguments and "--run-forever" in arguments
    executable, arguments = gpu_load_command({"glmark2": "", "vkcube": "/usr/bin/vkcube"})
    assert executable == "/usr/bin/vkcube"
    assert arguments == ["--c", "100000", "--width", "640", "--height", "480", "--suppress_popups", "--wsi", "wayland"]
    assert gpu_load_command({"vkcube": "/tmp/fake-vkcube"}) == ("", [])
    assert gpu_load_command({"glmark2": ""}) == ("", [])


def test_checker_shows_full_board_name_and_missing_gpu_helper() -> None:
    from PySide6.QtWidgets import QApplication, QWidget
    from modules.hardware_checker.v1_0.page import HardwareCheckerPage

    app = QApplication.instance() or QApplication([])
    class Settings:
        @staticmethod
        def value(_key, default=None, **_kwargs):
            return default

    host = QWidget()
    host.settings = Settings()
    page = HardwareCheckerPage(host, lambda text: text)
    board = "MAG X870 TOMAHAWK WIFI (MS-7E51) · extended hardware name"
    page.report = {"board": board, "gpus": [{"name": "GPU"}], "tools": {}, "memory_total": "64 GiB"}
    page._populate(under_load=False)
    row = next(row for row in range(page.table.rowCount()) if page.table.item(row, 1).text() == "Mainboard")
    assert page.table.item(row, 2).text() == board
    assert page.table.columnWidth(2) >= page.table.fontMetrics().horizontalAdvance(board)
    page._sync_ready_state()
    assert not page.gpu_button.isEnabled()
    assert tuple(page.cards) == ("cpu", "mainboard", "socket", "gpu", "nvme", "ram")
    assert page.cards["mainboard"].value.text() == board
    for columns in (1, 2, 3):
        page._reflow_cards(columns)
        assert page.card_grid.count() == 6
        assert page.card_grid.getItemPosition(5)[:2] == (5 // columns, 5 % columns)
    host.deleteLater()
    app.processEvents()
    assert not page.gpu_availability_label.isHidden()
    page.report["tools"] = {"vkcube": "/usr/bin/vkcube"}
    page._sync_ready_state()
    assert page.gpu_button.isEnabled()
    assert page.gpu_availability_label.isHidden()
    page.close()
    host.close()


def test_early_graphics_exit_cannot_confirm_a_loaded_pcie_result() -> None:
    import json
    from PySide6.QtCore import QProcess
    from PySide6.QtWidgets import QApplication, QWidget
    from modules.hardware_checker.v1_0.page import HardwareCheckerPage

    app = QApplication.instance() or QApplication([])
    host = QWidget()
    host.settings = type("Settings", (), {"value": lambda self, _key, default=None, **_kw: default})()
    page = HardwareCheckerPage(host, lambda text: text)
    report = {"board": "Board", "gpus": [{"name": "GPU"}], "tools": {}, "memory_total": "64 GiB"}
    page.scan_process = type("Scan", (), {"readAllStandardOutput": lambda self: json.dumps(report).encode()})()
    page.scan_under_load = True
    page.stress_process = QProcess(page)
    page._gpu_ended_early()
    page._scan_finished(0, QProcess.ExitStatus.NormalExit)
    assert page.gpu_test_interrupted
    assert not page.last_scan_under_load
    assert "beendet" in page.status_label.text()
    page.close()
    host.close()


def test_direct_gpu_click_scans_then_starts_the_load_test(monkeypatch) -> None:
    import json
    from PySide6.QtCore import QProcess
    from PySide6.QtWidgets import QApplication, QWidget
    from modules.hardware_checker.v1_0.page import HardwareCheckerPage

    app = QApplication.instance() or QApplication([])
    host = QWidget()
    host.settings = type("Settings", (), {"value": lambda self, _key, default=None, **_kw: default})()
    page = HardwareCheckerPage(host, lambda text: text)
    assert page.gpu_button.isEnabled()
    report = {"board": "Board", "gpus": [{"name": "GPU"}],
              "tools": {"vkcube": "/usr/bin/vkcube"}, "memory_total": "64 GiB"}
    scan = type("Scan", (), {"readAllStandardOutput": lambda self: json.dumps(report).encode()})()
    monkeypatch.setattr(page, "_start_scan", lambda *, under_load: setattr(page, "scan_process", scan))
    page.start_gpu_test()
    assert page.pending_gpu_test and page.scan_process is scan
    started = []
    monkeypatch.setattr(page, "start_gpu_test", lambda: started.append(True))
    page._scan_finished(0, QProcess.ExitStatus.NormalExit)
    assert started == [True] and not page.pending_gpu_test
    page.close()
    host.close()


def test_previous_gpu_test_deadlines_and_signals_cannot_affect_replacement(monkeypatch) -> None:
    from PySide6.QtCore import QCoreApplication, QEvent, QProcess, QTimer
    from PySide6.QtWidgets import QApplication, QWidget
    from modules.hardware_checker.v1_0 import page as checker

    app = QApplication.instance() or QApplication([])
    class FakeProcess(QProcess):
        running = False
        def start(self, *_args): self.running = True
        def state(self):
            return QProcess.ProcessState.Running if self.running else QProcess.ProcessState.NotRunning
        def kill(self): self.running = False
        def waitForFinished(self, _timeout): return True

    host = QWidget()
    host.settings = type("Settings", (), {"value": lambda self, _key, default=None, **_kw: default})()
    page = checker.HardwareCheckerPage(host, lambda text: text)
    deadlines = []
    monkeypatch.setattr(checker, "QProcess", FakeProcess)
    monkeypatch.setattr(QTimer, "singleShot", lambda delay, context, callback: deadlines.append((delay, context, callback)))
    page.report = {"gpus": [{"name": "GPU"}], "tools": {"vkcube": "/usr/bin/vkcube"}}
    try:
        page.start_gpu_test()
        previous = page.stress_process
        old_deadlines = tuple(deadlines)
        assert [item[0] for item in old_deadlines] == [9_000, 12_000]
        assert all(item[1] is previous for item in old_deadlines)
        page._gpu_ended_early(previous)
        page.start_gpu_test()
        replacement = page.stress_process
        assert replacement is not previous
        page.stress_started = True
        scans = []
        monkeypatch.setattr(page, "_start_scan", lambda **kwargs: scans.append(kwargs))
        for _delay, _context, callback in old_deadlines:
            callback()
        previous.finished.emit(0, QProcess.ExitStatus.NormalExit)
        previous.errorOccurred.emit(QProcess.ProcessError.Crashed)
        assert page.stress_process is replacement
        assert replacement.running and not scans
        page._scan_gpu_under_load(replacement)
        assert scans == [{"under_load": True}]
    finally:
        page.stop_processes()
        host.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_stale_scan_and_dmi_callbacks_preserve_current_process_and_report() -> None:
    from PySide6.QtCore import QCoreApplication, QEvent, QProcess
    from PySide6.QtWidgets import QApplication, QWidget
    from modules.hardware_checker.v1_0.page import HardwareCheckerPage

    app = QApplication.instance() or QApplication([])
    host = QWidget()
    host.settings = type("Settings", (), {"value": lambda self, _key, default=None, **_kw: default})()
    page = HardwareCheckerPage(host, lambda text: text)
    old, current_scan, current_dmi = (QProcess(page) for _ in range(3))
    page.scan_process, page.dmi_process = current_scan, current_dmi
    page.report = {"board": "Current board"}
    status = page.status_label.text()
    try:
        page._scan_finished(1, QProcess.ExitStatus.CrashExit, old)
        page._scan_failed(QProcess.ProcessError.Crashed, old)
        page._dmi_finished(1, QProcess.ExitStatus.CrashExit, old)
        page._dmi_failed(QProcess.ProcessError.Crashed, old)
        assert page.scan_process is current_scan and page.dmi_process is current_dmi
        assert page.report == {"board": "Current board"}
        assert page.status_label.text() == status
        page.stop_processes()
        assert page.scan_process is page.dmi_process is page.stress_process is None
        # Late delivery after shutdown is likewise inert.
        page._scan_failed(QProcess.ProcessError.Crashed, current_scan)
        page._dmi_failed(QProcess.ProcessError.Crashed, current_dmi)
        assert page.status_label.text() == status
    finally:
        host.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
