# Contract D RC4 Prereveal Predictions

Status: frozen prereveal predictions derived only from the six public authority files identified in `PRE_FREEZE_ACCESS_LOG.md`.

No incidental reference error strings are predicted.

## Public conformance cases

| Case | Predicted outcome |
|---|---|
| source-audit-positive | `candidate_for_authorization` |
| omitted-request-params-unconstrained | `candidate_for_authorization` |
| explicit-request-param-conflict | `not_applicable` |
| hold-operation-replay | `not_applicable` |
| hold-positive | `hold` |
| target-content-replay | `not_applicable` |

## Positive/state controls

- Source-audit CLEAR: valid; normalized `scope=claim`; exact applicability returns `candidate_for_authorization`.
- Citation-use CLEAR: valid; exact applicability returns `candidate_for_authorization`.
- Task-dispatch CLEAR: valid; exact applicability returns `candidate_for_authorization`.
- Completed HOLD: valid completed Decision; exact applicability returns `hold`.
- Evaluation failure: valid failed Decision with no disposition/effect; matching upstream/policy/target returns `evaluation_failed`.
- HOLD and failure remain distinct in validation, projection, semantic identity, and consumer outcome.

## Authority sensitivity predictions

| Mutation | Validity | Semantic identity | Applicability against original expected context |
|---|---|---|---|
| Contract D version to any non-exact value | invalid | no RC4 identity | `cannot_establish` |
| upstream kind | valid if non-empty string | changes | `not_applicable` |
| upstream id | valid if non-empty string | changes | `not_applicable` |
| upstream immutable id | valid if non-empty string | changes | `not_applicable` |
| policy id | valid if non-empty string | changes | `not_applicable` |
| policy version | valid if non-empty string | changes | `not_applicable` |
| target kind | valid if non-empty string | changes | `not_applicable` |
| target id | valid if non-empty string | changes | `not_applicable` |
| target immutable content hash | valid if exact hash syntax | changes | `not_applicable` |
| completed state changed to failed with failed shape | valid | changes | `evaluation_failed` after binding checks |
| unknown evaluation state | invalid | no RC4 identity | `cannot_establish` |
| clear to hold or hold to clear disposition | valid | changes | exact applicability changes terminal completed outcome |
| unknown disposition | invalid | no RC4 identity | `cannot_establish` |
| registered effect type changed to another registered type | valid only if its parameter schema is satisfied | changes | old requested operation becomes `not_applicable` |
| unknown effect type | invalid | no RC4 identity | `cannot_establish` |
| unknown effect version | invalid | no RC4 identity | `cannot_establish` |
| `knowledge.add_verified_tag@1.scope` claim to object or object to claim | valid | changes | explicit conflicting requested scope becomes `not_applicable` |
| unknown effect parameter | invalid | no RC4 identity | `cannot_establish` |

## RC4 discriminator predictions

1. Completed HOLD, matching upstream/policy/target, different requested operation -> `not_applicable`.
2. Completed HOLD, conflicting explicit requested effect parameter -> `not_applicable`.
3. Completed HOLD, exact operation/parameter applicability -> `hold`.
4. CLEAR normalized to `{"scope":"object"}`, requested params absent -> `candidate_for_authorization`.
5. Same CLEAR, requested params `{}` -> `candidate_for_authorization`.
6. Same CLEAR, explicit requested `{"scope":"claim"}` -> `not_applicable`.
7. Same CLEAR, explicit requested `{"scope":"object"}` -> `candidate_for_authorization`.
8. Invalid UTF-8 JSON bytes -> fail closed / `cannot_establish`.
9. Duplicate JSON object keys -> fail closed / `cannot_establish`.
10. `NaN`, `Infinity`, `-Infinity`, or other non-finite JSON numbers -> fail closed / `cannot_establish`.
11. Host-language-only value inside diagnostics on an already-decoded object -> invalid / `cannot_establish`.
12. Non-string object key on an already-decoded object -> invalid / `cannot_establish`.

## Normalization and canonicalization

- `knowledge.add_verified_tag@1` with omitted `params`, `{}`, omitted `scope`, or explicit `scope=claim` normalizes to one effect and one semantic identity.
- Explicit `scope=object` is authority-bearing and changes semantic identity from `scope=claim`.
- Canonical bytes are UTF-8, sorted-key, compact JSON, Unicode-preserving, array-order-preserving, finite-number-only, with exactly one trailing newline.
- Transport key order and whitespace do not change semantic identity after parsing/normalization.
- Duplicate-key transport never reaches canonicalization as accepted Contract D data.

### Recorded prereveal interpretation

For registered effects whose parameter schema is empty, the independent implementation normalizes the effect to include `params: {}`. This is the most deterministic reading of “normalized registered effect.” The public authority explicitly establishes equivalence of omitted/empty/defaulted parameters for `knowledge.add_verified_tag@1`, but does not separately spell out the serialized normalized shape for zero-parameter effects. If the frozen reference uses a different zero-parameter projection shape and that changes semantic identity, do not repair the independent implementation; classify whether the evidence shows specification underspecification or an implementation defect under stronger explicit authority.

## Identity and authority invariance

- Removing or changing metadata reason codes, explanation, or diagnostics does not change semantic identity or applicability.
- Authorization-only context such as actor, approval, delegation, autonomy, profile/trust state, execution permission/state/receipt is external and does not change Decision semantic identity.
- Injecting Authorization-only fields into Contract-D-owned structural objects is invalid because unknown fields fail closed.
- Failed Decisions project no effect.

## Replay/substitution predictions

- Reusing an effect for a different requested operation -> `not_applicable`.
- Target id substitution -> `not_applicable`.
- Target kind substitution -> `not_applicable`.
- Target immutable content substitution -> `not_applicable`.
- Upstream kind/id/immutable-id substitution -> `not_applicable`.
- Policy id/version substitution -> `not_applicable`.

## Future/unknown predictions

Unknown contract versions, evaluation states, dispositions, effect types, effect versions, effect parameters, and structural fields never gain current authority. They fail validation and consume as `cannot_establish`.

An unknown external requested parameter is merely an unsatisfied external constraint for an otherwise valid Decision, therefore predicts `not_applicable`, not new authority.

## Weak-consumer controls

The decisive evaluator must reject every required weak class:

- CLEAR/disposition-only: caught by requested-operation mismatch.
- target-id-only: caught by target-content substitution.
- target consumer ignoring kind/content: caught by target-kind substitution.
- HOLD/failure collapse: caught by exact HOLD control.
- reason-text effect inference: caught by failed Decision whose metadata text names an effect.
- unknown-effect acceptance: caught by unknown effect type/version case.
- policy-blind: caught by policy-version substitution.
- upstream-blind: caught by upstream immutable-id substitution.
- omitted requested params treated as registry defaults: caught by object-scope Decision with omitted requested params.
- HOLD returned before operation/parameter applicability: caught by HOLD operation replay.
- host-language-only diagnostics accepted: caught by decoded diagnostics containing a host-only value.
- Decision identity contaminated by Authorization context: caught by comparing the same Decision under two Authorization contexts.

Prediction: all weak controls must fail at least one decisive gate case. If any passes the same decisive gate, record evaluator weakness.

## Pre-reveal contamination statement

NO PRE-FREEZE DENIED MATERIAL OBSERVED at prediction freeze time.
