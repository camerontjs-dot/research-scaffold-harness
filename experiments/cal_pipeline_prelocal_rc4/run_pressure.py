from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType


def _site_packages(python: Path) -> list[str]:
    result = subprocess.run(
        [str(python), "-c", "import json,site; print(json.dumps(site.getsitepackages()))"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    value = json.loads(result.stdout)
    if not isinstance(value, list) or not value or not all(isinstance(row, str) for row in value):
        raise RuntimeError(f"invalid site-packages discovery from {python}: {value!r}")
    return value


def _load_rc1(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("cal_pipeline_prelocal_rc1_frozen_driver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen RC1 driver: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = Path.cwd().resolve()
    additions: list[str] = [
        str(root / "deps/claimgate/src"),
        str(root / "deps/eb/src"),
        str(root / "deps/cal/src"),
    ]
    for name in (".venv-cg", ".venv-eb", ".venv-cal"):
        additions.extend(_site_packages(root / name / "bin/python"))

    current = os.environ.get("PYTHONPATH", "")
    ordered: list[str] = []
    for row in additions + ([current] if current else []):
        if row and row not in ordered:
            ordered.append(row)
    os.environ["PYTHONPATH"] = os.pathsep.join(ordered)

    rc1_out = root / "build/cal_pipeline_prelocal_rc1"
    rc4_out = root / "build/cal_pipeline_prelocal_rc4"
    saved_logs = root / "build/_cal_pipeline_prelocal_rc4_component_logs"
    if saved_logs.exists():
        shutil.rmtree(saved_logs)
    component_logs = rc4_out / "component-logs"
    if component_logs.exists():
        shutil.copytree(component_logs, saved_logs)

    driver_path = root / "experiments/cal_pipeline_prelocal_rc1/run_pressure.py"
    rc1 = _load_rc1(driver_path)
    original_argv = sys.argv[:]
    try:
        sys.argv = [str(driver_path), "--root", str(root)]
        code = rc1.main()
    finally:
        sys.argv = original_argv

    if not rc1_out.exists():
        raise RuntimeError("frozen RC1 driver produced no evidence directory")
    if rc4_out.exists():
        shutil.rmtree(rc4_out)
    shutil.copytree(rc1_out, rc4_out)

    if saved_logs.exists():
        target = rc4_out / "component-logs"
        target.mkdir(parents=True, exist_ok=True)
        for path in saved_logs.iterdir():
            shutil.copy2(path, target / path.name)

    result_path = rc4_out / "RESULT.json"
    if not result_path.exists():
        raise RuntimeError("frozen RC1 driver produced no RESULT.json")
    value = json.loads(result_path.read_text(encoding="utf-8"))
    value["manifest"] = json.loads(
        (root / "experiments/cal_pipeline_prelocal_rc4/MANIFEST.json").read_text(encoding="utf-8")
    )
    value["apparatus_successor"] = {
        "reused_scientific_driver": "experiments/cal_pipeline_prelocal_rc1/run_pressure.py",
        "load_mode": "unique importlib module identity",
        "delta": [
            "exact venv site-packages exposed after predecessor symlink dereference",
            "exact checked-out ClaimGate/EB/CAL src roots exposed",
            "no RC2/RC3 wrapper import chain",
            "preserve component logs and frozen-driver evidence",
        ],
    }
    value["interpreter_environment"] = {
        "pythonpath_entries": ordered,
        "purpose": "apparatus-only restoration of dependency visibility",
    }
    result_path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
