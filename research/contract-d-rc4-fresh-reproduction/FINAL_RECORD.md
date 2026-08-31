# Contract D RC4 Context-Free Independent Reproduction Final Record

## Terminal disposition

**Primary:** `FALSIFIED`

**Secondary:**

- `INDEPENDENT_REPRODUCTION_SUCCEEDED`
- `REFERENCE_IMPLEMENTATION_DEFECT`

Reason: the public RC4 authority was independently recovered, the prereveal evaluator discriminated every required weak consumer, and native Decision Engine objects were consumed without translation. However, the frozen apparatus reference has an authority-relevant finite-JSON fail-closed defect for cyclic decoded host containers. Therefore this frozen candidate does not satisfy the packet's requirement for agreement on all authority-relevant behavior.

## 1. Isolation preflight

- implementation repository: `camerontjs-dot/research-scaffold-harness`
- branch: `research/contract-d-rc4-fresh-reproduction`
- clean base: `548bfa81f65290eda15af658f647497679b840ef`
- required ref-only surface: `refs/heads/research/contract-d-rc4-fresh-reproduction`
- observed preflight target: `548bfa81f65290eda15af658f647497679b840ef`
- result: **PASS, exact equality**

The preflight used only the Git ref surface. Before the equality result, no branch commit, tree, file, diff, history, PR, or workflow result was inspected.

No prior or sibling Contract D reproduction branch was inspected.

## 2. Immutable launch packet identity

- repository: `camerontjs-dot/apparatus-contracts`
- exact ref: `16182c1c1f8e44116c66eefa30267553a0d59b19`
- exact path: `research/contract-d-independent-authority-rc4/CONTEXT_FREE_LAUNCH_PACKET.md`
- expected blob: `5996e81486534370fca2f7db81f9c6c70a5cd393`
- observed blob: `5996e81486534370fca2f7db81f9c6c70a5cd393`
- identity: **MATCH**

## 3. Complete pre-freeze information aperture

The following were the only external/material authority sources opened before independent freeze.

### Frozen public Contract D authority

Repository/ref for all six files: `camerontjs-dot/apparatus-contracts@ca9302243ed99e69c603d82b3c9abd424a5bb38a`

| Order | Exact path | Expected blob | Observed blob |
|---:|---|---|---|
| 1 | `research/contract-d-independent-authority-rc4/candidate/SPEC.md` | `42a9819651ab41efdb154240eab4f7d808887cd6` | `42a9819651ab41efdb154240eab4f7d808887cd6` |
| 2 | `research/contract-d-independent-authority-rc4/candidate/schema.json` | `b17183038b75f3ee00804e63c2d9b8d7da476f2e` | `b17183038b75f3ee00804e63c2d9b8d7da476f2e` |
| 3 | `research/contract-d-independent-authority-rc4/candidate/effect-registry.json` | `53df222ca439248a44029e02a662825235db892f` | `53df222ca439248a44029e02a662825235db892f` |
| 4 | `research/contract-d-independent-authority-rc4/candidate/fixtures/valid.json` | `f40364a4b0a4e02e60fc08f8d0038ad0cb531e58` | `f40364a4b0a4e02e60fc08f8d0038ad0cb531e58` |
| 5 | `research/contract-d-independent-authority-rc4/candidate/fixtures/invalid.json` | `74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc` | `74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc` |
| 6 | `research/contract-d-independent-authority-rc4/candidate/conformance-cases.json` | `29825bfa89b2b91bfa9e457c001e2c869a3649a4` | `29825bfa89b2b91bfa9e457c001e2c869a3649a4` |

All six identities matched. No replacement search was performed.

### Other aperture facts

- The immutable launch packet and the ref-only preflight result were also recorded in `PRE_FREEZE_ACCESS_LOG.md`.
- Allowed durable governance/protocol files were not opened because validity did not depend on them; the narrower aperture was retained.
- No repository-wide search, GitHub code search, issue/PR search, history, adjacent commit, sibling research directory, prior Contract D material, hidden/reference implementation, Decision Engine producer, workflow result, conversation history, user memory, assistant memory, or web search was used pre-freeze.

Exact contamination statement:

**NO PRE-FREEZE DENIED MATERIAL OBSERVED**

## 4. Independent implementation freeze

- freeze commit: `a34fcccf15b752f0870099d18ee8370aae591b04`
- freeze tree: `8a9ba686ac737f096c8ee37b47eb17972f28b93f`
- freeze Git timestamp: `2026-08-31T00:21:25Z`
- final prereveal test timestamp: `2026-08-31T00:21:39Z`

