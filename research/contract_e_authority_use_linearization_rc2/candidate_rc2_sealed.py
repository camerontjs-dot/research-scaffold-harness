"""Sealed-candidate composition for RC2.

This wrapper adds the preregistered highest-generation anti-rollback invariant
around the frozen candidate core in candidate_rc2_final.py.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

_CORE_PATH = Path(__file__).with_name("candidate_rc2_final.py")
_SPEC = importlib.util.spec_from_file_location("contract_e_rc2_candidate_core", _CORE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load RC2 candidate core")
core = importlib.util.module_from_spec(_SPEC)
sys.modules["contract_e_rc2_candidate_core"] = core
_SPEC.loader.exec_module(core)

InjectedResponseLoss = core.InjectedResponseLoss
InjectedRollback = core.InjectedRollback
initialize_store = core.initialize_store
install_authority = core.install_authority
state_digest = core.state_digest
connect = core.connect
validate_decision = core.validate_decision
validate_intent = core.validate_intent

_BASE_LOAD_CURRENT = core.load_current_authority


def load_current_authority(conn, canonical_bytes):
    row, state = _BASE_LOAD_CURRENT(conn, canonical_bytes)
    highest = conn.execute(
        "SELECT MAX(generation) AS max_generation FROM authority_history WHERE epoch=?",
        (row["epoch"],),
    ).fetchone()
    if highest is None or highest["max_generation"] is None:
        raise ValueError("authority history missing highest generation")
    if row["generation"] != highest["max_generation"]:
        raise ValueError("authority current pointer rolled back below highest installed generation")
    return row, state


def execute(*args: Any, **kwargs: Any):
    # The core execute resolves load_current_authority from its module globals.
    # Patch only for the duration of the call so the frozen core plus this
    # wrapper form the exact candidate surface.
    previous = core.load_current_authority
    core.load_current_authority = load_current_authority
    try:
        return core.execute(*args, **kwargs)
    finally:
        core.load_current_authority = previous
