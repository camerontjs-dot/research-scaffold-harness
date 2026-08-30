# Contract D RC3 — Fresh Independent Consumption Reproduction, Successor Run

## Terminal research record

### 1. Isolation identity

- implementation repository: `camerontjs-dot/research-scaffold-harness`
- authorized branch: `research/contract-d-rc3-fresh-reproduction-2`
- clean starting base: `548bfa81f65290eda15af658f647497679b840ef`
- initial ref-only observed target: `548bfa81f65290eda15af658f647497679b840ef`
- initial ref-only verification: **PASS**
- predecessor branch surface opened before freeze: **NO**

### 2. Pre-freeze aperture

Candidate authority repository/ref actually opened before freeze:

`camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`

| Seq | Path | Expected blob | Observed blob |
|---:|---|---|---|
| 1 | `research/contract-d-independent-authority-rc3/candidate/SPEC.md` | `a91a9f171a3b5f3241b5970d7c0415e00f0477d7` | `a91a9f171a3b5f3241b5970d7c0415e00f0477d7` |
| 2 | `research/contract-d-independent-authority-rc3/candidate/schema.json` | `41481aa7941a789534c974ed7b368fddead6ce5a` | `41481aa7941a789534c974ed7b368fddead6ce5a` |
| 3 | `research/contract-d-independent-authority-rc3/candidate/effect-registry.json` | `53df222ca439248a44029e02a662825235db892f` | `53df222ca439248a44029e02a662825235db892f` |
| 4 | `research/contract-d-independent-authority-rc3/candidate/fixtures/valid.json` | `f823936c9945ea551943c40bee1e956faf1d834d` | `f823936c9945ea551943c40bee1e956faf1d834d` |
| 5 | `research/contract-d-independent-authority-rc3/candidate/fixtures/invalid.json` | `06c03ebba98d7fb2a1a9b146152cca7f9f085ab6` | `06c03ebba98d7fb2a1a9b146152cca7f9f085ab6` |
| 6 | `research/contract-d-independent-authority-rc3/candidate/conformance-cases.json` | `229f2898f756f9ca078086cfc99d2a6a2edd2a73` | `229f2898f756f9ca078086cfc99d2a6a2edd2a73` |

The five packet-authorized durable governance files were unavailable through this task aperture. They were not replaced with memory, conversation history, other project attachments, GitHub narrative, or reconstructed text. Execution continued under the narrower aperture because the task packet itself supplied the exact isolation/freeze/reveal protocol needed for validity.

Unexpected answer-bearing tool over-return before freeze: **NONE OBSERVED**.

Denied answer-bearing surfaces opened before freeze: **NONE**.

**NO PRE-FREEZE DENIED MATERIAL OBSERVED**

The complete observable ledger is frozen in `PRE_FREEZE_ACCESS_LOG.md` blob `64a25daa6406faec31265e8bfef8c96aac5f15ae`.

### 3. Independent freeze

- freeze commit: `af15722cc52372e79abb097c587efec5eab5ff13`
- freeze root tree: `4d38222cbd0b2024ca93477a387e97b6d2969095`
- freeze timestamp: `2026-08-30T23:11:20Z`

Frozen identities:

| Frozen artifact | Blob |
|---|---|
| `contract_d.py` | `ce7ba21008c7c557229a028634e614a4c8f3379e` |
| `test_contract_d.py` | `527a6968d5aec6865f54b7c3bd0b9f0ba470f984` |
| `weak_consumers.py` | `7d854ecc31c558fdabdc7565865dc995f2525100` |
| `self_generated_cases.json` | `e558ea0352514892ce02b68ed459357dc696fec4` |
| `PREDICTIONS.md` | `dc0df712558c40b4b19deee015f0deca6c51da5c` |
| `PRE_FREEZE_ACCESS_LOG.md` | `64a25daa6406faec31265e8bfef8c96aac5f15ae` |

Self-generated case identity: `self_generated_cases.json` is the single explicit case-corpus blob `e558ea0352514892ce02b68ed459357dc696fec4`. Programmatic mutations and weak-control cases are additionally frozen in the test/weak-control blobs above. No separate fixture directory was created.

Freeze receipt was added after the freeze, before reveal, without modifying the frozen object.

