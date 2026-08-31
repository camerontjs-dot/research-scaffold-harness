# Contract E RC3C fresh successor freeze receipt

FRESH_RC3C_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL

This receipt freezes the independent Grok reproduction **before** any
hidden/reference vector reveal. The implementation and pre-reveal tests
are immutable for scientific comparison after this marker.

## Identity

- Repository: `camerontjs-dot/research-scaffold-harness` (isolated workspace)
- Branch: `research/contract-e-rc3c-fresh-reproduction-grok-20260830T222828-e712ac`
- Provider / model / CLI: xAI Grok 4.6, isolated agent session
- Clean base SHA: `548bfa81f65290eda15af658f647497679b840ef`
- Clean base tree: `191976638bbf8b7153e3f2c94945a2f15cd640ad`

## Isolation controls

- Worked only in this isolated workspace.
- Pre-freeze information aperture: `TASK.md` plus the five blobs under `authority_input/`.
- Did not access GitHub, the web, other local repositories, prior Contract E reproductions, RC3A/RC3B/RC3C frozen cases, registries, validators, results, workflow artifacts, or another model's output.
- Did not open denied PRs, first-reproduction branches, or reference validators.
- Production harness C-A behavior was not modified except for an additive research console-script entry.

## Contamination status

**none**

No denied material was observed before freeze.

## Input aperture

- Aperture commit: `8902fca4e61221cfb40e52ce7abc6c58a1ec42d5`
- Aperture tree: `d8062a35715d9a3deb91b8658ea7020845bfbb43`
- `TASK.md` SHA-256: `7c1873b8834b945222949799059adae118363652c0c6d945e48dc97de512acb3`
- Spec corpus aggregate SHA-256 (filename + file SHA-256): `c3759d6012983c017ea08a0a465e4564088f3732594ff036bec33278cd446aa5`

Authorized blobs (git SHA-1 / file SHA-256):

| Blob | git SHA-1 | SHA-256 |
|---|---|---|
| SPEC-CANDIDATE.json | `9c1090335d87eb5e4885a755542923b453c45317` | `ff602f3645a16b69359e73d5667e8ad87b16046685a80bc77cf2254c3edaa364` |
| SPEC-SHAPES.json | `c3f293430ae6ddb87523d83ea6e5380b8b832136` | `f162b2d645afc09d7d18d0c0bd1395a22417d82b89183271f68ea31df20d39b7` |
| SPEC-PARTICIPANT-BOUNDARY.json | `8b1d292a240300388949d502e7b656e7a23a0b8e` | `5aa53d344c8f61d5a2cae732e83c9d64386e47786a614778e2ea152e1daddf0c` |
| BASIS-BINDING-SPEC.json | `63c952c9c28f1be2173e69c79976c7dfe5880c10` | `fe5ebd0944edcb3777f9dbec4dde5040bfa29bad30611288e46edd4722666319` |
| RC3C-SPEC.json | `f05feac88128fd693cca2fb25a0b2951654377eb` | `d1d355929060c0d94518fa4063a81d80d92f3e4ad9172bfca3d5cd20ce58bd35` |

Git blob identities match TASK.md section 3.

## Preregistration

- Preregistration commit: `a3a844fc8d7685ed15cec80aaefba5db2a8339c6`
- Preregistration tree: `e12e7b7a9e1e15b18bd7c6aa067223aea9c45599`
- Path: `docs/research/contract-e/rc3c-fresh-reproduction/PREREGISTRATION.md`
- SHA-256: `f60aabec6bfdc1edbc460a01c3862c39ed93308616765652226e897b11e8958d`
- git blob: `1655315ada16aa93a5ff78374e5c934603f15b17`

Committed **before** implementation.

## Frozen implementation

- Implementation commit: `310a44182a13dc9df9321bc2900bf3c60b4c87b5`
- Implementation tree: `0d7bfd8a957c22593a5c6980565b1af3e54a1403`
- Complete impl+tests commit (code freeze point): `0233869e4b059bd82af72186934e5318d8c893f6`
- Complete impl+tests tree: `2328707660d28e138f5656f6eb04843d7f37ff5a`
- Package: `research_scaffold_harness.contract_e_rc3c`
- CLI: `contract-e-rc3c` and `python -m research_scaffold_harness.contract_e_rc3c`
- Native consumption: JSON dict/list/bool/str checks; no Pydantic envelope coercion; no singular/plural adapter; `result` never read.

