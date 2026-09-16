from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apparatus", type=Path, required=True)
    parser.add_argument("--contract-d", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    successor_dir = (
        args.apparatus
        / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate"
    )
    predecessor_tests = (
        args.apparatus
        / "docs/research/contract-e/v1-rc3-exact-currentness-jcs-20260902/candidate/test_candidate.py"
    )
    sys.path.insert(0, str(successor_dir))
    import reference as e  # type: ignore  # noqa: PLC0415

    helpers = load_module("pipeline_freeze_contract_e_helpers", predecessor_tests)
    helpers.e = e

    d_bytes = args.contract_d.read_bytes()
    d_sha = "sha256:" + hashlib.sha256(d_bytes).hexdigest()
    dry_target = helpers.target("pipeline:dry-target", "T")
    decision_ref = {
        "ref_id": "D",
        "kind": "contract_d_decision",
        "version": "1.0.0",
        "immutable_id": d_sha,
        "identity_sha256": e.reference_identity("contract_d_decision", "1.0.0", d_sha),
    }
    support = [{"id": "support:D", "artifact_type": "contract_d_candidate", "ref_id": "D"}]

    state, target = helpers.make_state(ref=dry_target)
    baseline_request = helpers.request(
        state,
        target,
        references=[target, decision_ref],
        support=support,
    )
    baseline = e.evaluate(state, baseline_request)

    revoked_state, revoked_target = helpers.make_state(
        ref=dry_target,
        revoked_at="2026-09-02T17:30:00Z",
    )
    revoked = e.evaluate(
        revoked_state,
        helpers.request(
            revoked_state,
            revoked_target,
            references=[revoked_target, decision_ref],
            support=support,
        ),
    )

    expired_state, expired_target = helpers.make_state(
        ref=dry_target,
        valid_until="2026-09-02T17:30:00Z",
    )
    expired = e.evaluate(
        expired_state,
        helpers.request(
            expired_state,
            expired_target,
            references=[expired_target, decision_ref],
            support=support,
        ),
    )

    wrong_target = helpers.target("pipeline:wrong-target", "W")
    wrong_target_request = helpers.request(
        state,
        target,
        target_ref=wrong_target["identity_sha256"],
        references=[wrong_target, decision_ref],
        support=support,
    )
    wrong_target_result = e.evaluate(state, wrong_target_request)

    duplicate = deepcopy(target)
    duplicate["ref_id"] = "T2"
    ambiguous_request = helpers.request(
        state,
        target,
        references=[target, duplicate, decision_ref],
        support=support,
    )
    ambiguous = e.evaluate(state, ambiguous_request)

    invalid_state = {
        "schema": e.STATE_SCHEMA,
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [],
    }
    nonconferring = e.evaluate(invalid_state, baseline_request)

    checks = {
        "baseline_authorized_with_independent_authority_state": bool(baseline["authorized"]),
        "revoked_denied": not bool(revoked["authorized"]),
        "expired_denied": not bool(expired["authorized"]),
        "wrong_target_denied": not bool(wrong_target_result["authorized"]),
        "ambiguous_target_denied": not bool(ambiguous["authorized"]),
        "contract_d_support_does_not_confer_without_authority_state": not bool(
            nonconferring["authorized"]
        ),
    }
    if not all(checks.values()):
        raise SystemExit(f"Contract E dry pressure failure: {checks}")

    summary = {
        "contract_d_sha256": d_sha,
        "checks": checks,
        "baseline_receipt_id": baseline.get("receipt_id"),
        "note": "Research-only dry authorization over synthetic target; no execution or mutation.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