### Frozen file identities

| Frozen artifact | Blob/tree identity |
|---|---|
| `contract_d_independent.py` | `5c7ac5a4c821a76d6520412d2dade0cfb0c19021` |
| `test_rc4_independent.py` | `d48b8d26b42979750dc6ca9ab705e6d9ad9fc89c` |
| `weak_consumers.py` | `d380e1f96f91c94ec76aa3cd9d573da418cf0055` |
| `PREDICTIONS.md` | `691332aa05f2198cbeb8e5226446c70a26b5cfa1` |
| `PRE_FREEZE_ACCESS_LOG.md` | `b7dd2b2f7a63e5dfa108529ac3e641c41856ff9b` |
| `RUN.md` | `14dc32299eb594bbd4020fe590cfe86349eb4067` |
| `self_generated_cases.json` | `5b65ef441380e616be96c981a3e2ef25f456b283` |
| `self_generated/cases.json` | `5b65ef441380e616be96c981a3e2ef25f456b283` |
| `self_generated/` tree | `f22a4d236db6b7bbcb40d033840a60a8a41d3397` |

The root and directory self-generated case manifests are byte-identical; the directory copy provides an explicit case-corpus tree identity.

After reveal, none of these frozen implementation/test/case/weak-consumer/prediction/access-log files was modified.

## 5. Prereveal tests and evaluator assurance

Environment: `Python 3.13.5`

Exact command from `research/contract-d-rc4-fresh-reproduction/`:

```text
python3 -m unittest -v test_rc4_independent.py
```

Result:

```text
Ran 57 tests in 0.006s

OK
exit=0
```

The suite covered public fixtures and conformance, mutation, metamorphic, replay, substitution, invariance, parser behavior, finite-JSON ingress, canonicalization, semantic identity, authority sensitivity, future/unknown behavior, all twelve required RC4 discriminators, and weak-consumer discrimination.

### Weak-control outcomes

Every required weak consumer was rejected by at least one prereveal decisive case:

| Weak control | Outcome |
|---|---|
| CLEAR/disposition-only | discriminated |
| target-id-only | discriminated |
| target consumer ignoring kind/content | discriminated |
| HOLD/failure collapse | discriminated |
| reason-text effect inference | discriminated |
| unknown-effect acceptance | discriminated |
| policy-blind | discriminated |
| upstream-blind | discriminated |
| omitted requested params converted to registry defaults | discriminated |
| HOLD returned before applicability | discriminated |
| host-language-only diagnostics acceptance | discriminated |
| Decision identity contaminated by Authorization context | discriminated |

Evaluator result: **12/12 required weak controls discriminated**. No required materially weak consumer passed the prereveal decisive gate.

HOSTED TEST: NOT AVAILABLE ON CLEAN BASE. No hosted-runner surface was authorized or exposed inside the permitted clean-base aperture; repository-wide workflows were deliberately not inspected.

## 6. Prereveal prediction preserved

The independent implementation recorded before reveal that registered zero-parameter effects normalize to include `params: {}`. The frozen reference later agreed with this choice. No post-reveal repair was made.

## 7. Post-freeze reveal order and identities

### Phase A: frozen apparatus reference

Repository/ref for all Phase A files: `camerontjs-dot/apparatus-contracts@ca9302243ed99e69c603d82b3c9abd424a5bb38a`

| Reveal order | Exact path | Expected blob | Observed blob |
|---:|---|---|---|
| 1 | `research/contract-d-independent-authority-rc4/candidate/contract_d_core.py` | `ec0922c2821d89f24ca521be88725a92118b0ad9` | `ec0922c2821d89f24ca521be88725a92118b0ad9` |
| 2 | `research/contract-d-independent-authority-rc4/candidate/contract_d_validate.py` | `d9d621df1e817adbb5468be25ef65272c457e8cc` | `d9d621df1e817adbb5468be25ef65272c457e8cc` |
| 3 | `research/contract-d-independent-authority-rc4/candidate/contract_d_consume.py` | `ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4` | `ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4` |
| 4 | `research/contract-d-independent-authority-rc4/candidate/tests/test_rc4.py` | `56db533665f5205452fad77f1e8309fe5eca57be` | `56db533665f5205452fad77f1e8309fe5eca57be` |

All Phase A identities matched.

Reference test command:

```text
python3 -m pytest -q tests/test_rc4.py
```

