# Frozen Predictions

Status: **pre-reference-reveal prediction record**

These predictions are committed with the independent implementation and may not be edited after reference reveal.

## Semantic predictions

1. The candidate Contract D semantics can be reconstructed without Decision Engine implementation access.
2. Exact JSON nesting is not recoverable as a normative semantic requirement from the frozen research authority. A representation difference alone should therefore be classified as representation-only, not automatically as a semantic defect.
3. Contract D must bind:
   - contract/schema version;
   - exact upstream authority kind and id;
   - exact Decision policy id and version;
   - target kind/id plus immutable target content identity;
   - explicit evaluation state;
   - disposition only when evaluation completed;
   - typed/versioned machine-semantic effect and its machine parameters.
4. Completed `HOLD` and evaluation failure are semantically distinct.
5. A generic `CLEAR` or `eligible` state without typed effect/operation binding is insufficient for downstream Authorization.
6. Contract D itself must not carry actor authorization, requested-operation authorization, approval, autonomy/delegation, execution permission, execution success, or execution receipt authority.
7. Authorization-only changes may alter Authorization outcome but must not alter Contract D bytes or semantic identity.
8. Reason codes, explanation, and diagnostics are explanatory/audit metadata and do not alter downstream Authorization unless their meaning is explicitly promoted into a typed machine-semantic effect parameter.
9. Unknown future effect types and effect versions must not be treated as known authority. A consumer may parse them structurally but must fail closed for Authorization.
10. Some immutable target content/version identity is semantically required. This implementation uses `content_hash`.
11. A separately stored Decision id is semantically redundant when a deterministic semantic hash is available, though a stored id may be validated as a convenience integrity check.

## Representation and canonicalization predictions

The independent implementation chooses one conventional representation because the frozen research authority leaves representation underdetermined.

- Structured JSON envelope.
- UTF-8.
- Object keys sorted recursively by JSON serialization.
- Compact separators.
- Non-finite numbers rejected.
- One trailing newline.
- Semantic identity is SHA-256 over the canonical **normative semantic projection**, not over explanatory metadata or a stored `decision_id`.

Prediction: exact byte-for-byte canonicalization rules are under-specified by the public Contract D research authority. If the reference uses another deterministic representation/canonicalization while preserving the same semantic partition, classify that disagreement as specification ambiguity and/or representation-only variance rather than silently changing the frozen implementation.

## Unknown-field prediction

For this exact research contract version, the independent representation rejects unknown structural fields. This is a chosen fail-closed serialization rule, not a recovered universal Contract D semantic requirement. Unknown effect type/version is different: it remains structurally representable and fails closed at Authorization.

## Evaluation-failure representation prediction

This implementation represents `evaluation_state = failed` without `disposition` or `effect`. The semantic requirement is only that failure be distinguishable from a completed policy conclusion. If reference artifacts represent a typed failure payload or retain non-authoritative diagnostics, that may be representation variance unless it changes the authority boundary.

## Known-effect test registry

The test registry is research-only vocabulary, not a proposed Contract D registry:

| Effect | Version | Requested operation | Machine semantics |
| --- | ---: | --- | --- |
| `knowledge.tag` | 1 | `knowledge.apply_tag` | required `tag=audited_verified` |
| `citation.use` | 1 | `citation.use` | optional `scope`, default `same_target` |
| `task.dispatch` | 1 | `task.dispatch` | required `dispatch_class` |

## Expected terminal evidence interpretation

- If frozen independent semantics match reference semantics but bytes/nesting differ: `CONTRACT_D_SEMANTICS_REPRODUCED_WITH_REPRESENTATION_VARIANCE`.
- If an authority-relevant behavior cannot be derived without reference implementation knowledge: `SPECIFICATION_AMBIGUITY_FOUND` or `INDEPENDENT_REPRODUCTION_FAILED`, depending on severity.
- If downstream Authorization requires Decision Engine or Contract C reinterpretation, or Contract D itself confers execution authority: `CONTRACT_D_HYPOTHESIS_FALSIFIED`.
- No successful outcome automatically authorizes promotion.
