from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


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

    rc2_out = root / "build/cal_pipeline_prelocal_rc2"
    rc3_out = root / "build/cal_pipeline_prelocal_rc3"
    saved_logs = root / "build/_cal_pipeline_prelocal_rc3_component_logs"
    if saved_logs.exists():
        shutil.rmtree(saved_logs)
    component_logs = rc3_out / "component-logs"
    if component_logs.exists():
        shutil.copytree(component_logs, saved_logs)

    rc2_dir = root / "experiments/cal_pipeline_prelocal_rc2"
    sys.path.insert(0, str(rc2_dir))
    import run_pressure as rc2  # type: ignore  # noqa: PLC0415

    original_argv = sys.argv[:]
    try:
        sys.argv = [str(rc2_dir / "run_pressure.py")]
        code = rc2.main()
    finally:
        sys.argv = original_argv

    if saved_logs.exists():
        target = rc2_out / "component-logs"
        target.mkdir(parents=True, exist_ok=True)
        for path in saved_logs.iterdir():
            shutil.copy2(path, target / path.name)

    if rc3_out.exists():
        shutil.rmtree(rc3_out)
    shutil.copytree(rc2_out, rc3_out)

    result_path = rc3_out / "RESULT.json"
    if result_path.exists():
        value = json.loads(result_path.read_text(encoding="utf-8"))
        value["manifest"] = json.loads(
            (root / "experiments/cal_pipeline_prelocal_rc3/MANIFEST.json").read_text(encoding="utf-8")
        )
        value["apparatus_successor"] = {
            "reused_scientific_driver": "experiments/cal_pipeline_prelocal_rc1/run_pressure.py",
            "successor_chain": [
                "experiments/cal_pipeline_prelocal_rc2/run_pressure.py",
                "experiments/cal_pipeline_prelocal_rc3/run_pressure.py",
            ],
            "delta": [
                "discover exact installed site-packages for ClaimGate, EB, and CAL venvs",
                "prepend those site-packages plus exact checked-out src roots to PYTHONPATH",
                "preserve component logs and copy predecessor evidence into RC3 artifact",
            ],
        }
        value["interpreter_environment"] = {
            "pythonpath_entries": ordered,
            "purpose": "restore venv dependency visibility after predecessor Path.resolve() symlink dereference",
        }
        result_path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
