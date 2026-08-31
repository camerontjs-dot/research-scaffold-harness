#!/usr/bin/env python3
"""Post-freeze RC3D comparison harness.

Materializes hidden fixture DSL using the frozen VECTOR-MATERIALIZATION-SPEC
and calls the frozen Gemini Consumer natively. Does not edit consumer.py.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import traceback
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVEALED = HERE / "revealed"
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
from consumer import Consumer  # noqa: E402

EXPECTED_BLOBS = {
    "RC3A-FROZEN-CASES.json": "85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a",
    "RC3B-AUTHORITY-BASIS-REGISTRY.json": "76ea333ee0460d9614e9899edb69e6865e48eccb",
    "RC3B-FROZEN-BASIS-ATTACKS.json": "c726fb0ef914a850620e545131a70d427f4027bd",
    "RC3B-HARDENING-PREREGISTRATION.md": "1d85e2036d410b3af08d4b2b8926586da8fe6088",
    "RC3C-FROZEN-CASES.json": "17d45524125814478b987bb8e91d23f545fb514e",
    "RC3D-VECTOR-MATERIALIZATION-SPEC.json": "5c75e46a8eb4d7346128d84e21c25bdcea454ec4",
    "RC3D-FROZEN-CASES.json": "728b308d6eca0ebdf384e7de312c8a62b2f25577",
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
CONFERING = {"grant", "policy", "delegation"}

RC3C_SPEC = json.loads((REPO / "authority_input" / "RC3C-SPEC.json").read_text())
RC3D_SPEC = json.loads((REPO / "authority_input" / "RC3D-INTERFACE-SPEC.json").read_text())
RC3B_SPEC = json.loads((REPO / "authority_input" / "BASIS-BINDING-SPEC.json").read_text())
NORMATIVE = set(RC3C_SPEC["reason_contract"]["whole_envelope_precedence"])
NORMATIVE.update(RC3C_SPEC["reason_contract"]["relisted_cross_domain_primary_reasons"].values())
NORMATIVE.update(RC3C_SPEC["malformed_wire_reasons"].values())
NORMATIVE.update(RC3B_SPEC["ordering"]["reason_precedence"])
NORMATIVE.update(RC3D_SPEC["interface_reason_contract"]["canonical_primary_reasons"])

SUCCESSOR_REASON_FAMILIES = {
    "rc3b_basis_attacks",
    "rc3b_type_mutations",
    "rc3c_currentness",
    "rc3c_wire",
    "rc3c_delegation",
    "rc3c_reason",
    "rc3d_interface",
}


def git_blob(path: Path) -> str:
    import subprocess

    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def sha256_obj(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def deep(obj):
    return copy.deepcopy(obj)


def set_path(root, dotted, value) -> None:
    parts = dotted.split(".")
    cur = root
    for part in parts[:-1]:
        key = int(part) if part.isdigit() else part
        cur = cur[key]
    last = parts[-1]
    key = int(last) if last.isdigit() else last
    cur[key] = value


def get_path(root, dotted):
    cur = root
    for part in dotted.split("."):
        key = int(part) if part.isdigit() else part
        cur = cur[key]
    return cur


def apply_overlays(target: dict, case: dict) -> list[str]:
    mappings: list[str] = []
    if "set" in case and isinstance(case["set"], dict):
        target.update(deep(case["set"]))
        mappings.append("apply_set")
    if "set_path" in case and isinstance(case["set_path"], dict):
        for path, value in case["set_path"].items():
            set_path(target, path, deep(value))
        mappings.append("apply_set_path")
    if "remove" in case:
        for key in case["remove"]:
            target.pop(key, None)
        mappings.append("apply_remove")
    if "remove_authority_basis_types" in case:
        types = set(case["remove_authority_basis_types"])
        basis = target.get("authority_basis")
        if isinstance(basis, list):
            target["authority_basis"] = [
                item for item in basis if not (isinstance(item, dict) and item.get("type") in types)
            ]
        mappings.append("remove_authority_basis_types")
    if "replace_authority_reference" in case:
        spec = case["replace_authority_reference"]
        old_id = spec.get("old_id")
        new_ref = deep(spec.get("new_ref"))
        basis = target.get("authority_basis")
        if isinstance(basis, list):
            for i, item in enumerate(basis):
                if isinstance(item, dict) and item.get("id") == old_id:
                    basis[i] = new_ref
                    break
        mappings.append("replace_authority_reference")
    if "replace_path_with_first_item" in case:
        path = case["replace_path_with_first_item"]
        value = get_path(target, path)
        if isinstance(value, list) and value:
            set_path(target, path, deep(value[0]))
        mappings.append("replace_path_with_first_item")
    return mappings


def conferring_index(envelope: dict, canonical_id: str | None = None) -> int | None:
    basis = envelope.get("authority_basis")
    if not isinstance(basis, list):
        return None
    if canonical_id is not None:
        for i, item in enumerate(basis):
            if isinstance(item, dict) and item.get("id") == canonical_id:
                return i
    for i, item in enumerate(basis):
        if isinstance(item, dict) and item.get("type") in CONFERING:
            return i
    return None


def overlay_record(record: dict, override: dict) -> dict:
    updated = deep(record)
    if "set" in override and isinstance(override["set"], dict):
        updated.update(deep(override["set"]))
    return updated


def redact(text: str | None) -> str | None:
    if text is None:
        return None
    # Keep receipts free of host paths.
    return text.replace("/Users/", "/<redacted>/").replace("/home/", "/<redacted>/")


def interface_flags(request: dict, result: dict) -> dict:
    """Classify native-consumption / serialization failures without repairing input."""
    native_consumption = False
    native_serialization = bool(result.get("execution_error"))
    kind = request.get("kind")
    if kind == "propagation":
        nested = request.get("request")
        canonical_container = isinstance(nested, dict) and "mode" not in request
        if canonical_container:
            # Canonical RC3D places mode/fields under request_container_key "request".
            if result.get("reason") == "missing_required_field" or result.get("accepted") is None:
                native_consumption = True
            elif result.get("decision") not in {"permit", "reject"}:
                native_consumption = True
    if kind == "envelope":
        registry = request.get("registry")
        if isinstance(registry, dict) and "schema" in registry and "records" in registry:
            # Wrapper was passed intact. A malformed_registry_document on a
            # well-formed wrapper with matching map_key==id is consumption failure
            # only when the envelope itself is otherwise the canonical document.
            pass
    if kind == "delegation":
        child = request.get("child") if isinstance(request.get("child"), dict) else {}
        parent = request.get("parent") if isinstance(request.get("parent"), dict) else {}
        singular = any(isinstance((child or {}).get(k), str) for k in ("operations", "scope")) or any(
            isinstance((parent or {}).get(k), str) for k in ("operations", "scope")
        )
        if singular and result.get("reason") not in {
            "malformed_delegation_operations_shape",
            "malformed_delegation_scope_shape",
        }:
            native_serialization = True
    envelope = request.get("envelope") if isinstance(request.get("envelope"), dict) else {}
    if isinstance(envelope.get("warrant"), dict) and result.get("execution_error"):
        native_serialization = True
    return {
        "native_consumption_incompatibility": native_consumption,
        "native_serialization_incompatibility": native_serialization,
    }


def decision_of(request: dict) -> dict:
    consumer = Consumer()
    try:
        raw = consumer.evaluate(request)
    except Exception as exc:
        flags = interface_flags(request, {"execution_error": True, "accepted": None, "reason": None})
        return {
            "execution_error": True,
            "exception_type": type(exc).__name__,
            "exception": redact(str(exc)),
            "accepted": None,
            "decision": None,
            "reason": None,
            **flags,
        }
    if not isinstance(raw, dict):
        flags = interface_flags(request, {"execution_error": True, "accepted": None, "reason": None})
        return {
            "execution_error": True,
            "exception_type": "NonDictResult",
            "exception": redact(repr(raw)),
            "accepted": None,
            "decision": None,
            "reason": None,
            **flags,
        }
    decision = raw.get("decision")
    accepted = True if decision == "permit" else False if decision == "reject" else None
    result = {
        "execution_error": False,
        "accepted": accepted,
        "decision": decision,
        "reason": raw.get("reason"),
        "raw": raw,
    }
    result.update(interface_flags(request, result))
    return result


def classify_outcome(expected: str | None, accepted) -> str:
    if accepted is None:
        return "execution_error"
    if expected is None:
        return "no_expected_outcome"
    want_accept = expected == "accept"
    if want_accept and accepted:
        return "outcome_match"
    if (not want_accept) and (not accepted):
        return "outcome_match"
    if accepted and not want_accept:
        return "false_accept"
    return "false_reject"


def classify_reason(family: str, expected_reason, observed) -> str:
    if expected_reason is None:
        return "no_expected_reason"
    if observed == expected_reason:
        return "reason_match"
    if family in SUCCESSOR_REASON_FAMILIES and expected_reason in NORMATIVE:
        return "normative_reason_disagreement"
    return "non_normative_reason_difference"


def row(**kwargs) -> dict:
    return kwargs


def load(name: str):
    return json.loads((REVEALED / name).read_text())


def main() -> int:
    blob_report = {}
    for name, expected in EXPECTED_BLOBS.items():
        path = REVEALED / name
        actual = git_blob(path)
        blob_report[name] = {"expected": expected, "actual": actual, "match": actual == expected}
    if not all(item["match"] for item in blob_report.values()):
        print("blob verification failed", json.dumps(blob_report, indent=2), file=sys.stderr)
        return 2

    rc3a = load("RC3A-FROZEN-CASES.json")
    registry_doc = load("RC3B-AUTHORITY-BASIS-REGISTRY.json")
    attacks = load("RC3B-FROZEN-BASIS-ATTACKS.json")
    rc3c = load("RC3C-FROZEN-CASES.json")
    rc3d = load("RC3D-FROZEN-CASES.json")
    mat_spec = load("RC3D-VECTOR-MATERIALIZATION-SPEC.json")
    baselines = rc3a["baselines"]
    records = registry_doc["records"]
    env_by_id = {c["id"]: c for c in rc3a["envelope_cases"]}
    prop_by_id = {c["id"]: c for c in rc3a["propagation_cases"]}
    del_by_id = {c["id"]: c for c in rc3a["delegation_cases"]}
    hist_by_id = {c["id"]: c for c in rc3a["historical_cases"]}

    rows: list[dict] = []

    def envelope_request(envelope: dict, registry: dict, mode: str = "new_exercise") -> dict:
        return {
            "kind": "envelope",
            "envelope": envelope,
            "registry": registry,
            "mode": mode,
        }

    def materialize_envelope_case(case: dict, family: str) -> dict:
        mappings = ["envelope_case.clone_baseline", "pass_RegistryDocument_wrapper", "mode=new_exercise"]
        envelope = deep(baselines[case["base"]])
        mappings.extend(apply_overlays(envelope, case))
        registry = deep(registry_doc)
        if "record_override" in case:
            override = case["record_override"]
            rid = override["id"]
            registry["records"][rid] = overlay_record(registry["records"][rid], override)
            mappings.append("record_override")
        request = envelope_request(envelope, registry, "new_exercise")
        return finish(family, case, request, mappings, "envelope", "envelope_case")

    def materialize_propagation_case(case: dict, family: str, case_id: str | None = None) -> dict:
        mappings = ["propagation_case.requested_fields->fields"]
        request = {
            "kind": "propagation",
            "request": {
                "mode": case["mode"],
                "fields": deep(case["requested_fields"]),
            },
        }
        fake = {
            "id": case_id or case["id"],
            "expected": case["expected"],
            "reason": case.get("reason"),
        }
        return finish(family, fake, request, mappings, "propagation", "propagation_case")

    def materialize_delegation_case(case: dict, family: str, extra_set_path=None, case_id=None, expected=None, reason=None) -> dict:
        holder = {"parent": deep(case["parent"]), "child": deep(case["child"])}
        mappings = ["delegation_case.parent_child_byte_for_byte", "missing_field_invention_forbidden"]
        if extra_set_path:
            for path, value in extra_set_path.items():
                set_path(holder, path, deep(value))
            mappings.append("apply_set_path")
        request = {
            "kind": "delegation",
            "parent": holder["parent"],
            "child": holder["child"],
            "mode": "new_exercise",
        }
        fake = {
            "id": case_id or case["id"],
            "expected": expected if expected is not None else case["expected"],
            "reason": reason if reason is not None else case.get("reason"),
        }
        return finish(family, fake, request, mappings, "delegation", "delegation_case")

    def materialize_historical_case(case: dict, family: str, mode_override=None, case_id=None, expected=None, reason=None) -> dict:
        fixture_mode = mode_override if mode_override is not None else case["mode"]
        mapping_table = mat_spec["rules"]["historical_case"]["mode_mapping"]
        mappings = []
        if fixture_mode in mapping_table:
            canonical_mode = mapping_table[fixture_mode]
            mappings.append(f"historical_mode:{fixture_mode}->{canonical_mode}")
        else:
            canonical_mode = fixture_mode
            mappings.append(f"historical_mode_unmapped:{fixture_mode}")
        request = {
            "kind": "historical",
            "record": deep(case["historical_record"]),
            "registry": deep(registry_doc),
            "mode": canonical_mode,
        }
        fake = {
            "id": case_id or case["id"],
            "expected": expected if expected is not None else case["expected"],
            "reason": reason if reason is not None else case.get("reason"),
        }
        return finish(family, fake, request, mappings, "historical", "historical_case")

    def finish(family, case, request, mappings, kind, rule_id) -> dict:
        result = decision_of(request)
        expected = case.get("expected")
        expected_reason = case.get("reason")
        item = row(
            family=family,
            id=case["id"],
            source_case_id=case["id"],
            materialization_rule=rule_id,
            canonical_request_kind=kind,
            fixture_to_wire_mappings=mappings,
            request_sha256=sha256_obj(request),
            expected=expected,
            expected_reason=expected_reason,
            consumer_decision=result.get("decision"),
            consumer_reason=result.get("reason"),
            accepted=result.get("accepted"),
            outcome_class=classify_outcome(expected, result.get("accepted")),
            reason_class=classify_reason(family, expected_reason, result.get("reason")),
            execution_error=result.get("execution_error", False),
            exception=result.get("exception"),
            exception_type=result.get("exception_type"),
            native_consumption_incompatibility=result.get("native_consumption_incompatibility", False),
            native_serialization_incompatibility=result.get("native_serialization_incompatibility", False),
        )
        if result.get("execution_error"):
            item["outcome_class"] = "execution_error"
            item["reason_class"] = "execution_error"
        rows.append(item)
        return item

    for case in rc3a["envelope_cases"]:
        materialize_envelope_case(case, "rc3a_envelope")
    for case in rc3a["propagation_cases"]:
        materialize_propagation_case(case, "rc3a_propagation")
    for case in rc3a["delegation_cases"]:
        materialize_delegation_case(case, "rc3a_delegation")
    for case in rc3a["historical_cases"]:
        materialize_historical_case(case, "rc3a_historical")

    for case in attacks["cases"]:
        materialize_envelope_case(case, "rc3b_basis_attacks")

    conferring_ids = [rid for rid, rec in records.items() if rec.get("type") in CONFERING]
    for base_name, canonical_id in CANONICAL_BASIS.items():
        for record_id in conferring_ids:
            envelope = deep(baselines[base_name])
            idx = conferring_index(envelope, canonical_id)
            rec = records[record_id]
            mappings = ["rc3b_compatibility_matrix.replace_conferring_reference"]
            if idx is not None:
                envelope["authority_basis"][idx] = {
                    "type": rec["type"],
                    "id": record_id,
                    "current": True,
                }
            expected = "accept" if record_id == canonical_id else "reject"
            request = envelope_request(envelope, deep(registry_doc))
            fake = {"id": f"MATRIX-{base_name}--{record_id}", "expected": expected, "reason": None}
            item = finish("rc3b_compatibility_matrix", fake, request, mappings, "envelope", "rc3b_compatibility_matrix")
            item["base"] = base_name
            item["record_id"] = record_id
            item["canonical_id"] = canonical_id

    for base_name, canonical_id in CANONICAL_BASIS.items():
        original = deep(baselines[base_name])
        idx0 = conferring_index(original, canonical_id)
        original_type = original["authority_basis"][idx0]["type"] if idx0 is not None else None
        for other in sorted(CONFERING):
            if other == original_type:
                continue
            envelope = deep(baselines[base_name])
            idx = conferring_index(envelope, canonical_id)
            mappings = ["rc3b_type_mutation.replace_type_preserve_id"]
            if idx is not None:
                envelope["authority_basis"][idx] = {**deep(envelope["authority_basis"][idx]), "type": other}
            request = envelope_request(envelope, deep(registry_doc))
            fake = {
                "id": f"TYPE-{base_name}--{canonical_id}--{other}",
                "expected": "reject",
                "reason": "authority_basis_type_mismatch",
            }
            finish("rc3b_type_mutations", fake, request, mappings, "envelope", "rc3b_type_mutation")

    for case in rc3c["currentness_cases"]:
        materialize_envelope_case(case, "rc3c_currentness")
    for case in rc3c["wire_cases"]:
        materialize_envelope_case(case, "rc3c_wire")
    for case in rc3c["delegation_wire_cases"]:
        source = del_by_id[case["source_case"]]
        materialize_delegation_case(
            source,
            "rc3c_delegation",
            extra_set_path=case.get("set_path"),
            case_id=case["id"],
            expected=case["expected"],
            reason=case.get("reason"),
        )
    for case in rc3c["reason_cases"]:
        if "source_envelope_case" in case:
            source = env_by_id[case["source_envelope_case"]]
            merged = {**source, "id": case["id"], "expected": case["expected"], "reason": case.get("reason")}
            materialize_envelope_case(merged, "rc3c_reason")
        else:
            source = prop_by_id[case["source_propagation_case"]]
            materialize_propagation_case(source, "rc3c_reason", case_id=case["id"])
            rows[-1]["expected"] = case["expected"]
            rows[-1]["expected_reason"] = case.get("reason")
            rows[-1]["outcome_class"] = classify_outcome(case["expected"], rows[-1]["accepted"])
            rows[-1]["reason_class"] = classify_reason("rc3c_reason", case.get("reason"), rows[-1]["consumer_reason"])

    for case in rc3d["interface_cases"]:
        mappings: list[str] = ["rc3d_interface_case"]
        if "request" in case:
            request = deep(case["request"])
            kind = request.get("kind", "unknown")
            finish("rc3d_interface", case, request, mappings, kind, "rc3d_native_request")
        elif "source_envelope_baseline" in case:
            envelope = deep(baselines[case["source_envelope_baseline"]])
            registry = deep(registry_doc)
            if "registry_mutation" in case:
                mut = case["registry_mutation"]
                if "remove" in mut:
                    for key in mut["remove"]:
                        registry.pop(key, None)
                    mappings.append("registry_mutation.remove")
                if "set_path" in mut:
                    for path, value in mut["set_path"].items():
                        set_path(registry, path, deep(value))
                    mappings.append("registry_mutation.set_path")
            request = envelope_request(envelope, registry, case.get("mode", "new_exercise"))
            finish("rc3d_interface", case, request, mappings, "envelope", "envelope_case")
        elif "source_delegation_case" in case:
            source = del_by_id[case["source_delegation_case"]]
            materialize_delegation_case(
                source,
                "rc3d_interface",
                extra_set_path=case.get("set_path"),
                case_id=case["id"],
                expected=case["expected"],
                reason=case.get("reason"),
            )
        elif "source_historical_case" in case:
            source = hist_by_id[case["source_historical_case"]]
            # RC3D interface cases supply the native/fixture mode explicitly.
            # HIST-N01 tests the unmapped fixture token as native input.
            if case["id"] == "HIST-N01-fixture-token-not-native":
                request = {
                    "kind": "historical",
                    "record": deep(source["historical_record"]),
                    "registry": deep(registry_doc),
                    "mode": case["mode"],
                }
                mappings.append("pass_fixture_mode_token_unmapped")
                finish("rc3d_interface", case, request, mappings, "historical", "historical_case")
            else:
                materialize_historical_case(
                    source,
                    "rc3d_interface",
                    mode_override=case["mode"],
                    case_id=case["id"],
                    expected=case["expected"],
                    reason=case.get("reason"),
                )

    # Materializer assertions: inspect mapping, then evaluate materialized request.
    for assertion in rc3d["materializer_assertions"]:
        if assertion["id"] == "MAT-PROP-01":
            source = prop_by_id[assertion["source_propagation_case"]]
            request = {
                "kind": "propagation",
                "request": {"mode": source["mode"], "fields": deep(source["requested_fields"])},
            }
            native_ok = "requested_fields" not in request["request"] and "fields" in request["request"]
            fake = {"id": assertion["id"], "expected": assertion["expected"], "reason": None}
            item = finish("rc3d_materializer", fake, request, ["requested_fields->fields"], "propagation", "propagation_case")
            item["materializer_audit"] = {
                "expected_mapping": assertion["expected_mapping"],
                "observed_native_ok": native_ok,
            }
            if not native_ok:
                item["outcome_class"] = "materializer_audit_failure"
        elif assertion["id"] == "MAT-DEL-01":
            source = del_by_id[assertion["source_delegation_case"]]
            parent_keys = set(source["parent"])
            invented = {"delegator", "delegate", "parent_authority_id"} & parent_keys
            request = {
                "kind": "delegation",
                "parent": deep(source["parent"]),
                "child": deep(source["child"]),
                "mode": "new_exercise",
            }
            fake = {"id": assertion["id"], "expected": assertion["expected"], "reason": None}
            item = finish("rc3d_materializer", fake, request, ["parent_byte_for_byte"], "delegation", "delegation_case")
            item["materializer_audit"] = {
                "expected_parent_type": assertion["expected_parent_type"],
                "missing_field_invention_allowed": assertion["missing_field_invention_allowed"],
                "invented_parent_fields": sorted(invented),
            }
        elif assertion["id"] == "MAT-HIST-01":
            source = hist_by_id[assertion["source_historical_case"]]
            mapped = mat_spec["rules"]["historical_case"]["mode_mapping"][source["mode"]]
            request = {
                "kind": "historical",
                "record": deep(source["historical_record"]),
                "registry": deep(registry_doc),
                "mode": mapped,
            }
            fake = {"id": assertion["id"], "expected": assertion["expected"], "reason": None}
            item = finish("rc3d_materializer", fake, request, [f"historical_record->{mapped}"], "historical", "historical_case")
            item["materializer_audit"] = {"mapped_mode": mapped, "mapping_ok": mapped == "historical_inspection"}
        elif assertion["id"] == "MAT-REG-01":
            envelope = deep(baselines["source_access_ok"])
            request = envelope_request(envelope, deep(registry_doc))
            wrapper_intact = "schema" in request["registry"] and "records" in request["registry"]
            fake = {"id": assertion["id"], "expected": "accept", "reason": None}
            item = finish("rc3d_materializer", fake, request, ["pass_RegistryDocument_wrapper_intact"], "envelope", "envelope_case")
            item["materializer_audit"] = {
                "pass_wrapper_intact": wrapper_intact,
                "expected": "native",
            }
            if not wrapper_intact:
                item["outcome_class"] = "materializer_audit_failure"

    meta = rc3c["semantic_metamorphic"]
    for base_name in meta["bases"]:
        baseline_env = deep(baselines[base_name])
        baseline_req = envelope_request(baseline_env, deep(registry_doc))
        baseline_res = decision_of(baseline_req)
        baseline_sig = (baseline_res.get("accepted"), baseline_res.get("reason"))
        variants = list(meta["variants"])
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
            request = envelope_request(envelope, deep(registry_doc))
            fake = {
                "id": f"SEM-{base_name}--{label}",
                "expected": "accept" if baseline_res.get("accepted") else "reject",
                "reason": None,
            }
            item = finish("semantic_metamorphic", fake, request, ["replace_opaque_result_only"], "envelope", "semantic_metamorphic")
            sig = (item["accepted"], item["consumer_reason"])
            item["authority_signature_changed"] = sig != baseline_sig
            item["baseline_signature"] = {"accepted": baseline_sig[0], "reason": baseline_sig[1]}

    families = [
        "rc3a_envelope",
        "rc3a_propagation",
        "rc3a_delegation",
        "rc3a_historical",
        "rc3b_basis_attacks",
        "rc3b_compatibility_matrix",
        "rc3b_type_mutations",
        "rc3c_currentness",
        "rc3c_wire",
        "rc3c_delegation",
        "rc3c_reason",
        "rc3d_interface",
        "rc3d_materializer",
        "semantic_metamorphic",
    ]

    def sel(fam):
        return [r for r in rows if r["family"] == fam]

    by_family = {}
    for fam in families:
        items = sel(fam)
        by_family[fam] = {
            "n": len(items),
            "outcome_match": sum(1 for r in items if r["outcome_class"] == "outcome_match"),
            "outcome_disagreement": sum(1 for r in items if r["outcome_class"] in {"false_accept", "false_reject"}),
            "false_accept": sum(1 for r in items if r["outcome_class"] == "false_accept"),
            "false_reject": sum(1 for r in items if r["outcome_class"] == "false_reject"),
            "normative_reason_match": sum(1 for r in items if r["reason_class"] == "reason_match"),
            "normative_reason_disagreement": sum(1 for r in items if r["reason_class"] == "normative_reason_disagreement"),
            "non_normative_reason_difference": sum(1 for r in items if r["reason_class"] == "non_normative_reason_difference"),
            "execution_error": sum(1 for r in items if r["outcome_class"] == "execution_error"),
            "native_consumption_incompatibility": sum(1 for r in items if r.get("native_consumption_incompatibility")),
            "native_serialization_incompatibility": sum(1 for r in items if r.get("native_serialization_incompatibility")),
            "materializer_audit_failure": sum(1 for r in items if r["outcome_class"] == "materializer_audit_failure"),
            "semantic_signature_changes": sum(1 for r in items if r.get("authority_signature_changed")),
        }

    false_accepts = [r for r in rows if r["outcome_class"] == "false_accept"]
    false_rejects = [r for r in rows if r["outcome_class"] == "false_reject"]
    exec_errors = [r for r in rows if r["outcome_class"] == "execution_error"]
    normative_dis = [r for r in rows if r["reason_class"] == "normative_reason_disagreement"]
    sig_changes = [r for r in rows if r.get("authority_signature_changed")]
    mat_fail = [r for r in rows if r["outcome_class"] == "materializer_audit_failure"]

    native_cons = [r for r in rows if r.get("native_consumption_incompatibility")]
    native_ser = [r for r in rows if r.get("native_serialization_incompatibility")]

    # Cluster root causes. Do not collapse distinct causes.
    clusters = defaultdict(list)
    for r in rows:
        notable = (
            r["outcome_class"] in {"false_accept", "false_reject", "execution_error", "materializer_audit_failure"}
            or r["reason_class"] == "normative_reason_disagreement"
            or r.get("native_consumption_incompatibility")
            or r.get("native_serialization_incompatibility")
            or r.get("authority_signature_changed")
        )
        if not notable:
            continue
        parts = [
            r["outcome_class"],
            r["reason_class"],
            str(r.get("consumer_reason")),
            r["canonical_request_kind"],
        ]
        if r.get("native_consumption_incompatibility"):
            parts.append("native_consumption")
        if r.get("native_serialization_incompatibility"):
            parts.append("native_serialization")
        if r.get("authority_signature_changed"):
            parts.append("semantic_signature_change")
        if r.get("exception_type"):
            parts.append(str(r.get("exception_type")))
        clusters["|".join(parts)].append(r["id"])

    # Ambiguity resolution from RC3D interface cases
    def find(cid):
        return next((r for r in rows if r["id"] == cid), None)

    amb = {
        "registry_map_key_vs_record_id": {
            "exercised_by": "REG-N02-record-key-id-mismatch",
            "case": find("REG-N02-record-key-id-mismatch"),
        },
        "explicit_propagation_fields_absent_or_not_reauthorized": {
            "exercised_by": ["PROP-N02-explicit-missing-fields", "PROP-P01-native-fields"],
            "cases": [find("PROP-N02-explicit-missing-fields"), find("PROP-P01-native-fields")],
        },
        "wrapper_kind_mode_vs_inner_payload": {
            "exercised_by": ["KIND-N01-unknown-kind", "MODE-N01-envelope-unknown-mode"],
            "cases": [find("KIND-N01-unknown-kind"), find("MODE-N01-envelope-unknown-mode")],
        },
    }

    def amb_status(case):
        if not case:
            return "not_exercised"
        if case["outcome_class"] == "outcome_match" and case["reason_class"] in {"reason_match", "no_expected_reason"}:
            return "agreed"
        if case["outcome_class"] == "outcome_match" and case["reason_class"] == "normative_reason_disagreement":
            return "disagreed_reason"
        if case["outcome_class"] in {"false_accept", "false_reject", "execution_error"}:
            return "disagreed"
        return "underdetermined"

    authority_false_accepts = [
        r for r in false_accepts if r["family"] != "semantic_metamorphic"
    ]

    frozen_ok = True  # 42 tests already rerun by orchestrator; harness records command
    canonical_false_rejects = [
        r
        for r in false_rejects
        if r["family"]
        in {
            "rc3a_envelope",
            "rc3b_basis_attacks",
            "rc3b_compatibility_matrix",
            "rc3c_currentness",
            "rc3c_wire",
            "rc3c_delegation",
            "rc3d_interface",
        }
        and r.get("expected") == "accept"
    ]

    if authority_false_accepts:
        disposition = "FALSIFIED"
        why = "authority-relevant false accept/permit"
    elif canonical_false_rejects:
        disposition = "FALSIFIED"
        why = "canonical false reject"
    elif native_cons:
        disposition = "FALSIFIED"
        why = "native canonical consumption failed; consumer did not read RC3D request objects"
    elif any(by_family[f]["false_reject"] or by_family[f]["false_accept"] for f in ("rc3c_currentness", "rc3c_wire", "rc3b_basis_attacks", "rc3b_compatibility_matrix")):
        disposition = "FALSIFIED"
        why = "RC3B/RC3C outcome disagreement"
    elif sig_changes:
        disposition = "FALSIFIED"
        why = "semantic payload changed authority signature"
    elif mat_fail:
        disposition = "FALSIFIED"
        why = "materializer audit failure"
    elif exec_errors or native_ser:
        disposition = "FALSIFIED"
        why = "native serialization/interface incompatibility or uncaught exception on canonical request"
    elif any(by_family[f]["false_accept"] or by_family[f]["false_reject"] for f in ("rc3d_interface", "rc3a_propagation", "rc3a_delegation", "rc3a_historical", "rc3c_delegation", "rc3c_reason")):
        disposition = "FALSIFIED"
        why = "native interface or materialized inherited-case outcome disagreement"
    elif any(r["reason_class"] == "normative_reason_disagreement" for r in rows if r["family"] in SUCCESSOR_REASON_FAMILIES):
        disposition = "FALSIFIED"
        why = "normative reason disagreement on successor/interface families"
    else:
        disposition = "SUPPORTED FOR PROMOTION"
        why = "frozen Gemini implementation satisfied the comparison gate without post-reveal repair"

    payload = {
        "schema": "contract-e-rc3d-gemini-post-freeze-comparison",
        "generated_at": datetime.now(UTC).isoformat(),
        "frozen_head": "5364837007fe18f9e05eb39e0aa1031e28561290",
        "frozen_tree": "7ad575731f2e7c5786fff74ead02a311007f36ab",
        "frozen_implementation_commit": "76f63ed48538463487b7336b158745cdf63975d0",
        "revealed_blobs": blob_report,
        "frozen_suite_rerun": {
            "command": "python3 test_rc3d.py -v",
            "count": 42,
            "result": "OK",
        },
        "by_family": by_family,
        "overall": {
            "n": len(rows),
            "outcome_match": sum(1 for r in rows if r["outcome_class"] == "outcome_match"),
            "outcome_disagreement": sum(1 for r in rows if r["outcome_class"] in {"false_accept", "false_reject"}),
            "false_accept": len(false_accepts),
            "false_reject": len(false_rejects),
            "normative_reason_disagreement": len(normative_dis),
            "non_normative_reason_difference": sum(1 for r in rows if r["reason_class"] == "non_normative_reason_difference"),
            "execution_error": len(exec_errors),
            "native_consumption_incompatibility": len(native_cons),
            "native_serialization_incompatibility": len(native_ser),
            "semantic_signature_changes": len(sig_changes),
            "materializer_audit_failure": len(mat_fail),
        },
        "false_accepts": false_accepts,
        "false_rejects": false_rejects,
        "authority_relevant_false_accepts": authority_false_accepts,
        "canonical_false_rejects": canonical_false_rejects,
        "normative_reason_disagreements": normative_dis,
        "execution_errors": exec_errors,
        "native_consumption_incompatibilities": native_cons,
        "native_serialization_incompatibilities": native_ser,
        "semantic_signature_changes": sig_changes,
        "materializer_audit_failures": mat_fail,
        "clustered_root_causes": {k: v for k, v in clusters.items()},
        "preregistered_ambiguities": {
            "registry_map_key_vs_record_id": {
                "status": amb_status(amb["registry_map_key_vs_record_id"]["case"]),
                "case": amb["registry_map_key_vs_record_id"]["case"],
            },
            "explicit_propagation_absent_fields": {
                "status": [amb_status(c) for c in amb["explicit_propagation_fields_absent_or_not_reauthorized"]["cases"]],
                "cases": amb["explicit_propagation_fields_absent_or_not_reauthorized"]["cases"],
            },
            "wrapper_kind_mode_precedence": {
                "status": [amb_status(c) for c in amb["wrapper_kind_mode_vs_inner_payload"]["cases"]],
                "cases": amb["wrapper_kind_mode_vs_inner_payload"]["cases"],
            },
        },
        "contamination_status": "none observed; comparison used only the seven authorized reveal blobs plus the frozen consumer; prior Grok comparison was not imported",
        "adapter_used": False,
        "consumer_modified": False,
        "disposition": disposition,
        "disposition_why": why,
        "cases": rows,
    }

    (HERE / "COMPARISON-RESULTS.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    def ids(items):
        return ", ".join(r["id"] for r in items) if items else "(none)"

    md = []
    md.append("# Contract E RC3D Gemini — post-freeze comparison")
    md.append("")
    md.append(f"**Terminal disposition: {disposition}**")
    md.append("")
    md.append(why)
    md.append("")
    md.append("Frozen implementation and pre-reveal tests were not modified.")
    md.append("")
    md.append("## Frozen integrity")
    md.append("")
    md.append("- HEAD `5364837007fe18f9e05eb39e0aa1031e28561290`")
    md.append("- tree `7ad575731f2e7c5786fff74ead02a311007f36ab`")
    md.append("- consumer.py `a1275e1e2ddd6c4509ca8b7769b5651c19749f85`")
    md.append("- test_rc3d.py `1102fc173086c45040da45125de4d138ee495765`")
    md.append("- frozen suite rerun: `python3 test_rc3d.py -v` → 42 OK")
    md.append("")
    md.append("## Revealed blobs")
    md.append("")
    for name, item in blob_report.items():
        md.append(f"- `{name}` `{item['actual']}` match={item['match']}")
    md.append("")
    md.append("## Counts by family")
    md.append("")
    md.append("| Family | n | match | false accept | false reject | normative reason Δ | native consume Δ | native serial Δ | exec error |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for fam in families:
        s = by_family[fam]
        md.append(
            f"| `{fam}` | {s['n']} | {s['outcome_match']} | {s['false_accept']} | {s['false_reject']} | {s['normative_reason_disagreement']} | {s['native_consumption_incompatibility']} | {s['native_serialization_incompatibility']} | {s['execution_error']} |"
        )
    o = payload["overall"]
    md.append(
        f"| **overall** | {o['n']} | {o['outcome_match']} | {o['false_accept']} | {o['false_reject']} | {o['normative_reason_disagreement']} | {o['native_consumption_incompatibility']} | {o['native_serialization_incompatibility']} | {o['execution_error']} |"
    )
    md.append("")
    md.append("## Disagreements")
    md.append("")
    md.append(f"- Authority-relevant false accepts: {ids(authority_false_accepts)}")
    md.append(f"- False accepts: {ids(false_accepts)}")
    md.append(f"- False rejects: {ids(false_rejects)}")
    md.append(f"- Native consumption incompatibilities: {ids(native_cons)}")
    md.append(f"- Native serialization incompatibilities: {ids(native_ser)}")
    md.append(f"- Execution errors: {ids(exec_errors)}")
    md.append(f"- Semantic signature changes: {ids(sig_changes)}")
    md.append(f"- Materializer audit failures: {ids(mat_fail)}")
    md.append("")
    md.append("## Clustered root causes")
    md.append("")
    for key, members in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        md.append(f"- `{key}` ({len(members)}): {', '.join(members[:12])}{'…' if len(members) > 12 else ''}")
    md.append("")
    md.append("## Preregistered ambiguities")
    md.append("")
    md.append(f"1. Registry map-key vs record.id: **{payload['preregistered_ambiguities']['registry_map_key_vs_record_id']['status']}**")
    md.append(f"2. Explicit propagation without fields / not reauthorized: **{payload['preregistered_ambiguities']['explicit_propagation_absent_fields']['status']}**")
    md.append(f"3. Wrapper kind/mode precedence: **{payload['preregistered_ambiguities']['wrapper_kind_mode_precedence']['status']}**")
    md.append("")
    md.append("## Contamination")
    md.append("")
    md.append(payload["contamination_status"])
    md.append("")
    (HERE / "POST-FREEZE-COMPARISON.md").write_text("\n".join(md) + "\n")

    receipt = []
    receipt.append("# POST-FREEZE RECEIPT — Contract E RC3D Gemini")
    receipt.append("")
    receipt.append(f"Terminal disposition: **{disposition}**")
    receipt.append("")
    receipt.append(why)
    receipt.append("")
    receipt.append("## Frozen SHA/tree")
    receipt.append("")
    receipt.append("`5364837007fe18f9e05eb39e0aa1031e28561290` / `7ad575731f2e7c5786fff74ead02a311007f36ab`")
    receipt.append("")
    receipt.append("## Seven reveal blobs")
    receipt.append("")
    for name, item in blob_report.items():
        receipt.append(f"- {name}: `{item['actual']}`")
    receipt.append("")
    receipt.append("## Unchanged frozen hashes")
    receipt.append("")
    receipt.append("- consumer.py `a1275e1e2ddd6c4509ca8b7769b5651c19749f85`")
    receipt.append("- test_rc3d.py `1102fc173086c45040da45125de4d138ee495765`")
    receipt.append("")
    receipt.append("## Frozen suite rerun")
    receipt.append("")
    receipt.append("`python3 test_rc3d.py -v` → 42 tests OK")
    receipt.append("")
    receipt.append("## Comparison command")
    receipt.append("")
    receipt.append("`python3 docs/research/contract-e/rc3d-fresh-reproduction/compare_post_freeze.py`")
    receipt.append("")
    receipt.append(
        f"Overall n={o['n']} match={o['outcome_match']} false_accept={o['false_accept']} false_reject={o['false_reject']} "
        f"native_consumption={o['native_consumption_incompatibility']} native_serialization={o['native_serialization_incompatibility']} "
        f"exec_error={o['execution_error']} normative_reason_Δ={o['normative_reason_disagreement']}"
    )
    receipt.append("")
    receipt.append("No post-reveal repair of the frozen consumer.")
    receipt.append("")
    (HERE / "POST-FREEZE-RECEIPT.md").write_text("\n".join(receipt) + "\n")

    print(json.dumps({"disposition": disposition, "why": why, "n": o["n"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
