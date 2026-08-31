#!/usr/bin/env python3
"""Post-falsification causal diagnostic for RC3C comparison dialect mismatches.

This diagnostic DOES NOT repair or reinterpret the frozen Grok implementation.
It asks a narrower causal question: when the already-revealed fixture DSL is
translated into the canonical vocabulary stated by the normative pre-freeze
specification, do the residual comparison mismatches disappear?

Any canonicalized result is diagnostic-only and MUST NOT be counted as fresh
independent agreement. PR #3 remains FALSIFIED regardless of this output.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from research_scaffold_harness.contract_e_rc3c import evaluate

HERE = Path(__file__).resolve().parent
REVEALED = HERE / "revealed"
OUT = HERE / "EVALUATOR-DIALECT-DIAGNOSTIC.json"


def deep(value: Any) -> Any:
    return copy.deepcopy(value)


def load(name: str) -> Any:
    return json.loads((REVEALED / name).read_text())


def set_path(root: Any, dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur = root
    for part in parts[:-1]:
        key: Any = int(part) if part.isdigit() else part
        cur = cur[key]
    last: Any = int(parts[-1]) if parts[-1].isdigit() else parts[-1]
    cur[last] = deep(value)


def decision(request: dict[str, Any]) -> dict[str, Any]:
    return evaluate(request).to_dict()


def matches(expected: str, observed: dict[str, Any]) -> bool:
    return bool(observed["accepted"]) == (expected == "accept")


def propagation_request(case: dict[str, Any], canonical: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {"mode": case["mode"]}
    if canonical:
        # Normative SPEC-SHAPES propagation_shape.explicit requires `fields`.
        payload["fields"] = deep(case.get("requested_fields", []))
    else:
        # Frozen fixture DSL spelling used in the original native comparison.
        payload["requested_fields"] = deep(case.get("requested_fields", []))
    return {"kind": "propagation", "request": payload, "mode": "new_exercise"}


def complete_parent_as_delegation(parent: dict[str, Any], child: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Diagnostic H1 only: treat parent as the same canonical Delegation shape.

    RC3A frozen parent fixtures omit identity/linkage keys that the normative
    delegation_shape marks required. We add only missing required identity keys
    so the frozen evaluator can reach subset/amplification semantics.

    The values are deliberately non-semantic placeholders because the frozen
    evaluator checks presence but does not use these three values in subset,
    scope, currentness, or expiry decisions. This is NOT a proposed production
    representation and is not independent-conformance evidence.
    """
    out = deep(parent)
    added: list[str] = []
    defaults = {
        "delegator": "diagnostic-upstream-authority",
        "delegate": child.get("delegator", "diagnostic-parent-delegate"),
        "parent_authority_id": "diagnostic-upstream-parent-authority",
    }
    for key, value in defaults.items():
        if key not in out:
            out[key] = value
            added.append(key)
    return out, added


def delegation_request(case: dict[str, Any], canonical: bool) -> tuple[dict[str, Any], list[str]]:
    parent = deep(case["parent"])
    child = deep(case["child"])
    added: list[str] = []
    if canonical:
        parent, added = complete_parent_as_delegation(parent, child)
    return {
        "kind": "delegation",
        "parent": parent,
        "child": child,
        "mode": "new_exercise",
    }, added


def historical_request(case: dict[str, Any], canonical: bool) -> dict[str, Any]:
    mode = case["mode"]
    if canonical and mode == "historical_record":
        # Fresh Grok preregistered the semantic operation as historical_inspection;
        # inherited shapes define a historical record but no `historical_record`
        # consumer mode token.
        mode = "historical_inspection"
    return {
        "kind": "historical",
        "record": deep(case["historical_record"]),
        "registry": {},
        "mode": mode,
    }


def run_pair(family: str, case_id: str, expected: str, original_req: dict[str, Any], canonical_req: dict[str, Any], expected_reason: str | None = None, notes: list[str] | None = None) -> dict[str, Any]:
    original = decision(original_req)
    canonical = decision(canonical_req)
    return {
        "family": family,
        "id": case_id,
        "expected": expected,
        "expected_reason": expected_reason,
        "original": original,
        "canonicalized_diagnostic": canonical,
        "original_outcome_match": matches(expected, original),
        "canonical_outcome_match": matches(expected, canonical),
        "canonical_reason_match": expected_reason is None or canonical.get("primary_reason") == expected_reason,
        "outcome_changed_by_dialect_only": bool(original.get("accepted")) != bool(canonical.get("accepted")),
        "reason_changed_by_dialect_only": original.get("primary_reason") != canonical.get("primary_reason"),
        "diagnostic_notes": notes or [],
    }


