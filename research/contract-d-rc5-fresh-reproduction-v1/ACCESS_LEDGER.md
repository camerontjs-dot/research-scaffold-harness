# Contract D RC5 Fresh Reproduction Access Ledger

## Isolation status

- Clean execution repository: `camerontjs-dot/research-scaffold-harness`
- Required initial branch: `research/contract-d-rc5-fresh-reproduction-v1`
- Verified initial head: `548bfa81f65290eda15af658f647497679b840ef`
- Verified initial tree: `191976638bbf8b7153e3f2c94945a2f15cd640ad`
- Clean-base path-name check: recursive tree metadata contained no path matching `contract-d`.
- Authority was not opened until after the clean-base check and initial durable ledger commit.
- Contamination status: `NON_ANSWER_BEARING_METADATA_EXPOSURE_ONLY`.

### Accidental denied-metadata exposure

The GitHub connector rejected the branch-specific metadata endpoint used to verify the required fresh branch head. The fallback branch-collection response exposed only branch names and head commit SHAs for prior Contract D reproduction branches, not their files, commits' contents, tests, results, reports, or semantic conclusions:

- `research/contract-d-fresh-reproduction-rc0` @ `0ad80dbecca43dc3a057d015617914d742f32d23`
- `research/contract-d-rc3-fresh-reproduction` @ `cb000a2169fe8dd02baed028881d3ed945a6e606`
- `research/contract-d-rc3-fresh-reproduction-2` @ `b7447b8aabf7d0bfe89fe264786134e47f8dcbe3`
- `research/contract-d-rc4-fresh-reproduction` @ `75812088e7965e507a353da7414f7d3f503fcecd`
- `research/contract-d-rc4-fresh-reproduction-v2` @ `d5f461df0d6ba5d9687d58851f91927aae2b17c6`

This metadata is demonstrably non-answer-bearing for the independent Contract D semantic question. No denied branch was opened or searched and no prior reproduction content or outcome was observed.

## Prereveal accesses

1. `camerontjs-dot/apparatus-contracts` @ `fed140fc8e357c6122d66f8db7d6d9202a6b8edf`
   - `research/contract-d-independent-authority-rc5/CONTEXT_FREE_LAUNCH_PACKET.md`
   - verified blob: `fc8d10324a3011d4bc643dc9f66ef410d027a44e`
   - purpose: authoritative launch instructions and information aperture.

2. `camerontjs-dot/research-scaffold-harness`
   - branch collection metadata used only after the branch-specific endpoint returned no content
   - commit metadata for `548bfa81f65290eda15af658f647497679b840ef`
   - recursive tree metadata for `191976638bbf8b7153e3f2c94945a2f15cd640ad`
   - purpose: mandatory clean-base head/tree verification and path-name-only check for pre-existing Contract D reproduction material.

3. `camerontjs-dot/research-scaffold-harness` branch `research/contract-d-rc5-fresh-reproduction-v1`
   - `research/contract-d-rc5-fresh-reproduction-v1/ACCESS_LEDGER.md`
   - purpose: durable access ledger creation and maintenance.

4. `camerontjs-dot/apparatus-contracts` @ frozen candidate commit `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`
   - packet-pinned candidate subtree: `f5db874db39c0c3bf863f4ba2cc1a3597369f3bf`
   - `research/contract-d-independent-authority-rc5/candidate/SPEC.md` — blob `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`
   - `research/contract-d-independent-authority-rc5/candidate/schema.json` — blob `fe4e74464a53f581d52baed02257dd9452e6bfe3`
   - `research/contract-d-independent-authority-rc5/candidate/effect-registry.json` — blob `53df222ca439248a44029e02a662825235db892f`
   - `research/contract-d-independent-authority-rc5/candidate/fixtures/valid.json` — blob `f03b16f41f119a8a485e0f7ac3dac30f509c40b9`
   - `research/contract-d-independent-authority-rc5/candidate/fixtures/invalid.json` — blob `8c3fd3370d7f96a7cb162d8acfeacb7b189b4d86`
   - `research/contract-d-independent-authority-rc5/candidate/conformance-cases.json` — blob `29825bfa89b2b91bfa9e457c001e2c869a3649a4`
   - purpose: complete allowed prereveal Contract D authority surface.

5. External normative source explicitly permitted by the launch packet:
   - RFC Editor, RFC 8785 / JSON Canonicalization Scheme, `https://www.rfc-editor.org/rfc/rfc8785`
   - consulted for JCS primitive serialization, UTF-16 property ordering, negative-zero/number examples, and the canonical `295147905179352830000` sample.
   - no external Contract D behavioral source was used.

6. Local language/runtime execution:
   - Node.js `v22.16.0`, built-in modules only (`node:crypto`, `node:test`, `node:assert/strict`).
   - independent implementation scratch mirror used only to author and execute the files later committed below.

7. `camerontjs-dot/research-scaffold-harness` branch `research/contract-d-rc5-fresh-reproduction-v1`
   - `research/contract-d-rc5-fresh-reproduction-v1/contract_d_rc5.js` — frozen blob `e60d3a15da98e32a732f1860808b8dda7ba7f3ee`
   - `research/contract-d-rc5-fresh-reproduction-v1/test_contract_d_rc5.js` — frozen blob `102327e348364c62454369d2614ca98ce80d94c5`
   - purpose: independent implementation and prereveal tests. Git blob identities matched the locally executed files exactly.

## Prereveal test execution

