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

This metadata is classified as demonstrably non-answer-bearing for the independent Contract D semantic question: it reveals only that prior branches exist and their opaque Git identities. No denied branch was opened or searched and no prior reproduction content or outcome was observed.

## Accesses

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
   - purpose: durable access ledger creation and finalization.

4. `camerontjs-dot/apparatus-contracts` @ frozen candidate commit `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`
   - declared candidate subtree from launch packet: `f5db874db39c0c3bf863f4ba2cc1a3597369f3bf`
   - `research/contract-d-independent-authority-rc5/candidate/SPEC.md` — verified blob `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`
   - `research/contract-d-independent-authority-rc5/candidate/schema.json` — verified blob `fe4e74464a53f581d52baed02257dd9452e6bfe3`
   - `research/contract-d-independent-authority-rc5/candidate/effect-registry.json` — verified blob `53df222ca439248a44029e02a662825235db892f`
   - `research/contract-d-independent-authority-rc5/candidate/fixtures/valid.json` — verified blob `f03b16f41f119a8a485e0f7ac3dac30f509c40b9`
   - `research/contract-d-independent-authority-rc5/candidate/fixtures/invalid.json` — verified blob `8c3fd3370d7f96a7cb162d8acfeacb7b189b4d86`
   - `research/contract-d-independent-authority-rc5/candidate/conformance-cases.json` — verified blob `29825bfa89b2b91bfa9e457c001e2c869a3649a4`
   - purpose: complete allowed prereveal Contract D authority surface.

5. External normative source explicitly permitted by the packet:
   - RFC Editor, RFC 8785 / JSON Canonicalization Scheme: `https://www.rfc-editor.org/rfc/rfc8785`
   - consulted for JCS primitive serialization, UTF-16 property ordering, negative-zero/number examples, and the canonical `295147905179352830000` sample.
   - no other web search or external Contract D source was used.

6. Local language/runtime execution:
   - Node.js `v22.16.0`, built-in modules only (`node:crypto`, `node:test`, `node:assert/strict`); no third-party package or implementation consulted.
   - independent implementation scratch mirror used only to author and execute the files later committed below.

7. `camerontjs-dot/research-scaffold-harness` branch `research/contract-d-rc5-fresh-reproduction-v1`
   - `research/contract-d-rc5-fresh-reproduction-v1/contract_d_rc5.js`
   - committed blob verified: `e60d3a15da98e32a732f1860808b8dda7ba7f3ee`
   - `research/contract-d-rc5-fresh-reproduction-v1/test_contract_d_rc5.js`
   - committed blob verified: `102327e348364c62454369d2614ca98ce80d94c5`
   - purpose: independent implementation and prereveal tests. Git blob identities match the locally executed files exactly.

## Prereveal test execution

Command:

`node --test test_contract_d_rc5.js`

Runtime: Node.js `v22.16.0`.

Final prereveal result:

- tests: 24
- pass: 24
- fail: 0
- cancelled: 0
- skipped: 0
- todo: 0
- final TAP run duration: 86.232614 ms

The suite covers the required positive, negative, sensitivity, invariance, metamorphic, depth/cycle, byte-ingress, Unicode, RFC 8785/JCS numeric/canonicalization, applicability, failure-state, malformed-expectation, and Authorization-firewall controls described by the launch packet.

## Denied material

No denied Contract D reference implementation, reference tests, candidate requirements, RC5 change note, prior reproduction contents/results, adversarial-harness contents/results, producer implementation, promotion/EDR material, or surrounding ChatGPT/project/thread context was intentionally accessed.

The only denied-adjacent exposure was the opaque prior-branch name/head metadata listed above; it was not used to choose architecture, semantics, expected outputs, or fixes.
