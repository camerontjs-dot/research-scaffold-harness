from __future__ import annotations

from research.contract_e_fresh_reproduction.spec_loader import load_specs


def test_authorized_specs_load() -> None:
    spec = load_specs()
    assert spec.candidate["schema"] == "contract-e-authority-warrant-research-spec"
    assert spec.shapes["schema"] == "contract-e-authority-warrant-research-spec-shapes"
    assert spec.participant_boundary["schema"] == "contract-e-participant-boundary-research-spec"
    assert spec.basis_binding["schema"] == "contract-e-authority-basis-binding-research-spec"
    assert spec.envelope_required[-1] == "participant" or "participant" in spec.envelope_required
    precedence = spec.basis_binding["ordering"]["reason_precedence"]
    assert precedence[0] == "unresolvable_authority_basis"
    assert precedence[-1] == "authority_basis_outside_validity_interval"
