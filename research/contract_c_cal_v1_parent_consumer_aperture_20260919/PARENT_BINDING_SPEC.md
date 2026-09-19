# Contract C CAL V1 parent-recomposition public binding specification

**Status:** Context-free research aperture. This is a public consumer specification for the bounded RC0 handoff only. It is not a production Contract C release, Decision policy, Authorization object, or execution permission.

The outer object wraps one Candidate A RC2 result set. The nested RC2 object is governed by `INNER_RC2_SPEC.md`, except that its exact bytes are embedded within the outer canonical object rather than supplied as a separate transport object.

## 1. Consumer inputs

The consumer receives five independent inputs:

1. `raw`: exact UTF-8 bytes of one outer Contract C parent-bound handoff;
2. `contract_b_index`: exact Contract-B world/index authority for the nested RC2 result;
3. `expected_authority`: independently selected immutable authority constants and expected outer whole-object SHA-256;
4. `contract_a_decomposition`: exact upstream root/decomposition declaration;
5. `native_child_results`: mapping from child proposition ID to exact native CAL result.json bytes.

The object must not self-select or replace any of those external inputs.

## 2. Exact outer shape

Top-level fields are exactly:

- `profile`
- `result_set_id`
- `rc2_result`
- `recomposition`

Exact `profile`:

`contract-c-cal-v1-parent-recomposition-rc0`

`rc2_result` is one nested Candidate A RC2 object governed by `INNER_RC2_SPEC.md`.

## 3. Exact producer/freeze authority

The nested RC2 producer must equal the independently supplied constants in `expected_authority`.

For this frozen aperture the required constants are also listed in `AUTHORITIES.json`:

- frozen CAL V1 commit;
- qualified CAL semantic-source commit;
- CAL semantic implementation identity;
- RC2 public profile;
- CAL policy SHA-256;
- independently selected policy-resolver commit.

The outer `recomposition.cal_freeze_commit` and `cal_semantic_source_commit` must equal the corresponding independently supplied values.

## 4. Recompositon object

`recomposition` has exactly:

- `cal_freeze_commit`
- `cal_semantic_source_commit`
- `root`
- `decomposition_id`
- `operator`
- `ordered_children`
- `decomposition_receipt_id`
- `parent_conclusion`

### Root

`root` has exactly:

- `proposition_id`
- `text_sha256`

The pair must equal the exact root in `contract_a_decomposition`.

### Declaration

For RC0:

- `contract_a_decomposition.state` is exactly `declared`;
- `decomposition_id` is a nonblank exact match to the upstream declaration;
- `operator` is exactly `all_of`;
- there are at least two declared children;
- child sequences are exactly contiguous `1..N`;
- child proposition IDs are unique;
- no child equals the root;
- each child `(proposition_id, text_sha256, sequence)` exactly matches the upstream declaration.

## 5. Ordered child binding

Each `ordered_children` entry has exactly:

- `sequence`
- `proposition_id`
- `text_sha256`
- `contract_c_content_sha256`
- `native_result_sha256`
- `cal_result_id`
- `conclusion`

Required checks:

1. the set of outer child proposition IDs equals exactly the nested RC2 proposition set;
2. the outer child sequence/text binding equals the exact Contract-A declaration;
3. `contract_c_content_sha256` equals the matching nested RC2 proposition `content_sha256`;
4. `contract_c_content_sha256` also equals `sha256:` + the exact native CAL result field `proposition.proposition_sha256`;
5. `native_result_sha256` equals `sha256:` + SHA-256 of the exact raw native child result bytes supplied independently;
6. the native child result's `proposition.proposition_id` equals the declared child;
7. the native child result's `proposition.text_sha256` equals the declared child's exact tagged text SHA-256;
8. the native child result's `result.conclusion` is exactly one of `supported | contradicted | not_checkable` and equals the outer child `conclusion`;
9. the matching nested RC2 terminal verdict equals that same child conclusion.

Do not infer a different conclusion from evidence. The native CAL result is the producer artifact under verification.

## 6. Child result identity

For each child construct this exact material object:

```json
{
  "proposition_id": "<exact child id>",
  "text_sha256": "sha256:<64 lowercase hex>",
  "audit_result_sha256": "sha256:<SHA-256 of exact native result bytes>",
  "conclusion": "supported | contradicted | not_checkable"
}
```

