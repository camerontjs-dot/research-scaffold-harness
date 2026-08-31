"""Research-only native Contract E RC3C authority consumer.

This package is not a production authority implementation and does not
modify Research Scaffold Harness C-A behavior.
"""

from research_scaffold_harness.contract_e_rc3c.validator import (
    Decision,
    evaluate,
    evaluate_delegation,
    evaluate_envelope,
    evaluate_historical,
    evaluate_propagation,
    normalize_registry,
)

__all__ = [
    "Decision",
    "evaluate",
    "evaluate_delegation",
    "evaluate_envelope",
    "evaluate_historical",
    "evaluate_propagation",
    "normalize_registry",
]
