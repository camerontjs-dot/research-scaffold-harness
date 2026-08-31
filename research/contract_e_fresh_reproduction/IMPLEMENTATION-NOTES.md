# Implementation notes (post-preregistration)

Dated: 2026-08-31

Preregistration commit: `9d2b6345c8387de8615375495a16cfcb3e67c503`

This file records implementation-time notes. It does **not** rewrite `PREREGISTRATION.md`.

## Runtime

The host available to this run is Apple Command Line Tools Python 3.9.6. The scaffold repository's `pyproject.toml` asks for Python 3.11+, but the consumer uses only the standard library. Tests are executed with:

```text
python3 -m research.contract_e_fresh_reproduction.run_tests
```

pytest is supported if present (`pytest research/contract_e_fresh_reproduction`) but was not installed in this environment. A standard-library runner is therefore the recorded test command.

Evaluate a case:

```text
python3 -m research.contract_e_fresh_reproduction path/to/case.json
```

## Deviations / extra assumptions taken at implementation time

### D2. Delegation and domain `any_of`

Preregistration T16d predicted that a true-subset delegation can accept. Domain `any_of` lists for operational domains name `grant` and/or `policy` and do not name `delegation`, even though `delegation` is an authority-conferring type.

If `any_of` were applied to the child record type alone, every delegation would be rejected as `authority_basis_type_not_allowed_for_domain`. That would make the specified delegation shape dead.

**Local choice:** a delegation satisfies domain `any_of` when a parent chain reaches a record whose `type` is in that `any_of` list. Tagged in outcome notes as `D2-delegation-any-of-via-parent`.

This is an implementation assumption. If the intended reading is that delegation is never a domain basis unless listed in `any_of`, T16d is a false accept.

### Warrant currentness when `exercise_kind=historical`

`warrant_shape.current_required` is unconditional, unlike qualification's `current_required_for_new_exercise`. The implementation requires `warrant.current is true` whenever a warrant is evaluated, including historical mode. Historical tests in this suite do not depend on a stale warrant.

### Reference `current` ignored for the currentness decision

Matches assumption C1: record currentness (and `revoked_at` for new exercise) is authoritative.

## What the consumer is

A common validator over an evaluation case:

- `envelope` (required Contract E common envelope plus `participant`)
- `basis_records` (explicit resolver map; assumption R1)
- optional `qualification`, `warrant`, `result`, `historical_record`
- optional `propagated_fields`, `claimed_effects`, `claimed_responsibilities`
- `exercise_kind` (`new` default, or `historical`; assumption H1)

It is **not** a production authorization service, registry, or cryptographic verifier.

## Contamination

No withheld registry, frozen attack corpus, RC3 validator, RESULTS file, PR narrative, or other reproduction was observed during implementation.