### 4. Test receipts

Pre-freeze deterministic local command:

`cd /tmp/contract_d_rc3_repro && python -m unittest -v`

Final prereveal result:

- tests run: 12
- failures: 0
- errors: 0
- result: `OK`

Uploaded frozen source/test/case/prediction blobs were verified to equal the locally tested Git blob identities before the access ledger was sealed.

Freeze commit hosted combined statuses: none.

Freeze commit workflow runs: none.

**HOSTED TEST: NOT AVAILABLE ON CLEAN BASE**

Native producer execution command:

`node /tmp/emit_rc3.mjs > /tmp/decision_engine_rc3_native.json`

The locally executed `emit_rc3.mjs` Git blob was `1745b74a61ba1a3321c52f384a166b7d9d3b0e1c`, exactly equal to the authorized Decision Engine producer blob.

Stricter native-consumer rerun command using hard-coded public expected upstream/policy/target/operation/params:

`cd /tmp/contract_d_rc3_repro && python run_native_check.py /tmp/decision_engine_rc3_native.json`

Its output was byte-identical to the preserved first native result.

### 5. Post-freeze reveal

Reveal order:

| Order | Repository | Ref | Path | Expected/observed blob |
|---:|---|---|---|---|
| A1 | `camerontjs-dot/apparatus-contracts` | `b24d06caf944facb970df5129ebdd48c21c25eec` | `research/contract-d-independent-authority-rc3/candidate/contract_d_core.py` | `de46bb146b77fb34e721d16a51423ef83d23e675` |
| A2 | `camerontjs-dot/apparatus-contracts` | `b24d06caf944facb970df5129ebdd48c21c25eec` | `research/contract-d-independent-authority-rc3/candidate/contract_d_validate.py` | `d9d621df1e817adbb5468be25ef65272c457e8cc` |
| A3 | `camerontjs-dot/apparatus-contracts` | `b24d06caf944facb970df5129ebdd48c21c25eec` | `research/contract-d-independent-authority-rc3/candidate/contract_d_consume.py` | `37b03c8bf3be0ee183ab0369c01ec377a5265e69` |
| A4 | `camerontjs-dot/apparatus-contracts` | `b24d06caf944facb970df5129ebdd48c21c25eec` | `research/contract-d-independent-authority-rc3/candidate/tests/test_rc3.py` | `8aeb2aa2dbcb4042e5286a2dc8aee723327bda39` |
| B1 | `camerontjs-dot/decision-engine` | `63b0245b03ea63d0248a5aced83fba6697697598` | `research/contract-d-rc3-producer-conformance/emit.mjs` | `1745b74a61ba1a3321c52f384a166b7d9d3b0e1c` |

Phase C historical diagnosis was **NOT PERFORMED** because it was not needed to explain the decisive Phase A/B evidence.

### 6. Native producer-consumer result

Decisive path:

**Decision Engine -> RC3 -> frozen independent consumer**

No translation, compatibility adapter, shape normalization, field rename, version bridge, effect mapper, or non-contract default injector was used.

Durable raw native output blob: `4dfb4348007a4b9b022d65917b101b9af92ce4ac` (`PHASE_B_NATIVE_OUTPUT.json`).

Durable native result blob: `a4f5a63165eb0aee95849dd91e32782c9870bbe1` (`PHASE_B_NATIVE_RESULTS.json`).

| Native class | Frozen independent outcome | Translation required |
|---|---|---|
| source-audit CLEAR / `knowledge.add_verified_tag@1` | `candidate_for_authorization` | NO |
| citation-use CLEAR / `knowledge.cite_as_evidence@1` | `candidate_for_authorization` | NO |
| task-dispatch CLEAR / `task.dispatch@1` | `candidate_for_authorization` | NO |
| completed HOLD | `hold` | NO |
| evaluation failure | `evaluation_failed` | NO |

The stricter rerun used hard-coded expected authority/policy/target values from the frozen public fixture identities and produced the exact same result bytes as the first native run. Native cross-repository consumption therefore **SUCCEEDED** for the five required classes.

### 7. Complete disagreement table

| Case | Independent result | Reference result | Native producer result where relevant | Authority relevance | Governing published rule | Classification | Unresolved alternative explanation |
|---|---|---|---|---|---|---|---|
| HOLD with exact upstream/policy/target but requested operation `task.dispatch` instead of Decision effect `knowledge.add_verified_tag` | `not_applicable` | `hold` because reference returns HOLD before requested-operation comparison | Native HOLD uses matching operation, so it returns `hold` and does not discriminate this case | High | Requested-operation applicability says external requested operation is compared to registered effect type and a mismatch is non-applicable; HOLD is a completed Decision with an effect | **reference implementation defect under unambiguous published authority** | Reference may encode an intended but unpublished exception making HOLD terminal before effect/request applicability |
| HOLD with exact upstream/policy/target but requested `scope: object` while Decision normalizes `scope: claim` | `not_applicable` | `hold` because reference returns HOLD before param comparison | Native HOLD uses matching/default claim semantics, so it does not discriminate | High | Requested machine-semantic params are compared to normalized effect params; mismatch is non-applicable | **reference implementation defect under unambiguous published authority** | Same possible unpublished HOLD exception |
| CLEAR `knowledge.add_verified_tag@1`, Decision `scope: object`, no requested effect params supplied | `not_applicable`; independent treats omission as request for safe default `claim` | `candidate_for_authorization`; reference treats omission as no parameter constraint and compares only supplied request params | Native source-audit object uses `scope: claim`; both consumers accept it | High | Safe-default rule normalizes the Decision effect; requested-operation section says compare **any requested** params and does not declare an external-request default | **explicit independent implementation defect under published authority** | Broader prereveal interpretation could treat omitted request params as requesting registry defaults, but that behavior was not explicitly granted by the frozen text |
| Invalid UTF-8 raw bytes at independent parser/consumer ingress | uncaught `UnicodeDecodeError` rather than fail-closed Contract-D result/error | reference raw-byte parser maps invalid UTF-8 to `ContractDError("invalid_utf8")` | Native producer emits valid JSON/object content; not exercised | Medium/high for exact parsing | Canonical JSON is UTF-8 and malformed machinery cannot establish RC3 authority | **explicit independent implementation defect** | Reference consumer accepts object values, with raw-byte handling exposed separately by validator module |
| Runtime Decision object whose opaque `metadata.diagnostics` contains a Python `set` | rejected / cannot establish | reference object validator accepts the non-JSON runtime value; semantic projection excludes metadata so consumer can continue | Native JavaScript/JSON producer cannot emit a Python set | Medium valid/invalid boundary | Diagnostics are arbitrary finite **JSON** diagnostic content | **reference implementation defect under unambiguous published authority** | If all object ingress were guaranteed to have passed JSON decoding, this runtime-only shape would be unreachable; the reference nevertheless exposes object-level `Any` validation/consumption |

No other authority-relevant disagreement was found in the bounded published fixture, registry, identity, replay, unknown/future, metadata, or canonicalization behavior examined here.

### 8. Necessary agreements

The independent and reference implementations agree on: exact current version handling; public valid/invalid fixture classes; completed/failed shape; CLEAR/HOLD/failure distinction and identity separation; target kind/id/content binding; upstream kind/id/immutable binding; policy id/version binding; registered effect types/versions; effect-param enum/default normalization on the Decision object; unknown/future fail-closed behavior for published classes; structural unknown-field rejection; metadata non-authority; Authorization-only semantic-identity invariance; canonical sorted compact Unicode-preserving serialization for tested valid JSON; semantic projection excluding metadata; safe-default Decision-effect identity; all six public conformance cases; and the tested replay/substitution matrix.

### 9. Evaluator assurance

| Weak consumer/control | Expected rejection | Observed by frozen evaluator |
|---|---|---|
| CLEAR/disposition-only | reject | REJECTED |
| target-id-only | reject | REJECTED |
| target consumer ignoring kind/content | reject | REJECTED |
| HOLD/failure collapse | reject | REJECTED |
| reason-text effect inference | reject | REJECTED |
| unknown-effect acceptance | reject | REJECTED |
| policy-blind | reject | REJECTED |
| upstream-blind | reject | REJECTED |
| Decision identity contaminated by Authorization context | reject | REJECTED |

No preregistered weak control passed its intended rejection test.

Evaluator weakness nevertheless exists: the frozen decisive suite omitted the case `Decision scope=object + no requested params`, so the intended independent consumer passed the entire frozen suite despite its authority-relevant over-binding of absent external parameters. The suite also omitted invalid UTF-8 ingress. These gaps are preserved; no post-reveal strengthening is counted as prereveal assurance.

### 10. Falsifiers

#### Triggered

- authority-relevant semantic disagreement between frozen independent and reference behavior;
- requested-operation applicability not enforced by the reference for completed HOLD;
- machine-semantic requested parameters ignored by the reference for completed HOLD;
- valid/invalid object-class disagreement for non-JSON diagnostics runtime content;
- external requested-parameter omission semantics disagreement;
- independent malformed UTF-8 fail-closed defect;
- evaluator coverage weakness sufficient to let an authority-relevant independent defect pass the prereveal suite.

#### Not triggered in the evaluated surfaces

- unknown/future Contract D value acquiring current RC3 authority;
- HOLD collapsed with evaluation failure;
- target-id match accepted while target kind/content mismatch is ignored;
- upstream substitution accepted;
- upstream immutable-identity substitution accepted;
- policy or policy-version substitution accepted;
- Authorization context changing Contract D semantic identity;
- reason/explanation text becoming operational authority;
- tested valid-JSON canonicalization disagreement changing semantic identity;
- structural unknown-field acceptance at Contract-D-owned published locations;
- effect-registry type/version disagreement for published RC3 entries;
- Decision safe-default identity disagreement for omitted/empty/explicit `scope: claim`;
- native Decision Engine RC3 object requiring a bespoke translation adapter;
- any preregistered weak consumer passing its intended rejection case.

#### Not evaluated

- historical RC2 compatibility or prior reproduction behavior (Phase C intentionally skipped);
- compatibility with future Contract D/registry versions beyond fail-closed behavior;
- every possible host-language non-JSON runtime value or Unicode/numeric edge case outside the explicit tested/discriminating set;
- production Decision Engine, production Authorization, or production execution paths.

Not evaluated is not counted as passed.

### 11. Terminal state

**Primary disposition: FALSIFIED**

**Secondary label: REFERENCE_IMPLEMENTATION_DEFECT**

Evidence basis: the frozen independent implementation does not agree on all authority-relevant behavior, including external requested-parameter omission and invalid UTF-8 parsing; the frozen evaluator failed to expose at least one of those defects prereveal; and the revealed reference implementation itself conflicts with the published requested-operation/parameter applicability rule for completed HOLD and with the finite-JSON diagnostics boundary. Although native cross-repository consumption succeeds without an adapter for all five required producer classes, the promotion success criterion requires full bounded semantic agreement and adequate evaluator assurance, so the native success is insufficient to overturn the falsifiers.

### 12. Explicit non-claims

This run does **not** establish or authorize:

- production authorization;
- Contract D release or promotion authorization;
- correctness of downstream Authorization machinery;
- correctness or permission of downstream execution;
- correctness of production Decision Engine behavior outside the exact revealed research producer;
- authority claims outside Contract D `0.3.0-rc3` and effect registry version `1` as tested here;
- compatibility with future versions, historical RC2 representations, prior reproduction artifacts, or other untested cross-repository surfaces;
- that the reference implementation is wholly incorrect: most bounded RC3 semantics agree, and the defects identified are specific;
- that native cross-repository conformance failed: it explicitly succeeded for the five required classes without translation.

### 13. Smallest justified next step

Do **not** promote or repair RC3 in place from this run.

The smallest justified next action is a **separately authorized successor candidate** limited to the observed boundary defects/ambiguity pressure: make completed-HOLD requested-operation/parameter applicability explicit and conformant, make omission semantics for external requested effect parameters explicit, and enforce finite-JSON object ingress consistently. If a successor candidate is produced, its independent recoverability must be tested in a new clean-room reproduction; the frozen RC3 implementation here cannot be repaired and re-counted as independent evidence.

### 14. Thread completion

**NEW EXPERIMENT REQUIRED**

No operator decision is required inside this completed RC3 run. A new experiment requires separate authorization.
