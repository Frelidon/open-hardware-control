"""A user update must not leave autostart pointing to an old system install."""

from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from modules.application_activation.v1_0.autostart import retarget_entry, update_existing


@pytest.mark.parametrize("distribution", ["ubuntu", "fedora"])
@pytest.mark.parametrize("disabled", [False, True])
@pytest.mark.parametrize("entry_name", ["open-hardware-control.desktop", "kraken-control.desktop"])
def test_real_helper_updates_only_existing_entry_and_preserves_enabled_choice(tmp_path, distribution, disabled, entry_name):
    home = tmp_path / distribution / "User Home"
    folder = home / ".config/autostart"
    folder.mkdir(parents=True)
    entry = folder / entry_name
    entry.write_text("# retained\n[Desktop Entry]\nType=Application\n"
                     "Exec=/usr/bin/open-hardware-control --autostart --custom\n"
                     "Icon=/old/icon.png\nTryExec=/usr/bin/open-hardware-control\n"
                     f"Hidden={str(disabled).lower()}\n"
                     f"X-GNOME-Autostart-enabled={str(not disabled).lower()}\n")
    launcher = home / ".local/bin/open-hardware-control"
    icon = home / ".local/share/open-hardware-control/assets/branding/open-hardware-control-icon.png"
    helper = ROOT / "src/modules/application_activation/v1_0/autostart.py"
    subprocess.run([sys.executable, "-B", str(helper), str(home), str(launcher), str(icon)],
                   check=True, timeout=5)
    result = entry.read_text()
    assert f'Exec="{launcher}" --autostart --custom' in result
    assert f"Icon={icon}" in result and f"TryExec={launcher}" in result
    assert f"Hidden={str(disabled).lower()}" in result
    assert f"X-GNOME-Autostart-enabled={str(not disabled).lower()}" in result
    assert result.startswith("# retained")
    assert list(folder.iterdir()) == [entry]
    update_existing(home, launcher, icon)
    assert entry.read_text() == result


def test_missing_autostart_custom_wrapper_and_symlink_are_preserved(tmp_path):
    launcher = tmp_path / ".local/bin/open-hardware-control"
    icon = tmp_path / "icon.png"
    update_existing(tmp_path, launcher, icon)
    assert not (tmp_path / ".config").exists()
    custom = "[Desktop Entry]\nExec=/custom/wrapper --autostart\nIcon=custom\n"
    assert retarget_entry(custom, tmp_path, launcher, icon) == custom
    folder = tmp_path / ".config/autostart"
    folder.mkdir(parents=True)
    target = tmp_path / "unrelated.desktop"
    target.write_text("[Desktop Entry]\nExec=/usr/bin/open-hardware-control --autostart\n")
    (folder / "open-hardware-control.desktop").symlink_to(target)
    update_existing(tmp_path, launcher, icon)
    assert target.read_text().startswith("[Desktop Entry]\nExec=/usr/bin/")


def test_installer_calls_helper_after_updating_the_real_user_launcher():
    source = (ROOT / "packaging/install.sh").read_text()
    assert source.index('chmod 0755 "$BIN_DIR/open-hardware-control"') < source.index(
        'python3 "$APP_DIR/modules/application_activation/v1_0/autostart.py"')
