"""Standard-library runner for pre-reveal Contract E self-tests."""

from __future__ import annotations

import importlib
import json
import sys
import traceback
from pathlib import Path
from typing import Any


MODULES = (
    "research.contract_e_fresh_reproduction.tests.test_spec_loader",
    "research.contract_e_fresh_reproduction.tests.test_preregistered",
    "research.contract_e_fresh_reproduction.tests.test_cli_eval",
    "research.contract_e_fresh_reproduction.tests.test_fixtures",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_tests() -> dict[str, Any]:
    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    records: list[dict[str, Any]] = []
    passed = 0
    failed = 0
    errors = 0

    for module_name in MODULES:
        module = importlib.import_module(module_name)
        names = sorted(name for name in dir(module) if name.startswith("test_"))
        for name in names:
            fn = getattr(module, name)
            if not callable(fn):
                continue
            node = f"{module_name}:{name}"
            try:
                fn()
            except AssertionError as exc:
                failed += 1
                records.append(
                    {
                        "id": node,
                        "status": "fail",
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                )
            except Exception as exc:  # noqa: BLE001 — runner must surface unexpected errors
                errors += 1
                records.append(
                    {
                        "id": node,
                        "status": "error",
                        "error": f"{type(exc).__name__}: {exc}",
                        "traceback": traceback.format_exc(),
                    }
                )
            else:
                passed += 1
                records.append({"id": node, "status": "pass"})

    summary = {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "total": passed + failed + errors,
        "ok": failed == 0 and errors == 0,
    }
    return {
        "command": [sys.executable, "-m", "research.contract_e_fresh_reproduction.run_tests"],
        "summary": summary,
        "tests": records,
    }


def main() -> int:
    payload = run_tests()
    out_path = Path(__file__).resolve().parent / "self_test_results.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    summary = payload["summary"]
    for record in payload["tests"]:
        mark = {"pass": ".", "fail": "F", "error": "E"}[record["status"]]
        sys.stdout.write(mark)
    sys.stdout.write("\n")
    sys.stdout.write(
        f"{summary['passed']} passed, {summary['failed']} failed, "
        f"{summary['errors']} errors, {summary['total']} total\n"
    )
    if not summary["ok"]:
        for record in payload["tests"]:
            if record["status"] == "pass":
                continue
            sys.stdout.write(f"\n{record['status'].upper()} {record['id']}\n")
            sys.stdout.write(record.get("traceback") or record.get("error") or "")
            sys.stdout.write("\n")
    sys.stdout.write(f"wrote {out_path}\n")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
