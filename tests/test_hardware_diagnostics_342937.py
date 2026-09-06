from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hardware_diagnostics import (
    normalize_linux_clock,
    read_primary_amd_gpu_clock,
    validate_metric_snapshot,
)


def _amd_card(root: Path, card: str, *, vram: int, clock: int) -> None:
    device = root / card / "device"
    hwmon = device / "hwmon" / "hwmon0"
    hwmon.mkdir(parents=True)
    (device / "vendor").write_text("0x1002\n", encoding="ascii")
    (device / "mem_info_vram_total").write_text(f"{vram}\n", encoding="ascii")
    (hwmon / "freq1_input").write_text(f"{clock}\n", encoding="ascii")


def test_exact_one_million_hz_is_one_mhz_not_one_million_mhz(tmp_path: Path) -> None:
    _amd_card(tmp_path, "card0", vram=512 * 1024**2, clock=2_200_000_000)
    _amd_card(tmp_path, "card1", vram=16 * 1024**3, clock=1_000_000)
    reading = read_primary_amd_gpu_clock(tmp_path)
    assert reading.raw == 1_000_000
    assert reading.mhz == 1.0
    assert "TRCC-9.9.11-Grenzfall" in reading.issue


def test_normal_clock_units_and_implausible_metrics() -> None:
    assert normalize_linux_clock(1_558_000_000, maximum_mhz=5_000) == (1558.0, "")
    assert normalize_linux_clock(2715, maximum_mhz=5_000) == (2715.0, "")
    issues = validate_metric_snapshot({"gpuClock": 1_000_000, "gpuLoad": 43})
    assert len(issues) == 1
    assert issues[0].metric == "gpuClock"


def test_low_hz_idle_range_is_guarded_too(tmp_path: Path) -> None:
    _amd_card(tmp_path, "card0", vram=16 * 1024**3, clock=800_000)
    reading = read_primary_amd_gpu_clock(tmp_path)
    assert reading.mhz == 0.8
    assert "TRCC-9.9.11-Grenzfall" in reading.issue
