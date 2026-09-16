from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

CURRENT_CAL = "847cc970642bb648dc994b929c2053b5c9d4648c"
RESOLVER_AUTHORITY = "1d33e0612befcf8016816197c90c062373796df9"
PREDECESSOR_RESOLVER = "43b571464734325277374ee81098553fb7c1b944"
POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
MATERIALIZER_BLOB = "ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde"


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object in {path}")
    return value


def _reject(fn, label: str) -> str:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - deliberate hostile-boundary capture
        return f"{type(exc).__name__}: {exc}"
    raise RuntimeError(f"hostile control unexpectedly succeeded: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--cal-root", type=Path, required=True)
    parser.add_argument("--apparatus", type=Path, required=True)
    parser.add_argument("--resolver-root", type=Path, required=True)
    parser.add_argument("--predecessor-resolver-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA
    from claim_audit_lab.production_v1.bundle_input import prepare_contract_b_input
    from claim_audit_lab.production_v1.semantic.engine import audit

    if SEMANTIC_IMPLEMENTATION_SHA != CURRENT_CAL:
        raise RuntimeError(
            f"installed CAL semantic authority drift: {SEMANTIC_IMPLEMENTATION_SHA} != {CURRENT_CAL}"
        )

    materializer_path = (
        args.cal_root
        / "research/contract_c2_current_cal_producer_conformance_rc1/materialize.py"
    )
    materializer = _load_module("pipeline_freeze_exact_cal_c2_materializer", materializer_path)
    if getattr(materializer, "SEMANTIC_IMPLEMENTATION_SHA", None) != CURRENT_CAL:
        raise RuntimeError("hard-bound materializer semantic authority drift")

    sys.path.insert(0, str(args.apparatus.resolve()))
    try:
        from validators import contract_c_v2 as c2  # type: ignore
    finally:
        sys.path.pop(0)

    resolver_path = (
        args.resolver_root
        / "research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json"
    )
    predecessor_path = (
        args.predecessor_resolver_root
        / "research/contract_c_successor_ground_up_20260913/PHASE_1_5_POLICY_RESOLVER.json"
    )
    resolver = _load_json(resolver_path)
    predecessor = _load_json(predecessor_path)
    entries = resolver.get("entries")
    predecessor_entries = predecessor.get("entries")
    if not isinstance(entries, list) or not isinstance(predecessor_entries, list):
        raise RuntimeError("resolver entries missing")

    prepared = prepare_contract_b_input(args.bundle, args.target)
    context = prepared.context
    result = audit(context)
    unsealed = materializer.materialize_unsealed(
        context,
        result,
        policy_resolver_commit_sha=RESOLVER_AUTHORITY,
    )
    sealed = c2.seal(unsealed)
    c2.validate_object(sealed)
    c2.verify_contract_b_references(
        sealed,
        exact_contract_b=unsealed["contract_b"],
        evidence_index={
            (passage.source_id, passage.passage_id)
            for passage in context.evidence_world.admitted_passages
        },
    )
    resolved = c2.verify_policy_resolution(
        sealed,
        independently_selected_resolver_commit_sha=RESOLVER_AUTHORITY,
        resolver_entries=entries,
    )
    if resolved.get("semantic_implementation_sha") != CURRENT_CAL:
        raise RuntimeError("resolver returned wrong semantic implementation")
    if resolved.get("policy_sha256") != POLICY_SHA256:
        raise RuntimeError("resolver returned wrong policy digest")
    if resolved.get("projection_blob") != MATERIALIZER_BLOB:
        raise RuntimeError("resolver returned wrong materializer blob")

    controls: dict[str, str] = {}

    predecessor_bound = copy.deepcopy(unsealed)
    predecessor_bound["producer"]["policy_resolver_commit_sha"] = PREDECESSOR_RESOLVER
    predecessor_bound = c2.seal(predecessor_bound)
    controls["predecessor_resolver_rejects_current_cal"] = _reject(
        lambda: c2.verify_policy_resolution(
            predecessor_bound,
            independently_selected_resolver_commit_sha=PREDECESSOR_RESOLVER,
            resolver_entries=predecessor_entries,
        ),
        "predecessor resolver accepted current CAL",
    )

    wrong_policy = copy.deepcopy(unsealed)
    wrong_policy["producer"]["policy_sha256"] = "0" * 64
    wrong_policy = c2.seal(wrong_policy)
    controls["wrong_policy_digest_rejected"] = _reject(
        lambda: c2.verify_policy_resolution(
            wrong_policy,
            independently_selected_resolver_commit_sha=RESOLVER_AUTHORITY,
            resolver_entries=entries,
        ),
        "wrong policy digest",
    )

    wrong_resolver = copy.deepcopy(unsealed)
    wrong_resolver["producer"]["policy_resolver_commit_sha"] = PREDECESSOR_RESOLVER
    wrong_resolver = c2.seal(wrong_resolver)
    controls["resolver_commit_substitution_rejected"] = _reject(
        lambda: c2.verify_policy_resolution(
            wrong_resolver,
            independently_selected_resolver_commit_sha=RESOLVER_AUTHORITY,
            resolver_entries=entries,
        ),
        "resolver commit substitution",
    )

    canonical = c2.canonical_bytes(sealed)
    c2_path = args.out_dir / "contract_c2.json"
    c2_path.write_bytes(canonical)
    whole_sha = c2.whole_object_sha256(sealed)

    (args.out_dir / "expected_contract_b.json").write_text(
        json.dumps(unsealed["contract_b"], sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    proposition = sealed["propositions"][0]["proposition"]
    (args.out_dir / "decision_context.json").write_text(
        json.dumps(
            {
                "proposition_id": proposition["proposition_id"],
                "target": {
                    "kind": "claim",
                    "id": proposition["proposition_id"],
                    "content_sha256": proposition["content_sha256"],
                },
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
    summary = {
        "cal_conclusion": result.conclusion.value,
        "cal_failure_code": None if result.failure_code is None else result.failure_code.value,
        "semantic_implementation_sha": CURRENT_CAL,
        "resolver_authority": RESOLVER_AUTHORITY,
        "policy_sha256": POLICY_SHA256,
        "materializer_blob": MATERIALIZER_BLOB,
        "resolved_row": resolved,
        "structural_c2_validation": "pass",
        "contract_b_reference_validation": "pass",
        "producer_policy_resolution": "pass",
        "whole_object_sha256": whole_sha,
        "hostile_controls": controls,
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
