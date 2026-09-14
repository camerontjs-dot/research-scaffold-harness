from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APERTURE = ROOT / "research" / "contract_c_candidate_a_rc2_consumer_b_aperture"
CANDIDATE = ROOT / "candidate"
sys.path.insert(0, str(CANDIDATE))
from consumer import consume_contract_c  # noqa: E402

APPARATUS_HEAD = "b42c827acb0a9fe65353354d709add0e27bab307"
PUBLIC_VERSION = "2.0.0"
WIRE_PROFILE = "contract-c-successor-candidate-a-rc2-research"

EXPECTED = {
    "independent_supports": {
        "terminal": {"reason": "categorical_support", "verdict": "supported"},
        "basis": (("S1",), ("S2",)),
        "residual_only": False,
    },
    "alternative_joint_mixed": {
        "terminal": {"reason": "MIXED_RELATIONS", "verdict": "not_checkable"},
        "basis": (("R1", "S1"), ("R1", "S2")),
        "residual_only": False,
    },
    "no_deciding": {
        "terminal": {"reason": "no_deciding_relation", "verdict": "not_checkable"},
        "basis": (),
        "residual_only": True,
    },
    "unsupported_family": {
        "terminal": {
            "reason": "UNSUPPORTED_SEMANTIC_FAMILY",
            "verdict": "not_checkable",
        },
        "basis": (),
        "residual_only": True,
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _authority(common: dict[str, Any], whole: str) -> dict[str, Any]:
    return {
        "profile": common["profile"],
        "semantic_implementation_sha": common["semantic_implementation_sha"],
        "policy_sha256": common["policy_sha256"],
        "policy_resolver_commit_sha": common["policy_resolver_commit_sha"],
        "whole_object_sha256": whole,
    }


def _contract_b_tuple(index: dict[str, Any]) -> dict[str, str]:
    return {
        "contract_version": index["contract_version"],
        "bundle_id": index["bundle_id"],
        "bundle_hash": index["bundle_hash"],
    }


def _evidence_index(index: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (entry["source_id"], passage_id)
        for passage_id, entry in index["passages"].items()
    }


def _basis(obj: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
    groups = obj["propositions"][0]["basis_groups"]
    return tuple(
        sorted(
            tuple(sorted(member["passage_id"] for member in group))
            for group in groups
        )
    )


def _residual_only(obj: dict[str, Any]) -> bool:
    participants = obj["propositions"][0]["participants"]
    return bool(participants) and all(
        p["relation"] == "non_polarized" and p["role"] == "residual"
        for p in participants
    )


def evaluate(apparatus_root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(apparatus_root))
    try:
        prod = importlib.import_module("validators.contract_c_v2")
    finally:
        sys.path.pop(0)

    authorities = _load_json(APERTURE / "AUTHORITIES.json")
    indexes = _load_json(APERTURE / "CONTRACT_B_INDEXES.json")
    common = authorities["common"]
    versions = _load_json(apparatus_root / "schema" / "contract-c" / "versions.json")
    candidate_version = _load_json(
        apparatus_root / "schema" / "contract-c" / "2.0.0" / "promotion-version.json"
    )

    checks: dict[str, bool] = {}
    observations: dict[str, Any] = {}

    checks["production_identity_exact"] = (
        prod.CONTRACT_C_VERSION == PUBLIC_VERSION
        and prod.WIRE_PROFILE == WIRE_PROFILE
        and prod.PROFILE == WIRE_PROFILE
        and common["profile"] == WIRE_PROFILE
        and prod.CAL_RC1_IMPLEMENTATION == common["semantic_implementation_sha"]
        and prod.CAL_RC1_POLICY_SHA256 == common["policy_sha256"]
        and prod.POLICY_RESOLVER_FIXTURE_COMMIT
        == common["policy_resolver_commit_sha"]
    )
    checks["premerge_global_discovery_remains_c1"] = versions == {
        "canonical_version": "1.0.0",
        "supported_versions": ["1.0.0"],
    }
    checks["candidate_c2_version_is_external_and_noncanonical"] = (
        candidate_version.get("candidate_compatibility_version") == PUBLIC_VERSION
        and candidate_version.get("wire_profile") == WIRE_PROFILE
        and candidate_version.get("canonical_registry_switch_authorized") is False
    )

    all_prod_valid = True
    all_bytes_exact = True
    all_consumer_valid = True
    all_semantics_exact = True

    for key, metadata in authorities["handoffs"].items():
        raw = (APERTURE / metadata["file"]).read_bytes()
        obj = json.loads(raw.decode("utf-8"))
        index = indexes[metadata["contract_b_index"]]
        authority = _authority(common, metadata["whole_object_sha256"])

        prod.validate_object(obj)
        prod.verify_contract_b_references(
            obj,
            exact_contract_b=_contract_b_tuple(index),
            evidence_index=_evidence_index(index),
        )
        prod.verify_policy_resolution(
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
        prod.verify_external_authority(
            obj,
            expected_whole_object_sha256=metadata["whole_object_sha256"],
        )

        canonical = prod.canonical_bytes(obj)
        whole = prod.whole_object_sha256(obj)
        bytes_exact = canonical == raw
        whole_exact = whole == metadata["whole_object_sha256"]
        all_prod_valid = all_prod_valid and whole_exact
        all_bytes_exact = all_bytes_exact and bytes_exact and whole_exact

        consumed = consume_contract_c(raw, index, authority)
        expected = EXPECTED[key]
        semantics_exact = (
            consumed["propositions"][0]["terminal"] == expected["terminal"]
            and _basis(consumed) == expected["basis"]
            and (
                _residual_only(consumed)
                if expected["residual_only"]
                else True
            )
        )
        all_consumer_valid = all_consumer_valid and isinstance(consumed, dict)
        all_semantics_exact = all_semantics_exact and semantics_exact

        observations[key] = {
            "raw_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "whole_object_sha256": whole,
            "production_canonical_bytes_equal_frozen_raw": bytes_exact,
            "production_external_authority_exact": whole_exact,
            "consumer_terminal": consumed["propositions"][0]["terminal"],
            "consumer_basis_groups": [list(group) for group in _basis(consumed)],
            "consumer_semantics_exact": semantics_exact,
        }

    checks["all_four_validate_under_production_c2"] = all_prod_valid
    checks["all_four_production_bytes_and_authority_exact"] = all_bytes_exact
    checks["all_four_consumed_by_frozen_consumer_b"] = all_consumer_valid
    checks["all_four_public_semantics_exact"] = all_semantics_exact

    required = [
        "production_identity_exact",
        "premerge_global_discovery_remains_c1",
        "candidate_c2_version_is_external_and_noncanonical",
        "all_four_validate_under_production_c2",
        "all_four_production_bytes_and_authority_exact",
        "all_four_consumed_by_frozen_consumer_b",
        "all_four_public_semantics_exact",
    ]
    failures = [name for name in required if not checks[name]]
    disposition = (
        "SUPPORTED_C2_PROMOTION_INDEPENDENT_CONSUMER_CONFORMANCE"
        if not failures
        else "FALSIFIED"
    )
    return {
        "schema": "contract-c-2.0-promotion-consumer-b-conformance-rc0-result-v1",
        "research_disposition": disposition,
        "consumer_b_subject": "ba09743b28e57bc87dd1f315046ef79b93f24021",
        "apparatus_promotion_head": APPARATUS_HEAD,
        "checks": checks,
        "failures": failures,
        "observations": observations,
        "interpretation": {
            "consumer_b_modified": False,
            "producer_private_state_required": False if not failures else None,
            "production_profile_consumer_gate_satisfied": not failures,
            "postreveal_27_attack_programme_rerun_here": False,
            "contract_c_2_released": False,
            "promotion_merge_authorized": False,
        },
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: evaluate.py <apparatus-root> <output-json>")
    result = evaluate(Path(sys.argv[1]).resolve())
    output = Path(sys.argv[2])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["research_disposition"] != (
        "SUPPORTED_C2_PROMOTION_INDEPENDENT_CONSUMER_CONFORMANCE"
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
