#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
COMPARE = REPO / "docs/research/contract-e/rc3d-fresh-reproduction/compare_post_freeze.py"
ORIGINAL_RESULTS = REPO / "docs/research/contract-e/rc3d-fresh-reproduction/COMPARISON-RESULTS.json"

spec = importlib.util.spec_from_file_location("frozen_compare", COMPARE)
cmp = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cmp)

CONFERING = set(cmp.CONFERING)
CONDITIONS = {
    "W0_B0_control": (False, False),
    "W1_wrap_warrant": (True, False),
    "B1_conferring_only": (False, True),
    "W1_B1_combined": (True, True),
}

rc3a = cmp.load("RC3A-FROZEN-CASES.json")
registry_doc = cmp.load("RC3B-AUTHORITY-BASIS-REGISTRY.json")
attacks = cmp.load("RC3B-FROZEN-BASIS-ATTACKS.json")
rc3c = cmp.load("RC3C-FROZEN-CASES.json")
baselines = rc3a["baselines"]
records = registry_doc["records"]
env_by_id = {c["id"]: c for c in rc3a["envelope_cases"]}


def deep(x):
    return copy.deepcopy(x)


def materialize_case(case: dict) -> tuple[dict, dict]:
    env = deep(baselines[case["base"]])
    cmp.apply_overlays(env, case)
    reg = deep(registry_doc)
    if "record_override" in case:
        override = case["record_override"]
        rid = override["id"]
        reg["records"][rid] = cmp.overlay_record(reg["records"][rid], override)
    return env, reg


def request_of(env: dict, reg: dict) -> dict:
    return {"kind": "envelope", "envelope": env, "registry": reg, "mode": "new_exercise"}


def transform_request(request: dict, wrap_warrant: bool, conferring_only: bool) -> tuple[dict, dict]:
    req = deep(request)
    env = req["envelope"]
    meta = {"warrant_wrapped": False, "nonconferring_refs_removed": []}
    if wrap_warrant and isinstance(env.get("warrant"), dict):
        env["warrant"] = [deep(env["warrant"])]
        meta["warrant_wrapped"] = True
    if conferring_only and isinstance(env.get("authority_basis"), list):
        kept = []
        removed = []
        for ref in env["authority_basis"]:
            if isinstance(ref, dict) and ref.get("type") not in CONFERING:
                removed.append({"type": ref.get("type"), "id": ref.get("id")})
            else:
                kept.append(ref)
        env["authority_basis"] = kept
        meta["nonconferring_refs_removed"] = removed
    return req, meta


def outcome(expected: str | None, result: dict) -> str:
    if result.get("accepted") is None:
        return "execution_error"
    if expected is None:
        return "no_expected"
    want = expected == "accept"
    got = result["accepted"] is True
    if want == got:
        return "match"
    return "false_accept" if got else "false_reject"


def case_entry(family: str, case_id: str, expected: str | None, expected_reason: str | None, req: dict, tags=None):
    tags = tags or []
    return {
        "family": family,
        "id": case_id,
        "expected": expected,
        "expected_reason": expected_reason,
        "request": req,
        "tags": tags,
    }


cases = []

# RC3A envelope cases
for c in rc3a["envelope_cases"]:
    env, reg = materialize_case(c)
    cases.append(case_entry("rc3a_envelope", c["id"], c.get("expected"), c.get("reason"), request_of(env, reg)))

# RC3B direct basis attacks
for c in attacks["cases"]:
    env, reg = materialize_case(c)
    cases.append(case_entry("rc3b_basis_attacks", c["id"], c.get("expected"), c.get("reason"), request_of(env, reg)))

# Full 9x15 matrix
conferring_ids = [rid for rid, rec in records.items() if rec.get("type") in CONFERING]
for base_name, canonical_id in cmp.CANONICAL_BASIS.items():
    for record_id in conferring_ids:
        env = deep(baselines[base_name])
        idx = cmp.conferring_index(env, canonical_id)
        rec = records[record_id]
        if idx is not None:
            env["authority_basis"][idx] = {"type": rec["type"], "id": record_id, "current": True}
        expected = "accept" if record_id == canonical_id else "reject"
        cases.append(case_entry(
            "rc3b_compatibility_matrix",
            f"MATRIX-{base_name}--{record_id}",
            expected,
            None,
            request_of(env, deep(registry_doc)),
            tags=["matrix", "canonical" if expected == "accept" else "noncanonical"],
        ))

# RC3C currentness and envelope-wire cases
for c in rc3c["currentness_cases"]:
    env, reg = materialize_case(c)
    cases.append(case_entry("rc3c_currentness", c["id"], c.get("expected"), c.get("reason"), request_of(env, reg)))
for c in rc3c["wire_cases"]:
    env, reg = materialize_case(c)
    cases.append(case_entry("rc3c_wire", c["id"], c.get("expected"), c.get("reason"), request_of(env, reg)))

