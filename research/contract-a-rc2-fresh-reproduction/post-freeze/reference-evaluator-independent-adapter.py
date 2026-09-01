"""Mechanical invocation adapter to the immutable prereveal implementation."""
from __future__ import annotations
import sys
sys.path.insert(0, "/mnt/data/contract_a_independent")
import contract_a_rc2 as _ind

CandidateValidationError = _ind.ContractAValidationError
compute_handoff_sha256 = _ind.compute_handoff_sha256

def validate_candidate(value):
    _ind.validate_candidate(value)
    return value
