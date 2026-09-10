"""Sealed qualification-only known-good adapter.

This module is never part of the public aperture. It reuses the separately
qualified Apparatus shadow/released validator only to qualify the sealed
clean-room evaluator before reveal.
"""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import sys
from typing import Any

ORACLE_ROOT = Path(os.environ["ORACLE_ROOT"]).resolve()
sys.path.insert(0, str(ORACLE_ROOT))

from validators import contract_c as released  # type: ignore  # noqa: E402
from research.contract_c_non_deciding_shadow_rc0 import shadow  # type: ignore  # noqa: E402

VERSION = "research-contract-c-successor-rc1"


def canonical_bytes(value: dict) -> bytes:
    return released.canonical_bytes(value)


def result_set_identity(value: dict) -> str:
    return released.result_set_identity(value)


def _has_neutral(value: dict[str, Any]) -> bool:
    return any(
        c.get("channel") == "non_deciding"
        for p in value.get("propositions", [])
        for c in p.get("contributions", [])
        if isinstance(c, dict)
    )


def validate_contract_c_bytes(
    raw: bytes,
    *,
    expected_sha256: str | None = None,
    contract_b_index: dict | None = None,
) -> list[str]:
    errors: list[str] = []
    if expected_sha256 is not None:
        errors.extend(released.validate_whole_object_hash(raw, expected_sha256))
    try:
        value = released.parse_json_bytes(raw)
    except ValueError as exc:
        return errors + [str(exc)]
    try:
        if raw != released.canonical_bytes(value):
            errors.append("non-canonical successor bytes")
    except (TypeError, ValueError) as exc:
        return errors + [f"canonicalization failed: {exc}"]
    if value.get("contract_c_version") != VERSION:
        errors.append("wrong successor version")
        return errors
    expected_result = released.result_set_identity(value)
    if value.get("result_set_id") != expected_result:
        errors.append("result_set_id mismatch")

    projected = deepcopy(value)
    if _has_neutral(value):
        projected["contract_c_version"] = shadow.SHADOW_VERSION
        projected["result_set_id"] = released.result_set_identity(projected)
        errors.extend(shadow.validate_shadow_object(projected, contract_b_index=contract_b_index))
    else:
        projected["contract_c_version"] = released.CONTRACT_C_VERSION
        projected["result_set_id"] = released.result_set_identity(projected)
        errors.extend(released.validate_internal_structure(projected, contract_b_index=contract_b_index))
    return errors