Canonical child-identity bytes are UTF-8 JSON with:

- object keys lexicographically sorted;
- compact separators `,` and `:`;
- Unicode preserved, not ASCII-escaped;
- **no trailing LF**.

Then:

`cal_result_id = "cal-child-result:" + lowercase_sha256(canonical_child_identity_bytes)`

The supplied outer `cal_result_id` must equal the derived value.

Opaque strings, caller-selected aliases, private codecs, and structurally valid but differently derived IDs are invalid.

No child result ID may be reused.

## 7. Parent conclusion

For declared `all_of`, use only the exact child conclusions already verified above:

1. if any child is `contradicted`, parent is `contradicted`;
2. otherwise, if every child is `supported`, parent is `supported`;
3. otherwise, parent is `not_checkable`.

The supplied `parent_conclusion` must equal the derived value.

This is recomposition only. It does not re-audit child evidence.

## 8. Decomposition receipt identity

Construct this exact receipt material:

```json
{
  "root_proposition_id": "<root id>",
  "root_text_sha256": "sha256:<root text hash>",
  "decomposition_state": "declared",
  "decomposition_id": "<exact upstream id>",
  "operator": "all_of",
  "ordered_children": [
    {
      "proposition_id": "<child id>",
      "text_sha256": "sha256:<child text hash>",
      "result_id": "cal-child-result:<64 lowercase hex>",
      "conclusion": "supported | contradicted | not_checkable"
    }
  ],
  "root_result_id": null,
  "parent_conclusion": "supported | contradicted | not_checkable"
}
```

The `ordered_children` array is in exact semantic sequence `1..N`. Do not sort it by proposition ID.

Canonical receipt bytes use the same no-LF JSON rule as child identity: sorted object keys, compact separators, Unicode preserved.

`decomposition_receipt_id = lowercase_sha256(canonical_receipt_bytes)`

The supplied outer receipt ID must equal the derived value.

## 9. Outer local identity and canonical bytes

The outer transport is canonical JSON.

Parsing must reject duplicate object keys, non-finite constants, trailing non-whitespace data, and non-object top-level values.

To compute outer `result_set_id`:

1. remove only top-level `result_set_id`;
2. sort `recomposition.ordered_children` by numeric `sequence`;
3. leave the nested RC2 object intact except for the normalization already required by its own public specification;
4. serialize the complete outer object with lexicographically sorted object keys, compact separators, Unicode preserved;
5. append exactly one LF byte;
6. prefix the lowercase SHA-256 with `sha256:`.

The received `result_set_id` must equal that value.

After restoring `result_set_id`, canonical serialization of the complete outer object must equal the exact received `raw` bytes.

A reversed wire array with unchanged explicit sequence is semantically canonicalized by sequence. A changed explicit sequence is a semantic mutation and must fail against upstream authority.

## 10. Independent whole-object authority

`expected_authority.whole_object_sha256` is independently selected.

Verify:

`sha256:` + SHA-256(exact complete canonical outer raw bytes)

equals that expected value.

A coherent reseal after changing a child, receipt, root, parent conclusion, nested RC2 value, or other owned field is a different object and must fail against the original external authority even if local identities are recomputed.

## 11. Required fail-closed families

The consumer must reject at least:

- wrong outer profile or unknown outer field;
- wrong frozen CAL/source identity;
- malformed/stale outer result-set identity;
- noncanonical outer bytes;
- wrong external whole-object digest;
- invalid nested RC2 object;
- wrong Contract-B world/reference;
- wrong producer/policy/resolver authority;
- missing, extra, duplicate, or reordered-semantic child;
- child text or proposition substitution;
- native child-result byte/hash substitution;
- child conclusion mismatch;
- stale/wrong/private-codec/reused `cal_result_id`;
- cross-run child replay;
- nested RC2 child-content substitution;
- stale/wrong decomposition receipt;
- wrong parent conclusion;
- coherent semantic reseal against fixed authority;
- destination-policy, Decision, Authorization, actor, approval, delegation, requested-effect, or execution field injection.

## 12. Successful result

Return a deterministic projection preserving:

- nested RC2 public epistemic/result state;
- exact root/decomposition identity;
- ordered child proposition/text/content/native-result/result-id/conclusion bindings;
- verified decomposition receipt identity;
- verified parent conclusion;
- exact local and whole-object identities.

Do not add operational semantics.
