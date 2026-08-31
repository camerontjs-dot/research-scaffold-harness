# Contract D RC5 Fresh Independent Consumption Reproduction v1 — Final Record

## Terminal scientific disposition

- Primary scientific disposition: `INCONCLUSIVE`
- Independent-reproduction status: `INDEPENDENT_REPRODUCTION_INCONCLUSIVE`
- Terminal state: `TERMINAL`

The frozen independent implementation reproduces the frozen RC5 reference on 101 of 103 authority-relevant differential comparisons. The two remaining authority-relevant non-agreements are both the same prereveal uncertainty: whether a registered effect with an empty parameter schema contributes an explicit empty `params` object to the normalized semantic authority projection. The public authority specifies a normalized registered effect but does not explicitly resolve the representational presence or absence of an empty normalized `params` object. Because this changes normative `semantic_identity`, the difference cannot be ignored; because the public authority does not clearly choose one representation, it is classified as `PUBLIC_AUTHORITY_AMBIGUITY`, not a clearly incorrect independent implementation. This prevents both `SUPPORTED FOR PROMOTION` and a justified `FALSIFIED` disposition for this frozen reproduction.

## Verified clean base and isolation

Execution repository: `camerontjs-dot/research-scaffold-harness`

Branch: `research/contract-d-rc5-fresh-reproduction-v1`

Verified initial clean base:

- commit: `548bfa81f65290eda15af658f647497679b840ef`
- tree: `191976638bbf8b7153e3f2c94945a2f15cd640ad`
- recursive path-name check at the clean base contained no `contract-d` implementation/reproduction material.

Contamination status: `NON_ANSWER_BEARING_METADATA_EXPOSURE_ONLY`.

During clean-base verification, a branch-list fallback exposed only names and opaque head SHAs of prior Contract D reproduction branches. No prior implementation, tests, results, reports, expected outputs, or semantic conclusions were opened. This exposure was recorded prereveal and was not used to choose architecture, behavior, expected outputs, or repairs.

The prereveal candidate-subtree posture is not retroactively treated as contamination: the reproduction relied on the launch-packet-pinned subtree identity while independently verifying every allowed public authority blob. The post-freeze reveal packet explicitly instructs that this deliberate aperture choice not be reclassified as contamination.

## Immutable independent freeze

Immutable prereveal freeze:

- freeze commit: `54c78823e289a3d0d490189d1ffafc25d127d585`
- freeze tree: `6a691a691ed56c95616bae1595137daf1a96b86f`
- implementation: `research/contract-d-rc5-fresh-reproduction-v1/contract_d_rc5.js`
- implementation blob: `e60d3a15da98e32a732f1860808b8dda7ba7f3ee`
- prereveal tests: `research/contract-d-rc5-fresh-reproduction-v1/test_contract_d_rc5.js`
- prereveal test blob: `102327e348364c62454369d2614ca98ce80d94c5`
- prereveal result: `24 passed, 0 failed, 0 skipped, 0 cancelled, 0 todo`
- prereveal runtime: Node.js `v22.16.0`
- durable freeze receipt commit: `45115f39b5d07e20fed44c6765a5953593fb5678`

Before reveal and again immediately before this terminal record, both live-branch frozen files were re-verified to have exactly the same blob identities. Neither frozen independent file was modified after reference behavior was observed.

## Frozen public authority

Frozen candidate repository: `camerontjs-dot/apparatus-contracts`

Frozen candidate commit: `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`

Packet-pinned candidate subtree: `f5db874db39c0c3bf863f4ba2cc1a3597369f3bf`

Research token: `0.3.0-rc5`

The six public authority blobs used prereveal were independently verified exactly:

- `SPEC.md`: `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`
- `schema.json`: `fe4e74464a53f581d52baed02257dd9452e6bfe3`
- `effect-registry.json`: `53df222ca439248a44029e02a662825235db892f`
- `fixtures/valid.json`: `f03b16f41f119a8a485e0f7ac3dac30f509c40b9`
- `fixtures/invalid.json`: `8c3fd3370d7f96a7cb162d8acfeacb7b189b4d86`
- `conformance-cases.json`: `29825bfa89b2b91bfa9e457c001e2c869a3649a4`

## Post-freeze reveal authorization

Reveal packet:

- repository: `camerontjs-dot/apparatus-contracts`
- commit: `48a46db987b6ce3079abe28f83be6c8396aa2353`
- path: `research/contract-d-independent-authority-rc5/POST_FREEZE_REVEAL_PACKET.md`
- verified packet blob: `a403c343631f60144f87ddf1efb984afa60d1ca3`

No reference behavior was read until the immutable implementation/test blobs had been re-verified.

## Revealed reference identities

All newly authorized files were fetched only at exact candidate commit `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8` and matched the packet-pinned blobs:

