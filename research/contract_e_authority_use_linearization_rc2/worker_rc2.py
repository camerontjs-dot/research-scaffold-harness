#!/usr/bin/env python3
"""Process-isolated execution worker used only by the RC2 evaluator."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", required=True)
    p.add_argument("--apparatus-e", required=True)
    p.add_argument("--independent-e", required=True)
    p.add_argument("--db", required=True)
    p.add_argument("--decision", required=True)
    p.add_argument("--intent", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--evaluation-time", default="2026-09-04T12:00:00Z")
    a = p.parse_args()

    candidate = load_module("rc2_candidate_worker", Path(a.candidate).resolve())
    e_ref = load_module(
        "rc2_contract_e_reference_worker",
        Path(a.apparatus_e).resolve()
        / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate/reference.py",
    )
    e_ind = load_module("rc2_contract_e_independent_worker", Path(a.independent_e).resolve())
    decision = json.loads(Path(a.decision).read_text(encoding="utf-8"))
    intent = json.loads(Path(a.intent).read_text(encoding="utf-8"))

    try:
        result = candidate.execute(
            a.db,
            decision=decision,
            intent=intent,
            evaluation_time=a.evaluation_time,
            canonical_bytes=e_ref.canonical_bytes,
            contract_e_reference_evaluate=e_ref.evaluate,
            contract_e_independent_evaluate=e_ind.evaluate,
        )
        payload = {"status": "returned", "result": result}
        code = 0
    except Exception as exc:
        payload = {"status": "exception", "exception_type": type(exc).__name__, "message": str(exc)}
        code = 2
    Path(a.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
