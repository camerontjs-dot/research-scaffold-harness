"""Post-reveal comparison only. Does not alter the frozen implementation."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from contract_d import ContractDValidationError, authorization_evaluate, parse_and_validate

ROOT = Path(__file__).parent
REFERENCE = json.loads(
    (ROOT / "reference-reveal" / "decision-engine-rc2-core.json").read_text(encoding="utf-8")
)


def validation_result(obj):
    try:
        parsed = parse_and_validate(obj)
        return {"accepted": True, "semantic_identity": parsed.semantic_identity}
    except ContractDValidationError as exc:
        return {"accepted": False, "error": str(exc)}


def main() -> None:
    native_auth = authorization_evaluate(
        REFERENCE,
        actor="actor-a",
        requested_operation="knowledge.add_verified_tag",
        request_target=copy.deepcopy(REFERENCE["target"]),
        context={"scope": "claim"},
        authorization_profile={
            "allowed_actors": ["actor-a"],
            "allowed_operations": ["knowledge.add_verified_tag"],
        },
    )

    staged = []
    x = copy.deepcopy(REFERENCE)
    staged.append({"stage": "native_reference", **validation_result(x)})

    x["contract_version"] = "0.research-d"
    staged.append({"stage": "align_contract_version_only", **validation_result(x)})

    x["disposition"] = "CLEAR"
    staged.append({"stage": "also_align_disposition_encoding", **validation_result(x)})

    x["effect"]["version"] = 1
    staged.append({"stage": "also_align_effect_version_scalar_type", **validation_result(x)})

    aligned_auth = authorization_evaluate(
        x,
        actor="actor-a",
        requested_operation="knowledge.add_verified_tag",
        request_target=copy.deepcopy(x["target"]),
        context={"scope": "claim"},
        authorization_profile={
            "allowed_actors": ["actor-a"],
            "allowed_operations": ["knowledge.add_verified_tag"],
            "accepted_input_authorities": [["contract-c", "c1"]],
            "accepted_policies": [["source-audit", "1"]],
        },
    )

    receipt = {
        "freeze_sha": "43f3acc4e2c8a456e38723ee7031d89e75086529",
        "reference_head": "6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb",
        "native_reference_validation": staged[0],
        "native_frozen_consumer_result": native_auth,
        "staged_representation_alignment": staged,
        "representation_aligned_reference_vocabulary_consumer_result": aligned_auth,
        "native_cross_repository_conformance": False,
        "interpretation": (
            "The semantic core is recognizable, but native interoperability fails first on the "
            "undeclared serialization/version vocabulary and remains fail-closed on the undeclared "
            "effect registry after mechanical representation alignment."
        ),
    }

    assert receipt["native_reference_validation"]["accepted"] is False
    assert "contract_version" in receipt["native_reference_validation"]["error"]
    assert receipt["native_frozen_consumer_result"] == {
        "decision_status": "invalid_decision",
        "authorization": "cannot_establish",
    }
    assert staged[1]["accepted"] is False and "disposition" in staged[1]["error"]
    assert staged[2]["accepted"] is False and "effect.version" in staged[2]["error"]
    assert staged[3]["accepted"] is True
    assert aligned_auth == {"decision_status": "unknown_effect", "authorization": "cannot_establish"}
    assert receipt["native_cross_repository_conformance"] is False

    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
