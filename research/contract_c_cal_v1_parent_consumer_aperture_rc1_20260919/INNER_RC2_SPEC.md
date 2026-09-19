# Contract C Candidate A RC2 public consumer specification

**Status:** Frozen context-free research aperture. This specification defines only the public handoff semantics a downstream consumer is allowed to use. It is not a production Contract C version, Decision policy, Authorization object, or execution permission.

## 1. Consumer boundary

The consumer receives three independent inputs:

1. `raw`: exact bytes of one Contract C Candidate A RC2 object;
2. `contract_b_index`: an exact index for the Contract-B world named by that object;
3. `expected_authority`: out-of-band handoff authority containing the expected research profile, exact producer/policy identities, independently selected policy-resolver identity, and expected whole-object SHA-256.

The object must not select its own external authority merely by containing matching-looking identifiers.

A valid consumer preserves public epistemic/result state. It must not infer destination policy, action permission, Authorization, confidence, score, rank, a unique winner, or requested effect.

## 2. Exact owned shape

Top-level object fields are exactly:

- `profile`
- `result_set_id`
- `contract_b`
- `producer`
- `execution`
- `propositions`

Unknown Contract-C-owned fields are invalid.

### `profile`

Exact value:

`contract-c-successor-candidate-a-rc2-research`

### `contract_b`

Exact fields:

- `contract_version`: non-empty string
- `bundle_id`: non-empty string
- `bundle_hash`: `sha256:` plus 64 lowercase hexadecimal characters

The entire tuple must equal the independently supplied `contract_b_index` tuple.

### `producer`

Exact fields:

- `semantic_implementation_sha`: 40 lowercase hexadecimal characters
- `policy_sha256`: 64 lowercase hexadecimal characters, without `sha256:` prefix
- `policy_resolver_commit_sha`: 40 lowercase hexadecimal characters

All three must equal `expected_authority`. Producer identities embedded in the object are not sufficient authority by themselves.

### result-set `execution`

Exact field `state`, one of:

- `completed`
- `failed`
- `incomplete`

A failed or incomplete result-set has zero proposition records.

### `propositions`

Array of proposition-result records. Proposition IDs must be unique.

Each proposition-result has exactly:

- `proposition`
- `execution`
- `terminal`
- `participants`
- `basis_groups`

#### proposition binding

`proposition` has exactly:

- `proposition_id`: non-empty string
- `content_sha256`: `sha256:` plus 64 lowercase hexadecimal characters

The proposition ID must exist in `contract_b_index.propositions`. The object's `content_sha256` must equal `sha256:` plus the exact unprefixed digest stored for that proposition in the index.

#### proposition execution

`execution` has exactly:

- `state`: `completed | failed | incomplete`
- `completion`: `assessed | not_checkable | null`

Rules:

- `completed` requires `completion` of `assessed` or `not_checkable`;
- `failed` or `incomplete` requires `completion = null`, `terminal = null`, no participants, and no basis groups.

#### terminal

A completed proposition has a terminal object with exactly:

- `verdict`: `supported | contradicted | not_checkable`
- `reason`: exact case-sensitive public reason

Allowed reason values:

- `categorical_support`
- `categorical_refutation`
- `MIXED_RELATIONS`
- `unresolved_categorical_relation`
- `joint_public_cause`
- `no_deciding_relation`
- `UNSUPPORTED_SEMANTIC_FAMILY`

Completion/verdict coherence:

- `assessed` permits only `supported` or `contradicted`;
- `not_checkable` requires verdict `not_checkable`.

Verdict/reason coherence:

- `supported` -> `categorical_support`
- `contradicted` -> `categorical_refutation`
- `not_checkable` -> one of `MIXED_RELATIONS`, `unresolved_categorical_relation`, `joint_public_cause`, `no_deciding_relation`, `UNSUPPORTED_SEMANTIC_FAMILY`

Do not case-fold, alias, or normalize public reasons. In particular, `UNSUPPORTED_SEMANTIC_FAMILY` and `no_deciding_relation` are distinct states even if their participant/basis shape is otherwise identical.

## 3. Participants

Each participant has exactly:

- `evidence_ref`
- `relation`
- `role`

`evidence_ref` has exactly:

- `source_id`
- `passage_id`

Both are non-empty strings. The exact `(source_id, passage_id)` pair must exist in the supplied `contract_b_index.passages`. Duplicate exact participants are invalid.

`relation` is exactly one of:

- `supports`
- `refutes`
- `non_polarized`

`role` is exactly one of:

- `causal`
- `residual`

A consumer must preserve relation and role independently. `non_polarized` is not support, refutation, confidence, or permission.

## 4. Minimal sufficient basis groups

`basis_groups` is an array of zero or more groups. Each represented group:

- is a non-empty array of exact evidence references;
- contains no duplicate member;
- references only retained participants;
- references only participants whose role is `causal`.

Two groups that contain the same member set are duplicate equivalent groups and are invalid even if member order differs.

A represented group must not be a strict superset of another represented group. Such a group is non-minimal and invalid.

The union of all basis-group members must equal exactly the set of participants marked `causal`. No causal participant may be uncovered, and no residual participant may occur in a basis group.

The family of groups is semantic state. Multiple groups are alternative complete minimal sufficient bases. A consumer must retain all of them and must not choose one as a unique winner.

Examples of meaning only:

