# CONTEXT-FREE REQUIRED

You are the independent oracle reviewer for CAL RC5A security-class / diagnostic-separation verification.

This is an evaluator-qualification review, not an implementation task. Do not implement a verifier and do not inspect any candidate implementation, reference implementation, weak control, qualification output, RC5 post-reveal result, prior conversations, memory, web search, or surrounding repository material.

## Authorized inputs only

Read exactly these public RC5A authority files at frozen aperture commit:

`3c8d87efd63d215a76264f2232d687ba979b05f3`

- `research/cal_rc5a_security_diagnostic_aperture/SPEC.md`
  - Git blob `8a48ee1417495f79a775eff5d6085f8ecddd9a47`
- `research/cal_rc5a_security_diagnostic_aperture/WIRE-SCHEMA.json`
  - Git blob `1626e7358ae260a9d0b7e45785cb217429140bc4`
- `research/cal_rc5a_security_diagnostic_aperture/PUBLIC-KEYS.json`
  - Git blob `8d94b9daf1eb77291fb83b100358b617d4a60325`
- `research/cal_rc5a_security_diagnostic_aperture/TRUST-POLICY.json`
  - Git blob `eea849acccb344e185402d5a69dc684582696e98`
- `research/cal_rc5a_security_diagnostic_aperture/PUBLIC-POSITIVE-VECTORS.json`
  - Git blob `babbd96c632e23db6a56d8ff1630e50cb5d5875c`

Then read exactly this hidden-case programme by exact file/blob-scoped retrieval from the supervisor branch:

- branch: `research/cal-rc5a-security-diagnostic-supervisor-20260906`
- path: `research/cal_rc5a_security_diagnostic_supervisor/HIDDEN-CASE-PROGRAM.json`
- Git blob: `0ef8049ddf60af9570d69f42ca88c00e285eadc6`

Do not inspect the supervisor commit, tree, PR, directory listing, evaluator code, reference code, weak controls, or qualification result.

## Review objective

Independently determine whether every hidden case's `expected_failure_class` is uniquely supported by the public RC5A specification and its normative stage precedence.

Also review every declared `transport_variant_of` relation. Confirm whether the two cases preserve the same parsed object/underlying defect such that RC5A requires the same implementation-local `(diagnostic_stage, diagnostic_code)` tuple.

Do NOT require or infer any exact diagnostic token.

For each case return:
- `case_id`
- `declared_expected_failure_class`
- `reviewed_expected_failure_class`
- `status`: `AGREE`, `DISAGREE`, or `UNDERDETERMINED`
- concise `basis`

For each transport relation return:
- variant case id
- base case id
- `status`: `AGREE`, `DISAGREE`, or `UNDERDETERMINED`
- concise `basis`

## Materiality rule

Any `DISAGREE` or `UNDERDETERMINED` on a normative expected class is material and blocks evaluator seal.

Any `DISAGREE` or `UNDERDETERMINED` on a transport diagnostic-stability relation is material and blocks evaluator seal.

Do not repair or reinterpret the public spec or hidden cases during review.

## Output

Return one JSON object:

```json
{
  "profile": "CAL.RC5A/independent-oracle-review.v1",
  "aperture_commit": "3c8d87efd63d215a76264f2232d687ba979b05f3",
  "hidden_case_blob": "0ef8049ddf60af9570d69f42ca88c00e285eadc6",
  "contamination_status": "CLEAN" | "CONTAMINATED",
  "case_reviews": [],
  "transport_relation_reviews": [],
  "counts": {
    "agree": 0,
    "disagree": 0,
    "underdetermined": 0
  },
  "oracle_disposition": "QUALIFIED" | "INCONCLUSIVE_MATERIAL_ORACLE_DISAGREEMENT" | "INCONCLUSIVE_CONTAMINATION"
}
```

`QUALIFIED` is allowed only if contamination is clean and every normative case and transport relation is `AGREE`.

Stop after producing the review. No implementation, evaluator modification, seal, merge, promotion, tag, or release is authorized.
