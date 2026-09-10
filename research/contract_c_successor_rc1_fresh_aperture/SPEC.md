# Contract C successor RC1 — public clean-room specification

**Status:** research-only clean-room specification. This document does not define a canonical production Contract C version, authorize release, or assign SemVer.

## 1. Purpose

The object defined here is an immutable, decision-agnostic representation of producer-attributable epistemic/result state for a downstream consumer. It is exactly bound to its Contract-B evidence world and producer/policy identity.

It is not an operational authorization object, destination policy object, generic reasoning trace, telemetry dump, or replacement for Contract B.

The exact research wire sentinel is:

`research-contract-c-successor-rc1`

A consumer expecting another Contract C version must reject these bytes rather than translating, downgrading, relabeling, deleting, or coercing fields.

## 2. Relationship to the supplied machine schema

`schema.json` defines the exact structural vocabulary. This specification adds semantic, identity, canonicalization, and reference-integrity rules that JSON Schema alone cannot express.

Unknown Contract-C-owned fields are invalid. `producer.policy.canonical` is the one intentionally opaque JSON object. Its content is not interpreted by Contract C, but its exact canonical bytes are hash-bound.

## 3. Top-level object

Required top-level fields are exactly:

- `contract_c_version`
- `input`
- `producer`
- `execution`
- `propositions`
- `result_set_id`

`contract_c_version` must equal the research sentinel exactly.

A completed result set must contain at least one proposition. Proposition IDs must be unique within a result set.

## 4. Contract-B binding

`input.contract_b` contains exactly:

- non-empty `contract_version`
- non-empty `bundle_id`
- `bundle_hash` matching `sha256:<64 lowercase hex>`

When a Contract-B index is supplied to validation, all three fields must equal the index exactly.

The index shape is:

```json
{
  "contract_version": "...",
  "bundle_id": "...",
  "bundle_hash": "sha256:...",
  "propositions": {"<proposition_id>": "<64 lowercase hex text sha256>"},
  "passages": {
    "<passage_id>": {
      "source_id": "...",
      "passage_sha256": "sha256:<64 lowercase hex>"
    }
  }
}
```

Every proposition in Contract C must exist in the supplied index and its `text_sha256` must match. Every retained contribution evidence reference must resolve by `passage_id`; both `source_id` and `passage_sha256` must match the indexed passage exactly.

The index is validation input, not embedded evidence payload.

## 5. Producer and policy identity

`producer.semantic_implementation_sha` is exactly 40 lowercase hex characters.

`producer.policy` contains:

- `canonical`: opaque JSON object
- `sha256`: exactly 64 lowercase hex characters

The policy hash must equal lowercase SHA-256 of the deterministic Contract-C canonical bytes of `producer.policy.canonical`.

No human-readable policy name is an identity substitute.

## 6. Proposition binding

Each proposition record has:

```json
{"proposition_id":"...","text_sha256":"<64 lowercase hex>"}
```

The proposition ID is non-empty. When a Contract-B index is supplied, the ID and text hash must bind exactly as described above.

## 7. Retained contributions and the neutral channel

Each retained contribution contains exactly:

- `contribution_id`: `contribution:<64 lowercase hex>`
- `channel`: one of `support`, `counterevidence`, `non_deciding`
- `evidence_ref` with non-empty `source_id`, non-empty `passage_id`, and `passage_sha256` matching `sha256:<64 lowercase hex>`

Contribution IDs must be unique within a proposition.

`non_deciding` is a non-polarized retained evidence contribution. It means the referenced evidence participated in producer-attributable epistemic/result state without being classified as support or counterevidence. It is not a synonym for either polarized channel and must not be converted to one.

A `non_deciding` contribution follows the same exact evidence-reference, basis-membership, residual-classification, whole-object identity, and canonicalization rules as any other retained contribution.

This contract does not assign downstream action, utility, materiality, routing, or authorization meaning to any contribution channel.

## 8. Measurement receipt

`measurement` is either `null` or an object containing exactly:

- non-empty `kind`
- `value`: finite JSON number or `null`
- non-empty `basis_contribution_ids`: unique contribution IDs

Every measurement basis contribution ID must reference a retained contribution in the same proposition.

A measurement is recorded producer-attributable state. It does not confer downstream threshold or policy meaning.

## 9. Assessment-stage state

Each proposition always contains exactly four generic assessment slots:

- `eligibility`
- `semantic_validity`
- `aperture_completeness`
- `temporal_applicability`

Each slot is exactly one of:

- `{"state":"not_performed"}`
- `{"state":"performed","value":"unknown"}`
- `{"state":"performed","value":"adverse"}`
- `{"state":"not_applicable"}`
- `{"state":"failed"}`

Missing slots are invalid. These states must not be inferred from one another.

## 10. Proposition and result execution

Result-set `execution.state` is one of `completed`, `failed`, `incomplete`.

Proposition execution is exactly one of:

- `{"state":"completed","completion":"assessed"}`
- `{"state":"completed","completion":"not_checkable"}`
- `{"state":"failed"}`
- `{"state":"incomplete"}`

A failed or incomplete proposition must have `conclusion: null`.

A completed proposition must have a non-null conclusion.

A completed `not_checkable` proposition must report verdict `not_checkable`.