- `contract_d_core.py`: `6c3fbe3e6ac6effe0a4ed66f17145ffd32705edf`
- `contract_d_validate.py`: `8cc6d81515d7c5b0a86df163a38d1c12931f897f`
- `contract_d_consume.py`: `42536aaac5acd953f150a87891a70e9c194b7aaf`
- `requirements.txt`: `9bc3e4b733b2963a79a756a696eeafc92b532634`
- `tests/test_rc5.py`: `1f8470b4f6efea5bec3260cd575a626e8242c045`
- `tests/test_rc5_expectation_hardening.py`: `9d02b269fe83ba79ded16d154f59fed0267e87c5`
- `tests/test_rc5_jcs_vectors.py`: `35a01f918fc4b993e5367d7878e5b11a90bcd428`

The reference dependency file pins `rfc8785==0.1.4`.

## Frozen reference-suite execution

The exact reference suite was materialized in a separate hosted temporary directory from exact frozen URLs. The hosted runner re-verified all seven newly authorized reference blobs, the already-public registry/fixtures/conformance blobs needed by the suite, and both immutable independent JS blobs before execution.

Corrected scientific hosted run:

- GitHub Actions run: `33402915735`
- job: `99523356769`
- comparison-harness head: `57bd0eb7802fc6609e81220f545681c5ecf1a930`
- OS: Ubuntu `24.04.4`
- runner image: `ubuntu-24.04` version `20260823.283.1`
- Python: `3.12.3`
- Node: `v22.23.2`
- pip: `24.0`
- `rfc8785`: `0.1.4`
- pytest: `9.1.1`

Exact command:

`python -m pytest -q tests/test_rc5.py tests/test_rc5_expectation_hardening.py tests/test_rc5_jcs_vectors.py`

Exact result:

`67 passed in 0.10s`

Exit status: `0`.

The frozen reference suite therefore passed unchanged.

## Differential comparison

The corrected differential corpus contained 105 comparisons, including public fixtures and conformance cases plus cases exposed by the frozen reference tests and post-reveal cases required to score the prereveal uncertainties.

Corrected authority scoring:

- total comparisons: `105`
- authority-relevant comparisons: `103`
- authority-relevant agreements: `101`
- authority-relevant non-agreements: `2`
- `AUTHORITY_RELEVANT_DISAGREEMENT`: `0`
- `PUBLIC_AUTHORITY_AMBIGUITY`: `2`
- preserved `NON_AUTHORITY_IMPLEMENTATION_VARIANCE`: `2`
- `OUT_OF_DECLARED_DOMAIN_VARIANCE`: `0`
- `UNKNOWN`: `0`

The two authority-relevant non-agreement case identifiers are:

1. `semantic-identity:citation-use-clear.json`
   - reference: `decision:sha256:e86c5e5fffcd889b3a5a9eca66a384568a315d1ab0dea3886940bb3d0cd2139c`
   - frozen independent: `decision:sha256:d84e61c823f40e81b96d1b1080dec6202bde3ef7d88cb693e0c40896515736ec`
   - classification: `PUBLIC_AUTHORITY_AMBIGUITY`
2. `semantic-identity:task-dispatch-clear.json`
   - reference: `decision:sha256:a68aa5b74f49ccf293ec245ec8affd73d4c9bd2dd01f0a598149fd9722a512ce`
   - frozen independent: `decision:sha256:4da43cae85d6aa646fd42f7e9064f8068b771c526550997afb52bd118e07bb14`
   - classification: `PUBLIC_AUTHORITY_AMBIGUITY`

All other authority-relevant comparison areas agreed after applying the reveal packet's scoring rule that implementation-private exception wording is not normative and cross-language host representations are compared at Contract-D meaning/byte boundaries. Agreement covered:

- all six valid public fixtures;
- all invalid public fixtures at acceptance-versus-controlled-rejection level;
- exact, future/unknown, numeric, and case-varied version rejection;
- completed CLEAR, completed HOLD, and failed evaluation outcomes;
- registered effect validation and `knowledge.add_verified_tag@1` safe-default normalization;
- upstream, policy, target, requested-operation, and requested-parameter applicability;
- public conformance cases;
- unknown JSON-valid requested effect-parameter keys;
- malformed expectation missing/extra keys, wrong types, malformed target hashes, host-only requested values, non-finite requested values, and unpaired-surrogate requested operation;
- invalid UTF-8 and duplicate-key byte ingress;
- Unicode-scalar rejection;
- self-cycle and mutual-cycle controlled rejection;
- shared acyclic structures;
- exact container-depth 128 acceptance and depth 129 rejection;
- precision-losing integer-token rejection and accepted canonical/exact out-of-safe-range integer tokens;
- all 24 revealed RFC 8785 Appendix-B binary64/JCS number cases at the Contract-D byte boundary;
- negative zero;
- exponent and precision edges;
- non-BMP UTF-16 property ordering;
- canonical transport bytes for all six valid public decisions;
- semantic identities for completed HOLD, failed evaluation, `knowledge.add_verified_tag` default/object-scope cases;
- metadata invariance and Authorization-like metadata firewall behavior.

