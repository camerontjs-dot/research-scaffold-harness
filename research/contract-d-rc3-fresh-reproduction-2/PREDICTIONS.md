# Contract D RC3 Independent Predictions

Status: PRE-REVEAL. These predictions are frozen from the public RC3 authority only.

## Selected interpretations where ordering/normalization could otherwise be read more than one way

1. Registered effect normalization always materializes a `params` object in the semantic authority projection. Thus zero-parameter effects normalize to `params: {}` whether `params` was omitted or explicitly empty.
2. The declared `knowledge.add_verified_tag@1` safe default applies to both the Decision effect and the external requested machine-semantic parameter comparison. Omitted/empty requested params therefore normalize to `scope: "claim"`.
3. Applicability ordering is: validate exact RC3 machinery; compare expected upstream authority, policy, and target; then distinguish failed versus completed state. For completed decisions, compare requested operation and normalized machine-semantic params before returning `hold` or `candidate_for_authorization`. For failed decisions there is no effect, so requested operation/params are not compared after the upstream/policy/target boundary matches.
4. Consequently, a HOLD or failed Decision replayed against a different upstream authority, policy, or target is `not_applicable`, not `hold`/`evaluation_failed`.

These choices will not be tuned after reference reveal.

## Supplied public conformance cases

| Case | Prediction |
|---|---|
| source-audit-positive | `candidate_for_authorization` |
| target-kind-replay | `not_applicable` |
| target-content-replay | `not_applicable` |
| policy-version-replay | `not_applicable` |
| upstream-kind-replay | `not_applicable` |
| operation-replay | `not_applicable` |

## Supplied valid fixture/state predictions

| Fixture/class | Prediction |
|---|---|
| source-audit / `knowledge.add_verified_tag@1` CLEAR | valid; exact match => `candidate_for_authorization` |
| citation-use / `knowledge.cite_as_evidence@1` CLEAR | valid; exact match => `candidate_for_authorization` |
| task-dispatch / `task.dispatch@1` CLEAR | valid; exact match => `candidate_for_authorization` |
| completed HOLD | valid and semantically distinct from failure; exact match => `hold` |
| evaluation failure | valid with no disposition/effect; exact upstream/policy/target => `evaluation_failed` |

## Supplied invalid fixture predictions

All supplied invalid fixtures are predicted to fail exact RC3 establishment and yield `cannot_establish` through the consumer: top-level actor injection, policy approval injection, effect on failed evaluation, top-level execution receipt injection, numeric Contract D version, numeric effect version, unknown Contract D version, unknown disposition, unknown effect parameter, unknown effect type, and unknown effect version.

## Authority sensitivity predictions

Mutating any Decision authority-bearing value to another otherwise-valid current value changes semantic Decision identity. This includes upstream authority kind/id/immutable identity, policy id/version, target kind/id/content hash, completed disposition, effect type/version where the replacement remains registered/valid, and every machine-semantic effect parameter (`scope` in RC3). An unknown/future value instead prevents current RC3 identity from being established.

Expected applicability mismatches for an unchanged Decision are `not_applicable` when the external expected upstream authority, policy, target, requested operation, or requested normalized effect params differ.

## Authority invariance predictions

Changes to `metadata.reason_codes`, `metadata.explanation`, or `metadata.diagnostics`, including Authorization-looking data inside opaque diagnostics, do not change semantic Decision identity or applicability. Removing metadata also leaves both unchanged.

External actor, profile/trust posture, approval, delegation, autonomy, and operational context are outside Contract D. Changing them without changing the Decision cannot change its semantic identity.

## Future/unknown/injection predictions

Unknown Contract D version, evaluation state, disposition, effect type, effect version, effect parameter, or structural field cannot inherit RC3 authority and yields `cannot_establish`.

Actor, requested operation, approval, delegation, autonomy, execution permission, execution state, and execution receipt injected at plausible Contract-D-owned structural locations are unknown structural fields and fail exact RC3 establishment. The same shapes inside `metadata.diagnostics` remain non-authoritative diagnostics.

## Canonicalization and identity predictions

Lexicographic top-level and nested object key ordering, compact separators, UTF-8 with Unicode preserved, finite JSON numbers, one trailing newline, and array order preservation determine canonical serialization. Insignificant source formatting/whitespace does not affect parsed canonical bytes. Duplicate JSON keys are invalid.

Semantic identity hashes canonical bytes of the normalized authority projection, not canonical transport bytes of the whole Decision. Metadata is excluded. Safe-default normalization causes omitted/empty/explicit `scope: "claim"` variants to share one semantic identity.

## Weak-consumer predictions

The independent evaluator is expected to reject each intentionally weak control:

- CLEAR/disposition-only: rejected by target/policy/upstream/effect replay cases.
- target-id-only: rejected by target kind/content substitution.
- target consumer ignoring kind/content: rejected by target kind/content substitution.
- HOLD/failure collapse: rejected by explicit state distinction.
- reason-text effect inference: rejected by diagnostic/explanation text that mentions another operation.
- unknown-effect acceptance: rejected by future effect type/version cases.
- policy-blind: rejected by policy id/version substitution.
- upstream-blind: rejected by upstream kind/id/immutable substitution.
- Decision identity contaminated by Authorization context: rejected because external Authorization changes must not alter Contract D semantic identity.

If any materially weak control nevertheless satisfies the decisive gate, evaluator assurance is predicted inadequate and the broader result may be INCONCLUSIVE.
