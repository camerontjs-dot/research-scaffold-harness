"""Final frozen semantic fixtures for Contract E authority/use linearization RC2."""

from __future__ import annotations

import copy
import hashlib
from typing import Any

EVAL_TIME = "2026-09-04T12:00:00Z"
AUTHORITY_EPOCH = "probe-authority-epoch-1"
ACTOR = "agent:probe-executor"
OPERATION = "envelope_probe.transition"
OPERATION_VERSION = "1"
SCOPE = "record"
TARGET_KIND = "cal.envelope-probe-record"
TARGET_ID = "fixture-1"
TARGET_CLASS = TARGET_KIND
INITIAL_VERSION = 17
INITIAL_STATE = "ready"
FINAL_VERSION = 18
FINAL_STATE = "marked"
DECISION_SCHEMA = "cal-envelope-probe-decision-rc2"
INTENT_SCHEMA = "cal-envelope-probe-intent-rc2"
BASE_REQUEST_NONCE = "probe-request-1"
SECOND_REQUEST_NONCE = "probe-request-2"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def decision_fixture(canonical_bytes) -> dict[str, Any]:
    decision = {
        "schema": DECISION_SCHEMA,
        "decision_id": "sha256:" + "0" * 64,
        "target": {"kind": TARGET_KIND, "id": TARGET_ID, "expected_version": INITIAL_VERSION},
        "effect": {
            "type": OPERATION,
            "version": OPERATION_VERSION,
            "params": {"from_state": INITIAL_STATE, "to_state": FINAL_STATE},
        },
    }
    body = {k: copy.deepcopy(v) for k, v in decision.items() if k != "decision_id"}
    decision["decision_id"] = sha256_bytes(canonical_bytes(body))
    return decision


def intent_fixture(canonical_bytes, decision: dict[str, Any] | None = None, *, request_nonce: str = BASE_REQUEST_NONCE) -> dict[str, Any]:
    decision = decision_fixture(canonical_bytes) if decision is None else copy.deepcopy(decision)
    decision_sha = sha256_bytes(canonical_bytes(decision))
    intent = {
        "schema": INTENT_SCHEMA,
        "intent_id": "sha256:" + "0" * 64,
        "decision_id": decision["decision_id"],
        "decision_sha256": decision_sha,
        "request_nonce": request_nonce,
        "actor": ACTOR,
        "operation": OPERATION,
        "operation_version": OPERATION_VERSION,
        "target_kind": TARGET_KIND,
        "target_id": TARGET_ID,
        "expected_target_version": INITIAL_VERSION,
        "params": {"from_state": INITIAL_STATE, "to_state": FINAL_STATE},
    }
    body = {k: copy.deepcopy(v) for k, v in intent.items() if k != "intent_id"}
    intent["intent_id"] = sha256_bytes(canonical_bytes(body))
    return intent


def _authority_state(canonical_bytes, intent: dict[str, Any], *, revoked_at: str | None) -> dict[str, Any]:
    target_ref = sha256_bytes(canonical_bytes({
        "kind": "cal.envelope-probe-intent",
        "version": "rc2",
        "immutable_id": intent["intent_id"],
    }))
    state = {
        "schema": "contract-e-authority-state-candidate-rc3",
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [{
            "id": "probe-root",
            "basis_type": "policy",
            "subject_id": ACTOR,
            "domain": "cal.envelope-probe",
            "operation": OPERATION,
            "scope": SCOPE,
            "target_class": TARGET_CLASS,
            "target_ref": target_ref,
            "valid_from": "2026-09-04T00:00:00Z",
            "valid_until": "2026-09-05T00:00:00Z",
            "revoked_at": revoked_at,
            "parent_id": None,
            "delegated_by": None,
        }],
    }
    body = {k: copy.deepcopy(v) for k, v in state.items() if k != "authority_state_id"}
    state["authority_state_id"] = sha256_bytes(canonical_bytes(body))
    return state


def authority_a0(canonical_bytes, intent: dict[str, Any] | None = None) -> dict[str, Any]:
    intent = intent_fixture(canonical_bytes) if intent is None else copy.deepcopy(intent)
    return _authority_state(canonical_bytes, intent, revoked_at=None)


def authority_a1(canonical_bytes, intent: dict[str, Any] | None = None) -> dict[str, Any]:
    intent = intent_fixture(canonical_bytes) if intent is None else copy.deepcopy(intent)
    return _authority_state(canonical_bytes, intent, revoked_at=EVAL_TIME)
