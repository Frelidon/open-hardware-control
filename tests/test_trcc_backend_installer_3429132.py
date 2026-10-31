"""TRCC install UI and Ubuntu package helper stay explicit and verified."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
HELPER = (ROOT / "packaging/install-trcc.sh").read_text(encoding="utf-8")
INSTALLER = (
    ROOT / "src/modules/trcc_backend/v1_0/installer.py"
).read_text(encoding="utf-8")


def test_setup_wizard_offers_trcc_only_for_detected_missing_levita_backend() -> None:
    assert "thermalright_display_present() and find_trcc_executable() is None" in MAIN
    assert '"install_trcc": self.install_trcc_checkbox.isChecked()' in MAIN
    assert '"trcc", after=' in MAIN
    assert 'elif backend_name == "trcc":' in MAIN
    assert "install_trcc(self, after)" in MAIN


def test_trcc_helper_is_ubuntu_only_and_verifies_official_package() -> None:
    assert '[[ "${ID:-}" == ubuntu ]]' in HELPER
    assert "trcc-linux_9.10.4-1_all.deb" in HELPER
    assert "bc25685024e7cfafb6a8be9b13a83ac384c3da21443beffc9fc1a2018b558e8c" in HELPER
    assert "sha256sum -c -" in HELPER
    assert "apt-get install -y" in HELPER
    assert "dnf" not in HELPER


def test_trcc_installer_refreshes_studio_without_applying_hardware_design() -> None:
    assert 'host.backend.run_async([pkexec, str(script), "--install"]' in INSTALLER
    assert "studio.reload_backend_availability()" in INSTALLER
    assert "apply_design" not in INSTALLER
