from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nzxt_backend import (
    BY_PRODUCT_ID,
    SupportLevel,
    detect_profile_from_liquidctl_output,
    detect_profile_from_sysfs,
    nzxt_liquidctl_device_present,
    udev_product_ids,
)


def test_known_usb_ids_are_registered():
    assert udev_product_ids() == ("300e", "300c", "3012", "3014")
    assert BY_PRODUCT_ID["3012"].liquidctl_name == "NZXT Kraken 2024 Elite RGB"
    assert BY_PRODUCT_ID["3014"].display_name == "NZXT Kraken Plus"


def test_liquidctl_output_selects_specific_model():
    out = "NZXT Kraken 2024 Elite RGB\n├── Liquid temperature 28.1 °C\n"
    profile = detect_profile_from_liquidctl_output(out)
    assert profile is not None
    assert profile.product_id == "3012"
    assert profile.capabilities.lcd_static
    assert profile.capabilities.pump_rgb


def test_legacy_elite_is_detection_only():
    profile = BY_PRODUCT_ID["300c"]
    assert profile.support == SupportLevel.DETECTION_ONLY
    assert not profile.allows_writes


def test_sysfs_usb_id_detection(tmp_path: Path):
    dev = tmp_path / "1-2"
    dev.mkdir()
    (dev / "idVendor").write_text("1e71\n", encoding="ascii")
    (dev / "idProduct").write_text("3014\n", encoding="ascii")
    profile = detect_profile_from_sysfs(tmp_path)
    assert profile is not None
    assert profile.product_id == "3014"
    assert nzxt_liquidctl_device_present(tmp_path)


def test_nzxt_rgb_controller_counts_as_liquidctl_device_but_unrelated_usb_does_not(tmp_path: Path):
    nzxt = tmp_path / "1-4"
    nzxt.mkdir()
    (nzxt / "idVendor").write_text("1e71\n", encoding="ascii")
    (nzxt / "idProduct").write_text("2012\n", encoding="ascii")
    assert nzxt_liquidctl_device_present(tmp_path)
    (nzxt / "idVendor").write_text("87ad\n", encoding="ascii")
    assert not nzxt_liquidctl_device_present(tmp_path)
