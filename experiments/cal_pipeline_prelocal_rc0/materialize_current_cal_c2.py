from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA
from claim_audit_lab.production_v1.bundle_input import prepare_contract_b_input
from claim_audit_lab.production_v1.semantic.engine import AuditResult, PassageTrace, audit, compose
from claim_audit_lab.production_v1.semantic.models import CategoricalRelation, Conclusion, FailureCode

POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
POLICY_RESOLVER_COMMIT = "43b571464734325277374ee81098553fb7c1b944"


def public_terminal_state(result: AuditResult) -> tuple[str, str]:
    if result.conclusion is Conclusion.SUPPORTED:
        return "supported", "categorical_support"
    if result.conclusion is Conclusion.CONTRADICTED:
        return "contradicted", "categorical_refutation"
    if result.failure_code is FailureCode.MIXED_RELATIONS:
        return "not_checkable", "MIXED_RELATIONS"
    if result.failure_code is FailureCode.UNSUPPORTED_SEMANTIC_FAMILY:
        return "not_checkable", "UNSUPPORTED_SEMANTIC_FAMILY"
    if result.failure_code is FailureCode.RELATION_UNRESOLVED:
        has_unresolved = any(
            trace.relation is not None
            and trace.relation.categorical_relation is CategoricalRelation.UNRESOLVED
            for trace in result.traces
        )
        return (
            ("not_checkable", "unresolved_categorical_relation")
            if has_unresolved
            else ("not_checkable", "no_deciding_relation")
        )
    if result.failure_code is FailureCode.NO_DECIDING_RELATION:
        return "not_checkable", "no_deciding_relation"
    reason = result.failure_code.value if result.failure_code is not None else result.conclusion.value
    raise ValueError(f"unrepresentable current CAL terminal state: {reason}")


def derive_basis_passage_ids(context: Any, result: AuditResult) -> tuple[tuple[str, ...], ...]:
    _, reason = public_terminal_state(result)
    if reason in {"no_deciding_relation", "UNSUPPORTED_SEMANTIC_FAMILY"}:
        return ()
    traces = tuple(result.traces)
    minimal: list[frozenset[str]] = []
    for size in range(1, len(traces) + 1):
        for indexes in combinations(range(len(traces)), size):
            subset: tuple[PassageTrace, ...] = tuple(traces[index] for index in indexes)
            replay = compose(context, subset)
            if public_terminal_state(replay) != public_terminal_state(result):
                continue
            ids = frozenset(trace.passage_id for trace in subset)
            if any(existing <= ids for existing in minimal):
                continue
            minimal.append(ids)
    return tuple(sorted(tuple(sorted(group)) for group in minimal))


def relation_label(trace: PassageTrace) -> str:
    if trace.relation is None:
        return "non_polarized"
    relation = trace.relation.categorical_relation
    if relation is CategoricalRelation.SUPPORTS:
        return "supports"
    if relation is CategoricalRelation.REFUTES:
        return "refutes"
    return "non_polarized"


def materialize_unsealed(context: Any, result: AuditResult, profile: str) -> dict[str, Any]:
    if result.audit_context_sha256 != context.context_sha256:
        raise ValueError("result/context mismatch")
    if result.proposition_sha256 != context.proposition.sha256:
        raise ValueError("result/proposition mismatch")
    if result.evidence_world_sha256 != context.evidence_world.evidence_world_sha256:
        raise ValueError("result/evidence-world mismatch")

    verdict, reason = public_terminal_state(result)
    basis_ids = derive_basis_passage_ids(context, result)
    causal_ids = {passage_id for group in basis_ids for passage_id in group}
    participants: list[dict[str, Any]] = []
    refs: dict[str, dict[str, str]] = {}
    for trace in result.traces:
        passage = context.evidence_world.passage(trace.passage_id)
        ref = {"source_id": passage.source_id, "passage_id": passage.passage_id}
        refs[passage.passage_id] = ref
        participants.append(
            {
                "evidence_ref": ref,
                "relation": relation_label(trace),
                "role": "causal" if trace.passage_id in causal_ids else "residual",
            }
        )
    basis_groups = [[refs[passage_id] for passage_id in group] for group in basis_ids]
    completion = (
        "assessed"
        if result.conclusion in {Conclusion.SUPPORTED, Conclusion.CONTRADICTED}
        else "not_checkable"
    )
    return {
        "profile": profile,
        "contract_b": {
            "contract_version": context.evidence_world.contract_b_version,
            "bundle_id": context.evidence_world.bundle_id,
            "bundle_hash": context.evidence_world.bundle_hash,
        },
        "producer": {
            "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
            "policy_sha256": POLICY_SHA256,
            "policy_resolver_commit_sha": POLICY_RESOLVER_COMMIT,
        },
        "execution": {"state": "completed"},
        "propositions": [
            {
                "proposition": {
                    "proposition_id": context.proposition.proposition_id,
                    "content_sha256": f"sha256:{context.proposition.sha256}",
                },
                "execution": {"state": "completed", "completion": completion},
                "terminal": {"verdict": verdict, "reason": reason},
                "participants": participants,
                "basis_groups": basis_groups,
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--apparatus", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(args.apparatus.resolve()))
    from validators import contract_c_v2 as c2  # noqa: PLC0415

    prepared = prepare_contract_b_input(args.bundle, args.target)
    context = prepared.context
    result = audit(context)
    unsealed = materialize_unsealed(context, result, c2.PROFILE)
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

    canonical = c2.canonical_bytes(sealed)
    c2_path = args.out_dir / "contract_c2.json"
    c2_path.write_bytes(canonical)
    whole_sha = c2.whole_object_sha256(sealed)

    authority_status = "accepted"
    authority_error: str | None = None
    try:
        c2.verify_policy_resolution(
            sealed,
            independently_selected_resolver_commit_sha=c2.POLICY_RESOLVER_FIXTURE_COMMIT,
            resolver_entries=[
                {
                    "semantic_implementation_sha": c2.CAL_RC1_IMPLEMENTATION,
                    "policy_sha256": c2.CAL_RC1_POLICY_SHA256,
                }
            ],
        )
    except Exception as exc:  # noqa: BLE001
        authority_status = "rejected"
        authority_error = str(exc)

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
        "current_cal_semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "c2_frozen_cal_rc1_implementation": c2.CAL_RC1_IMPLEMENTATION,
        "structural_c2_validation": "pass",
        "contract_b_reference_validation": "pass",
        "whole_object_sha256": whole_sha,
        "producer_policy_resolution_against_frozen_c2_authority": authority_status,
        "producer_policy_resolution_error": authority_error,
        "producer_authority_gap_observed": authority_status != "accepted",
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
