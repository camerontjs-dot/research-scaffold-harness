from __future__ import annotations

import copy
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APERTURE = ROOT / "research" / "contract_c_candidate_a_rc2_consumer_b_aperture"
APPARATUS_HEAD = "b42c827acb0a9fe65353354d709add0e27bab307"
C2_PROFILE = "contract-c-successor-candidate-a-rc2-research"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _c2_index(index: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (entry["source_id"], passage_id)
        for passage_id, entry in index["passages"].items()
    }


def _c2_contract_b(index: dict[str, Any]) -> dict[str, str]:
    return {
        "contract_version": index["contract_version"],
        "bundle_id": index["bundle_id"],
        "bundle_hash": index["bundle_hash"],
    }


def evaluate(apparatus_root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(apparatus_root))
    try:
        c1 = importlib.import_module("validators.contract_c")
        c2 = importlib.import_module("validators.contract_c_v2")
    finally:
        sys.path.pop(0)

    c1_raw = (apparatus_root / "fixtures" / "contract-c" / "1.0.0" / "valid-canonical.json").read_bytes()
    c1_index = _load_json(
        apparatus_root / "fixtures" / "contract-c" / "1.0.0" / "contract-b-index.json"
    )
    c1_obj = c1.parse_json_bytes(c1_raw)
    c1_sha = _sha(c1_raw)

    authorities = _load_json(APERTURE / "AUTHORITIES.json")
    indexes = _load_json(APERTURE / "CONTRACT_B_INDEXES.json")

    checks: dict[str, bool] = {}
    observations: dict[str, Any] = {}

    c1_errors = c1.validate_contract_c_bytes(
        c1_raw,
        expected_sha256=c1_sha,
        contract_b_index=c1_index,
    )
    checks["c1_accepts_exact_c1"] = c1_errors == []

    try:
        c2.validate_object(c1_obj)
    except Exception as exc:
        c2_rejects_c1 = True
        c2_rejects_c1_error = f"{type(exc).__name__}: {exc}"
    else:
        c2_rejects_c1 = False
        c2_rejects_c1_error = None
    checks["c2_rejects_exact_c1"] = c2_rejects_c1

    common = authorities["common"]
    all_c1_reject_c2 = True
    all_c2_accept_c2 = True
    all_external_profile_binding = True

    for key, metadata in authorities["handoffs"].items():
        raw = (APERTURE / metadata["file"]).read_bytes()
        obj = json.loads(raw.decode("utf-8"))
        index = indexes[metadata["contract_b_index"]]

        c1_on_c2_errors = c1.validate_contract_c_bytes(raw)
        c1_rejects = bool(c1_on_c2_errors)
        all_c1_reject_c2 = all_c1_reject_c2 and c1_rejects

        try:
            c2.validate_object(obj)
            c2.verify_contract_b_references(
                obj,
                exact_contract_b=_c2_contract_b(index),
                evidence_index=_c2_index(index),
            )
            c2.verify_policy_resolution(
                obj,
                independently_selected_resolver_commit_sha=common[
                    "policy_resolver_commit_sha"
                ],
                resolver_entries=[
                    {
                        "semantic_implementation_sha": common[
                            "semantic_implementation_sha"
                        ],
                        "policy_sha256": common["policy_sha256"],
                    }
                ],
            )
            c2.verify_external_authority(
                obj,
                expected_whole_object_sha256=metadata["whole_object_sha256"],
            )
            c2_accepts = c2.canonical_bytes(obj) == raw
        except Exception:
            c2_accepts = False
        all_c2_accept_c2 = all_c2_accept_c2 and c2_accepts

        # Externally selected C1 cannot be overridden by the C2 artifact's profile.
        # Externally selected C2 succeeds only under C2's exact authority.
        externally_bound = c1_rejects and c2_accepts
        all_external_profile_binding = all_external_profile_binding and externally_bound

        observations[key] = {
            "c1_rejects_c2": c1_rejects,
            "c1_rejection_sample": c1_on_c2_errors[:4],
            "c2_accepts_c2": c2_accepts,
            "external_profile_binding_preserved": externally_bound,
            "whole_object_sha256": metadata["whole_object_sha256"],
        }

    checks["c1_rejects_all_four_exact_c2"] = all_c1_reject_c2
    checks["c2_accepts_all_four_exact_c2"] = all_c2_accept_c2
    checks["external_profile_selection_preserved"] = (
        all_external_profile_binding and c2_rejects_c1
    )

    # Test the current normative in-band downgrade boundary. C1's schema is
    # closed, so each required C2-only semantic surface must make an otherwise
    # valid C1 artifact invalid even after recomputing C1's local identity.
    mutations: dict[str, Any] = {}

    def score_mutation(label: str, mutate) -> None:
        value = copy.deepcopy(c1_obj)
        mutate(value)
        value = c1.with_result_set_identity(value)
        raw = c1.canonical_bytes(value)
        errors = c1.validate_contract_c_bytes(raw, contract_b_index=c1_index)
        mutations[label] = {
            "strict_c1_rejected": bool(errors),
            "rejection_sample": errors[:4],
        }

    score_mutation(
        "inject_terminal_reason",
        lambda value: value["propositions"][0].__setitem__(
            "terminal", {"verdict": "supported", "reason": "categorical_support"}
        ),
    )
    score_mutation(
        "inject_participant_role",
        lambda value: value["propositions"][0]["contributions"][0].__setitem__(
            "role", "causal"
        ),
    )
    score_mutation(
        "inject_basis_groups",
        lambda value: value["propositions"][0].__setitem__(
            "basis_groups",
            [[{"source_id": "src-md", "passage_id": "auto-src-md-947b3344e6db"}]],
        ),
    )
    score_mutation(
        "inject_non_polarized_relation",
        lambda value: value["propositions"][0]["contributions"][0].__setitem__(
            "channel", "non_polarized"
        ),
    )

    checks["c1_closed_grammar_rejects_tested_c2_semantic_surfaces"] = all(
        row["strict_c1_rejected"] for row in mutations.values()
    )

    versions = _load_json(apparatus_root / "schema" / "contract-c" / "versions.json")
    promotion_version = _load_json(
        apparatus_root / "schema" / "contract-c" / "2.0.0" / "promotion-version.json"
    )
    checks["premerge_version_authority_exact"] = (
        versions == {"canonical_version": "1.0.0", "supported_versions": ["1.0.0"]}
        and promotion_version.get("candidate_compatibility_version") == "2.0.0"
        and promotion_version.get("wire_profile") == C2_PROFILE
        and promotion_version.get("canonical_registry_switch_authorized") is False
        and c2.CONTRACT_C_VERSION == "2.0.0"
        and c2.WIRE_PROFILE == C2_PROFILE
    )

    required = [
        "c1_accepts_exact_c1",
        "c2_rejects_exact_c1",
        "c1_rejects_all_four_exact_c2",
        "c2_accepts_all_four_exact_c2",
        "external_profile_selection_preserved",
        "c1_closed_grammar_rejects_tested_c2_semantic_surfaces",
        "premerge_version_authority_exact",
    ]
    failures = [name for name in required if not checks[name]]
    disposition = (
        "SUPPORTED_C2_MAJOR_COMPATIBILITY_BOUNDARY" if not failures else "FALSIFIED"
    )
    return {
        "schema": "contract-c-2.0-promotion-compatibility-rc0-result-v1",
        "research_disposition": disposition,
        "apparatus_promotion_head": APPARATUS_HEAD,
        "checks": checks,
        "failures": failures,
        "observations": observations,
        "tested_c1_closed_grammar_injections": mutations,
        "c1_on_c1_errors": c1_errors,
        "c2_on_c1_rejection": c2_rejects_c1_error,
        "semver_evidence": {
            "existing_strict_c1_consumer_breaks_on_exact_c2": all_c1_reject_c2,
            "exact_c2_accepts_exact_c2": all_c2_accept_c2,
            "tested_c2_only_semantics_not_in_band_representable_in_c1": all(
                row["strict_c1_rejected"] for row in mutations.values()
            ),
            "governance_signal": "MAJOR" if not failures else "UNRESOLVED",
            "universal_translation_impossibility_claimed": False,
        },
        "interpretation": {
            "lossless_downgrade_adapter_authorized": False,
            "released_c1_mutated": False,
            "candidate_c2_canonical": False,
            "promotion_merge_authorized": False,
        },
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: evaluate_compat.py <apparatus-root> <output-json>")
    result = evaluate(Path(sys.argv[1]).resolve())
    output = Path(sys.argv[2])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["research_disposition"] != "SUPPORTED_C2_MAJOR_COMPATIBILITY_BOUNDARY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