Implementation source SHA-256:

| Path | SHA-256 |
|---|---|
| `src/research_scaffold_harness/contract_e_rc3c/__init__.py` | `73860fe6a47f41168d7dfed0b6e682e266b7408a3309a192129f90276e18acc5` |
| `src/research_scaffold_harness/contract_e_rc3c/__main__.py` | `b0de8348aa483469614cb2d45456aaddbdf69349f88da5d1da629f3d8caef11e` |
| `src/research_scaffold_harness/contract_e_rc3c/cli.py` | `6e7a8917054ba21317228af516971c4949f82a4160301f088b9c8b60682eee4a` |
| `src/research_scaffold_harness/contract_e_rc3c/spec.py` | `919b3787a85ae1ff3a47589859387aafaf258dc6b429b53e1fa5fecc4aaea009` |
| `src/research_scaffold_harness/contract_e_rc3c/validator.py` | `ffcf7a9013805d0a6acc6fb54a37c2f1d683fd7a21c7d0b935b1c2493c0f77cb` |
| `pyproject.toml` | `97b16d4c98520001abe3aebd6f7f79225ec78a2ef6d65c97b01bc989ad34e781` |

Implementation corpus aggregate SHA-256: `596d231c12a41282b78c7e9cdb2d7cb93410e7400454aa3ff6a3a968ac3c62ed`

## Pre-reveal tests

- Tests commit: `0233869e4b059bd82af72186934e5318d8c893f6`
- Tests tree: `2328707660d28e138f5656f6eb04843d7f37ff5a`
- Collected / passed: **145 / 145**
- Failed / skipped: 0 / 0
- Test files: 18
- Test corpus aggregate SHA-256: `338601c74f4c3f83fdf6d95268a167ddc58b91206705106811f4fc3240c402e1`

## Recorded ambiguities (preserved, not repaired)

A1 multiple conferring references (at-least-one sufficient bind)
A2 delegation not in domain `any_of`
A3 qualification.scope compared to jurisdiction.scope
A4 warrant is a single object
A5 non_implications wrong type → local `malformed_non_implications_shape`
A6 unparseable timestamps → local `unparseable_datetime`
A7 envelope.propagation string or object
A8 extra none/identity fields → local `propagation_forbidden_fields`
A9 `separately_reauthorized` boolean-true bypass only
A10 stale_target only via warrant hash / required fields
A11 historical extra fields ignored for live authority
A12 non-boolean current/applicable fail closed
A13 empty delegation arrays are malformed cardinality
A14 non-array resolved-record membership fields fail closed as mismatch
A15 unknown basis types cannot satisfy domain `any_of`
A16 nested `authorized` inside `result` ignored
A17 relisted reasons vs whole-envelope precedence
A18 missing qualification inner keys → missing_required_field
A19 incomplete resolved record → unresolvable_authority_basis
A20 inverted validity interval cannot authorize
A21 non-current delegation child on new_exercise → authority_basis_not_current
A22 identity_provenance_only fields may appear, must not exceed allow-list

## Native-wire / adaptation deviations

None in the frozen consumer. Canonical envelopes, registries, delegations, and
propagation objects are accepted as JSON. No hidden-vector adapter exists.

## Semantic metamorphic result (self-tests)

Replacing opaque `result` with omitted / positive / negative / indeterminate /
success/confidence variants did not change `accepted` or `primary_reason` on a
positive `numeric_relation` envelope or on a missing-basis reject.

## Post-freeze reveal

**not performed**

Authorized comparison artifacts from TASK.md section 7 were not opened.
No reference validators, generated reference results, RC3C design reasoning,
or first-reproduction materials were consulted.

A Draft Research PR was not opened in this session: GitHub is denylisted
before freeze, and this run is required to stop at the freeze marker.

## Terminal disposition of this session

FROZEN. Independent implementation and pre-reveal tests are immutable.
No post-freeze repair. No reference-vector comparison in this run.

FRESH_RC3C_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL
