# Contract D RC4 Fresh Independent Consumption Reproduction — Final Record

Final-record timestamp: `2026-08-31T01:01:24Z`

## Disposition

**Primary:** `SUPPORTED FOR PROMOTION`

**Secondary:** `INDEPENDENT_REPRODUCTION_SUCCEEDED`

Terminal state: `TERMINAL`

This disposition means the frozen Contract D RC4 public authority was independently recoverable on the tested authority domain, the independent evaluator discriminated the packet-required weak consumers, and the frozen Decision Engine RC4 producer objects were natively consumable without bespoke translation. It does not itself authorize production release or execution.

## Isolation repository / branch / base

- Implementation repository: `camerontjs-dot/research-scaffold-harness`
- Authorized branch: `research/contract-d-rc4-fresh-reproduction-v2`
- Required clean base: `548bfa81f65290eda15af658f647497679b840ef`
- Ref-only preflight surface: `refs/heads/research/contract-d-rc4-fresh-reproduction-v2`
- Ref-only observed commit before any candidate authority access: `548bfa81f65290eda15af658f647497679b840ef`
- Preflight result: PASS, exact equality.

The mandatory access ledger was created before the first allowlisted Contract D candidate file was opened. Because the available GitHub contents write surface materializes a write as a commit, that initialization created tooling commit `9f51301f1a1d8a78d9b766c4a6257476c132d36f` with clean-base parent `548bfa81f65290eda15af658f647497679b840ef`. This was recorded as a deviation before reveal and was not treated as the independent freeze.

## Launch packet identity

- Repository: `camerontjs-dot/apparatus-contracts`
- Ref: `32ccd9e732907645eab93e7653ad2d926b3840df`
- Path: `research/contract-d-independent-authority-rc4-successor-v1/CONTEXT_FREE_LAUNCH_PACKET.md`
- Expected blob: `efc5626aeea61db5d405e87671a5c062a4d7d010`
- Observed blob: `efc5626aeea61db5d405e87671a5c062a4d7d010`
- Result: MATCH.

## Complete pre-freeze aperture

The following were the only material task/authority sources opened before the independent freeze.

| Seq | Repository/surface | Exact path or surface | Exact ref | Expected identity | Observed identity | Result |
|---:|---|---|---|---|---|---|
| 1 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4-successor-v1/CONTEXT_FREE_LAUNCH_PACKET.md` | `32ccd9e732907645eab93e7653ad2d926b3840df` | `efc5626aeea61db5d405e87671a5c062a4d7d010` | `efc5626aeea61db5d405e87671a5c062a4d7d010` | MATCH |
| 2 | `camerontjs-dot/research-scaffold-harness` | `refs/heads/research/contract-d-rc4-fresh-reproduction-v2` ref-only | ref itself | `548bfa81f65290eda15af658f647497679b840ef` | `548bfa81f65290eda15af658f647497679b840ef` | MATCH |
| 3 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4/candidate/SPEC.md` | `fd6923115116b0ced0f9feb5c005099d2e51ea88` | `42a9819651ab41efdb154240eab4f7d808887cd6` | same | MATCH |
| 4 | same | `research/contract-d-independent-authority-rc4/candidate/schema.json` | same | `b17183038b75f3ee00804e63c2d9b8d7da476f2e` | same | MATCH |
| 5 | same | `research/contract-d-independent-authority-rc4/candidate/effect-registry.json` | same | `53df222ca439248a44029e02a662825235db892f` | same | MATCH |
| 6 | same | `research/contract-d-independent-authority-rc4/candidate/fixtures/valid.json` | same | `f40364a4b0a4e02e60fc08f8d0038ad0cb531e58` | same | MATCH |
| 7 | same | `research/contract-d-independent-authority-rc4/candidate/fixtures/invalid.json` | same | `74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc` | same | MATCH |
| 8 | same | `research/contract-d-independent-authority-rc4/candidate/conformance-cases.json` | same | `29825bfa89b2b91bfa9e457c001e2c869a3649a4` | same | MATCH |

`NO PRE-FREEZE DENIED MATERIAL OBSERVED`

No apparatus reference implementation/test, prior Contract D reproduction/result/receipt/packet, Decision Engine producer, repository-wide/code/issue/PR search, workflow/check output, project governance attachment, project-context retrieval, conversation summary, or memory source was opened before the independent freeze.

## Independent freeze

- Freeze commit: `79e94e7f3795472e31620cdbc4279dc399882ed5`
- Freeze tree: `96f7d44fb2a1d82550377322bac7903f029bd91f`

| Frozen artifact | Blob |
|---|---|
| `contract_d_independent.py` | `bf4ea3eb9a5cf379d5923198225fed542cc6345e` |
| `test_independent.py` | `19a9a780b5fe90f9e43f6387f5b639edf13dd541` |
| `weak_consumers.py` | `fdbc9374f842c6f3b8c56e4b681217f3b1cd40cf` |
| `generated_cases.json` | `6ae56233f7a2f9ef4c20c39105187c066659f5da` |
| `PREDICTIONS.md` | `6a52e508574127c9dbaf9924519f3b1deeee9b71` |
| `PRE_FREEZE_ACCESS_LOG.md` | `6b8895d59256d1eeff9c2cb57e720669745538a9` |

Self-generated case/fixture identity: `generated_cases.json` blob `6ae56233f7a2f9ef4c20c39105187c066659f5da`; mutation/metamorphic/replay/cycle/weak-consumer cases are generated deterministically in the frozen test code. No separate fixture directory/tree was created. The enclosing frozen experiment tree is `96f7d44fb2a1d82550377322bac7903f029bd91f`.

Pre-reveal freeze receipt was created additively after the freeze and before reveal:
- path `research/contract-d-rc4-fresh-reproduction-v2/PRE_REVEAL_FREEZE_RECEIPT.md`
- receipt commit `8c3857af2d5b51e8cf35bbc4f7870424657d874e`

After reveal, none of the frozen implementation, test, generated-case, weak-consumer, access-log, or prediction files was modified.

## Frozen local test

Exact frozen command:

`cd /mnt/data/research-scaffold-harness/research/contract-d-rc4-fresh-reproduction-v2 && python3 -m unittest -v`

Immediate pre-freeze result: all 8 frozen parameterized test methods passed; `Ran 8 tests in 0.004s`; `OK`.

The suite covers the public conformance/state cases, all seven requested-operation/parameter discriminators, authority sensitivity, replay/substitution, unknown/future behavior, finite-JSON byte ingress and decoded-host-value cycles/shared acyclic values, canonicalization/identity, metadata and Authorization-context invariance, and every required weak-consumer control.

`HOSTED TEST: NOT REQUESTED BY LAUNCH PACKET`

## Prereveal predictions / preserved ambiguities

`PREDICTIONS.md` was frozen before reference reveal. It explicitly recorded, rather than resolving by hidden-answer lookup:

1. finite-number lexical canonicalization is not fully specified for semantically similar host numeric values; the independent implementation chose the standard-library finite JSON encoder. The frozen reference later made the same choice, and tested canonical bytes agree exactly;
2. the public authority does not expressly define whether unrelated extra keys in the external expected upstream/policy/target container are ignored or rejected; the independent API chose exact expected-container keys;
3. malformed/non-mapping external requested-effect-parameter values are treated by the independent API as nonmatching, never as registry-default constraints.

These preserved edge cases are outside the declared conforming Decision authority and typed requested-parameter domain exercised by the success gate. They are not silently counted as agreement.

## Post-freeze Phase A reveal

All four reference sources were revealed at `camerontjs-dot/apparatus-contracts@fd6923115116b0ced0f9feb5c005099d2e51ea88`, only after the freeze receipt existed, in this exact order:

| Reveal order | Path | Expected blob | Observed blob | Result |
|---:|---|---|---|---|
| 1 | `research/contract-d-independent-authority-rc4/candidate/contract_d_core.py` | `589e3f1c31a21d305402e5750605d25be682a336` | same | MATCH |
| 2 | `research/contract-d-independent-authority-rc4/candidate/contract_d_validate.py` | `d9d621df1e817adbb5468be25ef65272c457e8cc` | same | MATCH |
| 3 | `research/contract-d-independent-authority-rc4/candidate/contract_d_consume.py` | `ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4` | same | MATCH |
| 4 | `research/contract-d-independent-authority-rc4/candidate/tests/test_rc4.py` | `8bece62cc9d4734af0f6ebee75bb39a0221ce397` | same | MATCH |

Exact revealed files were locally reconstituted and independently Git-blob rechecked to those identities before execution.

Frozen reference test command:

`cd /mnt/data/contract_d_phase_a/reference && python3 -m pytest -q tests/test_rc4.py`

Result: `27 passed in 0.08s`.

Phase A was durably recorded before Phase B at:
- path `research/contract-d-rc4-fresh-reproduction-v2/PHASE_A_COMPARISON.md`
- commit `2b129a19b0a93dc268edeccb16310ac185c439c6`