Reference result:

```text
........................                                                 [100%]
24 passed in 0.07s
```

Additive differential harness result: 57 comparisons, 53 direct agreements, 1 authority-relevant reference defect, and 3 host/API boundary-shape variances.

### Phase B: native Decision Engine producer

Phase B was not opened until `PHASE_A_REFERENCE_COMPARISON.md` had been durably committed.

- repository: `camerontjs-dot/decision-engine`
- commit: `e768cedc891fa0d3280dc55f54b578d149019555`
- path: `research/contract-d-rc4-producer-conformance/emit.mjs`
- expected blob: `96d7856493c498080e3e34366654aeebd14db9f4`
- observed blob: `96d7856493c498080e3e34366654aeebd14db9f4`
- local unchanged-file `git hash-object`: `96d7856493c498080e3e34366654aeebd14db9f4`
- identity: **MATCH**

No older Decision Engine material was opened.

## 8. Native producer-consumer result

Unchanged producer execution:

```text
node emit.mjs > producer_first_stdout.json
producer_exit=0
```

First stdout SHA-256:

`48c169ce0d5d3eb2a75a473f1594864d07b67ad530e22761315d24759f1d66ca`

The producer's emitted Decision objects were selected by case name and supplied directly to frozen independent implementation blob `5c7ac5a4c821a76d6520412d2dade0cfb0c19021` using prereveal public expectation values.

No translation, compatibility adapter, shape normalizer, field rename, version bridge, effect mapper, or default injector was used.

| Native class | Result | Expected | Translation required |
|---|---|---|---|
| source-audit CLEAR | `candidate_for_authorization` | `candidate_for_authorization` | no |
| citation-use CLEAR | `candidate_for_authorization` | `candidate_for_authorization` | no |
| task-dispatch CLEAR | `candidate_for_authorization` | `candidate_for_authorization` | no |
| completed HOLD | `hold` | `hold` | no |
| evaluation failure | `evaluation_failed` | `evaluation_failed` | no |

Native result: **PASS for all five required classes**.

The first producer stdout is preserved as `PHASE_B_PRODUCER_FIRST_STDOUT.json`; the first consumer result is preserved as `PHASE_B_NATIVE_FIRST_RESULT.json`.

No diagnostic translation was required or performed.

## 9. Complete disagreement table

| Case | Frozen independent result | Frozen reference result | Classification | Decision consequence |
|---|---|---|---|---|
| cyclic decoded host container in diagnostics | rejects as non-finite JSON; consumer returns `cannot_establish` | recursive validator escapes with `RecursionError`; consumer does not produce Contract D outcome | **reference implementation defect under explicit authority** | **authority-relevant**; finite-JSON fail-closed behavior differs |
| external expected target contains extra key but required target binding values match | `not_applicable` | `candidate_for_authorization` | external boundary shape variance | not counted as Contract D Decision semantic disagreement because the public authority specifies compared binding fields but no host expectation-envelope schema |
| external requested-parameter host value is `[]` | `not_applicable` | `candidate_for_authorization` because falsy host value is treated as absent | external boundary shape variance | malformed host binding input outside declared mapping/absence boundary; not counted as Decision authority disagreement |
| explicit host API `None` for requested params | `not_applicable`; independent uses omission as absence sentinel | `candidate_for_authorization`; reference uses `None` as absence sentinel | host API representation variance | language-binding sentinel difference; authority rule for absence and `{}` still agrees |

All other differential cases compared in Phase A agreed on authority behavior and, where applicable, exact semantic identity.

### Authority-relevant defect rationale

The public authority requires every accepted Contract D value, including diagnostics, to be genuine **finite** JSON data. A cyclic decoded host container is not finite JSON. It must fail closed. The frozen independent implementation detects the cycle and returns `cannot_establish`; the frozen reference descends recursively without cycle detection and escapes with `RecursionError` because its consumer catches only its Contract D error type.

This disagreement is resolved in classification, not repaired: `REFERENCE_IMPLEMENTATION_DEFECT`.

## 10. Falsifier ledger

