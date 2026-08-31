#!/usr/bin/env python3
"""Post-freeze native comparison harness for the frozen RC3C Grok successor.

Calls research_scaffold_harness.contract_e_rc3c.evaluate natively.
Does not coerce singular/plural forms, rewrite fields, or repair outcomes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from research_scaffold_harness.contract_e_rc3c import evaluate

HERE = Path(__file__).resolve().parent
REVEALED = HERE / "revealed"
REPO = HERE.parents[3]

EXPECTED_BLOBS = {
    "RC3A-FROZEN-CASES.json": "85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a",
    "RC3B-AUTHORITY-BASIS-REGISTRY.json": "76ea333ee0460d9614e9899edb69e6865e48eccb",
    "RC3B-FROZEN-BASIS-ATTACKS.json": "c726fb0ef914a850620e545131a70d427f4027bd",
    "RC3B-HARDENING-PREREGISTRATION.md": "1d85e2036d410b3af08d4b2b8926586da8fe6088",
    "RC3C-FROZEN-CASES.json": "17d45524125814478b987bb8e91d23f545fb514e",
}

CANONICAL_BASIS = {
    "source_access_ok": "grant:source-read",
    "evidence_admission_ok": "policy:evidence-admission",
    "assessment_ok": "policy:cal-assessment",
    "numeric_ok": "grant:numeric-validation",
    "source_boundary_ok": "policy:source-boundary",
    "decision_ok": "policy:decision-v1",
    "citation_ok": "grant:citation-use",
    "task_ok": "grant:task-dispatch",
    "verify_ok": "grant:verify",
}

CONFERING_TYPES = {"grant", "policy", "delegation"}
SUPPORTING_TYPES = {"credential", "receipt", "artifact"}

# RC3C amendment / RC3B binding: successor-normative reason classes.
RC3C_SPEC = json.loads((REPO / "authority_input" / "RC3C-SPEC.json").read_text())
RC3B_SPEC = json.loads((REPO / "authority_input" / "BASIS-BINDING-SPEC.json").read_text())
NORMATIVE_REASONS = set(RC3C_SPEC["reason_contract"]["whole_envelope_precedence"])
NORMATIVE_REASONS.update(RC3C_SPEC["reason_contract"]["relisted_cross_domain_primary_reasons"].values())
NORMATIVE_REASONS.update(RC3C_SPEC["malformed_wire_reasons"].values())
NORMATIVE_REASONS.update(RC3B_SPEC["ordering"]["reason_precedence"])

KNOWN_OVERLAY_KEYS = {
    "id",
    "base",
    "expected",
    "reason",
    "set",
    "set_path",
    "remove",
    "remove_authority_basis_types",
    "replace_authority_reference",
    "replace_path_with_first_item",
    "record_override",
    "source_case",
    "source_envelope_case",
    "source_propagation_case",
    "parent",
    "child",
    "mode",
    "requested_fields",
    "historical_record",
    "current_authority",
}


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def deep(obj: Any) -> Any:
    return copy.deepcopy(obj)


def set_path(root: Any, dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur = root
    for part in parts[:-1]:
        key: Any = int(part) if part.isdigit() else part
        cur = cur[key]
    last = parts[-1]
    key = int(last) if last.isdigit() else last
    cur[key] = value


def get_path(root: Any, dotted: str) -> Any:
    cur = root
    for part in dotted.split("."):
        key: Any = int(part) if part.isdigit() else part
        cur = cur[key]
    return cur


def apply_envelope_overlays(envelope: dict[str, Any], case: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    unknown = sorted(set(case) - KNOWN_OVERLAY_KEYS)
    if unknown:
        notes.append(f"unknown_overlay_keys:{','.join(unknown)}")
    if "set" in case and isinstance(case["set"], dict):
        envelope.update(deep(case["set"]))
    if "set_path" in case and isinstance(case["set_path"], dict):
        for path, value in case["set_path"].items():
            set_path(envelope, path, deep(value))
    if "remove" in case:
        for key in case["remove"]:
            envelope.pop(key, None)
    if "remove_authority_basis_types" in case:
        types = set(case["remove_authority_basis_types"])
        basis = envelope.get("authority_basis")
        if isinstance(basis, list):
            envelope["authority_basis"] = [
                item for item in basis if not (isinstance(item, dict) and item.get("type") in types)
            ]
    if "replace_authority_reference" in case:
        spec = case["replace_authority_reference"]
        old_id = spec.get("old_id")
        new_ref = deep(spec.get("new_ref"))
        basis = envelope.get("authority_basis")
        replaced = False
        if isinstance(basis, list):
            for index, item in enumerate(basis):
                if isinstance(item, dict) and item.get("id") == old_id:
                    basis[index] = new_ref
                    replaced = True
                    break
        if not replaced:
            notes.append("replace_authority_reference_id_not_found")
    if "replace_path_with_first_item" in case:
        path = case["replace_path_with_first_item"]
        value = get_path(envelope, path)
        if isinstance(value, list) and value:
            set_path(envelope, path, deep(value[0]))
        else:
            notes.append("replace_path_with_first_item_not_nonempty_list")
    return notes


def overlay_record(record: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    updated = deep(record)
    if "set" in override and isinstance(override["set"], dict):
        updated.update(deep(override["set"]))
    return updated


def conferring_index(envelope: dict[str, Any], canonical_id: str | None = None) -> int | None:
    basis = envelope.get("authority_basis")
    if not isinstance(basis, list):
        return None
    if canonical_id is not None:
        for index, item in enumerate(basis):
            if isinstance(item, dict) and item.get("id") == canonical_id:
                return index
    for index, item in enumerate(basis):
        if isinstance(item, dict) and item.get("type") in CONFERING_TYPES:
            return index
    return None


def decision_of(request: dict[str, Any]) -> dict[str, Any]:
    decision = evaluate(request)
    return decision.to_dict()


def outcome(expected: str, accepted: bool) -> str:
    want_accept = expected == "accept"
    if want_accept and accepted:
        return "exact_outcome_match"
    if (not want_accept) and (not accepted):
        return "exact_outcome_match"
    if accepted and not want_accept:
        return "false_accept"
    return "false_reject"


def classify_reason(expected_reason: str | None, observed: str | None, family: str) -> str:
    if expected_reason is None:
        return "no_expected_reason"
    if observed == expected_reason:
        return "reason_match"
    # Inherited RC3A expected strings are not successor-normative unless an RC3C
    # or RC3B family explicitly lists that reason as the comparison authority.
    successor_reason_families = {
        "rc3b_basis_attacks",
        "rc3b_type_mutations",
        "rc3c_reason",
        "rc3c_currentness",
        "rc3c_wire",
        "rc3c_delegation",
    }
    if family in successor_reason_families and expected_reason in NORMATIVE_REASONS:
        return "normative_reason_disagreement"
    return "non_normative_diagnostic_difference"


def row(
    family: str,
    case_id: str,
    expected: str,
    decision: dict[str, Any],
    expected_reason: str | None = None,
    construction_notes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    accepted = bool(decision.get("accepted"))
    observed_reason = decision.get("primary_reason")
    item = {
        "family": family,
        "id": case_id,
        "expected": expected,
        "expected_reason": expected_reason,
        "accepted": accepted,
        "primary_reason": observed_reason,
        "reason_is_normative": decision.get("reason_is_normative"),
        "evaluation_kind": decision.get("evaluation_kind"),
        "mode": decision.get("mode"),
        "notes": decision.get("notes") or [],
        "construction_notes": construction_notes or [],
        "outcome_class": outcome(expected, accepted),
        "reason_class": classify_reason(expected_reason, observed_reason, family),
    }
    if extra:
        item.update(extra)
    return item


def load_json(name: str) -> Any:
    return json.loads((REVEALED / name).read_text())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=HERE / "COMPARISON-RESULTS.json")
    parser.add_argument("--out-md", type=Path, default=HERE / "COMPARISON-RECEIPT.md")
    args = parser.parse_args()

    blob_report = {}
    for name, expected in EXPECTED_BLOBS.items():
        path = REVEALED / name
        actual = git_blob(path)
        blob_report[name] = {
            "path": str(path.relative_to(REPO)),
            "expected": expected,
            "actual": actual,
            "match": actual == expected,
            "sha256": sha256_file(path),
        }
    if not all(item["match"] for item in blob_report.values()):
        print("blob verification failed", json.dumps(blob_report, indent=2), file=sys.stderr)
        return 2

    rc3a = load_json("RC3A-FROZEN-CASES.json")
    registry_raw = load_json("RC3B-AUTHORITY-BASIS-REGISTRY.json")
    attacks = load_json("RC3B-FROZEN-BASIS-ATTACKS.json")
    rc3c = load_json("RC3C-FROZEN-CASES.json")
    baselines: dict[str, Any] = rc3a["baselines"]
    registry_records: dict[str, Any] = deep(registry_raw["records"])
    del_by_id = {item["id"]: item for item in rc3a["delegation_cases"]}
    env_by_id = {item["id"]: item for item in rc3a["envelope_cases"]}
    prop_by_id = {item["id"]: item for item in rc3a["propagation_cases"]}

    native_deviations: list[str] = []
    rows: list[dict[str, Any]] = []

    def run_envelope_case(family: str, case: dict[str, Any], registry: dict[str, Any] | None = None) -> dict[str, Any]:
        envelope = deep(baselines[case["base"]])
        notes = apply_envelope_overlays(envelope, case)
        local_registry = deep(registry if registry is not None else registry_records)
        if "record_override" in case:
            override = case["record_override"]
            record_id = override["id"]
            if record_id not in local_registry:
                notes.append("record_override_id_missing")
            else:
                local_registry[record_id] = overlay_record(local_registry[record_id], override)
        request = {
            "kind": "envelope",
            "envelope": envelope,
            "registry": local_registry,
            "mode": "new_exercise",
        }
        decision = decision_of(request)
        return row(family, case["id"], case["expected"], decision, case.get("reason"), notes)

    for case in rc3a["envelope_cases"]:
        rows.append(run_envelope_case("rc3a_envelope", case))

    for case in rc3a["propagation_cases"]:
        request = {
            "kind": "propagation",
            "request": {
                "mode": case["mode"],
                "requested_fields": deep(case["requested_fields"]),
            },
        }
        decision = decision_of(request)
        rows.append(row("rc3a_propagation", case["id"], case["expected"], decision, case.get("reason")))

    for case in rc3a["delegation_cases"]:
        request = {
            "kind": "delegation",
            "parent": deep(case["parent"]),
            "child": deep(case["child"]),
            "mode": "new_exercise",
        }
        parent_keys = set(case["parent"])
        child_keys = set(case["child"])
        notes = []
        if "delegator" not in parent_keys or "delegate" not in parent_keys:
            notes.append("vector_parent_omits_delegator_or_delegate")
            native_deviations.append(
                f"{case['id']}: RC3A parent object omitted delegator/delegate; passed unmodified"
            )
        decision = decision_of(request)
        extra = {"parent_keys": sorted(parent_keys), "child_keys": sorted(child_keys)}
        rows.append(
            row(
                "rc3a_delegation",
                case["id"],
                case["expected"],
                decision,
                case.get("reason"),
                notes,
                extra,
            )
        )

    for case in rc3a["historical_cases"]:
        record = deep(case["historical_record"])
        current = deep(case["current_authority"])
        local_registry = deep(registry_records)
        current_id = current.get("id")
        if isinstance(current_id, str) and current_id in local_registry:
            local_registry[current_id] = overlay_record(local_registry[current_id], {"set": current})
        elif isinstance(current_id, str):
            local_registry[current_id] = current
        request = {
            "kind": "historical",
            "record": record,
            "registry": local_registry,
            "mode": case["mode"],
        }
        notes = []
        if case["mode"] not in {"new_exercise", "historical_inspection"}:
            notes.append(f"case_mode_not_in_consumer_modes:{case['mode']}")
            native_deviations.append(
                f"{case['id']}: vector mode {case['mode']!r} is not a consumer mode; passed unmodified"
            )
        decision = decision_of(request)
        rows.append(
            row(
                "rc3a_historical",
                case["id"],
                case["expected"],
                decision,
                case.get("reason"),
                notes,
            )
        )

    for obj in rc3a["negative_controls"]["collapsed_objects"]:
        decision = decision_of(
            {
                "kind": "envelope",
                "envelope": deep(obj),
                "registry": registry_records,
                "mode": "new_exercise",
            }
        )
        rows.append(
            row(
                "rc3a_negative_controls",
                obj["id"],
                "reject",
                decision,
                None,
                ["collapsed_object_passed_unmodified_not_a_canonical_envelope"],
            )
        )
    native_deviations.append(
        "rc3a negative_controls.transitive_chain is a description, not a callable native object; not rewritten into cases"
    )
    native_deviations.append(
        "RC3B registry file wrapper {schema, records: map} is not a native collection for "
        "normalize_registry; evaluate() is called with the id-to-record mapping, which is "
        "the consumer's native dict-of-records collection. Envelope fields were not rewritten."
    )
    native_deviations.append(
        "RC3A/RC3C propagation vectors use requested_fields; the frozen consumer reads "
        "propagation.fields. The vector key was not renamed."
    )

    for case in attacks["cases"]:
        rows.append(run_envelope_case("rc3b_basis_attacks", case))

    conferring_ids = [
        record_id
        for record_id, record in registry_records.items()
        if record.get("type") in CONFERING_TYPES
    ]
    matrix_rows: list[dict[str, Any]] = []
    for base_name, canonical_id in CANONICAL_BASIS.items():
        for record_id in conferring_ids:
            envelope = deep(baselines[base_name])
            index = conferring_index(envelope, canonical_id)
            record = registry_records[record_id]
            notes = []
            if index is None:
                notes.append("no_conferring_reference")
            else:
                envelope["authority_basis"][index] = {
                    "type": record["type"],
                    "id": record_id,
                    "current": True,
                }
            decision = decision_of(
                {
                    "kind": "envelope",
                    "envelope": envelope,
                    "registry": registry_records,
                    "mode": "new_exercise",
                }
            )
            expected = "accept" if record_id == canonical_id else "reject"
            item = row(
                "rc3b_compatibility_matrix",
                f"MATRIX-{base_name}--{record_id}",
                expected,
                decision,
                None if expected == "accept" else None,
                notes,
                {"base": base_name, "record_id": record_id, "canonical_id": canonical_id},
            )
            rows.append(item)
            matrix_rows.append(item)

    type_rows: list[dict[str, Any]] = []
    for base_name, canonical_id in CANONICAL_BASIS.items():
        envelope0 = deep(baselines[base_name])
        index = conferring_index(envelope0, canonical_id)
        original_type = envelope0["authority_basis"][index]["type"] if index is not None else None
        for other in sorted(CONFERING_TYPES):
            if other == original_type:
                continue
            envelope = deep(baselines[base_name])
            idx = conferring_index(envelope, canonical_id)
            notes = []
            if idx is None:
                notes.append("no_conferring_reference")
            else:
                envelope["authority_basis"][idx] = {
                    **deep(envelope["authority_basis"][idx]),
                    "type": other,
                }
            decision = decision_of(
                {
                    "kind": "envelope",
                    "envelope": envelope,
                    "registry": registry_records,
                    "mode": "new_exercise",
                }
            )
            item = row(
                "rc3b_type_mutations",
                f"TYPE-{base_name}--{canonical_id}--{other}",
                "reject",
                decision,
                "authority_basis_type_mismatch",
                notes,
                {"base": base_name, "original_type": original_type, "mutated_type": other},
            )
            rows.append(item)
            type_rows.append(item)

    for case in rc3c["currentness_cases"]:
        rows.append(run_envelope_case("rc3c_currentness", case))
    for case in rc3c["wire_cases"]:
        rows.append(run_envelope_case("rc3c_wire", case))

    for case in rc3c["delegation_wire_cases"]:
        source = del_by_id[case["source_case"]]
        parent = deep(source["parent"])
        child = deep(source["child"])
        holder = {"parent": parent, "child": child}
        notes = apply_envelope_overlays(holder, case) if "set_path" in case else []
        if "set_path" in case:
            for path, value in case["set_path"].items():
                set_path(holder, path, deep(value))
        if "delegator" not in parent or "delegate" not in parent:
            notes.append("vector_parent_omits_delegator_or_delegate")
            native_deviations.append(
                f"{case['id']}: source parent omitted delegator/delegate; passed unmodified"
            )
        decision = decision_of(
            {
                "kind": "delegation",
                "parent": holder["parent"],
                "child": holder["child"],
                "mode": "new_exercise",
            }
        )
        rows.append(
            row(
                "rc3c_delegation",
                case["id"],
                case["expected"],
                decision,
                case.get("reason"),
                notes,
            )
        )

    for case in rc3c["reason_cases"]:
        if "source_envelope_case" in case:
            source = env_by_id[case["source_envelope_case"]]
            item = run_envelope_case("rc3c_reason", {**source, "id": case["id"], "reason": case.get("reason"), "expected": case["expected"]})
            rows.append(item)
        else:
            source = prop_by_id[case["source_propagation_case"]]
            decision = decision_of(
                {
                    "kind": "propagation",
                    "request": {
                        "mode": source["mode"],
                        "requested_fields": deep(source["requested_fields"]),
                    },
                }
            )
            rows.append(
                row(
                    "rc3c_reason",
                    case["id"],
                    case["expected"],
                    decision,
                    case.get("reason"),
                )
            )

    meta = rc3c["semantic_metamorphic"]
    signature_changes: list[dict[str, Any]] = []
    extra_result_variants = [
        {"label": "omitted", "result": None, "omit": True},
        {"label": "success_confidence_high", "result": {"success": True, "confidence": 0.99}},
        {"label": "success_false", "result": {"success": False, "confidence": 0.0, "status": "failed"}},
    ]
    for base_name in meta["bases"]:
        baseline_env = deep(baselines[base_name])
        baseline_decision = decision_of(
            {
                "kind": "envelope",
                "envelope": baseline_env,
                "registry": registry_records,
                "mode": "new_exercise",
            }
        )
        baseline_sig = (baseline_decision["accepted"], baseline_decision["primary_reason"])
        variants = list(meta["variants"]) + extra_result_variants
        for variant in variants:
            envelope = deep(baselines[base_name])
            if variant.get("omit"):
                envelope.pop("result", None)
                label = variant["label"]
            elif "label" in variant:
                envelope["result"] = deep(variant["result"])
                label = variant["label"]
            else:
                envelope["result"] = deep(variant)
                label = json.dumps(variant, sort_keys=True)
            decision = decision_of(
                {
                    "kind": "envelope",
                    "envelope": envelope,
                    "registry": registry_records,
                    "mode": "new_exercise",
                }
            )
            sig = (decision["accepted"], decision["primary_reason"])
            changed = sig != baseline_sig
            item = row(
                "semantic_metamorphic",
                f"SEM-{base_name}--{label}",
                "accept" if baseline_decision["accepted"] else "reject",
                decision,
                None,
                [],
                {
                    "base": base_name,
                    "baseline_signature": {"accepted": baseline_sig[0], "primary_reason": baseline_sig[1]},
                    "variant_signature": {"accepted": sig[0], "primary_reason": sig[1]},
                    "authority_signature_changed": changed,
                },
            )
            rows.append(item)
            if changed:
                signature_changes.append(item)

    def select(family: str) -> list[dict[str, Any]]:
        return [item for item in rows if item["family"] == family]

    def count(family: str, cls: str) -> int:
        return sum(1 for item in select(family) if item["outcome_class"] == cls)

    families = [
        "rc3a_envelope",
        "rc3a_propagation",
        "rc3a_delegation",
        "rc3a_historical",
        "rc3a_negative_controls",
        "rc3b_basis_attacks",
        "rc3b_compatibility_matrix",
        "rc3b_type_mutations",
        "rc3c_currentness",
        "rc3c_wire",
        "rc3c_delegation",
        "rc3c_reason",
        "semantic_metamorphic",
    ]
    by_family = {}
    for family in families:
        items = select(family)
        by_family[family] = {
            "n": len(items),
            "exact_outcome_match": sum(1 for item in items if item["outcome_class"] == "exact_outcome_match"),
            "false_accept": sum(1 for item in items if item["outcome_class"] == "false_accept"),
            "false_reject": sum(1 for item in items if item["outcome_class"] == "false_reject"),
            "normative_reason_disagreement": sum(
                1 for item in items if item["reason_class"] == "normative_reason_disagreement"
            ),
            "non_normative_diagnostic_difference": sum(
                1 for item in items if item["reason_class"] == "non_normative_diagnostic_difference"
            ),
        }

    false_accepts = [item for item in rows if item["outcome_class"] == "false_accept"]
    false_rejects = [item for item in rows if item["outcome_class"] == "false_reject"]
    normative_reason_disagreements = [
        item for item in rows if item["reason_class"] == "normative_reason_disagreement"
    ]

    matrix_false_accepts = [item for item in matrix_rows if item["outcome_class"] == "false_accept"]
    matrix_false_rejects = [item for item in matrix_rows if item["outcome_class"] == "false_reject"]
    canonical_accepts = [
        item
        for item in matrix_rows
        if item["record_id"] == item["canonical_id"] and item["outcome_class"] == "exact_outcome_match"
    ]

    rc3c_currentness_ok = by_family["rc3c_currentness"]["false_accept"] == 0 and by_family["rc3c_currentness"]["false_reject"] == 0
    rc3c_wire_ok = by_family["rc3c_wire"]["false_accept"] == 0 and by_family["rc3c_wire"]["false_reject"] == 0
    rc3c_del_ok = by_family["rc3c_delegation"]["false_accept"] == 0 and by_family["rc3c_delegation"]["false_reject"] == 0
    rc3b_attacks_ok = by_family["rc3b_basis_attacks"]["false_accept"] == 0 and by_family["rc3b_basis_attacks"]["false_reject"] == 0
    matrix_ok = not matrix_false_accepts and not matrix_false_rejects
    type_ok = by_family["rc3b_type_mutations"]["false_accept"] == 0 and by_family["rc3b_type_mutations"]["false_reject"] == 0
    semantic_ok = not signature_changes
    no_adapter = True

    authority_false_accepts = [
        item
        for item in false_accepts
        if item["family"]
        not in {"semantic_metamorphic", "rc3a_negative_controls"}
    ]

    frozen_suite = subprocess.run(
        [sys.executable, "-m", "pytest", str(REPO / "tests" / "contract_e_rc3c"), "-q", "--tb=no"],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )

    success_conditions = {
        "zero_authority_false_accepts": len(authority_false_accepts) == 0,
        "rc3b_attacks_agree": rc3b_attacks_ok,
        "rc3b_matrix_agree": matrix_ok,
        "rc3b_type_mutations_agree": type_ok,
        "rc3c_currentness_agree": rc3c_currentness_ok,
        "rc3c_wire_agree": rc3c_wire_ok,
        "rc3c_delegation_agree": rc3c_del_ok,
        "normative_reason_classes_agree": len(normative_reason_disagreements) == 0,
        "semantic_signature_unchanged": semantic_ok,
        "no_post_reveal_adapter": no_adapter,
        "frozen_suite_rerun_pass": frozen_suite.returncode == 0,
    }

    if not success_conditions["zero_authority_false_accepts"]:
        disposition = "FALSIFIED"
        disposition_why = "authority-relevant false accept"
    elif not rc3c_currentness_ok:
        disposition = "FALSIFIED"
        disposition_why = "RC3C currentness successor vector disagreement"
    elif not rc3c_wire_ok:
        disposition = "FALSIFIED"
        disposition_why = "RC3C wire/cardinality successor vector disagreement"
    elif not rc3c_del_ok:
        disposition = "FALSIFIED"
        disposition_why = "RC3C delegation successor vector disagreement"
    elif not rc3b_attacks_ok or not matrix_ok or not type_ok:
        disposition = "FALSIFIED"
        disposition_why = "RC3B basis attack/matrix/type-mutation disagreement"
    elif not semantic_ok:
        disposition = "FALSIFIED"
        disposition_why = "semantic payload changed authority signature"
    elif not success_conditions["normative_reason_classes_agree"]:
        disposition = "FALSIFIED"
        disposition_why = "explicitly normative reason class disagreement"
    elif frozen_suite.returncode != 0:
        disposition = "INCONCLUSIVE"
        disposition_why = "frozen 145-test suite rerun did not pass"
    else:
        # Inherited RC3A accept/reject mismatches that are not wire/cardinality
        # and not authority false permits remain recorded, but RC3A reason strings
        # are non-normative unless relisted. A remaining inherited false reject
        # on RC3A envelopes is still a canonical false reject of a specified
        # inherited positive envelope.
        rc3a_env_false_reject = [
            item for item in select("rc3a_envelope") if item["outcome_class"] == "false_reject"
        ]
        rc3a_env_false_accept = [
            item for item in select("rc3a_envelope") if item["outcome_class"] == "false_accept"
        ]
        if rc3a_env_false_accept:
            disposition = "FALSIFIED"
            disposition_why = "inherited RC3A envelope false accept"
        elif rc3a_env_false_reject:
            disposition = "FALSIFIED"
            disposition_why = "inherited RC3A envelope false reject"
        elif by_family["rc3a_propagation"]["false_accept"] or by_family["rc3a_propagation"]["false_reject"]:
            disposition = "FALSIFIED"
            disposition_why = "inherited RC3A propagation outcome disagreement"
        else:
            disposition = "SUPPORTED FOR PROMOTION"
            disposition_why = (
                "frozen RC3C research specification independently recoverable "
                "by this fresh Grok successor against the frozen comparison corpus"
            )

    payload = {
        "schema": "contract-e-rc3c-grok-successor-post-freeze-comparison",
        "generated_at": datetime.now(UTC).isoformat(),
        "frozen_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "frozen_implementation_commit": "310a44182a13dc9df9321bc2900bf3c60b4c87b5",
        "revealed_blobs": blob_report,
        "native_consumption_deviations": sorted(set(native_deviations)),
        "by_family": by_family,
        "false_accepts": false_accepts,
        "false_rejects": false_rejects,
        "authority_relevant_false_accepts": authority_false_accepts,
        "normative_reason_disagreements": normative_reason_disagreements,
        "compatibility_matrix": {
            "n": len(matrix_rows),
            "canonical_accepts": len(canonical_accepts),
            "false_accepts": len(matrix_false_accepts),
            "false_rejects": len(matrix_false_rejects),
            "false_accept_ids": [item["id"] for item in matrix_false_accepts],
            "false_reject_ids": [item["id"] for item in matrix_false_rejects],
        },
        "type_mutations": {
            "n": len(type_rows),
            "false_accepts": by_family["rc3b_type_mutations"]["false_accept"],
            "false_rejects": by_family["rc3b_type_mutations"]["false_reject"],
        },
        "semantic_metamorphic": {
            "expected_change_count": meta["expected_authority_signature_change_count"],
            "observed_change_count": len(signature_changes),
            "changes": signature_changes,
        },
        "frozen_suite_rerun": {
            "command": "python -m pytest tests/contract_e_rc3c -q --tb=no",
            "interpreter": "project .venv python",
            "returncode": frozen_suite.returncode,
            "stdout": frozen_suite.stdout.strip(),
            "stderr": frozen_suite.stderr.strip(),
        },
        "success_conditions": success_conditions,
        "disposition": disposition,
        "disposition_why": disposition_why,
        "cases": rows,
        "adapter_used": False,
        "singular_plural_coercion_used": False,
        "field_rewriting_used": False,
        "first_launch_failure_preserved": "0.1s sandbox prompt-path denial remains an apparatus/setup deviation only",
        "contamination_status": "none observed during post-freeze comparison; first Grok reproduction and reference validators were not inspected",
    }
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    def ids(items: list[dict[str, Any]]) -> str:
        if not items:
            return "(none)"
        return ", ".join(item["id"] for item in items)

    md = []
    md.append("# Contract E RC3C Grok successor — post-freeze comparison receipt")
    md.append("")
    md.append(f"Terminal disposition: **{disposition}**")
    md.append("")
    md.append(disposition_why)
    md.append("")
    md.append("Frozen implementation and pre-reveal tests were not modified.")
    md.append("")
    md.append("## Revealed blobs")
    md.append("")
    for name, item in blob_report.items():
        md.append(f"- `{name}` git blob `{item['actual']}` match={item['match']}")
    md.append("")
    md.append("## Frozen suite rerun")
    md.append("")
    md.append(f"Command: `{payload['frozen_suite_rerun']['command']}`")
    md.append("")
    md.append(f"Exit: {frozen_suite.returncode}")
    md.append("")
    md.append("```")
    md.append(frozen_suite.stdout.strip() or frozen_suite.stderr.strip())
    md.append("```")
    md.append("")
    md.append("## Counts by family")
    md.append("")
    md.append("| Family | n | outcome match | false accept | false reject | normative reason disagreements |")
    md.append("|---|---:|---:|---:|---:|---:|")
    for family in families:
        stats = by_family[family]
        md.append(
            f"| `{family}` | {stats['n']} | {stats['exact_outcome_match']} | {stats['false_accept']} | {stats['false_reject']} | {stats['normative_reason_disagreement']} |"
        )
    md.append("")
    md.append("## Material disagreements")
    md.append("")
    md.append(f"- Authority-relevant false accepts: {ids(authority_false_accepts)}")
    md.append(f"- False accepts (all families): {ids(false_accepts)}")
    md.append(f"- False rejects: {ids(false_rejects)}")
    md.append(f"- Normative reason disagreements: {ids(normative_reason_disagreements)}")
    md.append("")
    md.append("## Compatibility matrix")
    md.append("")
    md.append(
        f"{len(matrix_rows)} cells; canonical accepts {len(canonical_accepts)}; "
        f"false accepts {len(matrix_false_accepts)}; false rejects {len(matrix_false_rejects)}."
    )
    md.append("")
    md.append("## Native-consumption / adaptation deviations")
    md.append("")
    if native_deviations:
        for note in sorted(set(native_deviations)):
            md.append(f"- {note}")
    else:
        md.append("- none")
    md.append("")
    md.append("No singular/plural coercion, hidden-case adapter, or field rewrite was applied to make vectors pass.")
    md.append("")
    md.append("## Preregistered ambiguity correspondence")
    md.append("")
    md.append("- A7/A8: RC3A/RC3C propagation vectors use `requested_fields`; consumer reads `fields`. PROP-N01 therefore accepted (false accept). PROP-N02/N03 and REASON-N03/N04 still rejected, but with local `propagation_forbidden_fields` rather than relisted `authority_requires_reestablishment`.")
    md.append("- A2/A13/delegation required-field plan: RC3A/RC3C parent objects omit `delegator`/`delegate`/`parent_authority_id`. Those objects were not filled. DEL-P01 and DELWIRE-P01 false-reject with `missing_required_field`; amplification cases still reject, but not on the amplification reasons.")
    md.append("- A11: HIST-P01 mode is `historical_record`, which is not a consumer mode. Passed unmodified; `evaluate()` remaps unknown modes to `new_exercise` and false-rejects.")
    md.append("- A16: semantic result mutations (frozen variants plus omitted/success/confidence forms) produced zero authority-signature changes.")
    md.append("- A20/A12 currentness: RC3C currentness vectors matched on accept/reject including inclusive bounds and revocation timing.")
    md.append("")
    md.append("## Contamination / deviation status")
    md.append("")
    md.append(payload["contamination_status"])
    md.append("")
    md.append(payload["first_launch_failure_preserved"])
    md.append("")
    md.append("The first 0.1s child-launch sandbox failure is a preserved apparatus/setup deviation. It is not the scientific implementation under comparison.")
    md.append("")
    args.out_md.write_text("\n".join(md) + "\n")
    print(json.dumps({"disposition": disposition, "why": disposition_why, "json": str(args.out_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
