"""Every dynamic GPU fan workflow state translates without hardware or Qt."""

import ast
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from localization_catalog import UI_TRANSLATIONS


def test_all_five_fan_workflow_states_translate_in_all_supported_languages():
    path = ROOT / "src/modules/gpu_control/v1_0/fan_ui.py"
    tree = ast.parse(path.read_text())
    method = next(node for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef) and node.name == "_update_fan_workflow")
    namespace = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), "exec"), namespace)
    sources = [node.value for node in ast.walk(method)
               if isinstance(node, ast.Constant) and isinstance(node.value, str)
               and (node.value.startswith("1/3") or node.value.startswith("2/3") or node.value.startswith("✓"))]
    assert len(sources) == 5
    for language, translations in UI_TRANSLATIONS.items():
        observed = []
        label = SimpleNamespace(setText=observed.append)
        for index in range(5):
            host = SimpleNamespace(
                fan_workflow_status=label, preview_active=index == 0, tested=index == 1,
                candidate={"fan_control_enabled": True} if index == 1 else None,
                baseline={"fan_control_enabled": index == 3},
                _fan_changes=lambda selected=index: selected == 2,
                tr=lambda source, table=translations: table[source],
            )
            namespace["_update_fan_workflow"](host)
        assert observed == [translations[source] for source in sources]
        if language != "de":
            assert all(translations[source] != source for source in sources)
