# Contract D RC4 Prereveal Predictions

These predictions are derived only from the six authorized public authority files. They are frozen before any hidden/reference reveal.

## Public conformance cases

| Case | Predicted outcome | Basis |
|---|---|---|
| `source-audit-positive` | `candidate_for_authorization` | Exact upstream/policy/target/op and explicit `scope=claim` match normalized stored effect. |
| `omitted-request-params-unconstrained` | `candidate_for_authorization` | Stored `scope=object`; absent external params means no parameter constraint. |
| `explicit-request-param-conflict` | `not_applicable` | Explicit external `scope=claim` conflicts with normalized stored `scope=object`. |
| `hold-operation-replay` | `not_applicable` | HOLD is returned only after requested-operation applicability; requested `task.dispatch` conflicts. |
| `hold-positive` | `hold` | Completed HOLD with exact binding and operation match. |
| `target-content-replay` | `not_applicable` | Target immutable content differs despite same logical id. |

## Public valid/invalid corpus

All six public valid fixtures are predicted valid. The three CLEAR fixtures are candidates when exact applicability is supplied; completed HOLD returns `hold` only after exact applicability; failed evaluation returns `evaluation_failed` after upstream/policy/target binding.

All ten public invalid fixtures are predicted `cannot_establish`: actor top-level injection, effect on failure, numeric version, unknown version, unknown evaluation state, unknown disposition, unknown effect type, unknown effect version, unknown effect parameter, and unknown structural field.

## Major mutation classes

- Exact Contract D version mutation: invalid / `cannot_establish`.
- Upstream `kind`, `id`, or `immutable_id`: a valid mutated Decision has a different semantic identity; mismatch against the original expected upstream is `not_applicable`.
- Policy `id` or `version`: a valid mutated Decision has a different semantic identity; mismatch is `not_applicable`.
- Target `kind`, `id`, or `content_sha256`: a valid mutated Decision has a different semantic identity; mismatch is `not_applicable`.
- Evaluation `clear` versus `hold`: both may be valid completed states but have different semantic identity and distinct outcomes after applicability.
- Evaluation `failed`: valid only without disposition/effect; distinct semantic identity and `evaluation_failed` outcome after binding.
- Effect type/version mutation to an unregistered value: invalid / `cannot_establish`.
- Machine-semantic `scope` mutation between `claim` and `object`: valid, changes normalized effect and semantic identity, and may change applicability when explicitly constrained.
- Unknown structural/effect/metadata fields: invalid / `cannot_establish`.

## Unknown/future behavior

Unknown/future contract version, evaluation state, disposition, effect type, effect version, effect parameter, or Contract-D-owned structural field is predicted to fail closed as `cannot_establish`. No unknown value gains current RC4 authority.

## HOLD versus failure

- Completed HOLD is a completed policy conclusion with an effect. It must pass upstream/policy/target, operation, and requested-parameter applicability before returning `hold`.
- Failed evaluation has no disposition/effect. After upstream/policy/target binding succeeds it returns `evaluation_failed`; it is not HOLD.

## Semantic identity invariants

Predicted invariant under removal/mutation of valid metadata `reason_codes`, `explanation`, and finite-JSON `diagnostics`.

Predicted invariant under any change to external Authorization-only context such as actor, approval, delegation, autonomy, profile/trust state, execution permission/state/receipt, because those values are not part of Contract D semantic projection. Injecting such fields into a Contract D-owned structural object is instead invalid unless they are merely data inside opaque finite-JSON diagnostics.

Safe-default equivalents for `knowledge.add_verified_tag@1` are predicted to have one identity: params absent, `{}`, scope absent, and explicit `{"scope":"claim"}`. Explicit `{"scope":"object"}` has a different identity.

## Applicability mismatch predictions

Requested-operation replay, target id/kind/content substitution, upstream kind/id/immutable substitution, policy id/version substitution, and conflicting explicitly requested machine-semantic effect parameters are all predicted `not_applicable` for otherwise valid Decisions.

