# Phase A — Frozen Apparatus Reference Comparison

This record is post-reveal and additive. It does not modify the independent freeze at `af15722cc52372e79abb097c587efec5eab5ff13`.

## Reveal order and identities

All sources were revealed from `camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`, in the packet-authorized Phase A order:

1. `research/contract-d-independent-authority-rc3/candidate/contract_d_core.py` — expected/observed blob `de46bb146b77fb34e721d16a51423ef83d23e675`
2. `research/contract-d-independent-authority-rc3/candidate/contract_d_validate.py` — expected/observed blob `d9d621df1e817adbb5468be25ef65272c457e8cc`
3. `research/contract-d-independent-authority-rc3/candidate/contract_d_consume.py` — expected/observed blob `37b03c8bf3be0ee183ab0369c01ec377a5265e69`
4. `research/contract-d-independent-authority-rc3/candidate/tests/test_rc3.py` — expected/observed blob `8aeb2aa2dbcb4042e5286a2dc8aee723327bda39`

No frozen independent file was changed after reveal.

## Authority-relevant agreements

The frozen independent implementation and the revealed reference agree on the following bounded RC3 behavior:

- exact `0.3.0-rc3` version acceptance and fail-closed unknown version behavior;
- required top-level/input/policy/target/evaluation structure and unknown-field rejection at Contract-D-owned structural objects;
- completed versus failed evaluation shape;
- CLEAR/HOLD/failure semantic-state distinction and distinct HOLD/failure semantic identities;
- target kind/id/content binding;
- upstream kind/id/immutable identity binding;
- policy id/version binding;
- registered effect type/version validation;
- unknown effect type/version/parameter rejection;
- `knowledge.add_verified_tag@1` `scope` enum and safe Decision-effect default of `claim`;
- semantic projection excluding metadata;
- deterministic canonical serialization rules relevant to normal JSON values;
- safe-default Decision-effect identity equivalence for omitted params, empty params, omitted scope, and explicit `scope: claim`;
- metadata reason/explanation/diagnostic invariance;
- external Authorization-context invariance of Contract D semantic identity;
- all six supplied public conformance cases;
- all supplied public valid/invalid fixture classes;
- required target/upstream/policy replay substitutions;
- the minimum weak-consumer classes exercised by the independent suite are discriminated by its frozen tests.

## Disagreements and discriminating cases

| Case | Frozen independent result | Revealed reference result | Governing published rule | Authority relevance | Classification | Unresolved alternative explanation |
|---|---|---|---|---|---|---|
| Completed HOLD, exact upstream/policy/target, requested operation changed from `knowledge.add_verified_tag` to `task.dispatch` | `not_applicable` | `hold`; reference returns HOLD before requested-operation comparison | SPEC Requested-operation applicability: external requested operation is compared to registered `effect.type`; mismatch is non-applicable. HOLD is completed and carries an effect. | High | **REFERENCE_IMPLEMENTATION_DEFECT** under the unqualified published applicability rule | The reference source may embody an intended but unpublished interpretation that HOLD is a terminal state outcome before effect/request applicability. The frozen public text does not state that exception. |
| Completed HOLD, exact upstream/policy/target, requested `scope: object` while Decision normalizes `scope: claim` | `not_applicable` | `hold`; reference returns HOLD before effect-param comparison | SPEC Requested-operation applicability: requested machine-semantic params are compared to normalized registered effect params; mismatch is non-applicable. | High | **REFERENCE_IMPLEMENTATION_DEFECT** under the same published rule | Same possible unpublished HOLD exception as above. |
| CLEAR `knowledge.add_verified_tag@1` Decision with `scope: object`; caller supplies no requested effect params | `not_applicable`; frozen consumer normalizes omitted request params to default `scope: claim` | `candidate_for_authorization`; reference treats omitted requested params as no parameter constraint and only compares params actually supplied | SPEC says the Decision effect itself receives safe-default normalization, then says the consumer compares **any requested** machine-semantic params to normalized effect params. It does not declare a default for an absent external request constraint. | High | **EXPLICIT INDEPENDENT IMPLEMENTATION DEFECT** | A broader reading could treat omission as requesting registry defaults, but that behavior was a prereveal interpretation added by the independent implementation rather than an explicit rule. The revealed reference resolves the implementation intent in favor of subset matching. |
| Raw invalid UTF-8 bytes supplied to independent parser/consumer surface | uncaught `UnicodeDecodeError`; no `cannot_establish` result | reference parser converts invalid UTF-8 to `ContractDError("invalid_utf8")` | Canonical JSON requires UTF-8; malformed machinery cannot establish RC3 authority. | Medium/high for exact parsing surface | **EXPLICIT INDEPENDENT IMPLEMENTATION DEFECT** | The reference consumer itself accepts an object rather than bytes, but the reference validation module expressly defines the raw-byte parser and fail-closed behavior. |
| Python object with `metadata.diagnostics` containing a `set` (non-JSON runtime value) | rejected / `cannot_establish` | reference object validator accepts it; semantic projection excludes metadata, so reference consumer can proceed | SPEC restricts diagnostics to arbitrary **finite JSON** diagnostic content. A Python set is not JSON. | Medium, valid/invalid object-class boundary | **REFERENCE_IMPLEMENTATION_DEFECT** | If the only supported object ingress were guaranteed to be JSON-decoded values, this runtime-only case would be unreachable. The revealed reference nevertheless exposes object-level `validate`/`consume` surfaces accepting `Any`. |

Observed frozen independent outputs for the first five discrimination cases were executed after reveal without editing the frozen files. Reference outcomes above follow directly from the revealed control flow in the exact verified reference blobs.

## Evaluator assurance after reveal

The frozen evaluator rejected all preregistered required weak controls: CLEAR/disposition-only, target-id-only, target kind/content blind, HOLD/failure collapse, reason-text inference, unknown-effect acceptance, policy-blind, upstream-blind, and Authorization-contaminated identity.

However, the frozen decisive suite did **not** include the discriminating CLEAR case where a Decision has non-default `scope: object` and the caller omits requested effect params. Therefore the intended independent consumer passed its frozen suite despite the authority-relevant external-parameter defect above. The suite also did not test invalid UTF-8 byte ingress. This is an evaluator-coverage weakness and must not be repaired after reveal and retroactively counted as prereveal assurance.

No preregistered weak control unexpectedly passed its intended rejection test.

## Phase A result

Phase A does not establish full independent agreement. At least two authority-relevant defects are present in the frozen independent implementation, and at least two published-rule conflicts are present in the revealed reference implementation. The independent object remains frozen and unchanged.

Phase B native producer testing is still required by the packet and may distinguish native compatibility from apparatus semantic agreement; it cannot erase the Phase A disagreements.
