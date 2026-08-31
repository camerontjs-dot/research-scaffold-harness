# Contract D RC4 Phase A Reference Comparison

This record was created after the independent freeze and before any Decision Engine RC4 producer reveal. No frozen implementation, test, case, weak-consumer, access-log, or prediction file was modified.

## Independent freeze under comparison

- freeze commit: `a34fcccf15b752f0870099d18ee8370aae591b04`
- freeze tree: `8a9ba686ac737f096c8ee37b47eb17972f28b93f`
- prereveal suite: 57 tests passed, exit 0
- prereveal contamination statement: `NO PRE-FREEZE DENIED MATERIAL OBSERVED`

## Reveal order and verified identities

All files were revealed only at `camerontjs-dot/apparatus-contracts@ca9302243ed99e69c603d82b3c9abd424a5bb38a`, in the packet-required order:

| Order | Path | Expected blob | Observed blob | Identity |
|---:|---|---|---|---|
| 1 | `research/contract-d-independent-authority-rc4/candidate/contract_d_core.py` | `ec0922c2821d89f24ca521be88725a92118b0ad9` | `ec0922c2821d89f24ca521be88725a92118b0ad9` | MATCH |
| 2 | `research/contract-d-independent-authority-rc4/candidate/contract_d_validate.py` | `d9d621df1e817adbb5468be25ef65272c457e8cc` | `d9d621df1e817adbb5468be25ef65272c457e8cc` | MATCH |
| 3 | `research/contract-d-independent-authority-rc4/candidate/contract_d_consume.py` | `ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4` | `ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4` | MATCH |
| 4 | `research/contract-d-independent-authority-rc4/candidate/tests/test_rc4.py` | `56db533665f5205452fad77f1e8309fe5eca57be` | `56db533665f5205452fad77f1e8309fe5eca57be` | MATCH |

## Reference suite execution

The revealed reference files were staged unchanged with the already-opened frozen public registry/fixture/conformance files.

Command:

```text
python3 -m pytest -q tests/test_rc4.py
```

Result:

```text
........................                                                 [100%]
24 passed in 0.07s
```

## Differential comparison

An additive post-reveal differential harness compared the frozen independent implementation to the frozen reference over 57 checks.

Summary:

- 53 direct agreements
- 1 authority-relevant reference implementation defect candidate, classified below
- 3 host/API boundary-shape variances, classified below as non-authority or unspecified host binding behavior

### Direct authority agreements

The independent and reference implementations agree on:

- validity of every frozen public valid fixture;
- rejection of every frozen public invalid fixture;
- exact semantic identity for all six valid fixtures;
- all six public conformance-case outcomes;
- source-audit CLEAR, citation-use CLEAR, task-dispatch CLEAR;
- completed HOLD distinct from evaluation failure;
- HOLD operation mismatch -> `not_applicable`;
- HOLD requested-parameter conflict -> `not_applicable`;
- exact HOLD applicability -> `hold`;
- object-scope CLEAR with requested params absent -> `candidate_for_authorization`;
- object-scope CLEAR with requested params `{}` -> `candidate_for_authorization`;
- object-scope CLEAR with explicit `scope=claim` -> `not_applicable`;
- object-scope CLEAR with explicit `scope=object` -> `candidate_for_authorization`;
- invalid UTF-8 rejection;
- duplicate-key rejection;
- non-finite JSON-number rejection;
- host-language-only diagnostics rejection for ordinary non-JSON values;
- non-string decoded object-key rejection;
- safe-default normalization and identity equivalence;
- metadata identity invariance;
- Unicode-preserving sorted compact canonical bytes with one trailing newline;
- upstream kind/id/immutable-id mutation behavior;
- policy id/version mutation behavior;
- target kind/id/content mutation behavior;
- disposition mutation behavior;
- machine-semantic effect-parameter mutation behavior.

The prereveal interpretation that zero-parameter registered effects normalize to include `params: {}` agrees with the frozen reference.

## Preserved disagreements / variances

| Case | Frozen independent | Frozen reference | Classification | Authority relevance |
|---|---|---|---|---|
| cyclic decoded host container in diagnostics | rejects as non-finite JSON and consumer returns `cannot_establish` | recursive validator escapes with `RecursionError` | **reference implementation defect under explicit authority** | **authority-relevant**: public authority requires every accepted Contract D value to be genuine finite JSON and invalid objects to fail closed |
| extra key in external expected target object while the required target binding values match | `not_applicable` because independent host API requires exact expectation-object keys | ignores extra expectation key and returns `candidate_for_authorization` | external boundary shape variance | not a Decision-object semantic disagreement; public authority specifies the compared binding fields but does not define a host-language expectation-envelope schema |
| external requested-parameter host value `[]` | `not_applicable` | falsy host value is treated as no constraints and returns `candidate_for_authorization` | external boundary shape variance | malformed host binding input outside the declared mapping/absence boundary; not counted as Decision authority agreement/disagreement |
| explicit host API `None` for requested params | `not_applicable`; omission is the independent API's absence sentinel | `None` is the reference API's absence sentinel and returns `candidate_for_authorization` | host API representation variance | language-binding sentinel difference, not the authority rule that absence and `{}` impose no constraints |

### Reference finite-JSON defect detail

The public authority states that every accepted Contract D value must be genuine finite JSON data. A cyclic host container is not finite JSON. The independent validator detects cycles and fails closed. The reference `_json_value` recursively descends lists/dicts without cycle detection, so a cyclic decoded object escapes as `RecursionError`; the reference consumer catches only `ContractDError`, therefore it does not return the specified `cannot_establish` outcome.

This is not an independent implementation defect and is not repaired after reveal. It is classified as `REFERENCE_IMPLEMENTATION_DEFECT` under explicit public authority.

## Evaluator assurance

The prereveal independent evaluator rejected every required weak-consumer class:

1. CLEAR/disposition-only
2. target-id-only
3. target consumer ignoring kind/content
4. HOLD/failure collapse
5. reason-text effect inference
6. unknown-effect acceptance
7. policy-blind
8. upstream-blind
9. omitted requested params converted to registry defaults
10. HOLD returned before operation/parameter applicability
11. host-language-only diagnostics acceptance
12. Decision identity contaminated by Authorization context

Result: **12/12 required weak controls discriminated**. No materially weak required control passed the prereveal decisive gate.

The frozen reference test file itself exercises a narrower weak-control sample, but it is not being substituted for the prereveal independent evaluator.

## Phase A conclusion

- Public RC4 authority was independently recovered with matching authority semantics across the declared fixture/conformance/discriminator surface.
- The frozen reference contains one authority-relevant finite-JSON failure mode for cyclic decoded containers.
- The three additional observed variances concern host/API envelope representation not specified as Contract D Decision authority.
- Because Phase A comparison is now durably captured, Phase B native producer reveal is authorized by the launch packet.