# Only envelope-based RC3C reason cases. Propagation is intentionally untouched.
for c in rc3c["reason_cases"]:
    if "source_envelope_case" not in c:
        continue
    source = env_by_id[c["source_envelope_case"]]
    merged = {**source, "id": c["id"], "expected": c["expected"], "reason": c.get("reason")}
    env, reg = materialize_case(merged)
    cases.append(case_entry("rc3c_reason_envelope", c["id"], c.get("expected"), c.get("reason"), request_of(env, reg)))

# Semantic metamorphic requests. Expected outcome is canonical accept for these frozen positive bases.
meta = rc3c["semantic_metamorphic"]
semantic_groups = defaultdict(list)
for base_name in meta["bases"]:
    base_env = deep(baselines[base_name])
    base_id = f"SEM-{base_name}--BASELINE"
    entry = case_entry("semantic_metamorphic", base_id, "accept", None, request_of(base_env, deep(registry_doc)), tags=["semantic", base_name, "baseline"])
    cases.append(entry)
    semantic_groups[base_name].append(base_id)
    for variant in meta["variants"]:
        env = deep(baselines[base_name])
        if variant.get("omit"):
            env.pop("result", None)
            label = variant["label"]
        else:
            env["result"] = deep(variant["result"])
            label = variant["label"]
        cid = f"SEM-{base_name}--{label}"
        cases.append(case_entry("semantic_metamorphic", cid, "accept", None, request_of(env, deep(registry_doc)), tags=["semantic", base_name, label]))
        semantic_groups[base_name].append(cid)

rows = []
for item in cases:
    original_env = item["request"]["envelope"]
    warrant_affected = isinstance(original_env.get("warrant"), dict)
    support_affected = isinstance(original_env.get("authority_basis"), list) and any(
        isinstance(ref, dict) and ref.get("type") not in CONFERING for ref in original_env["authority_basis"]
    )
    for condition, (wrap, filt) in CONDITIONS.items():
        req, meta_applied = transform_request(item["request"], wrap, filt)
        res = cmp.decision_of(req)
        rows.append({
            "family": item["family"],
            "id": item["id"],
            "condition": condition,
            "expected": item["expected"],
            "expected_reason": item["expected_reason"],
            "decision": res.get("decision"),
            "reason": res.get("reason"),
            "accepted": res.get("accepted"),
            "exception_type": res.get("exception_type"),
            "exception": res.get("exception"),
            "outcome": outcome(item["expected"], res),
            "warrant_affected": warrant_affected,
            "support_affected": support_affected,
            **meta_applied,
        })

# Control correspondence with the published terminal comparison for overlapping family/id rows.
original = json.loads(ORIGINAL_RESULTS.read_text())
orig_rows = original.get("rows") or original.get("cases") or original.get("evaluations") or []
orig_index = {(r.get("family"), r.get("id")): r for r in orig_rows if isinstance(r, dict)}
control_mismatches = []
for r in rows:
    if r["condition"] != "W0_B0_control":
        continue
    prev = orig_index.get((r["family"], r["id"]))
    if not prev:
        continue
    prev_dec = prev.get("consumer_decision", prev.get("decision"))
    prev_reason = prev.get("consumer_reason", prev.get("reason"))
    prev_exc = prev.get("exception_type")
    if (r["decision"], r["reason"], r["exception_type"]) != (prev_dec, prev_reason, prev_exc):
        control_mismatches.append({"family": r["family"], "id": r["id"], "now": [r["decision"], r["reason"], r["exception_type"]], "prior": [prev_dec, prev_reason, prev_exc]})


def summarize(condition):
    rs = [r for r in rows if r["condition"] == condition]
    return dict(Counter(r["outcome"] for r in rs))

summary = {c: summarize(c) for c in CONDITIONS}

# Cluster-specific paired effects.
def index(condition):
    return {(r["family"], r["id"]): r for r in rows if r["condition"] == condition}
idx = {c: index(c) for c in CONDITIONS}

warrant_keys = [k for k, r in idx["W0_B0_control"].items() if r["warrant_affected"]]
support_keys = [k for k, r in idx["W0_B0_control"].items() if r["support_affected"]]

def transitions(keys, treatment):
    out = Counter()
    examples = []
    for k in keys:
        a = idx["W0_B0_control"][k]
        b = idx[treatment][k]
        label = f"{a['outcome']}->{b['outcome']}"
        out[label] += 1
        if a["outcome"] != b["outcome"] or a.get("exception_type") != b.get("exception_type") or a.get("reason") != b.get("reason"):
            examples.append({"family": k[0], "id": k[1], "before": {"outcome": a["outcome"], "reason": a["reason"], "exception": a["exception_type"]}, "after": {"outcome": b["outcome"], "reason": b["reason"], "exception": b["exception_type"]}})
    return {"counts": dict(out), "changed": examples}

