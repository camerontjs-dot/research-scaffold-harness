# Pre-reveal self-designed test report

Frozen at implementation+tests commit `0233869e4b059bd82af72186934e5318d8c893f6`.
Runner: `.venv/bin/python -m pytest tests/contract_e_rc3c`
Result: **145 passed**, 0 failed, 0 skipped.

Command identity: Python 3.11.15, pytest 9.1.1.

## Counts by file

| File | Collected tests |
|---|---|
| test_aperture_hashes.py | 1 |
| test_basis_binding.py | 20 |
| test_cli.py | 5 |
| test_currentness.py | 14 |
| test_delegation.py | 8 |
| test_happy_paths.py | 11 |
| test_historical.py | 4 |
| test_non_implication_and_registry.py | 7 |
| test_participant_and_envelope.py | 12 |
| test_precedence.py | 6 |
| test_propagation.py | 10 |
| test_qualification_warrant.py | 17 |
| test_result_opacity.py | 16 |
| test_wire_cardinality.py | 14 |
| **Total** | **145** |

## Surfaces covered

- Nine-domain native happy paths
- Wire cardinality / no-coercion attacks
- Currentness conjunction, inclusive validity bounds, revocation equality
- RC3B matching failures and non-conferring types
- Cross-domain assessment_mandate→citation_use and decision_mandate→task_dispatch
- Participant, generic authorized, unknown domain/operation
- Qualification and warrant attacks
- Propagation none/identity/explicit/reestablishment
- Delegation subset and amplification
- Historical inspection vs new-exercise recheck
- Result-payload metamorphism (positive informational baseline and reject)
- CLI evaluate-envelope / evaluate / evaluate-delegation / evaluate-historical / evaluate-propagation

No hidden/reference vectors were used. No test was designed against expected reference outcomes.