## Required requested-operation / parameter discriminators

1. HOLD + different requested operation -> `not_applicable`.
2. HOLD + conflicting explicit requested `scope` -> `not_applicable`.
3. HOLD + exact operation and parameter -> `hold`.
4. CLEAR stored normalized `scope=object` + requested params absent -> `candidate_for_authorization`.
5. Same + requested params `{}` -> `candidate_for_authorization`.
6. Same + requested `{"scope":"claim"}` -> `not_applicable`.
7. Same + requested `{"scope":"object"}` -> `candidate_for_authorization`.

Registry defaults are never injected into the external requested-parameter boundary.

## Required finite-JSON discriminators

- Invalid UTF-8 JSON bytes -> ingress rejection / cannot establish RC4 value.
- Duplicate JSON object keys -> ingress rejection.
- JSON tokens `NaN`, `Infinity`, `-Infinity` -> ingress rejection.
- Host-language-only diagnostics value -> decoded-value rejection / `cannot_establish`.
- Non-string decoded object key -> rejection / `cannot_establish`.
- Self-referential decoded list or dict -> cycle rejection / `cannot_establish`.
- Mutually recursive decoded containers -> cycle rejection / `cannot_establish`.
- Shared-but-acyclic decoded containers -> accepted if all leaves are finite JSON; repeated identity alone is not a cycle.

## Canonicalization predictions

Canonical bytes are UTF-8, object-key sorted, compact separators, Unicode not ASCII-escaped, array order preserved, and exactly one trailing newline. Whitespace and object insertion order do not affect canonical bytes. Duplicate-key JSON never reaches canonicalization as an accepted parsed value.

Semantic identity hashes canonical bytes of the normalized authority projection only, not metadata.

## Weak-consumer controls

Each weak consumer below is predicted to be caught by at least one decisive prereveal test:

| Weak consumer | Predicted decisive failure |
|---|---|
| CLEAR/disposition-only | Grants authority to structurally/version-invalid CLEAR. |
| target-id-only | Accepts same logical target id after immutable content substitution. |
| target ignores kind/content | Accepts cross-kind/content replay. |
| HOLD/failure collapse | Returns HOLD for failed evaluation. |
| reason-text effect inference | Lets non-authoritative metadata create authority. |
| unknown-effect acceptance | Grants current authority to future/unregistered effect. |
| policy-blind | Accepts policy id/version substitution. |
| upstream-blind | Accepts upstream substitution. |
| omitted requested params treated as registry-default constraints | Rejects stored `scope=object` even though absent request params impose no constraint. |
| HOLD returned before applicability | Returns HOLD for operation/parameter mismatch. |
| host-language-only diagnostics acceptance | Accepts non-JSON decoded data. |
| cyclic decoded-container acceptance/uncontrolled recursion | Accepts or fails unsafely on cycles instead of fail-closed outcome. |
| Decision identity contaminated by Authorization context | Identity varies with actor/approval/etc. external context. |

## Prereveal ambiguities / defensible choices

1. The public authority defines finite JSON numbers and canonical JSON formatting controls but does not fully specify lexical normalization among semantically similar finite numeric host values such as `1`, `1.0`, exponent spellings, or negative zero. Current authority-bearing RC4 fields and registered machine-semantic params are strings, so this does not alter the tested Decision semantic identity. The independent implementation uses the standard-library JSON encoder for finite decoded numeric values.
2. The public authority specifies exact applicability fields for external expected upstream/policy/target context but does not expressly define whether extra external context keys should be ignored or rejected. The independent consumer requires the external expected binding objects supplied to its API to contain exactly the specified binding keys; malformed external expectation objects return `cannot_establish`.
3. Unknown or malformed external requested-effect-parameter constraints are treated as non-matching (`not_applicable`) rather than as registry-default requests. The decisive required cases are unaffected.

No hidden answer was sought for these choices.