def main() -> int:
    rc3a = load("RC3A-FROZEN-CASES.json")
    rc3c = load("RC3C-FROZEN-CASES.json")
    rows: list[dict[str, Any]] = []

    # A. Propagation: fixture DSL `requested_fields` vs normative `fields`.
    prop_by_id = {item["id"]: item for item in rc3a["propagation_cases"]}
    for case in rc3a["propagation_cases"]:
        rows.append(run_pair(
            "rc3a_propagation",
            case["id"],
            case["expected"],
            propagation_request(case, canonical=False),
            propagation_request(case, canonical=True),
            case.get("reason"),
            ["diagnostic_translation: requested_fields -> fields"],
        ))

    # RC3C relisted propagation reasons point back to inherited propagation cases.
    for case in rc3c.get("reason_cases", []):
        source = case.get("source_propagation_case")
        if not source:
            continue
        inherited = prop_by_id[source]
        rows.append(run_pair(
            "rc3c_relisted_propagation_reason",
            case["id"],
            case["expected"],
            propagation_request(inherited, canonical=False),
            propagation_request(inherited, canonical=True),
            case.get("reason"),
            ["diagnostic_translation: requested_fields -> fields"],
        ))

    # B. Delegation: test H1 that parent is intended to be a Delegation object
    # under the same normative required-field shape as child.
    delegation_by_id = {item["id"]: item for item in rc3a["delegation_cases"]}
    for case in rc3a["delegation_cases"]:
        original_req, _ = delegation_request(case, canonical=False)
        canonical_req, added = delegation_request(case, canonical=True)
        rows.append(run_pair(
            "rc3a_delegation_parent_shape_h1",
            case["id"],
            case["expected"],
            original_req,
            canonical_req,
            case.get("reason"),
            [f"diagnostic_only_parent_completion:{','.join(added) if added else 'none'}"],
        ))

    # RC3C delegation cases are overlays over inherited delegation cases.
    for case in rc3c.get("delegation_wire_cases", []):
        source = delegation_by_id[case["source_case"]]
        materialized = deep(source)
        for path, value in case.get("set_path", {}).items():
            set_path(materialized, path, value)
        original_req, _ = delegation_request(materialized, canonical=False)
        canonical_req, added = delegation_request(materialized, canonical=True)
        rows.append(run_pair(
            "rc3c_delegation_parent_shape_h1",
            case["id"],
            case["expected"],
            original_req,
            canonical_req,
            case.get("reason"),
            [f"diagnostic_only_parent_completion:{','.join(added) if added else 'none'}"],
        ))

    # C. Historical API token: fixture `historical_record` vs fresh consumer's
    # preregistered semantic operation `historical_inspection`.
    for case in rc3a["historical_cases"]:
        rows.append(run_pair(
            "rc3a_historical_mode",
            case["id"],
            case["expected"],
            historical_request(case, canonical=False),
            historical_request(case, canonical=True),
            case.get("reason"),
            ["diagnostic_translation: historical_record mode -> historical_inspection" if case["mode"] == "historical_record" else "no_mode_translation"],
        ))

    original_mismatches = [r for r in rows if not r["original_outcome_match"]]
    canonical_mismatches = [r for r in rows if not r["canonical_outcome_match"]]

    # Reasons are only causally assessed where RC3C explicitly relists them or
    # the diagnostic family is the RC3C delegation successor family.
    normative_reason_rows = [
        r for r in rows
        if r["family"] in {"rc3c_relisted_propagation_reason", "rc3c_delegation_parent_shape_h1"}
        and r["expected"] == "reject"
        and r["expected_reason"] is not None
    ]
    canonical_reason_mismatches = [r for r in normative_reason_rows if not r["canonical_reason_match"]]

    summary = {
        "rows": len(rows),
        "original_outcome_mismatches": len(original_mismatches),
        "canonicalized_outcome_mismatches": len(canonical_mismatches),
        "canonicalized_normative_reason_mismatches": len(canonical_reason_mismatches),
        "original_mismatch_ids": [r["id"] for r in original_mismatches],
        "canonicalized_mismatch_ids": [r["id"] for r in canonical_mismatches],
        "canonicalized_normative_reason_mismatch_ids": [r["id"] for r in canonical_reason_mismatches],
        "diagnostic_signal": (
            "RESIDUAL_FAILURES_EXPLAINED_BY_DIALECT_OR_UNFROZEN_INTERFACE_SHAPE"
            if not canonical_mismatches and not canonical_reason_mismatches
            else "RESIDUAL_SEMANTIC_OR_INTERFACE_DISAGREEMENT_REMAINS"
        ),
        "scientific_nonclaim": "Canonicalized diagnostic outcomes are post-reveal causal probes only and do not convert PR #3 into independent agreement.",
    }

    result = {
        "status": "POST_FALSIFICATION_DIAGNOSTIC_ONLY",
        "frozen_implementation_modified": False,
        "source_tests_modified": False,
        "hypotheses": {
            "propagation": "Frozen fixture uses requested_fields while normative propagation shape requires fields.",
            "delegation": "Frozen positive parent may be an underspecified parent-authority representation; H1 tests same Delegation required shape only to reach subset semantics.",
            "historical": "Frozen fixture mode historical_record is not a normative mode token; historical_inspection is the fresh preregistered operation name.",
        },
        "summary": summary,
        "rows": rows,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if summary["diagnostic_signal"] == "RESIDUAL_FAILURES_EXPLAINED_BY_DIALECT_OR_UNFROZEN_INTERFACE_SHAPE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
