"""Evaluator for Contract E Production Envelope Shadow RC0.

Runs only in temporary disposable roots. The candidate never mutates target bytes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

CASE_IDS = [
    "POS-FRESH-EXACT-UNSEEN",
    "NEG-RECEIPT-ONLY-REVOKED-NOW",
    "NEG-RECEIPT-ONLY-EXPIRED-NOW",
    "NEG-WRONG-SUBJECT",
    "NEG-WRONG-OPERATION",
    "NEG-WRONG-TARGET-REF",
    "NEG-DUPLICATE-TARGET-REFERENCE",
    "NEG-RELEVANT-BLOCKER",
    "NEG-DECISION-SUBSTITUTION",
    "NEG-EFFECT-SUBSTITUTION",
    "NEG-SCOPE-PARAM-SUBSTITUTION",
    "NEG-INTENT-ID-FORGERY",
    "NEG-TARGET-ID-SUBSTITUTION",
    "NEG-STALE-PRESTATE",
    "NEG-CONCURRENT-CHANGE-DURING-WINDOW",
    "NEG-PATH-TRAVERSAL",
    "NEG-SYMLINK-ESCAPE",
    "NEG-NONDISPOSABLE-ROOT",
    "NEG-REPLAY-IDEMPOTENCY-KEY",
    "NEG-MALFORMED-AUTHORITY",
    "NEG-MALFORMED-REQUEST",
    "NEG-CONTRACT-E-ENGINE-EXCEPTION",
    "NEG-CONTRACT-E-ENGINE-DISAGREEMENT",
    "NEG-CONTRACT-D-HOLD",
    "NEG-CONTRACT-D-NOT-APPLICABLE",
    "NEG-CONTRACT-D-EVALUATION-FAILED",
]

BASE_BYTES = b"---\ntitle: Shadow RC0 fixture\nstatus: draft\n---\nBody stays unchanged.\n"
CHANGED_BYTES = b"---\ntitle: Shadow RC0 fixture\nstatus: changed\n---\nExternal concurrent change.\n"
MARKER_NAME = ".contract-e-shadow-rc0-disposable"
MARKER_BYTES = b"CONTRACT_E_SHADOW_RC0_DISPOSABLE\n"
EVAL_TIME = "2026-09-04T12:00:00Z"
SUBJECT = "agent:shadow-executor"
DOMAIN = "mainframe.knowledge"
OPERATION = "knowledge.add_verified_tag"
SCOPE = "claim"
TARGET_CLASS = "cal.shadow-execution-intent"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_file_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@dataclass
class Modules:
    pep: Any
    d_core: Any
    d_validate: Any
    d_consume: Any
    e_ref: Any
    e_ind: Any


@dataclass
class Context:
    case_id: str
    root: Path
    target: Path
    journal: Path
    contract_d_bytes: bytes
    expectation: Any
    intent: dict[str, Any]
    authority_state: Any
    request: Any
    historical_receipt: Any = None
    ref_eval: Callable[[Any, Any], dict[str, Any]] | None = None
    ind_eval: Callable[[Any, Any], dict[str, Any]] | None = None
    hook: Callable[[Path], None] | None = None
    externally_mutated: bool = False


def load_modules(args: argparse.Namespace) -> Modules:
    apparatus_d = Path(args.apparatus_d).resolve()
    apparatus_e = Path(args.apparatus_e).resolve()
    independent_e = Path(args.independent_e).resolve()
    candidate = Path(args.candidate).resolve()

    sys.path.insert(0, str(apparatus_d))
    d_core = importlib.import_module("validators.contract_d_core")
    d_validate = importlib.import_module("validators.contract_d_validate")
    d_consume = importlib.import_module("validators.contract_d_consume")

    e_ref = load_file_module(
        "contract_e_rc3_target_successor",
        apparatus_e
        / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate/reference.py",
    )
    e_ind = load_file_module("contract_e_rc3_fresh_independent", independent_e)
    pep = load_file_module("contract_e_shadow_rc0_candidate", candidate)
    return Modules(pep, d_core, d_validate, d_consume, e_ref, e_ind)


def baseline_decision(content_sha: str) -> dict[str, Any]:
    return {
        "contract_d_version": "1.0.0",
        "input_authority": {
            "kind": "contract-c",
            "id": "shadow-c1",
            "immutable_id": "result-set:" + "a" * 64,
        },
        "policy": {"id": "mainframe.source-audit", "version": "1"},
        "target": {"kind": "knowledge", "id": "shadow-note-1", "content_sha256": content_sha},
        "evaluation": {"state": "completed", "disposition": "clear"},
        "effect": {
            "type": "knowledge.add_verified_tag",
            "version": "1",
            "params": {"scope": "claim"},
        },
    }


def expectation_for(mods: Modules, decision: dict[str, Any]):
    return mods.d_consume.ApplicabilityExpectation(
        input_authority=copy.deepcopy(decision["input_authority"]),
        policy=copy.deepcopy(decision["policy"]),
        target=copy.deepcopy(decision["target"]),
        requested_operation="knowledge.add_verified_tag",
        effect_params={"scope": "claim"},
    )


def compute_intent_id(mods: Modules, intent: dict[str, Any]) -> str:
    payload = {k: copy.deepcopy(v) for k, v in intent.items() if k != "intent_id"}
    return sha256_bytes(mods.e_ref.canonical_bytes(payload))


def build_intent(
    mods: Modules,
    contract_d_bytes: bytes,
    decision: dict[str, Any],
    *,
    relative_path: str,
    target_id_override: str | None = None,
    effect_id: str = "knowledge.add_verified_tag",
    effect_version: str = "1",
    effect_params: dict[str, Any] | None = None,
    idempotency_key: str,
) -> dict[str, Any]:
    intent = {
        "schema": "cal-production-envelope-shadow-intent-rc0",
        "intent_id": "sha256:" + "0" * 64,
        "contract_d_sha256": sha256_bytes(contract_d_bytes),
        "effect_id": effect_id,
        "effect_version": effect_version,
        "effect_params": {"scope": "claim"} if effect_params is None else copy.deepcopy(effect_params),
        "contract_d_target_kind": decision["target"]["kind"],
        "contract_d_target_id": (
            decision["target"]["id"] if target_id_override is None else target_id_override
        ),
        "target_root_id": "disposable-root",
        "target_relative_path": relative_path,
        "target_pre_state_sha256": decision["target"]["content_sha256"],
        "idempotency_key": idempotency_key,
    }
    intent["intent_id"] = compute_intent_id(mods, intent)
    return intent


def build_state_request(
    mods: Modules,
    intent: dict[str, Any],
    *,
    state_mutator: Callable[[dict[str, Any]], None] | None = None,
    request_mutator: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    ref_identity = mods.e_ref.reference_identity(
        "cal.shadow-execution-intent", "rc0", intent["intent_id"]
    )
    record = {
        "id": "authority-root",
        "basis_type": "policy",
        "subject_id": SUBJECT,
        "domain": DOMAIN,
        "operation": OPERATION,
        "scope": SCOPE,
        "target_class": TARGET_CLASS,
        "target_ref": ref_identity,
        "valid_from": "2026-09-04T00:00:00Z",
        "valid_until": "2026-09-05T00:00:00Z",
        "revoked_at": None,
        "parent_id": None,
        "delegated_by": None,
    }
    if state_mutator is not None:
        state_mutator(record)
    state = {
        "schema": "contract-e-authority-state-candidate-rc3",
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [record],
    }
    state["authority_state_id"] = mods.e_ref.authority_state_identity(state)

    ref = {
        "ref_id": "intent",
        "kind": "cal.shadow-execution-intent",
        "version": "rc0",
        "immutable_id": intent["intent_id"],
        "identity_sha256": ref_identity,
    }
    request = {
        "schema": "contract-e-authorization-request-candidate-rc3",
        "request_id": "shadow-request",
        "authority_state_id": state["authority_state_id"],
        "evaluation_time": EVAL_TIME,
        "subject_id": SUBJECT,
        "jurisdiction": {
            "domain": DOMAIN,
            "operation": OPERATION,
            "scope": SCOPE,
            "target_class": TARGET_CLASS,
            "target_ref": ref_identity,
        },
        "references": [ref],
        "supporting_artifacts": [],
        "conflicts": [],
        "residues": [],
    }
    if request_mutator is not None:
        request_mutator(request)
    return state, request


def make_historical_receipt(mods: Modules, intent: dict[str, Any]) -> dict[str, Any]:
    state, req = build_state_request(mods, intent)
    req["evaluation_time"] = "2026-09-04T10:00:00Z"
    return mods.e_ref.evaluate(state, req)


def prepare_context(
    mods: Modules,
    td: Path,
    case_id: str,
    *,
    decision: dict[str, Any] | None = None,
    actual_bytes: bytes = BASE_BYTES,
    expected_content_bytes: bytes = BASE_BYTES,
    marker: bool = True,
    relative_path: str = "note.md",
    target_id_override: str | None = None,
    expectation_mutator: Callable[[Any], Any] | None = None,
    state_mutator: Callable[[dict[str, Any]], None] | None = None,
    request_mutator: Callable[[dict[str, Any]], None] | None = None,
    historical: bool = False,
) -> Context:
    root = td / case_id.lower().replace("_", "-")
    root.mkdir(parents=True)
    if marker:
        (root / MARKER_NAME).write_bytes(MARKER_BYTES)

    target = root / "note.md"
    target.write_bytes(actual_bytes)

    expected_sha = sha256_bytes(expected_content_bytes)
    if decision is None:
        decision = baseline_decision(expected_sha)
    d_bytes = mods.d_core.canonical_json_bytes(decision)
    expectation = expectation_for(mods, decision)
    if expectation_mutator is not None:
        expectation = expectation_mutator(expectation)

    intent = build_intent(
        mods,
        d_bytes,
        decision,
        relative_path=relative_path,
        target_id_override=target_id_override,
        idempotency_key=f"key-{case_id}",
    )
    state, request = build_state_request(
        mods, intent, state_mutator=state_mutator, request_mutator=request_mutator
    )
    historical_receipt = make_historical_receipt(mods, intent) if historical else None
    return Context(
        case_id=case_id,
        root=root,
        target=target,
        journal=root / "journal.jsonl",
        contract_d_bytes=d_bytes,
        expectation=expectation,
        intent=intent,
        authority_state=state,
        request=request,
        historical_receipt=historical_receipt,
        ref_eval=mods.e_ref.evaluate,
        ind_eval=mods.e_ind.evaluate,
    )


def invoke(mods: Modules, ctx: Context) -> dict[str, Any]:
    return mods.pep.shadow_evaluate(
        contract_d_bytes=ctx.contract_d_bytes,
        applicability_expectation=ctx.expectation,
        intent=ctx.intent,
        target_root=ctx.root,
        authority_state=ctx.authority_state,
        authorization_request=ctx.request,
        journal_path=ctx.journal,
        contract_d_require_canonical_bytes=mods.d_validate.require_canonical_bytes,
        contract_d_consume=mods.d_consume.consume,
        contract_d_validate_effect=mods.d_core.validate_effect,
        contract_e_reference_evaluate=ctx.ref_eval or mods.e_ref.evaluate,
        contract_e_independent_evaluate=ctx.ind_eval or mods.e_ind.evaluate,
        intent_canonical_bytes=mods.e_ref.canonical_bytes,
        contract_e_reference_identity=mods.e_ref.reference_identity,
        historical_receipt=ctx.historical_receipt,
        research_after_authorization_hook=ctx.hook,
    )


def case_context(mods: Modules, td: Path, case_id: str) -> Context:
    if case_id == "POS-FRESH-EXACT-UNSEEN":
        return prepare_context(mods, td, case_id)

    if case_id == "NEG-RECEIPT-ONLY-REVOKED-NOW":
        return prepare_context(
            mods,
            td,
            case_id,
            historical=True,
            state_mutator=lambda r: r.__setitem__("revoked_at", EVAL_TIME),
        )

    if case_id == "NEG-RECEIPT-ONLY-EXPIRED-NOW":
        return prepare_context(
            mods,
            td,
            case_id,
            historical=True,
            state_mutator=lambda r: r.__setitem__("valid_until", "2026-09-04T11:59:59Z"),
        )

    if case_id == "NEG-WRONG-SUBJECT":
        return prepare_context(
            mods, td, case_id, request_mutator=lambda r: r.__setitem__("subject_id", "agent:other")
        )

    if case_id == "NEG-WRONG-OPERATION":
        def wrong_op(req: dict[str, Any]) -> None:
            req["jurisdiction"]["operation"] = "knowledge.cite_as_evidence"
        return prepare_context(mods, td, case_id, request_mutator=wrong_op)

    if case_id == "NEG-WRONG-TARGET-REF":
        ctx = prepare_context(mods, td, case_id)
        other = mods.e_ref.reference_identity(
            "cal.shadow-execution-intent", "rc0", "sha256:" + "f" * 64
        )
        ctx.request["references"][0]["immutable_id"] = "sha256:" + "f" * 64
        ctx.request["references"][0]["identity_sha256"] = other
        ctx.request["jurisdiction"]["target_ref"] = other
        return ctx

    if case_id == "NEG-DUPLICATE-TARGET-REFERENCE":
        ctx = prepare_context(mods, td, case_id)
        dup = copy.deepcopy(ctx.request["references"][0])
        dup["ref_id"] = "intent-dup"
        ctx.request["references"].append(dup)
        return ctx

    if case_id == "NEG-RELEVANT-BLOCKER":
        return prepare_context(
            mods,
            td,
            case_id,
            request_mutator=lambda r: r["conflicts"].append(
                {"id": "c1", "relevant": True, "status": "unresolved"}
            ),
        )

    if case_id == "NEG-DECISION-SUBSTITUTION":
        ctx = prepare_context(mods, td, case_id)
        modified = baseline_decision(sha256_bytes(BASE_BYTES))
        modified["policy"]["version"] = "2"
        ctx.contract_d_bytes = mods.d_core.canonical_json_bytes(modified)
        ctx.expectation = expectation_for(mods, modified)
        return ctx

    if case_id == "NEG-EFFECT-SUBSTITUTION":
        d = baseline_decision(sha256_bytes(BASE_BYTES))
        d["effect"] = {"type": "knowledge.cite_as_evidence", "version": "1"}
        return prepare_context(mods, td, case_id, decision=d)

    if case_id == "NEG-SCOPE-PARAM-SUBSTITUTION":
        d = baseline_decision(sha256_bytes(BASE_BYTES))
        d["effect"]["params"]["scope"] = "object"
        return prepare_context(mods, td, case_id, decision=d)

    if case_id == "NEG-INTENT-ID-FORGERY":
        ctx = prepare_context(mods, td, case_id)
        ctx.intent["intent_id"] = "sha256:" + "e" * 64
        return ctx

    if case_id == "NEG-TARGET-ID-SUBSTITUTION":
        d = baseline_decision(sha256_bytes(BASE_BYTES))
        d["target"]["id"] = "different-target-id"
        return prepare_context(
            mods, td, case_id, decision=d, target_id_override="shadow-note-1"
        )

    if case_id == "NEG-STALE-PRESTATE":
        return prepare_context(
            mods, td, case_id, actual_bytes=CHANGED_BYTES, expected_content_bytes=BASE_BYTES
        )

    if case_id == "NEG-CONCURRENT-CHANGE-DURING-WINDOW":
        ctx = prepare_context(mods, td, case_id)
        def change(path: Path) -> None:
            path.write_bytes(CHANGED_BYTES)
        ctx.hook = change
        ctx.externally_mutated = True
        return ctx

    if case_id == "NEG-PATH-TRAVERSAL":
        ctx = prepare_context(mods, td, case_id, relative_path="../outside.md")
        (ctx.root.parent / "outside.md").write_bytes(BASE_BYTES)
        return ctx

    if case_id == "NEG-SYMLINK-ESCAPE":
        outside_dir = td / "symlink-outside"
        outside_dir.mkdir(exist_ok=True)
        outside = outside_dir / f"{case_id}.md"
        outside.write_bytes(BASE_BYTES)
        ctx = prepare_context(mods, td, case_id, relative_path="link.md")
        link = ctx.root / "link.md"
        link.symlink_to(outside)
        return ctx

    if case_id == "NEG-NONDISPOSABLE-ROOT":
        return prepare_context(mods, td, case_id, marker=False)

    if case_id == "NEG-REPLAY-IDEMPOTENCY-KEY":
        return prepare_context(mods, td, case_id)

    if case_id == "NEG-MALFORMED-AUTHORITY":
        ctx = prepare_context(mods, td, case_id)
        ctx.authority_state = {"bad": True}
        return ctx

    if case_id == "NEG-MALFORMED-REQUEST":
        ctx = prepare_context(mods, td, case_id)
        ctx.request = {"bad": True}
        return ctx

    if case_id == "NEG-CONTRACT-E-ENGINE-EXCEPTION":
        ctx = prepare_context(mods, td, case_id)
        def boom(_state: Any, _request: Any) -> dict[str, Any]:
            raise RuntimeError("seeded engine failure")
        ctx.ref_eval = boom
        return ctx

    if case_id == "NEG-CONTRACT-E-ENGINE-DISAGREEMENT":
        ctx = prepare_context(mods, td, case_id)
        exact_ind = mods.e_ind.evaluate
        def disagree(state: Any, request: Any) -> dict[str, Any]:
            out = copy.deepcopy(exact_ind(state, request))
            out["authorized"] = not bool(out.get("authorized"))
            return out
        ctx.ind_eval = disagree
        return ctx

    if case_id == "NEG-CONTRACT-D-HOLD":
        d = baseline_decision(sha256_bytes(BASE_BYTES))
        d["evaluation"]["disposition"] = "hold"
        return prepare_context(mods, td, case_id, decision=d)

    if case_id == "NEG-CONTRACT-D-NOT-APPLICABLE":
        def mismatch(exp: Any):
            return mods.d_consume.ApplicabilityExpectation(
                input_authority=copy.deepcopy(exp.input_authority),
                policy=copy.deepcopy(exp.policy),
                target={**copy.deepcopy(exp.target), "id": "other-target"},
                requested_operation=exp.requested_operation,
                effect_params=copy.deepcopy(exp.effect_params),
            )
        return prepare_context(mods, td, case_id, expectation_mutator=mismatch)

    if case_id == "NEG-CONTRACT-D-EVALUATION-FAILED":
        d = baseline_decision(sha256_bytes(BASE_BYTES))
        d["evaluation"] = {"state": "failed"}
        d.pop("effect")
        return prepare_context(mods, td, case_id, decision=d)

    raise KeyError(case_id)


def target_digest(path: Path) -> str | None:
    try:
        return sha256_bytes(path.read_bytes())
    except Exception:
        return None


def run_candidate_case(mods: Modules, td: Path, case_id: str) -> dict[str, Any]:
    ctx = case_context(mods, td, case_id)
    before = target_digest(ctx.target)

    if case_id == "NEG-REPLAY-IDEMPOTENCY-KEY":
        first = invoke(mods, ctx)
        if not first.get("shadow_allowed"):
            return {
                "case_id": case_id,
                "expected": False,
                "observed": False,
                "pass": False,
                "apparatus_failure": "replay_setup_first_call_did_not_allow",
                "first": first,
            }
        result = invoke(mods, ctx)
    else:
        result = invoke(mods, ctx)

    after = target_digest(ctx.target)
    expected = case_id == "POS-FRESH-EXACT-UNSEEN"
    observed = bool(result.get("shadow_allowed"))

    target_integrity_ok = True
    if not ctx.externally_mutated:
        target_integrity_ok = before == after
    else:
        target_integrity_ok = result.get("shadow_allowed") is False and after != before

    execution_flag_ok = result.get("execution_occurred") is False
    result_ok = observed == expected
    if expected:
        result_ok = (
            result_ok
            and result.get("idempotency_state") == "reserved"
            and result.get("contract_e_reference_authorized") is True
            and result.get("contract_e_independent_authorized") is True
        )
    return {
        "case_id": case_id,
        "expected": expected,
        "observed": observed,
        "pass": bool(result_ok and target_integrity_ok and execution_flag_ok),
        "target_before": before,
        "target_after": after,
        "externally_mutated": ctx.externally_mutated,
        "target_integrity_check": target_integrity_ok,
        "execution_flag_check": execution_flag_ok,
        "decision": result,
    }


def weak_common_authorized(mods: Modules, ctx: Context) -> bool:
    try:
        decision = mods.d_validate.require_canonical_bytes(ctx.contract_d_bytes)
        app = mods.d_consume.consume(decision, ctx.expectation)
        if app.get("outcome") != "candidate_for_authorization":
            return False
        return bool(mods.e_ref.evaluate(ctx.authority_state, ctx.request).get("authorized"))
    except Exception:
        return False


def weak_controls(mods: Modules, td: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    ctx = case_context(mods, td, "NEG-RECEIPT-ONLY-REVOKED-NOW")
    weak_allow = bool(
        isinstance(ctx.historical_receipt, dict) and ctx.historical_receipt.get("authorized")
    )
    results.append({
        "control": "W-RECEIPT-AS-PERMIT",
        "case": ctx.case_id,
        "weak_observed_allow": weak_allow,
        "caught": weak_allow,
    })

    ctx = case_context(mods, td, "NEG-CONCURRENT-CHANGE-DURING-WINDOW")
    weak_allow = weak_common_authorized(mods, ctx)
    results.append({
        "control": "W-AUTH-BEFORE-TARGET-CHECK",
        "case": ctx.case_id,
        "weak_observed_allow": weak_allow,
        "caught": weak_allow,
    })

    ctx = case_context(mods, td, "NEG-STALE-PRESTATE")
    weak_allow = weak_common_authorized(mods, ctx)
    results.append({
        "control": "W-NO-PRESTATE-BINDING",
        "case": ctx.case_id,
        "weak_observed_allow": weak_allow,
        "caught": weak_allow,
    })

    ctx = case_context(mods, td, "NEG-REPLAY-IDEMPOTENCY-KEY")
    weak_allow = weak_common_authorized(mods, ctx)
    results.append({
        "control": "W-NO-REPLAY-STATE",
        "case": ctx.case_id,
        "weak_observed_allow": weak_allow,
        "caught": weak_allow,
    })

    ctx = case_context(mods, td, "NEG-SYMLINK-ESCAPE")
    text_path_ok = ".." not in ctx.intent["target_relative_path"].split("/")
    weak_allow = text_path_ok and weak_common_authorized(mods, ctx)
    results.append({
        "control": "W-PATH-TEXT-ONLY",
        "case": ctx.case_id,
        "weak_observed_allow": weak_allow,
        "caught": weak_allow,
    })

    ctx = case_context(mods, td, "NEG-CONTRACT-E-ENGINE-EXCEPTION")
    try:
        assert ctx.ref_eval is not None
        ctx.ref_eval(ctx.authority_state, ctx.request)
        weak_allow = False
    except Exception:
        weak_allow = True
    results.append({
        "control": "W-FAIL-OPEN-ENGINE-ERROR",
        "case": ctx.case_id,
        "weak_observed_allow": weak_allow,
        "caught": weak_allow,
    })

    return results


def identity_report(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "candidate": Path(args.candidate),
        "contract_d_core": Path(args.apparatus_d) / "validators/contract_d_core.py",
        "contract_d_validate": Path(args.apparatus_d) / "validators/contract_d_validate.py",
        "contract_d_consume": Path(args.apparatus_d) / "validators/contract_d_consume.py",
        "contract_d_registry": Path(args.apparatus_d) / "schema/contract-d/1.0.0/effect-registry.json",
        "contract_e_reference": Path(args.apparatus_e) / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate/reference.py",
        "contract_e_independent": Path(args.independent_e),
    }
    return {
        key: {"path": str(path), "sha256": sha256_bytes(path.read_bytes())}
        for key, path in paths.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--apparatus-d", required=True)
    parser.add_argument("--apparatus-e", required=True)
    parser.add_argument("--independent-e", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mods = load_modules(args)
    identities = identity_report(args)
    (out_dir / "IDENTITIES.json").write_text(
        json.dumps(identities, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with tempfile.TemporaryDirectory(prefix="contract-e-shadow-rc0-") as tmp:
        base = Path(tmp)
        candidate_root = base / "candidate"
        candidate_root.mkdir()
        case_results = [run_candidate_case(mods, candidate_root, cid) for cid in CASE_IDS]

        weak_root = base / "weak"
        weak_root.mkdir()
        weak = weak_controls(mods, weak_root)

    all_cases_pass = all(row.get("pass") for row in case_results)
    weak_controls_pass = all(row.get("caught") for row in weak)
    false_allows = [
        row["case_id"] for row in case_results if not row["expected"] and row["observed"]
    ]
    positive_failures = [
        row["case_id"] for row in case_results if row["expected"] and not row["observed"]
    ]
    target_integrity_failures = [
        row["case_id"] for row in case_results if not row.get("target_integrity_check", False)
    ]
    execution_flag_failures = [
        row["case_id"] for row in case_results if not row.get("execution_flag_check", False)
    ]
    missed_weak_controls = [row["control"] for row in weak if not row.get("caught")]

    if all_cases_pass and weak_controls_pass:
        scientific_state = "SUPPORTED_FOR_BOUNDED_SHADOW_CLAIM"
    else:
        scientific_state = "FALSIFIED"

    summary = {
        "schema": "contract-e-production-envelope-shadow-rc0-results-v1",
        "scientific_state": scientific_state,
        "production_authorization": False,
        "case_count": len(case_results),
        "case_pass_count": sum(1 for row in case_results if row.get("pass")),
        "false_allow_ids": false_allows,
        "positive_failure_ids": positive_failures,
        "target_integrity_failure_ids": target_integrity_failures,
        "execution_flag_failure_ids": execution_flag_failures,
        "weak_control_count": len(weak),
        "weak_controls_caught": sum(1 for row in weak if row.get("caught")),
        "missed_weak_controls": missed_weak_controls,
        "explicit_nonclaims": [
            "no live MainFrame knowledge mutation",
            "no production consumer established",
            "no trusted AuthorityState origin established",
            "no authenticated workload/principal established",
            "no concrete verified-tag serialization established",
            "no exactly-once execution established",
            "no execution proof established",
            "no verification proof established",
            "no merge/tag/release/promotion authorization",
        ],
    }

    (out_dir / "CASES.json").write_text(
        json.dumps(case_results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "WEAK_CONTROLS.json").write_text(
        json.dumps(weak, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "RESULTS.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if scientific_state == "SUPPORTED_FOR_BOUNDED_SHADOW_CLAIM" else 1


if __name__ == "__main__":
    raise SystemExit(main())
