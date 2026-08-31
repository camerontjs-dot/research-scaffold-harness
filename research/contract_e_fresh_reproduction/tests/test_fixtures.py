from __future__ import annotations

import json
from pathlib import Path

from research.contract_e_fresh_reproduction.spec_loader import load_specs
from research.contract_e_fresh_reproduction.validator import evaluate

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_fixture_source_access_accepts() -> None:
    case = json.loads((FIXTURES / "source_access_accept.json").read_text(encoding="utf-8"))
    result = evaluate(case, load_specs())
    assert result["outcome"] == "accept"


def test_fixture_subject_mismatch_rejects() -> None:
    case = json.loads((FIXTURES / "subject_mismatch_reject.json").read_text(encoding="utf-8"))
    result = evaluate(case, load_specs())
    assert result["outcome"] == "reject"
    assert "authority_basis_subject_mismatch" in result["violations"]