## Explicit disposition of prereveal uncertainties

### 1. Empty-schema registered effects

**Frozen uncertainty:** whether omitted `params` and `{}` normalize identically, and whether an empty normalized `params` object is present or absent in the semantic authority projection/identity.

**Post-reveal result:** both implementations treat omitted `params` and `{}` equivalently for the empty-schema effects themselves, but they choose different normalized projection shapes. The frozen reference always returns a normalized effect containing `params: {}`. The frozen independent Node implementation normalizes `knowledge.cite_as_evidence@1` and `task.dispatch@1` without a `params` property. Because `semantic_identity` hashes the normalized authority projection, this produces the two exact identity differences recorded above.

**Disposition:** `PUBLIC_AUTHORITY_AMBIGUITY`.

The public SPEC says semantic identity includes the “normalized registered effect” and that empty-schema effects have no declared parameters, but it does not explicitly say whether the normalized representation must include an empty `params` object. The frozen independent prediction is therefore not silently reconciled to the reference, and the identity disagreement remains preserved.

### 2. Unknown but JSON-valid requested effect-parameter keys

**Frozen uncertainty:** `not_applicable` versus malformed expectation / `cannot_establish`.

**Post-reveal result:** reference and frozen independent implementation agree. A JSON-valid parameter object with an unknown requested key remains a valid external expectation shape; because the requested constraint is not present in the normalized Decision effect, the consumer returns `not_applicable`.

**Disposition:** `AGREEMENT — prereveal prediction confirmed as not_applicable`.

### 3. Candidate-subtree verification posture

**Frozen uncertainty:** prereveal relied on the packet-pinned candidate subtree identity while independently verifying all six public authority blobs.

**Post-reveal result:** the reveal packet explicitly instructs that this deliberate aperture choice must not be retroactively classified as contamination. All six prereveal public blobs and all seven newly revealed reference blobs were independently identity-verified.

**Disposition:** `NO_ADDITIONAL_CONTAMINATION`; preserve overall contamination status `NON_ANSWER_BEARING_METADATA_EXPOSURE_ONLY`.

## Preserved deviations and evaluator defects

### Initial differential scorer defect

The first hosted comparison run, `33402693664` / job `99522614919`, produced a raw overcount of differences because the post-reveal evaluator incorrectly:

1. compared implementation-private rejection/error codes as though exact wording were authority-bearing; and
2. compared large integer-valued Python `float` objects directly with JavaScript's single `Number` host type instead of comparing Contract-D-level meaning and normative canonical bytes.

Those choices contradicted Sections 6 and 7 of the reveal packet. This is classified as `EVALUATOR_OR_HARNESS_DEFECT`. The first run remains preserved in hosted logs. It was corrected without modifying either frozen independent file or any reference file, and its raw disagreement count is not used as scientific evidence.

### Cross-language host representation variance

Two direct generic host-object probes remain intentionally preserved as `NON_AUTHORITY_IMPLEMENTATION_VARIANCE`:

- `host-representation:integer-valued-binary64:9007199254740992`
- `host-representation:integer-valued-binary64:295147905179352830000`

Python distinguishes host `int` and `float`; JavaScript exposes both through `Number`. The frozen JS generic host-value validator rejects unsafe integer-valued Numbers, while the Python reference accepts the same binary64 values when explicitly supplied as `float`. At JSON-byte ingress, where the Contract-D interoperable/JCS meaning is representable without this host-type distinction, both implementations accept the allowed tokens and produce identical canonical bytes. Therefore these are not authority-relevant disagreements under the packet's explicit cross-language scoring rule.

### Operational environment deviation

The local execution environment could not materialize the pinned Python dependency from the network. The packet-authorized exact reference suite was therefore run on GitHub-hosted Ubuntu using exact blob-verified materialization and the pinned `rfc8785==0.1.4` dependency. This is an execution-location deviation, not a scientific blocker; the exact hosted suite and runtime are recorded above.

## Scope and non-claims

This terminal record establishes only bounded evidence about independent recoverability/conformance of the frozen Contract D RC5 research candidate `0.3.0-rc5` under the compared corpus and explicit ambiguity described above.

It does not authorize or establish:

- production Contract D `1.0.0` promotion or release;
- any merge or production PR;
- actor identity, approval, delegation, autonomy, or trust semantics;
- operational Authorization;
- execution permission or execution occurrence;
- MainFrame/operator mutation;
- correctness of upstream epistemic judgments;
- arbitrary future Contract D versions, producers, consumers, transports, runtimes, or resource bounds.

No production promotion, release, merge, or Authorization action was performed by this reproduction.

## Smallest justified next step

Clarify the public Contract D authority so that the normalized semantic projection for registered empty-parameter-schema effects explicitly states whether `params: {}` is present or absent. If that clarification changes the frozen candidate authority, issue a new immutable research candidate and run a new clean independent reproduction against it. Do not patch this frozen independent implementation after reveal and count the patched result as independent agreement.

TERMINAL