Command: `node --test test_contract_d_rc5.js`

Runtime: Node.js `v22.16.0`.

Result:

- tests: 24
- pass: 24
- fail: 0
- cancelled: 0
- skipped: 0
- todo: 0
- final TAP run duration: 86.232614 ms

## Post-freeze authorization and accesses

8. `camerontjs-dot/apparatus-contracts` @ `48a46db987b6ce3079abe28f83be6c8396aa2353`
   - `research/contract-d-independent-authority-rc5/POST_FREEZE_REVEAL_PACKET.md`
   - verified blob: `a403c343631f60144f87ddf1efb984afa60d1ca3`
   - purpose: exact post-freeze reveal and differential-comparison authorization.

9. Before opening reference behavior, the immutable independent objects were re-read at freeze commit `54c78823e289a3d0d490189d1ffafc25d127d585` and still matched:
   - `research/contract-d-rc5-fresh-reproduction-v1/contract_d_rc5.js` — `e60d3a15da98e32a732f1860808b8dda7ba7f3ee`
   - `research/contract-d-rc5-fresh-reproduction-v1/test_contract_d_rc5.js` — `102327e348364c62454369d2614ca98ce80d94c5`
   - result: no `FROZEN_IMPLEMENTATION_MOVED` blocker.

10. Newly authorized reference files, all read only at exact frozen candidate commit `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8` and all blob-verified:
   - `candidate/contract_d_core.py` — `6c3fbe3e6ac6effe0a4ed66f17145ffd32705edf`
   - `candidate/contract_d_validate.py` — `8cc6d81515d7c5b0a86df163a38d1c12931f897f`
   - `candidate/contract_d_consume.py` — `42536aaac5acd953f150a87891a70e9c194b7aaf`
   - `candidate/requirements.txt` — `9bc3e4b733b2963a79a756a696eeafc92b532634`
   - `candidate/tests/test_rc5.py` — `1f8470b4f6efea5bec3260cd575a626e8242c045`
   - `candidate/tests/test_rc5_expectation_hardening.py` — `9d02b269fe83ba79ded16d154f59fed0267e87c5`
   - `candidate/tests/test_rc5_jcs_vectors.py` — `35a01f918fc4b993e5367d7878e5b11a90bcd428`
   - `requirements.txt` pins `rfc8785==0.1.4`.

11. Post-reveal comparison-only files added under the permitted separate path:
   - `research/contract-d-rc5-fresh-reproduction-v1/post_reveal/node_adapter.js`
   - `research/contract-d-rc5-fresh-reproduction-v1/post_reveal/differential.py`
   - `research/contract-d-rc5-fresh-reproduction-v1/post_reveal/run_hosted_comparison.sh`
   - `.github/workflows/contract-d-rc5-post-reveal.yml`
   - purpose: exact hosted materialization, frozen reference execution, and differential comparison. These files do not modify the frozen independent implementation or prereveal tests.

12. GitHub Actions hosted reference execution and differential comparison:
   - corrected scientific run: workflow run `33402915735`, job `99523356769`, head `57bd0eb7802fc6609e81220f545681c5ecf1a930`
   - runner OS: Ubuntu `24.04.4`, `ubuntu-24.04` image `20260823.283.1`
   - Python: `3.12.3`
   - Node: `v22.23.2`
   - pip: `24.0`
   - `rfc8785`: `0.1.4`
   - pytest: `9.1.1`
   - exact reference-suite command: `python -m pytest -q tests/test_rc5.py tests/test_rc5_expectation_hardening.py tests/test_rc5_jcs_vectors.py`
   - exact reference-suite result: `67 passed in 0.10s`, exit `0`
   - the runner independently re-verified all seven newly authorized reference blobs, the required already-public registry/fixture/conformance blobs, and both frozen JS blobs before execution.

13. Differential evaluator history, preserved rather than erased:
   - initial hosted run `33402693664`, job `99522614919` exposed an `EVALUATOR_OR_HARNESS_DEFECT`: it compared implementation-private rejection codes as normative and compared Python `float` values directly with JavaScript's single `Number` host type for integer-valued binary64 values, contrary to the reveal packet's scoring rules.
   - initial raw scorer output was preserved in the hosted run logs and was not used for terminal scientific scoring.
   - corrected harness revision 2 normalized controlled rejection to acceptance-vs-controlled-rejection and compared cross-language integer-valued binary64 cases at the Contract-D byte/JCS boundary.
   - corrected result: 105 total comparisons; 103 authority-relevant; 101 authority-relevant agreements; 2 authority-relevant non-agreements, both `PUBLIC_AUTHORITY_AMBIGUITY`; 0 `AUTHORITY_RELEVANT_DISAGREEMENT`; plus 2 preserved `NON_AUTHORITY_IMPLEMENTATION_VARIANCE` host-representation cases.

## Post-freeze forbidden-material status

The reveal authorization did not open the wider research history. No `RC5_CHANGE_NOTE.md`, prior RC3/RC4 implementation/test/reproduction content, adversarial-harness content or results, Contract D promotion/EDR material, Decision Engine Contract D producer/reference code, or surrounding ChatGPT/project-history retrieval was intentionally accessed.

The prereveal contamination classification remains `NON_ANSWER_BEARING_METADATA_EXPOSURE_ONLY`. The packet-pinned candidate-subtree posture is not retroactively classified as contamination. The reference implementation/tests were accessed only after the immutable independent freeze and only under the explicit reveal packet.
