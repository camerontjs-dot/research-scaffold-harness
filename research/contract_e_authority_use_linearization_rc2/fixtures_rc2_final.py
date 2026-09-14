"""Final frozen fixture semantics for Contract E authority/use linearization RC2."""

from __future__ import annotations

import copy
import hashlib
from typing import Any

EVAL_TIME = "2026-09-04T12:00:00Z"
AUTHORITY_EPOCH = "probe-authority-epoch-1"
ACTOR = "agent:probe-executor"
DOMAIN = "cal.envelope-probe"
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
BASE_REQUEST_NONCE = "probe-request-1"
SECOND_REQUEST_NONCE = "probe-request-2"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def reference_identity(canonical_bytes, kind: str, version: str | None, immutable_id: str) -> str:
    return sha256_bytes(canonical_bytes({"kind": kind, "version": version, "immutable_id": immutable_id}))


def target_reference(canonical_bytes) -> dict[str, Any]:
    ident = reference_identity(canonical_bytes, TARGET_KIND, "rc2", TARGET_ID)
    return {
        "ref_id": "target",
        "kind": TARGET_KIND,
        "version": "rc2",
        "immutable_id": TARGET_ID,
        "identity_sha256": ident,
    }


def decision_fixture(canonical_bytes) -> dict[str, Any]:
    value = {
        "schema": "cal-envelope-probe-decision-rc2",
        "decision_id": "sha256:" + "0" * 64,
        "target": {"kind": TARGET_KIND, "id": TARGET_ID, "expected_version": INITIAL_VERSION},
        "effect": {
            "type": OPERATION,
            "version": OPERATION_VERSION,
            "params": {"from_state": INITIAL_STATE, "to_state": FINAL_STATE},
        },
    }
    body = {k: copy.deepcopy(v) for k, v in value.items() if k != "decision_id"}
    value["decision_id"] = sha256_bytes(canonical_bytes(body))
    return value


def intent_fixture(canonical_bytes, *, request_nonce: str = BASE_REQUEST_NONCE, decision: dict[str, Any] | None = None) -> dict[str, Any]:
    decision = decision_fixture(canonical_bytes) if decision is None else copy.deepcopy(decision)
    value = {
        "schema": "cal-envelope-probe-intent-rc2",
        "intent_id": "sha256:" + "0" * 64,
        "decision_id": decision["decision_id"],
        "decision_sha256": sha256_bytes(canonical_bytes(decision)),
        "request_nonce": request_nonce,
        "actor": ACTOR,
        "operation": OPERATION,
        "operation_version": OPERATION_VERSION,
        "target_kind": TARGET_KIND,
        "target_id": TARGET_ID,
        "expected_target_version": INITIAL_VERSION,
        "params": {"from_state": INITIAL_STATE, "to_state": FINAL_STATE},
    }
    body = {k: copy.deepcopy(v) for k, v in value.items() if k != "intent_id"}
    value["intent_id"] = sha256_bytes(canonical_bytes(body))
    return value


def _authority(canonical_bytes, *, revoked_at: str | None) -> dict[str, Any]:
    target_ref = target_reference(canonical_bytes)["identity_sha256"]
    value = {
        "schema": "contract-e-authority-state-candidate-rc3",
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [{
            "id": "probe-root",
            "basis_type": "policy",
            "subject_id": ACTOR,
            "domain": DOMAIN,
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
    body = {k: copy.deepcopy(v) for k, v in value.items() if k != "authority_state_id"}
    value["authority_state_id"] = sha256_bytes(canonical_bytes(body))
    return value


def authority_a0(canonical_bytes) -> dict[str, Any]:
    return _authority(canonical_bytes, revoked_at=None)


def authority_a1(canonical_bytes) -> dict[str, Any]:
    return _authority(canonical_bytes, revoked_at=EVAL_TIME)


def authorization_request(canonical_bytes, intent: dict[str, Any], authority_state: dict[str, Any]) -> dict[str, Any]:
    target = target_reference(canonical_bytes)
    intent_ident = reference_identity(canonical_bytes, "cal.envelope-probe-intent", "rc2", intent["intent_id"])
    intent_ref = {
        "ref_id": "intent",
        "kind": "cal.envelope-probe-intent",
        "version": "rc2",
        "immutable_id": intent["intent_id"],
        "identity_sha256": intent_ident,
    }
    return {
        "schema": "contract-e-authorization-request-candidate-rc3",
        "request_id": "probe-execution-request",
        "authority_state_id": authority_state["authority_state_id"],
        "evaluation_time": EVAL_TIME,
        "subject_id": intent["actor"],
        "jurisdiction": {
            "domain": DOMAIN,
            "operation": intent["operation"],
            "scope": SCOPE,
            "target_class": TARGET_CLASS,
            "target_ref": target["identity_sha256"],
        },
        "references": [target, intent_ref],
        "supporting_artifacts": [{"id": "exact-intent", "artifact_type": "execution-intent", "ref_id": "intent"}],
        "conflicts": [],
        "residues": [],
    }
