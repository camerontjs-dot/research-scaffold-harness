# Contract D RC5 Fresh Independent Reproduction — Freeze Receipt

## Freeze status

`PRE_REVEAL_FREEZE_COMPLETE`

This receipt records the immutable prereveal implementation/test freeze. The receipt itself is committed after the freeze commit so that it can name the already-frozen commit and tree without modifying the independent implementation or tests.

## Clean base

- Repository: `camerontjs-dot/research-scaffold-harness`
- Branch: `research/contract-d-rc5-fresh-reproduction-v1`
- Required and verified initial commit: `548bfa81f65290eda15af658f647497679b840ef`
- Required and verified initial tree: `191976638bbf8b7153e3f2c94945a2f15cd640ad`
- Initial recursive path-name check found no path matching `contract-d`.

## Allowed frozen authority

- Repository: `camerontjs-dot/apparatus-contracts`
- Candidate commit: `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`
- Candidate subtree specified by the launch packet: `f5db874db39c0c3bf863f4ba2cc1a3597369f3bf`
- Candidate token: `0.3.0-rc5`

Allowed public authority blobs, each independently verified when fetched at the frozen candidate commit:

- `research/contract-d-independent-authority-rc5/candidate/SPEC.md` — `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`
- `research/contract-d-independent-authority-rc5/candidate/schema.json` — `fe4e74464a53f581d52baed02257dd9452e6bfe3`
- `research/contract-d-independent-authority-rc5/candidate/effect-registry.json` — `53df222ca439248a44029e02a662825235db892f`
- `research/contract-d-independent-authority-rc5/candidate/fixtures/valid.json` — `f03b16f41f119a8a485e0f7ac3dac30f509c40b9`
- `research/contract-d-independent-authority-rc5/candidate/fixtures/invalid.json` — `8c3fd3370d7f96a7cb162d8acfeacb7b189b4d86`
- `research/contract-d-independent-authority-rc5/candidate/conformance-cases.json` — `29825bfa89b2b91bfa9e457c001e2c869a3649a4`

The authoritative launch packet was verified at blob `fc8d10324a3011d4bc643dc9f66ef410d027a44e` from commit `fed140fc8e357c6122d66f8db7d6d9202a6b8edf`.

## Access ledger and contamination status

- Ledger: `research/contract-d-rc5-fresh-reproduction-v1/ACCESS_LEDGER.md`
- Ledger blob at freeze: `1a5ddd61fe481a49beea1d82712de233d22888b5`
- Contamination status: `NON_ANSWER_BEARING_METADATA_EXPOSURE_ONLY`

During clean-base verification, a branch-specific metadata endpoint failed. The fallback branch-collection response exposed only names and opaque head SHAs of prior Contract D reproduction branches. No prior branch was opened; no prior implementation, test, result, report, expected output, or semantic conclusion was observed. This exposure is recorded in full in the access ledger and classified as demonstrably non-answer-bearing for the independent semantic question.

No denied reference implementation, denied reference tests, candidate requirements, RC5 change note, prior reproduction contents/results, adversarial-harness contents/results, Decision Engine producer implementation, promotion/EDR material, or surrounding ChatGPT/project/thread context was intentionally accessed.

## Independent implementation and tests

- Implementation path: `research/contract-d-rc5-fresh-reproduction-v1/contract_d_rc5.js`
- Implementation blob: `e60d3a15da98e32a732f1860808b8dda7ba7f3ee`
- Test path: `research/contract-d-rc5-fresh-reproduction-v1/test_contract_d_rc5.js`
- Test blob: `102327e348364c62454369d2614ca98ce80d94c5`

The committed Git blobs match the locally executed files exactly.

## Immutable prereveal freeze

- Freeze commit: `54c78823e289a3d0d490189d1ffafc25d127d585`
- Freeze tree: `6a691a691ed56c95616bae1595137daf1a96b86f`

The independent implementation and prereveal tests are frozen at that commit/tree and were not modified after the freeze.

## Prereveal test result

Execution environment:

- Node.js `v22.16.0`
- built-in modules only; no third-party implementation dependency

Command:

`node --test test_contract_d_rc5.js`

Final prereveal TAP result:

- tests: `24`
- pass: `24`
- fail: `0`
- cancelled: `0`
- skipped: `0`
- todo: `0`
- duration: `86.232614 ms`

## Unresolved prereveal uncertainties

1. For registered effects whose parameter schema is empty (`knowledge.cite_as_evidence@1` and `task.dispatch@1`), the implementation treats omitted `params` and explicit `{}` as the same machine-semantic effect and omits an empty `params` object from the normalized semantic projection. The public authority strongly suggests this from the empty parameter schema, but only the `knowledge.add_verified_tag@1` default-equivalence cases are stated explicitly.
2. For external requested effect parameters, a syntactically valid but unregistered/mismatching key is treated as a supplied constraint that fails applicability (`not_applicable`), rather than as a malformed expectation. This follows the public instruction to treat supplied keys as constraints, but the exact classification of an otherwise-valid unknown requested parameter name is not separately exemplified.
3. The candidate subtree SHA above is the exact immutable identity supplied by the verified launch packet. The six permitted public file blobs were independently verified, but the entire candidate subtree was not traversed because doing so could expose metadata for explicitly denied sibling files before freeze.

No post-freeze reveal, hidden/reference search, or differential comparison has been performed.