## Phase A authority agreement / disagreement

Post-reveal differential probes produced **72 authority-relevant agreements and 0 authority-relevant disagreements**.

| Authority area | Result | Classification |
|---|---|---|
| exact RC4 version and unknown structural behavior | AGREE | authority agreement |
| public valid/invalid classification | AGREE | authority agreement |
| typed effect registry and effect version/parameter validation | AGREE | authority agreement |
| stored safe-default normalization | AGREE | authority agreement |
| absent/empty external requested params impose no constraints | AGREE | authority agreement |
| explicit requested machine-semantic parameter constraints | AGREE | authority agreement |
| requested-operation binding before CLEAR/HOLD | AGREE | authority agreement |
| completed HOLD versus evaluation failure | AGREE | authority agreement |
| upstream kind/id/immutable-id binding | AGREE | authority agreement |
| policy id/version binding | AGREE | authority agreement |
| target kind/id/content binding | AGREE | authority agreement |
| replay/substitution rejection | AGREE | authority agreement |
| invalid UTF-8, duplicate JSON keys, non-finite JSON tokens | AGREE | authority agreement |
| decoded host-only values, non-string keys, non-finite numbers | AGREE | authority agreement |
| self/mutual decoded-container cycles fail closed | AGREE | authority agreement |
| shared acyclic decoded containers accepted | AGREE | authority agreement |
| tested canonical bytes | AGREE exactly | authority agreement |
| semantic authority projection and identities | AGREE exactly | authority agreement |
| metadata / Authorization-only identity invariance | AGREE | authority agreement |

Five auxiliary out-of-declared-API-domain probes diverged and are preserved in `PHASE_A_COMPARISON.md`: one extra-key external expected-target mapping and four falsy non-mapping `effect_params` values. They were prereveal-predicted as external API-shape ambiguity. Classification: specification underspecification / out-of-declared-API-domain variance, not an authority-relevant RC4 Decision-semantic disagreement. They do not alter Decision validity, canonical bytes, identity, or any outcome for a conforming external expectation using the specified binding fields and `effect_params` as `dict | None`.

No internal architecture, symbol name, incidental error string, or return-envelope formatting difference was counted as an authority disagreement.

## Evaluator assurance / weak controls

The frozen evaluator caught **13/13** required weak-consumer controls. The frozen weak-control test also passes independently after freeze (`Ran 1 test in 0.001s`; `OK`).

| Required weak consumer | Outcome |
|---|---|
| CLEAR/disposition-only | CAUGHT |
| target-id-only | CAUGHT |
| target consumer ignoring kind/content | CAUGHT |
| HOLD/failure collapse | CAUGHT |
| reason-text effect inference | CAUGHT |
| unknown-effect acceptance | CAUGHT |
| policy-blind | CAUGHT |
| upstream-blind | CAUGHT |
| omitted requested params treated as registry-default request constraints | CAUGHT |
| HOLD returned before operation/parameter applicability | CAUGHT |
| host-language-only diagnostics acceptance | CAUGHT |
| cyclic decoded-container acceptance / uncontrolled recursion | CAUGHT |
| Decision identity contaminated by Authorization context | CAUGHT |

No materially weak required consumer passed the decisive frozen evaluator.

## Post-freeze Phase B reveal

Phase B occurred only after `PHASE_A_COMPARISON.md` was durably committed.

- Repository: `camerontjs-dot/decision-engine`
- Commit: `e768cedc891fa0d3280dc55f54b578d149019555`
- Path: `research/contract-d-rc4-producer-conformance/emit.mjs`
- Expected blob: `96d7856493c498080e3e34366654aeebd14db9f4`
- Observed blob: `96d7856493c498080e3e34366654aeebd14db9f4`
- Result: MATCH.

The producer was materialized unchanged and locally Git-blob rechecked to the same identity.

Decisive path:

`Decision Engine -> frozen RC4 object -> frozen independent consumer`

The producer was executed unchanged. Its JSON envelope was parsed only to select each emitted Decision object; each Decision object was supplied unchanged to the frozen independent consumer with its exact emitted upstream/policy/target bindings and corresponding requested operation. No requested parameter constraint was added for this native compatibility gate.

| Native producer Decision | First frozen-consumer result | Required result |
|---|---|---|
| `source-audit-clear` | `candidate_for_authorization` | PASS |
| `citation-use-clear` | `candidate_for_authorization` | PASS |
| `task-dispatch-clear` | `candidate_for_authorization` | PASS |
| `completed-hold` | `hold` | PASS |
| `evaluation-failed` | `evaluation_failed` | PASS |

