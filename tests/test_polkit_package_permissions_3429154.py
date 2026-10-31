"""Execute the real package-policy stage without invoking a release build."""
from __future__ import annotations

import ast
import os
from pathlib import Path
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
POLICIES = (
    "io.github.Frelidon.OpenHardwareControl.dmi.policy",
    "io.github.Frelidon.OpenHardwareControl.fan.policy",
    "io.github.Frelidon.OpenHardwareControl.snapshot.policy",
)


@pytest.mark.parametrize("source_mode", [0o600, 0o644, 0o664, 0o666, 0o755])
def test_deb_and_rpm_stage_dmi_policy_as_readonly_regardless_of_checkout_mode(tmp_path, source_mode):
    source = ast.parse((ROOT / "scripts/build_release.py").read_text(encoding="utf-8"))
    install = next(node for node in source.body
                   if isinstance(node, ast.FunctionDef) and node.name == "install_runtime_tree")
    start = next(index for index, node in enumerate(install.body)
                 if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == "polkit_dir"
                         for target in node.targets))
    # Compile its real policy-copy suffix, not a reimplementation. Earlier
    # release orchestration, user assets, subprocesses and host paths never run.
    policy_stage = ast.FunctionDef(
        name="stage", args=install.args, body=install.body[start:],
        decorator_list=[], returns=None,
    )
    namespace = {"Path": Path, "shutil": shutil, "PACKAGING_DIR": tmp_path / "source"}
    namespace["PACKAGING_DIR"].mkdir()
    for name in POLICIES:
        fixture = namespace["PACKAGING_DIR"] / name
        fixture.write_text("<policyconfig/>\n", encoding="utf-8")
        fixture.chmod(source_mode)
    compiled = ast.fix_missing_locations(ast.Module(body=[policy_stage], type_ignores=[]))
    exec(compile(compiled, "<real-package-policy-stage>", "exec"), namespace)
    package_root = tmp_path / "package-stage"
    namespace["stage"](package_root)
    target = package_root / "usr/share/polkit-1/actions" / POLICIES[0]
    assert target.stat().st_mode & 0o777 == 0o644
    assert target.read_bytes() == (namespace["PACKAGING_DIR"] / POLICIES[0]).read_bytes()
    assert (namespace["PACKAGING_DIR"] / POLICIES[0]).stat().st_mode & 0o777 == source_mode
    for name in ("build_deb", "build_rpm"):
        function = next(node for node in source.body
                        if isinstance(node, ast.FunctionDef) and node.name == name)
        assert any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                   and node.func.id == "install_runtime_tree" for node in ast.walk(function))


def test_real_runtime_stage_normalizes_umask_and_copied_directory_modes_only_in_destination(tmp_path, monkeypatch):
    tree = ast.parse((ROOT / "scripts/build_release.py").read_text(encoding="utf-8"))
    install = next(node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name == "install_runtime_tree")
    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"RUNTIME_FILES", "PACKAGING_FILES"}:
                    constants[target.id] = ast.literal_eval(node.value)
    checkout = tmp_path / "source-checkout"
    package_root = tmp_path / "isolated-stage-parent" / "package-root"
    outside = tmp_path / "not-package-data"
    previous_umask = os.umask(0o002)
    try:
        files = {
            "LICENSE", "README.md", ".github/SECURITY.md",
            "docs/security/SECURITY_SCAN_REPORT.json", "docs/ai/LOCAL_AI_STARTPROMPT.txt",
            "packaging/VERSION", "packaging/BUILD_CHANNEL",
            "src/assets/branding/open-hardware-control-icon.png",
            "src/modules/snapshot_manager/v1_0/helper.py",
            "src/modules/trcc_backend/v1_0/launcher.py",
            *(f"src/{name}" for name in constants["RUNTIME_FILES"]),
            *(f"packaging/{name}" for name in constants["PACKAGING_FILES"]),
            *(f"src/assets/branding/icons/open-hardware-control-{size}.png"
              for size in (22, 32, 48, 64, 128, 256)),
        }
        for relative in files:
            fixture = checkout / relative
            fixture.parent.mkdir(parents=True, exist_ok=True)
            fixture.write_bytes((relative + "\n").encode("utf-8"))
        package_root.mkdir(parents=True)
        outside.mkdir()
        (package_root / "outside-link").symlink_to(outside, target_is_directory=True)
        source_modes = {path: path.stat().st_mode for path in (checkout, *checkout.rglob("*"))}
        source_contents = {path: path.read_bytes() for path in checkout.rglob("*") if path.is_file()}
        parent_mode, outside_mode = package_root.parent.stat().st_mode, outside.stat().st_mode
        assert parent_mode & 0o777 == outside_mode & 0o777 == 0o775
        changed = []
        original_chmod = Path.chmod

        def recorded_chmod(path, mode, *args, **kwargs):
            changed.append(path)
            return original_chmod(path, mode, *args, **kwargs)

        monkeypatch.setattr(Path, "chmod", recorded_chmod)
        namespace = {
            "Path": Path, "shutil": shutil, "ROOT": checkout,
            "SRC_DIR": checkout / "src", "PACKAGING_DIR": checkout / "packaging",
            "DOC_DIRS": (), "VERSION": "fixture", "CHANNEL": "INTERN", **constants,
        }
        exec(compile(ast.Module(body=[install], type_ignores=[]), "<real-runtime-stage>", "exec"), namespace)
        namespace["install_runtime_tree"](package_root)
    finally:
        os.umask(previous_umask)
    directories = [path for path in (package_root, *package_root.rglob("*"))
                   if not path.is_symlink() and path.is_dir()]
    assert directories and all(path.stat().st_mode & 0o7777 == 0o755 for path in directories)
    assert all(path == package_root or package_root in path.parents for path in changed)
    assert package_root.parent.stat().st_mode == parent_mode
    assert outside.stat().st_mode == outside_mode
    assert (package_root / "outside-link").is_symlink()
    assert all(path.stat().st_mode == mode for path, mode in source_modes.items())
    assert all(path.read_bytes() == content for path, content in source_contents.items())
    for name in ("open-hardware-control-dmi-memory-helper", "open-hardware-control-snapshot-helper",
                 "open-hardware-control-snapshot-admin-helper"):
        assert (package_root / "usr/libexec" / name).stat().st_mode & 0o777 == 0o755
    assert (package_root / "usr/share/polkit-1/actions" / POLICIES[0]).stat().st_mode & 0o777 == 0o644
