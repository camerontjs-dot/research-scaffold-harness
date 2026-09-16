from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    root = Path.cwd().resolve()
    eb_src = root / "deps/eb/src"
    current = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = str(eb_src) + (os.pathsep + current if current else "")

    rc1_out = root / "build/cal_pipeline_prelocal_rc1"
    rc2_out = root / "build/cal_pipeline_prelocal_rc2"
    saved_logs = root / "build/_cal_pipeline_prelocal_rc2_component_logs"
    if saved_logs.exists():
        shutil.rmtree(saved_logs)
    component_logs = rc2_out / "component-logs"
    if component_logs.exists():
        shutil.copytree(component_logs, saved_logs)

    rc1_dir = root / "experiments/cal_pipeline_prelocal_rc1"
    sys.path.insert(0, str(rc1_dir))
    import run_pressure as rc1  # type: ignore  # noqa: PLC0415

    original_argv = sys.argv[:]
    try:
        sys.argv = [str(rc1_dir / "run_pressure.py"), "--root", str(root)]
        code = rc1.main()
    finally:
        sys.argv = original_argv

    if saved_logs.exists():
        target = rc1_out / "component-logs"
        target.mkdir(parents=True, exist_ok=True)
        for path in saved_logs.iterdir():
            shutil.copy2(path, target / path.name)

    if rc2_out.exists():
        shutil.rmtree(rc2_out)
    shutil.copytree(rc1_out, rc2_out)
    result_path = rc2_out / "RESULT.json"
    if result_path.exists():
        value = json.loads(result_path.read_text(encoding="utf-8"))
        value["manifest"] = json.loads(
            (root / "experiments/cal_pipeline_prelocal_rc2/MANIFEST.json").read_text(encoding="utf-8")
        )
        value["apparatus_successor"] = {
            "reused_scientific_driver": "experiments/cal_pipeline_prelocal_rc1/run_pressure.py",
            "delta": ["explicit EB src PYTHONPATH", "preserve component logs"],
        }
        result_path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