Translation required: **NO**.

No compatibility adapter, shape normalizer, field rename, version bridge, effect mapper, or default injector was used. Diagnostic translation was not needed and was not performed.

Phase B durable record:
- path `research/contract-d-rc4-fresh-reproduction-v2/PHASE_B_NATIVE_CONFORMANCE.md`
- commit `1cc9db8c9945e8af94da3832856ef36ff22a1294`

## Explicit falsifiers

| Falsifier | Status | Evidence/classification |
|---|---|---|
| unknown/future values gain current authority | NOT TRIGGERED | frozen fail-closed tests and Phase A agreement |
| HOLD collapsed with failure | NOT TRIGGERED | distinct frozen outcomes/identities |
| HOLD returned despite requested-operation mismatch | NOT TRIGGERED | required discriminator returns `not_applicable` |
| HOLD returned despite requested-parameter mismatch | NOT TRIGGERED | required discriminator returns `not_applicable` |
| omitted external requested params converted into registry-default constraints | NOT TRIGGERED | object-scope Decision remains applicable with absent/`{}` request params |
| target kind/id/content replay weakness | NOT TRIGGERED | substitutions rejected |
| upstream substitution accepted | NOT TRIGGERED | substitutions rejected |
| policy id/version substitution accepted | NOT TRIGGERED | substitutions rejected |
| machine-semantic effect parameters ignored | NOT TRIGGERED | explicit scope conflict rejected; scope mutation changes identity |
| Authorization context changes Decision identity | NOT TRIGGERED | invariance demonstrated |
| reason/explanation becomes authority | NOT TRIGGERED | metadata invariance demonstrated |
| canonicalization disagreement changes semantic identity | NOT TRIGGERED | independent/reference canonical bytes and identities agree on tested domain and implementation algorithm |
| invalid UTF-8 fails to fail closed | NOT TRIGGERED | rejected by both implementations |
| duplicate JSON keys accepted | NOT TRIGGERED | rejected by both implementations |
| non-finite/host-only values accepted as Contract D JSON | NOT TRIGGERED | rejected by both implementations |
| cyclic decoded containers accepted/hang/overflow/escape | NOT TRIGGERED | self and mutual cycles fail closed |
| shared acyclic containers rejected merely for repeated identity | NOT TRIGGERED | accepted by both implementations |
| valid/invalid disagreement | NOT TRIGGERED | public corpora and mutation probes agree |
| effect-registry/default disagreement | NOT TRIGGERED | normalized behavior and identities agree |
| native Decision object requires translation | NOT TRIGGERED | five native classes pass directly |
| required weak consumer passes decisive evaluator | NOT TRIGGERED | 13/13 caught |
| public authority admits multiple unresolved authority-relevant interpretations | NOT TRIGGERED in claimed RC4 authority domain | preserved external API-shape edges are outside declared conforming authority/typed parameter domain and were prereveal-recorded |

## Success criterion evaluation

1. Frozen independent implementation agrees with the frozen reference on the tested authority-relevant RC4 semantics, including finite-JSON ingress and decoded-host-value behavior: **YES**.
2. Frozen evaluator meaningfully discriminates every required weak consumer: **YES, 13/13**.
3. No unresolved authority-relevant disagreement remains: **YES** within the packet-defined/tested RC4 authority domain. Preserved external malformed-container/API-shape edges are explicitly outside this claim.
4. Native Decision Engine -> RC4 -> frozen independent consumer succeeds without a bespoke adapter: **YES, 5/5 required classes**.

Therefore the packet's success criterion for `SUPPORTED FOR PROMOTION` is met.

## Explicit non-claims

This experiment does **not** establish or authorize:

- production authorization or production release;
- operational Authorization correctness;
- actor/approval/delegation/autonomy/trust/profile semantics;
- execution permission, execution state, execution receipt, or execution correctness;
- correctness of claims outside the tested Contract D `0.3.0-rc4` authority;
- compatibility with untested producers, consumers, versions, historical objects, or malformed external caller shapes;
- hosted-runner/CI conformance;
- any downstream action merely because a result is `candidate_for_authorization`.

`candidate_for_authorization` remains a Contract D consumer outcome, not Authorization or execution permission.

## Smallest justified next step

Use this frozen record as evidence input to the separate, explicitly authorized promotion/release decision process. No additional Contract D experiment is required by the evidence produced here unless that process chooses to expand the conforming external caller-shape domain beyond the one tested.

`TERMINAL`
