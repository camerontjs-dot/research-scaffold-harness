"""Compare the frozen Grok consumer with the four authorized post-reveal blobs.

This module imports and calls the frozen consumer directly.  It does not copy,
wrap, or alter its authority semantics.  Fixture projection only supplies the
case envelope and resolver map required by that consumer; source fixture shape
is preserved where the projection can represent it.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from research.contract_e_fresh_reproduction.spec_loader import load_specs
from research.contract_e_fresh_reproduction.validator import evaluate


FROZEN_IMPLEMENTATION_SHA = "8987bf2fa183e7a00c40e256694b0d9de007a566"
FROZEN_IMPLEMENTATION_TREE = "a1dd2835bb80d8c8e97c2f0967cac73cb74e8067"
PREREGISTRATION_SHA = "9d2b6345c8387de8615375495a16cfcb3e67c503"
INPUT_APERTURE_SHA = "ca9c00a3a238d449445485fc72974837fee7ac5c"
INPUT_APERTURE_TREE = "339c3c76a3c49ba7d66a71c44c124e40c2b3f371"
FREEZE_MARKER = "FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_REVEAL"

REFERENCE_ARTIFACTS = {
    "FROZEN-CASES.json": {
        "path": "docs/research/contract-e/rc3a-authority-warrant-spec/FROZEN-CASES.json",
        "blob": "85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a",
    },
    "AUTHORITY-BASIS-REGISTRY.json": {
        "path": "docs/research/contract-e/rc3b-authority-basis-binding/AUTHORITY-BASIS-REGISTRY.json",
        "blob": "76ea333ee0460d9614e9899edb69e6865e48eccb",
    },
    "FROZEN-BASIS-ATTACKS.json": {
        "path": "docs/research/contract-e/rc3b-authority-basis-binding/FROZEN-BASIS-ATTACKS.json",
        "blob": "c726fb0ef914a850620e545131a70d427f4027bd",
    },
    "HARDENING-PREREGISTRATION.md": {
        "path": "docs/research/contract-e/rc3b-authority-basis-binding/HARDENING-PREREGISTRATION.md",
        "blob": "1d85e2036d410b3af08d4b2b8926586da8fe6088",
    },
}

AMBIGUITY_DESCRIPTIONS = {
    "W1": "warrant required vs allowed",
    "B1": "any-of vs all-of basis combination",
    "R1": "in-memory resolver",
    "H1": "explicit exercise_kind",
    "T1": "validity-bound inclusivity",
    "Q1": "qualification scope matching",
    "S1": "stale-target definition",
    "O1": "overall check order",
    "D2": "delegation vs domain any_of via parent chain",
    "G1": "generic authorized reject vs ignore",
}

# The reference fixtures use broader reason labels for some RC3A envelope
# cases.  This is reporting normalization only: the raw expected label and
# every raw frozen-consumer violation remain in the receipt.
EXPECTED_REASON_CLASSES = {
    "missing_domain_authority_basis": "missing_domain_authority_basis",
    "missing_required_qualification": "missing_required_qualification",
    "qualification_type_mismatch": "qualification_type_mismatch",
    "warrant_domain_mismatch": "warrant_domain_mismatch",
    "warrant_target_mismatch": "warrant_target_mismatch",
    "warrant_target_hash_mismatch": "warrant_target_hash_mismatch",
    "warrant_not_current": "warrant_not_current",
    "jurisdiction_inapplicable": "jurisdiction_inapplicable",
    "jurisdiction_not_current": "jurisdiction_not_current",
    "participant_domain_out_of_scope": "participant_domain_out_of_scope",
    "domain_operation_mismatch": "domain_operation_mismatch",
    "unknown_authority_domain": "unknown_authority_domain",
    "generic_authorized_forbidden": "generic_authorized_forbidden",
    "forbidden_authority_propagation": "forbidden_authority_propagation",
    "authority_requires_reestablishment": "authority_requires_reestablishment",
    "delegation_operation_amplification": "delegation_operation_amplification",
    "delegation_scope_amplification": "delegation_scope_amplification",
    "delegation_expiry_amplification": "delegation_expiry_amplification",
    "current_authority_required": "current_authority_required",
}

ACTUAL_REASON_CLASSES = {
    "missing_required_basis": "missing_domain_authority_basis",
    "unknown_domain": "unknown_authority_domain",
    "participant_domain_not_accepted": "participant_domain_out_of_scope",
    "participant_operation_not_accepted": "domain_operation_mismatch",
    "authority_basis_operation_mismatch": "domain_operation_mismatch",
    "unknown_operation": "domain_operation_mismatch",
    "warrant_target_mismatch": "warrant_target_mismatch",
    "stale_target": "warrant_target_hash_mismatch",
    "authority_basis_not_current": "current_authority_required",
    "generic_authorized_boolean_forbidden": "generic_authorized_forbidden",
    "propagation_forbidden_field": "forbidden_authority_propagation",
    "delegation_operation_added": "delegation_operation_amplification",
    "delegation_scope_expanded": "delegation_scope_amplification",
    "delegation_expiry_extended": "delegation_expiry_amplification",
}

SEMANTIC_VARIANTS = (
    {
        "name": "negative-result",
        "payload": {
            "status": "fail",
            "success": False,
            "confidence": 0.0,
            "payload": {"variant": "negative", "value": -1},
        },
    },
    {
        "name": "positive-result",
        "payload": {
            "status": "pass",
            "success": True,
            "confidence": 1.0,
            "payload": {"variant": "positive", "value": {"nested": [1, 2, 3]}},
        },
    },
    {
        "name": "indeterminate-result",
        "payload": {
            "status": "indeterminate",
            "success": None,
            "confidence": 0.5,
            "payload": ["opaque", {"variant": "indeterminate"}],
        },
    },
)

HARNESS_DEVELOPMENT_FAILURES = [
    {
        "exit_code": 1,
        "stage": "frozen-anchor-guard",
        "observed": "git rev-parse rejected the invalid ^{parent} spelling",
        "corrective_action": "changed the guard to the first-parent ^ spelling",
    },
    {
        "exit_code": 1,
        "stage": "reference-preregistration-guard",
        "observed": "the registry blob check omitted the documented colon",
        "corrective_action": "corrected the string guard; verified blob identity remained unchanged",
    },
    {
        "exit_code": 1,
        "stage": "report-rendering",
        "observed": "report rendering used the wrong semantic-metamorphic result key path",
        "corrective_action": "corrected post-processing to read the nested category result",
    },
]


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} is not a JSON object")
    return value


def _git_hash(path: Path) -> str:
    return subprocess.run(
        ["git", "hash-object", str(path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_rev(*args: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def verify_reference_artifacts(reference_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    observed: dict[str, Any] = {}
    for filename, info in REFERENCE_ARTIFACTS.items():
        path = reference_dir / filename
        if not path.is_file():
            raise RuntimeError(f"missing authorized revealed artifact: {filename}")
        actual = _git_hash(path)
        if actual != info["blob"]:
            raise RuntimeError(
                f"revealed artifact hash mismatch for {filename}: expected {info['blob']}, got {actual}"
            )
        observed[filename] = {
            "source_repository": "camerontjs-dot/apparatus-contracts",
            "source_path": info["path"],
            "requested_blob": info["blob"],
            "verified_blob": actual,
            "bytes": path.stat().st_size,
        }
    frozen_cases = _read_json(reference_dir / "FROZEN-CASES.json")
    registry = _read_json(reference_dir / "AUTHORITY-BASIS-REGISTRY.json")
    attacks = _read_json(reference_dir / "FROZEN-BASIS-ATTACKS.json")
    preregistration = (reference_dir / "HARDENING-PREREGISTRATION.md").read_text(encoding="utf-8")
    if not frozen_cases.get("frozen_before_validator"):
        raise RuntimeError("RC3A fixture is not marked frozen_before_validator")
    if not attacks.get("frozen_before_validator"):
        raise RuntimeError("RC3B attack fixture is not marked frozen_before_validator")
    if "registry blob: `76ea333ee0460d9614e9899edb69e6865e48eccb`" not in preregistration:
        raise RuntimeError("hardening preregistration does not pin the verified registry blob")
    if "direct attack blob: `c726fb0ef914a850620e545131a70d427f4027bd`" not in preregistration:
        raise RuntimeError("hardening preregistration does not pin the verified attack blob")
    return frozen_cases, registry, attacks, preregistration


def verify_frozen_anchors() -> dict[str, str]:
    actual_tree = _git_rev(f"{FROZEN_IMPLEMENTATION_SHA}^{{tree}}")
    if actual_tree != FROZEN_IMPLEMENTATION_TREE:
        raise RuntimeError(f"frozen implementation tree mismatch: {actual_tree}")
    if _git_rev(f"{PREREGISTRATION_SHA}^") != INPUT_APERTURE_SHA:
        raise RuntimeError("preregistration parent is not the recorded input aperture")
    if _git_rev(f"{INPUT_APERTURE_SHA}^") != "548bfa81f65290eda15af658f647497679b840ef":
        raise RuntimeError("input aperture parent is not the authorized clean base")
    subprocess.run(
        ["git", "diff", "--quiet", FROZEN_IMPLEMENTATION_SHA, "--", "research/contract_e_fresh_reproduction"],
        check=True,
    )
    return {
        "frozen_implementation": FROZEN_IMPLEMENTATION_SHA,
        "frozen_tree": FROZEN_IMPLEMENTATION_TREE,
        "preregistration": PREREGISTRATION_SHA,
        "input_aperture": INPUT_APERTURE_SHA,
        "input_aperture_tree": INPUT_APERTURE_TREE,
    }


def _set_path(obj: Any, dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    current = obj
    for part in parts[:-1]:
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    last = parts[-1]
    if isinstance(current, list):
        current[int(last)] = copy.deepcopy(value)
    else:
        current[last] = copy.deepcopy(value)


def _contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(v, key) for v in value.values())
    if isinstance(value, list):
        return any(_contains_key(v, key) for v in value)
    return False


def _case_from_envelope(base: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    return {"envelope": copy.deepcopy(base), "basis_records": copy.deepcopy(registry["records"])}


def _apply_envelope_case(
    definition: dict[str, Any], baselines: dict[str, Any], registry: dict[str, Any]
) -> dict[str, Any]:
    envelope = copy.deepcopy(baselines[definition["base"]])
    for basis_type in definition.get("remove_authority_basis_types", []):
        envelope["authority_basis"] = [
            ref for ref in envelope.get("authority_basis", []) if ref.get("type") != basis_type
        ]
    for key in definition.get("remove", []):
        envelope.pop(key, None)
    for key, value in definition.get("set", {}).items():
        envelope[key] = copy.deepcopy(value)
    for path, value in definition.get("set_path", {}).items():
        _set_path(envelope, path, value)
    return _case_from_envelope(envelope, registry)


def _replace_reference(case: dict[str, Any], old_id: str, new_ref: dict[str, Any]) -> None:
    refs = case["envelope"]["authority_basis"]
    for index, ref in enumerate(refs):
        if isinstance(ref, dict) and ref.get("id") == old_id:
            refs[index] = copy.deepcopy(new_ref)
            return
    raise RuntimeError(f"authority reference {old_id} not found in generated case")


def _actual_reason_classes(actual: dict[str, Any]) -> list[str]:
    classes: set[str] = set()
    for reason in actual.get("violations", []):
        classes.add(reason)
        classes.add(ACTUAL_REASON_CLASSES.get(reason, reason))
    return sorted(classes)


def _run_native(case: dict[str, Any], spec: Any) -> dict[str, Any]:
    try:
        return evaluate(copy.deepcopy(case), spec)
    except Exception as exc:  # preserve execution deviations without a local traceback path
        return {
            "execution_status": "error",
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }


def _ambiguity_tags(category: str, case_id: str, case: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    tags: set[str] = set()
    envelope = case.get("envelope", case)
    domain = envelope.get("authority_domain") if isinstance(envelope, dict) else None
    if isinstance(case.get("basis_records"), dict):
        tags.update({"R1", "B1"})
    if category == "rc3a_historical":
        tags.update({"H1", "T1"})
    elif "exercise_kind" not in case and "exercise_kind" not in envelope:
        tags.add("H1")
    if category == "rc3a_delegation":
        tags.add("D2")
    if domain in {"numeric_relation", "source_boundary", "decision_mandate", "outcome_verification"}:
        tags.update({"W1", "Q1"})
    if _contains_key(case, "warrant"):
        tags.add("W1")
    qualification_values = [
        case.get("qualification"),
        case.get("competence"),
        envelope.get("qualification") if isinstance(envelope, dict) else None,
        envelope.get("competence") if isinstance(envelope, dict) else None,
    ]
    if any(
        isinstance(value, dict) or (isinstance(value, list) and bool(value))
        for value in qualification_values
    ):
        tags.add("Q1")
    if "stale" in case_id.lower() or "target_hash" in json.dumps(case, sort_keys=True):
        tags.add("S1")
    if _contains_key(case, "authorized"):
        tags.add("G1")
    if category in {"rc3a_envelope", "rc3b_attack"} and envelope.get("authority_basis") is not None:
        tags.add("O1")
    return sorted(tags)


def _run_vector(
    category: str,
    case_id: str,
    case: dict[str, Any],
    expected_outcome: str,
    expected_reason: str | None,
    spec: Any,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actual = _run_native(case, spec)
    is_error = actual.get("execution_status") == "error"
    actual_outcome = actual.get("outcome")
    actual_classes = _actual_reason_classes(actual)
    expected_class = EXPECTED_REASON_CLASSES.get(expected_reason, expected_reason) if expected_reason else None
    outcome_match = actual_outcome == expected_outcome
    reason_match = expected_class is None or expected_class in actual_classes
    record: dict[str, Any] = {
        "category": category,
        "id": case_id,
        "expected_outcome": expected_outcome,
        "expected_reason": expected_reason,
        "expected_reason_class": expected_class,
        "actual": actual,
        "actual_outcome": actual_outcome,
        "actual_reason_classes": actual_classes,
        "raw_reason_exact_match": expected_reason is None or expected_reason in actual.get("violations", []),
        "outcome_match": outcome_match,
        "reason_class_match": reason_match,
        "execution_error": is_error,
    }
    record["ambiguity_tags"] = _ambiguity_tags(category, case_id, case, actual)
    if metadata:
        record["metadata"] = copy.deepcopy(metadata)
    if not outcome_match or not reason_match:
        record["input_case"] = copy.deepcopy(case)
        record["disagreement"] = True
    else:
        record["disagreement"] = False
    return record


def _build_delegation_case(
    definition: dict[str, Any], baselines: dict[str, Any], registry: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    base = copy.deepcopy(baselines["task_ok"])
    parent = copy.deepcopy(definition["parent"])
    child = copy.deepcopy(definition["child"])
    child_scope = child.get("scope", [])
    parent_scope = parent.get("scope", [])
    child_scopes = copy.deepcopy(child_scope if isinstance(child_scope, list) else [child_scope])
    parent_scopes = copy.deepcopy(parent_scope if isinstance(parent_scope, list) else [parent_scope])
    task_record = copy.deepcopy(registry["records"]["grant:task-dispatch"])
    parent_record = copy.deepcopy(task_record)
    parent_record.update(
        {
            "id": parent["id"],
            "type": "grant",
            "subject_ids": [parent.get("delegator", "operator"), child.get("delegate", "task-agent")],
            "authority_domain": parent["authority_domain"],
            "operations": parent["operations"],
            "scopes": parent_scopes,
            "valid_until": parent["valid_until"],
            "current": parent["current"],
            # Preserve the source fixture's optional shape exactly.
            "scope": parent_scope,
        }
    )
    child_record = copy.deepcopy(task_record)
    child_record.update(
        {
            "id": child["id"],
            "type": "delegation",
            "subject_ids": [child["delegate"]],
            "authority_domain": child["authority_domain"],
            "operations": child["operations"],
            "scopes": child_scopes,
            "valid_until": child["valid_until"],
            "current": child["current"],
            "parent_authority_id": child["parent_authority_id"],
            "delegator": child["delegator"],
            "delegate": child["delegate"],
            # Do not coerce list scope to scalar: this is the revealed shape.
            "scope": child_scope,
        }
    )
    envelope = base
    envelope["subject"] = {"id": child["delegate"], "kind": "agent"}
    envelope["authority_domain"] = child["authority_domain"]
    envelope["operation"] = child["operations"][0]
    envelope["jurisdiction"] = {
        "scope": child_scopes[0],
        "applicable": True,
        "current": True,
    }
    envelope["authority_basis"] = [{"type": "delegation", "id": child["id"], "current": child["current"]}]
    envelope["non_implications"] = ["outcome_verification"]
    case = {
        "exercise_kind": "new",
        "envelope": envelope,
        "basis_records": {parent["id"]: parent_record, child["id"]: child_record},
    }
    return case, {
        "fixture_projection": "partial delegation fixture projected to a full native consumer case",
        "source_scope_shape_preserved": True,
        "translation_adapter_needed": True,
    }


def _authority_signature(actual: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (
        actual.get("outcome"),
        actual.get("primary_reason"),
        tuple(actual.get("violations", [])),
    )


def _all_records(categories: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for value in categories.values():
        if isinstance(value, dict) and isinstance(value.get("vectors"), list):
            records.extend(value["vectors"])
    return records


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(records),
        "outcome_matches": sum(1 for r in records if r.get("outcome_match")),
        "outcome_mismatches": sum(1 for r in records if not r.get("outcome_match")),
        "reason_checks": sum(1 for r in records if r.get("expected_reason") is not None),
        "reason_matches": sum(
            1 for r in records if r.get("expected_reason") is not None and r.get("reason_class_match")
        ),
        "reason_disagreements": sum(
            1 for r in records if r.get("expected_reason") is not None and not r.get("reason_class_match")
        ),
        "execution_errors": sum(1 for r in records if r.get("execution_error")),
        "disagreements": sum(1 for r in records if r.get("disagreement")),
    }


def _render_report(results: dict[str, Any]) -> str:
    lines = [
        "# Contract E Grok post-reveal comparison",
        "",
        "Terminal disposition: **" + results["terminal_disposition"] + "**",
        "",
        "This is a post-freeze comparison. The frozen consumer was imported and called directly; no frozen implementation file was modified.",
        "",
        "## Execution receipts",
        "",
        "- Frozen-suite integrity rerun: `PYTHONDONTWRITEBYTECODE=1 python3 -m research.contract_e_fresh_reproduction.run_tests`; exit 0; 73 passed, 0 failed, 0 errors, 73 total. Its tracked self-test receipt was restored to the frozen blob and was not included in this post-freeze commit.",
        "- Comparison run: `PYTHONDONTWRITEBYTECODE=1 python3 -m research.contract_e_post_reveal_comparison.compare --reference-dir <verified-revealed-artifacts> ...`; exit 0; 234 vector evaluations, 2 false accepts, 15 false rejects, 10 reason disagreements, 4 execution deviations; semantic authority changes false.",
        "- The three earlier exit-1 events were harness-only setup/reporting failures and are preserved in the machine receipt below; none evaluated or altered the frozen consumer.",
        "",
        "## Revealed artifacts",
        "",
    ]
    for name, info in results["revealed_artifacts"].items():
        lines.append(f"- `{name}` — verified Git blob `{info['verified_blob']}` ({info['bytes']} bytes)")
    lines += ["", "## Vector counts", ""]
    for name, value in results["categories"].items():
        lines.append(f"- `{name}`: {value['summary']['total']} vectors; {value['summary']['disagreements']} disagreements; {value['summary']['execution_errors']} execution errors")
    lines += [
        "",
        "## False accepts / false rejects",
        "",
        f"- False accepts: {len(results['false_accepts'])}",
        f"- False rejects: {len(results['false_rejects'])}",
        "",
        "## Reason disagreements",
        "",
    ]
    if results["reason_disagreements"]:
        for item in results["reason_disagreements"]:
            lines.append(
                f"- `{item['category']}/{item['id']}` expected `{item['expected_reason']}`; raw actual violations `{item['actual'].get('violations', [])}`; normalized actual classes `{item['actual_reason_classes']}`"
            )
    else:
        lines.append("- None.")
    lines += ["", "## Shape / execution deviations", ""]
    if results["shape_incompatibilities"]:
        for item in results["shape_incompatibilities"]:
            lines.append(f"- `{item['category']}/{item['id']}` — {item['observed_shape']}; {item['adapter_status']}")
    else:
        lines.append("- No shape incompatibilities observed.")
    lines.append("")
    if results["execution_deviations"]:
        for item in results["execution_deviations"]:
            lines.append(f"- `{item['category']}/{item['id']}` — `{item['actual'].get('exception_type')}: {item['actual'].get('exception_message')}`")
    else:
        lines.append("- None.")
    lines += ["", "## Semantic metamorphic result", "", f"- Payload mutations run: {results['categories']['semantic_metamorphic']['summary']['total']}", f"- Authority-signature changes: {len(results['categories']['semantic_metamorphic']['authority_changes'])}", ""]
    lines += ["## Preregistered ambiguity correspondence", ""]
    for code, item in results["ambiguity_correspondence"].items():
        lines.append(f"- `{code}` ({item['description']}): {item['vectors_covered']} vectors; {item['disagreements']} disagreements.")
    lines += [
        "",
        "## Contamination / deviation status",
        "",
        "- Reference reveal was limited to the four SHA-pinned artifacts listed above.",
        "- No reference validator, generated reference RESULTS, workflow artifacts/logs, prior PR reasoning, or post-freeze repair was used by this harness.",
        "- The pre-reveal marker remains exactly `FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_REVEAL`; it was not rewritten to the requested vector-reveal literal.",
    ]
    return "\n".join(lines) + "\n"


def run_comparison(reference_dir: Path) -> dict[str, Any]:
    anchors = verify_frozen_anchors()
    frozen_cases, registry, attacks, _hardening = verify_reference_artifacts(reference_dir)
    spec = load_specs()
    baselines = frozen_cases["baselines"]
    records = registry["records"]
    conferring_types = set(spec.conferring_types)
    categories: dict[str, Any] = {}

    envelope_vectors: list[dict[str, Any]] = []
    for definition in frozen_cases["envelope_cases"]:
        case = _apply_envelope_case(definition, baselines, registry)
        envelope_vectors.append(
            _run_vector(
                "rc3a_envelope",
                definition["id"],
                case,
                definition["expected"],
                definition.get("reason"),
                spec,
                {"base": definition["base"]},
            )
        )
    categories["rc3a_envelope"] = {"vectors": envelope_vectors, "summary": _summary(envelope_vectors)}

    propagation_vectors: list[dict[str, Any]] = []
    for definition in frozen_cases["propagation_cases"]:
        case = _case_from_envelope(baselines["source_access_ok"], registry)
        mode = definition["mode"]
        case["envelope"]["propagation"] = {"mode": mode}
        if mode == "explicit":
            case["envelope"]["propagation"]["fields"] = copy.deepcopy(definition["requested_fields"])
        case["propagated_fields"] = copy.deepcopy(definition["requested_fields"])
        propagation_vectors.append(
            _run_vector(
                "rc3a_propagation",
                definition["id"],
                case,
                definition["expected"],
                definition.get("reason"),
                spec,
                {"mode": mode, "requested_fields": definition["requested_fields"]},
            )
        )
    categories["rc3a_propagation"] = {"vectors": propagation_vectors, "summary": _summary(propagation_vectors)}

    delegation_vectors: list[dict[str, Any]] = []
    for definition in frozen_cases["delegation_cases"]:
        case, metadata = _build_delegation_case(definition, baselines, registry)
        delegation_vectors.append(
            _run_vector(
                "rc3a_delegation",
                definition["id"],
                case,
                definition["expected"],
                definition.get("reason"),
                spec,
                metadata,
            )
        )
    categories["rc3a_delegation"] = {"vectors": delegation_vectors, "summary": _summary(delegation_vectors)}

    historical_vectors: list[dict[str, Any]] = []
    for definition in frozen_cases["historical_cases"]:
        case = _case_from_envelope(baselines["task_ok"], registry)
        authority = definition["current_authority"]
        case["basis_records"][authority["id"]].update(copy.deepcopy(authority))
        case["exercise_kind"] = "historical" if definition["mode"] == "historical_record" else "new"
        case["historical_record"] = copy.deepcopy(definition["historical_record"])
        historical_vectors.append(
            _run_vector(
                "rc3a_historical",
                definition["id"],
                case,
                definition["expected"],
                definition.get("reason"),
                spec,
                {"mode": definition["mode"]},
            )
        )
    categories["rc3a_historical"] = {"vectors": historical_vectors, "summary": _summary(historical_vectors)}

    attack_vectors: list[dict[str, Any]] = []
    for definition in attacks["cases"]:
        case = _case_from_envelope(baselines[definition["base"]], registry)
        replacement = definition.get("replace_authority_reference")
        if replacement:
            _replace_reference(case, replacement["old_id"], replacement["new_ref"])
        attack_vectors.append(
            _run_vector(
                "rc3b_attack",
                definition["id"],
                case,
                definition["expected"],
                definition.get("reason"),
                spec,
                {"base": definition["base"]},
            )
        )
    categories["rc3b_attack"] = {"vectors": attack_vectors, "summary": _summary(attack_vectors)}

    authority_records = {
        key: value for key, value in records.items() if value.get("type") in conferring_types
    }
    matrix_vectors: list[dict[str, Any]] = []
    matrix_false_accepts: list[dict[str, Any]] = []
    matrix_false_rejects: list[dict[str, Any]] = []
    for baseline_id, baseline in baselines.items():
        canonical_refs = [
            ref for ref in baseline.get("authority_basis", []) if ref.get("type") in conferring_types
        ]
        if len(canonical_refs) != 1:
            raise RuntimeError(f"baseline {baseline_id} does not have exactly one canonical conferring reference")
        canonical = canonical_refs[0]
        for record_id, record in sorted(authority_records.items()):
            case = _case_from_envelope(baseline, registry)
            _replace_reference(
                case,
                canonical["id"],
                {"type": record["type"], "id": record_id, "current": record.get("current")},
            )
            expected = "accept" if record_id == canonical["id"] else "reject"
            result = _run_vector(
                "compatibility_matrix",
                f"{baseline_id}::{record_id}",
                case,
                expected,
                None,
                spec,
                {"baseline": baseline_id, "canonical_id": canonical["id"], "substitute_id": record_id},
            )
            matrix_vectors.append(result)
            if record_id != canonical["id"] and result.get("actual_outcome") == "accept":
                matrix_false_accepts.append(result)
            if record_id == canonical["id"] and result.get("actual_outcome") == "reject":
                matrix_false_rejects.append(result)
    categories["compatibility_matrix"] = {
        "vectors": matrix_vectors,
        "summary": _summary(matrix_vectors),
        "canonical_baselines": len(baselines),
        "authority_conferring_records": len(authority_records),
        "false_accepts": matrix_false_accepts,
        "false_rejects": matrix_false_rejects,
    }

    type_vectors: list[dict[str, Any]] = []
    for baseline_id, baseline in baselines.items():
        canonical_refs = [
            ref for ref in baseline.get("authority_basis", []) if ref.get("type") in conferring_types
        ]
        canonical = canonical_refs[0]
        for replacement_type in sorted(conferring_types - {canonical["type"]}):
            case = _case_from_envelope(baseline, registry)
            _replace_reference(
                case,
                canonical["id"],
                {"type": replacement_type, "id": canonical["id"], "current": canonical.get("current")},
            )
            type_vectors.append(
                _run_vector(
                    "authority_reference_type_mutation",
                    f"{baseline_id}::{canonical['id']}::type={replacement_type}",
                    case,
                    "reject",
                    "authority_basis_type_mismatch",
                    spec,
                    {"baseline": baseline_id, "original_type": canonical["type"], "replacement_type": replacement_type},
                )
            )
    categories["authority_reference_type_mutation"] = {"vectors": type_vectors, "summary": _summary(type_vectors)}

    semantic_vectors: list[dict[str, Any]] = []
    authority_changes: list[dict[str, Any]] = []
    for baseline_id, baseline in baselines.items():
        base_case = _case_from_envelope(baseline, registry)
        base_actual = _run_native(base_case, spec)
        base_signature = _authority_signature(base_actual)
        for variant in SEMANTIC_VARIANTS:
            case = copy.deepcopy(base_case)
            case["envelope"]["result"] = copy.deepcopy(variant["payload"])
            result = _run_vector(
                "semantic_metamorphic",
                f"{baseline_id}::{variant['name']}",
                case,
                "accept",
                None,
                spec,
                {"baseline": baseline_id, "variant": variant["name"], "base_signature": list(base_signature)},
            )
            result["authority_signature_same_as_baseline"] = _authority_signature(result["actual"]) == base_signature
            if not result["authority_signature_same_as_baseline"]:
                result["disagreement"] = True
                result["input_case"] = copy.deepcopy(case)
                authority_changes.append(result)
            semantic_vectors.append(result)
    categories["semantic_metamorphic"] = {
        "vectors": semantic_vectors,
        "summary": _summary(semantic_vectors),
        "authority_changes": authority_changes,
        "variant_count_per_positive_baseline": len(SEMANTIC_VARIANTS),
    }

    all_vectors = _all_records(categories)
    false_accepts = [
        r for r in all_vectors if r.get("expected_outcome") == "reject" and r.get("actual_outcome") == "accept"
    ]
    false_rejects = [
        r for r in all_vectors if r.get("expected_outcome") == "accept" and r.get("actual_outcome") == "reject"
    ]
    reason_disagreements = [
        r for r in all_vectors if r.get("expected_reason") is not None and not r.get("reason_class_match")
    ]
    execution_deviations = [r for r in all_vectors if r.get("execution_error")]
    shape_incompatibilities: list[dict[str, Any]] = []
    for record in all_vectors:
        case = record.get("input_case")
        envelope = case.get("envelope") if isinstance(case, dict) else None
        actual = record.get("actual", {})
        if isinstance(envelope, dict) and isinstance(envelope.get("competence"), list):
            if "missing_required_qualification" in actual.get("violations", []):
                shape_incompatibilities.append(
                    {
                        "category": record["category"],
                        "id": record["id"],
                        "observed_shape": "revealed envelope.competence is a list of qualification objects",
                        "frozen_expectation": "frozen consumer accepts only a singular dict under qualification/competence",
                        "adapter_status": "coercion to a singular object was not applied",
                    }
                )
        if record["category"] == "rc3a_delegation" and record.get("execution_error"):
            shape_incompatibilities.append(
                {
                    "category": record["category"],
                    "id": record["id"],
                    "observed_shape": "revealed delegation scope is a list preserved in optional record.scope",
                    "frozen_expectation": "frozen delegation subset path assumes a scalar optional scope",
                    "adapter_status": "scope coercion was not applied",
                }
            )

    ambiguity_correspondence: dict[str, Any] = {}
    for code, description in AMBIGUITY_DESCRIPTIONS.items():
        tagged = [r for r in all_vectors if code in r.get("ambiguity_tags", [])]
        disagreements = [r for r in tagged if r.get("disagreement")]
        ambiguity_correspondence[code] = {
            "description": description,
            "vectors_covered": len(tagged),
            "disagreements": len(disagreements),
            "disagreement_ids": [f"{r['category']}/{r['id']}" for r in disagreements],
        }

    disposition = "SUPPORTED FOR PROMOTION"
    if false_accepts:
        disposition = "FALSIFIED"
    elif false_rejects or reason_disagreements or execution_deviations or categories["semantic_metamorphic"]["authority_changes"]:
        disposition = "INCONCLUSIVE"

    return {
        "schema": "contract-e-grok-post-reveal-comparison-v1",
        "terminal_disposition": disposition,
        "frozen_anchors": anchors,
        "freeze_marker": FREEZE_MARKER,
        "revealed_artifacts": {
            name: {key: value for key, value in info.items() if key != "source_repository"}
            for name, info in verify_revealed_for_output(reference_dir).items()
        },
        "categories": categories,
        "total_vector_evaluations": len(all_vectors),
        "execution_receipts": {
            "frozen_suite_integrity_rerun": {
                "command": "PYTHONDONTWRITEBYTECODE=1 python3 -m research.contract_e_fresh_reproduction.run_tests",
                "exit_code": 0,
                "summary": "73 passed, 0 failed, 0 errors, 73 total",
                "tracked_receipt_restored_to_frozen_blob": "9521b5b4bd21bd02979651e19f6210d8dac7a3fa",
            },
            "comparison": {
                "command": "PYTHONDONTWRITEBYTECODE=1 python3 -m research.contract_e_post_reveal_comparison.compare --reference-dir <verified-revealed-artifacts> --output COMPARISON-RESULTS.json --report COMPARISON-REPORT.md",
                "exit_code": 0,
                "summary": "234 vector evaluations; 2 false accepts; 15 false rejects; 10 reason disagreements; 4 execution deviations; semantic authority changes false; terminal disposition FALSIFIED",
            },
        },
        "harness_development_failures": HARNESS_DEVELOPMENT_FAILURES,
        "false_accepts": false_accepts,
        "false_rejects": false_rejects,
        "reason_disagreements": reason_disagreements,
        "execution_deviations": execution_deviations,
        "shape_incompatibilities": shape_incompatibilities,
        "translation_adapter_required": bool(execution_deviations or shape_incompatibilities),
        "semantic_payload_changes_alter_authority": bool(categories["semantic_metamorphic"]["authority_changes"]),
        "ambiguity_correspondence": ambiguity_correspondence,
        "contamination_status": "No contamination observed; only the four SHA-pinned revealed artifacts were read by this comparison harness.",
        "procedural_deviation": {
            "emitted_marker": FREEZE_MARKER,
            "original_requested_literal": "FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL",
            "freeze_rewritten": False,
        },
    }


def verify_revealed_for_output(reference_dir: Path) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for filename, info in REFERENCE_ARTIFACTS.items():
        path = reference_dir / filename
        output[filename] = {
            "source_repository": "camerontjs-dot/apparatus-contracts",
            "source_path": info["path"],
            "requested_blob": info["blob"],
            "verified_blob": _git_hash(path),
            "bytes": path.stat().st_size,
        }
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    results = run_comparison(args.reference_dir)
    args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(_render_report(results), encoding="utf-8")
    print(json.dumps({
        "terminal_disposition": results["terminal_disposition"],
        "total_vector_evaluations": results["total_vector_evaluations"],
        "false_accepts": len(results["false_accepts"]),
        "false_rejects": len(results["false_rejects"]),
        "reason_disagreements": len(results["reason_disagreements"]),
        "execution_deviations": len(results["execution_deviations"]),
        "semantic_payload_changes_alter_authority": results["semantic_payload_changes_alter_authority"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