A completed `assessed` proposition must not report verdict `not_checkable`.

Execution state is distinct from subject-matter verdict.

## 11. Conclusion, classification, basis, and causal multiplicity

A completed proposition conclusion contains exactly:

- non-empty `reported_verdict`
- non-empty `terminal_branch`
- `causal_form`
- `basis_members`
- `residual_contribution_ids`
- `rule_roles`

`causal_form` is one of:

- `single_necessary`
- `independent_sufficient_alternatives`
- `jointly_sufficient`
- `redundant_non_deciding`

Basis members are unique `(namespace,id)` pairs. Namespace is one of `contribution`, `rule`, `state`.

Namespace prefixes are mandatory:

- contribution basis IDs: `contribution:<64 lowercase hex>`
- rule basis IDs: begin `rule-role:`
- state basis IDs: begin `state:`

Causal cardinality:

- `single_necessary` requires exactly one basis member.
- `independent_sufficient_alternatives` requires at least two basis members.
- `jointly_sufficient` requires at least two basis members.
- `redundant_non_deciding` requires zero basis members.

For contribution classification:

1. Every contribution-namespaced basis member must reference a retained contribution in the same proposition.
2. Every `residual_contribution_id` must reference a retained contribution in the same proposition.
3. Residual contribution IDs are unique.
4. A contribution cannot be both causal basis and residual.
5. Every retained contribution must be classified exactly once as causal basis or residual.

These rules apply equally to `support`, `counterevidence`, and `non_deciding` contributions. Neutral contributions may therefore be causal, residual, or appear in separate propositions with different roles, as dictated by the recorded result state.

## 12. Rule roles

Each rule role has exactly:

- `rule_id` beginning `rule-role:`
- non-empty `code`
- `terminal_role`: `causal` or `residual`

Rule IDs must be unique within the conclusion.

A rule-namespaced causal basis member must have a matching declared rule role marked `causal`.

A rule role marked `residual` must not appear in the causal basis.

## 13. Deterministic JSON parsing and canonicalization

Input must be UTF-8 JSON. Duplicate JSON object keys are invalid. Non-finite JSON numbers are invalid.

Normative canonical bytes are:

1. UTF-8 JSON;
2. object keys sorted lexicographically at every object level;
3. compact separators with no presentation whitespace;
4. Unicode preserved rather than ASCII-escaped;
5. finite JSON numbers only;
6. exactly one trailing LF (`\n`).

Array order is part of canonical byte identity. The validator does not silently sort arrays.

An otherwise semantically valid object whose received bytes differ from its normative canonical bytes is invalid.

## 14. Content-derived result-set identity

`result_set_id` is:

`result-set:` + lowercase SHA-256 of the normative canonical bytes after removing only the top-level `result_set_id` field.

The claimed result-set ID must equal the recomputed identity.

## 15. External whole-object identity

Whole-object binding is separate from internal validation.

When `expected_sha256` is supplied, it may be either 64 lowercase hex characters or `sha256:<64 lowercase hex>`. After removing an optional `sha256:` prefix, it must be exactly 64 lowercase hex characters.

The lowercase SHA-256 of the exact received bytes must equal the supplied expected digest. A structurally coherent object with recomputed internal identities is still a different immutable object and must fail if its exact bytes do not match the authorized external digest.

## 16. Exact validation layers

A conforming validator must be able to enforce, without hidden producer knowledge:

- external whole-object SHA-256 when requested;
- UTF-8 and duplicate-key rejection;
- canonical byte form;
- exact machine-schema vocabulary and unknown-field behavior;
- proposition/result-set execution rules;
- unique proposition/contribution/rule/basis/residual identities as specified;
- contribution classification completeness and disjointness;
- causal-form cardinality;
- measurement reference integrity;
- rule-role reference integrity;
- result-set identity;
- producer policy hash;
- exact Contract-B binding/proposition/evidence reference integrity when an index is supplied.

## 17. Exact-version and no-downgrade rule

This research successor is a distinct exact-version authority surface. It is not Contract C 1.0.0.

A system expecting Contract C 1.0.0 must reject this object rather than:

- relabel `non_deciding` as `support` or `counterevidence`;
- drop neutral contributions and repair basis/residual state;
- rewrite only the version field;
- infer that a structurally similar object is a 1.0 object.

Likewise, a validator for this research successor must require its own exact research sentinel. Validator selection is an external boundary decision; the artifact's self-declared version does not authorize a different validator.

## 18. Required public implementation interface

Create `research/contract_c_successor_rc1_fresh/contract_c_successor.py` exposing at least:

```python
def canonical_bytes(value: dict) -> bytes:
    ...

def result_set_identity(value: dict) -> str:
    ...

def validate_contract_c_bytes(
    raw: bytes,
    *,
    expected_sha256: str | None = None,
    contract_b_index: dict | None = None,
) -> list[str]:
    ...
```

An empty list means valid. Any invalidity must produce at least one error string. Exact error wording is not normative.

You may add private helpers or public convenience functions, but no adapter may change the artifact before validation.

## 19. Scope limits

This specification establishes no CAL semantic algorithm, no source retrieval behavior, no proposition decomposition, no Decision Engine policy, no root composition, and no operational authorization semantics.

It specifies only the bounded Contract C successor representation/validation surface above.
