# Contract D RC6 Fresh Reproduction v1 — Freeze Receipt

Status: `PRE_REVEAL_FREEZE_COMPLETE`

## Clean base

- Execution repository: `camerontjs-dot/research-scaffold-harness`
- Branch: `research/contract-d-rc6-fresh-reproduction-v1`
- Required/verified initial commit: `548bfa81f65290eda15af658f647497679b840ef`
- Required/verified initial tree: `191976638bbf8b7153e3f2c94945a2f15cd640ad`
- Exact branch-ref verification was used; repository branches were not enumerated.
- Exact initial-tree path-name inspection found no `contract-d` implementation/reproduction material.

## Allowed public authority identities

- Authoritative repository: `camerontjs-dot/apparatus-contracts`
- Frozen candidate commit: `bb656fc50806c344fda1ddeaf08a9878f5cb460e`
- Frozen candidate subtree: `5151e2c30235784d4ae594db454ac24c1e3868b4`
- Candidate token: `0.3.0-rc6`
- RC6 `candidate/SPEC.md`: `6ff21ae57b4ae57f1d76ba34c41052b7966df7c5`
- RC6 `candidate/schema.json`: `c7c9f6b7a5874e08cbe3b3ce06c126a2b889e900`
- RC6 `candidate/effect-registry.json`: `53df222ca439248a44029e02a662825235db892f`
- RC6 `candidate/fixtures/valid.json`: `14c9259ce327f6a52f4a0d5e14260c0f92ad5fa2`
- RC6 `candidate/fixtures/invalid.json`: `08b69594e94cae6573e2afd882ef78d9c70629dc`
- RC6 `candidate/conformance-cases.json`: `29825bfa89b2b91bfa9e457c001e2c869a3649a4`
- Incorporated RC5 public `candidate/SPEC.md` @ `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`: `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`
- Context-free launch packet @ `f759b0ba502e0158c190b53435d6aae588bd9b9e`: `47392bb18b4ceec6dc6dc689a1444ccd9de0fce9`

## Access ledger and contamination status

- Ledger: `research/contract-d-rc6-fresh-reproduction-v1/ACCESS_LEDGER.md`
- Finalized ledger blob before receipt: `cd80c34d513786cd8ee8b02c5b46250f0dae3398`
- Contamination status: **CLEAN for answer-bearing information**.
- During exact candidate-subtree identity verification, Git tree metadata exposed names and blob/tree identities for denied files, but no denied file content was fetched. The exact metadata exposure is recorded in the ledger and is assessed as non-answer-bearing.
- No hidden/reference implementation, reference tests, RC6 change-note content, RC6 dependency-file content, unauthorized RC5 content, RC3/RC4 material, prior final record, adversarial-harness result, Decision Engine producer/implementation code, or promotion/EDR record was intentionally accessed before freeze.
- Historical rationale text embedded inside the expressly allowed RC6 public SPEC was read only as part of that allowed authority; its referenced prior result was not opened.

## Independent implementation/test freeze

- Independent implementation:
  - `research/contract-d-rc6-fresh-reproduction-v1/contract_d_rc6_consumer.mjs`
  - blob `26058b7901347c6e7e3c207de2195a0ab529aa08`
- Independent tests:
  - `research/contract-d-rc6-fresh-reproduction-v1/test_contract_d_rc6_consumer.mjs`
  - blob `c4f733088fe25f482b07b24fe2685d7a524d1e20`
- Preserved prereveal test log:
  - `research/contract-d-rc6-fresh-reproduction-v1/PREREVEAL_TEST_LOG.md`
  - blob `f4f1864e78166d8c0ec58ed0c2c90b2fa952c9ce`
- Immutable implementation/test freeze commit: `f5ce28cef76808e390e016d63dec3d50a28fbda2`
- Freeze tree: `805c3b229922a605b16990a699ffa03f3a2e6250`
- Frozen implementation/test/log blobs were re-read at that exact commit and matched the independently computed local Git blob identities.
- No frozen implementation or prereveal test file was modified after the freeze commit.

## Prereveal test result

Runtime: Node.js `v22.16.0`

Command: `node test_contract_d_rc6_consumer.mjs`

- Preserved intermediate run: `66 passed, 1 failed, 67 total`.
- Intermediate failure: `JCS exponent serialization positive exponent` with controlled `non_interoperable_integer` error.
- The correction was derived solely from the allowed RC5 public authority's distinction between programmatic host integers and JSON-byte ingress; no hidden/reference behavior was consulted.
- Exact freeze-candidate prereveal result: **`67 passed, 0 failed, 67 total`**.
- No hosted prereveal test run was used; the recorded result is local execution of the frozen candidate contents before commit.

## Unresolved prereveal uncertainties

1. The public authority normatively fixes acceptance/rejection, named controlled failures in specific cases, and consumer outcomes, but does not fully standardize every internal validator error-code label used by this independent implementation. Internal detail codes should therefore not be treated as authority unless explicitly named by the public SPEC.
2. JavaScript has a single binary64 `Number` type rather than distinct integer/float host types. The implementation interprets the public safe-host-integer rule by rejecting programmatically supplied integer-valued Numbers outside the safe-integer range while preserving separately validated JSON-byte-ingress provenance. This is authority-motivated but remains a language-mapping point for later differential observation.
3. The prereveal suite covers representative RFC 8785/JCS exponent and precision edges required by the packet, but it is not an exhaustive binary64 serialization proof over every possible finite value.

## Receipt commit identity

The receipt's own containing commit SHA cannot be embedded self-referentially in the same immutable commit. The repository write result for this file is the durable receipt commit and is reported externally at the mandatory prereveal stop point.

## Boundary

This receipt records research-only prereveal reproducibility work. It does not authorize production promotion, release, Authorization behavior, execution behavior, downstream mutation, or post-freeze reference reveal.
