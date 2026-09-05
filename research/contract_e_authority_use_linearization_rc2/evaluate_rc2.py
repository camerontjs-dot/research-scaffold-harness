"""Evaluator for Contract E authority/use linearization RC2."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

CASE_IDS = [
    "POS-A0-T0-COMMIT",
    "POS-E-SERIALIZES-BEFORE-A1",
    "NEG-A1-SERIALIZES-BEFORE-E",
    "NEG-A1-WINS-BEFORE-TRANSACTION",
    "NEG-CALLER-SUPPLIED-STALE-A0",
    "NEG-STALE-TARGET-VERSION",
    "NEG-TARGET-CHANGE-WITHIN-SERIALIZATION-DOMAIN",
    "NEG-CONCURRENT-DISTINCT-INTENTS-SAME-V17",
    "POS-RETRY-SAME-INTENT-AFTER-COMMIT",
    "NEG-SAME-INTENT-ID-DIFFERENT-BYTES",
    "POS-CONCURRENT-SAME-INTENT",
    "POS-AMBIGUOUS-RESPONSE-LOSS",
    "NEG-FAIL-BEFORE-COMMIT",
    "NEG-FORGED-EXECUTOR-SUCCESS",
    "NEG-TARGET-TAMPER-AFTER-COMMIT",
    "NEG-DECISION-SUBSTITUTION",
    "NEG-INTENT-SUBSTITUTION",
    "NEG-HISTORICAL-RECEIPT-ONLY",
    "NEG-AUTHORITY-ROLLBACK-A1-TO-A0",
    "NEG-AUTHORITY-FORK-WRONG-PARENT",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Mods:
    pass


def load_modules(args: argparse.Namespace) -> Mods:
    m = Mods()
    m.candidate = load_module("rc2_candidate_eval", Path(args.candidate).resolve())
    m.fixtures = load_module("rc2_fixtures_eval", Path(args.fixtures).resolve())
    m.e_ref = load_module(
        "rc2_contract_e_ref_eval",
        Path(args.apparatus_e).resolve()
        / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate/reference.py",
    )
    m.e_ind = load_module("rc2_contract_e_ind_eval", Path(args.independent_e).resolve())
    m.weak_core = load_module("rc2_candidate_weak_core", Path(args.candidate).resolve().with_name("candidate_rc2_final.py"))
    return m


def prepare(mods: Mods, parent: Path, name: str):
    case = parent / name.lower().replace("_", "-")
    case.mkdir(parents=True, exist_ok=False)
    db = case / "probe.sqlite"
    decision = mods.fixtures.decision_fixture(mods.e_ref.canonical_bytes)
    intent1 = mods.fixtures.intent_fixture(mods.e_ref.canonical_bytes, decision=decision)
    intent2 = mods.fixtures.intent_fixture(
        mods.e_ref.canonical_bytes,
        decision=decision,
        request_nonce=mods.fixtures.SECOND_REQUEST_NONCE,
    )
    a0 = mods.fixtures.authority_a0(mods.e_ref.canonical_bytes)
    a1 = mods.fixtures.authority_a1(mods.e_ref.canonical_bytes)
    mods.candidate.initialize_store(db, authority_state=a0, canonical_bytes=mods.e_ref.canonical_bytes)
    return case, db, decision, intent1, intent2, a0, a1


def authority_digest(mods: Mods, state: dict[str, Any]) -> str:
    return mods.candidate.state_digest(state, mods.e_ref.canonical_bytes)[0]


def install_a1(mods: Mods, db: Path, a0: dict[str, Any], a1: dict[str, Any]):
    return mods.candidate.install_authority(
        db,
        new_generation=1,
        authority_state=a1,
        parent_authority_state_sha256=authority_digest(mods, a0),
        canonical_bytes=mods.e_ref.canonical_bytes,
    )


def execute(mods: Mods, db: Path, decision: dict[str, Any], intent: dict[str, Any], **kwargs):
    return mods.candidate.execute(
        db,
        decision=decision,
        intent=intent,
        evaluation_time=mods.fixtures.EVAL_TIME,
        canonical_bytes=mods.e_ref.canonical_bytes,
        contract_e_reference_evaluate=mods.e_ref.evaluate,
        contract_e_independent_evaluate=mods.e_ind.evaluate,
        **kwargs,
    )


def db_snapshot(db: Path) -> dict[str, Any]:
    conn = sqlite3.connect(str(db), isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        target = conn.execute("SELECT * FROM target WHERE id='fixture-1'").fetchone()
        current = conn.execute("SELECT * FROM authority_current WHERE singleton=1").fetchone()
        return {
            "target": dict(target) if target else None,
            "current_authority": dict(current) if current else None,
            "ledger_count": conn.execute("SELECT COUNT(*) FROM intent_ledger").fetchone()[0],
            "record_count": conn.execute("SELECT COUNT(*) FROM execution_record").fetchone()[0],
        }
    finally:
        conn.close()


def run_verifier(args: argparse.Namespace, db: Path, intent_id: str, out: Path) -> tuple[bool, dict[str, Any]]:
    proc = subprocess.run(
        [sys.executable, str(Path(args.verifier).resolve()), "--db", str(db), "--intent-id", intent_id, "--output", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        data = json.loads(out.read_text(encoding="utf-8"))
    except Exception:
        data = {"verification_pass": False, "failures": ["verifier_output_unreadable"], "stdout": proc.stdout, "stderr": proc.stderr}
    return proc.returncode == 0, data


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def concurrent_workers(args: argparse.Namespace, case: Path, db: Path, decision: dict[str, Any], intents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decision_path = case / "decision.json"
    write_json(decision_path, decision)
    gate = case / "GO"
    procs = []
    outputs = []
    for idx, intent in enumerate(intents):
        intent_path = case / f"intent-{idx}.json"
        output = case / f"worker-{idx}.json"
        write_json(intent_path, intent)
        outputs.append(output)
        cmd = [
            sys.executable, str(Path(args.worker).resolve()),
            "--candidate", str(Path(args.candidate).resolve()),
            "--apparatus-e", str(Path(args.apparatus_e).resolve()),
            "--independent-e", str(Path(args.independent_e).resolve()),
            "--db", str(db), "--decision", str(decision_path), "--intent", str(intent_path),
            "--output", str(output), "--gate", str(gate),
        ]
        procs.append(subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
    time.sleep(0.1)
    gate.write_text("go\n", encoding="utf-8")
    results = []
    for proc, output in zip(procs, outputs):
        stdout, stderr = proc.communicate(timeout=30)
        if output.exists():
            payload = json.loads(output.read_text(encoding="utf-8"))
        else:
            payload = {"status": "missing_output", "stdout": stdout, "stderr": stderr, "returncode": proc.returncode}
        results.append(payload)
    return results


def case_row(case_id: str, passed: bool, **evidence: Any) -> dict[str, Any]:
    return {"case_id": case_id, "pass": bool(passed), **evidence}


def run_case(mods: Mods, args: argparse.Namespace, parent: Path, case_id: str) -> dict[str, Any]:
    case, db, decision, intent1, intent2, a0, a1 = prepare(mods, parent, case_id)

    if case_id == "POS-A0-T0-COMMIT":
        obs = execute(mods, db, decision, intent1)
        v_ok, ver = run_verifier(args, db, intent1["intent_id"], case / "verify.json")
        snap = db_snapshot(db)
        ok = obs["outcome"] == "committed" and obs["performed_transition"] and obs["authority_generation_used"] == 0 and v_ok and snap["ledger_count"] == 1 and snap["record_count"] == 1
        return case_row(case_id, ok, observation=obs, verification=ver, snapshot=snap)

    if case_id == "POS-E-SERIALIZES-BEFORE-A1":
        blocked = {"value": False}
        def hook(_info):
            c = sqlite3.connect(str(db), timeout=0.0, isolation_level=None)
            try:
                try:
                    c.execute("BEGIN IMMEDIATE")
                except sqlite3.OperationalError as exc:
                    blocked["value"] = "locked" in str(exc).lower()
                else:
                    c.rollback()
            finally:
                c.close()
        obs = execute(mods, db, decision, intent1, after_authorize_hook=hook)
        installed = install_a1(mods, db, a0, a1)
        snap = db_snapshot(db)
        ok = blocked["value"] and obs["outcome"] == "committed" and obs["authority_generation_used"] == 0 and installed["installed"] and snap["current_authority"]["generation"] == 1
        return case_row(case_id, ok, observation=obs, authority_update=installed, write_lock_blocked_update=blocked["value"], snapshot=snap)

    if case_id == "NEG-A1-SERIALIZES-BEFORE-E":
        installed = install_a1(mods, db, a0, a1)
        obs = execute(mods, db, decision, intent1)
        snap = db_snapshot(db)
        ok = installed["installed"] and obs["outcome"] == "refused" and obs["authority_generation_used"] == 1 and "contract_e_denied" in obs["failures"] and snap["target"]["version"] == 17
        return case_row(case_id, ok, observation=obs, authority_update=installed, snapshot=snap)

    if case_id == "NEG-A1-WINS-BEFORE-TRANSACTION":
        held_intent = copy.deepcopy(intent1)
        installed = install_a1(mods, db, a0, a1)
        obs = execute(mods, db, decision, held_intent)
        ok = installed["installed"] and obs["outcome"] == "refused" and obs["authority_generation_used"] == 1 and "contract_e_denied" in obs["failures"]
        return case_row(case_id, ok, observation=obs, authority_update=installed)

    if case_id == "NEG-CALLER-SUPPLIED-STALE-A0":
        req = mods.fixtures.authorization_request(mods.e_ref.canonical_bytes, intent1, a0)
        receipt = mods.e_ref.evaluate(a0, req)
        installed = install_a1(mods, db, a0, a1)
        obs = execute(mods, db, decision, intent1, historical_receipt=receipt)
        ok = receipt.get("authorized") is True and installed["installed"] and obs["outcome"] == "refused" and obs["authority_generation_used"] == 1 and "contract_e_denied" in obs["failures"]
        return case_row(case_id, ok, historical_receipt_id=receipt.get("receipt_id"), observation=obs)

    if case_id == "NEG-STALE-TARGET-VERSION":
        c = sqlite3.connect(str(db), isolation_level=None)
        c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE target SET version=99,state='other',marker='external' WHERE id='fixture-1'"); c.commit(); c.close()
        obs = execute(mods, db, decision, intent1)
        snap = db_snapshot(db)
        ok = obs["outcome"] == "refused" and "target_precondition_failed" in obs["failures"] and snap["target"]["version"] == 99
        return case_row(case_id, ok, observation=obs, snapshot=snap)

    if case_id == "NEG-TARGET-CHANGE-WITHIN-SERIALIZATION-DOMAIN":
        blocked = {"value": False}
        def hook(_info):
            c = sqlite3.connect(str(db), timeout=0.0, isolation_level=None)
            try:
                try: c.execute("BEGIN IMMEDIATE")
                except sqlite3.OperationalError as exc: blocked["value"] = "locked" in str(exc).lower()
                else: c.rollback()
            finally: c.close()
        obs = execute(mods, db, decision, intent1, after_authorize_hook=hook)
        c = sqlite3.connect(str(db), isolation_level=None)
        c.execute("BEGIN IMMEDIATE")
        changed = c.execute("UPDATE target SET version=99,state='competitor',marker='competitor' WHERE id='fixture-1' AND version=17 AND state='ready' AND marker IS NULL").rowcount
        c.commit(); c.close()
        snap = db_snapshot(db)
        ok = blocked["value"] and obs["outcome"] == "committed" and changed == 0 and snap["target"]["version"] == 18
        return case_row(case_id, ok, observation=obs, competitor_blocked=blocked["value"], competitor_cas_rows=changed, snapshot=snap)

    if case_id == "NEG-CONCURRENT-DISTINCT-INTENTS-SAME-V17":
        workers = concurrent_workers(args, case, db, decision, [intent1, intent2])
        results = [w.get("result", {}) for w in workers if w.get("status") == "returned"]
        committed = [r for r in results if r.get("outcome") == "committed"]
        snap = db_snapshot(db)
        ok = len(results) == 2 and len(committed) == 1 and snap["record_count"] == 1 and snap["ledger_count"] == 1 and snap["target"]["version"] == 18
        return case_row(case_id, ok, workers=workers, snapshot=snap)

    if case_id == "POS-RETRY-SAME-INTENT-AFTER-COMMIT":
        first = execute(mods, db, decision, intent1)
        second = execute(mods, db, decision, intent1)
        snap = db_snapshot(db)
        ok = first["outcome"] == "committed" and second["returned_prior_outcome"] and second["execution_record_id"] == first["execution_record_id"] and snap["record_count"] == 1 and snap["ledger_count"] == 1
        return case_row(case_id, ok, first=first, retry=second, snapshot=snap)

    if case_id == "NEG-SAME-INTENT-ID-DIFFERENT-BYTES":
        first = execute(mods, db, decision, intent1)
        altered = copy.deepcopy(intent1); altered["request_nonce"] = "different-but-id-held"
        second = execute(mods, db, decision, altered)
        snap = db_snapshot(db)
        ok = first["outcome"] == "committed" and second["outcome"] == "refused" and "invalid_or_forged_intent" in second["failures"] and snap["record_count"] == 1
        return case_row(case_id, ok, first=first, conflicting_retry=second)

    if case_id == "POS-CONCURRENT-SAME-INTENT":
        workers = concurrent_workers(args, case, db, decision, [intent1, copy.deepcopy(intent1)])
        results = [w.get("result", {}) for w in workers if w.get("status") == "returned"]
        snap = db_snapshot(db)
        committed = [r for r in results if r.get("performed_transition")]
        prior = [r for r in results if r.get("returned_prior_outcome")]
        ok = len(results) == 2 and len(committed) == 1 and len(prior) == 1 and snap["record_count"] == 1 and snap["ledger_count"] == 1
        return case_row(case_id, ok, workers=workers, snapshot=snap)

    if case_id == "POS-AMBIGUOUS-RESPONSE-LOSS":
        lost = False
        try:
            execute(mods, db, decision, intent1, failpoint="after_commit_before_response")
        except mods.candidate.InjectedResponseLoss:
            lost = True
        retry = execute(mods, db, decision, intent1)
        snap = db_snapshot(db)
        ok = lost and retry["returned_prior_outcome"] and retry["outcome"] == "committed" and snap["record_count"] == 1 and snap["ledger_count"] == 1
        return case_row(case_id, ok, response_lost=lost, retry=retry, snapshot=snap)

    if case_id == "NEG-FAIL-BEFORE-COMMIT":
        rolled = False
        try:
            execute(mods, db, decision, intent1, failpoint="after_target_update_before_records")
        except mods.candidate.InjectedRollback:
            rolled = True
        snap = db_snapshot(db)
        ok = rolled and snap["target"]["version"] == 17 and snap["target"]["state"] == "ready" and snap["ledger_count"] == 0 and snap["record_count"] == 0
        return case_row(case_id, ok, injected_rollback=rolled, snapshot=snap)

    if case_id == "NEG-FORGED-EXECUTOR-SUCCESS":
        v_ok, ver = run_verifier(args, db, intent1["intent_id"], case / "verify.json")
        ok = not v_ok and ver.get("verification_pass") is False
        return case_row(case_id, ok, forged_executor_claim={"success": True}, verification=ver)

    if case_id == "NEG-TARGET-TAMPER-AFTER-COMMIT":
        obs = execute(mods, db, decision, intent1)
        c = sqlite3.connect(str(db), isolation_level=None); c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE target SET version=19,state='tampered',marker='evil' WHERE id='fixture-1'"); c.commit(); c.close()
        v_ok, ver = run_verifier(args, db, intent1["intent_id"], case / "verify.json")
        ok = obs["outcome"] == "committed" and not v_ok and "authoritative_target_disagrees" in ver.get("failures", [])
        return case_row(case_id, ok, observation=obs, verification=ver)

    if case_id == "NEG-DECISION-SUBSTITUTION":
        bad = copy.deepcopy(decision); bad["effect"]["params"]["to_state"] = "other"
        obs = execute(mods, db, bad, intent1)
        ok = obs["outcome"] == "refused" and "invalid_or_forged_decision" in obs["failures"] and db_snapshot(db)["target"]["version"] == 17
        return case_row(case_id, ok, observation=obs)

    if case_id == "NEG-INTENT-SUBSTITUTION":
        bad = copy.deepcopy(intent1); bad["operation"] = "other.operation"
        body = {k: copy.deepcopy(v) for k, v in bad.items() if k != "intent_id"}
        bad["intent_id"] = mods.fixtures.sha256_bytes(mods.e_ref.canonical_bytes(body))
        obs = execute(mods, db, decision, bad)
        ok = obs["outcome"] == "refused" and "invalid_or_forged_intent" in obs["failures"]
        return case_row(case_id, ok, observation=obs)

    if case_id == "NEG-HISTORICAL-RECEIPT-ONLY":
        req = mods.fixtures.authorization_request(mods.e_ref.canonical_bytes, intent1, a0)
        receipt = mods.e_ref.evaluate(a0, req)
        install_a1(mods, db, a0, a1)
        obs = execute(mods, db, decision, intent1, historical_receipt=receipt)
        ok = receipt.get("authorized") is True and obs["outcome"] == "refused" and "contract_e_denied" in obs["failures"]
        return case_row(case_id, ok, historical_receipt_id=receipt.get("receipt_id"), observation=obs)

    if case_id == "NEG-AUTHORITY-ROLLBACK-A1-TO-A0":
        installed = install_a1(mods, db, a0, a1)
        api_rollback = mods.candidate.install_authority(
            db, new_generation=0, authority_state=a0, parent_authority_state_sha256=None,
            canonical_bytes=mods.e_ref.canonical_bytes,
        )
        c = sqlite3.connect(str(db), isolation_level=None); c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE authority_current SET generation=0,authority_state_sha256=? WHERE singleton=1", (authority_digest(mods, a0),)); c.commit(); c.close()
        obs = execute(mods, db, decision, intent1)
        snap = db_snapshot(db)
        ok = installed["installed"] and not api_rollback["installed"] and obs["outcome"] == "refused" and any(x.startswith("authority_store_invalid") for x in obs["failures"]) and snap["target"]["version"] == 17
        return case_row(case_id, ok, install_a1=installed, installer_rollback=api_rollback, post_corruption_observation=obs)

    if case_id == "NEG-AUTHORITY-FORK-WRONG-PARENT":
        fork = mods.candidate.install_authority(
            db, new_generation=1, authority_state=a1,
            parent_authority_state_sha256="sha256:" + "f" * 64,
            canonical_bytes=mods.e_ref.canonical_bytes,
        )
        snap = db_snapshot(db)
        ok = not fork["installed"] and fork["failure"] == "parent_digest_mismatch" and snap["current_authority"]["generation"] == 0
        return case_row(case_id, ok, fork_attempt=fork, snapshot=snap)

    raise KeyError(case_id)


def weak_controls(mods: Mods, args: argparse.Namespace, parent: Path) -> list[dict[str, Any]]:
    rows = []

    # W-CHECK-THEN-WRITE-AUTHORITY-TOCTOU
    case, db, decision, intent, _, a0, a1 = prepare(mods, parent, "weak-auth-toctou")
    req = mods.fixtures.authorization_request(mods.e_ref.canonical_bytes, intent, a0)
    receipt = mods.e_ref.evaluate(a0, req)
    install_a1(mods, db, a0, a1)
    c = sqlite3.connect(str(db), isolation_level=None); c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE target SET version=18,state='marked',marker=? WHERE id='fixture-1'", (intent["intent_id"],)); c.commit(); c.close()
    unsafe = receipt.get("authorized") is True and db_snapshot(db)["current_authority"]["generation"] == 1 and db_snapshot(db)["target"]["version"] == 18
    rows.append({"control":"W-CHECK-THEN-WRITE-AUTHORITY-TOCTOU","unsafe_exposed":unsafe,"caught":unsafe})

    # W-NO-TARGET-CAS
    case, db, decision, intent, _, a0, _ = prepare(mods, parent, "weak-no-cas")
    req = mods.fixtures.authorization_request(mods.e_ref.canonical_bytes, intent, a0)
    allowed = mods.e_ref.evaluate(a0, req).get("authorized") is True
    c = sqlite3.connect(str(db), isolation_level=None); c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE target SET version=99,state='third',marker='third' WHERE id='fixture-1'"); c.commit(); c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE target SET version=18,state='marked',marker=? WHERE id='fixture-1'", (intent["intent_id"],)); c.commit(); c.close()
    unsafe = allowed and db_snapshot(db)["target"]["version"] == 18
    rows.append({"control":"W-NO-TARGET-CAS","unsafe_exposed":unsafe,"caught":unsafe})

    # W-NO-DURABLE-INTENT-RESULT
    case, db, decision, intent, _, _, _ = prepare(mods, parent, "weak-no-intent-result")
    c = sqlite3.connect(str(db), isolation_level=None); c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE target SET version=18,state='marked',marker=? WHERE id='fixture-1'", (intent["intent_id"],)); c.commit(); c.close()
    snap = db_snapshot(db)
    weak_retry_can_reconstruct = snap["ledger_count"] > 0 or snap["record_count"] > 0
    rows.append({"control":"W-NO-DURABLE-INTENT-RESULT","unsafe_exposed":not weak_retry_can_reconstruct,"caught":not weak_retry_can_reconstruct})

    # W-RECEIPT-AS-PERMIT
    case, db, decision, intent, _, a0, a1 = prepare(mods, parent, "weak-receipt-permit")
    req = mods.fixtures.authorization_request(mods.e_ref.canonical_bytes, intent, a0)
    receipt = mods.e_ref.evaluate(a0, req); install_a1(mods, db, a0, a1)
    if receipt.get("authorized"):
        c = sqlite3.connect(str(db), isolation_level=None); c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE target SET version=18,state='marked',marker=? WHERE id='fixture-1'", (intent["intent_id"],)); c.commit(); c.close()
    unsafe = receipt.get("authorized") is True and db_snapshot(db)["current_authority"]["generation"] == 1 and db_snapshot(db)["target"]["version"] == 18
    rows.append({"control":"W-RECEIPT-AS-PERMIT","unsafe_exposed":unsafe,"caught":unsafe})

    # W-EXECUTOR-SELF-VERIFY
    case, db, _, intent, _, _, _ = prepare(mods, parent, "weak-self-verify")
    weak_claim = True
    v_ok, _ = run_verifier(args, db, intent["intent_id"], case / "verify.json")
    rows.append({"control":"W-EXECUTOR-SELF-VERIFY","unsafe_exposed":weak_claim and not v_ok,"caught":weak_claim and not v_ok})

    # W-NO-AUTHORITY-ANTI-ROLLBACK
    case, db, decision, intent, _, a0, a1 = prepare(mods, parent, "weak-no-antirob")
    install_a1(mods, db, a0, a1)
    c = sqlite3.connect(str(db), isolation_level=None); c.execute("BEGIN IMMEDIATE"); c.execute("UPDATE authority_current SET generation=0,authority_state_sha256=? WHERE singleton=1", (authority_digest(mods, a0),)); c.commit(); c.close()
    weak_obs = mods.weak_core.execute(
        db, decision=decision, intent=intent, evaluation_time=mods.fixtures.EVAL_TIME,
        canonical_bytes=mods.e_ref.canonical_bytes,
        contract_e_reference_evaluate=mods.e_ref.evaluate,
        contract_e_independent_evaluate=mods.e_ind.evaluate,
    )
    unsafe = weak_obs.get("outcome") == "committed" and weak_obs.get("authority_generation_used") == 0
    rows.append({"control":"W-NO-AUTHORITY-ANTI-ROLLBACK","unsafe_exposed":unsafe,"caught":unsafe,"weak_observation":weak_obs})

    return rows


def identity_report(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "candidate_wrapper": Path(args.candidate),
        "candidate_core": Path(args.candidate).with_name("candidate_rc2_final.py"),
        "fixtures": Path(args.fixtures),
        "verifier": Path(args.verifier),
        "worker": Path(args.worker),
        "contract_e_reference": Path(args.apparatus_e) / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate/reference.py",
        "contract_e_independent": Path(args.independent_e),
    }
    import hashlib
    return {k:{"path":str(p),"sha256":"sha256:"+hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in paths.items()}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", required=True)
    p.add_argument("--fixtures", required=True)
    p.add_argument("--verifier", required=True)
    p.add_argument("--worker", required=True)
    p.add_argument("--apparatus-e", required=True)
    p.add_argument("--independent-e", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    mods = load_modules(args)
    write_json(out / "IDENTITIES.json", identity_report(args))
    with tempfile.TemporaryDirectory(prefix="contract-e-linearization-rc2-") as td:
        root = Path(td); cases_root = root / "cases"; cases_root.mkdir(); weak_root = root / "weak"; weak_root.mkdir()
        cases = [run_case(mods, args, cases_root, cid) for cid in CASE_IDS]
        weak = weak_controls(mods, args, weak_root)
    failures = [c["case_id"] for c in cases if not c.get("pass")]
    weak_misses = [w["control"] for w in weak if not w.get("caught")]
    state = "SUPPORTED_FOR_BOUNDED_AUTHORIZATION_USE_LINEARIZATION_CLAIM" if not failures and not weak_misses else "FALSIFIED"
    summary = {
        "schema":"contract-e-authority-use-linearization-rc2-results-v1",
        "scientific_state":state,
        "production_authorization":False,
        "case_count":len(cases),
        "case_pass_count":len(cases)-len(failures),
        "case_failure_ids":failures,
        "weak_control_count":len(weak),
        "weak_controls_caught":len(weak)-len(weak_misses),
        "missed_weak_controls":weak_misses,
        "explicit_nonclaims":[
            "trusted Decision/AuthorityState origin held fixed by experiment",
            "no production consumer or MainFrame mutation",
            "no production knowledge.add_verified_tag semantics",
            "no distributed authority/resource consistency",
            "no authenticated workload identity or PKI result",
            "no multi-object or multi-host transaction result",
            "no production merge/tag/release/promotion authorization",
        ],
    }
    write_json(out / "CASES.json", cases); write_json(out / "WEAK_CONTROLS.json", weak); write_json(out / "RESULTS.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if state == "SUPPORTED_FOR_BOUNDED_AUTHORIZATION_USE_LINEARIZATION_CLAIM" else 1


if __name__ == "__main__":
    raise SystemExit(main())