- `[[S1]]`: one sufficient basis
- `[[S1],[S2]]`: two independent sufficient alternatives
- `[[S1,S2]]`: one jointly sufficient basis
- `[[S1,R1],[S2,R1]]`: two alternative joint bases

The wire uses exact evidence references, not the symbolic names above.

## 5. Terminal causal coherence

For completed propositions:

### supported

- at least one basis group is required;
- every group contains `supports` participants only.

### contradicted

- at least one basis group is required;
- every group contains `refutes` participants only.

### `MIXED_RELATIONS`

- at least one basis group is required;
- every group contains at least one `supports` and at least one `refutes` participant;
- no `non_polarized` participant may occur in a mixed basis group.

### `unresolved_categorical_relation` or `joint_public_cause`

- at least one basis group is required;
- every member of every group is `non_polarized`.

### `no_deciding_relation`

- `basis_groups` is empty;
- every retained participant is `non_polarized / residual`.

### `UNSUPPORTED_SEMANTIC_FAMILY`

- `basis_groups` is empty;
- every retained participant is `non_polarized / residual`.

This structural similarity does not make it synonymous with `no_deciding_relation`. Exact terminal reason remains public semantic state.

## 6. Exact Contract-B reference validation

The supplied Contract-B index contains:

- exact Contract-B version, bundle ID, and bundle hash;
- admitted passage IDs, source IDs, and passage SHA-256 values;
- proposition IDs and exact proposition-content digests.

The consumer validates references against this independently supplied index. Contract C does not duplicate passage content/hash into each participant, so the consumer must not invent or accept an evidence reference absent from the exact bound index.

## 7. Canonical JSON and local identity

Raw handoff bytes are normative canonical bytes.

Parsing requirements:

- UTF-8 JSON;
- reject duplicate object keys;
- reject non-finite JSON numbers/constants;
- exactly one JSON object;
- no trailing non-whitespace data.

Canonical object normalization before serialization:

1. remove top-level `result_set_id` when computing local identity;
2. sort each proposition's `participants` by `(source_id, passage_id)`;
3. sort every basis group's members by `(source_id, passage_id)`;
4. sort basis groups lexicographically by the ordered sequence of `(source_id, passage_id)` members;
5. sort proposition records by `(proposition_id, content_sha256)`;
6. JSON object keys are lexicographically sorted;
7. use compact separators `,` and `:` with no presentation whitespace;
8. preserve Unicode rather than ASCII-escaping it;
9. append exactly one LF byte.

Arrays other than the normalization rules above are not silently rewritten.

`result_set_id` is:

`sha256:` + lowercase SHA-256 of canonical normalized bytes after removing only top-level `result_set_id`.

The received object must contain that exact value.

After restoring the exact `result_set_id`, canonical bytes of the complete object must equal the exact received `raw` bytes. A semantically plausible object in non-canonical byte form is not this exact handoff.

## 8. Independent whole-object authority

`expected_authority.whole_object_sha256` is an independently supplied binding over the exact complete canonical object bytes, including `result_set_id`.

The consumer must verify:

`sha256:` + SHA-256(`raw`) == `expected_authority.whole_object_sha256`

A caller-selected replacement hash is not authority. A coherent semantic deletion followed by recomputation of local `result_set_id` is still a different object and must fail against the original external digest.

## 9. Expected authority

`expected_authority` must bind at least:

- exact profile;
- exact semantic implementation SHA;
- exact policy SHA-256;
- exact independently selected policy-resolver commit SHA;
- exact whole-object SHA-256 for the named handoff.

The object must not self-select a different profile, producer identity, resolver authority, or whole-object digest.

## 10. Successful normalized result

On success, return a deterministic dictionary preserving the public semantic content needed to reconstruct the handoff, including:

- profile and result-set identity;
- exact Contract-B binding;
- exact producer/policy/resolver identity;
- result-set execution state;
- proposition binding and execution state;
- exact terminal verdict/reason;
- all exact participants with relation and role;
- all minimal sufficient basis groups.

The normalized result may use the same shape as the validated object or a smaller deterministic projection that preserves every item above.

It must not add:

- destination threshold or routing;
- `CLEAR`, `HOLD`, or another destination disposition;
- Authorization, actor, delegation, approval, or execution permission;
- confidence, probability, score, rank, or winner;
- requested operation/effect;
- producer-private traces or explanations.

## 11. Required fail-closed classes

The implementation must reject, rather than repair or silently normalize, at least these classes when encountered:

- wrong/unknown profile;
- unknown Contract-C-owned fields;
- malformed or stale `result_set_id`;
- non-canonical raw bytes;
- wrong external whole-object digest;
- wrong Contract-B tuple;
- proposition substitution;
- evidence reference absent from exact Contract B;
- wrong producer/policy/resolver identity;
- duplicate participants;
- duplicate basis member;
- duplicate equivalent basis group;
- unknown basis participant;
- residual participant in basis;
- causal participant omitted from basis-family coverage;
- non-minimal strict-superset basis group;
- relation/terminal incoherence;
- execution/terminal laundering;
- `non_polarized -> supports/refutes` laundering;
- artificial unique-winner deletion of an alternative basis;
- exact reason substitution or case-folding, including `MIXED_RELATIONS` and `UNSUPPORTED_SEMANTIC_FAMILY`;
- destination-policy or Authorization field injection.

The specification does not require one particular error-code vocabulary. It requires fail-closed behavior and preservation of the semantic distinctions above.
