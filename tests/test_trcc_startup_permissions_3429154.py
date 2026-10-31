"""TRCC startup metadata never grants the general dmidecode CLI root access."""
from __future__ import annotations

import os
import ast
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from types import ModuleType
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import ohc_trcc_dmi_helper as helper
from modules.trcc_backend.v1_0 import runtime


DMI = """Handle 0x0010, DMI type 17, 92 bytes
Memory Device
    Size: 16 GB
    Locator: DIMM_A2
    Type: DDR5
    Manufacturer: Test Manufacturer
    Part Number: MODEL-123
    Serial Number: PRIVATE-SERIAL-NEVER-KEEP
    Asset Tag: PRIVATE-ASSET
    Speed: 4800 MT/s
    Configured Memory Speed: 6000 MT/s
Handle 0x0011, DMI type 17, 92 bytes
Memory Device
    Size: 16 GB
    Locator: DIMM_B2
    Configured Memory Speed: 6000 MT/s
Handle 0x0012, DMI type 1, 27 bytes
System Information
    UUID: PRIVATE-UUID
    Manufacturer: PRIVATE-SYSTEM-MANUFACTURER
"""


@pytest.mark.parametrize("args", [
    ["--dump-bin", "/tmp/root-write"], ["-t", "memory"], ["--from-dump", "/tmp/file"],
    ["--help"], [";id"], [""],
])
def test_readonly_helper_rejects_every_argument_before_any_read(args, monkeypatch, capsys):
    monkeypatch.setattr(helper.subprocess, "run", lambda *_a, **_k: pytest.fail("must not execute"))
    assert helper.main(["helper", *args]) == 64
    assert capsys.readouterr().out == ""


def test_readonly_helper_requires_root_before_any_read(monkeypatch, capsys):
    monkeypatch.setattr(helper.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(helper.subprocess, "run", lambda *_a, **_k: pytest.fail("must not execute"))
    assert helper.main(["helper"]) == 77
    assert capsys.readouterr().out == ""


def test_readonly_helper_fixed_command_clean_environment_and_private_field_filter(monkeypatch, capsys):
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    monkeypatch.setattr(helper, "trusted_executable", lambda path: path == Path("/usr/sbin/dmidecode"))
    monkeypatch.setenv("LD_PRELOAD", "/tmp/attack.so")
    monkeypatch.setenv("PYTHONPATH", "/tmp/attack")
    calls = []
    def run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, DMI, "ignored")
    monkeypatch.setattr(helper.subprocess, "run", run)
    assert helper.main(["helper"]) == 0
    command, options = calls[0]
    assert command == ["/usr/sbin/dmidecode", "-t", "memory"]
    assert options["env"] == {"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C", "LC_ALL": "C"}
    assert options["timeout"] == 5 and options["cwd"] == "/"
    assert options["stdin"] == subprocess.DEVNULL
    output = capsys.readouterr().out
    assert output.count("Memory Device") == 2
    assert "Configured Memory Speed: 6000 MT/s" in output
    assert "Manufacturer: Test Manufacturer" in output
    assert "PRIVATE" not in output and "Serial Number" not in output and "UUID" not in output


def test_readonly_helper_refuses_untrusted_system_file_and_oversized_output(monkeypatch, capsys):
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    monkeypatch.setattr(helper, "trusted_executable", lambda _path: False)
    assert helper.main(["helper"]) == 69
    monkeypatch.setattr(helper, "trusted_executable", lambda _path: True)
    monkeypatch.setattr(helper.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a[0], 0, "x" * (helper.MAX_OUTPUT_BYTES + 1), ""))
    assert helper.main(["helper"]) == 74
    assert capsys.readouterr().out == ""


def test_system_file_requires_root_owner_and_safe_ancestors(monkeypatch):
    import stat
    def metadata(uid=0, mode=0o755, directory=False):
        return SimpleNamespace(st_uid=uid, st_mode=(stat.S_IFDIR if directory else stat.S_IFREG) | mode)
    target = Path("/usr/sbin/dmidecode")
    states = {target: metadata(), **{parent: metadata(directory=True) for parent in target.parents}}
    monkeypatch.setattr(Path, "lstat", lambda path: states[path])
    assert helper.trusted_executable(target)
    for replacement in (metadata(uid=1000), metadata(mode=0o777),
                        SimpleNamespace(st_uid=0, st_mode=stat.S_IFLNK | 0o777)):
        states[target] = replacement
        assert not helper.trusted_executable(target)
    states[target] = metadata()
    states[Path("/usr")] = metadata(mode=0o777, directory=True)
    assert not helper.trusted_executable(target)


