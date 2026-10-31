# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixed package worker, no shell, network, devices or external app commands."""
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from modules.profile_bundle.v1_0.archive import MAX_META, export_bundle, import_bundle
else:
    from .archive import MAX_META, export_bundle, import_bundle


def main():
    try:
        spec = Path(sys.argv[1])
        if spec.stat().st_size > MAX_META: raise ValueError("BUNDLE_METADATA_SIZE")
        job = json.loads(spec.read_bytes())
        if job["action"] == "export":
            result = export_bundle(job["path"], job["snapshot"], job.get("extra_roots", []))
        elif job["action"] == "import":
            result = import_bundle(job["path"], job["stage"])
        else: raise ValueError("BUNDLE_ACTION")
        print(json.dumps(dict(ok=True, result=result), ensure_ascii=False))
    except Exception as exc:
        print(json.dumps(dict(ok=False, error=type(exc).__name__ + ": " + str(exc)[:300])))
        return 1
    return 0


if __name__ == "__main__": raise SystemExit(main())
