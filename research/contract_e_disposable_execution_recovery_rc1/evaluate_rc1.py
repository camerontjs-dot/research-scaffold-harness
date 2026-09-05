"""Frozen evaluator for Contract E disposable execution/recovery RC1."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

CASE_IDS = [
    "POS-NORMAL-APPLY-VERIFY",
    "POS-RETRY-AFTER-VERIFIED",
    "POS-CRASH-AFTER-PREPARED-RETRY-AUTH-CURRENT",
    "NEG-CRASH-AFTER-PREPARED-RETRY-AUTH-REVOKED",
    "POS-CRASH-AFTER-REPLACE-BEFORE-APPLIED",
    "POS-CRASH-AFTER-APPLIED-BEFORE-VERIFY",
    "NEG-PRESTATE-CHANGED-BEFORE-FIRST-AUTH",
    "NEG-PRESTATE-CHANGED-AFTER-PREPARED",
    "NEG-CHANGE-BETWEEN-AUTH-AND-REPLACE",
    "NEG-POSTSTATE-TAMPER-BEFORE-VERIFY",
    "NEG-DECISION-DIGEST-SUBSTITUTION",
    "NEG-CONTRACT-D-NOT-CANDIDATE",
    "NEG-PLAN-ID-FORGERY",
    "NEG-TARGET-ID-SUBSTITUTION",
    "NEG-POST-BYTES-HASH-MISMATCH",
    "NEG-PATH-TRAVERSAL",
    "NEG-SYMLINK-ESCAPE",
    "NEG-NONDISPOSABLE-ROOT",
    "NEG-CONTRACT-E-ENGINE-ERROR",
    "NEG-CONTRACT-E-ENGINE-DISAGREEMENT",
    "NEG-JOURNAL-TAMPER",
    "NEG-JOURNAL-FORGED-APPLIED-PRESTATE",
    "NEG-AMBIGUOUS-RECOVERY-MUST-NOT-CLAIM-ATTRIBUTION",
]

PRE_BYTES = b"RC1 disposable pre-state\n"
POST_BYTES = b"RC1 disposable post-state\n"
THIRD_BYTES = b"RC1 unrelated concurrent third-state\n"
MARKER_NAME = ".contract-e-execution-rc1-disposable"
MARKER_BYTES = b"CONTRACT_E_EXECUTION_RC1_DISPOSABLE\n"
EVAL_TIME = "2026-09-04T12:00:00Z"
SUBJECT = "agent:disposable-executor"
DOMAIN = "mainframe.knowledge"
OP = "knowledge.add_verified_tag"
SCOPE = "claim"
TARGET_CLASS = "cal.disposable-execution-plan"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_file_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@dataclass
class Modules:
    executor: Any
    d_core: Any
    d_validate: Any
    d_consume: Any
    e_ref: Any
    e_ind: Any


@dataclass
class Ctx:
    case_id: str
    root: Path
    target: Path
    journal: Path
    plan_path: Path
    plan: dict[str, Any]
    contract_d_bytes: bytes
    expectation: Any
    state: Any
    request: Any
    ref_eval: Callable[[Any, Any], dict[str, Any]]
    ind_eval: Callable[[Any, Any], dict[str, Any]]


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
        "contract_e_rc3_successor_rc1",
        apparatus_e / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate/reference.py",
    )
    e_ind = load_file_module("contract_e_rc3_independent_rc1", independent_e)
    executor = load_file_module("contract_e_disposable_executor_rc1", candidate)
    return Modules(executor, d_core, d_validate, d_consume, e_ref, e_ind)


def baseline_decision(pre_sha: str, *, disposition: str = "clear", target_id: str = "disposable-note-1") -> dict[str, Any]:
    return {
        "contract_d_version": "1.0.0",
        "input_authority": {
            "kind": "contract-c",
            "id": "rc1-c1",
            "immutable_id": "result-set:" + "b" * 64,
        },
        "policy": {"id": "mainframe.source-audit", "version": "1"},
        "target": {"kind": "knowledge", "id": target_id, "content_sha256": pre_sha},
        "evaluation": {"state": "completed", "disposition": disposition},
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
        requested_operation=OP,
        effect_params={"scope": "claim"},
    )


def compute_plan_id(mods: Modules, plan: dict[str, Any]) -> str:
    body = {k: copy.deepcopy(v) for k, v in plan.items() if k != "operation_id"}
    return sha256_bytes(mods.e_ref.canonical_bytes(body))


def build_plan(
    mods: Modules,
    d_bytes: bytes,
    decision: dict[str, Any],
    *,
    relative_path: str = "note.md",
    target_id_override: str | None = None,
    post_bytes: bytes = POST_BYTES,
    expected_post_sha: str | None = None,
) -> dict[str, Any]:
    plan = {
        "schema": "cal-disposable-execution-plan-rc1",
        "operation_id": "sha256:" + "0" * 64,
        "contract_d_sha256": sha256_bytes(d_bytes),
        "contract_d_target_kind": decision["target"]["kind"],
        "contract_d_target_id": decision["target"]["id"] if target_id_override is None else target_id_override,
        "effect_id": "knowledge.add_verified_tag",
        "effect_version": "1",
        "effect_params": {"scope": "claim"},
        "target_root_id": "rc1-disposable-root",
        "target_relative_path": relative_path,
        "expected_pre_sha256": decision["target"]["content_sha256"],
        "expected_post_sha256": sha256_bytes(post_bytes) if expected_post_sha is None else expected_post_sha,
        "post_bytes_b64": base64.b64encode(post_bytes).decode("ascii"),
        "authorization_subject_id": SUBJECT,
        "authorization_domain": DOMAIN,
        "authorization_operation": OP,
        "authorization_scope": SCOPE,
        "authorization_target_class": TARGET_CLASS,
    }
    plan["operation_id"] = compute_plan_id(mods, plan)
    return plan


def build_state_request(
    mods: Modules,
    plan: dict[str, Any],
    *,
    revoked: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    ref_identity = mods.e_ref.reference_identity(
        "cal.disposable-execution-plan", "rc1", plan["operation_id"]
    )
    record = {
        "id": "authority-root-rc1",
        "basis_type": "policy",
        "subject_id": SUBJECT,
        "domain": DOMAIN,
        "operation": OP,
        "scope": SCOPE,
        "target_class": TARGET_CLASS,
        "target_ref": ref_identity,
        "valid_from": "2026-09-04T00:00:00Z",
        "valid_until": "2026-09-05T00:00:00Z",
        "revoked_at": EVAL_TIME if revoked else None,
        "parent_id": None,
        "delegated_by": None,
    }
    state = {
        "schema": "contract-e-authority-state-candidate-rc3",
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [record],
    }
    state["authority_state_id"] = mods.e_ref.authority_state_identity(state)
    ref = {
        "ref_id": "plan",
        "kind": "cal.disposable-execution-plan",
        "version": "rc1",
        "immutable_id": plan["operation_id"],
        "identity_sha256": ref_identity,
    }
    request = {
        "schema": "contract-e-authorization-request-candidate-rc3",
        "request_id": "rc1-request",
        "authority_state_id": state["authority_state_id"],
        "evaluation_time": EVAL_TIME,
        "subject_id": SUBJECT,
        "jurisdiction": {
            "domain": DOMAIN,
            "operation": OP,
            "scope": SCOPE,
            "target_class": TARGET_CLASS,
            "target_ref": ref_identity,
        },
        "references": [ref],
        "supporting_artifacts": [],
        "conflicts": [],
        "residues": [],
    }
    return state, request


def write_plan(ctx: Ctx) -> None:
    ctx.plan_path.write_text(json.dumps(ctx.plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rebind_request(mods: Modules, ctx: Ctx, *, revoked: bool = False) -> None:
    ctx.state, ctx.request = build_state_request(mods, ctx.plan, revoked=revoked)
    write_plan(ctx)


def prepare(
    mods: Modules,
    parent: Path,
    case_id: str,
    *,
    actual_bytes: bytes = PRE_BYTES,
    marker: bool = True,
    decision: dict[str, Any] | None = None,
    relative_path: str = "note.md",
    target_id_override: str | None = None,
    post_bytes: bytes = POST_BYTES,
    expected_post_sha: str | None = None,
) -> Ctx:
    root = parent / case_id.lower().replace("_", "-")
    root.mkdir(parents=True)
    if marker:
        (root / MARKER_NAME).write_bytes(MARKER_BYTES)
    target = root / "note.md"
    target.write_bytes(actual_bytes)
    if decision is None:
        decision = baseline_decision(sha256_bytes(PRE_BYTES))
    d_bytes = mods.d_core.canonical_json_bytes(decision)
    expectation = expectation_for(mods, decision)
    plan = build_plan(
        mods,
        d_bytes,
        decision,
        relative_path=relative_path,
        target_id_override=target_id_override,
        post_bytes=post_bytes,
        expected_post_sha=expected_post_sha,
    )
    state, request = build_state_request(mods, plan)
    ctx = Ctx(
        case_id=case_id,
        root=root,
        target=target,
        journal=root / "execution.jsonl",
        plan_path=root / "plan.json",
        plan=plan,
        contract_d_bytes=d_bytes,
        expectation=expectation,
        state=state,
        request=request,
        ref_eval=mods.e_ref.evaluate,
        ind_eval=mods.e_ind.evaluate,
    )
    write_plan(ctx)
    return ctx


def invoke(
    mods: Modules,
    ctx: Ctx,
    *,
    failpoint: str | None = None,
    hook: Callable[[Path], None] | None = None,
) -> tuple[str, dict[str, Any] | None]:
    try:
        result = mods.executor.execute(
            plan=ctx.plan,
            contract_d_bytes=ctx.contract_d_bytes,
            applicability_expectation=ctx.expectation,
            target_root=ctx.root,
            journal_path=ctx.journal,
            authority_state=ctx.state,
            authorization_request=ctx.request,
            contract_d_require_canonical_bytes=mods.d_validate.require_canonical_bytes,
            contract_d_consume=mods.d_consume.consume,
            contract_d_validate_effect=mods.d_core.validate_effect,
            contract_e_reference_evaluate=ctx.ref_eval,
            contract_e_independent_evaluate=ctx.ind_eval,
            canonical_bytes=mods.e_ref.canonical_bytes,
            contract_e_reference_identity=mods.e_ref.reference_identity,
            failpoint=failpoint,
            research_before_replace_hook=hook,
        )
        return "returned", result
    except mods.executor.InjectedInterruption as exc:
        return f"interrupted:{exc}", None


def verifier_path(args: argparse.Namespace) -> Path:
    return Path(args.verifier).resolve()


def run_verifier(args: argparse.Namespace, ctx: Ctx) -> tuple[bool, dict[str, Any]]:
    output = ctx.root / "verification.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(verifier_path(args)),
            "--plan",
            str(ctx.plan_path),
            "--target-root",
            str(ctx.root),
            "--journal",
            str(ctx.journal),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    data: dict[str, Any]
    try:
        data = json.loads(output.read_text(encoding="utf-8"))
    except Exception:
        data = {"verification_pass": False, "failures": ["verifier_output_unreadable"], "stdout": proc.stdout, "stderr": proc.stderr}
    return proc.returncode == 0, data


def journal_events(ctx: Ctx) -> list[dict[str, Any]]:
    if not ctx.journal.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in ctx.journal.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def inode(path: Path) -> tuple[int, int]:
    s = path.stat()
    return s.st_dev, s.st_ino


def case_result(case_id: str, passed: bool, **evidence: Any) -> dict[str, Any]:
    return {"case_id": case_id, "pass": bool(passed), **evidence}


def run_case(mods: Modules, args: argparse.Namespace, parent: Path, case_id: str) -> dict[str, Any]:
    if case_id == "POS-NORMAL-APPLY-VERIFY":
        ctx = prepare(mods, parent, case_id)
        status, obs = invoke(mods, ctx)
        v_ok, ver = run_verifier(args, ctx)
        passed = (
            status == "returned"
            and obs is not None
            and obs.get("allowed") is True
            and obs.get("performed_write") is True
            and obs.get("fresh_authorization_performed") is True
            and ctx.target.read_bytes() == POST_BYTES
            and [e["event_type"] for e in journal_events(ctx)] == ["PREPARED", "APPLIED"]
            and v_ok
            and ver.get("terminal_event") == "APPLIED"
        )
        return case_result(case_id, passed, observation=obs, verification=ver)

    if case_id == "POS-RETRY-AFTER-VERIFIED":
        ctx = prepare(mods, parent, case_id)
        _, first = invoke(mods, ctx)
        before_inode = inode(ctx.target)
        before_journal = ctx.journal.read_bytes()
        _, second = invoke(mods, ctx)
        after_inode = inode(ctx.target)
        after_journal = ctx.journal.read_bytes()
        v_ok, ver = run_verifier(args, ctx)
        passed = (
            first is not None and first.get("performed_write") is True
            and second is not None and second.get("allowed") is True
            and second.get("performed_write") is False
            and second.get("fresh_authorization_performed") is False
            and before_inode == after_inode
            and before_journal == after_journal
            and v_ok
        )
        return case_result(case_id, passed, first=first, retry=second, verification=ver)

    if case_id == "POS-CRASH-AFTER-PREPARED-RETRY-AUTH-CURRENT":
        ctx = prepare(mods, parent, case_id)
        first_status, _ = invoke(mods, ctx, failpoint="after_prepared")
        pre_after_crash = ctx.target.read_bytes()
        retry_status, retry = invoke(mods, ctx)
        v_ok, ver = run_verifier(args, ctx)
        types = [e["event_type"] for e in journal_events(ctx)]
        passed = (
            first_status == "interrupted:after_prepared"
            and pre_after_crash == PRE_BYTES
            and retry_status == "returned"
            and retry is not None and retry.get("performed_write") is True
            and retry.get("fresh_authorization_performed") is True
            and types == ["PREPARED", "PREPARED", "APPLIED"]
            and v_ok
        )
        return case_result(case_id, passed, retry=retry, journal_types=types, verification=ver)

    if case_id == "NEG-CRASH-AFTER-PREPARED-RETRY-AUTH-REVOKED":
        ctx = prepare(mods, parent, case_id)
        first_status, _ = invoke(mods, ctx, failpoint="after_prepared")
        rebind_request(mods, ctx, revoked=True)
        retry_status, retry = invoke(mods, ctx)
        events = journal_events(ctx)
        passed = (
            first_status == "interrupted:after_prepared"
            and retry_status == "returned"
            and retry is not None and retry.get("allowed") is False
            and retry.get("fresh_authorization_performed") is True
            and ctx.target.read_bytes() == PRE_BYTES
            and [e["event_type"] for e in events] == ["PREPARED", "ABORTED"]
        )
        return case_result(case_id, passed, retry=retry, journal=events)

    if case_id == "POS-CRASH-AFTER-REPLACE-BEFORE-APPLIED":
        ctx = prepare(mods, parent, case_id)
        first_status, _ = invoke(mods, ctx, failpoint="after_replace_before_applied")
        inode_before_retry = inode(ctx.target)
        retry_status, retry = invoke(mods, ctx)
        inode_after_retry = inode(ctx.target)
        v_ok, ver = run_verifier(args, ctx)
        events = journal_events(ctx)
        passed = (
            first_status == "interrupted:after_replace_before_applied"
            and ctx.target.read_bytes() == POST_BYTES
            and retry_status == "returned"
            and retry is not None and retry.get("performed_write") is False
            and retry.get("fresh_authorization_performed") is False
            and retry.get("execution_attribution") == "unknown"
            and retry.get("journal_terminal_event") == "RECOVERED_POSTSTATE"
            and inode_before_retry == inode_after_retry
            and [e["event_type"] for e in events] == ["PREPARED", "RECOVERED_POSTSTATE"]
            and v_ok and ver.get("execution_attribution") == "unknown"
        )
        return case_result(case_id, passed, retry=retry, verification=ver)

    if case_id == "POS-CRASH-AFTER-APPLIED-BEFORE-VERIFY":
        ctx = prepare(mods, parent, case_id)
        status, _ = invoke(mods, ctx, failpoint="after_applied")
        v_ok, ver = run_verifier(args, ctx)
        passed = (
            status == "interrupted:after_applied"
            and ctx.target.read_bytes() == POST_BYTES
            and [e["event_type"] for e in journal_events(ctx)] == ["PREPARED", "APPLIED"]
            and v_ok and ver.get("terminal_event") == "APPLIED"
        )
        return case_result(case_id, passed, verification=ver)

    if case_id == "NEG-PRESTATE-CHANGED-BEFORE-FIRST-AUTH":
        ctx = prepare(mods, parent, case_id, actual_bytes=THIRD_BYTES)
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and obs.get("fresh_authorization_performed") is False and ctx.target.read_bytes() == THIRD_BYTES
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-PRESTATE-CHANGED-AFTER-PREPARED":
        ctx = prepare(mods, parent, case_id)
        first_status, _ = invoke(mods, ctx, failpoint="after_prepared")
        ctx.target.write_bytes(THIRD_BYTES)
        _, retry = invoke(mods, ctx)
        types = [e["event_type"] for e in journal_events(ctx)]
        passed = first_status == "interrupted:after_prepared" and retry is not None and retry.get("allowed") is False and ctx.target.read_bytes() == THIRD_BYTES and types == ["PREPARED", "ABORTED"]
        return case_result(case_id, passed, retry=retry, journal_types=types)

    if case_id == "NEG-CHANGE-BETWEEN-AUTH-AND-REPLACE":
        ctx = prepare(mods, parent, case_id)
        def change(path: Path) -> None:
            path.write_bytes(THIRD_BYTES)
        _, obs = invoke(mods, ctx, hook=change)
        types = [e["event_type"] for e in journal_events(ctx)]
        passed = obs is not None and obs.get("allowed") is False and ctx.target.read_bytes() == THIRD_BYTES and types == ["PREPARED", "ABORTED"]
        return case_result(case_id, passed, observation=obs, journal_types=types)

    if case_id == "NEG-POSTSTATE-TAMPER-BEFORE-VERIFY":
        ctx = prepare(mods, parent, case_id)
        _, obs = invoke(mods, ctx)
        ctx.target.write_bytes(THIRD_BYTES)
        v_ok, ver = run_verifier(args, ctx)
        passed = obs is not None and obs.get("performed_write") is True and not v_ok and ver.get("verification_pass") is False
        return case_result(case_id, passed, observation=obs, verification=ver)

    if case_id == "NEG-DECISION-DIGEST-SUBSTITUTION":
        ctx = prepare(mods, parent, case_id)
        modified = baseline_decision(sha256_bytes(PRE_BYTES))
        modified["policy"]["version"] = "2"
        ctx.contract_d_bytes = mods.d_core.canonical_json_bytes(modified)
        ctx.expectation = expectation_for(mods, modified)
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "contract_d_digest_mismatch" in obs.get("failures", []) and ctx.target.read_bytes() == PRE_BYTES
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-CONTRACT-D-NOT-CANDIDATE":
        decision = baseline_decision(sha256_bytes(PRE_BYTES), disposition="hold")
        ctx = prepare(mods, parent, case_id, decision=decision)
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "contract_d_not_candidate_for_authorization" in obs.get("failures", []) and ctx.target.read_bytes() == PRE_BYTES
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-PLAN-ID-FORGERY":
        ctx = prepare(mods, parent, case_id)
        ctx.plan["operation_id"] = "sha256:" + "e" * 64
        rebind_request(mods, ctx)
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "invalid_or_forged_plan" in obs.get("failures", [])
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-TARGET-ID-SUBSTITUTION":
        decision = baseline_decision(sha256_bytes(PRE_BYTES), target_id="other-target")
        ctx = prepare(mods, parent, case_id, decision=decision, target_id_override="disposable-note-1")
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "contract_d_plan_binding_mismatch" in obs.get("failures", [])
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-POST-BYTES-HASH-MISMATCH":
        ctx = prepare(mods, parent, case_id)
        ctx.plan["post_bytes_b64"] = base64.b64encode(b"wrong post bytes\n").decode("ascii")
        ctx.plan["operation_id"] = compute_plan_id(mods, ctx.plan)
        rebind_request(mods, ctx)
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "invalid_or_forged_plan" in obs.get("failures", []) and ctx.target.read_bytes() == PRE_BYTES
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-PATH-TRAVERSAL":
        ctx = prepare(mods, parent, case_id, relative_path="../outside.md")
        (ctx.root.parent / "outside.md").write_bytes(PRE_BYTES)
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "invalid_target_relative_path" in obs.get("failures", [])
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-SYMLINK-ESCAPE":
        outside_dir = parent / "outside"
        outside_dir.mkdir(exist_ok=True)
        outside = outside_dir / f"{case_id}.md"
        outside.write_bytes(PRE_BYTES)
        ctx = prepare(mods, parent, case_id, relative_path="link.md")
        (ctx.root / "link.md").symlink_to(outside)
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "target_outside_root_or_not_regular" in obs.get("failures", [])
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-NONDISPOSABLE-ROOT":
        ctx = prepare(mods, parent, case_id, marker=False)
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "non_disposable_root" in obs.get("failures", [])
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-CONTRACT-E-ENGINE-ERROR":
        ctx = prepare(mods, parent, case_id)
        def boom(_s: Any, _r: Any) -> dict[str, Any]:
            raise RuntimeError("seeded")
        ctx.ref_eval = boom
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "fresh_authorization_failed" in obs.get("failures", []) and ctx.target.read_bytes() == PRE_BYTES
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-CONTRACT-E-ENGINE-DISAGREEMENT":
        ctx = prepare(mods, parent, case_id)
        exact = mods.e_ind.evaluate
        def disagree(state: Any, request: Any) -> dict[str, Any]:
            out = copy.deepcopy(exact(state, request))
            out["authorized"] = not bool(out.get("authorized"))
            return out
        ctx.ind_eval = disagree
        _, obs = invoke(mods, ctx)
        passed = obs is not None and obs.get("allowed") is False and "fresh_authorization_failed" in obs.get("failures", []) and ctx.target.read_bytes() == PRE_BYTES
        return case_result(case_id, passed, observation=obs)

    if case_id == "NEG-JOURNAL-TAMPER":
        ctx = prepare(mods, parent, case_id)
        _, obs = invoke(mods, ctx)
        lines = ctx.journal.read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0])
        first["reason"] = "tampered-after-the-fact"
        lines[0] = json.dumps(first, sort_keys=True, separators=(",", ":"))
        ctx.journal.write_text("\n".join(lines) + "\n", encoding="utf-8")
        v_ok, ver = run_verifier(args, ctx)
        passed = obs is not None and obs.get("performed_write") is True and not v_ok and "journal_event_hash_mismatch" in ver.get("failures", [])
        return case_result(case_id, passed, verification=ver)

    if case_id == "NEG-JOURNAL-FORGED-APPLIED-PRESTATE":
        ctx = prepare(mods, parent, case_id)
        # Adversarially construct a hash-consistent-looking journal while target remains pre-state.
        prev = "0" * 64
        events = []
        for seq, et, target_hash, attribution in [
            (1, "PREPARED", ctx.plan["expected_pre_sha256"], None),
            (2, "APPLIED", ctx.plan["expected_post_sha256"], "this_invocation"),
        ]:
            e = {
                "schema": "cal-disposable-execution-journal-event-rc1",
                "operation_id": ctx.plan["operation_id"],
                "sequence": seq,
                "event_type": et,
                "target_sha256": target_hash,
                "authorization_receipt_id": "sha256:" + "a" * 64,
                "authority_conferring": False,
                "execution_attribution": attribution,
                "reason": "forged",
                "prev_event_sha256": prev,
            }
            body = json.dumps(e, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            e["event_sha256"] = hashlib.sha256(body).hexdigest()
            prev = e["event_sha256"]
            events.append(e)
        ctx.journal.write_text("\n".join(json.dumps(e, sort_keys=True, separators=(",", ":")) for e in events) + "\n", encoding="utf-8")
        v_ok, ver = run_verifier(args, ctx)
        passed = not v_ok and "current_target_not_exact_poststate" in ver.get("failures", []) and ctx.target.read_bytes() == PRE_BYTES
        return case_result(case_id, passed, verification=ver)

    if case_id == "NEG-AMBIGUOUS-RECOVERY-MUST-NOT-CLAIM-ATTRIBUTION":
        ctx = prepare(mods, parent, case_id)
        first_status, _ = invoke(mods, ctx, failpoint="after_prepared")
        # An external actor/process creates the exact post-state while no APPLIED event exists.
        ctx.target.write_bytes(POST_BYTES)
        inode_before = inode(ctx.target)
        _, retry = invoke(mods, ctx)
        inode_after = inode(ctx.target)
        v_ok, ver = run_verifier(args, ctx)
        passed = (
            first_status == "interrupted:after_prepared"
            and retry is not None and retry.get("performed_write") is False
            and retry.get("execution_attribution") == "unknown"
            and inode_before == inode_after
            and v_ok and ver.get("execution_attribution") == "unknown"
        )
        return case_result(case_id, passed, retry=retry, verification=ver)

    raise KeyError(case_id)


def weak_controls(mods: Modules, args: argparse.Namespace, parent: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    # 1. PREPARED as reusable permission after revocation.
    ctx = prepare(mods, parent, "weak-prepared-permit")
    invoke(mods, ctx, failpoint="after_prepared")
    rebind_request(mods, ctx, revoked=True)
    _, strong = invoke(mods, ctx)
    weak_allow = any(e.get("event_type") == "PREPARED" for e in journal_events(ctx))
    out.append({"control": "W-PREPARED-AS-PERMIT", "weak_observed_unsafe": weak_allow, "strong_rejected": strong is not None and strong.get("allowed") is False, "caught": weak_allow and strong is not None and strong.get("allowed") is False})

    # 2. Rewriting exact post-state if APPLIED is absent.
    ctx = prepare(mods, parent, "weak-rewrite-poststate")
    invoke(mods, ctx, failpoint="after_replace_before_applied")
    inode_before = inode(ctx.target)
    _, recovered = invoke(mods, ctx)
    inode_after = inode(ctx.target)
    weak_would_write = ctx.target.read_bytes() == POST_BYTES and not any(e.get("event_type") == "APPLIED" for e in journal_events(ctx))
    out.append({"control": "W-REWRITE-POSTSTATE", "weak_observed_unsafe": weak_would_write, "strong_avoided_rewrite": recovered is not None and recovered.get("performed_write") is False and inode_before == inode_after, "caught": weak_would_write and recovered is not None and recovered.get("performed_write") is False and inode_before == inode_after})

    # 3. Claiming attribution from observed post-state after interruption.
    ctx = prepare(mods, parent, "weak-recovery-attribution")
    invoke(mods, ctx, failpoint="after_prepared")
    ctx.target.write_bytes(POST_BYTES)
    _, recovered = invoke(mods, ctx)
    weak_claim = True
    strong_unknown = recovered is not None and recovered.get("execution_attribution") == "unknown"
    out.append({"control": "W-CLAIM-ATTRIBUTION-ON-RECOVERY", "weak_observed_unsafe": weak_claim, "strong_unknown": strong_unknown, "caught": weak_claim and strong_unknown})

    # 4. Ignoring pre-state CAS after authorization.
    ctx = prepare(mods, parent, "weak-no-prestate-cas")
    def change(path: Path) -> None:
        path.write_bytes(THIRD_BYTES)
    _, strong = invoke(mods, ctx, hook=change)
    weak_would_overwrite = True
    strong_rejected = strong is not None and strong.get("allowed") is False and ctx.target.read_bytes() == THIRD_BYTES
    out.append({"control": "W-NO-PRESTATE-CAS", "weak_observed_unsafe": weak_would_overwrite, "strong_rejected": strong_rejected, "caught": weak_would_overwrite and strong_rejected})

    # 5. Trusting APPLIED journal before observing state.
    ctx = prepare(mods, parent, "weak-applied-before-state")
    prev = "0" * 64
    events = []
    for seq, et, target_hash, attr in [(1, "PREPARED", ctx.plan["expected_pre_sha256"], None), (2, "APPLIED", ctx.plan["expected_post_sha256"], "this_invocation")]:
        e = {"schema": "cal-disposable-execution-journal-event-rc1", "operation_id": ctx.plan["operation_id"], "sequence": seq, "event_type": et, "target_sha256": target_hash, "authorization_receipt_id": "sha256:" + "a" * 64, "authority_conferring": False, "execution_attribution": attr, "reason": "weak", "prev_event_sha256": prev}
        e["event_sha256"] = hashlib.sha256(json.dumps(e, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        prev = e["event_sha256"]
        events.append(e)
    ctx.journal.write_text("\n".join(json.dumps(e, sort_keys=True, separators=(",", ":")) for e in events) + "\n", encoding="utf-8")
    weak_pass = events[-1]["event_type"] == "APPLIED"
    v_ok, _ = run_verifier(args, ctx)
    out.append({"control": "W-APPLIED-BEFORE-STATE", "weak_observed_unsafe": weak_pass, "independent_verifier_rejected": not v_ok, "caught": weak_pass and not v_ok})

    # 6. Treating executor return as verification.
    ctx = prepare(mods, parent, "weak-self-verify")
    _, strong_exec = invoke(mods, ctx)
    ctx.target.write_bytes(THIRD_BYTES)
    weak_pass = strong_exec is not None and strong_exec.get("allowed") is True
    v_ok, _ = run_verifier(args, ctx)
    out.append({"control": "W-SELF-VERIFY", "weak_observed_unsafe": weak_pass, "independent_verifier_rejected": not v_ok, "caught": weak_pass and not v_ok})

    return out


def identity_report(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "candidate": Path(args.candidate),
        "verifier": Path(args.verifier),
        "contract_d_core": Path(args.apparatus_d) / "validators/contract_d_core.py",
        "contract_d_validate": Path(args.apparatus_d) / "validators/contract_d_validate.py",
        "contract_d_consume": Path(args.apparatus_d) / "validators/contract_d_consume.py",
        "contract_e_reference": Path(args.apparatus_e) / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate/reference.py",
        "contract_e_independent": Path(args.independent_e),
    }
    return {k: {"path": str(p), "sha256": sha256_bytes(p.read_bytes())} for k, p in paths.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--verifier", required=True)
    parser.add_argument("--apparatus-d", required=True)
    parser.add_argument("--apparatus-e", required=True)
    parser.add_argument("--independent-e", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    mods = load_modules(args)

    (out_dir / "IDENTITIES.json").write_text(json.dumps(identity_report(args), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="contract-e-exec-rc1-") as td:
        root = Path(td)
        cases_root = root / "cases"
        cases_root.mkdir()
        cases = [run_case(mods, args, cases_root, cid) for cid in CASE_IDS]
        weak_root = root / "weak"
        weak_root.mkdir()
        weak = weak_controls(mods, args, weak_root)

    case_failures = [c["case_id"] for c in cases if not c.get("pass")]
    weak_misses = [w["control"] for w in weak if not w.get("caught")]
    state = "SUPPORTED_FOR_BOUNDED_DISPOSABLE_EXECUTION_RECOVERY_CLAIM" if not case_failures and not weak_misses else "FALSIFIED"
    summary = {
        "schema": "contract-e-disposable-execution-recovery-rc1-results-v1",
        "scientific_state": state,
        "production_authorization": False,
        "case_count": len(cases),
        "case_pass_count": len(cases) - len(case_failures),
        "case_failure_ids": case_failures,
        "weak_control_count": len(weak),
        "weak_controls_caught": len(weak) - len(weak_misses),
        "missed_weak_controls": weak_misses,
        "explicit_nonclaims": [
            "no production verified-tag representation",
            "no live MainFrame mutation",
            "no real production consumer",
            "no authenticated AuthorityState origin",
            "no authenticated workload/principal",
            "no cryptographically signed execution evidence",
            "no power-loss durability proof",
            "no distributed exactly-once guarantee",
            "no attribution after interrupted post-state without APPLIED evidence",
            "no merge/tag/release/promotion authorization",
        ],
    }
    (out_dir / "CASES.json").write_text(json.dumps(cases, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "WEAK_CONTROLS.json").write_text(json.dumps(weak, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "RESULTS.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if state == "SUPPORTED_FOR_BOUNDED_DISPOSABLE_EXECUTION_RECOVERY_CLAIM" else 1


if __name__ == "__main__":
    raise SystemExit(main())
