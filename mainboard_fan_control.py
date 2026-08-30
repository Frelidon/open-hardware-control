#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Safe Linux hwmon motherboard fan-control helpers for Open Hardware Control.

The module intentionally separates discovery, curve math and hardware writes so
all policy can be unit-tested without touching a real fan controller.  No PWM
channel is ever guessed from a board name: users must calibrate/label channels
before automatic curves may write to them.
"""
from __future__ import annotations

import os
import re
import json
import selectors
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

DEFAULT_HWMON_ROOT = Path("/sys/class/hwmon")
DEFAULT_DMI_ROOT = Path("/sys/class/dmi/id")
DEFAULT_FAN_HELPER = Path("/usr/libexec/open-hardware-control-fan-helper")
DEFAULT_PKEXEC = Path("/usr/bin/pkexec")
PERSISTENT_FAN_RULES_DIR = Path("/etc/polkit-1/rules.d")
PERSISTENT_FAN_RULE_PREFIX = "49-open-hardware-control-fan"


def _read_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return default


def _read_int(path: Path) -> int | None:
    try:
        return int(_read_text(path))
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class DmiInfo:
    board_vendor: str = ""
    board_name: str = ""
    board_version: str = ""
    product_name: str = ""

    @property
    def normalized(self) -> str:
        return " ".join((self.board_vendor, self.board_name, self.product_name)).upper()

    @property
    def is_msi_x870_family(self) -> bool:
        text = self.normalized
        return "X870" in text and ("MICRO-STAR" in text or "MSI" in text)

    @property
    def is_msi_mag_x870_tomahawk(self) -> bool:
        text = self.normalized
        return ("MSI" in text or "MICRO-STAR" in text) and "X870" in text and "TOMAHAWK" in text


def detect_dmi(root: Path = DEFAULT_DMI_ROOT) -> DmiInfo:
    return DmiInfo(
        board_vendor=_read_text(root / "board_vendor"),
        board_name=_read_text(root / "board_name"),
        board_version=_read_text(root / "board_version"),
        product_name=_read_text(root / "product_name"),
    )


@dataclass
class FanChannel:
    index: int
    hwmon_path: Path
    name: str
    pwm_path: Path
    enable_path: Path | None
    rpm_path: Path | None
    label_path: Path | None = None
    writable: bool = False
    pwm_value: int | None = None
    enable_value: int | None = None
    rpm: int | None = None

    @property
    def stable_id(self) -> str:
        # hwmon numbers are unstable across boots; use chip name + PWM index.
        return f"{self.name}:pwm{self.index}"

    @property
    def display_name(self) -> str:
        label = _read_text(self.label_path) if self.label_path else ""
        if label:
            return f"{label} · pwm{self.index}"
        return f"PWM {self.index} · {self.name}"


@dataclass
class HwmonController:
    path: Path
    name: str
    channels: list[FanChannel] = field(default_factory=list)

    @property
    def is_nct6687(self) -> bool:
        return self.name.casefold().startswith("nct6687")

    @property
    def watchdog_path(self) -> Path | None:
        path = self.path / "fan_control_watchdog"
        return path if path.exists() else None


def discover_hwmon_controllers(root: Path = DEFAULT_HWMON_ROOT) -> list[HwmonController]:
    controllers: list[HwmonController] = []
    if not root.exists():
        return controllers
    for entry in sorted(root.glob("hwmon*")):
        name = _read_text(entry / "name")
        if not name:
            continue
        channel_indices: set[int] = set()
        for pwm_path in entry.glob("pwm[0-9]*"):
            match = re.fullmatch(r"pwm(\d+)", pwm_path.name)
            if match:
                channel_indices.add(int(match.group(1)))
        channels: list[FanChannel] = []
        for index in sorted(channel_indices):
            pwm_path = entry / f"pwm{index}"
            enable_path = entry / f"pwm{index}_enable"
            rpm_path = entry / f"fan{index}_input"
            label_path = entry / f"fan{index}_label"
            channels.append(
                FanChannel(
                    index=index,
                    hwmon_path=entry,
                    name=name,
                    pwm_path=pwm_path,
                    enable_path=enable_path if enable_path.exists() else None,
                    rpm_path=rpm_path if rpm_path.exists() else None,
                    label_path=label_path if label_path.exists() else None,
                    writable=os.access(pwm_path, os.W_OK),
                    pwm_value=_read_int(pwm_path),
                    enable_value=_read_int(enable_path) if enable_path.exists() else None,
                    rpm=_read_int(rpm_path) if rpm_path.exists() else None,
                )
            )
        if channels:
            controllers.append(HwmonController(path=entry, name=name, channels=channels))
    return controllers


def preferred_nct6687_controller(controllers: Iterable[HwmonController]) -> HwmonController | None:
    matches = [item for item in controllers if item.is_nct6687]
    return matches[0] if matches else None


def channel_is_chassis_fan(channel: FanChannel) -> bool:
    """Return True only for motherboard/system fan headers.

    CPU_FAN and PUMP_FAN stay in the dedicated CPU/Kraken cooling area.  This
    is intentionally label based rather than a guessed physical mapping: the
    NCT6687 driver supplies the header class while the exact chassis position
    still has to be calibrated by the user.
    """
    label = _read_text(channel.label_path).casefold() if channel.label_path else ""
    if any(token in label for token in ("cpu fan", "cpu_fan", "pump fan", "pump_fan", "pumpe")):
        return False
    return bool("system fan" in label or "sys fan" in label or "sys_fan" in label)


def percent_to_pwm(percent: float) -> int:
    percent = max(0.0, min(100.0, float(percent)))
    return int(round(percent * 255.0 / 100.0))


def pwm_to_percent(value: int | float) -> int:
    return int(round(max(0.0, min(255.0, float(value))) * 100.0 / 255.0))


def interpolate_curve(points: Iterable[tuple[float, float]], temperature_c: float) -> float:
    ordered = sorted((float(t), float(d)) for t, d in points)
    if not ordered:
        raise ValueError("curve must contain at least one point")
    if temperature_c <= ordered[0][0]:
        return ordered[0][1]
    if temperature_c >= ordered[-1][0]:
        return ordered[-1][1]
    for (t1, d1), (t2, d2) in zip(ordered, ordered[1:]):
        if t1 <= temperature_c <= t2:
            span = max(0.001, t2 - t1)
            ratio = (temperature_c - t1) / span
            return d1 + (d2 - d1) * ratio
    return ordered[-1][1]


def select_temperature(
    source: str,
    *,
    cpu: float | None,
    gpu: float | None,
    liquid: float | None,
    cpu_weight: int = 60,
) -> float | None:
    source = str(source).strip().casefold()
    values = {"cpu": cpu, "gpu": gpu, "liquid": liquid}
    if source in values:
        return values[source]
    available = [value for value in (cpu, gpu, liquid) if value is not None]
    if source == "max":
        return max(available) if available else None
    if source == "weighted":
        if cpu is None and gpu is None:
            return liquid
        if cpu is None:
            return gpu
        if gpu is None:
            return cpu
        weight = max(0, min(100, int(cpu_weight))) / 100.0
        return cpu * weight + gpu * (1.0 - weight)
    return None




@dataclass(frozen=True)
class FanPreset:
    key: str
    name: str
    description: str
    source: str
    points: tuple[tuple[int, int], ...]
    minimum_percent: int
    hysteresis_c: int
    response_delay_s: int
    cpu_weight: int = 60


MAINBOARD_FAN_PRESETS: dict[str, FanPreset] = {
    "quiet": FanPreset(
        key="quiet",
        name="Leise",
        description="Niedrige Grunddrehzahl und ruhige Reaktion für leisen Desktop-Betrieb.",
        source="cpu",
        points=((30, 25), (45, 30), (60, 40), (75, 60), (88, 100)),
        minimum_percent=25,
        hysteresis_c=3,
        response_delay_s=5,
    ),
    "balanced": FanPreset(
        key="balanced",
        name="Ausbalanciert",
        description="Empfohlener Allround-Modus mit moderater Lautstärke und schneller Reserve unter Last.",
        source="cpu",
        points=((30, 30), (45, 40), (60, 55), (75, 75), (85, 100)),
        minimum_percent=25,
        hysteresis_c=2,
        response_delay_s=3,
    ),
    "performance": FanPreset(
        key="performance",
        name="Leistung",
        description="Frühere und stärkere Lüfteranhebung für hohe Dauerlast oder wärmere Radiator-/Abluftpfade.",
        source="cpu",
        points=((30, 40), (45, 50), (60, 65), (75, 85), (85, 100)),
        minimum_percent=35,
        hysteresis_c=1,
        response_delay_s=2,
    ),
}


def fan_preset(key: str) -> FanPreset:
    return MAINBOARD_FAN_PRESETS.get(str(key).strip().casefold(), MAINBOARD_FAN_PRESETS["balanced"])


def recommend_fan_preset(*, channel_name: str = "", board_name: str = "", rpm: int | None = None) -> str:
    """Return a conservative preset suggestion without authorizing hardware writes.

    Physical pwm-to-fan mapping is intentionally *not* inferred here.  The
    heuristic only influences the UI suggestion after discovery/calibration and
    never marks a channel calibrated or enabled.
    """
    text = f"{channel_name} {board_name}".casefold()
    if any(token in text for token in ("pump", "pumpe", "radiator", "aio")):
        return "performance"
    if any(token in text for token in ("silent", "leise", "quiet")):
        return "quiet"
    # Very low observed RPM can be a hint that the connected fan is already a
    # low-speed case fan, but we still keep Balanced as the safe recommendation.
    _ = rpm
    return "balanced"


@dataclass
class CurvePolicy:
    points: list[tuple[int, int]]
    minimum_percent: int = 20
    hysteresis_c: float = 2.0
    response_delay_s: float = 2.0
    emergency_temp_c: float = 90.0
    emergency_percent: int = 100


@dataclass
class CurveState:
    last_temperature_c: float | None = None
    last_percent: int | None = None
    last_write_monotonic: float = 0.0


@dataclass(frozen=True)
class CurveDecision:
    should_write: bool
    percent: int | None
    reason: str


def decide_curve_output(
    policy: CurvePolicy,
    state: CurveState,
    temperature_c: float | None,
    *,
    now: float | None = None,
    force: bool = False,
) -> CurveDecision:
    if temperature_c is None:
        return CurveDecision(False, None, "sensor-unavailable")
    now = time.monotonic() if now is None else float(now)
    if temperature_c >= policy.emergency_temp_c:
        target = max(policy.minimum_percent, min(100, policy.emergency_percent))
        if state.last_percent != target or force:
            return CurveDecision(True, target, "emergency")
        return CurveDecision(False, target, "emergency-unchanged")
    target = int(round(interpolate_curve(policy.points, temperature_c)))
    target = max(policy.minimum_percent, min(100, target))
    if state.last_percent is None:
        return CurveDecision(True, target, "initial")
    if not force and state.last_temperature_c is not None:
        if abs(temperature_c - state.last_temperature_c) < max(0.0, policy.hysteresis_c) and abs(target - state.last_percent) < 3:
            return CurveDecision(False, state.last_percent, "hysteresis")
    if not force and now - state.last_write_monotonic < max(0.0, policy.response_delay_s):
        return CurveDecision(False, state.last_percent, "response-delay")
    if target == state.last_percent and not force:
        return CurveDecision(False, target, "unchanged")
    return CurveDecision(True, target, "curve")


def update_curve_state(state: CurveState, temperature_c: float, percent: int, *, now: float | None = None) -> None:
    state.last_temperature_c = float(temperature_c)
    state.last_percent = int(percent)
    state.last_write_monotonic = time.monotonic() if now is None else float(now)


class FanWriteError(RuntimeError):
    pass


class PrivilegedFanHelperSession:
    """One authenticated, pipe-bound helper for the lifetime of OHC.

    Polkit's ``auth_admin_keep`` cache expires after a few minutes. Starting a
    new pkexec process for every temperature-curve adjustment would therefore
    eventually open another authentication request from a background timer.
    This session authenticates once, keeps the narrowly validated helper as a
    child process, and disappears automatically when OHC closes its stdin.
    """

    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None
        self.lock = threading.RLock()

    def active(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def stop(self) -> None:
        process = self.process
        self.process = None
        if process is None:
            return
        try:
            if process.stdin is not None:
                process.stdin.close()
        except OSError:
            pass
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=1.0)

    def _reply(self, timeout: float) -> dict[str, object]:
        process = self.process
        if process is None or process.stdout is None:
            raise FanWriteError("privilegierte Lüfter-Helfersitzung ist nicht verfügbar")
        selector = selectors.DefaultSelector()
        try:
            selector.register(process.stdout, selectors.EVENT_READ)
            if not selector.select(max(0.1, float(timeout))):
                self.stop()
                raise FanWriteError(
                    "Administratorfreigabe für die Lüftersteuerung hat nicht rechtzeitig geantwortet; "
                    "die Kurvenregelung wurde sicher pausiert"
                )
            line = process.stdout.readline()
        finally:
            selector.close()
        if not line:
            detail = ""
            if process.poll() is not None and process.stderr is not None:
                try:
                    detail = process.stderr.read().strip()
                except OSError:
                    detail = ""
            self.stop()
            raise FanWriteError(
                detail or "Authentifizierung für Mainboard-Lüftersteuerung abgebrochen oder verweigert"
            )
        try:
            payload = json.loads(line)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self.stop()
            raise FanWriteError("ungültige Antwort der privilegierten Lüfter-Helfersitzung") from exc
        if not isinstance(payload, dict) or payload.get("ok") is not True:
            self.stop()
            raise FanWriteError(
                str(payload.get("error", "Lüfter-Helfer meldete keinen Erfolg"))
                if isinstance(payload, dict) else "Lüfter-Helfer meldete keinen Erfolg"
            )
        return payload

    def start(self, timeout: float = 120.0) -> None:
        with self.lock:
            if self.active():
                return
            self.stop()
            if not privileged_fan_helper_available():
                raise FanWriteError("privilegierter NCT6687-Helfer ist nicht installiert")
            try:
                self.process = subprocess.Popen(
                    [str(DEFAULT_PKEXEC), str(DEFAULT_FAN_HELPER), "session"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )
            except OSError as exc:
                self.process = None
                raise FanWriteError(f"privilegierter Lüfter-Helfer konnte nicht gestartet werden: {exc}") from exc
            self._reply(timeout)

    def request(self, args: tuple[str, ...], timeout: float = 15.0) -> dict[str, object]:
        with self.lock:
            self.start()
            process = self.process
            if process is None or process.stdin is None:
                raise FanWriteError("privilegierte Lüfter-Helfersitzung ist nicht verfügbar")
            try:
                process.stdin.write(json.dumps(list(args), ensure_ascii=True) + "\n")
                process.stdin.flush()
            except (BrokenPipeError, OSError) as exc:
                self.stop()
                raise FanWriteError("Verbindung zur privilegierten Lüfter-Helfersitzung wurde beendet") from exc
            return self._reply(timeout)


_PRIVILEGED_FAN_SESSION = PrivilegedFanHelperSession()


def stop_privileged_fan_helper_session() -> None:
    _PRIVILEGED_FAN_SESSION.stop()


def privileged_fan_helper_available() -> bool:
    return DEFAULT_FAN_HELPER.is_file() and os.access(DEFAULT_FAN_HELPER, os.X_OK) and DEFAULT_PKEXEC.is_file()


def persistent_fan_authorization_path(uid: int | None = None) -> Path:
    """Return the fixed per-user Polkit rule path without accepting input paths."""

    user_id = os.getuid() if uid is None else int(uid)
    if user_id < 0:
        raise ValueError("ungültige Benutzer-ID")
    return PERSISTENT_FAN_RULES_DIR / f"{PERSISTENT_FAN_RULE_PREFIX}-{user_id}.rules"


def persistent_fan_authorization_enabled(uid: int | None = None) -> bool:
    return persistent_fan_authorization_path(uid).is_file()


def persistent_fan_authorization_command(enabled: bool) -> list[str]:
    """Build the fixed pkexec command that grants or revokes the local rule."""

    if not privileged_fan_helper_available():
        raise FanWriteError("privilegierter NCT6687-Helfer ist nicht installiert")
    operation = "grant-persistent" if enabled else "revoke-persistent"
    return [str(DEFAULT_PKEXEC), str(DEFAULT_FAN_HELPER), operation]


def channel_control_method(channel: FanChannel) -> str:
    if os.access(channel.pwm_path, os.W_OK):
        return "direct"
    if privileged_fan_helper_available() and channel.name.casefold().startswith("nct6687"):
        return "polkit"
    return "none"


def channel_can_control(channel: FanChannel) -> bool:
    return channel_control_method(channel) != "none"


def _run_privileged_helper(*args: str, timeout: float = 15.0) -> dict[str, object]:
    return _PRIVILEGED_FAN_SESSION.request(tuple(map(str, args)), timeout=timeout)


def _write_sysfs(path: Path, value: str) -> None:
    try:
        path.write_text(value, encoding="ascii")
    except OSError as exc:
        raise FanWriteError(f"{path}: {exc}") from exc


def set_channel_percent(channel: FanChannel, percent: int) -> None:
    percent = max(0, min(100, int(percent)))
    method = channel_control_method(channel)
    if method == "polkit":
        _run_privileged_helper("set-percent", str(channel.index), str(percent))
        return
    if method != "direct":
        raise FanWriteError(f"{channel.pwm_path} ist weder direkt noch über den privilegierten Helfer schreibbar")
    if channel.enable_path is not None and os.access(channel.enable_path, os.W_OK):
        _write_sysfs(channel.enable_path, "1\n")
    _write_sysfs(channel.pwm_path, f"{percent_to_pwm(percent)}\n")


def restore_firmware_control(channel: FanChannel) -> None:
    if channel.enable_path is None:
        raise FanWriteError("firmware restore is not exposed through pwm_enable")
    if os.access(channel.enable_path, os.W_OK):
        _write_sysfs(channel.enable_path, "2\n")
        return
    if channel_control_method(channel) == "polkit":
        _run_privileged_helper("restore-firmware", str(channel.index))
        return
    raise FanWriteError("firmware restore is not writable and privileged helper is unavailable")


def set_fan_control_watchdog(controller: HwmonController, timeout_s: int) -> bool:
    """Arm/refresh the optional nct6687d manual-control lease.

    Newer nct6687d exposes ``fan_control_watchdog`` when the MSI brute-force
    fan path is active.  The driver itself restores changed channels if a
    controlling userspace process disappears and stops refreshing the lease.
    Returning False means the installed driver does not expose the safeguard;
    it is not treated as an error.
    """

    path = controller.watchdog_path
    if path is None:
        return False
    timeout_s = max(0, min(300, int(timeout_s)))
    if os.access(path, os.W_OK):
        _write_sysfs(path, f"{timeout_s}\n")
        return True
    if controller.is_nct6687 and privileged_fan_helper_available():
        _run_privileged_helper("watchdog", str(timeout_s))
        return True
    return False


def disarm_fan_control_watchdog(controller: HwmonController) -> bool:
    return set_fan_control_watchdog(controller, 0)


@dataclass
class CalibrationSnapshot:
    pwm: int | None
    enable: int | None


def snapshot_channel(channel: FanChannel) -> CalibrationSnapshot:
    return CalibrationSnapshot(_read_int(channel.pwm_path), _read_int(channel.enable_path) if channel.enable_path else None)


def restore_snapshot(channel: FanChannel, snapshot: CalibrationSnapshot) -> None:
    # For automatic NCT6687 control the driver itself restores the complete
    # firmware/MSI curve when pwmN_enable=2 is requested. Replaying only the
    # instantaneous pwmN value would be less correct on msi_fan_brute_force.
    if snapshot.enable in (2, 99):
        restore_firmware_control(channel)
        return
    if snapshot.pwm is None:
        return
    raw = max(0, min(255, int(snapshot.pwm)))
    if os.access(channel.pwm_path, os.W_OK):
        if channel.enable_path is not None and os.access(channel.enable_path, os.W_OK):
            _write_sysfs(channel.enable_path, "1\n")
        _write_sysfs(channel.pwm_path, f"{raw}\n")
        if snapshot.enable is not None and channel.enable_path is not None and os.access(channel.enable_path, os.W_OK):
            _write_sysfs(channel.enable_path, f"{snapshot.enable}\n")
        return
    if channel_control_method(channel) == "polkit" and snapshot.enable is not None:
        _run_privileged_helper("restore-snapshot", str(channel.index), str(raw), str(snapshot.enable))
        return
    raise FanWriteError("Kalibrierungszustand kann ohne Schreibrecht/Helfer nicht wiederhergestellt werden")


@dataclass(frozen=True)
class SecureBootDiagnostics:
    secure_boot: str
    module_loaded: bool
    module_path: str
    mokutil_available: bool
    dkms_available: bool


def secure_boot_diagnostics(module_name: str = "nct6687") -> SecureBootDiagnostics:
    mokutil = shutil.which("mokutil")
    secure_boot = "Unbekannt"
    if mokutil:
        try:
            result = subprocess.run([mokutil, "--sb-state"], capture_output=True, text=True, timeout=4, check=False)
            secure_boot = (result.stdout or result.stderr).strip() or "Unbekannt"
        except (OSError, subprocess.SubprocessError):
            secure_boot = "Unbekannt"
    module_loaded = False
    try:
        modules = Path("/proc/modules").read_text(encoding="utf-8", errors="replace")
        module_loaded = re.search(rf"^{re.escape(module_name)}\s", modules, re.MULTILINE) is not None
    except OSError:
        pass
    module_path = ""
    modinfo = shutil.which("modinfo")
    if modinfo:
        try:
            result = subprocess.run([modinfo, "-n", module_name], capture_output=True, text=True, timeout=4, check=False)
            if result.returncode == 0:
                module_path = result.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return SecureBootDiagnostics(
        secure_boot=secure_boot,
        module_loaded=module_loaded,
        module_path=module_path,
        mokutil_available=bool(mokutil),
        dkms_available=bool(shutil.which("dkms")),
    )


def fedora_nct6687_setup_commands() -> list[str]:
    return [
        "sudo dnf install -y git make gcc gcc-c++ kernel-devel kernel-headers dkms openssl mokutil",
        "git clone https://github.com/Fred78290/nct6687d.git",
        "cd nct6687d && sudo make dkms/install",
        'echo "options nct6687 msi_fan_brute_force=1" | sudo tee /etc/modprobe.d/nct6687_msi.conf',
        'echo "nct6687" | sudo tee /etc/modules-load.d/nct6687.conf',
    ]


def validate_curve(points: Iterable[tuple[int, int]], minimum_percent: int = 0) -> list[tuple[int, int]]:
    normalized = [(int(t), int(p)) for t, p in points]
    if len(normalized) < 2:
        raise ValueError("curve requires at least two points")
    temperatures = [t for t, _ in normalized]
    duties = [p for _, p in normalized]
    if any(b <= a for a, b in zip(temperatures, temperatures[1:])):
        raise ValueError("temperatures must be strictly increasing")
    if any(p < minimum_percent or p > 100 for p in duties):
        raise ValueError("duty outside allowed range")
    if any(b < a for a, b in zip(duties, duties[1:])):
        raise ValueError("duty must not decrease as temperature rises")
    if duties[-1] != 100:
        raise ValueError("last curve point must request 100 percent")
    return normalized
