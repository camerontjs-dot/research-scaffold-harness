"""Qualification-only mutant wrapper for the sealed Contract C evaluator."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from typing import Any

import reference_adapter as ref

MODE = os.environ.get("MUTANT_MODE", "accept_all")


def canonical_bytes(value: dict) -> bytes:
    return ref.canonical_bytes(value)


def result_set_identity(value: dict) -> str:
    return ref.result_set_identity(value)


def _parse(raw: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def validate_contract_c_bytes(raw: bytes, *, expected_sha256: str | None = None, contract_b_index: dict | None = None) -> list[str]:
    if MODE == "accept_all":
        return []
    if MODE == "reject_all":
        return ["mutant rejects all"]
    if MODE == "reject_neutral":
        if b'"non_deciding"' in raw:
            return ["mutant rejects neutral channel"]
        return ref.validate_contract_c_bytes(raw, expected_sha256=expected_sha256, contract_b_index=contract_b_index)
    if MODE == "ignore_contract_b":
        return ref.validate_contract_c_bytes(raw, expected_sha256=expected_sha256, contract_b_index=None)
    if MODE == "ignore_whole_hash":
        return ref.validate_contract_c_bytes(raw, expected_sha256=None, contract_b_index=contract_b_index)
    if MODE == "canonicalize_before_validate":
        value = _parse(raw)
        if value is None:
            return ref.validate_contract_c_bytes(raw, expected_sha256=expected_sha256, contract_b_index=contract_b_index)
        normalized = ref.canonical_bytes(value)
        return ref.validate_contract_c_bytes(normalized, expected_sha256=None, contract_b_index=contract_b_index)
    if MODE == "repair_unclassified":
        value = _parse(raw)
        if value is None:
            return ref.validate_contract_c_bytes(raw, expected_sha256=expected_sha256, contract_b_index=contract_b_index)
        value = deepcopy(value)
        for proposition in value.get("propositions", []):
            conclusion = proposition.get("conclusion")
            if not isinstance(conclusion, dict):
                continue
            contributions = {c.get("contribution_id") for c in proposition.get("contributions", []) if isinstance(c, dict)}
            causal = {b.get("id") for b in conclusion.get("basis_members", []) if isinstance(b, dict) and b.get("namespace") == "contribution"}
            residual = set(conclusion.get("residual_contribution_ids", []))
            missing = sorted(x for x in contributions - causal - residual if isinstance(x, str))
            conclusion["residual_contribution_ids"] = sorted(residual | set(missing))
        value["result_set_id"] = ref.result_set_identity(value)
        normalized = ref.canonical_bytes(value)
        return ref.validate_contract_c_bytes(normalized, expected_sha256=None, contract_b_index=contract_b_index)
    raise RuntimeError(f"unknown MUTANT_MODE: {MODE}")