| Packet falsifier | Status | Evidence |
|---|---|---|
| unknown/future values gain authority | NOT TRIGGERED | unknown contract/evaluation/disposition/effect/version/parameter/structural values fail closed |
| HOLD collapsed with failure | NOT TRIGGERED | distinct identities and outcomes |
| HOLD returned despite requested-operation mismatch | NOT TRIGGERED | mismatch -> `not_applicable` |
| HOLD returned despite requested-parameter mismatch | NOT TRIGGERED | mismatch -> `not_applicable` |
| omitted external requested params silently converted to registry defaults | NOT TRIGGERED | object-scope Decision remains applicable for absent and `{}` |
| target id/kind/content replay weakness | NOT TRIGGERED | substitutions -> `not_applicable` |
| upstream substitution accepted | NOT TRIGGERED | substitutions -> `not_applicable` |
| policy id/version substitution accepted | NOT TRIGGERED | substitutions -> `not_applicable` |
| machine-semantic effect parameters ignored | NOT TRIGGERED | `scope` conflict -> `not_applicable`; mutation changes semantic identity |
| Authorization context changes Decision identity | NOT TRIGGERED | identity invariant; Decision-field injection invalid |
| reason/explanation becomes authority | NOT TRIGGERED | metadata mutations identity/applicability invariant |
| canonicalization disagreement changes semantic identity | NOT TRIGGERED | independent/reference canonical bytes and identities agree on tested finite JSON |
| invalid UTF-8 does not fail closed | NOT TRIGGERED | both reject |
| duplicate keys accepted | NOT TRIGGERED | both reject |
| non-finite ordinary JSON/host-only values accepted | NOT TRIGGERED | both reject NaN/Infinity, set, and non-string decoded keys |
| valid/invalid or fail-closed disagreement | **TRIGGERED** | cyclic decoded host container: independent returns `cannot_establish`; frozen reference escapes `RecursionError` |
| effect registry/default disagreement | NOT TRIGGERED | normalization/default identities agree |
| native object requires translation | NOT TRIGGERED | all five native classes consume directly |
| weak consumer passes decisive evaluator | NOT TRIGGERED | 12/12 required weak controls discriminated |
| public authority admits multiple unresolved authority-relevant interpretations | NOT TRIGGERED | prereveal zero-param projection question agreed with reference; observed host-envelope variances are outside Decision authority and do not alter tested native path |

Additional finite-JSON observation: the triggered cyclic-container case is a fail-closed implementation defect, not acceptance of the cyclic value as valid Contract D JSON.

## 11. Success-criterion assessment

1. Frozen independent implementation recovered the explicit public RC4 authority semantics across the declared public and adversarial surface: **YES**.
2. Evaluator meaningfully discriminates weak consumers: **YES, 12/12 required controls**.
3. No unresolved authority-relevant disagreement remains: **classification is resolved**, but an authority-relevant frozen reference defect remains present in the candidate.
4. Native Decision Engine -> RC4 -> frozen independent consumer succeeds without bespoke adapter: **YES, 5/5**.

Because the objective requires agreement on all authority-relevant behavior of the frozen candidate, the present reference defect prevents `SUPPORTED FOR PROMOTION` for this immutable RC4 candidate.

## 12. Disposition

**Primary: `FALSIFIED`**

**Secondary labels:**

- `INDEPENDENT_REPRODUCTION_SUCCEEDED`
- `REFERENCE_IMPLEMENTATION_DEFECT`

Not applied:

- `CROSS_REPOSITORY_CONFORMANCE_FAILED` - native cross-repository conformance succeeded.
- `CONTRACT_AUTHORITY_STILL_UNDERSPECIFIED` - no unresolved Decision-authority ambiguity was established.
- `CONTAMINATED` - no pre-freeze denied material was observed.
- `BLOCKED` - the authorized experiment completed.

## 13. Explicit non-claims

This experiment does **not** establish or authorize:

- production authorization;
- production release or promotion;
- release authorization;
- correctness of any Authorization layer, actor/approval/delegation/autonomy policy, trust/profile state, or operational permission;
- execution correctness, execution safety, execution state, or execution receipts;
- correctness of claims outside the tested Contract D RC4 authority;
- compatibility with untested producers, consumers, versions, language bindings, malformed external host API envelopes, or other untested surfaces;
- reinterpretation of upstream epistemic authority.

`candidate_for_authorization` remains only the Contract D consumer outcome defined by the candidate; it is not Authorization or execution permission.

## 14. Smallest justified next step

Freeze a **new immutable candidate** whose reference finite-JSON validator detects cyclic decoded containers and fails closed through the Contract D error/outcome path, then run a **new context-free independent reproduction** from a clean authorized successor surface. Do not patch this frozen reference in place or count a repaired post-reveal implementation from this run as independent agreement.

**NEW EXPERIMENT REQUIRED**
