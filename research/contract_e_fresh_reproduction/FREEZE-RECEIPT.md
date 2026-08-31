# Contract E fresh reproduction — pre-reveal freeze receipt

Marker: `FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_REVEAL`

## Identity

- Model/provider: Grok 4.6, xAI
- Execution date/time (UTC): 2026-08-31T00:44:42Z
- Host Python: Apple Command Line Tools Python 3.9.6
- Branch: `research/contract-e-fresh-reproduction-grok-final-20260830-LVwH1H`
- Remotes at freeze: none observed

## Git SHAs

- Authorized clean base: `548bfa81f65290eda15af658f647497679b840ef`
- Exact starting/input commit SHA: `ca9c00a3a238d449445485fc72974837fee7ac5c`
- Preregistration commit SHA: `9d2b6345c8387de8615375495a16cfcb3e67c503`
- Final implementation freeze commit SHA: `PENDING_THIS_COMMIT`
- Final tree SHA: `PENDING_THIS_TREE`

These PENDING values are replaced with `git rev-parse HEAD` and `git rev-parse HEAD^{tree}` of the freeze commit that introduces this receipt.

## Authorized input specification hashes

Git blobs (must match the launch packet):

| File | Git blob |
|---|---|
| `authority_input/SPEC-CANDIDATE.json` | `9c1090335d87eb5e4885a755542923b453c45317` |
| `authority_input/SPEC-SHAPES.json` | `c3f293430ae6ddb87523d83ea6e5380b8b832136` |
| `authority_input/SPEC-PARTICIPANT-BOUNDARY.json` | `8b1d292a240300388949d502e7b656e7a23a0b8e` |
| `authority_input/BASIS-BINDING-SPEC.json` | `63c952c9c28f1be2173e69c79976c7dfe5880c10` |

SHA-256 of the same files in this workspace:

| File | SHA-256 | Bytes |
|---|---|---|
| `authority_input/SPEC-CANDIDATE.json` | `ff602f3645a16b69359e73d5667e8ad87b16046685a80bc77cf2254c3edaa364` | 8075 |
| `authority_input/SPEC-SHAPES.json` | `f162b2d645afc09d7d18d0c0bd1395a22417d82b89183271f68ea31df20d39b7` | 3005 |
| `authority_input/SPEC-PARTICIPANT-BOUNDARY.json` | `5aa53d344c8f61d5a2cae732e83c9d64386e47786a614778e2ea152e1daddf0c` | 487 |
| `authority_input/BASIS-BINDING-SPEC.json` | `fe5ebd0944edcb3777f9dbec4dde5040bfa29bad30611288e46edd4722666319` | 2530 |

The four input files were not modified during this run.

## Implementation/test manifest

Deterministic per-file SHA-256 list: `research/contract_e_fresh_reproduction/MANIFEST.sha256`

Regenerate with:

```text
python3 -m research.contract_e_fresh_reproduction.hash_manifest
```

## Exact test command(s)

Primary (recorded, standard library; pytest was not installed on the host):

```text
python3 -m research.contract_e_fresh_reproduction.run_tests
```

Equivalent if pytest is available:

```text
python3 -m pytest research/contract_e_fresh_reproduction -q
```

CLI smoke on frozen fixtures:

```text
python3 -m research.contract_e_fresh_reproduction research/contract_e_fresh_reproduction/fixtures/source_access_accept.json
python3 -m research.contract_e_fresh_reproduction research/contract_e_fresh_reproduction/fixtures/subject_mismatch_reject.json
```

Machine-readable suite output: `research/contract_e_fresh_reproduction/self_test_results.json`

## Test counts and results

- 73 passed
- 0 failed
- 0 errors
- 73 total
- `ok: true`

No test failure was suppressed. Failures, had they occurred, would have been preserved.

CLI fixture outcomes:

- `source_access_accept.json` → `accept` / `ok`
- `subject_mismatch_reject.json` → `reject` / `authority_basis_subject_mismatch`

## Unresolved ambiguities

These remain unresolved specification gaps. Local deterministic branches are labeled as implementation assumptions in `PREREGISTRATION.md` and `IMPLEMENTATION-NOTES.md`. They are **not** specification authority.

1. Warrant required vs allowed when `domain_basis_requirements` names a warrant (W1).
2. Multiple `authority_basis` entries combined as any-matching-conferring (B1).
3. Resolver is an explicit in-memory `basis_records` map (R1).
4. `exercise_kind` new vs historical is an extra input, default `new` (H1).
5. Reference `current` cannot override record currentness; record is authoritative (C1).
6. `revoked_at <= evaluated_at` treated as not current for new exercise (C2).
7. Validity-interval bounds inclusive; ISO-8601 timestamps (T1).
8. `authority_basis` must be a list; a single object is malformed (B2).
9. Qualification `scope` is not matched against jurisdiction (Q1).
10. Stale target is hash divergence or `target.current is false` (S1).
11. Excluded responsibilities checked only when claimed (P1).
12. Overall check order outside basis `reason_precedence` (O1, O2).
13. Delegation parent-subset details and subject/`delegate` (A13).
14. Delegation satisfies domain `any_of` via parent chain (D2; implementation-time).
15. `input_artifact_ids` presence-only (W2).
16. Non-implications union of envelope and warrant-type lists (N1).
17. Presence of generic `authorized` rejects rather than ignores (G1).
18. Unknown extra envelope fields ignored except forbidden generic boolean (X1).
19. Domain `kind` is documentary (K1).
20. Historical `authority_was_valid_at_time=true` is recomputed (H2).
21. Non-conferring types never satisfy authority (B3).
22. Inapplicable applies to both jurisdiction and warrant (I1).
23. Warrant `current` required whenever a warrant is evaluated.

Disagreement with a later reference on any of these is evidence, not a pre-reveal defect to patch.

## Deviations

- Preregistration was not rewritten.
- Implementation-time assumption D2 (delegation/`any_of`) is recorded in `IMPLEMENTATION-NOTES.md`.
- Tests run on Python 3.9.6 with a standard-library runner because pytest and Python 3.11 were not available on the host.
- `research/__init__.py` was added so the consumer is importable as `research.contract_e_fresh_reproduction`.

## Contamination

None observed. Forbidden materials listed in TASK.md section 4 were not searched, opened, or used. No web, GitHub, or other-repository retrieval was performed. No other reproduction's implementation was read.

Literal marker (valid only because no forbidden material was observed):

`FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_REVEAL`