def fake_backend():
    return (SimpleNamespace(_privileged_cmd=lambda *_: ["unsafe"]),
            SimpleNamespace(_daemon_spawn_cmd=lambda: ["unadapted"]))


def test_adapter_only_exact_memory_query_uses_fixed_helper_and_daemon_inherits(monkeypatch):
    monkeypatch.setenv("TRCC_DISABLE_LIVE_IMC", "")
    monkeypatch.setattr(runtime, "memory_helper_available", lambda: True)
    linux, daemon = fake_backend()
    prefix = ("/usr/bin/python3", "launcher.py", "/usr/local/bin/trcc")
    runtime.configure_backend(linux, daemon, prefix)
    assert linux._privileged_cmd("dmidecode", ["-t", "memory"]) == ["/usr/bin/pkexec", str(runtime.DMI_HELPER)]
    assert daemon._daemon_spawn_cmd() == [*prefix, "daemon"]
    assert os.environ["TRCC_DISABLE_LIVE_IMC"] == "1"
    for binary, args in (("dmidecode", ["--dump-bin", "/tmp/file"]),
                         ("dmidecode", ["-t", "memory", "--dump-bin", "/tmp/file"]),
                         ("smartctl", ["-a", "/dev/sda"])):
        assert linux._privileged_cmd(binary, args) == [binary, *args]


def test_missing_helper_degrades_to_unprivileged_metadata_without_password(monkeypatch):
    monkeypatch.setenv("TRCC_DISABLE_LIVE_IMC", "")
    monkeypatch.setattr(runtime, "memory_helper_available", lambda: False)
    linux, daemon = fake_backend()
    runtime.configure_backend(linux, daemon, ("launcher",))
    assert linux._privileged_cmd("dmidecode", ["-t", "memory"]) == ["dmidecode", "-t", "memory"]


def test_prefix_changes_only_trusted_ubuntu_system_backend(monkeypatch):
    monkeypatch.setattr(runtime, "_trusted_file", lambda *_a, **_k: True)
    executable = "/usr/local/bin/trcc"
    assert runtime.command_prefix(executable, ubuntu=False) == (executable,)
    assert runtime.command_prefix("/home/exampleuser/.local/bin/trcc", ubuntu=True) == ("/home/exampleuser/.local/bin/trcc",)
    assert runtime.command_prefix(executable, ubuntu=True) == (
        "/usr/bin/python3", str(Path(runtime.__file__).with_name("launcher.py")), executable,
    )
    monkeypatch.setattr(runtime, "_trusted_file", lambda *_a, **_k: False)
    assert runtime.command_prefix(executable, ubuntu=True) == (executable,)


def test_memory_policy_authorizes_only_immutable_no_argument_reader():
    policy = ET.parse(ROOT / "packaging/io.github.Frelidon.OpenHardwareControl.dmi.policy")
    action = policy.find("action")
    assert action.attrib["id"] == "io.github.Frelidon.OpenHardwareControl.memory-info"
    assert action.findtext("defaults/allow_any") == "no"
    assert action.findtext("defaults/allow_inactive") == "no"
    assert action.findtext("defaults/allow_active") == "yes"
    assert action.findtext("annotate[@key='org.freedesktop.policykit.exec.path']") == str(runtime.DMI_HELPER)
    text = ET.tostring(action, encoding="unicode")
    assert "/usr/sbin/dmidecode" not in text and "/usr/bin/python" not in text
    assert "allow_gui" not in text and "command_line" not in text


def test_package_and_explicit_ubuntu_setup_include_same_fixed_helper():
    builder = (ROOT / "scripts/build_release.py").read_text()
    installer = (ROOT / "packaging/install.sh").read_text()
    setup = (ROOT / "packaging/install-trcc.sh").read_text()
    for source in (builder, installer, setup):
        assert "ohc_trcc_dmi_helper.py" in source
        assert "io.github.Frelidon.OpenHardwareControl.dmi.policy" in source
    assert "/usr/libexec/open-hardware-control-dmi-memory-helper" in builder
    assert '[[ "$family" == ubuntu ]]' in setup
    assert "system setup" not in setup
    assert "install_dmi_helper" in setup and "dmi_helper_present" in setup