# Matrix safety for each condition.
matrix = {}
for condition in CONDITIONS:
    rs = [r for r in rows if r["condition"] == condition and r["family"] == "rc3b_compatibility_matrix"]
    canonical = [r for r in rs if r["expected"] == "accept"]
    noncanonical = [r for r in rs if r["expected"] == "reject"]
    matrix[condition] = {
        "canonical_accepts": sum(1 for r in canonical if r["accepted"] is True),
        "canonical_false_rejects": sum(1 for r in canonical if r["outcome"] == "false_reject"),
        "canonical_execution_errors": sum(1 for r in canonical if r["outcome"] == "execution_error"),
        "noncanonical_false_accepts": sum(1 for r in noncanonical if r["outcome"] == "false_accept"),
        "noncanonical_rejects": sum(1 for r in noncanonical if r["accepted"] is False),
        "noncanonical_execution_errors": sum(1 for r in noncanonical if r["outcome"] == "execution_error"),
    }

# Semantic metamorphic completion/invariance under each condition.
semantic = {}
for condition in CONDITIONS:
    byid = idx[condition]
    completed = 0
    changes = 0
    group_details = {}
    for base_name, ids in semantic_groups.items():
        base = byid[("semantic_metamorphic", ids[0])]
        base_sig = (base["accepted"], base["reason"])
        base_complete = base["accepted"] is not None
        var_complete = 0
        var_changes = 0
        for cid in ids[1:]:
            rr = byid[("semantic_metamorphic", cid)]
            if base_complete and rr["accepted"] is not None:
                completed += 1
                var_complete += 1
                if (rr["accepted"], rr["reason"]) != base_sig:
                    changes += 1
                    var_changes += 1
        group_details[base_name] = {"baseline_complete": base_complete, "completed_variant_comparisons": var_complete, "signature_changes": var_changes}
    semantic[condition] = {"completed_variant_comparisons": completed, "authority_signature_changes": changes, "groups": group_details}

# Explicit clusters intentionally untouched: verify diagnostic never transforms non-envelope request families.
untouched_note = {
    "propagation_nested_request": "not transformed or rescored",
    "delegation_singular_operations_scope": "not transformed or rescored",
    "qualification_scope_array": "not transformed or rescored",
}

result = {
    "schema": "contract-e-rc3d-gemini-post-falsification-diagnostic-v1",
    "terminal_disposition_of_subject": "FALSIFIED_UNCHANGED",
    "control_correspondence_mismatches": control_mismatches,
    "eligible_case_count": len(cases),
    "evaluation_count": len(rows),
    "summary_by_condition": summary,
    "warrant_affected_case_count": len(warrant_keys),
    "warrant_W1_transitions": transitions(warrant_keys, "W1_wrap_warrant"),
    "support_affected_case_count": len(support_keys),
    "support_B1_transitions": transitions(support_keys, "B1_conferring_only"),
    "combined_transitions_on_warrant_cases": transitions(warrant_keys, "W1_B1_combined"),
    "combined_transitions_on_support_cases": transitions(support_keys, "W1_B1_combined"),
    "compatibility_matrix": matrix,
    "semantic_metamorphic": semantic,
    "explicit_failures_left_untouched": untouched_note,
    "rows": rows,
}

out = HERE / "DIAGNOSTIC-RESULTS.json"
out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

print("CONTROL_CORRESPONDENCE_MISMATCHES", len(control_mismatches))
print("ELIGIBLE_CASES", len(cases))
print("EVALUATIONS", len(rows))
for c in CONDITIONS:
    print("SUMMARY", c, json.dumps(summary[c], sort_keys=True))
print("WARRANT_AFFECTED", len(warrant_keys), json.dumps(transitions(warrant_keys, "W1_wrap_warrant")["counts"], sort_keys=True))
print("SUPPORT_AFFECTED", len(support_keys), json.dumps(transitions(support_keys, "B1_conferring_only")["counts"], sort_keys=True))
for c in CONDITIONS:
    print("MATRIX", c, json.dumps(matrix[c], sort_keys=True))
    print("SEMANTIC", c, json.dumps({k:v for k,v in semantic[c].items() if k != "groups"}, sort_keys=True))

# Fail only for invalid apparatus/control correspondence or unsafe treatment false permits.
unsafe = sum(v.get("false_accept", 0) for k, v in summary.items() if k != "W0_B0_control")
if control_mismatches:
    print("DIAGNOSTIC_INVALID_CONTROL_MISMATCH")
    raise SystemExit(2)
if unsafe:
    print("DIAGNOSTIC_UNSAFE_TREATMENT_FALSE_PERMITS", unsafe)
    raise SystemExit(3)
print("DIAGNOSTIC_EXECUTED")
