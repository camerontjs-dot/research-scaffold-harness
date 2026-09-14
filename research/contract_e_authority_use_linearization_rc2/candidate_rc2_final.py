"""Final research-only authority/use linearization candidate for RC2.

One disposable SQLite database is the serialization domain for current authority,
target state, intent dedupe, mutation, and durable ExecutionRecord. Standing
Contract E authority targets the stable probe resource; exact intent binding is
performed by the PEP and preserved as non-conferring request evidence.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable

DB_SCHEMA = "cal-envelope-linearization-rc2"
AUTHORITY_EPOCH = "probe-authority-epoch-1"
DECISION_SCHEMA = "cal-envelope-probe-decision-rc2"
INTENT_SCHEMA = "cal-envelope-probe-intent-rc2"
DOMAIN = "cal.envelope-probe"
OPERATION = "envelope_probe.transition"
OPERATION_VERSION = "1"
SCOPE = "record"
TARGET_KIND = "cal.envelope-probe-record"
TARGET_ID = "fixture-1"
FROM_STATE = "ready"
TO_STATE = "marked"
INITIAL_VERSION = 17
FINAL_VERSION = 18


class InjectedResponseLoss(RuntimeError):
    pass


class InjectedRollback(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_identity(value: dict[str, Any], identity_field: str, canonical_bytes) -> str:
    body = {k: copy.deepcopy(v) for k, v in value.items() if k != identity_field}
    return sha256_bytes(canonical_bytes(body))


def exact_keys(value: Any, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def validate_decision(decision: Any, canonical_bytes) -> tuple[bool, str | None, str | None]:
    if not exact_keys(decision, {"schema", "decision_id", "target", "effect"}) or decision.get("schema") != DECISION_SCHEMA:
        return False, None, None
    target = decision.get("target")
    effect = decision.get("effect")
    if not exact_keys(target, {"kind", "id", "expected_version"}) or not exact_keys(effect, {"type", "version", "params"}):
        return False, None, None
    if (
        target.get("kind") != TARGET_KIND
        or target.get("id") != TARGET_ID
        or target.get("expected_version") != INITIAL_VERSION
        or effect.get("type") != OPERATION
        or effect.get("version") != OPERATION_VERSION
        or effect.get("params") != {"from_state": FROM_STATE, "to_state": TO_STATE}
    ):
        return False, None, None
    try:
        computed = canonical_identity(decision, "decision_id", canonical_bytes)
        digest = sha256_bytes(canonical_bytes(decision))
    except Exception:
        return False, None, None
    return computed == decision.get("decision_id"), computed, digest


def validate_intent(intent: Any, decision: dict[str, Any], decision_digest: str, canonical_bytes) -> tuple[bool, str | None, str | None]:
    keys = {
        "schema", "intent_id", "decision_id", "decision_sha256", "request_nonce",
        "actor", "operation", "operation_version", "target_kind", "target_id",
        "expected_target_version", "params",
    }
    if not exact_keys(intent, keys) or intent.get("schema") != INTENT_SCHEMA:
        return False, None, None
    if not isinstance(intent.get("request_nonce"), str) or not intent["request_nonce"]:
        return False, None, None
    if (
        intent.get("decision_id") != decision.get("decision_id")
        or intent.get("decision_sha256") != decision_digest
        or intent.get("actor") != "agent:probe-executor"
        or intent.get("operation") != OPERATION
        or intent.get("operation_version") != OPERATION_VERSION
        or intent.get("target_kind") != TARGET_KIND
        or intent.get("target_id") != TARGET_ID
        or intent.get("expected_target_version") != INITIAL_VERSION
        or intent.get("params") != {"from_state": FROM_STATE, "to_state": TO_STATE}
    ):
        return False, None, None
    try:
        computed = canonical_identity(intent, "intent_id", canonical_bytes)
        digest = sha256_bytes(canonical_bytes(intent))
    except Exception:
        return False, None, None
    return computed == intent.get("intent_id"), computed, digest


def state_digest(state: dict[str, Any], canonical_bytes) -> tuple[str, str]:
    digest = sha256_bytes(canonical_bytes(state))
    body = {k: copy.deepcopy(v) for k, v in state.items() if k != "authority_state_id"}
    expected_id = sha256_bytes(canonical_bytes(body))
    return digest, expected_id


def connect(db_path: str | Path, *, timeout: float = 30.0) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=timeout, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    return conn


def initialize_store(db_path: str | Path, *, authority_state: dict[str, Any], canonical_bytes) -> None:
    db = Path(db_path)
    if db.exists():
        db.unlink()
    conn = connect(db)
    try:
        conn.executescript(
            """
            CREATE TABLE meta(schema TEXT NOT NULL);
            CREATE TABLE authority_history(
                epoch TEXT NOT NULL,
                generation INTEGER NOT NULL,
                authority_state_id TEXT NOT NULL,
                authority_state_sha256 TEXT NOT NULL,
                parent_authority_state_sha256 TEXT,
                authority_state_json BLOB NOT NULL,
                PRIMARY KEY(epoch, generation),
                UNIQUE(authority_state_sha256)
            );
            CREATE TABLE authority_current(
                singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                epoch TEXT NOT NULL,
                generation INTEGER NOT NULL,
                authority_state_sha256 TEXT NOT NULL,
                FOREIGN KEY(epoch, generation) REFERENCES authority_history(epoch, generation)
            );
            CREATE TABLE target(id TEXT PRIMARY KEY, version INTEGER NOT NULL, state TEXT NOT NULL, marker TEXT);
            CREATE TABLE intent_ledger(
                intent_id TEXT PRIMARY KEY,
                intent_sha256 TEXT NOT NULL,
                committed_outcome TEXT NOT NULL,
                execution_record_id TEXT NOT NULL UNIQUE
            );
            CREATE TABLE execution_record(
                execution_record_id TEXT PRIMARY KEY,
                intent_id TEXT NOT NULL UNIQUE,
                intent_sha256 TEXT NOT NULL,
                decision_id TEXT NOT NULL,
                decision_sha256 TEXT NOT NULL,
                authority_epoch TEXT NOT NULL,
                authority_generation INTEGER NOT NULL,
                authority_state_id TEXT NOT NULL,
                authority_state_sha256 TEXT NOT NULL,
                target_id TEXT NOT NULL,
                target_before_version INTEGER NOT NULL,
                target_before_state TEXT NOT NULL,
                target_after_version INTEGER NOT NULL,
                target_after_state TEXT NOT NULL,
                committed_outcome TEXT NOT NULL
            );
            """
        )
        digest, expected_id = state_digest(authority_state, canonical_bytes)
        if expected_id != authority_state.get("authority_state_id"):
            raise ValueError("initial authority_state_id mismatch")
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO meta(schema) VALUES (?)", (DB_SCHEMA,))
        conn.execute("INSERT INTO authority_history VALUES (?,?,?,?,?,?)", (
            AUTHORITY_EPOCH, 0, authority_state["authority_state_id"], digest, None, canonical_bytes(authority_state)
        ))
        conn.execute("INSERT INTO authority_current(singleton,epoch,generation,authority_state_sha256) VALUES (1,?,?,?)", (
            AUTHORITY_EPOCH, 0, digest
        ))
        conn.execute("INSERT INTO target(id,version,state,marker) VALUES (?,?,?,NULL)", (TARGET_ID, INITIAL_VERSION, FROM_STATE))
        conn.commit()
    finally:
        conn.close()


def install_authority(db_path: str | Path, *, new_generation: int, authority_state: dict[str, Any], parent_authority_state_sha256: str | None, canonical_bytes) -> dict[str, Any]:
    result = {"installed": False, "generation": None, "failure": None}
    conn = connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        current = conn.execute("SELECT epoch,generation,authority_state_sha256 FROM authority_current WHERE singleton=1").fetchone()
        if current is None or current["epoch"] != AUTHORITY_EPOCH:
            conn.rollback(); result["failure"] = "missing_or_wrong_current_authority"; return result
        if new_generation != current["generation"] + 1:
            conn.rollback(); result["failure"] = "generation_not_monotonic_successor"; return result
        if parent_authority_state_sha256 != current["authority_state_sha256"]:
            conn.rollback(); result["failure"] = "parent_digest_mismatch"; return result
        digest, expected_id = state_digest(authority_state, canonical_bytes)
        if expected_id != authority_state.get("authority_state_id"):
            conn.rollback(); result["failure"] = "authority_state_identity_mismatch"; return result
        conn.execute("INSERT INTO authority_history VALUES (?,?,?,?,?,?)", (
            AUTHORITY_EPOCH, new_generation, authority_state["authority_state_id"], digest,
            parent_authority_state_sha256, canonical_bytes(authority_state)
        ))
        changed = conn.execute(
            "UPDATE authority_current SET generation=?,authority_state_sha256=? WHERE singleton=1 AND generation=? AND authority_state_sha256=?",
            (new_generation, digest, current["generation"], current["authority_state_sha256"]),
        ).rowcount
        if changed != 1:
            conn.rollback(); result["failure"] = "current_authority_compare_and_swap_failed"; return result
        conn.commit(); result.update({"installed": True, "generation": new_generation}); return result
    except sqlite3.IntegrityError as exc:
        conn.rollback(); result["failure"] = f"integrity_error:{type(exc).__name__}"; return result
    finally:
        conn.close()


def load_current_authority(conn: sqlite3.Connection, canonical_bytes) -> tuple[sqlite3.Row, dict[str, Any]]:
    row = conn.execute(
        """
        SELECT c.epoch,c.generation,c.authority_state_sha256,
               h.authority_state_id,h.parent_authority_state_sha256,h.authority_state_json
          FROM authority_current c
          JOIN authority_history h ON h.epoch=c.epoch AND h.generation=c.generation
         WHERE c.singleton=1 AND h.authority_state_sha256=c.authority_state_sha256
        """
    ).fetchone()
    if row is None:
        raise ValueError("current authority pointer/history mismatch")
    state = json.loads(bytes(row["authority_state_json"]).decode("utf-8"))
    digest, expected_id = state_digest(state, canonical_bytes)
    if digest != row["authority_state_sha256"] or expected_id != row["authority_state_id"]:
        raise ValueError("current authority bytes/identity mismatch")
    if row["generation"] == 0:
        if row["parent_authority_state_sha256"] is not None:
            raise ValueError("generation zero parent must be null")
    else:
        prev = conn.execute("SELECT authority_state_sha256 FROM authority_history WHERE epoch=? AND generation=?", (row["epoch"], row["generation"] - 1)).fetchone()
        if prev is None or prev["authority_state_sha256"] != row["parent_authority_state_sha256"]:
            raise ValueError("authority lineage mismatch")
    return row, state


def reference_identity(kind: str, version: str | None, immutable_id: str, canonical_bytes) -> str:
    return sha256_bytes(canonical_bytes({"kind": kind, "version": version, "immutable_id": immutable_id}))


def authorization_request(intent: dict[str, Any], state: dict[str, Any], *, evaluation_time: str, canonical_bytes) -> dict[str, Any]:
    target_ref = reference_identity(TARGET_KIND, "rc2", TARGET_ID, canonical_bytes)
    intent_ref = reference_identity("cal.envelope-probe-intent", "rc2", intent["intent_id"], canonical_bytes)
    return {
        "schema": "contract-e-authorization-request-candidate-rc3",
        "request_id": "probe-execution-request",
        "authority_state_id": state["authority_state_id"],
        "evaluation_time": evaluation_time,
        "subject_id": intent["actor"],
        "jurisdiction": {
            "domain": DOMAIN,
            "operation": intent["operation"],
            "scope": SCOPE,
            "target_class": TARGET_KIND,
            "target_ref": target_ref,
        },
        "references": [
            {"ref_id": "target", "kind": TARGET_KIND, "version": "rc2", "immutable_id": TARGET_ID, "identity_sha256": target_ref},
            {"ref_id": "intent", "kind": "cal.envelope-probe-intent", "version": "rc2", "immutable_id": intent["intent_id"], "identity_sha256": intent_ref},
        ],
        "supporting_artifacts": [{"id": "exact-intent", "artifact_type": "execution-intent", "ref_id": "intent"}],
        "conflicts": [],
        "residues": [],
    }


def receipt_projection(receipt: Any) -> Any:
    if not isinstance(receipt, dict):
        return receipt
    return {k: copy.deepcopy(v) for k, v in receipt.items() if k != "diagnostics"}


def execute(
    db_path: str | Path,
    *, decision: dict[str, Any], intent: dict[str, Any], evaluation_time: str, canonical_bytes,
    contract_e_reference_evaluate, contract_e_independent_evaluate,
    after_authorize_hook: Callable[[dict[str, Any]], None] | None = None,
    failpoint: str | None = None, historical_receipt: Any = None,
) -> dict[str, Any]:
    del historical_receipt
    result = {
        "outcome": "refused", "performed_transition": False, "returned_prior_outcome": False,
        "intent_id": None, "intent_sha256": None, "authority_generation_used": None,
        "authority_state_id_used": None, "authority_state_sha256_used": None,
        "target_before": None, "target_after": None, "execution_record_id": None, "failures": [],
    }
    d_ok, d_id, d_digest = validate_decision(decision, canonical_bytes)
    if not d_ok or d_id is None or d_digest is None:
        result["failures"].append("invalid_or_forged_decision"); return result
    i_ok, i_id, i_digest = validate_intent(intent, decision, d_digest, canonical_bytes)
    if not i_ok or i_id is None or i_digest is None:
        result["failures"].append("invalid_or_forged_intent"); return result
    result["intent_id"] = i_id; result["intent_sha256"] = i_digest

    conn = connect(db_path)
    committed = False
    try:
        conn.execute("BEGIN IMMEDIATE")
        prior = conn.execute("SELECT intent_sha256,committed_outcome,execution_record_id FROM intent_ledger WHERE intent_id=?", (intent["intent_id"],)).fetchone()
        if prior is not None:
            if prior["intent_sha256"] != i_digest:
                conn.rollback(); result["failures"].append("intent_id_digest_conflict"); return result
            record = conn.execute("SELECT * FROM execution_record WHERE execution_record_id=?", (prior["execution_record_id"],)).fetchone()
            target = conn.execute("SELECT id,version,state,marker FROM target WHERE id=?", (TARGET_ID,)).fetchone()
            if record is None or target is None:
                conn.rollback(); result["failures"].append("prior_commit_evidence_incomplete"); return result
            if target["version"] != record["target_after_version"] or target["state"] != record["target_after_state"] or target["marker"] != intent["intent_id"]:
                conn.rollback(); result["failures"].append("prior_commit_target_disagrees"); return result
            conn.rollback(); result.update({
                "outcome": prior["committed_outcome"], "returned_prior_outcome": True,
                "execution_record_id": prior["execution_record_id"],
                "target_after": {"version": target["version"], "state": target["state"], "marker": target["marker"]},
            }); return result

        try:
            auth_row, auth_state = load_current_authority(conn, canonical_bytes)
        except Exception as exc:
            conn.rollback(); result["failures"].append(f"authority_store_invalid:{type(exc).__name__}"); return result
        result["authority_generation_used"] = auth_row["generation"]
        result["authority_state_id_used"] = auth_row["authority_state_id"]
        result["authority_state_sha256_used"] = auth_row["authority_state_sha256"]

        target = conn.execute("SELECT id,version,state,marker FROM target WHERE id=?", (TARGET_ID,)).fetchone()
        if target is None:
            conn.rollback(); result["failures"].append("target_missing"); return result
        result["target_before"] = {"version": target["version"], "state": target["state"], "marker": target["marker"]}
        if target["version"] != intent["expected_target_version"] or target["state"] != intent["params"]["from_state"] or target["marker"] is not None:
            conn.rollback(); result["failures"].append("target_precondition_failed"); return result

        request = authorization_request(intent, auth_state, evaluation_time=evaluation_time, canonical_bytes=canonical_bytes)
        try:
            rr = contract_e_reference_evaluate(auth_state, request)
            ir = contract_e_independent_evaluate(auth_state, request)
        except Exception as exc:
            conn.rollback(); result["failures"].append(f"contract_e_engine_error:{type(exc).__name__}"); return result
        if receipt_projection(rr) != receipt_projection(ir):
            conn.rollback(); result["failures"].append("contract_e_normative_disagreement"); return result
        if not isinstance(rr, dict) or rr.get("authorized") is not True:
            conn.rollback(); result["failures"].append("contract_e_denied"); return result

        if after_authorize_hook:
            after_authorize_hook({
                "authority_generation": auth_row["generation"],
                "authority_state_sha256": auth_row["authority_state_sha256"],
                "target_version": target["version"],
            })

        changed = conn.execute(
            "UPDATE target SET version=?,state=?,marker=? WHERE id=? AND version=? AND state=? AND marker IS NULL",
            (FINAL_VERSION, TO_STATE, intent["intent_id"], TARGET_ID, INITIAL_VERSION, FROM_STATE),
        ).rowcount
        if changed != 1:
            conn.rollback(); result["failures"].append("target_compare_and_swap_failed"); return result
        if failpoint == "after_target_update_before_records":
            raise InjectedRollback("after_target_update_before_records")

        record_body = {
            "intent_id": intent["intent_id"], "intent_sha256": i_digest,
            "decision_id": decision["decision_id"], "decision_sha256": d_digest,
            "authority_epoch": auth_row["epoch"], "authority_generation": auth_row["generation"],
            "authority_state_id": auth_row["authority_state_id"], "authority_state_sha256": auth_row["authority_state_sha256"],
            "target_id": TARGET_ID, "target_before_version": INITIAL_VERSION, "target_before_state": FROM_STATE,
            "target_after_version": FINAL_VERSION, "target_after_state": TO_STATE, "committed_outcome": "committed",
        }
        record_id = sha256_bytes(canonical_bytes(record_body))
        conn.execute("INSERT INTO execution_record VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            record_id, intent["intent_id"], i_digest, decision["decision_id"], d_digest,
            auth_row["epoch"], auth_row["generation"], auth_row["authority_state_id"], auth_row["authority_state_sha256"],
            TARGET_ID, INITIAL_VERSION, FROM_STATE, FINAL_VERSION, TO_STATE, "committed"
        ))
        conn.execute("INSERT INTO intent_ledger(intent_id,intent_sha256,committed_outcome,execution_record_id) VALUES (?,?,?,?)", (
            intent["intent_id"], i_digest, "committed", record_id
        ))
        conn.commit(); committed = True
        result.update({
            "outcome": "committed", "performed_transition": True, "execution_record_id": record_id,
            "target_after": {"version": FINAL_VERSION, "state": TO_STATE, "marker": intent["intent_id"]},
        })
        if failpoint == "after_commit_before_response":
            raise InjectedResponseLoss("after_commit_before_response")
        return result
    except InjectedRollback:
        if not committed:
            conn.rollback()
        raise
    finally:
        conn.close()