@pytest.mark.parametrize("count", [2, 4])
def test_filtered_records_match_installed_upstream_parser_without_importing_hardware(count):
    # Compile only the actual upstream pure parser, never construct its App,
    # import sensor discovery or run dmidecode. Keep this recorded contract
    # independent of whether the optional TRCC package is installed in CI.
    path = Path("/usr/lib/python3/dist-packages/trcc/adapters/system/linux.py")
    if not path.is_file():
        pytest.skip("optional upstream package is absent")
    source = ast.parse(path.read_text())
    functions = [node for node in source.body if isinstance(node, ast.FunctionDef)
                 and node.name in {"_is_populated", "_parse_dmi_memory"}]
    fields = {value.casefold().replace(" ", "_") for value in helper.MEMORY_FIELDS}
    namespace = {"_DMI_MEMORY_FIELDS": fields, "_DMI_EMPTY_SLOT": "No Module Installed",
                 "log": SimpleNamespace(debug=lambda *_a, **_k: None)}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec"), namespace)
    fixture = "".join(
        f"Handle 0x{index:04x}, DMI type 17, 92 bytes\nMemory Device\n"
        f"\tSize: 16 GB\n\tLocator: DIMM_{index}\n\tConfigured Memory Speed: 6000 MT/s\n"
        "\tSerial Number: PRIVATE-ID\n" for index in range(count)
    )
    filtered = helper.filter_memory_fields(fixture)
    records = namespace["_parse_dmi_memory"](filtered)
    assert len(records) == count
    assert [slot["locator"] for slot in records] == [f"DIMM_{index}" for index in range(count)]
    assert all(slot["configured_memory_speed"] == "6000 MT/s" for slot in records)
    assert "PRIVATE-ID" not in filtered


def test_runtime_policy_must_really_authorize_only_active_fixed_reader(tmp_path, monkeypatch):
    policy = tmp_path / "metadata.policy"
    original = (ROOT / "packaging/io.github.Frelidon.OpenHardwareControl.dmi.policy").read_text()
    policy.write_text(original)
    monkeypatch.setattr(runtime, "DMI_POLICY", policy)
    monkeypatch.setattr(runtime, "_trusted_file", lambda *_a, **_k: True)
    assert runtime.memory_helper_available()
    for broken in (original.replace("<allow_active>yes", "<allow_active>auth_admin"),
                   original.replace(str(runtime.DMI_HELPER), "/usr/sbin/dmidecode"),
                   "invalid XML", "x" * 16_385):
        policy.write_text(broken)
        assert not runtime.memory_helper_available()


def test_adapted_daemon_retains_existing_exact_process_identity_contract():
    from modules.levita_daemon_health.v1_1.model import is_trcc_daemon_command
    prefix = ("/usr/bin/python3", str(Path(runtime.__file__).with_name("launcher.py")), "/usr/local/bin/trcc")
    assert is_trcc_daemon_command((*prefix, "daemon"))
    assert not is_trcc_daemon_command((*prefix, "detect"))


def test_launcher_passes_cli_arguments_and_future_daemon_through_same_adapter(monkeypatch):
    from modules.trcc_backend.v1_0 import launcher
    linux, daemon = fake_backend()
    root = ModuleType("trcc")
    root.daemon = daemon
    system = ModuleType("trcc.adapters.system")
    system.linux = linux
    entry = ModuleType("trcc._entry")
    received = []
    entry.main = lambda: received.append(tuple(sys.argv)) or 0
    for name, module in (("trcc", root), ("trcc.adapters.system", system), ("trcc._entry", entry)):
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(sys, "argv", ["test"])
    monkeypatch.setenv("TRCC_DISABLE_LIVE_IMC", "")
    monkeypatch.setattr(sys, "path", list(sys.path))
    assert launcher.main(["launcher.py", "/usr/local/bin/trcc", "display", "video-status", "87ad:70db"]) == 0
    assert received == [("/usr/local/bin/trcc", "display", "video-status", "87ad:70db")]
    assert daemon._daemon_spawn_cmd() == [sys.executable, str(Path(launcher.__file__).resolve()), "/usr/local/bin/trcc", "daemon"]


def test_launcher_version_reads_only_package_metadata_not_cli_or_sensors(monkeypatch, capsys):
    from modules.trcc_backend.v1_0 import launcher
    version = ModuleType("trcc.__version__")
    version.__version__ = "9.10.4"
    monkeypatch.setitem(sys.modules, "trcc.__version__", version)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(runtime, "configure_backend", lambda *_a, **_k: pytest.fail("must not initialize backend"))
    assert launcher.main(["launcher.py", "/usr/local/bin/trcc", "--version"]) == 0
    assert capsys.readouterr().out == "trcc 9.10.4\n"
